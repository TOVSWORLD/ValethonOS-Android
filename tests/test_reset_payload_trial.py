import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_reset_payload_trial as trial
from build_reset_payload import build, QUALIFIED_IMAGE_SHA


class TwoStageGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.payload_dir = Path(cls.tmp.name) / 'payload'
        cls.payload = build(cls.payload_dir, 'b' * 32)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        d = tempfile.TemporaryDirectory(); self.addCleanup(d.cleanup)
        self.p = Path(d.name)
        self.q = dict(source_sha256=self.payload['source_sha256'],
                      qualified_canonical_image_sha256=QUALIFIED_IMAGE_SHA,
                      all_required_tests_passed=True, tests_skipped=0)
        self.policy = dict(scope=trial.SCOPE_TWO_STAGE, target_kind='reset-payload-v1',
                           source_cpu_shutdown_before_devices=True,
                           failure_policy='pivot_after_one_failed_or_inconclusive_jump',
                           reset_payload_report_sha256=trial.digest(self.payload_dir / 'report.json'),
                           qualified_canonical_image_sha256=QUALIFIED_IMAGE_SHA)
        self.a = SimpleNamespace(policy=self.p / 'policy.json', image=self.payload_dir / 'Image',
                                 payload_report=self.payload_dir / 'report.json',
                                 emulation_report=self.p / 'emulation.json',
                                 source_package=self.p / 'package', linked_report=self.p / 'linked',
                                 capture_report=self.p / 'capture', helper=self.p / 'helper',
                                 authorization=None, output=self.p / 'out')

    def write(self):
        self.a.emulation_report.write_text(json.dumps(self.q))
        self.policy['reset_emulation_report_sha256'] = trial.digest(self.a.emulation_report)
        self.a.policy.write_text(json.dumps(self.policy))

    def refuses_before_connection(self):
        self.write()
        with patch.object(trial, 'validate_source'), patch.object(trial, 'LabADB') as connection:
            with self.assertRaises(ValueError):
                trial.run(self.a)
            connection.assert_not_called()

    def test_qualified_scope_can_reach_read_only_source_validation(self):
        self.write()
        with patch.object(trial, 'validate_source') as source:
            p, _ = trial.validate(self.a)
            self.assertEqual(p['scope'], trial.SCOPE_TWO_STAGE)
            source.assert_called_once()

    def test_legacy_scope_refused(self):
        self.policy['scope'] = 'early-cpu-shutdown-two-stage-trial-1'
        self.refuses_before_connection()

    def test_additional_cpu_experiment_refused(self):
        self.policy['target_cpu_limit'] = 1
        self.refuses_before_connection()

    def test_missing_terminal_pivot_policy_refused(self):
        self.policy['failure_policy'] = 'try_again'
        self.refuses_before_connection()

    def test_skipped_emulator_cannot_authorize_hardware(self):
        self.q['tests_skipped'] = 1
        self.refuses_before_connection()

    def test_emulation_of_different_source_cannot_authorize_hardware(self):
        self.q['source_sha256'] = '0' * 64
        self.refuses_before_connection()


if __name__ == '__main__':
    unittest.main()
