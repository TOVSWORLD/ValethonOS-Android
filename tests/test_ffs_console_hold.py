import shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_ffs_console_hold import HELPER,function,prepare as prepare_ffs
from prepare_usb_console_queue_fix import fix_queue,prepare as prepare_queue
from prepare_handoff_usb_dwell import add_dwell

ROOT=Path(__file__).resolve().parents[1]
class ActualKernelFunctions(unittest.TestCase):
 def compile(self,folder,source,name):
  cc=shutil.which('cc')
  if not cc:self.skipTest('C compiler required')
  subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-I'+str(folder),str(ROOT/'tests'/source),'-o',str(folder/name)],check=True,capture_output=True)
 def test_actual_functionfs_last_close_guards(self):
  old=(ROOT/'tests/fixtures/ffs_last_close_baseline.inc').read_text()
  actual=function(HELPER,'bool ft_keep_adb_console(')+old.replace('if (ffs->no_disconnect) {','if (ffs->no_disconnect || ft_keep_adb_console(ffs)) {')
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'actual-last-close.inc').write_text(actual);self.compile(p,'ffs_console_hold_harness.c','control')
   for case in range(12):
    with self.subTest(case=case):subprocess.run([str(p/'control'),str(case)],check=True,capture_output=True)
 def test_actual_console_early_and_late_completion(self):
  old=(ROOT/'tests/fixtures/usb_console_queue_baseline.inc').read_text()
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)
   for name,s,fixed in [('baseline',old,0),('fixed',fix_queue(old),1)]:
    (p/'console-under-test.inc').write_text(s);self.compile(p,'usb_console_queue_harness.c',name)
    for schedule in ([0,1] if not fixed else [0,1,2]):
     with self.subTest(version=name,schedule=schedule):
      r=subprocess.run([str(p/name),str(schedule),str(fixed)],check=True,capture_output=True,text=True)
      self.assertIn('baseline_lost_completion_reproduced' if not fixed and schedule==0 else 'console_queue_control=passed',r.stdout)
 def test_changed_source_refused_before_any_patch(self):
  for prepare in [prepare_ffs,prepare_queue]:
   with self.assertRaises(ValueError):prepare('unreviewed source')
 def test_checkpoint_requires_native_image_admission_board_and_pid1(self):
  old=(ROOT/'tests/fixtures/native_kexec_entry_baseline.inc').read_text()
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'native-under-test.inc').write_text(add_dwell(old));self.compile(p,'native_entry_checkpoint_harness.c','native')
   for case in range(6):
    with self.subTest(case=case):subprocess.run([str(p/'native'),str(case)],check=True,capture_output=True)
