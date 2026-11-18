from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import lab_log_config
from build_lab_log_initramfs import inspect_archive
from build_diagnostic_initramfs import archive
from select_kernel_build_scope import choose


class LabLogComponent(unittest.TestCase):
    def test_config_composition_and_security_negatives(self):
        required = lab_log_config.requirements()
        self.assertEqual(required['ARCH_MEDIATEK'], 'y')
        self.assertEqual(required['ARCH_QCOM'], 'n')
        self.assertNotIn('ARCH_HAS_STRICT_KERNEL_RWX', required)
        self.assertEqual(required['BLOCK'], 'n')
        self.assertEqual(required['USB_MUSB_MEDIATEK'], 'y')
        self.assertEqual(required['SECURITY_SELINUX'], 'y')
        self.assertEqual(required['SECURITY_SELINUX_DEVELOP'], 'n')
        self.assertEqual(required['SECURITY_SELINUX_BOOTPARAM'], 'n')
        text = '\n'.join('CONFIG_' + k + '=' + v for k, v in required.items() if v != 'n')
        lab_log_config.diagnostic_config.check(text, required)
        for name, value in [('BLOCK', 'y'), ('SECURITY_SELINUX', 'n'),
                            ('SECURITY_SELINUX_DEVELOP', 'y'), ('USB_GADGET', 'n')]:
            mutated = '\n'.join(line for line in text.splitlines() if not line.startswith('CONFIG_' + name + '='))
            with self.assertRaises(ValueError):
                lab_log_config.diagnostic_config.check(mutated + '\nCONFIG_' + name + '=' + value, required)
        self.assertEqual(choose('workflow_dispatch', mode='lab-log')['mode'], 'lab-log')
        with self.assertRaises(ValueError):
            choose('workflow_dispatch', mode='lab-log', argument_profile='generic-force')
        with self.assertRaises(ValueError):
            choose('workflow_dispatch', mode='lab-log', emulated_boot=True)

    def test_archive_independent_validation_and_negative_mutations(self):
        entries = [(n, 0o040755, b'', (0, 0)) for n in ['dev', 'proc', 'sys', 'security', 'config']]
        entries += [('dev/console', 0o020600, b'', (5, 1)),
                    ('dev/kmsg', 0o020400, b'', (1, 11)), ('init', 0o100500, b'ELF-fixture', (0, 0))]
        raw = archive(entries)
        self.assertEqual(inspect_archive(raw, entries), [e[0] for e in entries])
        for changed in [raw[:-1] + b'X', b'X' + raw[1:], raw[:115] + b'X' + raw[116:]]:
            with self.assertRaises(ValueError):
                inspect_archive(changed, entries)
        wrong = entries.copy()
        wrong[6] = ('dev/kmsg', 0o020600, b'', (1, 11))
        with self.assertRaises(ValueError):
            inspect_archive(archive(wrong), wrong)
