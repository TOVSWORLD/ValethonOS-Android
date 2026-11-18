import hashlib,os,pty,sys,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import capture_usb_kernel_console as receiver
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
  self.profile={'purpose':'native-usb-console-target-1','physical_path':'1-2','vendor':'0525','product':'a4a7','trial':'a'*32,'wait_seconds':1,'after_marker_seconds':1}
 def stream(self,chunks,limit=None):
  master,slave=pty.openpty();chosen={'path':os.ttyname(slave),'rdev':os.fstat(slave).st_rdev,'interface':'mock'}
  def send():
   time.sleep(.05)
   try:
    for data in chunks:os.write(master,data);time.sleep(.03)
    time.sleep(.1)
   except OSError:pass
   finally:os.close(master)
  thread=threading.Thread(target=send);thread.start()
  try:
   with patch.object(Path,'glob',return_value=[Path('/sys/class/tty/ttyACM0')]),patch.object(receiver,'identity',return_value=chosen),patch.object(receiver,'MAX_BYTES',limit or receiver.MAX_BYTES):result=receiver.capture(self.profile,self.root/'capture')
  finally:os.close(slave);thread.join()
  return result
 def test_actual_fd_stream_is_synced_and_proves_only_target_entry(self):
  payload=b'Linux version test\n[ 0.01] '+receiver.expected_marker('a'*32)+b'\n'
  r=self.stream([payload]);raw=(self.root/'capture/kernel-console-private.bin').read_bytes()
  self.assertTrue(r['complete']);self.assertTrue(r['target_entry_proven']);self.assertFalse(r['normal_android_boot_qualified']);self.assertFalse(r['device_commands_sent']);self.assertEqual(r['capture_sha256'],hashlib.sha256(raw).hexdigest());self.assertTrue(r['capture_fsynced'])
 def test_other_trial_does_not_pass_but_bytes_are_kept(self):
  r=self.stream([receiver.expected_marker('b'*32)+b'\n']);self.assertFalse(r['complete']);self.assertFalse(r['target_entry_proven']);self.assertGreater(r['capture_bytes'],0);self.assertTrue(r['capture_fsynced'])
 def test_marker_split_across_reads(self):
  m=receiver.expected_marker('a'*32);r=self.stream([m[:25],m[25:]+b'\n']);self.assertTrue(r['target_marker_received'])
 def test_byte_limit_preserves_partial_capture_without_claiming_entry(self):
  r=self.stream([b'x'*128],limit=64);self.assertEqual(r['capture_bytes'],64);self.assertTrue(r['byte_limit_reached']);self.assertFalse(r['complete'])
 def test_no_endpoint_is_bounded(self):
  with patch.object(receiver.time,'monotonic',side_effect=[0,2]),patch.object(Path,'glob',return_value=[]):r=receiver.capture(self.profile,self.root/'capture')
  self.assertFalse(r['complete']);self.assertFalse(r['endpoint_selected']);self.assertEqual(r['failure_stage'],'waiting_for_target_usb')
 def test_early_kernel_cmdline_can_attribute_target_if_late_marker_wrapped(self):
  line=('Kernel command line: console=ttyGS0 g_serial.ft_bind=1 g_serial.ft_trial='+self.profile['trial']+' original_args\n').encode()
  r=self.stream([line]);self.assertTrue(r['target_entry_proven']);self.assertEqual(r['target_marker_kind'],'target_kernel_cmdline')
 def test_wrong_target_descriptor_refused_before_capture(self):
  self.profile['vendor']='0000'
  with self.assertRaises(ValueError):receiver.capture(self.profile,self.root/'capture')
  self.assertFalse((self.root/'capture').exists())
