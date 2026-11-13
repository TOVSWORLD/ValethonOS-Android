import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import run_native_source_boot as runner
CANDIDATE='a'*64
OLD='11111111-1111-1111-1111-111111111111'
NEW='22222222-2222-2222-2222-222222222222'


class Fake:
    def __init__(self,partial=False,wrong_return=False,restore_fail=False,unroot_fail=False,uncertain=False):
        self.root=False;self.boot=runner.BOOT_SHA;self.config=runner.ORIGINAL_CONFIG;self.ident=OLD
        self.partial=partial;self.wrong_return=wrong_return;self.restore_fail=restore_fail;self.unroot_fail=unroot_fail;self.uncertain=uncertain
        self.calls=[];self.sources={};self.stages=0
    def host(self,args):
        return subprocess.CompletedProcess(args,0,((CANDIDATE if args[-1].endswith('/boot-full.img') else runner.BOOT_SHA)+' file\n').encode(),b'')
    def adb(self,*args,**kw):
        self.calls.append(args)
        if args[0]=='root':self.root=True
        if args[0]=='unroot':
            if self.unroot_fail:raise RuntimeError('unroot')
            self.root=False
        if args[0]=='reboot':
            self.ident=NEW;self.config=runner.ORIGINAL_CONFIG if self.wrong_return else runner.NATIVE_CONFIG
            self.root=False
            if self.uncertain:raise RuntimeError('reboot disconnected')
        return subprocess.CompletedProcess(args,0,b'',b'')
    def shell(self,command,**kw):
        self.calls.append(('shell',command))
        if command.startswith('dd '):
            path=command.split()[1][3:];expected=self.sources[path]
            if expected==CANDIDATE and self.partial:self.boot='f'*64;raise RuntimeError('partial write')
            if expected==runner.BOOT_SHA and self.restore_fail:raise RuntimeError('restore failed')
            self.boot=expected;return b''
        if command=='id':return b'uid=0(root)' if self.root else b'uid=2000(shell)'
        if command=='cat /proc/sys/kernel/random/boot_id':return self.ident.encode()
        if command=='getprop sys.boot_completed':return b'1'
        if command=='cat /sys/kernel/kexec_loaded':return b'0'
        if command.startswith('dmesg |'):return b''
        if command=='cat /proc/mounts':return b'tmpfs /dev tmpfs rw 0 0\n'
        if command=='cat /proc/meminfo':return b'MemAvailable: 131072 kB\n'
        if command=='sync' or command.startswith('rm -f '):return b''
        raise AssertionError('Unexpected shell command '+command)


class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.p=Path(t.name)
        self.report={'candidate_sha256':CANDIDATE,'original_boot_sha256':runner.BOOT_SHA,'resolved_config_sha256':runner.NATIVE_CONFIG}
        self.auth=self.p/'approval.json';self.auth.write_text(json.dumps({'scope':runner.SCOPE,'runner_sha256':runner.sha(Path(runner.__file__).read_bytes()),'candidate_sha256':CANDIDATE,'original_boot_sha256':runner.BOOT_SHA,'owner_approved':True,'owner_available':True,'maximum_candidate_writes':1,'maximum_restore_writes':1,'maximum_reboots':1,'recovery_writes_allowed':False,'experimental_jump_allowed':False}))
    def run_case(self,f,execute=True,out='result',wrong_source=False):
        def facts(d):
            return {'boot':d.boot,'config':'bad' if wrong_source else d.config,'boot_id':d.ident}
        def stage(d,file,expected):
            d.stages+=1;folder='/dev/test'+str(d.stages);d.sources[folder+'/boot.img']=expected;return folder,folder+'/boot.img'
        with patch.object(runner,'facts',side_effect=facts),patch.object(runner,'stage',side_effect=stage),patch.object(runner,'partition',side_effect=lambda d,n,s:d.boot if n==5 else runner.RECOVERY_SHA):
            return runner.run(f,'/lab/package',self.report,self.p/out,self.auth if execute else None)
    def result(self):return json.loads((self.p/'result/result.json').read_text())
    def test_preflight_has_no_write_or_reboot(self):
        f=Fake();r=self.run_case(f,False);self.assertTrue(r['complete']);self.assertTrue(r['normal_shell_restored']);self.assertEqual(f.stages,0);self.assertEqual(r['reboot_requests'],0)
    def test_one_boot_and_restore_leaves_native_ram_original_flash(self):
        f=Fake();r=self.run_case(f)
        self.assertTrue(r['complete']);self.assertTrue(r['native_kernel_running']);self.assertTrue(r['original_boot_restored']);self.assertEqual(f.boot,runner.BOOT_SHA);self.assertEqual(f.config,runner.NATIVE_CONFIG)
        self.assertEqual((r['candidate_write_attempts'],r['restore_write_attempts'],r['reboot_requests']),(1,1,1));self.assertFalse(r['experimental_jump_executed']);self.assertFalse(r['recovery_written'])
    def test_partial_install_restores_without_boot(self):
        f=Fake(partial=True)
        with self.assertRaises(RuntimeError):self.run_case(f)
        r=self.result();self.assertEqual(r['reboot_requests'],0);self.assertTrue(r['original_boot_restored']);self.assertFalse(r['complete']);self.assertEqual(f.boot,runner.BOOT_SHA)
    def test_wrong_source_never_installs(self):
        f=Fake()
        with self.assertRaises(ValueError):self.run_case(f,wrong_source=True)
        self.assertEqual(self.result()['candidate_write_attempts'],0);self.assertEqual(f.stages,0)
    def test_wrong_return_restores_and_does_not_reboot_twice(self):
        f=Fake(wrong_return=True)
        with self.assertRaises(ValueError):self.run_case(f)
        r=self.result();self.assertTrue(r['original_boot_restored']);self.assertEqual(r['reboot_requests'],1);self.assertFalse(r['native_kernel_running'])
    def test_failed_restore_is_not_retried(self):
        f=Fake(restore_fail=True)
        with self.assertRaises(RuntimeError):self.run_case(f)
        r=self.result();self.assertEqual(r['restore_write_attempts'],1);self.assertTrue(r['owner_attention_required']);self.assertFalse(r['original_boot_restored'])
    def test_unroot_failure_cannot_pass(self):
        r=self.run_case(Fake(unroot_fail=True));self.assertFalse(r['complete']);self.assertTrue(r['owner_attention_required']);self.assertTrue(r['original_boot_restored'])
    def test_reboot_transport_uncertainty_does_not_reissue(self):
        f=Fake(uncertain=True);r=self.run_case(f);self.assertTrue(r['complete']);self.assertEqual(sum(c[0]=='reboot' for c in f.calls),1)
    def test_timeout_restores_if_reachable_without_reboot_retry(self):
        f=Fake()
        with patch.object(runner.time,'monotonic',side_effect=[0,301]):
            with self.assertRaises(RuntimeError):self.run_case(f)
        r=self.result();self.assertTrue(r['original_boot_restored']);self.assertEqual(r['reboot_requests'],1)
    def test_bad_approval_is_rejected_before_root(self):
        a=json.loads(self.auth.read_text());a['maximum_candidate_writes']=2;self.auth.write_text(json.dumps(a));f=Fake()
        with self.assertRaises(ValueError):self.run_case(f)
        self.assertEqual(f.calls,[])
    def test_same_approval_cannot_be_reused(self):
        self.run_case(Fake());f=Fake()
        with self.assertRaises(FileExistsError):self.run_case(f,out='again')
        self.assertEqual(f.calls,[])


if __name__=='__main__':unittest.main()
