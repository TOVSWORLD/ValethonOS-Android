import gzip,stat,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_diagnostic_initramfs import archive
from prepare_android_direct_boot import ramdisk,ROOT,MAX_CPIO
def elf(interpreter=False):
    b=bytearray(84);b[:7]=b'\x7fELF\x01\x01\x01';struct.pack_into('<HH',b,16,2,40);struct.pack_into('<I',b,28,52);struct.pack_into('<HH',b,42,32,1);struct.pack_into('<I',b,52,3 if interpreter else 1)
    return bytes(b)
def entries():
    return [('dev',stat.S_IFDIR|0o755,b'',(0,0)),('init',stat.S_IFREG|0o750,elf(),(0,0)),('fstab.douglas',stat.S_IFREG|0o640,(ROOT/'projects/firetabs-android/android-integration/device/init/fstab.douglas').read_bytes(),(0,0))]
class AndroidRamdisk(unittest.TestCase):
 def test_android_identical_directory_entries_are_valid(self):
    e=entries();e.append(e[0]);raw,report=ramdisk(gzip.compress(archive(e)))
    self.assertEqual(report['identical_directory_duplicates'],['dev']);self.assertTrue(report['first_stage_init_arm32_static'])
 def test_duplicate_executable_rejected(self):
    e=entries();e.append(e[1])
    with self.assertRaisesRegex(ValueError,'duplicate'):ramdisk(gzip.compress(archive(e)))
 def test_unsafe_name_rejected(self):
    e=entries();e.append(('../outside',stat.S_IFREG|0o600,b'x',(0,0)))
    with self.assertRaisesRegex(ValueError,'Unsafe'):ramdisk(gzip.compress(archive(e)))
 def test_first_stage_cannot_require_host_or_system_linker(self):
    e=entries();e[1]=('init',stat.S_IFREG|0o750,elf(True),(0,0))
    with self.assertRaisesRegex(ValueError,'dynamic interpreter'):ramdisk(gzip.compress(archive(e)))
 def test_modified_fstab_cannot_enter_package(self):
    e=entries();e[2]=('fstab.douglas',stat.S_IFREG|0o640,b'/dev/userdata /data ext4 rw format',(0,0))
    with self.assertRaisesRegex(ValueError,'system-only'):ramdisk(gzip.compress(archive(e)))
 def test_concatenated_and_oversized_archives_rejected(self):
    good=gzip.compress(archive(entries()))
    for bad in [good+good,gzip.compress(b'x'*(MAX_CPIO+1))]:
      with self.subTest(size=len(bad)),self.assertRaisesRegex(ValueError,'bounded complete'):ramdisk(bad)
