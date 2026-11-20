#!/usr/bin/env python3
"""One scoped boot-only diagnostic transaction; never writes system/recovery/userdata."""
import argparse,fcntl,json,os,time
from pathlib import Path
from restore_diagnostic_boot import Adb,BOOT,BOOT_BYTES,RECOVERY,RECOVERY_BYTES,sha,preflight,restore,update_receipt
from display_direct_device import ORIGINAL,RECOVERY as RECOVERY_SHA
from android_direct_device import SYSTEM,SYSTEM_BYTES,AndroidAdb,file_hash
import retained_log_mailbox as mailbox
SCOPE='android-early-capture-1'
SUPPORT=['android_early_capture_device.py','run_android_early_return.py','capture_android_early_console.py','restore_diagnostic_boot.py','display_direct_device.py','android_direct_device.py','retained_log_mailbox.py','bounded_recovery_entry.py','capture_live_acm_probe.py']
def inputs(case):
 m=json.loads((case/'case-manifest-private.json').read_text());r=json.loads((case/'report.json').read_text())
 if m.get('scope')!=SCOPE or m.get('recovery_sha256')!=RECOVERY_SHA:raise ValueError('Exact diagnostic case required')
 for key,name in [('boot','boot-full.img'),('original_boot','original-boot.img')]:
  p=case/name
  if p.is_symlink() or p.stat().st_size!=BOOT_BYTES or file_hash(p)!=m['files'][key]['sha256'] or m['files'][key]['bytes']!=BOOT_BYTES:raise ValueError('Case artifact mismatch')
 if m['files']['original_boot']['sha256']!=ORIGINAL or r['partition_sha256']!=m['files']['boot']['sha256']:raise ValueError('Pinned original/candidate required')
 nonce=(case/'trial-nonce-private.bin').read_bytes()
 if sha(nonce)!=m['nonce_sha256'] or r['nonce_sha256']!=m['nonce_sha256']:raise ValueError('Nonce mismatch')
 mailbox.inspect((case/'boot-full.img').read_bytes(),nonce,r['retained_prefix_sha256'])
 return m

def authorization(case,m):
 expected={'scope':SCOPE,'owner_approved':True,'candidate_sha256':m['files']['boot']['sha256'],'nonce_sha256':m['nonce_sha256'],'manifest_sha256':sha((case/'case-manifest-private.json').read_bytes()),'selector_sha256':sha((case/'selector-private.json').read_bytes()),'maximum_boot_requests':1,'maximum_candidate_writes':1,'system_writes_allowed':False,'recovery_writes_allowed':False,'userdata_writes_allowed':False,'automatic_retry':False,'support_sha256':{n:sha((Path(__file__).parent/n).read_bytes()) for n in SUPPORT},'return_config_sha256':sha((case/'return-config-private.json').read_bytes()),'capture_profile_sha256':sha((case/'capture-profile-private.json').read_bytes())}
 if json.loads((case/'owner-authorization-private.json').read_text())!=expected:raise ValueError('Exact diagnostic authorization required')
 return expected

def exclusive(path,data):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as f:json.dump(data,f);f.flush();os.fsync(f.fileno())

def check_system(adb,m):
 if adb.run(['shell','readlink','/dev/block/platform/mtk-msdc.0/by-name/system']).strip()!=SYSTEM.encode():raise ValueError('System alias mismatch')
 if int(adb.run(['exec-out','cat','/sys/class/block/mmcblk0p14/size']).strip())*512!=SYSTEM_BYTES:raise ValueError('System size mismatch')
 if adb.digest(SYSTEM)!=m['system_sha256']:raise ValueError('Installed system differs')

def run(case,adb,action):
 m=inputs(case);authorization(case,m);boot=(case/'boot-full.img').read_bytes()
 manifest={'boot':m['files']['boot'],'recovery':{'bytes':RECOVERY_BYTES,'sha256':RECOVERY_SHA}}
 if action in ['preflight','install']:
  preflight(adb,boot,manifest,m['expected_boot_before_sha256']);check_system(adb,m)
  if action=='preflight':return {'passed':True,'written':False}
  return restore(adb,boot,manifest,m['expected_boot_before_sha256'],case/'install-receipt-private.json',operation='One approved early-capture boot-only install')
 receipt=json.loads((case/'install-receipt-private.json').read_text())
 if receipt.get('verified') is not True or receipt.get('rollback_sha256')!=sha(boot):raise ValueError('Owned verified install required')
 if action=='boot':
  preflight(adb,boot,manifest,sha(boot))
  exclusive(case/'boot-request-private.json',{'candidate_boot_sha256':sha(boot),'at':time.time(),'maximum_boot_requests':1})
  adb.run(['reboot']);return {'boot_requested':True,'automatic_retry':False}
 if action=='collect':
  # Recovery identity and exact immutable prefix+seed are prerequisites to readout.
  if adb.run(['get-state']).strip()!=b'recovery' or sha(adb.read(RECOVERY,RECOVERY_BYTES))!=RECOVERY_SHA:raise ValueError('Original recovery required')
  actual=adb.read(BOOT,BOOT_BYTES);r=json.loads((case/'report.json').read_text())
  records=mailbox.inspect(actual,(case/'trial-nonce-private.bin').read_bytes(),r['retained_prefix_sha256'])
  check_system(adb,m)
  with (case/'collected-boot-private.img').open('xb') as f:f.write(actual)
  latest=records['latest'];result={'scope':SCOPE,'recovery_unchanged':True,'system_unchanged':True,'boot_prefix_unchanged':True,'full_boot_sha256':sha(actual),'record_sequence':latest['sequence'] if latest else None,'kernel_snapshot_found':bool(latest and latest['sequence']>=2),'panic_captured':bool(latest and latest['sequence']>=2 and b'Kernel panic' in latest['payload']),'written':False}
  if latest:(case/'retained-kernel-private.bin').write_bytes(latest['payload'])
  exclusive(case/'collection-receipt-private.json',result);return result
 raise ValueError('Unsupported action')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=Path,required=True);p.add_argument('action',choices=['preflight','install','boot','collect']);a=p.parse_args()
 m=inputs(a.case);authorization(a.case,m);selector=json.loads((a.case/'selector-private.json').read_text())['selector']
 lock=(a.case/'.device-operation.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 print(json.dumps(run(a.case,AndroidAdb('adb',selector),a.action)))
