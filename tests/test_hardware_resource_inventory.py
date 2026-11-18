import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_hardware_resource_inventory import export
class HardwareExport(unittest.TestCase):
 def test_private_channels_and_properties_are_not_exported(self):
  t={'/chosen':{'reg':'1','bootargs':'aa'},'/idme/serial':{'reg':'2'},'/firmware/android/x':{'compatible':'1'},'/soc/uart':{'reg':'11 0 20 0','serial-number':'de ad','mac-address':'be ef','value':'12','status':'6f 6b 61 79 0'}}
  r=export(t);self.assertEqual(set(r),{'/soc/uart'});self.assertEqual(set(r['/soc/uart']['properties_hex_bytes']),{'reg','status'})
 def test_direct_provider_links_resolve_without_reinterpreting_clock_arguments(self):
  t={'/regulator':{'phandle':'0 0 0 1'},'/pins':{'phandle':'0 0 0 2'},'/device':{'vdd-supply':'0 0 0 1','pinctrl-0':'0 0 0 2','clocks':'0 0 0 1 0 0 0 9'}}
  r=export(t)['/device'];self.assertEqual(r['resolved_direct_providers'],{'pinctrl-0':['/pins'],'vdd-supply':['/regulator']});self.assertEqual(r['properties_hex_bytes']['clocks'],t['/device']['clocks'])
 def test_unknown_pinctrl_is_explicit(self):
  self.assertEqual(export({'/d':{'pinctrl-0':'0 0 0 7'}})['/d']['resolved_direct_providers'],{'pinctrl-0':['UNRESOLVED']})
if __name__=='__main__':unittest.main()
