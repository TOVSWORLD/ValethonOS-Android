#!/usr/bin/env python3
"""Read-only cached sysfs metadata for one selected USB port. Never open a TTY.

No serial/manufacturer/product strings, unrelated ports, uevents, control requests,
udev changes or target data reads. Events are private; physical origin of a kernel
log cannot be qualified by this observer alone.
"""
import argparse
import json
import os
from pathlib import Path
import re
import time


def snapshot(port, sysroot=Path('/sys')):
    if not re.fullmatch(r'[0-9]{1,3}-[0-9]{1,3}(?:\.[0-9]{1,3}){0,6}',port):
        raise ValueError('One explicit physical USB port required')
    device=sysroot/'bus/usb/devices'/port
    if not device.exists():return {'present':False}
    def read(path):
        try:return path.read_text().strip()
        except FileNotFoundError:return None
    result={'present':True,'vendor':read(device/'idVendor'),'product':read(device/'idProduct'),
            'device_class':read(device/'bDeviceClass'),'speed':read(device/'speed'),'interfaces':[]}
    for interface in sorted(device.glob(port+':*')):
        if len(result['interfaces'])>=16:raise ValueError('Interface metadata bound exceeded')
        driver=None
        try:driver=(interface/'driver').resolve(strict=True).name
        except FileNotFoundError:pass
        tty=sorted(p.name for p in (interface/'tty').glob('ttyACM*'))
        if len(tty)>8:raise ValueError('TTY metadata bound exceeded')
        result['interfaces'].append({'number':read(interface/'bInterfaceNumber'),
            'class':read(interface/'bInterfaceClass'),'subclass':read(interface/'bInterfaceSubClass'),
            'protocol':read(interface/'bInterfaceProtocol'),'driver':driver,'tty_acm_nodes':tty})
    return result


def observe(port, output, seconds, sysroot=Path('/sys'), clock=time.monotonic, sleep=time.sleep):
    if not 0<seconds<=900:raise ValueError('Bounded observation required')
    fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    start=clock();previous=None;events=0
    with os.fdopen(fd,'w') as stream:
        os.fchmod(stream.fileno(),0o600)
        while True:
            now=clock()
            if now-start>=seconds:break
            state=snapshot(port,sysroot)
            if state!=previous:
                events+=1
                if events>5000:raise ValueError('Metadata event budget exceeded')
                stream.write(json.dumps({'elapsed_ms':int((now-start)*1000),**state})+'\n')
                stream.flush();os.fsync(stream.fileno());previous=state
            sleep(min(.2,max(0,seconds-(clock()-start))))
    return {'events':events,'seconds':seconds,'port_opened':False,'device_written':False,
            'rebooted':False,'kernel_logging_qualified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=int,default=300)
    a=p.parse_args();print(json.dumps(observe(a.port,a.output,a.seconds),indent=2))
