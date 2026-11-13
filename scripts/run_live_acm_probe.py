#!/usr/bin/env python3
"""Default read-only. Exact approval: temporary ACM+ADB, device-side return to ADB."""
import argparse,hashlib,json,os,re,secrets,selectors,shlex,subprocess,time
from pathlib import Path
from run_pstore_warm_reboot import LabADB
from run_native_source_boot import ram_guard
SCOPE='usb-acm-live-capture-1'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(device,lab_package,build_report,out,authorization=None):
 b=json.loads(build_report.read_text());runner=sha(Path(__file__).read_bytes());nonce=secrets.token_hex(16)
 expected={'scope':SCOPE,'runner_sha256':runner,'helper_sha256':b['helper_sha256'],'receiver_sha256':b['receiver_sha256'],'owner_approved':True,'owner_available':True,'maximum_trial_launches':1,'stream_window_seconds':30,'boot_writes_allowed':False,'reboots_allowed':False}
 if authorization is not None:
  a=json.loads(authorization.read_text())
  if any(type(a.get(k)) is not type(v) or a.get(k)!=v for k,v in expected.items()):raise ValueError('Exact current ACM test approval required')
 out.mkdir(mode=0o700)
 if authorization is not None:
  f=os.open(str(authorization)+'.consumed',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(f)
 result={'scope':SCOPE,'runner_sha256':runner,'helper_sha256':b['helper_sha256'],'receiver_sha256':b['receiver_sha256'],'trial_launches':0,'complete':False,'host_received':False,'usb_mode_changed':False,'adb_only_restored':False,'normal_shell_restored':False,'boot_written':False,'reboot_requested':False,'owner_attention_required':False}
 folder=None;receiver=None;receipt=None;started=None
 def save():
  (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');(out/'result.json').chmod(0o600)
 def checks():
  if device.shell('getprop sys.usb.config').strip()!=b'adb' or device.shell('getprop sys.usb.state').strip()!=b'adb':raise ValueError('Original ADB-only mode required')
  if device.shell('cat /config/usb_gadget/g1/UDC').strip()!=b'musb-hdrc':raise ValueError('Expected bound UDC required')
  if device.shell('readlink -f /config/usb_gadget/g1/configs/b.1/f1').strip()!=b'/config/usb_gadget/g1/functions/ffs.adb':raise ValueError('Original ADB link differs')
  if device.shell('if [ -e /config/usb_gadget/g1/configs/b.1/f2 ] || [ -L /config/usb_gadget/g1/configs/b.1/f2 ]; then echo occupied; fi').strip():raise ValueError('Do not replace existing function')
 try:
  save();device.adb('root');device.adb('wait-for-device');checks();ram_guard(device)
  path=device.adb('get-devpath').stdout.strip().decode()
  if not path.startswith('usb:'):raise ValueError('Physical USB transport required')
  ids=device.shell('cat /config/usb_gadget/g1/idVendor /config/usb_gadget/g1/idProduct').decode().split()
  ids=[format(int(v,16),'04x') for v in ids]
  if len(ids)!=2 or not re.fullmatch('[0-9]+-[0-9]+(?:\\.[0-9]+)*',path[4:]):raise ValueError('Exact physical USB identity required')
  for name,key in [('acm-trial','helper_sha256'),('capture_live_acm_probe.py','receiver_sha256')]:
   if device.host(['sha256sum',lab_package+'/'+name]).stdout.split()[0].decode()!=b[key]:raise ValueError('Lab artifact differs')
  device.host(['sudo','-n','true'])
  result['preflight']='passed';save()
  if authorization is None:result['complete']=True;return result
  folder='/dev/kxusb-acm-'+nonce;device.shell('mkdir -m 700 '+folder);target=folder+'/acm-trial'
  device.adb('push',lab_package+'/acm-trial',target);device.shell('chmod 700 '+target)
  if device.shell('sha256sum '+target).split()[0].decode()!=b['helper_sha256']:raise ValueError('RAM helper differs')
  profile={'physical_path':path[4:],'vendor':ids[0],'product':ids[1],'trial':nonce,'allow_privileged_open':True};remoteout=lab_package+'/capture-'+nonce
  code='import json,sys,pathlib;sys.path.insert(0,'+repr(lab_package)+');from capture_live_acm_probe import capture;r=capture('+repr(profile)+',pathlib.Path('+repr(remoteout)+'));print(json.dumps(r))'
  receiver=subprocess.Popen(device.args+['python3 -c '+shlex.quote(code)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  sel=selectors.DefaultSelector();sel.register(receiver.stdout,selectors.EVENT_READ)
  if not sel.select(15) or receiver.stdout.readline()!=b'USB_ACM_RECEIVER_READY\n':raise RuntimeError('Receiver did not arm')
  checks();result['trial_launches']=1;result['usb_mode_change_requested']=True;save();started=time.monotonic()
  try:device.shell(target+' '+nonce,timeout=15)
  except RuntimeError:result['launch_transport_uncertain']=True
  stdout,stderr=receiver.communicate(timeout=60)
  try:capture=json.loads(stdout)
  except (ValueError,TypeError):raise RuntimeError('Invalid receiver result')
  result['capture']=capture;result['host_received']=capture.get('host_received') is True
  # Give the autonomous device helper its 30s stream window plus driver-close slack.
  remaining=started+50-time.monotonic()
  if remaining>0:time.sleep(remaining)
  device.adb('wait-for-device',timeout=30)
  receipt=device.shell('cat '+folder+'/receipt').decode();(out/'device-receipt-private.txt').write_text(receipt);result['usb_mode_changed']='unbind_complete errno=0\n' in receipt
  if 'restore_verified errno=0\n' not in receipt or 'finished errno=0\n' not in receipt:raise RuntimeError('Device-side restoration not verified')
  checks();result['adb_only_restored']=True
  if result['host_received']:
   raw=device.host(['cat',remoteout+'/capture-private.bin']).stdout
   if sha(raw)!=capture['capture_sha256']:raise ValueError('Captured bytes changed')
   with (out/'capture-private.bin').open('xb') as h:os.fchmod(h.fileno(),0o600);h.write(raw);h.flush();os.fsync(h.fileno())
  result['kernel_record_captured']='kernel_record_captured errno=0\n' in receipt
  result['complete']=result['host_received'] and result['kernel_record_captured'];return result
 except BaseException as error:result['failure_kind']=type(error).__name__;raise
 finally:
  if receiver and receiver.poll() is None:receiver.kill();receiver.wait(timeout=10)
  if result['trial_launches'] and not result['adb_only_restored'] and started is not None:
   remaining=started+50-time.monotonic()
   if remaining>0:time.sleep(remaining)
   try:
    device.adb('wait-for-device',timeout=20)
    receipt=device.shell('cat '+folder+'/receipt').decode();(out/'device-receipt-private.txt').write_text(receipt)
    result['usb_mode_changed']='unbind_complete errno=0\n' in receipt
    checks()
    if 'finished errno=0\n' in receipt:result['adb_only_restored']=True
   except BaseException:pass
  if folder and (not result['trial_launches'] or result['adb_only_restored']):
   try:device.shell('rm -f '+folder+'/acm-trial '+folder+'/receipt; rmdir '+folder)
   except BaseException:result['ram_cleanup_unconfirmed']=True;result['complete']=False
  try:
   device.adb('unroot',timeout=20);device.adb('wait-for-device',timeout=30);result['normal_shell_restored']=b'uid=2000(' in device.shell('id',timeout=10)
  except BaseException:pass
  if not result['normal_shell_restored'] or (result['trial_launches'] and not result['adb_only_restored']):result['complete']=False;result['owner_attention_required']=True
  save()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['ssh-args','build-report','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--lab-package',required=True);p.add_argument('--authorization',type=Path);a=p.parse_args()
 try:
  r=run(LabADB(json.loads(a.ssh_args.read_text())),a.lab_package,a.build_report,a.output,a.authorization);print(json.dumps(r,indent=2));raise SystemExit(0 if r['complete'] else 1)
 except Exception as e:print(json.dumps({'error_kind':type(e).__name__,'message':str(e)}));raise SystemExit(1)
