from pathlib import Path
import json
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from observe_selected_usb import snapshot,observe

class SelectedUSB(unittest.TestCase):
    def fixture(self,root):
        d=root/'bus/usb/devices/1-2';d.mkdir(parents=True)
        for name,value in [('idVendor','abcd'),('idProduct','1234'),('bDeviceClass','00'),('speed','480'),('serial','must-not-read')]:
            (d/name).write_text(value)
        i=d/'1-2:1.0';i.mkdir()
        for name,value in [('bInterfaceNumber','00'),('bInterfaceClass','ff'),('bInterfaceSubClass','42'),('bInterfaceProtocol','01')]:
            (i/name).write_text(value)
        driver=root/'drivers/usbfs';driver.mkdir(parents=True);(i/'driver').symlink_to(driver)
        (i/'tty/ttyACM9').mkdir(parents=True)
        other=root/'bus/usb/devices/1-3';other.mkdir();(other/'serial').write_text('other-private')
        return d
    def test_unexpected_identity_and_driver_are_recorded_without_serial(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.fixture(root);s=snapshot('1-2',root)
            self.assertEqual(s['vendor'],'abcd');self.assertEqual(s['interfaces'][0]['driver'],'usbfs')
            self.assertEqual(s['interfaces'][0]['tty_acm_nodes'],['ttyACM9'])
            self.assertNotIn('must-not-read',json.dumps(s));self.assertNotIn('other-private',json.dumps(s))
    def test_disconnect_is_a_change_and_output_is_private(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);d=self.fixture(root);now=[0]
            def sleep(n):
                now[0]+=n
                if d.exists():d.rename(d.with_name('gone'))
            out=root/'events.jsonl';r=observe('1-2',out,.4,root,clock=lambda:now[0],sleep=sleep)
            rows=[json.loads(x) for x in out.read_text().splitlines()]
            self.assertEqual([x['present'] for x in rows],[True,False]);self.assertEqual(r['events'],2)
            self.assertEqual(out.stat().st_mode & 0o777,0o600);self.assertFalse(r['port_opened'])
    def test_no_discovery_or_reused_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaises(ValueError):snapshot('../',root)
            out=root/'exists';out.write_text('retain')
            with self.assertRaises(FileExistsError):observe('1-2',out,1,root)
            self.assertEqual(out.read_text(),'retain')
