#!/usr/bin/env python3
"""Prepare the exact-source legacy affinity binding; never executes firmware."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

SHA = '142416b4d183500269fc8fa3adfb78183ac889be29cdd9f9eee4fdae8fd4b781'


def prepare(source, policy, output):
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('Matched PSCI source hash differs')
    before = raw.decode()
    declaration = 'static int __init psci_0_1_init(struct device_node *np)'
    helpers = '''#include "legacy_affinity_policy.h"
static u32 mt8163_legacy_affinity_id;
static int mt8163_legacy_affinity_info(unsigned long target, unsigned long level)
{
 if (!kxaff_query_args(target, level)) return -EINVAL;
 return invoke_psci_fn(mt8163_legacy_affinity_id, target, level, 0);
}

'''
    after = before.replace(declaration, helpers+declaration, 1)
    start = after.index(declaration)
    anchor = '\nout_put_node:\n'
    at = after.index(anchor, start)
    binding = '''
 /* MT8163's observed legacy DT provides an SMC32 affinity-info ID. Do not
  * silently substitute the standard SMC64 v0.2 ID or probe during boot.
  * Actual firmware support must be qualified separately.
  */
 if (!of_property_read_u32(np, "affinity_info", &id) &&
     kxaff_legacy_allowed(!!of_machine_is_compatible("mediatek,mt8163"),
       !!of_device_is_compatible(np, "arm,psci"),
       psci_ops.conduit == PSCI_CONDUIT_SMC, id)) {
  mt8163_legacy_affinity_id = id;
  psci_ops.affinity_info = mt8163_legacy_affinity_info;
 }
'''
    after = after[:at] + '\n'+binding + after[at:]
    output.mkdir()
    (output/'psci.c').write_text(after)
    (output/'legacy_affinity_policy.h').write_bytes(policy.read_bytes())
    (output/'binding.patch').write_text(''.join(difflib.unified_diff(
        before.splitlines(True), after.splitlines(True),
        fromfile='a/drivers/firmware/psci.c', tofile='b/drivers/firmware/psci.c')))
    report = {'scope':'Offline legacy affinity binding; firmware support untested',
              'source_sha256':SHA, 'patched_sha256':hashlib.sha256(after.encode()).hexdigest(),
              'policy_sha256':hashlib.sha256(policy.read_bytes()).hexdigest(),
              'fid':'0x84000004', 'conduit':'smc', 'target_range':[0,3],
              'lowest_affinity_level':0, 'boot_time_firmware_probe':False,
              'hardware_qualified':False}
    (output/'binding-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['source','policy','out']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();print(json.dumps(prepare(a.source,a.policy,a.out),indent=2))
