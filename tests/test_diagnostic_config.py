import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('diagnostic_config', Path(__file__).resolve().parents[1] / 'scripts/diagnostic_config.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DiagnosticConfiguration(unittest.TestCase):
    def test_modular_and_builtin_storage_are_rejected(self):
        for state in ['m', 'y']:
            with self.assertRaisesRegex(ValueError, 'CONFIG_BLOCK'):
                module.check('CONFIG_BLOCK=' + state, {'BLOCK': 'n'})

    def test_missing_or_modular_console_is_rejected(self):
        for config in ['', 'CONFIG_SERIAL_8250_CONSOLE=m']:
            with self.assertRaises(ValueError):
                module.check(config, {'SERIAL_8250_CONSOLE': 'y'})

    def test_retained_generic_config_is_not_diagnostic(self):
        path = Path(__file__).resolve().parents[1] / 'evidence/pinctrl-port/combined-image.config'
        with self.assertRaises(ValueError):
            module.check(path.read_text(), module.policy())

    def test_disabled_or_absent_symbols_do_not_compile(self):
        self.assertTrue(module.check('# CONFIG_BLOCK is not set\nCONFIG_SERIAL_8250_CONSOLE=y',
                                     {'BLOCK': 'n', 'MMC': 'n', 'SERIAL_8250_CONSOLE': 'y'})['passed'])

    def test_ram_logging_is_builtin_and_block_backend_disabled(self):
        requirements = module.policy()
        for symbol in ('PSTORE', 'PSTORE_RAM', 'PSTORE_CONSOLE'):
            self.assertEqual(requirements[symbol], 'y')
            for actual in ('m', 'n'):
                with self.assertRaisesRegex(ValueError, symbol):
                    module.check('CONFIG_' + symbol + '=' + actual, {symbol: 'y'})
        self.assertEqual(requirements['PSTORE_BLK'], 'n')
        with self.assertRaises(ValueError):
            module.check('CONFIG_PSTORE_BLK=y', {'PSTORE_BLK': 'n'})

    def test_old_compiled_config_cannot_pass_current_logging_policy(self):
        path = Path(__file__).resolve().parents[1] / 'evidence/diagnostic-kernel/diagnostic.config'
        with self.assertRaisesRegex(ValueError, 'PSTORE_RAM'):
            module.check(path.read_text(), module.policy())
