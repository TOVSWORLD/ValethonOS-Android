import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from receive_display_errors import decode,extent,receive_fd,CAPACITY
from inspect_display_errors import inspect


class DisplayErrors(unittest.TestCase):
    nonce=bytes(range(32))

    def frame(self,payload=b'3,1,100,-;mediatek-drm probe failed -517\n',error=0,flags=1,records=1):
        status=(b'VDISP002'+self.nonce+
                struct.pack('<IIiIIIIIQIi',2,1,-110,1,0,0,0,0,0,0,0)+bytes(32))
        return status+b'VKMSG001'+self.nonce+struct.pack('<IiII',len(payload),error,flags,records)+payload

    def test_failure_status_and_real_error_payload_are_independent(self):
        result=decode(self.frame(),self.nonce)
        self.assertFalse(result['console_banner_written'])
        self.assertTrue(result['kernel_snapshot_received'])
        self.assertTrue(result['kernel_snapshot_caught_up'])
        self.assertNotIn('payload',result)
        self.assertFalse(result['physical_pixels_confirmed'])

    def test_missing_tail_preserves_display_status(self):
        for data in [self.frame()[:120],self.frame()[:-1],self.frame()+b'extra']:
            result=decode(data,self.nonce)
            self.assertFalse(result['kernel_snapshot_received'])
            self.assertEqual(result['error'],-110)

    def test_explicit_read_failure_loss_and_truncation(self):
        result=decode(self.frame(b'',-13,16,0),self.nonce)
        self.assertTrue(result['kernel_snapshot_received'])
        self.assertEqual(result['kernel_snapshot_read_error'],-13)
        result=decode(self.frame(flags=6),self.nonce)
        self.assertTrue(result['kernel_snapshot_ring_loss'])
        self.assertTrue(result['kernel_snapshot_truncated'])
        self.assertFalse(result['kernel_snapshot_caught_up'])

    def test_replay_and_unbounded_header_rejected(self):
        with self.assertRaises(ValueError):decode(self.frame(),bytes(32))
        header=self.frame()[120:176]
        for at,value in [(40,CAPACITY+1),(48,0),(48,32),(52,4097),(48,16)]:
            bad=bytearray(header);struct.pack_into('<I',bad,at,value)
            with self.assertRaises(ValueError):extent(bytes(bad),self.nonce)
        with self.assertRaises(ValueError):decode(b'VDISP001'+self.frame()[8:],self.nonce)

    def test_one_way_capture_persists_status_and_tail(self):
        read,write=os.pipe()
        try:
            os.write(write,self.frame());os.close(write);write=None
            with tempfile.TemporaryFile() as raw:
                result=receive_fd(read,raw.fileno(),self.nonce,time.monotonic()+1)
                raw.seek(0);self.assertEqual(raw.read(),self.frame())
                self.assertTrue(result['kernel_snapshot_received'])
                self.assertTrue(result['complete'])
        finally:
            os.close(read)
            if write is not None:os.close(write)

    def test_disconnection_after_status_keeps_status_and_partial_wire(self):
        read,write=os.pipe()
        try:
            data=self.frame()[:130]
            os.write(write,data);os.close(write)
            with tempfile.TemporaryFile() as raw:
                result=receive_fd(read,raw.fileno(),self.nonce,time.monotonic()+1)
                raw.seek(0);self.assertEqual(raw.read(),data)
                self.assertTrue(result['complete'])
                self.assertFalse(result['kernel_snapshot_received'])
        finally:os.close(read)

    def test_error_extraction_stays_in_private_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);wire=root/'wire';wire.write_bytes(self.frame())
            result=inspect(wire,self.nonce,root/'inspection')
            self.assertEqual(result['parsed_records'],1)
            self.assertEqual(result['relevant_records'],1)
            output=root/'inspection/display-errors-private.txt'
            self.assertIn(b'probe failed -517',output.read_bytes())
            self.assertEqual(output.stat().st_mode&0o777,0o600)

    def test_actual_c_snapshot_limits_errors_and_no_ack(self):
        source=r'''
#include <stdlib.h>
#include <string.h>
#include "lab_log_io.h"
struct fake {int mode,reads,writes,closed;long sent;};
static long open_kmsg(struct ft_acm_io *io){struct fake *f=io->ctx;return f->mode==1?-13:42;}
#define ll_open_kmsg open_kmsg
#include "display_errors.h"
static long call(void *opaque,long nr,long a,long b,long c,long d,long e,long f){
 struct fake *s=opaque;(void)d;(void)e;(void)f;
 if(nr==LL_NR_CLOCK_GETTIME){long *ts=(long *)b;ts[0]=1;ts[1]=0;return 0;}
 if(nr==FT_NR_CLOSE){if(a!=42)abort();s->closed++;return 0;}
 if(nr==FT_NR_READ){
  if(a!=42)abort();s->reads++;
  if(s->mode==2&&s->reads==1)return -32;
  if(s->mode==3)return -4;
  if(s->mode==4){memset((void *)b,'x',(size_t)c);return c;}
  if(s->mode==5)return 8193;
  if(s->reads>(s->mode==2?2:1))return -11;
  const char text[]="3,1,100,-;drm probe failed -517\n";
  memcpy((void *)b,text,sizeof(text)-1);return sizeof(text)-1;
 }
 if(nr==FT_NR_WRITE){if(a!=9)abort();s->writes++;s->sent+=c;return c;}
 abort();
}
int main(void){
 for(int mode=0;mode<7;mode++){
  struct fake f={0};f.mode=mode;struct ft_acm_io io={call,&f};
  struct ll_context ctx={&io,9,-1,mode==6?999:5000,0};struct de_result r={0};
  de_snapshot(&ctx,&r);
  if(mode==0&&(r.flags!=1||r.records!=1||r.error))abort();
  if(mode==1&&(r.flags!=16||r.error!=-13||f.reads))abort();
  if(mode==2&&(r.flags!=5||r.records!=1))abort();
  if(mode==3&&(r.flags!=2||f.reads!=4096))abort();
  if(mode==4&&(r.flags!=2||r.bytes!=DE_CAPACITY||r.records!=32))abort();
  if(mode==5&&(r.flags!=16||r.error!=-5))abort();
  if(mode==6&&(r.flags!=8||r.error!=-110||f.reads))abort();
  int reads=f.reads;unsigned char nonce[32]={1};
  if(de_send(&ctx,nonce,&r)&&mode!=6)abort();
  if(f.reads!=reads)abort();
  if(mode!=6&&f.sent!=(long)(56+r.bytes))abort();
  if(mode!=1&&f.closed!=1)abort();
 }
 return 0;
}
'''
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);(p/'probe.c').write_text(source)
            subprocess.run([shutil.which('clang') or 'cc','-std=c11','-fsanitize=address,undefined',
                            '-I',str(root/'projects/firetabs-android/diagnostic-usb'),str(p/'probe.c'),
                            '-o',str(p/'probe')],check=True,capture_output=True)
            subprocess.run([str(p/'probe')],check=True,capture_output=True)
