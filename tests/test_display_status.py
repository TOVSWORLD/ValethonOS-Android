import os
import shutil
import subprocess
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from receive_display_status import decode, receive_fd


class DisplayStatus(unittest.TestCase):
    nonce = bytes(range(32))

    def packet(self, stage=3, error=0, flags=7, banner_error=0):
        return (b'VDISP001' + self.nonce +
                struct.pack('<IIiIIIIIQIi', 1, stage, error, flags, 800, 1280,
                            32, 3200, 4096000, 13, banner_error) +
                b'mediatekdrmfb' + bytes(19))

    def test_banner_success_requires_visual_confirmation(self):
        result = decode(self.packet(), self.nonce)
        self.assertTrue(result['console_banner_written'])
        self.assertFalse(result['physical_pixels_confirmed'])
        self.assertTrue(result['owner_visual_confirmation_required'])
        self.assertFalse(result['kernel_log_transfer_required'])

    def test_failures_remain_failures(self):
        result = decode(self.packet(stage=2, flags=3, error=-13, banner_error=-13), self.nonce)
        self.assertTrue(result['framebuffer_metadata_ready'])
        self.assertFalse(result['console_banner_written'])

    def test_rejects_replay_corruption_and_false_success(self):
        good = self.packet()
        cases = [good[:-1], good + b'x', b'VSTORE01' + good[8:],
                 self.packet(stage=2, flags=3), self.packet(error=-5),
                 self.packet(stage=1, flags=7)]
        for offset, value in [(56, 801), (60, 720), (64, 8), (68, 1), (80, 32)]:
            bad = bytearray(good)
            struct.pack_into('<I', bad, offset, value)
            cases.append(bytes(bad))
        cases.append(good[:-1] + b'x')
        for packet in cases:
            with self.subTest(packet=packet[40:88]), self.assertRaises(ValueError):
                decode(packet, self.nonce)
        with self.assertRaises(ValueError):
            decode(good, bytes(32))

    def test_one_way_receiver_persists_exact_packet(self):
        read, write = os.pipe()
        try:
            os.write(write, self.packet())
            with tempfile.TemporaryFile() as raw:
                result = receive_fd(read, raw.fileno(), self.nonce, time.monotonic()+1)
                raw.seek(0)
                self.assertEqual(raw.read(), self.packet())
                self.assertTrue(result['complete'])
                self.assertFalse(result['device_qualified'])
        finally:
            os.close(read)
            os.close(write)

    def test_actual_probe_metadata_banner_and_failures(self):
        source = r'''
#include <string.h>
#include <stdlib.h>
#include "display_status.h"
struct fake {int which,position,bad,short_write,writes;};
static long call(void *opaque,long nr,long a,long b,long c,long d,long e,long f){
 struct fake *s=opaque;(void)d;(void)e;(void)f;
 if(nr==FT_NR_OPENAT){
  const char *p=(const char *)b;s->position=0;
  if(strstr(p,"virtual_size"))s->which=0;
  else if(strstr(p,"bits_per_pixel"))s->which=1;
  else if(strstr(p,"stride"))s->which=2;
  else if(strstr(p,"/name"))s->which=3;
  else if(!strcmp(p,"/dev/console")){s->which=4;return 9;}
  else abort();
  return 8;
 }
 if(nr==FT_NR_CLOSE)return 0;
 if(nr==FT_NR_READ){
  const char *data[]={"800,1280\n","32\n","3200\n","mediatekdrmfb\n"};
  const char *text=s->bad&&s->which==2?"1\n":data[s->which];
  size_t n=strlen(text)-s->position;if(n>(size_t)c)n=(size_t)c;
  memcpy((void *)b,text+s->position,n);s->position+=(int)n;return (long)n;
 }
 if(nr==FT_NR_WRITE){
  if(a!=9||s->which!=4||!strstr((const char *)b,"VALETHON DISPLAY TEST"))abort();
  s->writes++;return c-s->short_write;
 }
 abort();
}
int main(void){
 struct fake f={0};struct ft_acm_io io={call,&f};struct fd_result r={0};
 if(fd_metadata(&io,&r)||r.width!=800||r.height!=1280||r.name_length!=13)abort();
 if(fd_banner(&io)||f.writes!=1)abort();
 f.short_write=1;if(fd_banner(&io)!=-5)abort();
 f.bad=1;if(fd_metadata(&io,&r)!=-19)abort();
 unsigned char nonce[32]={1},packet[120];r.stage=3;r.flags=7;r.error=0;
 fd_packet(packet,nonce,&r);if(memcmp(packet,"VDISP001",8)||packet[8]!=1||packet[44]!=3)abort();
 return 0;
}
'''
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path/'probe.c').write_text(source)
            subprocess.run([shutil.which('clang') or 'cc', '-std=c11',
                            '-fsanitize=address,undefined','-DFT_ACM_HOST_TEST=1', '-I',
                            str(root/'projects/firetabs-android/diagnostic-usb'),
                            str(path/'probe.c'), '-o', str(path/'probe')], check=True,
                           capture_output=True)
            subprocess.run([str(path/'probe')], check=True, capture_output=True)
