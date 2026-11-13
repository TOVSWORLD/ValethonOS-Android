from pathlib import Path
import re
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]


class LabLabels(unittest.TestCase):
    def test_pinned_label_syscall_numbers(self):
        header = (ROOT / 'projects/firetabs-android/diagnostic-usb/lab_labels.h').read_text()
        table = (ROOT / 'evidence/usb-acm-userspace/source/syscall.tbl').read_text()
        for name, number in re.findall(r'#define LL_NR_(L\w+XATTR) (\d+)', header):
            self.assertRegex(table, r'(?m)^' + number + r'\s+common\s+' + name.lower() + r'\s')

    def test_actual_label_and_namespace_checks_with_faults(self):
        code = r'''
#include <assert.h>
#include <string.h>
#define FT_ACM_HOST_TEST 1
#include "lab_labels.h"
static const char *paths[]={"/dev","/dev/console","/dev/kmsg"};
static const char *contexts[]={"system_u:object_r:dev_dir_t","system_u:object_r:console_t","system_u:object_r:kmsg_t"};
struct fake {int calls,fail,labels[3],sets,bad_device,bad_readback,namespace_mode,seen[2];};
static unsigned long record(unsigned char *out,const char *name){
 unsigned long n=strlen(name),size=(20+n+7)&~7UL;memset(out,0,size);out[16]=(unsigned char)size;memcpy(out+19,name,n+1);return size;
}
static long call(void *ctx,long nr,long a,long b,long c,long d,long e,long f){
 struct fake *s=ctx;(void)f;s->calls++;if(s->fail==s->calls)return -5;
 if(nr==FT_NR_OPENAT){
  if(s->namespace_mode){if(!strcmp((char *)b,"/config"))return 20;assert(!strcmp((char *)b,"/config/usb_gadget"));return 21;}
  for(int i=0;i<3;i++)if(!strcmp((char *)b,paths[i]))return 10+i;assert(0);
 }
 if(nr==FT_NR_CLOSE)return 0;
 if(nr==FT_SERIAL_STATX){int i=(int)a-10;unsigned char *p=(unsigned char *)e;assert(i>=0&&i<3);memset(p,0,256);p[0]=1;p[29]=i?0x20:0x40;
  if(i){p[128]=i==1?5:1;p[132]=i==1?1:11;}if(s->bad_device)p[29]=0xa0;return 0;}
 if(nr==LL_NR_LGETXATTR||nr==LL_NR_LSETXATTR){
  assert(!strcmp((char *)b,"security.selinux"));int i=0;while(i<3&&strcmp((char *)a,paths[i]))i++;assert(i<3);
  if(nr==LL_NR_LSETXATTR){assert(!strcmp((char *)c,contexts[i]));assert(d==(long)strlen(contexts[i])+1);s->labels[i]=1;s->sets++;return 0;}
  const char *value=s->labels[i]&&!s->bad_readback?contexts[i]:"system_u:object_r:rootfs_t";memcpy((void *)c,value,strlen(value)+1);return (long)strlen(value)+1;
 }
 if(nr==FT_NR_GETDENTS64){int i=(int)a-20;assert(i==0||i==1);if(s->seen[i]++)return 0;
  unsigned char *p=(unsigned char *)b;unsigned long n=record(p,".");n+=record(p+n,"..");
  if(!i)n+=record(p+n,s->namespace_mode==2?"other":"usb_gadget");
  if(i&&s->namespace_mode==3)n+=record(p+n,"existing-gadget");
  if(s->namespace_mode==4)p[16]=0;return (long)n;
 }
 assert(0);return -5;
}
int main(void){
 struct fake good={0};struct ft_acm_io io={call,&good};assert(ll_label_archive(&io)==0&&good.sets==3);int calls=good.calls;
 for(int n=1;n<=calls;n++){struct fake bad={0};bad.fail=n;io.ctx=&bad;assert(ll_label_archive(&io)<0);assert(bad.sets<=3);}
 struct fake wrong={0};wrong.bad_device=1;io.ctx=&wrong;assert(ll_label_archive(&io)==-19&&wrong.sets==0);
 struct fake readback={0};readback.bad_readback=1;io.ctx=&readback;assert(ll_label_archive(&io)==-13&&readback.sets==1);
 assert(ll_context_equal((const unsigned char *)contexts[0],strlen(contexts[0]),contexts[0]));
 assert(!ll_context_equal((const unsigned char *)"other",5,contexts[0]));
 for(int mode=1;mode<=4;mode++){struct fake space={0};space.namespace_mode=mode;io.ctx=&space;int r=ll_usb_namespace(&io);assert(mode==1?r==0:r<0);assert(space.sets==0);}
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / 'labels.c'
            source.write_text(code)
            binary = Path(d) / 'labels'
            r = subprocess.run(['cc', '-std=c11', '-fsanitize=address,undefined',
                                '-I', str(ROOT / 'projects/firetabs-android/diagnostic-usb'),
                                str(source), '-o', str(binary)], capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr.decode())
            subprocess.run([str(binary)], check=True, capture_output=True)
