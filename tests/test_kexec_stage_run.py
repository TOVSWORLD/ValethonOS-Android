import gzip,hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_kexec_stage as stage

class StageRun(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
  self.module=self.p/'stage.ko';self.module.write_bytes(b'module');self.client=self.p/'client';self.client.write_bytes(b'client')
  self.checked={'module_sha256':hashlib.sha256(b'module').hexdigest(),'client_sha256':hashlib.sha256(b'client').hexdigest()}
  self.auth=self.p/'auth.json';self.auth.write_text(json.dumps(dict(scope=stage.SCOPE,target_boot_sha256=stage.BOOT_SHA,
   owner_approved=True,owner_available=True,handoff_allowed=False,selftest_bytes=16384,**self.checked)))
  self.commands=[];self.loaded=False;self.ever=False;self.fail_client=False;self.config=b'cfg';self.boot=bytes(16777216)
 def adb(self,args,**kwargs):
  c='push '+args[-1] if len(args)>3 and args[3]=='push' else args[-1];self.commands.append(c);rc=0
  if c=='get-state':b=b'device\n'
  elif c=='uname -r':b=stage.RELEASE.encode()+b'\n'
  elif c=='id':b=b'uid=0(root)'
  elif c=='cat /proc/config.gz':b=gzip.compress(self.config)
  elif c.startswith('head -c 16777216'):b=self.boot
  elif c=='cat /proc/modules':b=b'kxstage 20000 0 - Live\n' if self.loaded else b''
  elif c in ['test ! -e /dev/kxstage','test ! -e /sys/class/misc/kxstage']:b=b'';rc=int(self.loaded)
  elif c=='cat /proc/meminfo':b=b'MemAvailable: 131072 kB\n'
  elif c=='cat /proc/mounts':b=b'tmpfs /dev tmpfs rw,nosuid 0 0\n'
  elif c=='dmesg':b=b'KXSTAGE unloaded owned_pages=0 execute_disabled=1\n' if self.ever and not self.loaded else b'normal\n'
  elif c.startswith('umask 077;') or c.startswith('push ') or c.startswith('chmod ') or c.startswith('rm -f ') or c.startswith('test ! -e /dev/kxstage-'):b=b''
  elif c.startswith('cat /dev/kxstage-'):b=b'module' if c.endswith('.ko') else b'client'
  elif c.startswith('insmod '):self.loaded=True;self.ever=True;b=b''
  elif c=='test -c /dev/kxstage':b=b'';rc=int(not self.loaded)
  elif c.startswith('/dev/kxstage-') and c.endswith(' --selftest'):
   r=dict(complete=not self.fail_client,phase='failed' if self.fail_client else 'complete',errno=0,segments=3,
    requested_bytes=16384,staged_bytes=16384,owned_pages_prepared=7,owned_pages_after=0,
    crc32=stage.expected_crc(),execute_disabled=True,handoff_attempted=False)
   b=json.dumps(r).encode();rc=int(self.fail_client)
  elif c=='rmmod kxstage':self.loaded=False;b=b''
  else:raise AssertionError('Unexpected operation '+c)
  return subprocess.CompletedProcess(args,rc,b,b'')
 def execute(self,approved=True):
  real=stage.digest
  def digest(b):return stage.CONFIG_SHA if b==self.config else stage.BOOT_SHA if b==self.boot else real(b)
  with patch.object(stage,'verify',return_value=self.checked),patch.object(stage,'digest',side_effect=digest),patch.object(stage.subprocess,'run',side_effect=self.adb):
   return stage.run('test',self.module,self.p/'versions',self.client,self.p/'result',self.auth if approved else None)
 def test_bad_approval_prevents_any_device_access(self):
  self.auth.write_text('{}')
  with self.assertRaisesRegex(ValueError,'approval'):self.execute()
  self.assertEqual(self.commands,[])
 def test_preflight_does_not_stage_or_load(self):
  r=self.execute(False);self.assertTrue(r['complete']);self.assertEqual(r['module_load_attempts'],0)
  self.assertFalse(any(c.startswith(('push ','insmod ')) for c in self.commands))
 def test_success_is_one_ram_cycle_and_verified_unload(self):
  r=self.execute();self.assertTrue(r['complete']);self.assertTrue(r['module_unloaded']);self.assertTrue(r['ram_cleanup_verified']);self.assertTrue(r['device_node_removed'])
  self.assertEqual(r['module_load_attempts'],1);self.assertEqual(r['client_runs'],1)
  self.assertFalse(r['handoff_attempted']);self.assertFalse(any('reboot' in c for c in self.commands))
  self.assertEqual(sum(c.startswith('push /dev/') for c in self.commands),2)
 def test_failed_client_unloads_and_does_not_retry(self):
  self.fail_client=True
  with self.assertRaisesRegex(RuntimeError,'client failed'):self.execute()
  r=json.loads((self.p/'result/result.json').read_text());self.assertTrue(r['module_unloaded']);self.assertFalse(r['complete'])
  self.assertEqual(r['client_runs'],1);self.assertEqual(r['module_load_attempts'],1)
 def test_client_must_match_crc_and_zero_owned_pages(self):
  valid=dict(complete=True,phase='complete',errno=0,segments=3,requested_bytes=16384,staged_bytes=16384,
   owned_pages_prepared=7,owned_pages_after=0,crc32=stage.expected_crc(),execute_disabled=True,handoff_attempted=False)
  stage.validate_client(valid)
  for change in [dict(owned_pages_after=1),dict(crc32=['0']*3),dict(execute_disabled=False),dict(handoff_attempted=True)]:
   with self.assertRaises(ValueError):stage.validate_client(dict(valid,**change))

if __name__=='__main__':unittest.main()
