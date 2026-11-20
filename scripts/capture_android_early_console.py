#!/usr/bin/env python3
"""Receive-only bounded kernel USB console; no boot/reset/partition commands."""
import argparse,fcntl,json,os,re,select,stat,termios,time
from pathlib import Path
from capture_live_acm_probe import identity,open_serial
from restore_diagnostic_boot import sha

def capture(profile,output):
 if profile.get('scope')!='android-early-capture-1' or profile.get('vendor')!='0525' or profile.get('product')!='a4a7' or not re.fullmatch(r'[0-9]+-[0-9]+(?:\.[0-9]+)*',profile.get('physical_path','')) or not re.fullmatch('[0-9a-f]{64}',profile.get('trial','')):raise ValueError('Exact selected console profile required')
 output.mkdir(mode=0o700);fd=None;old=None;data=bytearray();end=time.monotonic()+300
 (output/'ready-private.json').write_text(json.dumps({'ready':True,'device_commands_sent':False}))
 try:
  while time.monotonic()<end and len(data)<8*1024*1024:
   if fd is None:
    matches=[i for tty in Path('/sys/class/tty').glob('ttyACM*') if (i:=identity(tty.name,profile)) is not None]
    if len(matches)>1:raise ValueError('Ambiguous selected endpoint')
    if not matches:time.sleep(.05);continue
    chosen=matches[0];fd=open_serial(chosen,profile.get('allow_privileged_open') is True)
    if not stat.S_ISCHR(os.fstat(fd).st_mode) or os.fstat(fd).st_rdev!=chosen['rdev'] or identity(Path(chosen['path']).name,profile)!=chosen:raise ValueError('Endpoint changed')
    fcntl.ioctl(fd,termios.TIOCEXCL);old=termios.tcgetattr(fd)
    attrs=[0,0,termios.CS8|termios.CREAD|termios.CLOCAL,0,termios.B115200,termios.B115200,list(old[6])];attrs[6][termios.VMIN]=1;attrs[6][termios.VTIME]=0;termios.tcsetattr(fd,termios.TCSANOW,attrs)
   if not select.select([fd],[],[],.1)[0]:continue
   try:b=os.read(fd,min(8192,8*1024*1024-len(data)))
   except BlockingIOError:continue
   except OSError:break
   if not b:break
   data.extend(b)
   # Persist every received chunk, including partial failed attempts.
   with (output/'console-private.bin').open('ab') as f:os.chmod(f.name,0o600);f.write(b);f.flush();os.fsync(f.fileno())
 finally:
  if fd is not None:
   if old is not None:
    try:termios.tcsetattr(fd,termios.TCSANOW,old)
    except OSError:pass
   os.close(fd)
  bound=profile['trial'].encode() in data
  r={'scope':'Receive-only early kernel console','bytes':len(data),'sha256':sha(data),'fresh_identity_found':bound,'panic_found':bound and b'Kernel panic' in data,'preinit_seen':bound and b'VALETHON PREINIT: entered' in data,'android_init_handoff_seen':bound and b'executing original Android /init' in data,'device_commands_sent':False}
  (output/'result-private.json').write_text(json.dumps(r,indent=2))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(capture(json.loads(a.profile.read_text()),a.output)))
