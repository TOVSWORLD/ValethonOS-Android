import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import run_pstore_warm_reboot as runner

OLD='11111111-1111-1111-1111-111111111111'
NEW='22222222-2222-2222-2222-222222222222'


class Fake:
    def __init__(self, retained=True, marker_fail=False, unroot_fail=False, reboot_transport_fail=False):
        self.root=False;self.boot=OLD;self.calls=[];self.marker=None
        self.retained=retained;self.marker_fail=marker_fail;self.unroot_fail=unroot_fail
        self.reboot_transport_fail=reboot_transport_fail
    def adb(self,*args,**kw):
        self.calls.append(args)
        if args[0]=='root':self.root=True
        if args[0]=='unroot':
            if self.unroot_fail:raise RuntimeError('unroot failed')
            self.root=False
        if args[0]=='reboot':
            self.boot=NEW
            if self.reboot_transport_fail:raise RuntimeError('disconnect during accepted reboot')
        return subprocess.CompletedProcess(args,0,b'',b'')
    def shell(self,command,**kw):
        self.calls.append(('shell',command))
        if command=='id':return b'uid=0(root)' if self.root else b'uid=2000(shell)'
        if command.startswith('printf '):
            if self.marker_fail:raise RuntimeError('marker write failed')
            import shlex
            self.marker=shlex.split(command)[1][3:].strip();return b''
        if command.startswith('dmesg | grep'):return ('[ 1.0] '+self.marker+'\n').encode()
        if command.startswith('for f in /sys/fs/pstore/console-ramoops'):
            return (self.marker+'\n').encode() if self.retained else b''
        if command=='cat /proc/sys/kernel/random/boot_id':return self.boot.encode()+b'\n'
        if command=='getprop sys.boot_completed':return b'1\n'
        raise AssertionError('Unexpected shell command '+command)


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.p=Path(self.temp.name);self.auth=self.p/'approval.json'
        self.auth.write_text(json.dumps({'scope':runner.SCOPE,'runner_sha256':runner.sha(runner.RUNNER.read_bytes()),
          'target_boot_sha256':runner.BOOT_SHA,'owner_approved':True,'owner_available':True,
          'maximum_marker_writes':1,'maximum_reboots':1,'boot_writes_allowed':False,
          'module_loading_allowed':False,'handoff_allowed':False,'approval_id':'a'*32}))
    def run_test(self,f,execute=True,out='result',verify=None):
        with patch.object(runner,'verify_source',side_effect=verify or (lambda d:d.boot)):
            # Preflight listing remains empty; readout is handled separately.
            original=f.shell
            def shell(command,**kw):
                if command=='ls -1 /sys/fs/pstore':return b''
                return original(command,**kw)
            with patch.object(f,'shell',side_effect=shell):
                return runner.run(f,self.p/out,self.auth if execute else None)
    def test_preflight_has_no_marker_or_reboot(self):
        f=Fake();r=self.run_test(f,False)
        self.assertTrue(r['complete']);self.assertTrue(r['normal_shell_restored'])
        self.assertEqual(r['marker_write_attempts'],0);self.assertEqual(r['reboot_requests'],0)
        self.assertFalse(any(a[0]=='reboot' for a in f.calls));self.assertIsNone(f.marker)
    def test_one_marker_one_reboot_retention_and_cleanup(self):
        f=Fake();r=self.run_test(f)
        self.assertTrue(r['complete']);self.assertTrue(r['orderly_warm_reboot_retention_qualified'])
        self.assertFalse(r['failed_handoff_retention_qualified']);self.assertTrue(r['normal_shell_restored'])
        self.assertEqual(sum(a[0]=='reboot' for a in f.calls),1)
        self.assertEqual(sum(a[0]=='shell' and a[1].startswith('printf ') for a in f.calls),1)
        self.assertNotEqual(r['source_boot_id_sha256'],r['target_boot_id_sha256'])
        self.assertFalse(r['pstore_records_deleted']);self.assertFalse(r['personal_log_contents_collected'])
    def test_absent_marker_is_inconclusive_and_does_not_retry(self):
        f=Fake(retained=False);r=self.run_test(f)
        self.assertTrue(r['complete']);self.assertFalse(r['orderly_warm_reboot_retention_qualified'])
        self.assertEqual(r['outcome'],'inconclusive-marker-absent-or-nonunique')
        self.assertEqual(sum(a[0]=='reboot' for a in f.calls),1)
    def test_failed_marker_never_reboots_and_restores(self):
        f=Fake(marker_fail=True)
        with self.assertRaises(RuntimeError):self.run_test(f)
        self.assertFalse(any(a[0]=='reboot' for a in f.calls));self.assertFalse(f.root)
        self.assertFalse(json.loads((self.p/'result/result.json').read_text())['complete'])
    def test_failed_unroot_cannot_report_completion(self):
        r=self.run_test(Fake(unroot_fail=True));self.assertFalse(r['complete'])
        self.assertFalse(r['normal_shell_restored'])
    def test_bad_approval_rejected_before_root(self):
        a=json.loads(self.auth.read_text());a['maximum_reboots']=2;self.auth.write_text(json.dumps(a));f=Fake()
        with self.assertRaises(ValueError):self.run_test(f)
        self.assertEqual(f.calls,[])
    def test_approval_cannot_be_reused(self):
        self.run_test(Fake());f=Fake()
        with self.assertRaises(FileExistsError):self.run_test(f,out='again')
        self.assertEqual(f.calls,[])
    def test_wrong_source_cannot_write_or_reboot(self):
        f=Fake()
        with self.assertRaises(ValueError):self.run_test(f,verify=ValueError('wrong source'))
        self.assertFalse(any(a[0]=='reboot' for a in f.calls));self.assertIsNone(f.marker)
        self.assertFalse(f.root)
    def test_uncertain_reboot_transport_is_not_reissued(self):
        f=Fake(reboot_transport_fail=True);r=self.run_test(f)
        self.assertTrue(r['complete']);self.assertTrue(r['reboot_transport_uncertain'])
        self.assertEqual(sum(a[0]=='reboot' for a in f.calls),1)
    def test_changed_target_rejected_without_second_reboot(self):
        f=Fake()
        with self.assertRaises(ValueError):self.run_test(f,verify=[OLD,ValueError('changed target')])
        self.assertEqual(sum(a[0]=='reboot' for a in f.calls),1);self.assertFalse(f.root)
    def test_return_timeout_stops_without_retry(self):
        f=Fake()
        with patch.object(runner.time,'monotonic',side_effect=[0,241]):
            with self.assertRaises(RuntimeError):self.run_test(f)
        self.assertEqual(sum(a[0]=='reboot' for a in f.calls),1);self.assertFalse(f.root)
    def test_nonzero_and_missing_remote_status_rejected(self):
        for data in [b'payload',b'payload\nTAG=1\n',b'payload\nTAG=0\nextra']:
            with self.assertRaises(RuntimeError):runner.framed_result(data,b'TAG')
        self.assertEqual(runner.framed_result(b'payload\nTAG=0\n',b'TAG'),b'payload')


if __name__=='__main__':unittest.main()
