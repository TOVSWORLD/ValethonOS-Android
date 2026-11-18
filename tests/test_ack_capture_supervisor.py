import hashlib,json,os,subprocess,sys,tempfile,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import ack_capture_supervisor as supervisor
from capture_ack_native_console import validate_profile

class DurableCapture(unittest.TestCase):
 def profile(self,nonce):return dict(scope='ack-native-pid1-capture-1',nonce_sha256=hashlib.sha256(nonce).hexdigest(),usb_id='1209:0001',interface='00',wait_seconds=90,allow_privileged_open=True,physical_usb_path='1-2')
 def test_profile_stays_exact_and_single_port(self):
  nonce=bytes(range(32));p=self.profile(nonce);self.assertEqual(validate_profile(p,nonce),p)
  for key,value in [('wait_seconds',900),('interface','01'),('physical_usb_path','../tty'),('allow_privileged_open',False)]:
   with self.assertRaises(ValueError):validate_profile({**p,key:value},nonce)
 def test_worker_survives_parent_death_and_preserves_failure_receipt(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);nonce=bytes(range(32));profile=self.profile(nonce);out=p/'capture'
   # Test transport only: no USB path is opened. Run the production worker and
   # deadline/private-result code with a short fixture replacing physical I/O.
   child=p/'child.py';child.write_text('import sys,time\nfrom pathlib import Path\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\nimport ack_capture_supervisor as s, capture_lab_kernel_log as c\ndef fixture(profile,nonce,output,ready):\n output.mkdir(mode=0o700);ready();time.sleep(.4);return {"complete":False,"failure_stage":"fixture_no_usb","endpoint_selected":False}\nc.capture=fixture\ns.worker(Path(sys.argv[1]))\n')
   parent=p/'parent.py';parent.write_text('import sys,subprocess,json\nfrom pathlib import Path\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\nimport ack_capture_supervisor as s\ndef launch(control,stdout,stderr):return subprocess.Popen([sys.executable,'+repr(str(child))+',str(control)],stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,start_new_session=True,close_fds=True)\ns.launch=launch\ns.supervise('+repr(profile)+','+repr(nonce)+',Path('+repr(str(out))+'))\n')
   proc=subprocess.Popen([sys.executable,str(parent)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   try:
    self.assertEqual(proc.stdout.readline(),b'ACK_NATIVE_RECEIVER_READY\n');proc.kill();proc.communicate(timeout=5)
    control=out.with_name(out.name+'.control');end=time.monotonic()+5
    while not (control/'result.json').exists() and time.monotonic()<end:time.sleep(.02)
    result=json.loads((control/'result.json').read_text());self.assertFalse(result['complete']);self.assertEqual(result['failure_stage'],'fixture_no_usb')
    self.assertEqual((control/'nonce.bin').stat().st_mode&0o777,0o600)
    self.assertEqual((control/'result.json').stat().st_mode&0o777,0o600)
   finally:
    if proc.poll() is None:proc.kill();proc.communicate(timeout=5)
if __name__=='__main__':unittest.main()
