import gzip,hashlib,json,struct,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_android_early_capture import augment,kernel_check
from build_diagnostic_initramfs import archive
from test_android_direct_boot import entries

def wrapper():
 b=bytearray(128);b[:7]=b'\x7fELF\x02\x01\x01';struct.pack_into('<HH',b,16,2,183);struct.pack_into('<Q',b,24,0x400078);struct.pack_into('<Q',b,32,64);struct.pack_into('<HH',b,54,56,1);struct.pack_into('<IIQQQQQQ',b,64,1,5,0,0x400000,0,128,128,4096);return bytes(b)
class EarlyCapture(unittest.TestCase):
 def test_original_init_and_fstab_bytes_preserved(self):
  original=archive(entries());result,report=augment(gzip.compress(original),wrapper())
  at=original.index(b'TRAILER!!!')-110
  # Find actual trailer header rather than stripping potentially meaningful NULs.
  while original[at:at+6]!=b'070701':at-=1
  self.assertEqual(result[:at],original[:at]);self.assertIn(b'valethon-preinit\0',result)
  self.assertTrue(report['first_stage_init_arm32_static'])
 def test_existing_wrapper_rejected(self):
  e=entries()+[('valethon-preinit',0o100500,wrapper(),(0,0))]
  with self.assertRaisesRegex(ValueError,'Existing wrapper'):augment(gzip.compress(archive(e)),wrapper())
 def test_dynamic_wrapper_rejected(self):
  b=bytearray(wrapper());struct.pack_into('<I',b,64,3)
  with self.assertRaisesRegex(ValueError,'Dynamic'):augment(gzip.compress(archive(entries())),b)
 def test_unrelated_kernel_delta_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);config=b'CONFIG_U_SERIAL_CONSOLE=y\nCONFIG_USB_G_SERIAL=y\nCONFIG_PSTORE=y\nCONFIG_PSTORE_RAM=y\nCONFIG_PSTORE_CONSOLE=y\nCONFIG_SECURITY_SELINUX=n\n';(p/'.config').write_bytes(config)
   (p/'result.json').write_text(json.dumps({'artifacts':{'.config':hashlib.sha256(config).hexdigest()},'delta':{}}))
   with self.assertRaisesRegex(ValueError,'Unreviewed'):kernel_check(p,b'CONFIG_SECURITY_SELINUX=y\n')
if __name__=='__main__':unittest.main()
