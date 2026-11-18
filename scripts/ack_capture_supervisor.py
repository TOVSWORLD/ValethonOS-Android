#!/usr/bin/env python3
"""Bounded detached host capture; SSH loss must not destroy the receiver outcome."""
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
LIMIT=135

def private(path,value):
 path=Path(path);tmp=path.with_name(path.name+'.tmp')
 with os.fdopen(os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w') as f:
  json.dump(value,f);f.flush();os.fsync(f.fileno())
 os.link(tmp,path,follow_symlinks=False);os.unlink(tmp)
 fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)

def launch(control,stdout,stderr):
 return subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(control)],stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,start_new_session=True,close_fds=True)

def worker(control):
 import resource
 from capture_ack_native_console import validate_profile
 from capture_lab_kernel_log import capture,private_bytes
 control=Path(control);inputs=json.loads(private_bytes(control/'inputs.json',4096));nonce=private_bytes(control/'nonce.bin',32)
 profile=inputs['profile'];validate_profile(profile,nonce)
 resource.setrlimit(resource.RLIMIT_FSIZE,(512*1024,512*1024))
 def expired(signum,frame):raise TimeoutError('Bounded host capture worker deadline')
 signal.signal(signal.SIGALRM,expired);signal.alarm(125)
 def ready():private(control/'ready.json',dict(pid=os.getpid(),nonce_sha256=hashlib.sha256(nonce).hexdigest(),profile_sha256=hashlib.sha256(json.dumps(profile,sort_keys=True).encode()).hexdigest()))
 try:
  if profile['scope']=='ack-storage-readonly-capture-1':
   from receive_storage_status import receive_fd
   result=capture(profile,nonce,Path(inputs['output']),ready=ready,receiver=receive_fd)
  elif profile['scope']=='ack-display-errors-capture-2':
   from receive_display_errors import receive_fd
   result=capture(profile,nonce,Path(inputs['output']),ready=ready,receiver=receive_fd)
  elif profile['scope']=='ack-display-functional-capture-1':
   from receive_display_status import receive_fd
   result=capture(profile,nonce,Path(inputs['output']),ready=ready,receiver=receive_fd)
  else:
   result=capture(profile,nonce,Path(inputs['output']),ready=ready)
 except BaseException as e:
  result=dict(complete=False,device_qualified=False,endpoint_selected=False,port_opened=False,worker_failure=type(e).__name__)
 finally:signal.alarm(0)
 private(control/'result.json',result)
 return result

def supervise(profile,nonce,output):
 output=Path(output).resolve();control=output.with_name(output.name+'.control')
 control.mkdir(mode=0o700)
 private(control/'inputs.json',dict(profile=profile,output=str(output),started_monotonic=time.monotonic()))
 fd=os.open(control/'nonce.bin',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(nonce);f.flush();os.fsync(f.fileno())
 stdout=os.open(control/'stdout-private.bin',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 stderr=os.open(control/'stderr-private.bin',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 try:process=launch(control,stdout,stderr)
 finally:os.close(stdout);os.close(stderr)
 began=time.monotonic();ready_file=control/'ready.json'
 while not ready_file.exists():
  if process.poll() is not None or time.monotonic()-began>12:raise RuntimeError('Detached capture did not durably arm')
  time.sleep(.02)
 ready=json.loads(ready_file.read_text())
 if (ready.get('pid')!=process.pid or ready.get('nonce_sha256')!=hashlib.sha256(nonce).hexdigest() or ready.get('profile_sha256')!=hashlib.sha256(json.dumps(profile,sort_keys=True).encode()).hexdigest()):raise ValueError('Capture readiness identity differs')
 print('ACK_NATIVE_RECEIVER_READY',flush=True)
 heartbeat=time.monotonic()+10
 while time.monotonic()-began<LIMIT:
  result=control/'result.json'
  if result.exists():
   value=json.loads(result.read_text());value['detached_worker_completed']=True;return value
  if process.poll() is not None:return dict(complete=False,worker_exit_code=process.returncode,worker_result_missing=True)
  if time.monotonic()>=heartbeat:
   try:print('ACK_NATIVE_RECEIVER_WAITING',flush=True)
   except (BrokenPipeError,OSError):pass # Detached worker remains bounded/alive.
   heartbeat=time.monotonic()+10
  time.sleep(.05)
 # Only the child/session launched here may be stopped; no device command.
 process.terminate()
 try:process.wait(timeout=5)
 except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
 return dict(complete=False,worker_deadline_exceeded=True)

if __name__=='__main__':
 if len(sys.argv)!=3 or sys.argv[1]!='--worker':raise SystemExit(2)
 worker(Path(sys.argv[2]))
