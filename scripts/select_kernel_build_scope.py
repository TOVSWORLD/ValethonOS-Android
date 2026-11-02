#!/usr/bin/env python3
"""Choose a single explicit provider build; preserve the USB-off diagnostic scope."""
import argparse
import json
from pathlib import Path
import subprocess
USB_PATHS={'scripts/apply_usb_port.py','scripts/select_kernel_build_scope.py'}
MODES={'lab-log','clocks','clocks-pinctrl','providers','usb-providers','usb-acm-diagnostic','diagnostic','sym827-provider','mipi-provider','dsi-provider','pwm-provider'}


def choose(event,changed=(),mode='diagnostic',argument_profile='none',emulated_boot=False):
    if event=='pull_request':
        pwm=any(p in {'scripts/apply_pwm_port.py','scripts/build_pwm_provider.sh'} or p.startswith('projects/firetabs-android/kernel/pwm-port/') for p in changed)
        if pwm:
            if any(p.startswith('projects/firetabs-android/kernel/usb-port/') or p.startswith('projects/firetabs-android/kernel/usb-acm/') or p in {'scripts/apply_usb_port.py','scripts/usb_acm_config.py'} for p in changed):raise ValueError('Mixed USB/PWM source scope requires separate builds')
            return {'mode':'pwm-provider','argument_profile':'none','qemu':False}
        dsi=any(p in {'scripts/apply_dsi_port.py','scripts/build_dsi_provider.sh'} or p.startswith('projects/firetabs-android/kernel/dsi-port/') and (p.endswith('.patch') or p.endswith('inputs.json') or p.endswith('.h')) for p in changed)
        if dsi:
            if any(p.startswith('projects/firetabs-android/kernel/usb-port/') or p.startswith('projects/firetabs-android/kernel/usb-acm/') or p in {'scripts/apply_usb_port.py','scripts/usb_acm_config.py'} for p in changed):raise ValueError('Mixed USB/DSI source scope requires a separate build')
            return {'mode':'dsi-provider','argument_profile':'none','qemu':False}
        mipi=any(p in {'scripts/apply_mipi_port.py','scripts/build_mipi_provider.sh'} or p.startswith('projects/firetabs-android/kernel/mipi-port/') and (p.endswith('.patch') or p.endswith('inputs.json')) for p in changed)
        if mipi:
            if any(p.startswith('projects/firetabs-android/kernel/usb-port/') or p.startswith('projects/firetabs-android/kernel/usb-acm/') or p in {'scripts/apply_usb_port.py','scripts/usb_acm_config.py'} for p in changed):raise ValueError('Mixed USB/MIPI source scope requires a separate build')
            return {'mode':'mipi-provider','argument_profile':'none','qemu':False}
        sym=any(p in {'scripts/apply_sym827_port.py','scripts/build_sym827_provider.sh'} or p.startswith('projects/firetabs-android/kernel/regulator-port/') for p in changed)
        if sym:
            if any(p.startswith('projects/firetabs-android/kernel/usb-port/') or p.startswith('projects/firetabs-android/kernel/usb-acm/') or p in {'scripts/apply_usb_port.py','scripts/usb_acm_config.py'} for p in changed):raise ValueError('Mixed USB/SYM827 source scope requires a separate build')
            return {'mode':'sym827-provider','argument_profile':'none','qemu':False}
        acm=any(p in {'scripts/usb_acm_config.py','projects/firetabs-android/kernel/usb-acm/fragment.config','projects/firetabs-android/kernel/usb-acm/profile.json'} for p in changed)
        if acm:return {'mode':'usb-acm-diagnostic','argument_profile':'none','qemu':False}
        usb=any(p in USB_PATHS or p.startswith('projects/firetabs-android/kernel/usb-port/') and (p.endswith('.patch') or p.endswith('inputs.json')) for p in changed)
        return {'mode':'usb-providers' if usb else 'diagnostic','argument_profile':'none' if usb else 'generic-force','qemu':not usb}
    if mode not in MODES or argument_profile not in ['none','generic-force']:raise ValueError('Unknown build scope')
    if mode!='diagnostic' and (argument_profile!='none' or emulated_boot):raise ValueError('Generic diagnostic QEMU requires diagnostic mode')
    return {'mode':mode,'argument_profile':argument_profile,'qemu':emulated_boot}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--event',required=True);p.add_argument('--mode',default='diagnostic');p.add_argument('--argument-profile',default='none');p.add_argument('--emulated-boot',choices=['true','false'],default='false');p.add_argument('--github-output',type=Path);a=p.parse_args()
    changed=subprocess.check_output(['git','diff','--no-renames','--name-only','HEAD^1','HEAD'],text=True).splitlines() if a.event=='pull_request' else []
    result=choose(a.event,changed,a.mode,a.argument_profile,a.emulated_boot=='true')
    if a.github_output:
        with a.github_output.open('a') as f:
            for key,value in result.items():f.write(key+'='+str(value).lower()+'\n')
    print(json.dumps({'scope':'One Linux build selected; USB provider compilation is not device transport','usb_scope_selected':result['mode'] in ['usb-providers','usb-acm-diagnostic'],**result},indent=2))

if __name__=='__main__':main()
