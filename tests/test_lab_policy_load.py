from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LabPolicyLoad(unittest.TestCase):
    def test_pinned_abi_and_bootstrap_syscall_numbers(self):
        subprocess.run(['python3', str(ROOT / 'scripts/generate_diagnostic_selinux_abi.py'), '--check'], check=True)
        text = (ROOT / 'projects/firetabs-android/diagnostic-usb/lab_policy_load.h').read_text()
        table = (ROOT / 'evidence/usb-acm-userspace/source/syscall.tbl').read_text()
        for name, value in re.findall(r'^#define VP_NR_(\w+) (\d+)$', text, re.M):
            self.assertRegex(table, r'(?m)^' + value + r'\s+(?:common|64)\s+' + name.lower() + r'\s')

    def test_actual_bootstrap_and_faults_use_only_ram_callbacks(self):
        code = r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "lab_policy_load.h"
struct fake {int calls,fail_at,fail_code,writes,loads,remounts,read_pos,probe,permissive,short_write;};
static long call(void *ctx,long nr,long a,long b,long c,long d,long e,long f) {
 struct fake *s=ctx;(void)e;(void)f;s->calls++;
 if(nr==VP_NR_WRITE)s->writes++;
 if(s->fail_at==s->calls)return s->fail_code?s->fail_code:-5;
 if(nr==VP_NR_MOUNT){
  assert(strcmp((const char *)b,"/security")==0);
  if(d==14){assert(strcmp((const char *)a,"selinuxfs")==0);assert(strcmp((const char *)c,"selinuxfs")==0);}
  else {assert(d==47&&a==0&&c==0);s->remounts++;}return 0;
 }
 if(nr==VP_NR_OPENAT){assert(a==-100);const char *path=(const char *)b;
  if(strcmp(path,"/security/enforce")==0){s->read_pos=0;return 10;}
  if(strcmp(path,"/security/policy")==0)return s->probe?s->probe:-22;
  assert(strcmp(path,"/security/load")==0);assert(c&1);return 11;
 }
 if(nr==VP_NR_READ){assert(a==10&&c>=1);if(s->read_pos++)return 0;
  *(char *)b=s->permissive?'0':'1';return 1;
 }
 if(nr==VP_NR_WRITE){assert(a==11);s->loads++;return s->short_write?c-1:c;}
 if(nr==VP_NR_CLOSE){assert(a==10||a==11||a==30);return 0;}
 assert(0);return -5;
}
int main(void){
 unsigned char policy[32]={0x8c,0xff,0x7c,0xf9,8,0,0,0,'S','E',' ','L','i','n','u','x',33};
 struct fake good={0};struct vp_io io={call,&good};struct vp_state state={0};
 assert(vp_bootstrap(&io,policy,sizeof(policy),&state)==0);
 assert(state.attempted&&state.mounted&&state.loaded&&state.readonly);
 assert(good.writes==1&&good.loads==1&&good.remounts==1);int calls=good.calls;
 assert(vp_bootstrap(&io,policy,sizeof(policy),&state)==-16&&good.calls==calls);
 for(int fail=1;fail<=calls;fail++){
  struct fake bad={0};bad.fail_at=fail;bad.fail_code=-4;io.ctx=&bad;struct vp_state attempt={0};
  assert(vp_bootstrap(&io,policy,sizeof(policy),&attempt)<0);assert(bad.writes<=1);
  int used=bad.calls;assert(vp_bootstrap(&io,policy,sizeof(policy),&attempt)==-16&&bad.calls==used);
 }
 for(int mode=0;mode<4;mode++){
  struct fake bad={0};if(mode==0)bad.probe=30;if(mode==1)bad.probe=-13;
  if(mode==2)bad.permissive=1;if(mode==3)bad.short_write=1;
  io.ctx=&bad;struct vp_state attempt={0};assert(vp_bootstrap(&io,policy,sizeof(policy),&attempt)<0);
  assert(bad.writes==(mode==3?1:0));assert(!attempt.readonly);
 }
 struct fake invalid={0};io.ctx=&invalid;struct vp_state attempt={0};policy[16]=34;
 assert(vp_bootstrap(&io,policy,sizeof(policy),&attempt)==-22&&!invalid.calls);
 puts("VALETHON_POLICY_BOOTSTRAP_RAM_PASS");return 0;
}
'''
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / 'test.c'
            source.write_text(code)
            binary = folder / 'test'
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
                            '-I', str(ROOT / 'projects/firetabs-android/diagnostic-usb'),
                            str(source), '-o', str(binary)], check=True)
            result = subprocess.run([str(binary)], capture_output=True, text=True, check=True)
            self.assertIn('VALETHON_POLICY_BOOTSTRAP_RAM_PASS', result.stdout)


if __name__ == '__main__':
    unittest.main()
