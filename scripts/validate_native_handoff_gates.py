#!/usr/bin/env python3
"""Execute actual generated load/final gate text with mocked kernel APIs."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from validate_legacy_affinity import function


def validate(source):
    text=source.read_text()
    load=function(text,'static int mt8163_kexec_load_gate(')
    final=function(text,'static void mt8163_kexec_final_gate(')
    prepare=function(text,'int machine_kexec_prepare(')
    execute=function(text,'void machine_kexec(')
    if prepare.index('mt8163_kexec_load_gate(')>prepare.index('kimage_start ='):
        raise ValueError('Load gate too late')
    if execute.index('mt8163_kexec_final_gate();')>execute.index('memcpy('):
        raise ValueError('Final gate after relocation preparation')
    c=r'''
#include <errno.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
#define KEXEC_TYPE_DEFAULT 0
struct kimage { int type; };
static int board,possible_count,possible_bits,online_zero,current,off_ret;
static int checks,panics,records;
static unsigned long failures;
static unsigned long mt_kexec_cpu_off_failures(void) { return failures; }
static jmp_buf escape;
static struct { void *affinity_info; } psci_ops;
static int of_machine_is_compatible(const char *s) { return board; }
static int num_possible_cpus(void) { return possible_count; }
static int cpu_online(int cpu) { return !cpu && online_zero; }
static int cpu_possible(int cpu) { return !!(possible_bits & (1<<cpu)); }
static int raw_smp_processor_id(void) { return current; }
static int mt_kexec_secondary_off_gate(void) { checks++;return off_ret; }
static void __attribute__((noreturn)) panic(const char *fmt,...) { panics++;longjmp(escape,1); }
#define pr_emerg(...) (records++)
'''+load+'\n'+final+r'''
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"line %d\n",__LINE__);return 1; } } while(0)
int main(void) {
 unsigned cases=0,mode;struct kimage image;
 for(mode=0;mode<8;mode++) {
  failures=0;board=1;possible_count=4;possible_bits=15;online_zero=1;psci_ops.affinity_info=(void*)1;image.type=0;
  if(mode==1)image.type=1;
  if(mode==2)possible_count=3;
  if(mode==3)online_zero=0;
  if(mode==4)psci_ops.affinity_info=0;
  if(mode==5)possible_bits=7;
  if(mode==7)failures=1;
  if(mode==6){board=0;image.type=1;possible_bits=0;psci_ops.affinity_info=0;}
  CHECK((mt8163_kexec_load_gate(&image)==0)==(mode==0 || mode==6));cases++;
 }
 for(mode=0;mode<5;mode++) {
  board=1;current=0;off_ret=0;checks=panics=records=0;
  if(mode==1)current=1;
  if(mode==2)off_ret=-EIO;
  if(mode==3)off_ret=-ETIMEDOUT;
  if(mode==4){board=0;current=2;off_ret=-EIO;}
  if(!setjmp(escape)) {
   mt8163_kexec_final_gate();
   CHECK(mode==0 || mode==4); /* Only these may reach relocation. */
  } else CHECK(mode>=1 && mode<=3);
  CHECK(panics==(mode>=1 && mode<=3));
  CHECK(checks==(mode==0 || mode==2 || mode==3));
  CHECK(records==(mode==0));cases++;
 }
 printf("%u\n",cases);return 0;
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp);(p/'control.c').write_text(c)
        subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-unused-parameter',str(p/'control.c'),'-o',str(p/'control')],capture_output=True,check=True)
        result=subprocess.run([str(p/'control')],capture_output=True,text=True,check=True)
    return {'scope':'Generated CPU gate control flow with mocked kernel APIs; no hardware',
      'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases_passed':int(result.stdout),
      'load_gate_precedes_state_assignment':True,'final_gate_precedes_relocation_setup':True,
      'post_shutdown_refusal_cannot_reach_relocation':True,'hardware_execution':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=validate(a.source);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
