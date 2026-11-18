import struct,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_ack_ramfix_bundle import exclusions,ram_ranges
from validate_ack_ramfix_vm import geometry
import run_ack_native_trial as trial

class LiveRAM(unittest.TestCase):
 def test_actual_missing_carveout_and_atf_gap(self):
  ram=ram_ranges('40000000-42ffffff : System RAM\n43030000-983fffff : System RAM\n98600000-995fffff : System RAM\n')
  gaps=exclusions([(0x40000000,0x80000000),(0x80000000,0x99600000)],ram)
  self.assertEqual(gaps,[(0x43000000,0x43030000),(0x98400000,0x98600000)])
  self.assertTrue(any(a<=0x985ff008<z for a,z in gaps))
 def test_interval_boundaries_partial_banks_and_empty_ram(self):
  self.assertEqual(exclusions([(0,10)],[(2,4),(4,6),(8,20)]),[(0,2),(6,8)])
  self.assertEqual(exclusions([(2,8)],[(0,10)]),[])
  self.assertEqual(exclusions([(0,10)],[]),[(0,10)])
 def test_live_map_refuses_empty_unaligned_and_overlapping(self):
  for value in ['', '40000001-40000fff : System RAM\n','40000000-40000ffe : System RAM\n','40000000-40001fff : System RAM\n40001000-40002fff : System RAM\n']:
   with self.assertRaises(ValueError):ram_ranges(value)
 def test_consumed_cinit_scope_cannot_authorize_ramfix(self):
  a=SimpleNamespace(policy=Path('unused'),ramfix=True,cinit=False,combined=False)
  with patch.object(trial,'read',return_value={'scope':'ack-linux-cinit-two-stage-3','target_kind':'ack-linux-cinit-v3'}):
   with self.assertRaisesRegex(ValueError,'policy required'):trial.validate(a)
 def test_new_usb_trial_cannot_reuse_ramfix_parent_scope(self):
  a=SimpleNamespace(policy=Path('unused'),ramfix=True,cinit=False,combined=False,usb_end_to_end=True)
  with patch.object(trial,'read',return_value={'scope':'ack-linux-ramfix-two-stage-4','target_kind':'ack-linux-ramfix-v4'}):
   with self.assertRaisesRegex(ValueError,'policy required'):trial.validate(a)
 def test_usb_mode_requires_ram_fixed_kernel(self):
  a=SimpleNamespace(policy=Path('unused'),ramfix=False,cinit=True,combined=False,usb_end_to_end=True)
  with patch.object(trial,'read',return_value={}):
   with self.assertRaisesRegex(ValueError,'requires the RAM-fixed'):trial.validate(a)
 def test_vm_geometry_transplants_banks_and_nomap(self):
  strings=b'reg\0';begin=lambda name:struct.pack('>I',1)+(name+b'\0')+bytes((-(len(name)+1))%4)
  st=begin(b'')+begin(b'memory@40000000')+struct.pack('>IIIQQ',3,16,0,0x40000000,0x60000000)+struct.pack('>III',2,2,9)
  data=struct.pack('>10I',0xd00dfeed,56+len(st)+len(strings),56,56+len(st),40,17,16,0,len(strings),len(st))+bytes(16)+st+strings
  out=geometry(data,{'memory_banks':[(0x40000000,0x80000000),(0x80000000,0x99600000)],'nomap_ranges':[(0x98400000,0x98600000)]})
  h=struct.unpack_from('>10I',out)
  self.assertEqual(h[1],len(out));self.assertIn(b'reserved-memory\0',out)
  self.assertIn(struct.pack('>QQ',0x98400000,0x200000),out)
  self.assertIn(struct.pack('>QQQQ',0x40000000,0x40000000,0x80000000,0x19600000),out)
  self.assertIn(b'no-map\0',out[h[3]:])
if __name__=='__main__':unittest.main()
