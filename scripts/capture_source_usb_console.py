#!/usr/bin/env python3
"""Source printk console capture: fresh challenge required before shutdown."""
import fcntl, hashlib, json, os, re, select, stat, termios, time
from pathlib import Path
from capture_live_acm_probe import identity, open_serial

LIMIT=2*1024*1024

def marker(trial):
    if not re.fullmatch('[0-9a-f]{32}',trial):
        raise ValueError('Exact source trial required')
    return ('KXSOURCE trial='+trial+' kernel_console_ready=1').encode()

def read_console(fd, output, expected, deadline, proof=lambda:None):
    data=bytearray(); proven=False; reason='timeout'
    try:
        while time.monotonic()<deadline and len(data)<LIMIT:
            if not select.select([fd],[],[],.1)[0]:continue
            try:chunk=os.read(fd,min(8192,LIMIT-len(data)))
            except BlockingIOError:continue
            except OSError:reason='disconnect_or_read_error';break
            if not chunk:reason='disconnect';break
            output.write(chunk);output.flush();data.extend(chunk)
            if not proven and expected in data:
                proven=True;proof()
        if len(data)==LIMIT:reason='byte_limit'
    finally:
        output.flush();os.fsync(output.fileno())
    phases=data[data.index(expected)+len(expected):] if proven else b''
    return {'source_console_proven':proven,'capture_bytes':len(data),
            'capture_sha256':hashlib.sha256(data).hexdigest(),'end_reason':reason,
            'capture_fsynced':True,
            'init_reboot_route_seen':b'KXHANDOFF init_reboot_route=1 kexec_requested=1' in phases,
            'starting_new_kernel_seen':b'Starting new kernel' in phases,
            'final_cpu_gate_seen':b'KXHANDOFF final_cpu_gate=passed survivor=0' in phases}

def capture(profile,out):
    expected=marker(profile['trial'])
    if profile.get('vendor')!='1949' or profile.get('product')!='0338' or not re.fullmatch(r'[0-9]+-[0-9]+(?:\.[0-9]+)*',profile['physical_path']):
        raise ValueError('Exact source USB device/port required')
    out.mkdir(mode=0o700);fd=None;old=None
    result={'source_console_proven':False,'capture_bytes':0}
    try:
        print('SOURCE_RECEIVER_READY',flush=True);end=time.monotonic()+240
        while time.monotonic()<end:
            matches=[x for tty in Path('/sys/class/tty').glob('ttyACM*') if (x:=identity(tty.name,profile)) is not None]
            if len(matches)>1:raise ValueError('Ambiguous source ACM')
            if matches:chosen=matches[0];break
            time.sleep(.05)
        else:raise TimeoutError('Source ACM absent')
        fd=open_serial(chosen,True)
        if not stat.S_ISCHR(os.fstat(fd).st_mode) or os.fstat(fd).st_rdev!=chosen['rdev'] or identity(Path(chosen['path']).name,profile)!=chosen:
            raise ValueError('Source endpoint identity changed')
        fcntl.ioctl(fd,termios.TIOCEXCL);old=termios.tcgetattr(fd)
        attrs=[0,0,termios.CS8|termios.CREAD|termios.CLOCAL,0,termios.B9600,termios.B9600,list(old[6])]
        attrs[6][termios.VMIN]=1;attrs[6][termios.VTIME]=0
        termios.tcsetattr(fd,termios.TCSANOW,attrs)
        print('SOURCE_USB_OPEN',flush=True)
        with (out/'source-console-private.bin').open('xb') as f:
            os.fchmod(f.fileno(),0o600)
            result=read_console(fd,f,expected,end,lambda:print('SOURCE_CONSOLE_PROVEN',flush=True))
    except Exception as e:result['failure_kind']=type(e).__name__
    finally:
        if fd is not None:
            try:
                if old is not None:termios.tcsetattr(fd,termios.TCSANOW,old)
            except OSError:pass
            os.close(fd)
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        (out/'result.json').chmod(0o600)
    return result
