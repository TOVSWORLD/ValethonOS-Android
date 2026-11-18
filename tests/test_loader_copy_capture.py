import json,struct,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from loader_screen_record import decode_words,decode_pixels,CHECK
from decode_loader_screen_photo import project
from prepare_pre_shutdown_control import profile_guard,SCOPE as HISTORICAL_SCOPE
from prepare_loader_copy_control import SCOPE

class Capture(unittest.TestCase):
 def record(self,phase=4,token=0x1234,value=0xffffff96,status=0x980a00b3):
  h=0x57000000|(phase<<16)|token
  return [h,value,status,h^value^status^CHECK]
 def test_signed_error_and_mask_are_attributed_without_kernel_claim(self):
  r=decode_words(self.record(),0x1234,4)
  self.assertEqual(r['signed_value'],-106);self.assertTrue(r['irq_masked']);self.assertFalse(r['kernel_entry_proved'])
 def test_wrong_nonce_checksum_and_phase_rejected(self):
  for word,token,phase in [(self.record(),0x4321,4),(self.record(),0x1234,5),([*self.record()[:3],0],0x1234,4),(self.record(phase=9),0x1234,None)]:
   with self.assertRaises(ValueError):decode_words(word,token,phase)
 def test_samples_and_low_contrast_fail_closed(self):
  w=self.record()
  def sample(x,y):
   row=(y-120)//8;bit=x//8
   return 215 if w[row]&(1<<(31-bit)) else 45
  self.assertEqual(decode_pixels(sample,0x1234,4)['signed_value'],-106)
  with self.assertRaises(ValueError):decode_pixels(lambda x,y:127,0x1234,4)
 def test_projective_corner_mapping_and_degenerate_input(self):
  corners=[20,30,460,50,470,780,10,760];p=project(corners)
  for src,target in zip([(0,0),(800,0),(800,1280),(0,1280)],zip(corners[::2],corners[1::2])):
   for a,b in zip(p(*src),target):self.assertAlmostEqual(a,b,places=6)
  with self.assertRaises(ValueError):project([0]*8)
 def test_new_scope_and_every_hash_without_mutating_old_profile(self):
  template=(Path(__file__).resolve().parents[1]/'scripts/guard_known_boot_capture.py').read_text()
  m={'snapshot_stage':'pre_shutdown','checkpoint_site':'0x4bd3e3e8','candidate_sha256':'1'*64,'observer_sha256':'2'*64,'prefix_sha256':'3'*64,'seed_sha256':'4'*64}
  new=profile_guard(template,m,SCOPE);old=profile_guard(template,m)
  self.assertIn(repr(SCOPE),new);self.assertNotIn(repr(HISTORICAL_SCOPE),new);self.assertIn(repr(HISTORICAL_SCOPE),old)
  for expected in ['1'*64,'2'*64,'3'*64,'4'*64]:self.assertIn(expected,new)

if __name__=='__main__':unittest.main()
