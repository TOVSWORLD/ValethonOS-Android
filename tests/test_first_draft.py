"""Combined draft keeps logging/security while adding integrated providers."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import first_draft_config as config
from select_kernel_build_scope import choose

class Draft(unittest.TestCase):
    def test_logging_and_enforcement_are_not_sacrificed_for_provider_integration(self):
        req=config.requirements()
        for symbol in ['USB_CONFIGFS_ACM','MMC_MTK','SECURITY_SELINUX','DRM_MEDIATEK','PWM_MTK_DISP','REGULATOR_FAN53555','ANDROID_BINDER_IPC']:
            self.assertEqual(req[symbol],'y')
        self.assertEqual(req['SECURITY_SELINUX_DEVELOP'],'n')
        self.assertEqual(req['LOG_BUF_SHIFT'],'20')
        self.assertEqual(req['PANIC_TIMEOUT'],'0')
    def test_explicit_combined_build_rejects_unrelated_forced_commandline(self):
        self.assertEqual(choose('workflow_dispatch',mode='first-draft')['mode'],'first-draft')
        with self.assertRaises(ValueError):choose('workflow_dispatch',mode='first-draft',argument_profile='generic-force')
