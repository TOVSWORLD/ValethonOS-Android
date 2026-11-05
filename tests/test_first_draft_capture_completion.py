"""A finished or failed host waiter must not retain a live-armed claim."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import first_draft_capture_after_boot as runner

class Completion(unittest.TestCase):
    def run_case(self,error):
        with tempfile.TemporaryDirectory() as folder:
            case=Path(folder);(case/'private').mkdir()
            data={'capture-plan-private.json':{'wait_seconds':300,'minimum_no_intervention_seconds':300,'automatic_return_helper':False,'automatic_restore':False,'automatic_reboot':False,'physical_usb_path':'1-2'},'candidate-report.json':{'partition_sha256':'0'*64},'install-receipt.json':{'verified':True,'rollback_sha256':'0'*64},'initial-usb-identity.json':{'vendor':'abcd','product':'ef00'}}
            def read(path,maximum):return bytes(range(32)) if path.name=='nonce-private.bin' else json.dumps(data[path.name]).encode()
            with patch.object(runner,'private_bytes',side_effect=read),patch.object(runner,'validate'),patch.object(runner,'wait_departure',side_effect=error,return_value=123),patch.object(runner,'capture',return_value={'complete':False}),patch.object(sys,'argv',['capture','--case',str(case)]),contextlib.redirect_stdout(io.StringIO()):
                if error:
                    with self.assertRaises(TimeoutError):runner.main()
                else:runner.main()
            result=json.loads((case/'private/capture-arm-receipt.json').read_text())
            self.assertFalse(result['armed']);self.assertTrue(result['capture_finished']);self.assertFalse(result['capture_complete'])
            return result
    def test_completed_receiver_clears_arm(self):self.run_case(None)
    def test_travel_timeout_clears_arm(self):self.assertEqual(self.run_case(TimeoutError('travel'))['failure_kind'],'TimeoutError')
