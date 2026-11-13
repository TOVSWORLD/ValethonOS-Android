import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_native_jump as r
class Device:
 def __init__(self):self.root=False;self.loaded=False;self.target=False;self.calls=[];self.preloaded=False;self.load_error=False;self.marker=True;self.uncertain=False;self.unload_error=False;self.wrong_flash=False;self.postload_dt=False
 def host(self,args):return subprocess.CompletedProcess(args,0,('a'*64+' file\n').encode(),b'')
 def adb(self,*args,**kw):
  self.calls.append(args)
  if args[0]=='root':self.root=True
  if args[0]=='unroot':self.root=False
 def shell(self,cmd,**kw):
  self.calls.append(cmd)
  if cmd=='id':return b'uid=0(root)' if self.root else b'uid=2000(shell)'
  if cmd=='cat /sys/kernel/kexec_loaded':return b'1' if self.loaded or self.preloaded else b'0'
  if cmd=='cat /sys/firmware/fdt':return b'changed' if self.postload_dt and self.loaded else b'dtb'
  if cmd=='cat /proc/mounts':return b'tmpfs /dev tmpfs rw 0 0\n'
  if cmd=='cat /proc/meminfo':return b'MemAvailable: 131072 kB\n'
  if cmd.startswith('sha256sum '):return ('a'*64+' file\n').encode()
  if 'native-load --load ' in cmd:
   self.loaded=True
   if self.load_error:raise RuntimeError('uncertain load')
   return b'loaded'
  if 'native-load --unload ' in cmd:
   if self.unload_error:raise RuntimeError('unload')
   self.loaded=False;return b'unloaded'
  if cmd=='setprop sys.powerctl reboot,valethon-kexec':
   self.target=True;self.loaded=False
   if self.uncertain:raise RuntimeError('disconnected')
   return b''
  if cmd=='cat /proc/sys/kernel/random/boot_id':return (('2' if self.target else '1')*8+'-1111-1111-1111-111111111111').encode()
  if cmd=='getprop sys.boot_completed':return b'1'
  if cmd=='cat /proc/device-tree/chosen/valethon,kexec-trial':return b'1'*32+b'\0' if self.marker else b''
  if cmd.startswith(('mkdir ','chmod ','rm -f ')):return b''
  raise AssertionError(cmd)
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.p=Path(t.name)
  self.m=self.p/'manifest';self.c=self.p/'client';self.a=self.p/'auth'
  self.m.write_text(json.dumps({'original_boot_sha256':r.BOOT_SHA,'entry':0x42018000,'trial_id':'1'*32,'source_dtb_sha256':r.sha(b'dtb'),'segments':[{'file':n,'sha256':'a'*64} for n in ['image.bin','metadata.bin','initrd.bin']]}))
  self.c.write_text(json.dumps({'manifest_sha256':r.sha(self.m.read_bytes()),'client_sha256':'a'*64,'execute_implemented':False}))
  self.a.write_text(json.dumps({'scope':r.SCOPE,'runner_sha256':r.sha(Path(r.__file__).read_bytes()),'manifest_sha256':r.sha(self.m.read_bytes()),'client_sha256':'a'*64,'trial_id':'1'*32,'owner_approved':True,'owner_available':True,'maximum_loads':1,'maximum_jump_requests':1,'boot_writes_allowed':False,'recovery_writes_allowed':False,'automatic_reboot_allowed':False}))
 def result(self):return json.loads((self.p/'out/result.json').read_text())
 def run_case(self,d,execute=True):
  def facts(x):return {'boot':'bad' if x.wrong_flash else r.BOOT_SHA,'config':r.ORIGINAL_CONFIG if x.target else r.NATIVE_CONFIG,'boot_id':('2' if x.target else '1')*8+'-1111-1111-1111-111111111111'}
  with patch.object(r,'facts',side_effect=facts):return r.run(d,'/lab',self.m,self.c,self.p/'out',self.a if execute else None)
 def test_preflight_never_stages_or_loads(self):
  d=Device();v=self.run_case(d,False);self.assertTrue(v['complete']);self.assertEqual(v['load_attempts'],0);self.assertFalse(any('push' in c for c in d.calls if isinstance(c,tuple)))
 def test_success_requires_trial_marker_original_flash_and_config(self):
  v=self.run_case(Device());self.assertTrue(v['jump_proven']);self.assertTrue(v['complete']);self.assertEqual((v['load_attempts'],v['jump_requests']),(1,1));self.assertFalse(v['boot_written']);self.assertTrue(v['normal_shell_restored'])
 def test_ordinary_reboot_cannot_masquerade_as_jump(self):
  d=Device();d.marker=False
  with self.assertRaises(ValueError):self.run_case(d)
  self.assertFalse(self.result()['jump_proven']);self.assertTrue(self.result()['owner_attention_required']);self.assertEqual(self.result()['unload_attempts'],0)
 def test_existing_image_not_replaced_or_unloaded(self):
  d=Device();d.preloaded=True
  with self.assertRaises(ValueError):self.run_case(d)
  self.assertEqual(self.result()['load_attempts'],0);self.assertEqual(self.result()['unload_attempts'],0)
 def test_uncertain_load_is_unloaded_before_any_shutdown(self):
  d=Device();d.load_error=True
  with self.assertRaises(RuntimeError):self.run_case(d)
  self.assertFalse(d.loaded);self.assertEqual(self.result()['unload_attempts'],1);self.assertEqual(self.result()['jump_requests'],0)
 def test_failed_unload_not_retried(self):
  d=Device();d.load_error=True;d.unload_error=True
  with self.assertRaises(RuntimeError):self.run_case(d)
  self.assertEqual(self.result()['unload_attempts'],1);self.assertTrue(self.result()['owner_attention_required'])
 def test_changed_source_after_load_unloads_without_jump(self):
  d=Device();d.postload_dt=True
  with self.assertRaises(ValueError):self.run_case(d)
  self.assertFalse(d.loaded);self.assertEqual(self.result()['jump_requests'],0)
 def test_uncertain_shutdown_request_not_reissued(self):
  d=Device();d.uncertain=True;v=self.run_case(d);self.assertTrue(v['jump_proven']);self.assertTrue(v['request_transport_uncertain']);self.assertEqual(v['jump_requests'],1)
 def test_wrong_flash_never_loads(self):
  d=Device();d.wrong_flash=True
  with self.assertRaises(ValueError):self.run_case(d)
  self.assertEqual(self.result()['load_attempts'],0)
 def test_bad_approval_does_not_touch_device(self):
  self.a.write_text('{}');d=Device()
  with self.assertRaises(ValueError):self.run_case(d)
  self.assertEqual(d.calls,[])
 def test_timeout_never_unloads_or_reboots_after_request(self):
  with patch.object(r.time,'monotonic',side_effect=[0,301]):
   with self.assertRaises(RuntimeError):self.run_case(Device())
  v=self.result();self.assertEqual(v['jump_requests'],1);self.assertEqual(v['unload_attempts'],0);self.assertFalse(v['jump_proven'])
