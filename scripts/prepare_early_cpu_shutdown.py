#!/usr/bin/env python3
"""Prepare an exact-source MT8163 handoff-order experiment; offline only."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

SOURCE_SHA = '0149bfdcd72217b3065a8c08de5ccdc85225fbabb367bb1d743a8b1d5d1d9239'
OLD = '''\t\tkexec_in_progress = true;
\t\tkernel_restart_prepare(NULL);
\t\tmigrate_to_reboot_cpu();

\t\t/*
\t\t * migrate_to_reboot_cpu() disables CPU hotplug assuming that
\t\t * no further code needs to use CPU hotplug (which is true in
\t\t * the reboot case). However, the kexec path depends on using
\t\t * CPU hotplug again; so re-enable it here.
\t\t */
\t\tcpu_hotplug_enable();
\t\tpr_emerg("Starting new kernel\\n");
\t\tmachine_shutdown();'''
NEW = '''\t\tbool early_cpu_shutdown = false;

\t\tkexec_in_progress = true;
#ifdef CONFIG_MACH_MT8163
\t\t/* Experiment: complete normal CPU hotplug while platform drivers
\t\t * still exist. Keep hotplug frozen throughout device shutdown and
\t\t * retain the independent machine_kexec final hardware gate.
\t\t * The preserve-context branch above does not enter this block.
\t\t */
\t\tif (kexec_image->type == KEXEC_TYPE_DEFAULT &&
\t\t    task_tgid_nr(current) == 1 &&
\t\t    of_machine_is_compatible("mediatek,mt8163")) {
\t\t\tmigrate_to_reboot_cpu();
\t\t\tcpu_hotplug_enable();
\t\t\terror = disable_nonboot_cpus();
\t\t\tif (error || raw_smp_processor_id() != 0 ||
\t\t\t    num_online_cpus() != 1 || !cpu_online(0))
\t\t\t\tpanic("KXHANDOFF early CPU shutdown failed %d", error);
\t\t\terror = mt_kexec_secondary_off_gate();
\t\t\tif (error)
\t\t\t\tpanic("KXHANDOFF early hardware CPU gate failed %d", error);
\t\t\tearly_cpu_shutdown = true;
\t\t\tpr_emerg("KXHANDOFF early_cpu_gate=passed survivor=0\\n");
\t\t\tmsleep(1000);
\t\t}
#endif
\t\tkernel_restart_prepare(NULL);
\t\tif (!early_cpu_shutdown) {
\t\t\tmigrate_to_reboot_cpu();
\t\t\t/* Balance migration's hotplug disable before machine_shutdown. */
\t\t\tcpu_hotplug_enable();
\t\t}
\t\tpr_emerg("Starting new kernel\\n");
\t\tif (!early_cpu_shutdown)
\t\t\tmachine_shutdown();'''


def prepare(before):
    if hashlib.sha256(before.encode()).hexdigest() != SOURCE_SHA:
        raise ValueError('Exact hardware-tested native-entry source required')
    if before.count(OLD) != 1:
        raise ValueError('Native shutdown sequence differs')
    decl = '#ifdef CONFIG_MACH_MT8163\nextern int mt_kexec_secondary_off_gate(void);\n#endif\n\n'
    return before.replace('DEFINE_MUTEX(kexec_mutex);', decl + 'DEFINE_MUTEX(kexec_mutex);', 1).replace(OLD, NEW, 1)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    before = a.source.read_text()
    after = prepare(before)
    a.out.mkdir(mode=0o700)
    (a.out / 'kexec_core.c').write_text(after)
    (a.out / 'early-cpu-shutdown.patch').write_text(''.join(difflib.unified_diff(
        before.splitlines(True), after.splitlines(True),
        fromfile='a/kernel/kexec_core.c', tofile='b/kernel/kexec_core.c')))
    (a.out / 'report.json').write_text(json.dumps({
        'original_sha256': SOURCE_SHA,
        'patched_sha256': hashlib.sha256(after.encode()).hexdigest(),
        'scope': 'MT8163 PID1 default-image CPU shutdown before device shutdown',
        'normal_reboot_dispatch_unchanged': True,
        'preserve_context_branch_unchanged': True,
        'cpu_off_implementation_unchanged': True,
        'final_hardware_cpu_gate_retained': True,
        'relocation_cache_mmu_el_transition_unchanged': True,
        'new_watchdog_or_log_transport': False,
        'hardware_execution': False,
        'target_boot_proven': False
    }, indent=2) + '\n')
