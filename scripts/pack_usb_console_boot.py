#!/usr/bin/env python3
"""Offline source-boot package for a verified USB-console/native kernel profile."""
import argparse,hashlib,json
from pathlib import Path
from pack_native_kexec_boot import assemble
from verify_usb_console_build import ALLOWED,SERIAL_SHA

def pack(original,image,linked):
 for name in ['usb_console_linked','serial_bind_is_opt_in','arm64_syscall_104_is_kexec_load','handoff_gate_wired']:
  if linked.get(name) is not True:raise ValueError('Verified console/native link profile required: '+name)
 if linked.get('serial_source_sha256')!=SERIAL_SHA or set(linked.get('usb_profile_config_changes',{}))!=ALLOWED:raise ValueError('Exact USB profile required')
 if any(v!={'before':'n','after':'y'} for v in linked['usb_profile_config_changes'].values()):raise ValueError('USB config drift')
 config=linked['artifacts']['.config']['sha256']
 candidate,r=assemble(original,image,linked,expected_config_sha256=config)
 r.update(scope='USB-console native source boot; default legacy gadget bind disabled',usb_console_linked=True,serial_bind_is_opt_in=True,console_capture_at_boot_qualified=False,source_ramdisk_and_cmdline_unchanged=True,security_changes=False,watchdog_changes=False)
 return candidate,r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['original-boot','image','linked-report','out']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();candidate,r=pack(a.original_boot.read_bytes(),a.image.read_bytes(),json.loads(a.linked_report.read_text()));a.out.mkdir(mode=0o700)
 for name,data in [('boot-full.img',candidate),('original-boot.img',a.original_boot.read_bytes()),('report.json',(json.dumps(r,indent=2)+'\n').encode())]:
  f=a.out/name;f.write_bytes(data);f.chmod(0o600)
 print(json.dumps(r,indent=2))
