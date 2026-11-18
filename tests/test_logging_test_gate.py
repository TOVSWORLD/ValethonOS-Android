"""Regression tests for the unqualified physical measurement hold."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import guard_loader_observer as observer
import logging_test_gate as gate


class LoggingGate(unittest.TestCase):
    def test_no_model_or_receipt_override(self):
        with self.assertRaisesRegex(ValueError, 'no known-kernel logging control'):
            gate.require_logging_control()

    def test_install_stops_before_preflight_or_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = Path(folder)/'receipt.json'
            with patch.object(observer, 'sha', return_value=observer.CANDIDATE), patch.object(observer, 'preflight') as preflight:
                with self.assertRaisesRegex(ValueError, 'logging control'):
                    observer.write_once(object(), b'x'*observer.SIZE, {}, observer.ORIGINAL, observer.ORIGINAL_BOOT, receipt)
                preflight.assert_not_called()
                self.assertFalse(receipt.exists())

    def test_original_restore_reaches_existing_guards(self):
        # The new hold must never obstruct an existing original rollback.
        with patch.object(observer, 'sha', return_value=observer.ORIGINAL), patch.object(observer, 'require_logging_control') as hold, patch.object(observer, 'preflight', side_effect=ValueError('existing rollback guard')):
            with self.assertRaisesRegex(ValueError, 'existing rollback guard'):
                observer.write_once(object(), b'x'*observer.SIZE, {}, observer.CANDIDATE, observer.ORIGINAL_BOOT, Path('/unused'))
            hold.assert_not_called()

    def test_candidate_write_and_arm_stop_before_reading_inputs(self):
        # Nonexistent inputs prove these entry points stop before ADB construction.
        commands = [
            ('write_lab_boot_candidate.py', ['selector-file','candidate','candidate-report','original-boot','rollback-manifest'], '--write-candidate'),
            ('run_lab_log_trial.py', ['plan','candidate-report','nonce','output','modules','initial-usb-identity','selector-file','candidate','original-boot','rollback-manifest','receipt'], '--arm-once'),
        ]
        for script, arguments, action in commands:
            args = [sys.executable, str(ROOT/'scripts'/script), action]
            for name in arguments:
                args += ['--'+name, '/nonexistent-logging-gate-fixture']
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)
