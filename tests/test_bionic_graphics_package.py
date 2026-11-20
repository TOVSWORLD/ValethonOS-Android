import importlib.util,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bionic_package',ROOT/'scripts/package_bionic_graphics.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def fixture(soname='libEGL_valethon.so',needed='libc.so',api=34,machine=40,runpath=None):
 strings=b'\0'+soname.encode()+b'\0'+needed.encode()+b'\0';needed_offset=len(soname)+2
 dynamic=struct.pack('<iI',14,1)+struct.pack('<iI',1,needed_offset)
 if runpath:
  at=len(strings);strings+=runpath.encode()+b'\0';dynamic+=struct.pack('<iI',29,at)
 dynamic+=struct.pack('<iI',0,0)
 note=struct.pack('<III',8,4,1)+b'Android\0'+struct.pack('<I',api)
 offset=52;parts=[];sections=[(0,0,0,0,0,0,0,0,0,0)]
 for kind,raw,link,entsize in [(3,strings,0,0),(6,dynamic,1,8),(7,note,0,0)]:
  sections.append((0,kind,0,0,offset,len(raw),link,0,4,entsize));parts.append(raw);offset+=len(raw)
 header=b'\x7fELF\x01\x01\x01'+b'\0'*9+struct.pack('<HHIIIIIHHHHHH',3,machine,1,0,0,offset,0x5000200,52,0,0,40,len(sections),0)
 return header+b''.join(parts)+b''.join(struct.pack('<IIIIIIIIII',*s) for s in sections)
class BionicELFAdmission(unittest.TestCase):
 def test_android_arm32_metadata_parsed(self):
  r=module.elf_info(fixture());self.assertEqual(r['android_api'],34);self.assertEqual(r['needed'],['libc.so']);self.assertEqual(r['soname'],'libEGL_valethon.so')
 def test_glibc_dependency_cannot_be_mislabelled_android(self):
  with self.assertRaises(ValueError):module.elf_info(fixture(needed='libc.so.6'))
 def test_host_search_path_rejected(self):
  with self.assertRaises(ValueError):module.elf_info(fixture(runpath='/tmp/build/android_stub'))
 def test_wrong_architecture_and_future_api_rejected(self):
  for raw in [fixture(machine=183),fixture(api=99),fixture(soname='libEGL_valethon.so.1')]:
   with self.assertRaises(ValueError):module.elf_info(raw)
 def test_truncated_elf_not_accepted(self):
  with self.assertRaises(ValueError):module.elf_info(fixture()[:-20])
