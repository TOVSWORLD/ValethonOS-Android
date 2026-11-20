import gzip,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_android_bootstrap_vm import vm_ramdisk,assess
from build_diagnostic_initramfs import archive
from test_android_direct_boot import entries
class AndroidBootstrapVM(unittest.TestCase):
 def test_vm_archive_changes_only_storage_entry_and_keeps_init(self):
  original=archive(entries());data,delta=vm_ramdisk(gzip.compress(original));decoded=gzip.decompress(data)
  self.assertIn(b'/dev/block/vda /system ext4 ro,barrier=1 wait,first_stage_mount',decoded)
  self.assertNotIn(b'/dev/block/mmcblk0p14',decoded);self.assertTrue(delta['original_android_init_unchanged'])
  for name,mode,payload,dev in entries():
   if name=='init':self.assertIn(payload,decoded)
 def test_second_stage_alone_is_not_bootstrap_pass(self):
  d=b'init first stage started!\ninit second stage started!\n'
  self.assertFalse(assess(d)['passed'])
  self.assertFalse(assess(d+b'bootstrap-apexd-failed')['passed'])
 def test_actual_apex_exit_zero_required_and_prior_failure_rejected(self):
  d=b"init first stage started!\ninit second stage started!\nService 'apexd-bootstrap' (pid 3) exited with status 0\n"
  self.assertTrue(assess(d)['passed'])
  for error in [b'Kernel panic',b'Failed to setup cpuset cgroup',b'bootstrap-apexd-failed']:
   self.assertFalse(assess(d+error)['passed'])
