#!/usr/bin/env python3
"""Exercise generated orderly reboot routing with mocked kernel entry/panic."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from validate_legacy_affinity import function


def validate(source):
    text=source.read_text();helper=function(text,'static int mt8163_orderly_kexec(')
    dispatch=text.split('case LINUX_REBOOT_CMD_RESTART2:',1)[1].split('case LINUX_REBOOT_CMD_KEXEC:',1)[0]
    expected='ret = mt8163_orderly_kexec(buffer);\n\t\tif (ret) break;\n\t\tkernel_restart(buffer);'
    if expected not in dispatch:raise ValueError('Dispatcher could fall through on refusal')
    c=r'''
#include <errno.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
static int board,tgid,calls,panics,records,response,jumped;
static jmp_buf escape;
#define current ((void*)0)
static int of_machine_is_compatible(const char *name) { return board; }
static int task_tgid_nr(void *task) { return tgid; }
static int kernel_kexec(void) { calls++;if(jumped)longjmp(escape,2);return response; }
static void __attribute__((noreturn)) panic(const char *fmt,...) { panics++;longjmp(escape,1); }
#define pr_emerg(...) (records++)
'''+helper+r'''
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"line %d\n",__LINE__);return 1; } } while(0)
int main(void) {
 const char *targets[]={"","recovery","bootloader","valethon-kexec-extra","valethon-kexec"};
 unsigned b,p,t,cases=0;int ret,event;
 for(b=0;b<2;b++)for(p=0;p<2;p++)for(t=0;t<5;t++) {
  board=b;tgid=p?1:99;calls=panics=records=0;response=-EINVAL;jumped=0;
  event=setjmp(escape);
  if(!event) {
   ret=mt8163_orderly_kexec(targets[t]);
   CHECK(!(b && p && t==4));
   CHECK(ret==((b && !p && t==4)?-EPERM:0));
  } else CHECK(event==1 && b && p && t==4);
  CHECK(calls==(b && p && t==4));CHECK(panics==calls);CHECK(records==calls);cases++;
 }
 for(p=0;p<2;p++) {
  board=tgid=1;calls=panics=records=0;jumped=p;response=0;
  event=setjmp(escape);
  if(!event) { mt8163_orderly_kexec("valethon-kexec");CHECK(0); }
  CHECK(calls==1 && records==1);CHECK(event==(p?2:1));CHECK(panics==!p);cases++;
 }
 printf("%u\n",cases);return 0;
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp);(p/'control.c').write_text(c)
        subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-unused-parameter',str(p/'control.c'),'-o',str(p/'control')],capture_output=True,check=True)
        r=subprocess.run([str(p/'control')],capture_output=True,text=True,check=True)
    return {'scope':'Actual generated namespace/board/PID1/error routing with mocked kernel calls',
      'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases_passed':int(r.stdout),
      'other_targets_unchanged':True,'wrong_caller_cannot_jump':True,
      'post_shutdown_return_cannot_silently_firmware_reboot':True,'hardware_execution':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=validate(a.source);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
