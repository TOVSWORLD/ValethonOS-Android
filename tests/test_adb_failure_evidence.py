"""Private transport evidence is retained without repeating a device command."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import restore_diagnostic_boot as r
import pull_retained_mailbox as p
import retained_log_mailbox as m
from test_restore_diagnostic_boot import BACKUP,MANIFEST,FakeAdb


class TransportEvidence(unittest.TestCase):
    def test_exit_and_timeout_preserve_bytes_but_sanitize_error(self):
        for timeout in [False,True]:
            result=subprocess.CompletedProcess([],1,b'private partial',b'private selector')
            effect=subprocess.TimeoutExpired(['private selector'],90,output=result.stdout,stderr=result.stderr) if timeout else None
            with patch.object(r.subprocess,'run',return_value=result,side_effect=effect) as run:
                with self.assertRaises(r.AdbCommandError) as caught:r.Adb('adb','private selector').read(r.RECOVERY,r.RECOVERY_BYTES)
                error=caught.exception
                self.assertEqual(run.call_count,1)
                self.assertEqual(error.stdout,b'private partial')
                self.assertEqual(error.stderr,b'private selector')
                self.assertEqual(error.details['transport_timed_out'],timeout)
                self.assertNotIn('private',str(error))
                self.assertNotIn('private',str(error.details))

    def test_collection_retains_both_streams_without_valid_readout(self):
        nonce=bytes(range(32));candidate,_=m.prepare(BACKUP,nonce)
        class Failed(FakeAdb):
            reads=0
            def read(self,node,size):
                self.reads+=1
                raise r.AdbCommandError(b'partial',b'private transport detail',1)
        adb=Failed();adb.boot=candidate
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'failure'
            with self.assertRaises(p.CollectionError) as caught:p.collect(adb,BACKUP,MANIFEST,candidate,nonce,output)
            self.assertEqual(caught.exception.reason,'adb_command_failed')
            for name,value in [('failed-adb-stdout-private.bin',b'partial'),('failed-adb-stderr-private.bin',b'private transport detail')]:
                path=output/name;self.assertEqual(path.read_bytes(),value)
                self.assertEqual(path.stat().st_mode & 0o777,0o600)
            self.assertFalse((output/'report.json').exists())
            self.assertFalse((output/'boot-after-trial-private.img').exists())
            self.assertEqual(adb.reads,1);self.assertEqual(adb.writes,0)
