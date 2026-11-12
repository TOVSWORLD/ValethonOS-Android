#!/usr/bin/env python3
"""Native link checks plus exact FunctionFS hold and console ordering sources."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from verify_usb_console_build import verify

def check(build,baseline,source,ffs_report,queue_report,entry_report):
    r=verify(build,baseline,source)
    sources={'drivers/usb/gadget/function/f_fs.c':ffs_report['patched_sha256'],
             'drivers/usb/gadget/function/u_serial.c':queue_report['patched_sha256'],
             'kernel/kexec_core.c':entry_report['patched_sha256']}
    for name,expected in sources.items():
        if hashlib.sha256((source/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('Diagnostic source differs: '+name)
    nm=subprocess.run(['aarch64-linux-gnu-nm','--defined-only',str(build/'vmlinux')],capture_output=True,text=True,check=True).stdout
    symbols={x.split()[-1] for x in nm.splitlines() if len(x.split())==3}
    for name in ['__param_ft_hold_adb','__param_ft_hold_trial']:
        if name not in symbols:raise ValueError('Hold parameter not linked: '+name)
    elf=(build/'vmlinux').read_bytes()
    for s in [b'usb_f_fs.ft_hold_adb',b'usb_f_fs.ft_hold_trial',b'KXUSB_FFS trial=',b'KXHANDOFF native_entry=1 image_present=1']:
        if s not in elf:raise ValueError('Hold parameter/marker missing')
    code=subprocess.run(['aarch64-linux-gnu-objdump','-dr',str(build/'kernel/kexec_core.o')],capture_output=True,text=True,check=True).stdout
    if code.count('R_AARCH64_CALL26\tmsleep')!=1:raise ValueError('Expected single bounded diagnostic msleep call')
    r.update(scope='Default-off FunctionFS last-close hold and console queue ordering; native CPU/relocation route unchanged',
             ffs_console_hold_linked=True,ffs_hold_default_enabled=False,
             console_queue_ownership_before_submit=True,diagnostic_source_sha256=sources,
             diagnostic_route_console_dwell_ms=1000,native_entry_checkpoint_linked=True,
             usb_boot_capture_qualified=False,hardware_execution=False)
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['build','baseline-config','source','ffs-report','queue-report','output']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--entry-report','--reboot-report',dest='entry_report',type=Path,required=True)
    a=p.parse_args();r=check(a.build,a.baseline_config,a.source,json.loads(a.ffs_report.read_text()),json.loads(a.queue_report.read_text()),json.loads(a.entry_report.read_text()))
    a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
