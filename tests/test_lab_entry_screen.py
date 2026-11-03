from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import apply_lab_entry_screen as entry


class LabEntryScreen(unittest.TestCase):
    def test_exact_source_patch_and_no_reapplication(self):
        lock = entry.contract()
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)
            target = source / lock['target']
            target.parent.mkdir(parents=True)
            original = (ROOT / lock['source']).read_bytes()
            target.write_bytes(original)
            with self.assertRaises(ValueError):
                entry.apply(source, 'wrong')
            self.assertEqual(target.read_bytes(), original)
            result = entry.apply(source, lock['ack_commit'])
            self.assertFalse(result['runtime_qualified'])
            self.assertFalse(result['device_written'])
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), lock['patched_sha256'])
            with self.assertRaises(ValueError):
                entry.apply(source, lock['ack_commit'])

    def test_source_drift_and_existing_overlay_fail_before_edit(self):
        lock = entry.contract()
        for drift in (True, False):
            with self.subTest(drift=drift), tempfile.TemporaryDirectory() as folder:
                source = Path(folder)
                target = source / lock['target']; target.parent.mkdir(parents=True)
                original = (ROOT / lock['source']).read_bytes()
                target.write_bytes(original + (b'\n' if drift else b''))
                if not drift:
                    (source / lock['overlay_target']).write_text('existing')
                before = target.read_bytes()
                with self.assertRaises(ValueError):
                    entry.apply(source, lock['ack_commit'])
                self.assertEqual(target.read_bytes(), before)

    def test_metadata_integrity_and_ownership_rejected(self):
        lock = entry.contract()
        original = json.loads((ROOT / lock['metadata_source']).read_text())
        for mode in ('hash', 'ownership'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); port = root / 'port'; port.mkdir()
                path = root / lock['metadata_source']; path.parent.mkdir(parents=True)
                data = json.loads(json.dumps(original))
                data['firmware_handoff_tag']['fb_base'] = '0x0'
                path.write_text(json.dumps(data))
                changed = dict(lock)
                if mode == 'ownership':
                    changed['metadata_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                (port / 'inputs.json').write_text(json.dumps(changed))
                with patch.object(entry, 'ROOT', root), patch.object(entry, 'PORT', port):
                    with self.assertRaises(ValueError):
                        entry.contract()
