import ctypes
import shutil
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Segment(ctypes.Structure):
    _fields_ = [('buf', ctypes.c_void_p), ('bufsz', ctypes.c_ulong),
                ('mem', ctypes.c_ulong), ('memsz', ctypes.c_ulong)]

class StageLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc = shutil.which('cc')
        if not cc: raise unittest.SkipTest('Native C compiler unavailable')
        cls.temp = tempfile.TemporaryDirectory()
        directory = Path(cls.temp.name)
        source = directory / 'check.c'; library = directory / 'check.so'
        source.write_text('''#include <stdint.h>
#include <stddef.h>
struct kexec_segment {void *buf; unsigned long bufsz, mem, memsz;};
#include "stage_limits.h"
#include "stage_crc.h"
int check(uint64_t entry, unsigned long n, const struct kexec_segment *s) {return kxstage_layout_ok(entry,n,s);}
uint32_t checksum(const unsigned char *p, size_t n) {return kxstage_crc32(p,n);}
''')
        flag = '-dynamiclib' if sys.platform == 'darwin' else '-shared'
        subprocess.run([cc, flag, '-fPIC', '-Wall', '-Wextra', '-Werror', '-I',
                        str(ROOT / 'projects/firetabs-android/kexec-stage'), str(source), '-o', str(library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.check.argtypes = [ctypes.c_uint64, ctypes.c_ulong, ctypes.POINTER(Segment)]
        cls.lib.check.restype = ctypes.c_int
        cls.lib.checksum.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        cls.lib.checksum.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def segments(self):
        return (Segment * 3)(Segment(1, 5123, 0x40080000, 8192),
                             Segment(1, 1149, 0x48000000, 4096),
                             Segment(1, 3999, 0x43480000, 4096))

    def test_valid_three_segment_layout(self):
        self.assertEqual(self.lib.check(0x40080000, 3, self.segments()), 1)

    def test_invalid_count(self):
        for n in [0,4,2**32]: self.assertEqual(self.lib.check(0x40080000,n,self.segments()),0)

    def test_destination_overflow(self):
        s=self.segments();s[0].mem=2**64-4096;s[0].bufsz=4096
        self.assertEqual(self.lib.check(s[0].mem,3,s),0)

    def test_overlapping_segments(self):
        s=self.segments();s[1].mem=s[0].mem+4096
        self.assertEqual(self.lib.check(s[0].mem,3,s),0)

    def test_alignment_and_entry_bounds(self):
        s=self.segments()
        for entry in [s[0].mem-4,s[0].mem+5124,s[0].mem+1]:
            self.assertEqual(self.lib.check(entry,3,s),0)
        s[1].mem+=1;self.assertEqual(self.lib.check(s[0].mem,3,s),0)

    def test_oversized_source_null_source_and_zero_kernel(self):
        for size, pointer in [(8193,1),(5123,None),(0,1)]:
            s=self.segments();s[0].bufsz=size;s[0].buf=pointer
            self.assertEqual(self.lib.check(s[0].mem,3,s),0)

    def test_total_and_per_segment_limits(self):
        s=self.segments();s[0].memsz=32*1024*1024
        self.assertEqual(self.lib.check(s[0].mem,3,s),0)
        s[0].memsz+=4096;self.assertEqual(self.lib.check(s[0].mem,1,s),0)
        s=self.segments();s[0].memsz=0;self.assertEqual(self.lib.check(s[0].mem,1,s),0)

    def test_client_crc_matches_independent_zlib_including_zero_padding(self):
        for count in [0,1,5123,8192,16384]:
            data=bytes((i*17+3)&255 for i in range(count))
            self.assertEqual(self.lib.checksum(data,len(data)),zlib.crc32(data))
        for i,(bufsz,memsz) in enumerate([(5123,8192),(1149,4096),(3999,4096)]):
            data=bytes((j*17+i*71+3)&255 for j in range(bufsz))+bytes(memsz-bufsz)
            self.assertEqual(self.lib.checksum(data,len(data)),zlib.crc32(data))

if __name__=='__main__': unittest.main()
