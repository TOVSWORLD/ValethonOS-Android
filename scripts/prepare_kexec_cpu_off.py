#!/usr/bin/env python3
"""Generate a pinned-source CPU-off PATCH/overlay for compile review, never deploy."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

PIN = '72940eb733af8df948cc216cb977cd8be9cba5a9'
PREFIX = 'drivers/misc/mediatek/base/power/mt8163/'
HEADER_SHA = '3430b5449722792c331adc4ed6d57686f614eea16f9e10dd020c799c9f3752db'
OPS_HEADER_SHA = '3da30319721715c1671b896941c4e9b897947e915f158ca0536ea976958aa5f3'


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Matched-source anchor differs: '+old[:80])
    return text.replace(old, new)


def prepare(source, own, audit, output):
    expected = json.loads(audit.read_text())
    if expected['source_commit'] != PIN:
        raise ValueError('Unexpected audited vendor revision')
    before = {}
    for name in ['mtcmos.c', 'mt_psci.c']:
        p = source/name
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != expected['files'][PREFIX+name]['sha256']:
            raise ValueError('Vendor source hash differs: '+name)
        before[name] = p.read_text()
    before['mtcmos.h'] = (source/'mtcmos.h').read_text()
    # Header is pinned separately: all offsets/bits are also compile-bound by
    # BUILD_BUG_ON assertions in the adapter against the actual matched header.
    header_sha = hashlib.sha256((source/'mtcmos.h').read_bytes()).hexdigest()
    if header_sha != HEADER_SHA:
        raise ValueError('Matched MTCMOS header hash differs')
    if hashlib.sha256((source/'mt_cpu_psci_ops.h').read_bytes()).hexdigest() != OPS_HEADER_SHA:
        raise ValueError('Matched CPU-ops header hash differs')
    after = dict(before)
    after['mtcmos.c'] += '\n#include "bounded_secondary_adapter.inc"\n'
    after['mtcmos.h'] = replace_once(after['mtcmos.h'], '#endif\n',
        'extern int spm_mtcmos_secondary_off_bounded(unsigned int cpu);\n'
        'extern int spm_mtcmos_secondary_off_check(unsigned long failures);\n#endif\n')
    t = after['mt_psci.c']
    t = replace_once(t, '#include <linux/init.h>',
                    '#include <linux/init.h>\n#include <linux/bitops.h>')
    start = t.index('static int mt_psci_cpu_kill(unsigned int cpu)')
    end = t.index('\n#ifdef CONFIG_CPU_IDLE', start)
    old = t[start:end]
    t = replace_once(t, old, '''/* Sticky failure evidence: generic __cpu_die only warns on errors.
 * A future handoff gate must consult this while CPU hotplug is serialized.
 * No interface here initiates hotplug or admits a handoff.
 */
static unsigned long mt_kexec_off_failed;
unsigned long mt_kexec_cpu_off_failures(void);
unsigned long mt_kexec_cpu_off_failures(void)
{
 return READ_ONCE(mt_kexec_off_failed);
}
int mt_kexec_secondary_off_gate(void);
int mt_kexec_secondary_off_gate(void)
{
 int ret = spm_mtcmos_secondary_off_check(READ_ONCE(mt_kexec_off_failed));
 return READ_ONCE(mt_kexec_off_failed) ? -EIO : ret;
}
static int mt_psci_cpu_kill(unsigned int cpu)
{
 int ret = spm_mtcmos_secondary_off_bounded(cpu);
 if (ret) set_bit(cpu, &mt_kexec_off_failed);
 return ret;
}
''')
    after['mt_psci.c'] = t
    output.mkdir()
    patch = []
    for name, content in after.items():
        (output/name).write_text(content)
        patch.extend(difflib.unified_diff(before[name].splitlines(True), content.splitlines(True),
                     fromfile='a/'+PREFIX+name, tofile='b/'+PREFIX+name))
    for name in ['bounded_secondary_off.h', 'bounded_secondary_adapter.inc']:
        (output/name).write_bytes((own/name).read_bytes())
    (output/'mt_cpu_psci_ops.h').write_bytes((source/'mt_cpu_psci_ops.h').read_bytes())
    (output/'Makefile').write_text('obj-m := cpu-off-preview.o\ncpu-off-preview-y := mtcmos.o mt_psci.o\n')
    (output/'candidate.patch').write_text(''.join(patch))
    report = {'scope': 'Compile-only matched MT8163 secondary-off patch; not deployed',
              'source_commit': PIN, 'source_mtcmos_header_sha256': header_sha,
              'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in output.iterdir() if p.is_file()},
              'limits': {'steps': 4096, 'timeout_ns': 100000000},
              'hardware_timing_qualified': False, 'whole_hotplug_bound_proved': False,
              'handoff_admitted': False,
              'limits_cannot_interrupt': ['firmware calls', 'regmap/bus accesses', 'clock callbacks'],
              'integration_remaining': ['call compiled final off gate before relocation',
                'serialize CPU hotplug and validate survivor CPU/secondary masks',
                'independent power-state readback', 'abort/recovery after partial shutdown']}
    (output/'source-report.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['source', 'own', 'audit', 'out']:
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.source, a.own, a.audit, a.out), indent=2))
