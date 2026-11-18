#!/usr/bin/env python3
"""Profile-bound wrapper for the proven one-boot/restore source-kernel runner."""
import argparse,hashlib,json
from pathlib import Path
import run_native_source_boot as base
from verify_usb_console_build import ALLOWED,SERIAL_SHA
SCOPE='usb-console-native-source-boot-1'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(device,lab_package,report,linked,output,authorization=None):
 if linked.get('usb_console_linked') is not True or linked.get('serial_bind_is_opt_in') is not True or linked.get('serial_source_sha256')!=SERIAL_SHA:raise ValueError('Linked opt-in USB console profile required')
 changes=linked.get('usb_profile_config_changes',{})
 if set(changes)!=ALLOWED or any(v!={'before':'n','after':'y'} for v in changes.values()):raise ValueError('Only reviewed USB configuration changes admitted')
 config=linked['artifacts']['.config']['sha256']
 if report['resolved_config_sha256']!=config or report.get('serial_bind_is_opt_in') is not True:raise ValueError('Wrong source boot package')
 if linked['artifacts']['arch/arm64/boot/Image']['sha256']!=report['image_sha256']:raise ValueError('Image differs from linked profile')
 wrapper=sha(Path(__file__).read_bytes())
 if authorization is not None:
  a=json.loads(authorization.read_text())
  if a.get('profile_runner_sha256')!=wrapper or a.get('native_config_sha256')!=config:raise ValueError('Exact profile wrapper/config approval required')
 old_scope,old_config=base.SCOPE,base.NATIVE_CONFIG
 try:
  base.SCOPE=SCOPE;base.NATIVE_CONFIG=config
  r=base.run(device,lab_package,report,output,authorization)
  r['profile_runner_sha256']=wrapper
  with (output/'result.json').open('w') as h:json.dump(r,h,indent=2);h.write('\n')
  return r
 finally:base.SCOPE=old_scope;base.NATIVE_CONFIG=old_config
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['ssh-args','package-report','linked-report','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--lab-package',required=True);p.add_argument('--authorization',type=Path);a=p.parse_args()
 try:
  r=run(base.LabADB(json.loads(a.ssh_args.read_text())),a.lab_package,json.loads(a.package_report.read_text()),json.loads(a.linked_report.read_text()),a.output,a.authorization);print(json.dumps(r,indent=2));raise SystemExit(0 if r['complete'] else 1)
 except Exception as e:print(json.dumps({'error_kind':type(e).__name__,'message':str(e)}));raise SystemExit(1)
