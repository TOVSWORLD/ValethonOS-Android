#!/usr/bin/env python3
"""Exercise generated legacy binding initialization/argument guards with native stubs.
Uses actual generated function text; no kernel or firmware calls occur.
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


def function(text, declaration):
    start = text.index(declaration)
    opening = text.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        if text[end] == '{': depth += 1
        if text[end] == '}': depth -= 1
        end += 1
    return text[start:end]


def validate(source, policy, compiler='cc'):
    text = source.read_text()
    wrapper = function(text, 'static int mt8163_legacy_affinity_info(')
    initializer = function(text, 'static int __init psci_0_1_init(')
    harness = r'''
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "legacy_affinity_policy.h"
typedef uint32_t u32;
#define __init
#define PSCI_CONDUIT_SMC 1
#define PSCI_FN_CPU_SUSPEND 0
#define PSCI_FN_CPU_OFF 1
#define PSCI_FN_CPU_ON 2
#define PSCI_FN_MIGRATE 3
#define pr_info(...) ((void)0)
struct device_node { int unused; };
static struct { int conduit; void (*cpu_suspend)(void), (*cpu_off)(void),
 (*cpu_on)(void), (*migrate)(void); int (*affinity_info)(unsigned long, unsigned long); } psci_ops;
static u32 psci_function_id[4], mt8163_legacy_affinity_id;
static int board, legacy, method, property, conduit_error, calls, puts_count;
static u32 requested_fid;
static unsigned long got[4];
static long response;
static void psci_cpu_suspend(void) {}
static void psci_cpu_off(void) {}
static void psci_cpu_on(void) {}
static void psci_migrate(void) {}
static int get_set_conduit_method(struct device_node *np) {
 psci_ops.conduit=method; return conduit_error;
}
static int of_machine_is_compatible(const char *s) { return board; }
static int of_device_is_compatible(struct device_node *np,const char *s) { return legacy; }
static int of_property_read_u32(struct device_node *np,const char *s,u32 *out) {
 if (!strcmp(s,"affinity_info")) { if (!property) return -EINVAL; *out=requested_fid; }
 else *out=123; return 0;
}
static void of_node_put(struct device_node *np) { puts_count++; }
static unsigned long firmware(unsigned long fid,unsigned long cpu,unsigned long level,unsigned long zero) {
 calls++; got[0]=fid;got[1]=cpu;got[2]=level;got[3]=zero;return (unsigned long)response;
}
static unsigned long (*invoke_psci_fn)(unsigned long,unsigned long,unsigned long,unsigned long)=firmware;
'''
    harness += '\n'+wrapper+'\n'+initializer+'\n'
    harness += r'''
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"line %d\n",__LINE__); return 1; } } while(0)
int main(void) {
 struct device_node node;
 unsigned cases=0,mode,cpu; long ret;
 for (mode=0;mode<8;mode++) {
  memset(&psci_ops,0,sizeof(psci_ops));mt8163_legacy_affinity_id=0;
  calls=puts_count=0;board=legacy=32767;method=PSCI_CONDUIT_SMC;
  property=1;conduit_error=0;requested_fid=KXAFF_FID;
  if(mode==1) board=0;
  if(mode==2) legacy=0;
  if(mode==3) method=2;
  if(mode==4) property=0;
  if(mode==5) requested_fid=0x84000002U;
  if(mode==6) requested_fid=0xc4000004U;
  if(mode==7) conduit_error=-EIO;
  ret=psci_0_1_init(&node);
  CHECK(calls==0 && puts_count==1);
  CHECK(ret==(mode==7 ? -EIO:0));
  CHECK((psci_ops.affinity_info!=0)==(mode==0));
  if(mode==0) {
   CHECK(mt8163_legacy_affinity_id==KXAFF_FID);
   CHECK(psci_ops.cpu_suspend && psci_ops.cpu_off && psci_ops.cpu_on && psci_ops.migrate);
   for(cpu=0;cpu<4;cpu++) {
    response=cpu%3; calls=0; ret=psci_ops.affinity_info(cpu,0);
    CHECK(ret==response && calls==1 && got[0]==KXAFF_FID && got[1]==cpu && got[2]==0 && got[3]==0);cases++;
   }
   response=-1;calls=0;CHECK(psci_ops.affinity_info(0,0)==-1 && calls==1);cases++;
   calls=0;CHECK(psci_ops.affinity_info(4,0)==-EINVAL && calls==0);cases++;
   CHECK(psci_ops.affinity_info(~0UL,0)==-EINVAL && calls==0);cases++;
   CHECK(psci_ops.affinity_info(0,1)==-EINVAL && calls==0);cases++;
   CHECK(psci_ops.affinity_info(0,~0UL)==-EINVAL && calls==0);cases++;
  }
  cases++;
 }
 printf("%u\n",cases);return 0;
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp);(p/'binding.c').write_text(harness)
        (p/'legacy_affinity_policy.h').write_bytes(policy.read_bytes())
        subprocess.run([compiler,'-std=c99','-Wall','-Wextra','-Werror',
          '-Wno-unused-parameter','-Wno-misleading-indentation',str(p/'binding.c'),'-o',str(p/'validate')],
          check=True,capture_output=True)
        r=subprocess.run([str(p/'validate')],check=True,capture_output=True,text=True)
    return {'scope':'Actual generated initializer and callback text, native mocked APIs',
      'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'policy_sha256':hashlib.sha256(policy.read_bytes()).hexdigest(),
      'cases_passed':int(r.stdout),'firmware_calls':0,'hardware_qualified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['source','policy','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();r=validate(a.source,a.policy);a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
