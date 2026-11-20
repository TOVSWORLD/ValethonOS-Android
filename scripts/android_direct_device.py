#!/usr/bin/env python3
"""Guarded Android boot/system transaction from selected original TWRP; default read-only."""
import argparse,fcntl,hashlib,json,os,re,secrets,subprocess,time
from pathlib import Path
from restore_diagnostic_boot import Adb,BOOT,BOOT_BYTES,RECOVERY,RECOVERY_BYTES,sha,restore,preflight as boot_preflight,update_receipt
from display_direct_device import ORIGINAL,RECOVERY as RECOVERY_SHA
SYSTEM='/dev/block/mmcblk0p14';SYSTEM_BYTES=1692925952;CHUNK=8*1024*1024
FILES={'boot':'boot-full.img','system':'system-raw.img','original_boot':'original-boot.img','original_system':'pretest-system.img'}
def file_hash(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def chunks(size):
    if size!=SYSTEM_BYTES or size%4096:raise ValueError('Exact existing system geometry required')
    return [(at,min(CHUNK,size-at)) for at in range(0,size,CHUNK)]
def inputs(case):
    m=json.loads((case/'case-manifest-private.json').read_text())
    if m.get('scope')!='android-t1-1' or m.get('recovery_sha256')!=RECOVERY_SHA:raise ValueError('Exact Android T1/recovery contract required')
    sizes={'boot':BOOT_BYTES,'system':SYSTEM_BYTES,'original_boot':BOOT_BYTES,'original_system':SYSTEM_BYTES}
    for key,name in FILES.items():
        p=case/name;row=m['files'][key]
        if p.is_symlink() or not p.is_file() or p.stat().st_size!=sizes[key] or row['bytes']!=sizes[key] or file_hash(p)!=row['sha256']:raise ValueError('Case input size/hash mismatch: '+key)
    if m['files']['original_boot']['sha256']!=ORIGINAL:raise ValueError('Verified original Android boot rollback required')
    if sha((case/'trial-nonce-private.bin').read_bytes())!=m['nonce_sha256']:raise ValueError('Fresh trial binding mismatch')
    with (case/FILES['system']).open('rb') as f:f.seek(1080);magic=f.read(2)
    if magic!=b'\x53\xef':raise ValueError('Raw ext4 image required; do not write sparse container')
    return m
def authorization(case,m):
    a=json.loads((case/'owner-authorization-private.json').read_text())
    if a.get('owner_approved') is not True:raise ValueError('Exact candidate owner authorization required')
    expected={'scope':'android-t1-1','owner_approved':True,'boot_sha256':m['files']['boot']['sha256'],'system_sha256':m['files']['system']['sha256'],'original_system_sha256':m['files']['original_system']['sha256'],'nonce_sha256':m['nonce_sha256'],'runner_sha256':sha(Path(__file__).read_bytes()),'return_config_sha256':sha((case/'return-config-private.json').read_bytes()),'return_runner_sha256':sha((Path(__file__).parent/'run_android_t1_return.py').read_bytes()),'case_manifest_sha256':sha((case/'case-manifest-private.json').read_bytes()),'support_sha256':{n:sha((Path(__file__).parent/n).read_bytes()) for n in ['restore_diagnostic_boot.py','display_direct_device.py']},'maximum_boot_writes':1,'maximum_system_writes':1,'maximum_original_restore_writes':1,'recovery_writes_allowed':False,'userdata_writes_allowed':False,'automatic_trial_retry':False}
    if any(type(a.get(k)) is not type(v) or a.get(k)!=v for k,v in expected.items()):raise ValueError('Exact candidate owner authorization required')
    return a
class AndroidAdb(Adb):
    def digest(self,node):
        allowed={SYSTEM,BOOT,RECOVERY}
        if node not in allowed and not re.fullmatch(r'/tmp/valethonos-android-[a-f0-9]{32}/chunk.img',node):raise ValueError('Unrelated digest path rejected')
        r=subprocess.run(self.command+['exec-out','sha256sum',node],capture_output=True,timeout=900)
        if r.returncode or not re.fullmatch(rb'[a-f0-9]{64}\s+[^\r\n]+\s*',r.stdout):raise ValueError('Selected digest failed')
        return r.stdout.split()[0].decode()
def preflight(adb,case,m,expected_boot,expected_system=None):
    original=(case/'original-boot.img').read_bytes();contract={'boot':m['files']['original_boot'],'recovery':{'bytes':RECOVERY_BYTES,'sha256':RECOVERY_SHA}}
    boot_preflight(adb,original,contract,expected_boot)
    if int(adb.run(['exec-out','cat','/sys/class/block/mmcblk0p14/size']).strip())*512!=SYSTEM_BYTES:raise ValueError('System partition geometry changed')
    mounts=adb.run(['exec-out','cat','/proc/mounts']).splitlines()
    if any(row.split()[0]==SYSTEM.encode() for row in mounts if row.split()):raise ValueError('System must be unmounted in TWRP before raw image operation')
    if expected_system is not None and adb.digest(SYSTEM)!=expected_system:raise ValueError('Current system differs from expected backup/candidate')
def receipt(path,data):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
def write_system(adb,path,expected_hash,log,log_path):
    mounts=[x.split() for x in adb.run(['exec-out','cat','/proc/mounts']).splitlines()]
    if adb.run(['exec-out','readlink','-f','/tmp']).strip()!=b'/tmp' or len([x for x in mounts if len(x)>=4 and x[1]==b'/tmp' and x[2]==b'tmpfs' and b'rw' in x[3].split(b',')])!=1:raise ValueError('Verified writable recovery tmpfs required')
    folder='/tmp/valethonos-android-'+secrets.token_hex(16);destination=folder+'/chunk.img'
    if adb.run(['exec-out','mkdir','-m','700',folder]):raise ValueError('Exclusive RAM stage failed')
    log['private_ram_staging']=folder;update_receipt(log_path,log)
    with path.open('rb') as source:
        for offset,length in chunks(SYSTEM_BYTES):
            data=source.read(length)
            if len(data)!=length:raise ValueError('Short host image; stop without retry')
            adb.push(data,destination)
            if adb.digest(destination)!=sha(data):raise ValueError('RAM chunk digest mismatch; stop before write')
            log.update(system_write_started=True,next_offset=offset,next_bytes=length);update_receipt(log_path,log)
            # Only p14; staging is bounded RAM, never userdata or recovery.
            adb.run(['exec-out','dd','if='+destination,'of='+SYSTEM,'bs=4096','seek='+str(offset//4096),'count='+str(length//4096)])
            log['bytes_submitted']=offset+length;update_receipt(log_path,log)
    adb.run(['exec-out','sync'])
    if adb.digest(SYSTEM)!=expected_hash:raise ValueError('Full system readback differs; boot write not admitted')
    log['system_readback_verified']=True;update_receipt(log_path,log)
    adb.run(['exec-out','rm',destination]);adb.run(['exec-out','rmdir',folder])
def run(case,adb,action):
    m=inputs(case)
    if action=='preflight':
        preflight(adb,case,m,m['expected_boot_before_sha256'],m['files']['original_system']['sha256'])
        return {'scope':'Read-only physical TWRP preflight','passed':True,'written':False}
    if action=='verify-installed':
        preflight(adb,case,m,m['files']['boot']['sha256'],m['files']['system']['sha256'])
        return {'scope':'Read-only installed candidate/recovery verification','passed':True,'written':False}
    authorization(case,m)
    if action=='boot':
        done=json.loads((case/'install-receipt-private.json').read_text())
        if not done.get('verified') or done.get('candidate_boot_sha256')!=m['files']['boot']['sha256']:raise ValueError('Verified exact installation required')
        boot_preflight(adb,(case/'original-boot.img').read_bytes(),{'boot':m['files']['original_boot'],'recovery':{'bytes':RECOVERY_BYTES,'sha256':RECOVERY_SHA}},m['files']['boot']['sha256'])
        p=case/'boot-request-private.json';receipt(p,{'requested':True,'candidate_boot_sha256':m['files']['boot']['sha256'],'at':time.time(),'maximum_boot_requests':1})
        adb.run(['reboot']);return {'boot_requested':True,'automatic_retry':False}
    if action not in {'install','rollback'}:raise ValueError('Unknown action')
    if action=='install':
        expected_boot=m['expected_boot_before_sha256'];expected_system=m['files']['original_system']['sha256'];system_key='system';boot_key='boot'
    else:
        prior=json.loads((case/'install-receipt-private.json').read_text())
        if prior.get('candidate_boot_sha256')!=m['files']['boot']['sha256'] or not prior.get('system_write_started'):raise ValueError('Owned install attempt required before rollback')
        current=sha(adb.read(BOOT,BOOT_BYTES))
        if current not in {m['expected_boot_before_sha256'],m['files']['boot']['sha256']}:raise ValueError('Unrelated current boot; rollback stopped')
        expected_boot=current;expected_system=None;system_key='original_system';boot_key='original_boot'
    preflight(adb,case,m,expected_boot,expected_system)
    p=case/(action+'-receipt-private.json')
    log={'scope':'android-t1-1','action':action,'candidate_boot_sha256':m['files']['boot']['sha256'],'system_write_started':False,'verified':False,'recovery_written':False,'userdata_written':False,'rebooted':False,'automatic_retry':False};receipt(p,log)
    write_system(adb,case/FILES[system_key],m['files'][system_key]['sha256'],log,p)
    # Boot-last means an incomplete system transfer leaves the known graphics boot intact.
    target=(case/FILES[boot_key]).read_bytes()
    result=restore(adb,target,{'boot':m['files'][boot_key],'recovery':{'bytes':RECOVERY_BYTES,'sha256':RECOVERY_SHA}},expected_boot,case/(action+'-boot-receipt-private.json'),operation='Android T1 '+action+'; exact system verified before boot write')
    if not result.get('verified'):raise ValueError('Boot verification incomplete')
    log.update(verified=True,boot_readback_verified=True,finished_at=time.time());update_receipt(p,log)
    return {'action':action,'verified':True,'rebooted':False,'recovery_written':False,'userdata_written':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=Path,required=True);p.add_argument('--selector-file',type=Path,required=True);p.add_argument('action',choices=['preflight','verify-installed','install','boot','rollback']);a=p.parse_args()
    selector=json.loads(a.selector_file.read_text())['selector']
    if not isinstance(selector,str) or not selector or selector.startswith('-'):raise ValueError('Pinned selector required')
    lock=(a.case/'.device-operation.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    print(json.dumps(run(a.case,AndroidAdb('adb',selector),a.action)))
