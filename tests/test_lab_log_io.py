from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]


class LabLogIO(unittest.TestCase):
    def test_actual_nonblocking_adapter_faults(self):
        code = r'''
#include <assert.h>
#include <string.h>
#define FT_ACM_HOST_TEST 1
#include "lab_log_io.h"
struct fake {unsigned long ms;int fail,read_mode,writes,reads,closes,wrong_device;};
static long call(void *opaque,long nr,long a,long b,long c,long d,long e,long f){
 struct fake *s=opaque;(void)d;(void)e;(void)f;
 if(nr==LL_NR_CLOCK_GETTIME){long *t=(long *)b;t[0]=1;t[1]=(long)(s->ms++*1000000);return 0;}
 if(nr==FT_SERIAL_NANOSLEEP)return 0;
 if(nr==FT_NR_OPENAT){assert(!strcmp((char *)b,"/dev/kmsg"));return 7;}
 if(nr==FT_SERIAL_STATX){unsigned char *p=(unsigned char *)e;memset(p,0,256);p[0]=1;p[29]=0x20;p[128]=1;p[132]=s->wrong_device?12:11;return 0;}
 if(nr==LL_NR_LSEEK){assert(a==7&&b==0&&c==0);return 0;}
 if(nr==FT_NR_CLOSE){s->closes++;return 0;}
 if(nr==FT_NR_WRITE){s->writes++;return s->fail?s->fail:1;}
 if(nr==FT_NR_READ){s->reads++;if(s->read_mode)return s->read_mode;
  if(a==7){memcpy((void *)b,"log",3);return 3;}memset((void *)b,'x',c);return c;}
 assert(0);return -5;
}
int main(void){
 struct fake s={0};struct ft_acm_io io={call,&s};
 assert(ll_open_kmsg(&io)==7);s.wrong_device=1;assert(ll_open_kmsg(&io)==-19&&s.closes==1);
 s.wrong_device=0;struct ll_context c={&io,8,7,2000,1900};unsigned char b[16]={0};
 assert(ll_send(&c,b,16)==0&&s.writes==16);
 s.fail=-5;assert(ll_send(&c,b,2)==-5);s.fail=-11;c.deadline_ms=1050;assert(ll_send(&c,b,2)==-110);
 s.ms=0;c.deadline_ms=2000;assert(ll_read_log(&c,b,sizeof(b))==3);
 s.read_mode=-32;assert(ll_read_log(&c,b,sizeof(b))==-32); /* kmsg loss */
 s.read_mode=-5;assert(ll_read_log(&c,b,sizeof(b))==-5);
 c.stop_ms=1;assert(ll_read_log(&c,b,sizeof(b))==0);
 c.stop_ms=0;assert(ll_read_log(&c,b,sizeof(b))==-22);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / 'adapter.c'
            source.write_text(code)
            binary = Path(d) / 'adapter'
            subprocess.run(['cc', '-std=c11', '-fsanitize=address,undefined',
                            '-I', str(ROOT / 'projects/firetabs-android/diagnostic-usb'),
                            str(source), '-o', str(binary)], check=True, capture_output=True)
            subprocess.run([str(binary)], check=True, capture_output=True)
