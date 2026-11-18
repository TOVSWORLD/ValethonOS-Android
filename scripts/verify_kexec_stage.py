#!/usr/bin/env python3
"""Independent artifact checks for the prepare-only module and native client."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_kexec_probe import inspect_module, RELEASE

ALLOWED_IMPORTS = {
 '__alloc_pages_nodemask','__arch_copy_from_user','__arch_copy_to_user',
 '__check_object_size','__free_pages','__stack_chk_fail','__stack_chk_guard',
 'capable','clear_bit','clear_page','contig_page_data','copy_page','crc32_le',
 'kfree','kmalloc_caches','kmem_cache_alloc_trace','memcpy','memset',
 'memstart_addr','misc_deregister','misc_register','mutex_lock','mutex_trylock',
 'mutex_unlock','preempt_schedule','printk','security_kernel_read_file','set_bit','totalram_pages',
}
FORBIDDEN_SYMBOLS = {'machine_kexec','__cpu_soft_restart','arm64_relocate_new_kernel',
                    '__hyp_shim_vectors','cpu_soft_restart','machine_shutdown',
                    'kernel_restart_prepare','migrate_to_reboot_cpu','cpu_down',
                    'cpu_hotplug_enable','__hyp_set_vectors'}

def symbols(data):
    off=struct.unpack_from('<Q',data,40)[0];stride,count,_=struct.unpack_from('<HHH',data,58)
    headers=[struct.unpack_from('<IIQQQQIIQQ',data,off+i*stride) for i in range(count)]
    result={}
    for h in headers:
        if h[1]!=2:continue
        strings=headers[h[6]];names=data[strings[4]:strings[4]+strings[5]]
        for at in range(h[4],h[4]+h[5],24):
            name,info,_,section,value,size=struct.unpack_from('<IBBHQQ',data,at)
            n=names[name:].split(b'\0',1)[0].decode()
            if n and section and section<count:
                target=headers[section]
                result[n]=data[target[4]+value:target[4]+value+size]
    return result

def refusal_stub(code):
    # GCC13/AArch64: mov w0,#-EOPNOTSUPP; ret. No arbitrary entry can be reached.
    if code != struct.pack('<II',0x12800bc0,0xd65f03c0):
        raise ValueError('Execution refusal stub differs')

def validate_imports(imports):
    if imports-ALLOWED_IMPORTS:
        raise ValueError('Unexpected staging imports: '+', '.join(sorted(imports-ALLOWED_IMPORTS)))

def verify(module, provider, client, objdump='aarch64-linux-musl-objdump'):
    data=module.read_bytes();imports,meta,versions=inspect_module(data);validate_imports(imports)
    magic=meta.get('vermagic','').split()
    if not magic or magic[0]!=RELEASE or not {'SMP','preempt','mod_unload','modversions','aarch64'}<=set(magic):
        raise ValueError('Wrong module ABI')
    table={}
    for row in provider.read_text().splitlines():
        fields=row.split()
        if len(fields)>=3 and fields[2]=='vmlinux':table[fields[1]]=int(fields[0],16)
    for name in imports|{'module_layout'}:
        if name not in versions or name not in table or versions[name]!=table[name]:
            raise ValueError('Missing/mismatched CRC: '+name)
    defined=symbols(data)
    if FORBIDDEN_SYMBOLS & (defined.keys()|imports):
        raise ValueError('Shutdown/restart symbol linked')
    refusal_stub(defined.get('kernel_kexec',b''))
    dis=subprocess.run([objdump,'-d',str(module)],capture_output=True,text=True,check=True).stdout
    ops=re.findall(r'^\s*[0-9a-f]+:\s+[0-9a-f]{8}\s+(\S+)',dis,re.M)
    forbidden=set(ops)&{'hvc','smc','msr','eret','tlbi','dc','ic','br','blr'}
    if forbidden:raise ValueError('Forbidden control/privileged instruction: '+repr(forbidden))
    b=client.read_bytes()
    if len(b)<64 or b[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<HH',b,16)!=(2,183):
        raise ValueError('Native static AArch64 client required')
    offset=struct.unpack_from('<Q',b,32)[0];stride,count=struct.unpack_from('<HH',b,54)
    if stride!=56 or offset+stride*count>len(b):raise ValueError('Invalid client program headers')
    programs=[struct.unpack_from('<IIQQQQQQ',b,offset+i*stride) for i in range(count)]
    if any(h[0]==3 for h in programs):
        raise ValueError('Client has a dynamic interpreter')
    if any(h[5]>h[6] or h[2]+h[5]>len(b) for h in programs if h[0]==1):
        raise ValueError('Invalid client load segment')
    entry=struct.unpack_from('<Q',b,24)[0]
    if not any(h[0]==1 and h[1]&1 and h[5] and h[3]<=entry<h[3]+h[6] for h in programs):
        raise ValueError('No executable client entry segment')
    return {'scope':'Prepare-only staging artifact verification; not hardware acceptance',
        'module_sha256':hashlib.sha256(data).hexdigest(),'module_bytes':len(data),
        'client_sha256':hashlib.sha256(b).hexdigest(),'client_bytes':len(b),
        'vermagic':meta['vermagic'],'imports':sorted(imports),'versioned_symbols':len(imports)+1,
        'all_crcs_match_provider':True,'execution_stub_returns_eopnotsupp':True,
        'restart_or_shutdown_symbols_linked':False,'forbidden_privileged_or_indirect_instructions':[],
        'instruction_count':len(ops),'client_static_aarch64':True,
        'loaded_on_tablet':False,'kernel_handoff_implemented':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['module','provider','client','output']:p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--objdump',default='aarch64-linux-musl-objdump')
    a=p.parse_args();r=verify(a.module,a.provider,a.client,a.objdump);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
