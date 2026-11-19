import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from graphics_direct_device import ExactReadAdb
from restore_diagnostic_boot import BOOT, BOOT_BYTES, PartitionReadError


class ExactGraphicsRead(unittest.TestCase):
    def device(self,body,sectors=b'32768\n'):
        d=object.__new__(ExactReadAdb);calls=[]
        def run(args,data=None):
            calls.append(args)
            return sectors if args[1]=='cat' else body
        d.run=run
        return d,calls

    def test_full_geometry_and_bounded_binary_are_both_required(self):
        body=b'X'*BOOT_BYTES;d,calls=self.device(body)
        self.assertEqual(d.read(BOOT,BOOT_BYTES),body)
        self.assertEqual(calls[1],['exec-out','head','-c',str(BOOT_BYTES),BOOT])
        for malformed in [body[:-1],body+b'footer']:
            d,_=self.device(malformed)
            with self.assertRaises(PartitionReadError):d.read(BOOT,BOOT_BYTES)
        for sectors in [b'32769\n',b'32768\nextra']:
            d,calls=self.device(body,sectors)
            with self.assertRaises(ValueError):d.read(BOOT,BOOT_BYTES)
            self.assertEqual(len(calls),1)
        d,calls=self.device(body)
        with self.assertRaises(ValueError):d.read('/dev/block/mmcblk0p1',BOOT_BYTES)
        self.assertEqual(calls,[])

    def test_only_exact_private_ram_staging_file_is_admitted(self):
        node='/tmp/valethonos-rollback-'+'a'*32+'/boot.img'
        d=object.__new__(ExactReadAdb);calls=[]
        d.run=lambda args: calls.append(args) or b'X'*BOOT_BYTES
        self.assertEqual(len(d.read(node,BOOT_BYTES)),BOOT_BYTES)
        self.assertEqual(calls,[['exec-out','cat',node]])
        d.run=lambda args: b'X'*(BOOT_BYTES-1)
        with self.assertRaises(PartitionReadError):d.read(node,BOOT_BYTES)
        for invalid in [node+'/extra',node.replace('boot.img','other.img'),'/tmp/boot.img']:
            with self.assertRaises(ValueError):d.read(invalid,BOOT_BYTES)
