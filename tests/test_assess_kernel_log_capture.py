"""Synthetic wire fixtures are integrity tests, never physical qualification."""
import hashlib
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from assess_kernel_log_capture import assess
from kernel_log_protocol import MAGIC
NONCE=bytes(range(32))
BOOT=b'6,0,1,-;Linux version 3.18.19-test (private fixture)\n'


def fixture(records):
    raw=MAGIC+NONCE+b''.join(struct.pack('>II',i,len(p))+p for i,p in enumerate(records))+struct.pack('>II',len(records),0)
    return raw,dict(complete=True,failure=None,cleanup=[],records=len(records),payload_bytes=sum(map(len,records)),wire_sha256=hashlib.sha256(raw).hexdigest())


class Assessment(unittest.TestCase):
    def test_matching_fixture_never_qualifies_device_or_admits_test(self):
        raw,receipt=fixture([BOOT]);result=assess(raw,NONCE,receipt,'3.18.19-test')
        self.assertTrue(result['matching_kernel_boot_record'])
        for key in ['device_qualified','physical_origin_verified','test_admission']:
            self.assertFalse(result[key])
        self.assertNotIn('private fixture',str(result))

    def test_host_loader_userspace_and_empty_are_not_kernel(self):
        for records in [[],[b'VALETHON HOST CONTROL v1\n'],[b'LK handoff'],[b'Linux version 3.18.19-test'],[BOOT.replace(b'6,',b'14,',1)]]:
            raw,receipt=fixture(records)
            with self.subTest(records=records),self.assertRaises(ValueError):assess(raw,NONCE,receipt,'3.18.19-test')

    def test_nonce_release_truncation_and_trailing_bytes_rejected(self):
        raw,receipt=fixture([BOOT])
        for data,nonce,release in [(raw,bytes([1])*32,'3.18.19-test'),(raw,NONCE,'other'),(raw[:-1],NONCE,'3.18.19-test'),(raw+b'x',NONCE,'3.18.19-test')]:
            with self.subTest(length=len(data)),self.assertRaises(ValueError):assess(data,nonce,receipt,release)

    def test_receipt_failures_counts_and_hash_rejected(self):
        raw,receipt=fixture([BOOT])
        for change in [dict(complete=False),dict(failure='timeout'),dict(cleanup=['failure']),dict(records=2),dict(payload_bytes=0),dict(wire_sha256='0'*64)]:
            with self.subTest(change=change),self.assertRaises(ValueError):assess(raw,NONCE,{**receipt,**change},'3.18.19-test')

    def test_bad_sequence_rejected_even_with_matching_digest(self):
        raw,receipt=fixture([BOOT]);raw=raw[:40]+struct.pack('>I',1)+raw[44:];receipt['wire_sha256']=hashlib.sha256(raw).hexdigest()
        with self.assertRaises(ValueError):assess(raw,NONCE,receipt,'3.18.19-test')
