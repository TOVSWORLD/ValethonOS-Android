#!/usr/bin/env python3
"""Native link checks plus exact FunctionFS hold and console ordering sources."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from verify_usb_console_build import verify

def check(build,baseline,source,ffs_report,queue_report,entry_report,early_cpu_report=None):
    r=verify(build,baseline,source)
    sources={'drivers/usb/gadget/function/f_fs.c':ffs_report['patched_sha256'],
             'drivers/usb/gadget/function/u_serial.c':queue_report['patched_sha256'],
             'kernel/kexec_core.c':entry_report['patched_sha256']}
    if early_cpu_report is not None:
        from prepare_early_cpu_shutdown import SOURCE_SHA
        if early_cpu_report['original_sha256'] != SOURCE_SHA or entry_report['patched_sha256'] != SOURCE_SHA:
            raise ValueError('Early CPU experiment must extend exact native-entry profile')
        sources['kernel/kexec_core.c'] = early_cpu_report['patched_sha256']
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
    expected_dwells = 2 if early_cpu_report is not None else 1
    if code.count('R_AARCH64_CALL26\tmsleep')!=expected_dwells:raise ValueError('Unexpected diagnostic msleep call count')
    if early_cpu_report is not None:
        for name in ['freeze_secondary_cpus','mt_kexec_secondary_off_gate','kernel_restart_prepare']:
            if 'R_AARCH64_CALL26\t'+name not in code:
                raise ValueError('Early CPU shutdown call missing: '+name)
        if b'KXHANDOFF early_cpu_gate=passed survivor=0' not in elf:
            raise ValueError('Early CPU gate marker not linked')
    r.update(scope='Default-off FunctionFS last-close hold and console queue ordering; native CPU/relocation route unchanged',
             ffs_console_hold_linked=True,ffs_hold_default_enabled=False,
             console_queue_ownership_before_submit=True,diagnostic_source_sha256=sources,
             diagnostic_route_console_dwell_ms=1000,native_entry_checkpoint_linked=True,
             usb_boot_capture_qualified=False,hardware_execution=False)
    if early_cpu_report is not None:
        r.update(scope='MT8163 PID1 CPU shutdown before device shutdown; USB/native gates retained; hardware unqualified',
                 early_cpu_shutdown_before_devices=True,early_cpu_source_report=early_cpu_report,
                 early_cpu_gate_console_dwell_ms=1000)
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['build','baseline-config','source','ffs-report','queue-report','output']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--entry-report','--reboot-report',dest='entry_report',type=Path,required=True)
    p.add_argument('--early-cpu-report',type=Path)
    a=p.parse_args();r=check(a.build,a.baseline_config,a.source,json.loads(a.ffs_report.read_text()),json.loads(a.queue_report.read_text()),json.loads(a.entry_report.read_text()),json.loads(a.early_cpu_report.read_text()) if a.early_cpu_report else None)
    a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
