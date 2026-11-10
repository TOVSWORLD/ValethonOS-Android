#!/usr/bin/env python3
"""Private bounded target kernel console capture at one physical USB port."""
import argparse,fcntl,hashlib,json,os,re,select,stat,termios,time
from pathlib import Path
from capture_live_acm_probe import identity,open_serial
MAX_BYTES=2*1024*1024
def expected_marker(trial):
 if not re.fullmatch('[0-9a-f]{32}',trial):raise ValueError('Exact hexadecimal target trial ID required')
 return ('KXUSB target_trial='+trial+' console_bind=requested').encode()
def marker_kind(data,trial):
 direct=expected_marker(trial)
 if direct in data:return 'gserial_init'
 command=('Kernel command line: console=ttyGS0 g_serial.ft_bind=1 g_serial.ft_trial='+trial+' ').encode()
 if command in data:return 'target_kernel_cmdline'
 return None

def usb_state(physical,sysroot=Path('/sys')):
 if not re.fullmatch(r'[0-9]+-[0-9]+(?:\.[0-9]+)*',physical):raise ValueError('Exact physical port required')
 root=sysroot/'bus/usb/devices'/physical
 try:
  vendor=(root/'idVendor').read_text().strip().lower();product=(root/'idProduct').read_text().strip().lower()
  if not re.fullmatch('[0-9a-f]{4}',vendor) or not re.fullmatch('[0-9a-f]{4}',product):return {'present':False}
  return {'present':True,'vendor':vendor,'product':product}
 except OSError:return {'present':False}

def capture(profile,out):
 marker=expected_marker(profile['trial'])
 if profile.get('purpose')!='native-usb-console-target-1' or profile.get('vendor')!='0525' or profile.get('product')!='a4a7':raise ValueError('Pinned builtin ACM target descriptors required')
 if not re.fullmatch(r'[0-9]+-[0-9]+(?:\.[0-9]+)*',profile['physical_path']):raise ValueError('Physical USB port required')
 wait=profile.get('wait_seconds',300);window=profile.get('after_marker_seconds',10)
 if type(wait) is not int or not 1<=wait<=600 or type(window) is not int or not 1<=window<=30:raise ValueError('Bounded wait/capture window required')
 out.mkdir(mode=0o700);fd=None;old=None;blob=bytearray();stage='waiting_for_target_usb'
 events=[];last_state=None;started=None
 def observe():
  nonlocal last_state
  state=usb_state(profile['physical_path'])
  if state!=last_state:
   if len(events)<2048:events.append({'elapsed_ms':round((time.monotonic()-started)*1000),'state':state})
   last_state=state
 result={'scope':'Target kernel USB console; no boot/flash/device-write commands','complete':False,'endpoint_selected':False,'target_marker_received':False,'target_entry_proven':False,'normal_android_boot_qualified':False,'device_commands_sent':False}
 try:
  print('USB_KERNEL_CONSOLE_READY',flush=True);started=time.monotonic();end=started+wait
  while time.monotonic()<end:
   observe()
   matches=[x for tty in Path('/sys/class/tty').glob('ttyACM*') if (x:=identity(tty.name,profile)) is not None]
   if len(matches)>1:raise ValueError('Ambiguous target interfaces at selected physical port')
   if matches:chosen=matches[0];break
   time.sleep(.05)
  else:raise TimeoutError('Target console USB endpoint not observed')
  stage='opening_target_console';fd=open_serial(chosen,profile.get('allow_privileged_open') is True)
  if not stat.S_ISCHR(os.fstat(fd).st_mode) or os.fstat(fd).st_rdev!=chosen['rdev'] or identity(Path(chosen['path']).name,profile)!=chosen:raise ValueError('Target endpoint identity changed')
  result['endpoint_selected']=True;fcntl.ioctl(fd,termios.TIOCEXCL);old=termios.tcgetattr(fd)
  attrs=[0,0,termios.CS8|termios.CREAD|termios.CLOCAL,0,termios.B9600,termios.B9600,list(old[6])];attrs[6][termios.VMIN]=1;attrs[6][termios.VTIME]=0;termios.tcsetattr(fd,termios.TCSANOW,attrs)
  stage='reading_target_kernel_console';capture_end=end;result['end_reason']='wait_window'
  with (out/'kernel-console-private.bin').open('xb') as h:
   os.fchmod(h.fileno(),0o600)
   try:
    while time.monotonic()<capture_end and len(blob)<MAX_BYTES:
     observe()
     if not select.select([fd],[],[],.25)[0]:continue
     try:data=os.read(fd,min(8192,MAX_BYTES-len(blob)))
     except BlockingIOError:continue
     except OSError:result['end_reason']='usb_read_error';break
     if not data:result['end_reason']='usb_disconnect';break
     h.write(data);blob.extend(data)
     kind=marker_kind(blob,profile['trial'])
     if not result['target_marker_received'] and kind is not None:
      result['target_marker_received']=True;result['target_marker_kind']=kind;result['target_entry_proven']=True;capture_end=min(end,time.monotonic()+window);result['end_reason']='post_marker_window'
   finally:h.flush();os.fsync(h.fileno());result['capture_fsynced']=True
  result.update(capture_bytes=len(blob),capture_sha256=hashlib.sha256(blob).hexdigest(),byte_limit_reached=len(blob)==MAX_BYTES,complete=result['target_marker_received'])
 except Exception as error:result['failure_kind']=type(error).__name__;result['failure_stage']=stage
 finally:
  if fd is not None:
   try:
    if old is not None:termios.tcsetattr(fd,termios.TCSANOW,old)
   except OSError:result['tty_restore_unconfirmed']=True
   os.close(fd)
  result['usb_port_event_count']=len(events);result['usb_port_observer']='Best-effort selected-port metadata polls; no serial strings'
  with (out/'usb-port-events-private.json').open('w') as h:os.fchmod(h.fileno(),0o600);json.dump(events,h,indent=2);h.flush();os.fsync(h.fileno())
  with (out/'result.json').open('w') as h:os.fchmod(h.fileno(),0o600);json.dump(result,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(capture(json.loads(a.profile.read_text()),a.output),indent=2))
