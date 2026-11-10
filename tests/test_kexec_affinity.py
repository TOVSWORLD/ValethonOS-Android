import ctypes
import errno
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import run_kexec_affinity as runner


def records(states=(0,0,1,0),current=0,online=11):
    return ['KXAFF v1 fid=84000004 conduit=smc queries=4 current_cpu=%d online_mask=%x'%(current,online)]+[
      'KXAFF cpu=%d target=%x result=%d'%(i,i,v) for i,v in enumerate(states)]+[
      'KXAFF complete supported=%d current_on=%d state_changes=0 handoff=0'%(
       sum(0<=v<=2 for v in states),states[current]==0)]


class AffinityPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc=shutil.which('cc')
        if not cc:raise unittest.SkipTest('C compiler required')
        cls.temp=tempfile.TemporaryDirectory();p=Path(cls.temp.name)
        (p/'policy.c').write_text('#include "legacy_affinity_policy.h"\nint allowed(int b,int l,int s,unsigned f){return kxaff_legacy_allowed(b,l,s,f);}\nint args(unsigned long t,unsigned long l){return kxaff_query_args(t,l);}\n')
        subprocess.run([cc,'-dynamiclib' if sys.platform=='darwin' else '-shared','-fPIC',
          '-Wall','-Wextra','-Werror','-I',str(ROOT/'projects/firetabs-android/kexec-stage'),
          str(p/'policy.c'),'-o',str(p/'policy.so')],check=True,capture_output=True)
        cls.lib=ctypes.CDLL(str(p/'policy.so'))
        cls.lib.allowed.argtypes=[ctypes.c_int]*3+[ctypes.c_uint]
        cls.lib.args.argtypes=[ctypes.c_ulong,ctypes.c_ulong]

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_only_observed_legacy_smc32_binding_is_admitted(self):
        self.assertEqual(self.lib.allowed(1,1,1,0x84000004),1)
        for b,l,s,f in [(0,1,1,0x84000004),(1,0,1,0x84000004),(1,1,0,0x84000004),
                        (1,1,1,0xc4000004),(1,1,1,0x84000002),(2,1,1,0x84000004)]:
            self.assertEqual(self.lib.allowed(b,l,s,f),0)

    def test_only_four_cpu_targets_and_level_zero(self):
        for n in range(4):self.assertEqual(self.lib.args(n,0),1)
        for n,l in [(4,0),(2**32,0),(0,1),(0,2**32)]:self.assertEqual(self.lib.args(n,l),0)


class AffinityReport(unittest.TestCase):
    def test_complete_query_support_and_current_cpu_on(self):
        r=runner.parse_report(records())
        self.assertTrue(r['firmware_affinity_qualified'])
        self.assertEqual(r['results'],{'0':0,'1':0,'2':1,'3':0})

    def test_unsupported_results_are_retained_without_qualification(self):
        r=runner.parse_report(records((-1,-1,-1,-1)))
        self.assertFalse(r['firmware_affinity_qualified'])
        self.assertEqual(r['results']['0'],-1)

    def test_off_current_cpu_or_unknown_state_never_qualifies(self):
        for states in [(1,0,1,0),(3,0,1,0),(4294967295,0,1,0)]:
            self.assertFalse(runner.parse_report(records(states))['firmware_affinity_qualified'])

    def test_duplicate_missing_or_tampered_records_rejected(self):
        base=records()
        for lines in [base[:-1],base+[base[1]],base[:2]+[base[1]]+base[3:],
                      [base[0].replace('84000004','84000002')]+base[1:],
                      base[:-1]+[base[-1].replace('supported=4','supported=3')],
                      [base[0].replace('online_mask=b','online_mask=2')]+base[1:]]:
            with self.assertRaises(ValueError):runner.parse_report(lines)


class FakeADB:
    def __init__(self,module,lines=None,unload_fail=False):
        self.module=module;self.lines=lines or records();self.loaded=False
        self.queried=False;self.unloaded=False;self.file=False;self.calls=[];self.unload_fail=unload_fail
    def __call__(self,args,**kwargs):
        self.calls.append(args)
        if args[3]=='push':return subprocess.CompletedProcess(args,0,b'pushed',b'')
        cmd=args[4];out=b'';code=0
        if cmd=='uname -r':out=runner.RELEASE.encode()
        elif cmd=='id':out=b'uid=0(root)'
        elif cmd=='cat /proc/config.gz':out=gzip.compress(b'config')
        elif cmd.startswith('head -c'):out=b'b'*(16*1024*1024)
        elif cmd=='cat /proc/mounts':out=b'tmpfs /dev tmpfs rw 0 0\n'
        elif cmd=='cat /proc/modules':out=b'kxaffinity 8192 0 - Live\n' if self.loaded else b''
        elif cmd=='dmesg':
            out=b'baseline\n'
            if self.queried:out+='\n'.join(self.lines).encode()+b'\n'
            if self.unloaded:out+=b'KXAFF unloaded state_changes=0 handoff=0\n'
        elif cmd.startswith('umask '):self.file=True
        elif cmd.startswith('chmod '):pass
        elif cmd.startswith('cat /dev/kxaffinity-'):out=self.module
        elif cmd.startswith('insmod '):self.loaded=True;self.queried=True
        elif cmd=='rmmod kxaffinity':
            if self.unload_fail:code=1
            else:self.loaded=False;self.unloaded=True
        elif cmd.startswith('rm -f '):self.file=False
        elif cmd.startswith('test ! -e '):code=int(self.file)
        else:raise AssertionError('Unexpected command: '+cmd)
        return subprocess.CompletedProcess(args,code,out,b'')


class AffinityRunner(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.module=self.root/'module.ko';self.module.write_bytes(b'compiled-module')
        self.hash=hashlib.sha256(self.module.read_bytes()).hexdigest()
        self.auth={'scope':runner.SCOPE,'module_sha256':self.hash,'target_boot_sha256':hashlib.sha256(b'b'*(16*1024*1024)).hexdigest(),
          'owner_approved':True,'owner_available':True,'query_fid':'0x84000004','maximum_queries':4,
          'cpu_state_changes_allowed':False,'handoff_allowed':False}
    def tearDown(self):self.temp.cleanup()
    def run_fake(self,fake,execute=True,auth_change=None):
        auth=None
        if execute:
            auth=self.root/'auth.json';data=dict(self.auth);data.update(auth_change or {});auth.write_text(json.dumps(data))
        with patch.object(runner,'verify',return_value={'module_sha256':self.hash}), \
             patch.object(runner,'BOOT_SHA',self.auth['target_boot_sha256']), \
             patch.object(runner,'CONFIG_SHA',hashlib.sha256(b'config').hexdigest()), \
             patch.object(runner.subprocess,'run',fake):
            return runner.run('selected',self.module,self.root/'providers',self.root/'result',auth)

    def test_preflight_only_cannot_upload_or_query(self):
        f=FakeADB(self.module.read_bytes());r=self.run_fake(f,False)
        self.assertTrue(r['complete']);self.assertFalse(f.queried)
        self.assertEqual(r['module_load_attempts'],0)
        self.assertFalse(any('push' in a for a in f.calls))

    def test_one_test_unloads_and_cleans_up(self):
        f=FakeADB(self.module.read_bytes());r=self.run_fake(f)
        self.assertTrue(r['complete']);self.assertTrue(r['firmware_affinity_qualified'])
        self.assertTrue(r['module_unloaded']);self.assertTrue(r['ram_cleanup_verified'])
        self.assertEqual(sum(a[4].startswith('insmod ') for a in f.calls if a[3]=='exec-out'),1)

    def test_bad_approval_rejected_before_device_access(self):
        f=FakeADB(self.module.read_bytes())
        with self.assertRaises(ValueError):self.run_fake(f,auth_change={'maximum_queries':5})
        self.assertEqual(f.calls,[])

    def test_malformed_kernel_report_still_unloads(self):
        f=FakeADB(self.module.read_bytes(),lines=records()[:-1])
        with self.assertRaises(ValueError):self.run_fake(f)
        self.assertTrue(f.unloaded);self.assertFalse(f.file)

    def test_failed_unload_cannot_report_completion_and_is_not_retried(self):
        f=FakeADB(self.module.read_bytes(),unload_fail=True);r=self.run_fake(f)
        self.assertFalse(r['complete']);self.assertFalse(r['module_unloaded'])
        self.assertEqual(sum(a[4]=='rmmod kxaffinity' for a in f.calls if a[3]=='exec-out'),1)


if __name__=='__main__':unittest.main()
