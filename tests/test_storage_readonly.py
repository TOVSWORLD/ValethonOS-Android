"""Functional wire negatives and RAM-only syscall tests; never access a device."""
import shutil
import os
import time
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from receive_storage_status import decode, receive_fd, BOOT_SHA256, BOOT_BYTES
from build_lab_log_initramfs import inspect_archive
from build_diagnostic_initramfs import archive


def packet(nonce, *, stage=5, error=0, flags=31, read=BOOT_BYTES, digest=None):
    return (b'VSTORE01' + nonce + struct.pack('<IIiIQQQII', 1, stage, error, flags,
            read, BOOT_BYTES, 0, 179, 5) + (bytes.fromhex(BOOT_SHA256) if digest is None else digest))


class StorageReadonly(unittest.TestCase):
    def test_complete_packet_and_stale_identity(self):
        nonce = bytes(range(32))
        self.assertTrue(decode(packet(nonce), nonce)['storage_readonly_verified'])
        with self.assertRaises(ValueError):
            decode(packet(nonce), bytes(reversed(nonce)))
        for raw in [packet(nonce)[:-1], packet(nonce) + b'x', b'VLOG0002' + packet(nonce)[8:]]:
            with self.assertRaises(ValueError):
                decode(raw, nonce)

    def test_failure_and_inconsistent_success(self):
        nonce = bytes(range(32))
        raw = packet(nonce, stage=3, error=-5, flags=7, read=4096, digest=bytes(32))
        self.assertFalse(decode(raw, nonce)['storage_readonly_verified'])
        for kwargs in [dict(flags=15, stage=4, digest=bytes(32)), dict(read=BOOT_BYTES-1),
                       dict(digest=bytes(32)), dict(flags=63), dict(error=1), dict(stage=4),
                       dict(stage=1, flags=1, error=-19, read=0)]:
            with self.assertRaises(ValueError):
                decode(packet(nonce, **kwargs), nonce)

    def test_one_way_receiver_preserves_status_and_failure_packets(self):
        nonce=bytes(range(32))
        for error in (0, -5):
            status=packet(nonce, error=error)
            rd,wr=os.pipe()
            try:
                os.write(wr,status);os.close(wr);wr=-1
                with tempfile.TemporaryFile() as raw:
                    report=receive_fd(rd,raw.fileno(),nonce,time.monotonic()+1)
                    raw.seek(0);self.assertEqual(raw.read(),status)
                    self.assertTrue(report['complete'])
                    self.assertEqual(report['storage_readonly_verified'],not error)
            finally:
                os.close(rd)
                if wr>=0:os.close(wr)
        rd,wr=os.pipe();os.close(wr)
        try:
            with tempfile.TemporaryFile() as raw, self.assertRaises(ValueError):
                receive_fd(rd,raw.fileno(),nonce,time.monotonic()+1)
        finally:os.close(rd)

    def test_storage_archive_cannot_enter_logging_profile(self):
        entries = [(n, 0o040755, b'', (0, 0)) for n in ['dev', 'proc', 'sys', 'security', 'config']]
        entries += [('dev/console', 0o020600, b'', (5, 1)), ('dev/kmsg', 0o020400, b'', (1, 11)),
                    ('dev/firetabs-boot', 0o060400, b'', (179, 5)), ('init', 0o100500, b'ELF-fixture', (0, 0))]
        self.assertIn('dev/firetabs-boot', inspect_archive(archive(entries), entries, storage_readonly=True))
        with self.assertRaises(ValueError):
            inspect_archive(archive(entries), entries)
        for mode, dev in [(0o060600, (179, 5)), (0o060400, (179, 6)), (0o020400, (179, 5))]:
            mutated = entries.copy();mutated[-2] = ('dev/firetabs-boot', mode, b'', dev)
            with self.assertRaises(ValueError):
                inspect_archive(archive(mutated), mutated, storage_readonly=True)

    def test_ram_only_syscall_failures_and_packet(self):
        compiler = shutil.which('clang') or shutil.which('cc')
        self.assertIsNotNone(compiler, 'Native compiler required for syscall contract test')
        harness = r'''
#define FT_ACM_HOST_TEST 1
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "storage_readonly.h"
struct fake {int mode,blockopens,closed,freed;unsigned long offset,clock;const char *metadata;};
int combined_verify(const unsigned char *p,unsigned long n,const unsigned char hash[32]){
 if(n!=FS_BOOT_BYTES||hash[0]!=8||hash[31]!=0x1e)return 2;
 return p[0]==0x5a?0:1;
}
static long call(void *opaque,long nr,long a,long b,long c,long d,long e,long f){
 struct fake *x=opaque;(void)d;(void)e;(void)f;
 if(nr==LL_NR_CLOCK_GETTIME){long *ts=(long *)b;ts[0]=1;ts[1]=(long)(x->clock++*1000);return 0;}
 if(nr==FT_SERIAL_NANOSLEEP)return 0;
 if(nr==FT_NR_OPENAT){
  const char *path=(const char *)b;
  if(!strcmp(path,"/dev/firetabs-boot")){
   if(c!=(FT_O_NOFOLLOW|FT_O_CLOEXEC))abort();x->blockopens++;return 10;
  }
  if(!strcmp(path,"/sys/class/block/mmcblk0p5/dev"))x->metadata=x->mode==1?"179:6\n":"179:5\n";
  else if(!strcmp(path,"/sys/class/block/mmcblk0p5/partition"))x->metadata="5\n";
  else if(!strcmp(path,"/sys/class/block/mmcblk0p5/size"))x->metadata="32768\n";
  else if(!strcmp(path,"/sys/class/block/mmcblk0/device/type"))x->metadata="MMC\n";
  else abort();return 20;
 }
 if(nr==FT_NR_READ){
  if(a==20){unsigned long n=strlen(x->metadata);if(n>(unsigned long)c)abort();memcpy((void *)b,x->metadata,n);x->metadata="";return (long)n;}
  if(a!=10)abort();
  if(x->mode==3&&x->offset>=4096)return 0;
  if(x->offset==FS_BOOT_BYTES){if(x->mode==5){*(char *)b='X';return 1;}return 0;}
  unsigned long n=(unsigned long)c;if(x->mode==3&&n>4096)n=4096;
  memset((void *)b,x->mode==4?0:0x5a,n);x->offset+=n;return (long)n;
 }
 if(nr==FT_SERIAL_STATX){unsigned char *st=(unsigned char *)e;memset(st,0,256);st[0]=1;st[29]=0x60;st[128]=179;st[132]=x->mode==2?6:5;return 0;}
 if(nr==222)return (long)malloc(FS_BOOT_BYTES);
 if(nr==215){free((void *)a);x->freed++;return 0;}
 if(nr==FT_NR_CLOSE){if(a==10)x->closed++;return 0;}
 /* In particular: no ioctl, write, mount, mknod or alternate path. */
 abort();
}
int main(void){
 for(int mode=0;mode<=5;mode++){
  struct fake x={0};x.mode=mode;struct ft_acm_io io={call,&x};struct ll_context ctx={&io,-1,-1,10000,0};struct fs_result r={0};
  int result=fs_probe(&ctx,&r);
  if((mode==0)!=(result==0))return 10+mode;
  if(mode==0&&(r.flags!=31||r.stage!=5||r.bytes!=FS_BOOT_BYTES))return 20;
  if(mode==1&&(x.blockopens||x.closed||x.freed))return 21;
  if(mode==2&&(x.closed!=1||x.freed))return 22;
  if(mode>=3&&(x.closed!=1||x.freed!=1))return 23;
  unsigned char nonce[32],wire[120];for(int i=0;i<32;i++)nonce[i]=(unsigned char)i;
  fs_packet(wire,nonce,&r);if(fwrite(wire,1,120,stdout)!=120)return 24;
 }
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'probe.c';source.write_text(harness)
            binary = Path(directory)/'probe'
            subprocess.run([compiler, '-std=c11', '-Wall', '-Wextra', '-Wno-unused-function',
                            '-I', str(ROOT/'projects/firetabs-android/diagnostic-usb'), str(source), '-o', str(binary)],
                           check=True, capture_output=True)
            result = subprocess.run([str(binary)], check=True, capture_output=True)
        self.assertEqual(len(result.stdout), 720)
        for mode in range(6):
            report = decode(result.stdout[mode*120:(mode+1)*120], bytes(range(32)))
            self.assertEqual(report['storage_readonly_verified'], mode == 0)
