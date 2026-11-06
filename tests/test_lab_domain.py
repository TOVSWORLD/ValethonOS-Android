from pathlib import Path
import subprocess
import re
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]


class LabDomain(unittest.TestCase):
    def test_pinned_lsm_abi(self):
        source = (ROOT / 'projects/firetabs-android/diagnostic-usb/lab_domain.h').read_text()
        table = (ROOT / 'evidence/usb-acm-userspace/source/syscall.tbl').read_text()
        for name, number in re.findall(r'#define LL_NR_(LSM_\w+) (\d+)', source):
            self.assertRegex(table, r'(?m)^' + number + r'\s+common\s+' + name.lower() + r'\s')
        header = (ROOT / 'evidence/independent-recovery/selinux-source/lsm.h').read_text()
        for local, upstream in [('LL_LSM_ID_SELINUX', 'LSM_ID_SELINUX'), ('LL_LSM_ATTR_CURRENT', 'LSM_ATTR_CURRENT'), ('LL_LSM_FLAG_SINGLE', 'LSM_FLAG_SINGLE')]:
            a = re.search(r'#define ' + local + r'\s+(0x[0-9a-f]+|[0-9]+)', source)[1]
            b = re.search(r'#define ' + upstream + r'\s+(0x[0-9a-f]+|[0-9]+)', header)[1]
            self.assertEqual(int(a, 0), int(b, 0))

    def test_actual_lsm_transition_readback_and_failure_paths(self):
        code = r'''
#include <assert.h>
#include <string.h>
#define FT_ACM_HOST_TEST 1
#include "lab_domain.h"
struct fake {int calls,fail,sets,gets,enforce_pos,wrong,wrongid,multiple,permissive;};
static long call(void *ctx,long nr,long a,long b,long c,long d,long e,long f){
 struct fake *s=ctx;(void)e;(void)f;s->calls++;if(nr==460)s->sets++;if(nr==459)s->gets++;if(s->fail==s->calls)return -5;
 if(nr==460){unsigned long long *v=(void *)b;assert(a==100&&c==64&&d==0);assert(v[0]==101&&v[1]==0&&v[2]==64);assert(v[3]==sizeof("system_u:system_r:init_t"));assert(!strcmp((char *)v+32,"system_u:system_r:init_t"));return 0;}
 if(nr==459){unsigned long long *v=(void *)b;unsigned int *size=(void *)c;assert(a==100&&d==1&&v[0]==101&&*size==128);
  const char *text=s->wrong?"system_u:system_r:kernel_t":"system_u:system_r:init_t";unsigned long n=strlen(text)+1;memset(v,0,128);v[0]=s->wrongid?102:101;v[2]=32+n;v[3]=n;*size=(unsigned int)v[2];memcpy((char *)v+32,text,n);return s->multiple?2:1;}
 if(nr==56){assert(a==-100&&!strcmp((char *)b,"/security/enforce"));s->enforce_pos=0;return 11;}
 if(nr==63){assert(a==11);if(s->enforce_pos++)return 0;*(char *)b=s->permissive?'0':'1';return 1;}
 if(nr==57)return 0;
 assert(0);return -5;
}
int main(void){
 struct fake good={0};struct ft_acm_io io={call,&good};assert(ll_enter_init(&io)==0);assert(good.sets==1&&good.gets==1);int count=good.calls;
 for(int fail=1;fail<=count;fail++){struct fake bad={0};bad.fail=fail;io.ctx=&bad;assert(ll_enter_init(&io)<0);assert(bad.sets==1&&bad.gets<=1);}
 for(int mode=0;mode<4;mode++){struct fake bad={0};bad.wrong=mode==0;bad.wrongid=mode==1;bad.multiple=mode==2;bad.permissive=mode==3;io.ctx=&bad;assert(ll_enter_init(&io)<0);assert(bad.sets==1&&bad.gets==1);}
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            source, binary = Path(d) / 'domain.c', Path(d) / 'domain'
            source.write_text(code)
            r = subprocess.run(['cc', '-std=c11', '-fsanitize=address,undefined',
                                '-I', str(ROOT / 'projects/firetabs-android/diagnostic-usb'),
                                str(source), '-o', str(binary)], capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr.decode())
            subprocess.run([str(binary)], check=True, capture_output=True)
