from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import apply_lab_watchdog
import lab_log_config


class LabWatchdog(unittest.TestCase):
    def test_patch_exact_match_and_reject_wrong_inputs_or_reapplication(self):
        lock = json.loads((apply_lab_watchdog.PORT / 'inputs.json').read_text())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / lock['target']; path.parent.mkdir(parents=True)
            original = (ROOT / lock['source']).read_bytes(); path.write_bytes(original)
            with self.assertRaises(ValueError):
                apply_lab_watchdog.apply(root, 'wrong')
            self.assertEqual(path.read_bytes(), original)
            self.assertFalse(apply_lab_watchdog.apply(root, lock['ack_commit'])['runtime_qualified'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), lock['patched_sha256'])
            with self.assertRaises(ValueError):
                apply_lab_watchdog.apply(root, lock['ack_commit'])

    def test_boot_enabled_handoff_is_explicit_and_no_userspace_watchdog(self):
        required = lab_log_config.requirements()
        for name in ['WATCHDOG', 'WATCHDOG_CORE', 'MEDIATEK_WATCHDOG', 'WATCHDOG_HANDLE_BOOT_ENABLED']:
            self.assertEqual(required[name], 'y')
        self.assertEqual(required['WATCHDOG_OPEN_TIMEOUT'], '0')
        self.assertEqual(required['WATCHDOG_PRETIMEOUT_GOV'], 'n')
        self.assertNotIn('watchdog', (ROOT / 'scripts/build_lab_log_initramfs.py').read_text())

    def test_actual_upstream_init_only_services_inherited_running_timer(self):
        source = (ROOT / 'evidence/independent-recovery/watchdog-source/mtk_wdt.c').read_text()
        start = source.index('static void mtk_wdt_init(')
        code = source[start:source.index('\nstatic int mtk_wdt_stop', start)]
        harness = '''#include <assert.h>
#define __iomem
#define WDOG_HW_RUNNING 0
#define WDT_MODE 0
#define WDT_MODE_EN 1
struct watchdog_device {unsigned long status;unsigned timeout;};
struct mtk_wdt_dev {void *wdt_base;};
static unsigned mode,calls;static struct mtk_wdt_dev dev;
static void *watchdog_get_drvdata(struct watchdog_device *w){(void)w;return &dev;}
static unsigned readl(void *p){(void)p;return mode;}
static void set_bit(unsigned b,unsigned long *p){*p|=1UL<<b;}
static int mtk_wdt_set_timeout(struct watchdog_device *w,unsigned t){assert(t==31);calls++;(void)w;return 0;}
''' + code + '''
int main(void){struct watchdog_device w={0,31};mode=0;mtk_wdt_init(&w);assert(!calls&&!w.status);
mode=1;mtk_wdt_init(&w);assert(calls==1&&w.status==1);return 0;}
'''
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder); (p/'probe.c').write_text(harness)
            subprocess.run([shutil.which('cc'), '-std=gnu11', '-Wall', '-Wextra', '-Werror', str(p/'probe.c'), '-o', str(p/'probe')], check=True)
            subprocess.run([str(p/'probe')], check=True)
