import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from apply_goodix_board_port import apply
from select_kernel_build_scope import choose
ROOT=Path(__file__).resolve().parents[1]


class GoodixBoardPort(unittest.TestCase):
    def test_exact_source_alias_only_and_replay_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'drivers/input/touchscreen/goodix.c';p.parent.mkdir(parents=True)
            original=(ROOT/'evidence/kernel-audit/ack/drivers/input/touchscreen/goodix.c').read_bytes();p.write_bytes(original)
            apply(root);new=p.read_bytes()
            self.assertEqual(new.replace(b'\t{ .compatible = "goodix,gt9xx" },\n',b''),original)
            with self.assertRaises(ValueError):apply(root)

    def test_touch_scope_preserves_display_and_cannot_request_generic_vm(self):
        self.assertEqual(choose('pull_request',['scripts/build_touch_provider.sh','scripts/build_display_provider.sh'])['mode'],'touch-provider')
        self.assertEqual(choose('workflow_dispatch',mode='touch-provider')['mode'],'touch-provider')
        with self.assertRaises(ValueError):choose('workflow_dispatch',mode='touch-provider',emulated_boot=True)
