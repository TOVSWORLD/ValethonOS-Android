import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_kexec_stage import refusal_stub,validate_imports

class StageArtifactGate(unittest.TestCase):
 def test_only_exact_eopnotsupp_stub_accepted(self):
  refusal_stub(struct.pack('<II',0x12800bc0,0xd65f03c0))
  for code in [b'',struct.pack('<II',0x52800000,0xd65f03c0),struct.pack('<II',0xd61f0000,0xd65f03c0)]:
   with self.assertRaises(ValueError):refusal_stub(code)
 def test_memory_imports_do_not_admit_shutdown_or_physical_io(self):
  validate_imports({'__alloc_pages_nodemask','__free_pages','crc32_le','misc_register','printk'})
  for name in ['machine_shutdown','kernel_restart_prepare','cpu_down','__hyp_set_vectors','ioremap','vfs_write']:
   with self.assertRaises(ValueError):validate_imports({name})

if __name__=='__main__':unittest.main()
