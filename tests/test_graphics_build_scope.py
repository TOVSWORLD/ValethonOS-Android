import json, os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from select_kernel_build_scope import choose


class GraphicsBuild(unittest.TestCase):
    def test_graphics_scope_keeps_one_explicit_non_device_build(self):
        self.assertEqual(choose('pull_request', ['scripts/build_graphics_provider.sh', 'scripts/build_display_provider.sh'])['mode'], 'graphics-provider')
        self.assertEqual(choose('workflow_dispatch', mode='graphics-provider')['mode'], 'graphics-provider')
        with self.assertRaises(ValueError):
            choose('workflow_dispatch', mode='graphics-provider', emulated_boot=True)

    def test_actual_workflow_retains_gpu_display_touch_and_watchdog(self):
        text = (ROOT/'.github/workflows/kernel-baseline.yml').read_text()
        block = text.split("          python3 - <<'PY'\n", 1)[1].split('\n          PY', 1)[0]
        code = '\n'.join(l[10:] for l in block.splitlines()).replace('${{ steps.scope.outputs.mode }}', 'graphics-provider')
        names = ['arch/arm64/boot/Image', 'arch/arm64/boot/Image.gz', '.config', 'System.map',
                 'drivers/gpu/drm/panel/panel-amazon-douglas-tpv.o', 'drivers/gpu/drm/mediatek/mtk_drm_drv.o',
                 'drivers/gpu/drm/mediatek/mtk_disp_gamma.o', 'drivers/soc/mediatek/mtk-mutex.o',
                 'drivers/video/backlight/lp855x_bl.o', 'drivers/video/backlight/pwm_bl.o',
                 'drivers/input/touchscreen/goodix.o', 'drivers/watchdog/mtk_wdt.o', 'drivers/gpu/drm/panfrost/panfrost_drv.o', 'drivers/gpu/drm/panfrost/panfrost_device.o', 'drivers/gpu/drm/panfrost/panfrost_gpu.o']
        with tempfile.TemporaryDirectory() as tmp:
            old = Path.cwd()
            try:
                os.chdir(tmp)
                root = Path('work/ack-baseline')
                for n in names:
                    p = root/'output'/n; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(n.encode())
                for n in ['display-image-size-report.json', 'display-build-result.json']:
                    (root/n).write_text('{}')
                with patch.dict(os.environ, {'GITHUB_SHA': 'source', 'ENTRY_CHECKPOINT_PROFILE': 'none', 'GITHUB_RUN_ID': '1', 'GITHUB_RUN_ATTEMPT': '1'}), patch('subprocess.check_output', return_value='kernel'):
                    exec(compile(code, '<actual workflow retention>', 'exec'), {})
                manifest = json.loads(Path('out/diagnostic-kernel-artifact/manifest.json').read_text())
                self.assertEqual(manifest['build_mode'], 'graphics-provider')
                self.assertTrue({'panfrost_drv.o', 'panfrost_gpu.o', 'panfrost_device.o', 'goodix.o', 'mtk_wdt.o', 'mtk_drm_drv.o'}.issubset(manifest['files']))
            finally:
                os.chdir(old)
