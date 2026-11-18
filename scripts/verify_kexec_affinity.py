#!/usr/bin/env python3
"""Reject affinity modules outside the reviewed query-only import/control set."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from verify_kexec_probe import inspect_module, RELEASE

ALLOWED = {'printk','__arm_smccc_smc','of_find_node_opts_by_path',
 '__of_device_is_compatible','of_device_is_compatible','of_machine_is_compatible',
 'of_property_read_string','of_property_read_variable_u32_array','of_get_cpu_node',
 'of_node_put','__of_find_all_nodes','of_find_compatible_node',
 'get_online_cpus','put_online_cpus','__cpu_possible_mask','__cpu_online_mask',
 '__sw_hweight64','__bitmap_weight','nr_cpu_ids','__per_cpu_offset','cpu_number',
 'debug_smp_processor_id','preempt_schedule','__stack_chk_fail','__stack_chk_guard',
 'strcmp'}


def verify(module,provider,objdump='aarch64-linux-gnu-objdump'):
    data=module.read_bytes();imports,meta,versions=inspect_module(data)
    if imports-ALLOWED or '__arm_smccc_smc' not in imports:
        raise ValueError('Unexpected query module imports: '+repr(imports-ALLOWED))
    magic=meta.get('vermagic','').split()
    if not magic or magic[0]!=RELEASE or not {'SMP','preempt','mod_unload','modversions','aarch64'}<=set(magic):
        raise ValueError('Query module ABI differs')
    table={}
    for l in provider.read_text().splitlines():
        f=l.split()
        if len(f)>=3 and f[2]=='vmlinux':table[f[1]]=int(f[0],16)
    for n in imports|{'module_layout'}:
        if n not in table or versions.get(n)!=table[n]:raise ValueError('CRC mismatch: '+n)
    dis=subprocess.run([objdump,'-dr',str(module)],capture_output=True,text=True,check=True).stdout
    ops=re.findall(r'^\s*[0-9a-f]+:\s+[0-9a-f]{8}\s+(\S+)',dis,re.M)
    if set(ops)&{'smc','hvc','msr','eret','dc','ic','tlbi','br','blr'}:
        raise ValueError('Unexpected privileged/control instruction in query module')
    calls=re.findall(r'R_AARCH64_CALL26\s+__arm_smccc_smc',dis)
    if len(calls)!=1:raise ValueError('Expected one statically reviewed SMC call site')
    return {'scope':'Query module ABI/import/instruction checks; not firmware safety proof',
      'module_sha256':hashlib.sha256(data).hexdigest(),'module_bytes':len(data),
      'imports':sorted(imports),'vermagic':meta['vermagic'],
      'all_required_crcs_match':True,'smccc_query_call_sites':len(calls),
      'firmware_queries':4,'query_fid':'0x84000004',
      'firmware_call_can_be_interrupted':False,'hardware_qualified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['module','provider','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();r=verify(a.module,a.provider);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
