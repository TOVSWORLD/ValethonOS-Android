#!/usr/bin/env python3
"""Exact USB console config profile plus existing native handoff link checks."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from verify_native_kexec_build import check,CONFIG_SHA as BASE_CONFIG
SERIAL_SHA='b27ef69e4ed90ee5fc2511eaebb001ad8d3c88ede0bde04cb962ce4e52fbb5f9'
ALLOWED={'CONFIG_USB_G_SERIAL','CONFIG_U_SERIAL_CONSOLE','CONFIG_USB_F_OBEX'}
def sha(b):return hashlib.sha256(b).hexdigest()
def values(text):
 result={}
 for line in text.splitlines():
  if line.startswith('CONFIG_') and '=' in line:k,v=line.split('=',1);result[k]=v
  elif m:=re.fullmatch('# (CONFIG_\w+) is not set',line):result[m[1]]='n'
 return result
def verify(build,baseline,source):
 old=baseline.read_bytes();new=(build/'.config').read_bytes()
 if sha(old)!=BASE_CONFIG:raise ValueError('Exact hardware-booted native baseline config required')
 a,b=values(old.decode()),values(new.decode());changes={k:{'before':a.get(k,'n'),'after':b.get(k,'n')} for k in a.keys()|b.keys() if a.get(k,'n')!=b.get(k,'n')}
 if set(changes)!=ALLOWED or any(v!={'before':'n','after':'y'} for v in changes.values()):raise ValueError('Only builtin serial/console/OBEX dependency changes allowed')
 if sha((source/'drivers/usb/gadget/legacy/serial.c').read_bytes())!=SERIAL_SHA:raise ValueError('Exact opt-in serial binding source required')
 result=check(build,expected_config_sha256=sha(new));elf=(build/'vmlinux').read_bytes()
 nm=subprocess.run(['aarch64-linux-gnu-nm','--defined-only',str(build/'vmlinux')],capture_output=True,text=True,check=True).stdout
 symbols={l.split()[-1] for l in nm.splitlines() if len(l.split())==3}
 for symbol in ['gserial_cons','gs_console_write','gs_console_setup','__param_ft_bind','__param_ft_trial']:
  if symbol not in symbols:raise ValueError('USB console/opt-in symbol absent: '+symbol)
 for marker in [b'g_serial.ft_bind',b'g_serial.ft_trial',b'KXUSB target_trial=']:
  if marker not in elf:raise ValueError('USB console parameter/marker missing')
 result.update(scope='USB kernel console + native handoff linked profile; not boot acceptance',usb_console_linked=True,serial_bind_is_opt_in=True,usb_profile_config_changes=changes,serial_source_sha256=SERIAL_SHA,live_acm_capture_already_observed=True,usb_boot_capture_qualified=False,watchdog_changes=False)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['build','baseline-config','source','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();r=verify(a.build,a.baseline_config,a.source);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
