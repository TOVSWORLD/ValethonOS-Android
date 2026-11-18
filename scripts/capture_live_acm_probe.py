#!/usr/bin/env python3
"""One exact physical USB/descriptor ACM probe; no device commands or mode changes."""
import argparse,array,fcntl,hashlib,json,os,re,select,socket,stat,struct,subprocess,tempfile,termios,time
from pathlib import Path

def identity(tty,profile,sysroot=Path('/sys')):
 path=(sysroot/'class/tty'/tty/'device')
 if not re.fullmatch('ttyACM[0-9]+',tty) or not path.exists():return None
 real=path.resolve();nodes=[real,*real.parents]
 usb=next((n for n in nodes if n.name==profile['physical_path'] and (n/'idVendor').is_file()),None)
 iface=next((n for n in nodes if (n/'bInterfaceNumber').is_file()),None)
 if usb is None or iface is None:return None
 if (usb/'idVendor').read_text().strip()!=profile['vendor'] or (usb/'idProduct').read_text().strip()!=profile['product']:return None
 if not (iface/'driver').exists():return None
 if (iface/'driver').resolve().name!='cdc_acm':raise ValueError('Selected endpoint lacks cdc_acm driver')
 major,minor=map(int,(sysroot/'class/tty'/tty/'dev').read_text().split(':'))
 return {'path':'/dev/'+tty,'rdev':os.makedev(major,minor),'interface':str(iface)}
def open_serial(chosen,allow_privileged=False):
 flags=os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY|os.O_NOFOLLOW|os.O_CLOEXEC
 try:return os.open(chosen['path'],flags)
 except PermissionError:
  if not allow_privileged:raise
 # Privileged helper opens only the selected char node, then hands the fd back.
 # Receiver stays unprivileged; no ACL, group, udev or persistent host change.
 with tempfile.TemporaryDirectory(prefix='kxusb-acm-') as directory:
  address=str(Path(directory)/'fd.sock');server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(address);server.listen(1);server.settimeout(10)
  code='import os,socket,array,stat;f=os.open('+repr(chosen['path'])+','+str(flags)+');s=os.fstat(f);assert stat.S_ISCHR(s.st_mode) and s.st_rdev=='+str(chosen['rdev'])+';c=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);c.connect('+repr(address)+');c.sendmsg([b"F"],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array("i",[f]))]);os.close(f);c.close()'
  process=subprocess.Popen(['sudo','-n','python3','-c',code],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  received=[]
  try:
   connection,_=server.accept()
   with connection:
    _,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    if uid!=0:raise ValueError('Privileged opener identity differs')
    data,ancillary,msgflags,_=connection.recvmsg(1,socket.CMSG_SPACE(array.array('i').itemsize),socket.MSG_CMSG_CLOEXEC)
    for level,kind,value in ancillary:
     if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
      descriptors=array.array('i');descriptors.frombytes(value[:len(value)-len(value)%descriptors.itemsize]);received.extend(descriptors)
    process.communicate(timeout=10)
    if process.returncode or data!=b'F' or len(received)!=1 or msgflags&socket.MSG_CTRUNC:raise ValueError('Invalid privileged fd transfer')
    fd=received.pop();return fd
  finally:
   server.close()
   for fd in received:os.close(fd)
   if process.poll() is None:process.kill();process.communicate(timeout=5)

def capture(profile,out):
 if not re.fullmatch('[0-9]+-[0-9]+(?:\\.[0-9]+)*',profile['physical_path']) or not re.fullmatch('[0-9a-f]{4}',profile['vendor']) or not re.fullmatch('[0-9a-f]{4}',profile['product']) or not re.fullmatch('[0-9a-f]{32}',profile['trial']):raise ValueError('Exact USB identity/nonce required')
 out.mkdir(mode=0o700);raw=out/'capture-private.bin';fd=None;old=None;blob=bytearray();r={'endpoint_selected':False,'complete':False,'host_received':False}
 try:
  print('USB_ACM_RECEIVER_READY',flush=True);end=time.monotonic()+45
  while time.monotonic()<end:
   matches=[x for p in Path('/sys/class/tty').glob('ttyACM*') if (x:=identity(p.name,profile)) is not None]
   if len(matches)>1:raise ValueError('Ambiguous ACM endpoints at selected device')
   if matches:
    chosen=matches[0];break
   time.sleep(.05)
  else:raise TimeoutError('No ACM endpoint at selected USB port')
  fd=open_serial(chosen,profile.get('allow_privileged_open') is True)
  if not stat.S_ISCHR(os.fstat(fd).st_mode) or os.fstat(fd).st_rdev!=chosen['rdev'] or identity(Path(chosen['path']).name,profile)!=chosen:raise ValueError('Opened endpoint changed')
  r['endpoint_selected']=True;fcntl.ioctl(fd,termios.TIOCEXCL);old=termios.tcgetattr(fd)
  attrs=[0,0,termios.CS8|termios.CREAD|termios.CLOCAL,0,termios.B9600,termios.B9600,list(old[6])];attrs[6][termios.VMIN]=1;attrs[6][termios.VTIME]=0
  termios.tcsetattr(fd,termios.TCSANOW,attrs)
  expected=('KXUSB_ACM trial='+profile['trial']+' capture_probe=1').encode()
  with raw.open('xb') as h:
   os.fchmod(h.fileno(),0o600)
   while time.monotonic()<end and len(blob)<65536:
    if not select.select([fd],[],[],.25)[0]:continue
    try:b=os.read(fd,min(4096,65536-len(blob)))
    except BlockingIOError:continue
    if not b:raise EOFError('ACM disconnected before frame')
    h.write(b);blob.extend(b)
    if expected+b'\n' in blob.splitlines(keepends=True):r['host_received']=True;break
   h.flush();os.fsync(h.fileno())
  if not r['host_received']:raise TimeoutError('Unique ACM frame not received')
  r.update({'complete':True,'capture_bytes':len(blob),'capture_sha256':hashlib.sha256(blob).hexdigest(),'capture_fsynced':True})
 except Exception as e:r['failure_kind']=type(e).__name__
 finally:
  if fd is not None:
   try:
    if old is not None:termios.tcsetattr(fd,termios.TCSANOW,old)
   except OSError:r['tty_restore_unconfirmed']=True
   os.close(fd)
  (out/'result.json').write_text(json.dumps(r,indent=2)+'\n');(out/'result.json').chmod(0o600)
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(capture(json.loads(a.profile.read_text()),a.output),indent=2))
