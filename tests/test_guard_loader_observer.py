import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import guard_loader_observer as g


def gpt(overlap=False):
    b=bytearray(17408);h=bytearray(512);h[:8]=b'EFI PART';struct.pack_into('<I',h,12,92)
    table=bytearray(16384)
    for n,a,z,name in [(17,30325760,30551039,'boot'),(18,30551040,30776319,'recovery'),(5,18432,51199,'boot_x'),(6,51200,86015,'recovery_x'),(7,30548983 if overlap else 90000,30549944 if overlap else 91000,'other')]:
        off=(n-1)*128;table[off]=1;struct.pack_into('<QQ',table,off+32,a,z);text=name.encode('utf-16le');table[off+56:off+56+len(text)]=text
    struct.pack_into('<QIII',h,72,2,128,128,zlib.crc32(table));struct.pack_into('<I',h,16,zlib.crc32(h[:92]));b[512:1024]=h;b[1024:]=table;return bytes(b)


class Geometry(unittest.TestCase):
    def test_reviewed_span(self):self.assertTrue(g.gpt_range(gpt()))
    def test_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError,'overlaps'):g.gpt_range(gpt(True))
    def test_corrupted_crc_rejected(self):
        b=bytearray(gpt());b[-1]^=1
        with self.assertRaisesRegex(ValueError,'CRC'):g.gpt_range(b)


class Fake:
    def __init__(self,data,fail=False):self.data=data;self.calls=[];self.fail=fail
    def read(self,node,size):return self.data
    def push(self,data,destination):self.calls.append(['push',destination])
    def run(self,args):
        self.calls.append(args)
        if args==['exec-out','readlink','-f','/tmp']:return b'/tmp\n'
        if args==['exec-out','cat','/proc/mounts']:return b'tmpfs /tmp tmpfs rw 0 0\n'
        if args[:2]==['exec-out','dd'] and self.fail:raise ValueError('injected uncertain transport failure')
        if args[0]=='shell':return b'RAM_CLEAN\n'
        return b''


class WriteGuard(unittest.TestCase):
    def run_case(self,preflight,fail=False):
        data=b'X'*g.SIZE;adb=Fake(data,fail)
        with tempfile.TemporaryDirectory() as f,patch.object(g,'preflight',side_effect=preflight),patch.object(g,'sha',return_value=g.CANDIDATE):
            path=Path(f)/'receipt.json'
            try:r=g.write_once(adb,data,{},g.ORIGINAL,g.ORIGINAL_BOOT,path)
            except ValueError:r=json.loads(path.read_text())
            return adb.calls,r
    def test_second_preflight_failure_stops_before_write(self):
        calls,r=self.run_case([{},ValueError('current bytes changed')])
        self.assertFalse(any(c[:2]==['exec-out','dd'] for c in calls));self.assertFalse(r['write_started'])
    def test_exact_single_extent_and_readback_gate(self):
        calls,r=self.run_case([{}, {}, {}])
        copies=[c for c in calls if c[:2]==['exec-out','dd']]
        self.assertEqual(len(copies),1)
        self.assertEqual(copies[0][3:],['of='+g.TARGET,'bs=512','seek=223223','count=962','conv=notrunc'])
        self.assertTrue(r['verified']);self.assertTrue(r['ram_cleanup_verified'])
        self.assertFalse(any('reboot' in c for c in calls))
    def test_uncertain_write_never_retried_or_claimed_verified(self):
        calls,r=self.run_case([{},{}],True)
        self.assertEqual(sum(c[:2]==['exec-out','dd'] for c in calls),1)
        self.assertTrue(r['write_started']);self.assertFalse(r['verified'])
