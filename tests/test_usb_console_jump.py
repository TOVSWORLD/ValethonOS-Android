import io,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_usb_console_jump as runner
from test_native_jump_run import Device
CFG='a'*64;IMAGE='b'*64;RAW=b'kernel console bytes'
class Fake(Device):
 args=[]
 def adb(self,*args,**kw):
  super().adb(*args,**kw)
  return subprocess.CompletedProcess(args,0,b'usb:1-2\n' if args[0]=='get-devpath' else b'',b'')
 def host(self,args,**kw):
  if args[0]=='cat':return subprocess.CompletedProcess(args,0,RAW,b'')
  if args[0]=='sha256sum':
   name=args[-1].split('/')[-1];digest=runner.sha((Path(runner.__file__).parent/name).read_bytes()) if name.endswith('.py') else 'a'*64
   return subprocess.CompletedProcess(args,0,(digest+' file\n').encode(),b'')
  return subprocess.CompletedProcess(args,0,b'',b'')
class Process:
 def __init__(self,complete=True,ready=True):self.stdout=io.BytesIO(b'USB_KERNEL_CONSOLE_READY\n' if ready else b'wrong\n');self.complete=complete
 def poll(self):return 0
 def communicate(self,**kw):return json.dumps({'complete':self.complete,'target_entry_proven':self.complete,'capture_bytes':len(RAW),'capture_sha256':runner.sha(RAW),'capture_fsynced':True}).encode(),b''
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.p=Path(t.name);self.m=self.p/'manifest';self.c=self.p/'client';self.a=self.p/'auth';self.trial='1'*32
  self.manifest={'trial_id':self.trial,'source_config_sha256':CFG,'target_config_sha256':CFG,'target_image_sha256':IMAGE,'original_boot_sha256':runner.BOOT_SHA,'bootargs_prefix':['console=ttyGS0','g_serial.ft_bind=1','g_serial.ft_trial='+self.trial],'entry':0x42018000,'source_dtb_sha256':runner.sha(b'dtb'),'segments':[{'file':n,'sha256':'a'*64} for n in ['image.bin','metadata.bin','initrd.bin']]};self.write_manifest()
  self.linked={'usb_console_linked':True,'serial_bind_is_opt_in':True,'serial_source_sha256':runner.SERIAL_SHA,'usb_profile_config_changes':{k:{'before':'n','after':'y'} for k in runner.ALLOWED},'artifacts':{'.config':{'sha256':CFG},'arch/arm64/boot/Image':{'sha256':IMAGE}}}
  here=Path(runner.__file__).parent
  self.auth={'scope':runner.SCOPE,'runner_sha256':runner.sha(Path(runner.__file__).read_bytes()),'manifest_sha256':runner.sha(self.m.read_bytes()),'client_sha256':'a'*64,'target_image_sha256':IMAGE,'native_config_sha256':CFG,'receiver_sha256':runner.sha((here/'capture_usb_kernel_console.py').read_bytes()),'shared_receiver_sha256':runner.sha((here/'capture_live_acm_probe.py').read_bytes()),'owner_approved':True,'owner_available':True,'maximum_loads':1,'maximum_jump_requests':1,'boot_writes_allowed':False,'automatic_reboot_allowed':False};self.a.write_text(json.dumps(self.auth))
 def write_manifest(self):
  self.m.write_text(json.dumps(self.manifest));self.c.write_text(json.dumps({'manifest_sha256':runner.sha(self.m.read_bytes()),'client_sha256':'a'*64,'execute_implemented':False}))
 def run_case(self,d=None,execute=True,process=None):
  d=d or Fake();process=process or Process()
  def facts(x):return {'boot':runner.BOOT_SHA,'config':CFG,'boot_id':'11111111-1111-1111-1111-111111111111'}
  with patch.object(runner,'facts',side_effect=facts),patch.object(runner.subprocess,'Popen',return_value=process),patch.object(runner.selectors,'DefaultSelector') as sel:
   sel.return_value.select.return_value=[True]
   r=runner.run(d,'/lab',self.m,self.c,self.linked,self.p/'out',self.a if execute else None)
  return r,d
 def result(self):return json.loads((self.p/'out/result.json').read_text())
 def test_preflight_never_loads_or_launches(self):
  r,d=self.run_case(execute=False);self.assertTrue(r['complete']);self.assertEqual(r['load_attempts'],0);self.assertTrue(r['normal_shell_restored'])
 def test_console_success_proves_target_and_still_requires_owner_return(self):
  r,d=self.run_case();self.assertTrue(r['target_entry_proven']);self.assertTrue(r['complete']);self.assertTrue(r['owner_return_required']);self.assertFalse(r['normal_android_boot_qualified']);self.assertFalse(r['boot_written']);self.assertEqual((r['load_attempts'],r['jump_requests']),(1,1));self.assertFalse(any(isinstance(c,tuple) and c[0]=='unroot' for c in d.calls));self.assertEqual((self.p/'out/kernel-console-private.bin').read_bytes(),RAW)
 def test_partial_usb_logs_do_not_claim_entry_and_are_kept(self):
  r,d=self.run_case(process=Process(False));self.assertFalse(r['target_entry_proven']);self.assertFalse(r['complete']);self.assertTrue(r['owner_return_required']);self.assertTrue((self.p/'out/kernel-console-private.bin').exists())
 def test_auxiliary_usb_trace_does_not_block_valid_kernel_capture(self):
  d=Fake();original=d.host
  def host(args,**kw):
   if args[0]=='cat' and args[-1].endswith('usb-port-events-private.json'):raise RuntimeError('metadata only')
   return original(args,**kw)
  d.host=host;r,_=self.run_case(d);self.assertTrue(r['complete']);self.assertTrue(r['target_entry_proven']);self.assertTrue(r['usb_metadata_copy_unconfirmed'])
 def test_preexisting_image_preserved(self):
  d=Fake();d.preloaded=True
  with self.assertRaises(ValueError):self.run_case(d)
  self.assertEqual(self.result()['load_attempts'],0);self.assertEqual(self.result()['unload_attempts'],0)
 def test_uncertain_load_unloads_before_shutdown(self):
  d=Fake();d.load_error=True
  with self.assertRaises(RuntimeError):self.run_case(d)
  r=self.result();self.assertEqual(r['unload_attempts'],1);self.assertEqual(r['jump_requests'],0);self.assertFalse(d.loaded)
 def test_no_load_if_receiver_not_ready(self):
  with self.assertRaises(RuntimeError):self.run_case(process=Process(ready=False))
  self.assertEqual(self.result()['load_attempts'],0)
 def test_offline_preview_never_loadable(self):
  self.manifest['offline_preview']=True;self.write_manifest();d=Fake()
  with self.assertRaises(ValueError):self.run_case(d,False)
  self.assertEqual(d.calls,[])
 def test_bad_approval_before_device(self):
  self.a.write_text('{}');d=Fake()
  with self.assertRaises(ValueError):self.run_case(d)
  self.assertEqual(d.calls,[])
