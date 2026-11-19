import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import display_direct_device as direct


class DirectDisplayGuards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.case=Path(self.tmp.name);self.candidate=b'ANDROID!'+bytes(direct.BOOT_BYTES-8)
        self.original=b'ANDROID!'+bytes([1])*(direct.BOOT_BYTES-8)
        self.manifest={'recovery':{'bytes':17825792,'sha256':direct.RECOVERY}}

    def test_default_preflight_never_installs_or_reboots(self):
        with patch.object(direct,'inputs',return_value=(self.candidate,self.original,self.manifest)),\
             patch.object(direct,'preflight') as check,patch.object(direct,'restore') as write:
            direct.run(self.case,object(),'preflight');check.assert_called_once();write.assert_not_called()

    def test_rollback_refuses_without_verified_owned_install(self):
        (self.case/'install-receipt.json').write_text(json.dumps({'verified':False}))
        with patch.object(direct,'inputs',return_value=(self.candidate,self.original,self.manifest)),\
             patch.object(direct,'restore') as write:
            with self.assertRaises(ValueError):direct.run(self.case,object(),'restore')
            write.assert_not_called()

    def test_rollback_requires_exact_current_candidate_and_exclusive_receipt(self):
        (self.case/'install-receipt.json').write_text(json.dumps({'verified':True,'rollback_sha256':direct.sha(self.candidate)}))
        with patch.object(direct,'inputs',return_value=(self.candidate,self.original,self.manifest)),\
             patch.object(direct,'restore') as write:
            device=object();direct.run(self.case,device,'restore')
            write.assert_called_once_with(device,self.original,self.manifest,direct.sha(self.candidate),self.case/'restore-receipt.json')

    def test_package_drift_rejects_before_device_access(self):
        from unittest.mock import mock_open
        # Full original is pinned independently; an arbitrary package never gets
        # past backup verification, even with an apparently matching approval.
        for name,data in [('boot-full.img',self.candidate),('original-boot.img',self.original),
                          ('trial-nonce-private.bin',bytes([2])*32)]:
            (self.case/name).write_bytes(data)
        for name in ['report.json','owner-authorization-private.json']:(self.case/name).write_text('{}')
        with self.assertRaises(ValueError):direct.inputs(self.case)

    def test_consumed_first_direct_scope_cannot_authorize_corrected_test(self):
        nonce=bytes([2])*32
        for name,data in [('boot-full.img',self.candidate),('original-boot.img',self.original),
                          ('trial-nonce-private.bin',nonce)]:
            (self.case/name).write_bytes(data)
        (self.case/'report.json').write_text('{}')
        auth=dict(scope='display-direct-coldboot-1',candidate_sha256=direct.sha(self.candidate),
                  nonce_sha256=direct.sha(nonce),runner_sha256=direct.sha(Path(direct.__file__).read_bytes()),
                  owner_approved=True,maximum_candidate_writes=1,maximum_original_restore_writes=1,
                  recovery_writes_allowed=False,automatic_trial_retry=False)
        (self.case/'owner-authorization-private.json').write_text(json.dumps(auth))
        with patch.object(direct,'validate_backup'):
            with self.assertRaisesRegex(ValueError,'authorization'):direct.inputs(self.case)
