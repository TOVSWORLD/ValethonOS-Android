import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_native_jump_bundle import ranges_ok
class Tests(unittest.TestCase):
 def test_accept_real_layout(self):
  ranges_ok([(0x40080000,0x4101b000),(0x42000000,0x42019000),(0x69244000,0x69318000)],[(0x40000000,0x43000000),(0x43030000,0x98400000)],[(0x44410000,0x444f0000)])
 def test_protect_pstore_and_every_reserved_byte(self):
  for r in [(0x44410000,0x444f0000),(0x43000000,0x43030000)]:
   with self.assertRaises(ValueError):ranges_ok([(r[0],r[0]+4096)],[(0x40000000,0x98400000)],[r])
 def test_reject_dynamic_allocation_hole(self):
  with self.assertRaises(ValueError):ranges_ok([(0x98400000,0x98401000)],[(0x43030000,0x98400000),(0x98600000,0x99600000)],[])
 def test_no_cross_gap_or_segment_overlap(self):
  for seg in [[(0x42fff000,0x43031000)],[(0x42000000,0x42002000),(0x42001000,0x42003000)]]:
   with self.assertRaises(ValueError):ranges_ok(seg,[(0x40000000,0x43000000),(0x43030000,0x98400000)],[])
 def test_boundaries_and_alignment(self):
  ranges_ok([(4096,8192)],[(4096,8192)],[(8192,12288)])
  for seg in [[(4097,8192)],[(4096,8193)],[(8192,4096)],[(4096,4096)]]:
   with self.assertRaises(ValueError):ranges_ok(seg,[(0,16384)],[])
