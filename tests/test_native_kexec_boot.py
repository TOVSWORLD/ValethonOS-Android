import gzip
import hashlib
import json
import struct
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from pack_native_kexec_boot import assemble,split_kernel,PARTITION,CONFIG_SHA
from inspect_boot_image import inspect


def image(payload=b''):
    b=bytearray(4096+len(payload));b[4096:]=payload
    struct.pack_into('<QQQ',b,8,0x80000,0x20000,10);b[56:60]=b'ARMd';return bytes(b)


def dtb():
    structure=struct.pack('>I',1)+bytes(4)+struct.pack('>II',2,9)
    return struct.pack('>10I',0xd00dfeed,72,56,72,40,17,16,0,0,16)+bytes(16)+structure


def original():
    k=gzip.compress(image(),mtime=0)+dtb()+dtb();rd=gzip.compress(b'070701-original-ramdisk',mtime=0)
    header=bytearray(2048);header[:8]=b'ANDROID!'
    struct.pack_into('<10I',header,8,len(k),0x40080000,len(rd),0x69244e00,0,0,0x48000000,2048,0,123)
    args=b'original boot arguments\0';header[64:64+len(args)]=args
    raw=bytes(header)
    for p in [k,rd]:raw+=p+bytes((-len(p))%2048)
    raw+=bytes(PARTITION-len(raw));raw=bytearray(raw);raw[-512:-500]=b'opaque-tail!'
    return bytes(raw)


def linked(b):return {'arm64_syscall_104_is_kexec_load':True,'handoff_gate_wired':True,'orderly_reboot_namespace_linked':True,'artifacts':{'arch/arm64/boot/Image':{'sha256':hashlib.sha256(b).hexdigest()},'.config':{'sha256':CONFIG_SHA}}}


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.old=original();cls.oldsha=hashlib.sha256(cls.old).hexdigest()
    def pack(self,b,report=None):return assemble(self.old,b,report or linked(b),self.oldsha)
    def test_round_trip_keeps_userspace_dt_and_header(self):
        new=image(bytes(range(256))*24);candidate,r=self.pack(new)
        parsed=inspect(candidate);k,rd,_=parsed['components'];oldparts=inspect(self.old)['components'];oldrd=oldparts[1]
        self.assertEqual(split_kernel(candidate[k['offset']:k['offset']+k['bytes']])[0],new)
        self.assertEqual(candidate[rd['offset']:rd['offset']+rd['bytes']],self.old[oldrd['offset']:oldrd['offset']+oldrd['bytes']])
        self.assertEqual(candidate[r['new_declared_end']:],self.old[r['new_declared_end']:])
        self.assertTrue(r['original_header_changes_only_kernel_size_and_id']);self.assertEqual(len(r['appended_dtbs']),2)
        self.assertFalse(r['boot_tested']);self.assertFalse(r['experimental_jump_executed'])
    def test_wrong_original_refused(self):
        with self.assertRaises(ValueError):assemble(self.old,image(),linked(image()),'0'*64)
    def test_unwired_gate_refused(self):
        b=image();report=linked(b);report['handoff_gate_wired']=False
        with self.assertRaises(ValueError):self.pack(b,report)
    def test_wrong_image_hash_refused(self):
        b=image();report=linked(b);report['artifacts']['arch/arm64/boot/Image']['sha256']='0'*64
        with self.assertRaises(ValueError):self.pack(b,report)
    def test_changed_config_refused(self):
        b=image();report=linked(b);report['artifacts']['.config']['sha256']='0'*64
        with self.assertRaises(ValueError):self.pack(b,report)
    def test_loader_extent_overflow_refused(self):
        b=bytearray(image());struct.pack_into('<Q',b,16,0x3000000);b=bytes(b)
        with self.assertRaises(ValueError):self.pack(b)
    def test_protocol_change_refused(self):
        b=bytearray(image());struct.pack_into('<Q',b,8,0x1000);b=bytes(b)
        with self.assertRaises(ValueError):self.pack(b)
    def test_truncated_suffix_refused(self):
        with self.assertRaises(ValueError):split_kernel(gzip.compress(image(),mtime=0)+dtb()[:-1])


if __name__=='__main__':unittest.main()
