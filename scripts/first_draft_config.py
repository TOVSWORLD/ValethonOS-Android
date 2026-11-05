#!/usr/bin/env python3
"""One combined MT8163 kernel draft; no physical admission or recovery policy."""
import argparse
import json
from pathlib import Path
import subprocess
import diagnostic_config
import lab_log_config


def requirements():
    result = lab_log_config.requirements(retained=True)
    result.update({name:'y' for name in ['I2C','SPI','INPUT','HID','VT','DRM','DRM_MEDIATEK',
        'PHY_MTK_MIPI_DSI','RESET_CONTROLLER','PWM','PWM_MTK_DISP','REGULATOR_FAN53555',
        'PM','SUSPEND','PM_SLEEP','HOTPLUG_CPU','FTRACE','FTRACE_SYSCALLS','EVENT_TRACING','PRINTK_TIME','IKCONFIG','IKCONFIG_PROC','KALLSYMS','ANDROID_BINDER_IPC']})
    result.update({'LOG_BUF_SHIFT':'20','LOCALVERSION':'"-valethon-draft1"',
                   'LOCALVERSION_AUTO':'n','PANIC_TIMEOUT':'0'})
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['apply','check']);p.add_argument('config',type=Path)
    p.add_argument('--source',type=Path);a=p.parse_args();expected=requirements()
    if a.mode=='check':
        diagnostic_config.check(a.config.read_text(),expected)
        print(json.dumps({'combined_draft_config':True,'hardware_qualified':False,'required':expected},indent=2));return
    if a.source is None:p.error('--source required')
    for name,value in expected.items():
        command=[str(a.source/'scripts/config'),'--file',str(a.config)]
        if value.startswith('"'):command+=['--set-str',name,value[1:-1]]
        elif value in ['y','n']:command+=['--enable' if value=='y' else '--disable',name]
        else:command+=['--set-val',name,value]
        subprocess.run(command,check=True)

if __name__=='__main__':main()
