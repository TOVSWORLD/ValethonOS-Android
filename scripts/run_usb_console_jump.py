#!/usr/bin/env python3
"""One profile-bound native jump; target success is fresh USB kernel console receipt."""
import argparse,hashlib,json,os,re,secrets,selectors,shlex,subprocess
from pathlib import Path
from run_pstore_warm_reboot import LabADB
from run_native_source_boot import facts,ram_guard,BOOT_SHA
from verify_usb_console_build import ALLOWED,SERIAL_SHA
from prepare_native_jump_bundle import target_prefix
SCOPE='native-usb-console-jump-1'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(device,lab_package,manifest,client_report,linked,output,authorization=None,source_report=None):
 m=json.loads(manifest.read_text());c=json.loads(client_report.read_text());config=linked['artifacts']['.config']['sha256'];image=linked['artifacts']['arch/arm64/boot/Image']['sha256'];trial=m['trial_id'];runner=sha(Path(__file__).read_bytes())
 if m.get('offline_preview') is True:raise ValueError('Offline preview bundle cannot be loaded')
 if linked.get('usb_console_linked') is not True or linked.get('serial_bind_is_opt_in') is not True or linked.get('serial_source_sha256')!=SERIAL_SHA or set(linked.get('usb_profile_config_changes',{}))!=ALLOWED:raise ValueError('Verified USB console profile required')
 if any(v!={'before':'n','after':'y'} for v in linked['usb_profile_config_changes'].values()):raise ValueError('Config drift')
 if not re.fullmatch('[0-9a-f]{32}',trial) or m.get('source_config_sha256')!=config or m.get('target_config_sha256')!=config or m['target_image_sha256']!=image or m['original_boot_sha256']!=BOOT_SHA:raise ValueError('Exact source/target profile required')
 cpu_limit=m.get('target_cpu_limit')
 if m['bootargs_prefix']!=target_prefix(trial,cpu_limit) or m['entry']!=0x42018000 or [s['file'] for s in m['segments']]!=['image.bin','metadata.bin','initrd.bin']:raise ValueError('Reviewed target parameters/layout required')
 if cpu_limit is not None and (source_report is None or source_report.get('functionfs_hold') is not True or linked.get('native_entry_checkpoint_linked') is not True):raise ValueError('CPU0-only target requires the proven source capture profile')
 if c['manifest_sha256']!=sha(manifest.read_bytes()) or c['execute_implemented'] is not False:raise ValueError('Bound load-only client required')
 here=Path(__file__).parent;receiver_sha=sha((here/'capture_usb_kernel_console.py').read_bytes());shared_sha=sha((here/'capture_live_acm_probe.py').read_bytes())
 expected={'scope':SCOPE,'runner_sha256':runner,'manifest_sha256':sha(manifest.read_bytes()),'client_sha256':c['client_sha256'],'target_image_sha256':image,'native_config_sha256':config,'receiver_sha256':receiver_sha,'shared_receiver_sha256':shared_sha,'owner_approved':True,'owner_available':True,'maximum_loads':1,'maximum_jump_requests':1,'boot_writes_allowed':False,'automatic_reboot_allowed':False}
 if source_report is not None:
  expected.update(scope='native-usb-source-target-console-jump-1',source_capture_report_sha256=sha(json.dumps(source_report,sort_keys=True).encode()),source_capture_manager_sha256=sha((here/'source_usb_console_trial.py').read_bytes()))
  if source_report.get('receiver_sha256')!=sha((here/'capture_source_usb_console.py').read_bytes()):raise ValueError('Exact source receiver required')
 if cpu_limit is not None:expected.update(scope='native-single-cpu-usb-source-target-console-jump-1',target_cpu_limit=1)
 if authorization is not None:
  a=json.loads(authorization.read_text())
  if any(type(a.get(k)) is not type(v) or a.get(k)!=v for k,v in expected.items()):raise ValueError('Exact USB console jump approval required')
 output.mkdir(mode=0o700)
 if authorization is not None:
  f=os.open(str(authorization)+'.consumed',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(f)
 r={'scope':expected['scope'],'runner_sha256':runner,'manifest_sha256':expected['manifest_sha256'],'target_image_sha256':image,'native_config_sha256':config,'trial_id':trial,'load_attempts':0,'unload_attempts':0,'jump_requests':0,'complete':False,'target_entry_proven':False,'boot_written':False,'recovery_written':False,'owner_return_required':False,'normal_shell_restored':False};folder=None;receiver=None;source_capture=None
 if cpu_limit is not None:r['target_cpu_limit']=1
 def save():
  with (output/'result.json').open('w') as h:os.fchmod(h.fileno(),0o600);json.dump(r,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
 def loaded():return device.shell('cat /sys/kernel/kexec_loaded').strip()
 def source():
  f=facts(device)
  if f['boot']!=BOOT_SHA or f['config']!=config or sha(device.shell('cat /sys/firmware/fdt'))!=m['source_dtb_sha256']:raise ValueError('Current source kernel/DT/flash differs')
  return f
 try:
  save();device.adb('root');device.adb('wait-for-device');before=source();ram_guard(device)
  if loaded()!=b'0':raise ValueError('Pre-existing image must not be replaced')
  path=device.adb('get-devpath').stdout.strip().decode()
  if not path.startswith('usb:') or not re.fullmatch(r'[0-9]+-[0-9]+(?:\.[0-9]+)*',path[4:]):raise ValueError('Physical USB port required')
  assets=[('native-load',c['client_sha256'])]+[(s['file'],s['sha256']) for s in m['segments']]
  for name,digest in assets+[('capture_usb_kernel_console.py',receiver_sha),('capture_live_acm_probe.py',shared_sha)]:
   if device.host(['sha256sum',lab_package+'/'+name]).stdout.split()[0].decode()!=digest:raise ValueError('Lab artifact differs')
  device.host(['sudo','-n','true']);r['preflight']='passed';save()
  if authorization is None:r['complete']=True;return r
  if source_report is not None:
   from source_usb_console_trial import SourceCapture
   source_capture=SourceCapture(device,lab_package,source_report,trial,path[4:],output)
   source_capture.start();r['source_console_proven_before_load']=True;save()
  folder='/dev/kx-console-'+secrets.token_hex(12);device.shell('mkdir -m 700 '+folder)
  for name,digest in assets:
   target=folder+'/'+name;device.adb('push',lab_package+'/'+name,target);device.shell('chmod '+('700 ' if name=='native-load' else '600 ')+target)
   if device.shell('sha256sum '+target).split()[0].decode()!=digest:raise ValueError('RAM artifact differs')
  profile={'purpose':'native-usb-console-target-1','physical_path':path[4:],'vendor':'0525','product':'a4a7','trial':trial,'wait_seconds':300,'after_marker_seconds':10,'allow_privileged_open':True};remoteout=lab_package+'/target-capture-'+trial
  code='import sys,pathlib,json;sys.path.insert(0,'+repr(lab_package)+');from capture_usb_kernel_console import capture;r=capture('+repr(profile)+',pathlib.Path('+repr(remoteout)+'));print(json.dumps(r))'
  receiver=subprocess.Popen(device.args+['python3 -c '+shlex.quote(code)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  sel=selectors.DefaultSelector();sel.register(receiver.stdout,selectors.EVENT_READ)
  if not sel.select(15) or receiver.stdout.readline()!=b'USB_KERNEL_CONSOLE_READY\n':raise RuntimeError('USB receiver did not arm')
  if source()!=before or loaded()!=b'0':raise ValueError('Source changed before load')
  r['load_attempts']=1;save();device.shell(folder+'/native-load --load '+folder,timeout=90)
  if loaded()!=b'1':raise RuntimeError('Loaded state not observed')
  r['native_load_verified']=True
  if source()!=before:raise ValueError('Source changed after load')
  if source_capture:source_capture.intent()
  r['original_boot_verified_before_jump']=True;r['recovery_verified_before_jump']=True;r['jump_requests']=1;r['owner_return_required']=True;save()
  try:device.shell('setprop sys.powerctl reboot,valethon-kexec',timeout=15)
  except RuntimeError:r['request_transport_uncertain']=True;save()
  stdout,stderr=receiver.communicate(timeout=330);capture=json.loads(stdout);r['capture']=capture
  if capture.get('capture_bytes',0):
   raw=device.host(['cat',remoteout+'/kernel-console-private.bin'],timeout=30).stdout
   if sha(raw)!=capture['capture_sha256']:raise ValueError('Host capture hash differs')
   with (output/'kernel-console-private.bin').open('xb') as h:os.fchmod(h.fileno(),0o600);h.write(raw);h.flush();os.fsync(h.fileno())
  try:
   trace=device.host(['cat',remoteout+'/usb-port-events-private.json'],timeout=20).stdout
   with (output/'usb-port-events-private.json').open('xb') as h:os.fchmod(h.fileno(),0o600);h.write(trace);h.flush();os.fsync(h.fileno())
  except RuntimeError:r['usb_metadata_copy_unconfirmed']=True
  r['target_entry_proven']=capture.get('target_entry_proven') is True;r['complete']=capture.get('complete') is True;r['normal_android_boot_qualified']=False
  return r
 except BaseException as error:r['failure_kind']=type(error).__name__;raise
 finally:
  if receiver and receiver.poll() is None:receiver.kill();receiver.wait(timeout=10)
  if source_capture:
   try:
    if r['jump_requests']:r['source_capture']=source_capture.collect()
    else:source_capture.abort()
   except Exception as error:r['source_capture_collection_failure']=type(error).__name__;r['owner_return_required']=True
  if not r['jump_requests']:
   if r['load_attempts']:
    try:
     if loaded()==b'1':r['unload_attempts']=1;save();device.shell(folder+'/native-load --unload '+folder)
     if loaded()!=b'0':raise RuntimeError('Unload not verified')
    except BaseException:r['owner_return_required']=True;r['complete']=False
   if folder:
    try:device.shell('rm -f '+' '.join(folder+'/'+n for n in ['native-load','image.bin','metadata.bin','initrd.bin'])+'; rmdir '+folder)
    except BaseException:r['ram_cleanup_unconfirmed']=True;r['complete']=False
   try:
    device.adb('unroot',timeout=20);device.adb('wait-for-device',timeout=30);r['normal_shell_restored']=b'uid=2000(' in device.shell('id',timeout=10)
   except BaseException:pass
   if not r['normal_shell_restored']:r['owner_return_required']=True;r['complete']=False
  # After request, do not touch a partially shut-down OS or send console commands.
  save()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['ssh-args','manifest','client-report','linked-report','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--lab-package',required=True);p.add_argument('--authorization',type=Path);p.add_argument('--source-console-report',type=Path);a=p.parse_args()
 try:
  r=run(LabADB(json.loads(a.ssh_args.read_text())),a.lab_package,a.manifest,a.client_report,json.loads(a.linked_report.read_text()),a.output,a.authorization,json.loads(a.source_console_report.read_text()) if a.source_console_report else None);print(json.dumps(r,indent=2));raise SystemExit(0 if r['complete'] else 1)
 except Exception as e:print(json.dumps({'error_kind':type(e).__name__,'message':str(e)}));raise SystemExit(1)
