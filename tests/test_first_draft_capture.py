from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_first_draft_capture import prepare


class CaptureOnly(unittest.TestCase):
    def fixture(self,root):
        p=root/'package';p.mkdir();nonce=bytes(range(32));image=b'ANDROID!'+bytes(16777216-8)
        (p/'boot-full.img').write_bytes(image);(p/'nonce-private.bin').write_bytes(nonce)
        (p/'report.json').write_text(json.dumps({'partition_sha256':hashlib.sha256(image).hexdigest(),'nonce_sha256':hashlib.sha256(nonce).hexdigest()}))
        return p
    def test_five_minute_capture_has_no_return_or_restore_action(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=self.fixture(root);out=root/'capture';result=prepare(p,'1-2',out)
            plan=json.loads((out/'capture-plan-private.json').read_text())
            self.assertEqual(plan['wait_seconds'],300);self.assertEqual(plan['minimum_no_intervention_seconds'],300)
            for key in ['automatic_return_helper','automatic_restore','automatic_reboot']:self.assertIs(plan[key],False)
            self.assertFalse(result['armed']);self.assertEqual(out.stat().st_mode & 0o777,0o700)
    def test_changed_package_or_invalid_identity_stops_before_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=self.fixture(root);out=root/'capture'
            with self.assertRaises(ValueError):prepare(p,'auto',out)
            self.assertFalse(out.exists())
            (p/'nonce-private.bin').write_bytes(bytes([1])*32)
            with self.assertRaises(ValueError):prepare(p,'1-2',out)
            self.assertFalse(out.exists())
