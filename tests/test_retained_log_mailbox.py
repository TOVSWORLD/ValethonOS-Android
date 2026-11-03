import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import retained_log_mailbox as m


class RetainedMailbox(unittest.TestCase):
    def setUp(self):
        self.image=b'candidate-prefix\n'+bytes(m.PARTITION-17)
        self.nonce=bytes(range(32))
        self.image,self.sha=m.prepare(self.image,self.nonce)

    def test_actual_disk_roundtrip_two_commits_and_torn_latest_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'fixture.img';p.write_bytes(self.image)
            first=m.write_fixture(p,self.nonce,self.sha,b'kernel checkpoint one\n')
            second=m.write_fixture(p,self.nonce,self.sha,b'kernel checkpoint two\n')
            self.assertEqual((first['sequence'],second['sequence']),(1,2))
            image=bytearray(p.read_bytes());image[m.SLOT_BASE+m.SLOT+m.HEADER]^=1
            state=m.inspect(image,self.nonce,self.sha)
            self.assertEqual(state['latest']['payload'],b'kernel checkpoint one\n')
            self.assertEqual(state['invalid_slots'],[1])
            # Interrupted invalidation of the inactive slot must retain the active one.
            image=bytearray(p.read_bytes());image[m.SLOT_BASE:m.SLOT_BASE+m.HEADER]=bytes(m.HEADER)
            self.assertEqual(m.inspect(image,self.nonce,self.sha)['latest']['sequence'],2)
            self.assertEqual(p.read_bytes()[:m.BASE],self.image[:m.BASE])

    def test_corrupt_stale_oversize_and_immutable_prefix(self):
        payload=b'x'*100;slot=m.header(1,self.nonce,payload)+payload+bytes(m.CAPACITY-len(payload))
        self.assertEqual(m.decode(slot,self.nonce)['payload'],payload)
        for offset in (0,8,16,24,56,60,64,100,m.HEADER):
            bad=bytearray(slot);bad[offset]^=1
            with self.subTest(offset=offset),self.assertRaises(ValueError):m.decode(bad,self.nonce)
        with self.assertRaises(ValueError):m.decode(slot,b'z'*32)
        with self.assertRaises(ValueError):m.header(1,self.nonce,b'x'*(m.CAPACITY+1))
        with self.assertRaises(ValueError):m.inspect(self.image,self.nonce,'0'*64)
        with self.assertRaises(ValueError):m.header(0,self.nonce,b'x')

    def test_foreign_tail_symlink_wrong_size_and_bad_nonce_are_no_write(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'fixture.img';bad=self.image[:-1]+b'x';p.write_bytes(bad)
            with self.assertRaises(ValueError):m.write_fixture(p,self.nonce,self.sha,b'x')
            self.assertEqual(p.read_bytes(),bad)
            alias=Path(folder)/'alias';alias.symlink_to(p)
            with self.assertRaises(OSError):m.write_fixture(alias,self.nonce,self.sha,b'x')
            p.write_bytes(self.image[:-1])
            with self.assertRaises(ValueError):m.write_fixture(p,self.nonce,self.sha,b'x')
            p.write_bytes(self.image)
            with self.assertRaises(ValueError):m.write_fixture(p,bytes(32),self.sha,b'x')
            self.assertEqual(p.read_bytes(),self.image)

    def test_actual_c_writer_matches_python_reader_and_every_write_flush_cut(self):
        import shutil
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);binary=folder/'probe'
            subprocess.run([shutil.which('cc'),'-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(ROOT/'projects/firetabs-android/diagnostic-usb'),str(ROOT/'tests/fixtures/retained_mailbox_probe.c'),'-o',str(binary)],check=True)
            prefix=bytes(range(251))*(m.BASE//251)+bytes(range(m.BASE%251))
            image,sha=m.prepare(prefix+bytes(m.PARTITION-m.BASE),self.nonce)
            p=folder/'disk.img';p.write_bytes(image)
            r=subprocess.run([str(binary),str(p),'0'],check=True,capture_output=True,text=True)
            self.assertEqual(r.stdout.strip(),'0 3')
            first=p.read_bytes();record=m.inspect(first,self.nonce,sha)['latest']
            self.assertEqual(record['payload'],b'C writer persisted before USB\n')
            for cut in range(1,7):
                p.write_bytes(first)
                subprocess.run([str(binary),str(p),str(cut)],check=True,capture_output=True)
                record=m.inspect(p.read_bytes(),self.nonce,sha)['latest']
                self.assertIsNotNone(record)
                self.assertIn(record['sequence'],[1,2])
                self.assertEqual(p.read_bytes()[:m.BASE],prefix)
            bad=bytearray(first);bad[5]^=1;p.write_bytes(bad)
            r=subprocess.run([str(binary),str(p),'0'],check=True,capture_output=True,text=True)
            self.assertEqual(r.stdout.strip(),'-3 0')
            self.assertEqual(p.read_bytes(),bad)

    def test_preinstalled_host_control_is_distinct_and_survives_torn_kernel_record(self):
        control=b'VALETHON HOST CONTROL v1\nnot a kernel log\n'
        empty=b'ANDROID!'+bytes(m.PARTITION-8)
        image,sha=m.prepare(empty,self.nonce,control)
        self.assertEqual(m.inspect(image,self.nonce,sha)['latest']['sequence'],1)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'fixture';p.write_bytes(image)
            m.write_fixture(p,self.nonce,sha,b'VALETHON RETAINED KERNEL LOG v1 release=test\nactual printk\n')
            after=bytearray(p.read_bytes());after[m.SLOT_BASE+m.SLOT+m.HEADER]^=1
            fallback=m.inspect(after,self.nonce,sha)['latest']
            self.assertEqual(fallback['sequence'],1);self.assertEqual(fallback['payload'],control)
