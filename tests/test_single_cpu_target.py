import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_native_jump_bundle import target_prefix,usb_bootargs
import test_usb_console_jump as fixture
from test_usb_console_jump import runner,Fake,Process,CFG

class BootArguments(unittest.TestCase):
 def test_only_cpu0_target_has_two_explicit_caps_and_keeps_suffix(self):
  old=b'loader=1 console=ttyGS0 console=ttyMT0 original=1'
  prefix,suffix=usb_bootargs(old,'1'*32,1)
  self.assertEqual(prefix,b'console=ttyGS0 g_serial.ft_bind=1 g_serial.ft_trial='+b'1'*32+b' nr_cpus=1 maxcpus=1 ')
  self.assertEqual(suffix,b'loader=1 console=ttyMT0 original=1')
 def test_existing_cpu_policy_is_not_silently_overridden(self):
  for value in [b'maxcpus=4',b'nr_cpus=4',b'nosmp',b'"maxcpus=4"']:
   with self.assertRaises(ValueError):usb_bootargs(value,'1'*32,1)
 def test_no_other_cpu_limit_or_bool_mode_is_accepted(self):
  for value in [True,False,0,2,4,'1']:
   with self.assertRaises(ValueError):target_prefix('1'*32,value)
 def test_previous_unlimited_profile_is_unchanged(self):
  self.assertEqual(len(target_prefix('1'*32)),3)

class GuardedTrial(unittest.TestCase):
 setUp=fixture.Tests.setUp
 write_manifest=fixture.Tests.write_manifest
 result=fixture.Tests.result
 def setup_mode(self):
  self.manifest.update(target_cpu_limit=1,bootargs_prefix=target_prefix(self.trial,1));self.write_manifest()
  self.linked['native_entry_checkpoint_linked']=True
  self.source={'functionfs_hold':True,'receiver_sha256':runner.sha(Path('scripts/capture_source_usb_console.py').read_bytes()),'helper_sha256':'f'*64}
  self.auth.update(scope='native-single-cpu-usb-source-target-console-jump-1',target_cpu_limit=1,manifest_sha256=runner.sha(self.m.read_bytes()),source_capture_report_sha256=runner.sha(json.dumps(self.source,sort_keys=True).encode()),source_capture_manager_sha256=runner.sha(Path('scripts/source_usb_console_trial.py').read_bytes()))
  self.a.write_text(json.dumps(self.auth))
 def invoke(self,execute=True,source=True):
  d=Fake();self.device=d
  with patch.object(runner,'facts',return_value={'boot':runner.BOOT_SHA,'config':CFG,'boot_id':'same'}),patch.object(runner.subprocess,'Popen',return_value=Process()),patch.object(runner.selectors,'DefaultSelector') as select,patch('source_usb_console_trial.SourceCapture') as capture:
   select.return_value.select.return_value=[True];capture.return_value.collect.return_value={'native_entry_seen':True}
   return runner.run(d,'/lab',self.m,self.c,self.linked,self.p/'out',self.a if execute else None,self.source if source else None)
 def test_one_cpu_target_can_complete_only_through_new_scope_and_source_proof(self):
  self.setup_mode();r=self.invoke()
  self.assertEqual((r['target_cpu_limit'],r['load_attempts'],r['jump_requests']),(1,1,1));self.assertTrue(r['target_entry_proven'])
 def test_preflight_never_loads(self):
  self.setup_mode();r=self.invoke(execute=False);self.assertEqual(r['load_attempts'],0);self.assertTrue(r['normal_shell_restored'])
 def test_old_scope_cannot_authorize_new_target(self):
  self.setup_mode();self.auth['scope']='native-usb-source-target-console-jump-1';self.a.write_text(json.dumps(self.auth))
  with self.assertRaises(ValueError):self.invoke()
  self.assertEqual(self.device.calls,[])
 def test_cpu_mode_cannot_run_without_source_capture(self):
  self.setup_mode()
  with self.assertRaises(ValueError):self.invoke(source=False)
  self.assertEqual(self.device.calls,[])
 def test_missing_cpu_flags_are_rejected_before_device_commands(self):
  self.setup_mode();self.manifest['bootargs_prefix']=target_prefix(self.trial);self.write_manifest()
  with self.assertRaises(ValueError):self.invoke()
  self.assertEqual(self.device.calls,[])
