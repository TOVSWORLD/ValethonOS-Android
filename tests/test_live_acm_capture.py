import json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from capture_live_acm_probe import identity
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
  self.usb=self.root/'devices/1-2.3';iface=self.usb/'1-2.3:1.2';iface.mkdir(parents=True)
  (self.usb/'idVendor').write_text('18d1\n');(self.usb/'idProduct').write_text('0001\n');(iface/'bInterfaceNumber').write_text('02\n')
  driver=self.root/'drivers/cdc_acm';driver.mkdir(parents=True);(iface/'driver').symlink_to(driver,target_is_directory=True)
  tty=self.root/'class/tty/ttyACM0';tty.mkdir(parents=True);(tty/'device').symlink_to(iface,target_is_directory=True);(tty/'dev').write_text('166:0\n')
  self.profile={'physical_path':'1-2.3','vendor':'18d1','product':'0001'};self.iface=iface
 def test_exact_physical_port_and_descriptor(self):self.assertEqual(identity('ttyACM0',self.profile,self.root)['rdev'],os.makedev(166,0))
 def test_other_device_not_selected(self):
  for k,v in [('physical_path','1-9'),('vendor','0000'),('product','ffff')]:
   p=dict(self.profile);p[k]=v;self.assertIsNone(identity('ttyACM0',p,self.root))
 def test_unbound_driver_waits(self):
  (self.iface/'driver').unlink();self.assertIsNone(identity('ttyACM0',self.profile,self.root))
 def test_wrong_driver_refused(self):
  d=self.root/'drivers/foreign';d.mkdir();(self.iface/'driver').unlink();(self.iface/'driver').symlink_to(d)
  with self.assertRaises(ValueError):identity('ttyACM0',self.profile,self.root)
 def test_non_acm_name_not_selected(self):self.assertIsNone(identity('ttyUSB0',self.profile,self.root))
 def test_current_node_number_used(self):
  (self.root/'class/tty/ttyACM0/dev').write_text('166:7\n');self.assertEqual(identity('ttyACM0',self.profile,self.root)['rdev'],os.makedev(166,7))
