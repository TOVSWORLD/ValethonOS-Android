import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('contents', Path(__file__).resolve().parents[1] / 'scripts/check_android_product_contents.py')
contents = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contents)


class ProductContentsAudit(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.product = self.root / 'out/target/product/douglas'
        self.product.mkdir(parents=True)
        self.modules = {}
        for name in contents.REQUIRED:
            path = self.product / 'system/app' / name / (name + '.apk')
            path.parent.mkdir(parents=True)
            path.write_bytes(b'fixture')
            self.modules[name] = {'installed': [str(path.relative_to(self.root))]}
        (self.product / 'system/media').mkdir()
        (self.product / 'system/media/bootanimation.zip').write_bytes(b'fixture')
        (self.product / 'system.img').write_bytes(b'fixture')
        (self.product / 'ramdisk.img').write_bytes(b'fixture')
        self.info = self.product / 'module-info.json'

    def run_audit(self):
        self.info.write_text(json.dumps(self.modules))
        with patch.object(contents.subprocess, 'run') as run:
            run.return_value.stdout = "package: name='com.android.webview' versionName='test'"
            return contents.audit(self.root, self.product, self.info, Path('/aapt2'))

    def test_declared_but_uninstalled_provider_is_rejected(self):
        self.modules['webview']['installed'] = []
        with self.assertRaisesRegex(ValueError, 'no installed output'):
            self.run_audit()

    def test_security_service_graph_entry_without_actual_file_is_rejected(self):
        name = 'android.hardware.security.keymint-service.nonsecure'
        path = self.root / self.modules[name]['installed'][0]
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'Missing or out-of-product'):
            self.run_audit()

    def test_gatekeeper_package_is_required_for_the_grouped_profile(self):
        self.modules['com.android.hardware.gatekeeper.rust.nonsecure']['installed'] = []
        with self.assertRaisesRegex(ValueError, 'no installed output'):
            self.run_audit()

    def test_compressed_apex_cannot_consume_volatile_data_budget(self):
        path = self.product / 'system/apex/unexpected.capex'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'fixture')
        with self.assertRaisesRegex(ValueError, 'Compressed APEX'):
            self.run_audit()

    def test_host_adbd_does_not_substitute_for_device_apex(self):
        self.modules['com.android.adbd']['installed'] = []
        self.modules['adbd'] = {'installed': ['out/host/linux-x86/bin/adbd']}
        with self.assertRaisesRegex(ValueError, 'com.android.adbd'):
            self.run_audit()

    def test_installed_path_outside_product_is_rejected(self):
        self.modules['webview']['installed'] = ['../../outside.apk']
        with self.assertRaisesRegex(ValueError, 'out-of-product'):
            self.run_audit()

    def test_android_system_root_symlink_resolves_inside_built_image(self):
        target = self.product / 'system/product/lib/libjni_latinime.so'
        target.parent.mkdir(parents=True)
        target.write_bytes(b'built device library')
        link = self.product / 'system/app/LatinIME/libjni_latinime.so'
        link.symlink_to('/system/product/lib/libjni_latinime.so')
        self.modules['LatinIME']['installed'].append(str(link.relative_to(self.root)))
        result = self.run_audit()
        self.assertEqual(result['packages']['LatinIME'][-1]['resolved_path'],
                         'system/product/lib/libjni_latinime.so')

    def test_installed_symlink_cannot_use_host_file(self):
        link = self.product / 'system/app/LatinIME/host'
        link.symlink_to('/etc/hosts')
        self.modules['LatinIME']['installed'].append(str(link.relative_to(self.root)))
        with self.assertRaisesRegex(ValueError, 'Out-of-product installed symlink'):
            self.run_audit()

    def test_sparse_size_uses_expanded_not_small_file_size(self):
        header = struct.pack('<IHHHHIIII', 0xed26ff3a, 1, 0, 28, 12, 4096,
                             contents.LIMIT // 4096 + 1, 1, 0)
        (self.product / 'system.img').write_bytes(header)
        with self.assertRaisesRegex(ValueError, 'exceeds existing partition'):
            self.run_audit()

    def test_output_never_claims_tablet_or_persistent_storage_pass(self):
        result = self.run_audit()
        self.assertFalse(result['tablet_runtime_verified'])
        self.assertEqual(result['storage_profile'], 'volatile-data')
        self.assertEqual(set(result['packages']), set(contents.REQUIRED))
