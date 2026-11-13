#!/usr/bin/env python3
"""Mark accepted native kexec entry and pause one second before device shutdown."""
import argparse,difflib,hashlib,json
from pathlib import Path
SOURCE_SHA='d6059029914ea4eb59b1dfa8d1ca12bd721fc5e34e3108c277a1b7d1e2d5bf65'
CHECKPOINT='''
#ifdef CONFIG_MACH_MT8163
 /* Image ownership is serialized here. Make native entry observable before
  * device_shutdown tears down the USB controller. No CPU/relocation change.
  */
 if (kexec_image->type == KEXEC_TYPE_DEFAULT && task_tgid_nr(current) == 1 &&
     of_machine_is_compatible("mediatek,mt8163")) {
  pr_emerg("KXHANDOFF native_entry=1 image_present=1\\n");
  msleep(1000);
 }
#endif

'''
def prepare(before):
    if hashlib.sha256(before.encode()).hexdigest()!=SOURCE_SHA:raise ValueError('Exact audited native kexec core required')
    return add_dwell(before)
def add_dwell(before):
    anchor='\tif (!kexec_image) {\n\t\terror = -EINVAL;\n\t\tgoto Unlock;\n\t}\n\n'
    if before.count(anchor)!=1:raise ValueError('Native image admission checkpoint differs')
    after=before.replace('#include <linux/capability.h>','#include <linux/capability.h>\n#include <linux/delay.h>\n#include <linux/of.h>\n#include <linux/sched.h>',1)
    return after.replace(anchor,anchor+CHECKPOINT,1)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();before=a.source.read_text();after=prepare(before);a.out.mkdir(mode=0o700)
    (a.out/'kexec_core.c').write_text(after)
    (a.out/'checkpoint-dwell.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/kernel/kexec_core.c',tofile='b/kernel/kexec_core.c')))
    (a.out/'report.json').write_text(json.dumps(dict(original_sha256=SOURCE_SHA,patched_sha256=hashlib.sha256(after.encode()).hexdigest(),dwell_ms=1000,requires_board_and_pid1=True,after_native_image_and_mutex_admission=True,before_device_shutdown=True,ordinary_reboot_targets_unchanged=True,cpu_and_relocation_unchanged=True,hardware_execution=False),indent=2)+'\n')
