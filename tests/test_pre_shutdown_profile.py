import ast
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_pre_shutdown_control import profile_guard,SCOPE


class Profile(unittest.TestCase):
    def test_every_candidate_prefix_seed_and_scope_is_rebound(self):
        template=(Path(__file__).resolve().parents[1]/'scripts/guard_known_boot_capture.py').read_text()
        manifest={'snapshot_stage':'pre_shutdown','checkpoint_site':'0x4bd3e3e8',
                  'candidate_sha256':'1'*64,'observer_sha256':'2'*64,'prefix_sha256':'3'*64,'seed_sha256':'4'*64}
        result=profile_guard(template,manifest)
        values={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(result).body
                if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)
                and n.targets[0].id in ['CANDIDATE','KERNEL_CANDIDATE','CONTROL_PREFIX','CONTROL_SEED']}
        self.assertEqual(values,{'CANDIDATE':'2'*64,'KERNEL_CANDIDATE':'1'*64,'CONTROL_PREFIX':'3'*64,'CONTROL_SEED':'4'*64})
        self.assertIn(repr(SCOPE),result);self.assertNotIn("'known-boot-capture-control-1'",result)

    def test_unknown_profile_and_missing_bindings_are_rejected(self):
        template=(Path(__file__).resolve().parents[1]/'scripts/guard_known_boot_capture.py').read_text()
        with self.assertRaises(ValueError):profile_guard(template,{'snapshot_stage':'pre_handoff'})
        manifest={'snapshot_stage':'pre_shutdown','checkpoint_site':'0x4bd3e3e8',
                  'candidate_sha256':'1'*64,'observer_sha256':'2'*64,'prefix_sha256':'3'*64,'seed_sha256':'invalid'}
        with self.assertRaises(ValueError):profile_guard(template,manifest)
