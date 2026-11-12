import hashlib,json,os,pty,shlex,sys,tempfile,threading,time,tty,unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pack_source_usb_console_boot import enable_source_console,PREFIX
from prepare_native_jump_bundle import usb_bootargs
from capture_source_usb_console import marker,read_console
from prepare_source_acm_hold import prepare
import test_usb_console_jump as jump_fixture
from test_usb_console_jump import Fake,Process,runner,CFG
import run_source_usb_trial as driver
import capture_source_usb_console as source_receiver
from source_usb_console_trial import SourceCapture

class Packaging(unittest.TestCase):
 def boot(self,args=b'console=ttyMT0 original=1'):
  b=bytearray(16777216);b[:8]=b'ANDROID!';b[64:576]=args.ljust(512,b'\0');return bytes(b)
 def test_only_fixed_header_cmdline_changes(self):
  old=self.boot();new=enable_source_console(old)
  self.assertEqual(new[:64],old[:64]);self.assertEqual(new[576:],old[576:])
  self.assertEqual(new[64:576].split(b'\0')[0],PREFIX+b'console=ttyMT0 original=1')
 def test_existing_console_and_ambiguous_header_refused(self):
  for args in [b'console=ttyGS0',b'g_serial.ft_bind=1',b'x'*500,b'x'*512]:
   with self.assertRaises(ValueError):enable_source_console(self.boot(args))
  b=bytearray(self.boot());b[608]=1
  with self.assertRaises(ValueError):enable_source_console(bytes(b))
 def test_target_replaces_only_reviewed_source_prefix(self):
  prefix,args=usb_bootargs(PREFIX+b'console=ttyMT0 original=1','1'*32)
  self.assertEqual(args,b'console=ttyMT0 original=1');self.assertEqual((prefix+args).count(b'console=ttyGS0'),1)
  for args in [b'g_serial.ft_bind=1',b'console=ttyMT0 console=ttyGS1',PREFIX+PREFIX+b'foo']:
   with self.assertRaises(ValueError):usb_bootargs(args,'1'*32)
 def test_bootloader_prefix_preserves_every_other_argument_and_spacing(self):
  source=b'loader=1  console=ttyGS0 console=ttyMT0 original=1'
  prefix,args=usb_bootargs(source,'1'*32)
  self.assertEqual(args,b'loader=1  console=ttyMT0 original=1')
  self.assertEqual((prefix+args).count(b'console=ttyGS0'),1)
  for bad in [b'loader=1 console=ttyGS00',b'loader=1 console=ttyGS0 console=ttyGS0',b'loader=1 g_serial.ft_bind=1 console=ttyGS0']:
   with self.assertRaises(ValueError):usb_bootargs(bad,'1'*32)
 def test_hold_source_is_exact_and_retains_restore(self):
  source=Path('projects/firetabs-android/usb-live-capture/acm_trial.c').read_text();out=prepare(source)
  self.assertIn('static int restore(int owned)',out);self.assertNotIn('kernel_frame',out)
  self.assertIn('handoff_intent_no_further_usb_writes',out)
  with self.assertRaises(ValueError):prepare(source+'\n')

class ActualFd(unittest.TestCase):
 def capture(self,parts,expected):
  master,slave=pty.openpty();tty.setraw(slave);calls=[]
  def send():
   for b in parts:os.write(master,b);time.sleep(.015)
  thread=threading.Thread(target=send);thread.start()
  try:
   with tempfile.TemporaryFile() as f:
    r=read_console(slave,f,expected,time.monotonic()+.12,lambda:calls.append(True))
    f.seek(0);raw=f.read();self.assertEqual(r['capture_sha256'],hashlib.sha256(raw).hexdigest())
  finally:thread.join();os.close(master);os.close(slave)
  return r,calls
 def test_split_fresh_challenge_and_post_marker_phase(self):
  m=marker('1'*32);r,c=self.capture([m[:9],m[9:],b'\nKXHANDOFF init_reboot_route=1 kexec_requested=1\n'],m)
  self.assertTrue(r['source_console_proven']);self.assertEqual(c,[True]);self.assertTrue(r['init_reboot_route_seen'])
 def test_old_phase_and_wrong_nonce_cannot_become_current_proof(self):
  r,_=self.capture([b'KXHANDOFF final_cpu_gate=passed survivor=0\n',marker('2'*32),marker('1'*32)],marker('1'*32))
  self.assertFalse(r['final_cpu_gate_seen'])
  r,c=self.capture([marker('2'*32)],marker('1'*32));self.assertFalse(r['source_console_proven']);self.assertEqual(c,[])
 def test_disconnected_tty_restore_keeps_capture_receipt(self):
  master,slave=pty.openpty();self.addCleanup(os.close,master);self.addCleanup(os.close,slave)
  chosen={'path':os.ttyname(slave),'rdev':os.fstat(slave).st_rdev}
  with tempfile.TemporaryDirectory() as tmp,patch.object(Path,'glob',return_value=[Path('ttyACM0')]),patch.object(source_receiver,'identity',return_value=chosen),patch.object(source_receiver,'open_serial',return_value=os.dup(slave)),patch.object(source_receiver.termios,'tcsetattr',side_effect=[None,source_receiver.termios.error(5,'disconnected')]),patch.object(source_receiver,'read_console',return_value={'source_console_proven':True,'capture_bytes':0}):
   out=Path(tmp)/'capture';r=source_receiver.capture({'trial':'1'*32,'physical_path':'1-2','vendor':'1949','product':'0338'},out)
   self.assertTrue(r['tty_restore_unconfirmed']);self.assertTrue(r['source_console_proven']);self.assertTrue((out/'result.json').exists())
 def test_missing_collector_receipt_salvages_and_hash_verifies_raw_capture(self):
  raw=marker('1'*32)+b'\nsource bytes\n'
  class Device:
   def host(self,args,**kwargs):
    return SimpleNamespace(stdout=raw if args[0]=='cat' else (hashlib.sha256(raw).hexdigest()+'\n').encode())
  with tempfile.TemporaryDirectory() as tmp:
   c=SourceCapture(Device(),'/lab',{},'1'*32,'1-2',Path(tmp));c.process=SimpleNamespace(communicate=lambda **kw:(b'',b'disconnected'))
   r=c.collect();self.assertTrue(r['collector_receipt_missing']);self.assertTrue(r['source_console_proven']);self.assertEqual((Path(tmp)/'source-console-private.bin').read_bytes(),raw)

class Ordering(unittest.TestCase):
 setUp=jump_fixture.Tests.setUp
 write_manifest=jump_fixture.Tests.write_manifest
 result=jump_fixture.Tests.result
 def invoke(self,start_error=False,intent_error=False,execute=True):
  d=Fake();source_report={'receiver_sha256':runner.sha(Path('scripts/capture_source_usb_console.py').read_bytes()),'helper_sha256':'f'*64}
  self.auth.update(scope='native-usb-source-target-console-jump-1',source_capture_report_sha256=runner.sha(json.dumps(source_report,sort_keys=True).encode()),source_capture_manager_sha256=runner.sha(Path('scripts/source_usb_console_trial.py').read_bytes()))
  self.a.write_text(json.dumps(self.auth));self.device=d
  with patch.object(runner,'facts',return_value={'boot':runner.BOOT_SHA,'config':CFG,'boot_id':'same'}),patch.object(runner.subprocess,'Popen',return_value=Process()),patch.object(runner.selectors,'DefaultSelector') as sel,patch('source_usb_console_trial.SourceCapture') as capture:
   sel.return_value.select.return_value=[True];self.capture=capture
   if start_error:capture.return_value.start.side_effect=RuntimeError('No source proof')
   if intent_error:capture.return_value.intent.side_effect=RuntimeError('No intent ack')
   capture.return_value.collect.return_value={'source_console_proven':True}
   return runner.run(d,'/lab',self.m,self.c,self.linked,self.p/'out',self.a if execute else None,source_report)
 def test_source_proof_failure_stops_before_load(self):
  with self.assertRaises(RuntimeError):self.invoke(start_error=True)
  self.assertEqual(self.result()['load_attempts'],0);self.assertEqual(self.result()['jump_requests'],0)
  self.capture.return_value.abort.assert_called_once()
 def test_intent_failure_unloads_without_jump(self):
  with self.assertRaises(RuntimeError):self.invoke(intent_error=True)
  r=self.result();self.assertEqual(r['unload_attempts'],1);self.assertEqual(r['jump_requests'],0);self.assertFalse(self.device.target)
 def test_both_receivers_and_one_jump(self):
  r=self.invoke();self.assertTrue(r['source_console_proven_before_load']);self.assertEqual(r['jump_requests'],1)
  self.capture.return_value.start.assert_called_once();self.capture.return_value.collect.assert_called_once();self.capture.return_value.abort.assert_not_called()
 def test_preflight_starts_neither_source_capture_nor_helper(self):
  r=self.invoke(execute=False);self.capture.assert_not_called();self.assertEqual(r['load_attempts'],0)

class ParentPolicy(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.p=Path(t.name)
  self.package=self.p/'package';self.package.mkdir()
  self.policy={'code_sha256':{},'owner_approved':False,'owner_available':False,'native_config_sha256':'a'*64}
  assets=[('report.json','source_package_report_sha256',b'{}'),('boot-full.img','source_boot_candidate_sha256',b'candidate'),('original-boot.img','original_boot_sha256',b'original')]
  for name,key,data in assets:
   f=self.package/name;f.write_bytes(data);self.policy[key]=driver.sha(f)
  self.args=SimpleNamespace(source_package=self.package,authorization=None,output=self.p/'out',lab_package='/lab')
  for attr,key,data in [('linked_report','linked_report_sha256',b'{}'),('image','target_image_sha256',b'image'),('helper','source_helper_sha256',b'helper'),('ssh_args','unused',b'[]')]:
   f=self.p/attr;f.write_bytes(data);setattr(self.args,attr,f)
   if key!='unused':self.policy[key]=driver.sha(f)
  f=self.p/'capture';f.write_text(json.dumps({'helper_sha256':driver.sha(self.args.helper),'receiver_sha256':driver.sha(Path('scripts/capture_source_usb_console.py'))}));self.args.capture_report=f;self.policy['capture_report_sha256']=driver.sha(f)
  self.policyfile=self.p/'policy';self.policyfile.write_text(json.dumps(self.policy))
 def test_wrong_approval_rejected_before_connection(self):
  self.args.authorization=self.p/'authorization';self.args.authorization.write_text(json.dumps(self.policy))
  with patch.object(driver,'POLICY',self.policyfile),patch.object(driver,'LabADB') as connection:
   with self.assertRaises(ValueError):driver.run(self.args)
   connection.assert_not_called()
 def test_default_stops_after_read_only_source_preflight(self):
  with patch.object(driver,'POLICY',self.policyfile),patch.object(driver,'LabADB'),patch.object(driver,'source_boot',return_value={'complete':True}) as source,patch.object(driver,'jump') as jump:
   self.assertTrue(driver.run(self.args)['read_only_preflight']['complete']);self.assertIsNone(source.call_args.args[-1]);jump.assert_not_called()
 def test_hold_report_cannot_use_an_unqualified_kernel_profile(self):
  report=json.loads(self.args.capture_report.read_text());report['functionfs_hold']=True
  self.args.capture_report.write_text(json.dumps(report));self.policy['capture_report_sha256']=driver.sha(self.args.capture_report);self.policyfile.write_text(json.dumps(self.policy))
  with patch.object(driver,'POLICY',self.policyfile),patch.object(driver,'LabADB') as connection:
   with self.assertRaises(ValueError):driver.run(self.args)
   connection.assert_not_called()
 def test_source_failure_does_not_prepare_or_jump_and_approval_is_single_use(self):
  self.args.authorization=self.p/'authorization';self.args.authorization.write_text(json.dumps({**self.policy,'owner_approved':True,'owner_available':True}))
  with patch.object(driver,'POLICY',self.policyfile),patch.object(driver,'LabADB'),patch.object(driver,'source_boot',return_value={'complete':False}),patch.object(driver,'prepare') as prepare,patch.object(driver,'jump') as jump:
   self.assertFalse(driver.run(self.args)['jump_executed']);prepare.assert_not_called();jump.assert_not_called()
   self.args.output=self.p/'out2'
   with self.assertRaises(FileExistsError):driver.run(self.args)

class HoldSettings(unittest.TestCase):
 class Device:
  def __init__(self):
   self.values={'ft_hold_adb':'N','ft_hold_trial':'','printk':'7 4 1 7'};self.writes=[];self.fail_quiet=False
  def shell(self,cmd,**kw):
   args=shlex.split(cmd);name=args[-1].rsplit('/',1)[-1]
   if args[0]=='cat':return (self.values[name]+'\n').encode()
   assert args[0]=='printf' and args[-2]=='>'
   value=args[2] if args[1]=='%s' else args[1]
   if value==r'\n':value=''
   if name=='printk' and value.startswith('1 ') and self.fail_quiet:raise RuntimeError('write failed')
   self.writes.append((name,value));self.values[name]=('Y' if value=='1' else 'N') if name=='ft_hold_adb' else value
   return b''
 def source(self,d):return SourceCapture(d,'/lab',{'functionfs_hold':True},'1'*32,'1-2',Path('/unused'))
 def test_arm_reads_back_hold_nonce_and_quiet_level_then_restores_all_values(self):
  d=self.Device();c=self.source(d);c.arm_ffs_hold()
  self.assertEqual(d.values,{'ft_hold_adb':'Y','ft_hold_trial':'1'*32,'printk':'1 4 1 7'})
  c.restore_settings();self.assertEqual(d.values,{'ft_hold_adb':'N','ft_hold_trial':'','printk':'7 4 1 7'})
 def test_foreign_hold_or_nonce_refused_without_writes(self):
  for field,value in [('ft_hold_adb','Y'),('ft_hold_trial','foreign')]:
   d=self.Device();d.values[field]=value
   with self.assertRaises(ValueError):self.source(d).arm_ffs_hold()
   self.assertEqual(d.writes,[])
 def test_bad_printk_state_refused_before_any_write(self):
  d=self.Device();d.values['printk']='unreviewed'
  with self.assertRaises(ValueError):self.source(d).arm_ffs_hold()
  self.assertEqual(d.writes,[])
 def test_partial_arm_failure_is_owned_and_cleaned_up(self):
  d=self.Device();d.fail_quiet=True;c=self.source(d)
  with self.assertRaises(RuntimeError):c.arm_ffs_hold()
  self.assertTrue(c.ffs_hold_armed);d.fail_quiet=False;c.restore_settings()
  self.assertEqual(d.values,{'ft_hold_adb':'N','ft_hold_trial':'','printk':'7 4 1 7'})
 def test_abort_refuses_to_clear_someone_elses_nonce(self):
  d=self.Device();c=self.source(d);c.arm_ffs_hold();d.values['ft_hold_trial']='f'*32;before=list(d.writes)
  with self.assertRaises(ValueError):c.restore_settings()
  self.assertEqual(d.writes,before)
