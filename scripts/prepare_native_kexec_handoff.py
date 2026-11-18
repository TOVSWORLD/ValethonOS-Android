#!/usr/bin/env python3
"""Prepare exact-source native handoff CPU gates; never deploys or executes."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

MACHINE_SHA='c026a6fd6a260c584bd8053b0bb3b283194676e5103fe8fde584892db7f57815'
REBOOT_SHA='26a5412f18d29581785a6b05895c8e3bb64968fe2c5f385930aeef1d410ba208'
RESET_SHA='6f8873558cb62ac5403af15f25493ecab5b73bf803b835e449712e7dcbde0666'
HELPERS=r'''
#ifdef CONFIG_MACH_MT8163
#include <linux/of.h>
#include <linux/psci.h>
extern int mt_kexec_secondary_off_gate(void);
extern unsigned long mt_kexec_cpu_off_failures(void);
/* Load-time refusal is recoverable; final refusal follows device shutdown and
 * must never return to userspace or proceed to relocation. Existing panic policy
 * applies. This adds no reboot timer or recovery automation.
 */
static int mt8163_kexec_load_gate(const struct kimage *image)
{
 unsigned cpu;
 if (!of_machine_is_compatible("mediatek,mt8163")) return 0;
 if (image->type != KEXEC_TYPE_DEFAULT) return -EINVAL;
 if (num_possible_cpus() != 4 || !cpu_online(0) || !psci_ops.affinity_info)
  return -EOPNOTSUPP;
 for (cpu=0;cpu<4;cpu++) if (!cpu_possible(cpu)) return -EINVAL;
 if (mt_kexec_cpu_off_failures()) return -EIO;
 return 0;
}
static void mt8163_kexec_final_gate(void)
{
 int ret;
 if (!of_machine_is_compatible("mediatek,mt8163")) return;
 if (raw_smp_processor_id() != 0)
  panic("KXHANDOFF wrong survivor CPU; relocation refused");
 ret = mt_kexec_secondary_off_gate();
 if (ret)
  panic("KXHANDOFF secondary-off gate failed %d; relocation refused",ret);
 pr_emerg("KXHANDOFF final_cpu_gate=passed survivor=0\n");
}
#else
static int mt8163_kexec_load_gate(const struct kimage *image) { return 0; }
static void mt8163_kexec_final_gate(void) { }
#endif
'''

ORDERLY_HELPER=r'''
#if defined(CONFIG_KEXEC_CORE) && defined(CONFIG_MACH_MT8163)
#include <linux/of.h>
#include <linux/sched.h>
/* Android init performs its existing service/volume/filesystem shutdown before
 * RESTART2. Only this exact board-specific target selects the loaded image.
 * A return after that shutdown is fatal, never a silent firmware reboot.
 */
static int mt8163_orderly_kexec(const char *target)
{
 int ret;
 if (!of_machine_is_compatible("mediatek,mt8163") ||
     strcmp(target,"valethon-kexec")) return 0;
 if (task_tgid_nr(current) != 1) return -EPERM;
 pr_emerg("KXHANDOFF init_reboot_route=1 kexec_requested=1\n");
 ret = kernel_kexec();
 panic("KXHANDOFF orderly kexec returned %d; no firmware fallback",ret);
}
#else
static int mt8163_orderly_kexec(const char *target) { return 0; }
#endif
'''


def prepare_orderly_reboot(source, out):
    raw=source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=REBOOT_SHA:raise ValueError('Exact reboot dispatcher source required')
    before=raw.decode()
    after=replace(before,'void kernel_restart_prepare(char *cmd)',ORDERLY_HELPER+'\nvoid kernel_restart_prepare(char *cmd)')
    after=replace(after,'\t\tkernel_restart(buffer);','\t\tret = mt8163_orderly_kexec(buffer);\n\t\tif (ret) break;\n\t\tkernel_restart(buffer);')
    out.mkdir()
    (out/'reboot.c').write_text(after)
    (out/'orderly-kexec.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/kernel/reboot.c',tofile='b/kernel/reboot.c')))
    report={'scope':'Namespaced Android orderly reboot-to-kexec routing; not hardware-tested',
      'original_sha256':REBOOT_SHA,'patched_sha256':hashlib.sha256(after.encode()).hexdigest(),
      'target':'valethon-kexec','other_reboot_targets_unchanged':True,'requires_init_thread_group':True,
      'post_shutdown_return':'existing panic policy; no silent firmware fallback',
      'android_source_reference':'https://github.com/LineageOS/android_system_core/blob/lineage-18.1/init/reboot.cpp',
      'android_reboot_syscall_reference':'https://github.com/LineageOS/android_system_core/blob/lineage-18.1/init/reboot_utils.cpp',
      'userspace_binary_equivalence_qualified':False,'hardware_execution':False}
    (out/'source-report.json').write_text(json.dumps(report,indent=2)+'\n');return report


def replace(text,old,new):
    if text.count(old)!=1:raise ValueError('Pinned native handoff anchor differs')
    return text.replace(old,new)


def prepare(machine, reset, out):
    raw=machine.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=MACHINE_SHA or hashlib.sha256(reset.read_bytes()).hexdigest()!=RESET_SHA:
        raise ValueError('Exact native kexec/reset source required')
    before=raw.decode()
    after=replace(before,'static unsigned long kimage_start;','static unsigned long kimage_start;\n'+HELPERS)
    after=replace(after,'int machine_kexec_prepare(struct kimage *kimage)\n{',
      'int machine_kexec_prepare(struct kimage *kimage)\n{\n\tint ret = mt8163_kexec_load_gate(kimage);\n\tif (ret) return ret;')
    after=replace(after,'\tvoid *reboot_code_buffer;\n',
      '\tvoid *reboot_code_buffer;\n\n\t/* Native machine_shutdown froze hotplug; keep it disabled through relocation. */\n\tmt8163_kexec_final_gate();\n')
    out.mkdir()
    (out/'machine_kexec.c').write_text(after)
    (out/'native-handoff.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/arch/arm64/kernel/machine_kexec.c',tofile='b/arch/arm64/kernel/machine_kexec.c')))
    report={'scope':'Native handoff CPU gates; unbuilt and not hardware-qualified',
      'original_sha256':MACHINE_SHA,'patched_sha256':hashlib.sha256(after.encode()).hexdigest(),
      'reset_header_unchanged_sha256':RESET_SHA,'uses_existing_conditional_el2_switch':True,
      'final_gate_precedes_relocation_and_cache_transition':True,'post_shutdown_failure':'existing panic policy; no return/jump',
      'required_config':{'CONFIG_KEXEC':'y','CONFIG_KEXEC_CORE':'y','CONFIG_MACH_MT8163':'y','CONFIG_MTK_PSCI':'y'},
      'excluded_config':['CONFIG_KEXEC_JUMP=y','CONFIG_CRASH_DUMP=y'],
      'failed_jump_log_qualification_required_before_first_jump':False,
      'hardware_execution':False,'boot_image_packaged':False}
    (out/'source-report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['machine-source','cpu-reset-header','out']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();print(json.dumps(prepare(a.machine_source,a.cpu_reset_header,a.out),indent=2))
