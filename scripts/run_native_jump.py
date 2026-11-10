#!/usr/bin/env python3
"""Default read-only; exact approval permits one native load and orderly jump request."""
import argparse,hashlib,json,os,re,secrets,time
from pathlib import Path
from run_pstore_warm_reboot import LabADB
from run_native_source_boot import facts,ram_guard,BOOT_SHA,NATIVE_CONFIG,ORIGINAL_CONFIG
SCOPE='native-kexec-first-jump-1'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(device,lab_package,manifest,client_report,output,authorization=None):
 m=json.loads(manifest.read_text());c=json.loads(client_report.read_text());runner=sha(Path(__file__).read_bytes())
 if c['manifest_sha256']!=sha(manifest.read_bytes()) or c['execute_implemented'] is not False:raise ValueError('Client/manifest binding required')
 if m['original_boot_sha256']!=BOOT_SHA or m['entry']!=0x42018000 or not re.fullmatch('[0-9a-f]{32}',m['trial_id']):raise ValueError('Reviewed target required')
 if [s['file'] for s in m['segments']]!=['image.bin','metadata.bin','initrd.bin']:raise ValueError('Exact bundle filenames required')
 approval={'scope':SCOPE,'runner_sha256':runner,'manifest_sha256':sha(manifest.read_bytes()),'client_sha256':c['client_sha256'],'trial_id':m['trial_id'],'owner_approved':True,'owner_available':True,'maximum_loads':1,'maximum_jump_requests':1,'boot_writes_allowed':False,'recovery_writes_allowed':False,'automatic_reboot_allowed':False}
 if authorization is not None:
  a=json.loads(authorization.read_text())
  if any(type(a.get(k)) is not type(v) or a.get(k)!=v for k,v in approval.items()):raise ValueError('Exact current jump approval required')
 output.mkdir(mode=0o700)
 if authorization is not None:
  fd=os.open(str(authorization)+'.consumed',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
 r={'scope':SCOPE,'runner_sha256':runner,'manifest_sha256':approval['manifest_sha256'],'client_sha256':c['client_sha256'],'trial_id':m['trial_id'],'load_attempts':0,'unload_attempts':0,'jump_requests':0,'complete':False,'jump_proven':False,'boot_written':False,'recovery_written':False,'normal_shell_restored':False,'owner_attention_required':False}
 folder=None;before=None
 def save():
  with (output/'result.json').open('w') as h:
   os.fchmod(h.fileno(),0o600);json.dump(r,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
 def root():device.adb('root');device.adb('wait-for-device')
 def loaded():return device.shell('cat /sys/kernel/kexec_loaded').strip()
 def source():
  f=facts(device)
  if f['boot']!=BOOT_SHA or f['config']!=NATIVE_CONFIG:raise ValueError('Native RAM kernel and original flash required')
  if sha(device.shell('cat /sys/firmware/fdt'))!=m['source_dtb_sha256']:raise ValueError('Source DT changed')
  return f
 try:
  save();root();before=source();ram_guard(device)
  if loaded()!=b'0':raise ValueError('Refuse pre-existing loaded image')
  assets=[('native-load',c['client_sha256'])]+[(s['file'],s['sha256']) for s in m['segments']]
  for name,digest in assets:
   if device.host(['sha256sum',lab_package+'/'+name]).stdout.split()[0].decode()!=digest:raise ValueError('Prepared lab package differs')
  r['preflight']='passed';save()
  if authorization is None:r['complete']=True;return r
  folder='/dev/kx-jump-'+secrets.token_hex(12);device.shell('mkdir -m 700 '+folder)
  for name,digest in assets:
   path=folder+'/'+name;device.adb('push',lab_package+'/'+name,path);device.shell('chmod '+('700 ' if name=='native-load' else '600 ')+path)
   if device.shell('sha256sum '+path).split()[0].decode()!=digest:raise ValueError('RAM asset differs')
  if source()!=before or loaded()!=b'0':raise ValueError('Source changed before load')
  r['load_attempts']=1;save();device.shell(folder+'/native-load --load '+folder,timeout=90)
  if loaded()!=b'1':raise RuntimeError('Native loaded state not observed')
  r['native_load_verified']=True;save()
  if source()!=before:raise ValueError('Source changed after load')
  # Android init owns the ordinary service/filesystem shutdown. No direct reboot syscall.
  r['jump_requests']=1;save()
  try:device.shell('setprop sys.powerctl reboot,valethon-kexec',timeout=15)
  except RuntimeError:r['request_transport_uncertain']=True;save()
  end=time.monotonic()+300;returned=False
  while time.monotonic()<end:
   try:
    ident=device.shell('cat /proc/sys/kernel/random/boot_id',timeout=10).strip().decode()
    if re.fullmatch('[0-9a-f-]{36}',ident) and ident!=before['boot_id'] and device.shell('getprop sys.boot_completed',timeout=10).strip()==b'1':returned=True;break
   except RuntimeError:pass
   time.sleep(1)
  if not returned:raise RuntimeError('Target Android not observed; no reboot retry')
  root();after=facts(device)
  if after['boot']!=BOOT_SHA or after['config']!=ORIGINAL_CONFIG:raise ValueError('Unexpected returned kernel or flash')
  if device.shell('cat /proc/device-tree/chosen/valethon,kexec-trial')!=m['trial_id'].encode()+b'\0':raise ValueError('Changed boot alone is insufficient; target trial DT marker absent')
  r['jump_proven']=True;r['original_boot_verified']=True;r['recovery_verified']=True;r['complete']=True;return r
 except BaseException as error:r['failure_kind']=type(error).__name__;r['owner_attention_required']=bool(r['jump_requests']);raise
 finally:
  # Only undo a load owned by this run before any shutdown request. No retry after request.
  if r['load_attempts'] and not r['jump_requests']:
   try:
    if loaded()==b'1':r['unload_attempts']=1;save();device.shell(folder+'/native-load --unload '+folder)
    if loaded()!=b'0':raise RuntimeError('Unload not verified')
   except BaseException:r['owner_attention_required']=True;r['complete']=False
  if folder and (not r['jump_requests'] or r['jump_proven']):
   try:
    device.shell('rm -f '+' '.join(folder+'/'+n for n in ['native-load','image.bin','metadata.bin','initrd.bin'])+'; if [ -d '+folder+' ]; then rmdir '+folder+'; fi')
   except BaseException:r['ram_cleanup_unconfirmed']=True;r['complete']=False;r['owner_attention_required']=True
  try:
   device.adb('unroot',timeout=20);device.adb('wait-for-device',timeout=30);r['normal_shell_restored']=b'uid=2000(' in device.shell('id',timeout=10)
  except BaseException:pass
  if not r['normal_shell_restored']:r['complete']=False;r['owner_attention_required']=True
  save()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['ssh-args','manifest','client-report','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--lab-package',required=True);p.add_argument('--authorization',type=Path);a=p.parse_args()
 try:
  r=run(LabADB(json.loads(a.ssh_args.read_text())),a.lab_package,a.manifest,a.client_report,a.output,a.authorization);print(json.dumps(r,indent=2));raise SystemExit(0 if r['complete'] else 1)
 except Exception as e:print(json.dumps({'error_kind':type(e).__name__,'message':str(e)}));raise SystemExit(1)
