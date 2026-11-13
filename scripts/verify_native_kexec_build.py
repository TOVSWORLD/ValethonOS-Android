#!/usr/bin/env python3
"""Check native syscall wiring and linked handoff gates; never runs a device."""
import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from verify_kexec_source_integration import verify

CONFIG_SHA='71184d29b986824d086f9a0cb0ce6bb00d2d63723e0476a49d3381cb00603ac9'


def mapped_bytes(elf,address,size):
    off=struct.unpack_from('<Q',elf,32)[0];stride,count=struct.unpack_from('<HH',elf,54)
    if stride!=56 or off+stride*count>len(elf):raise ValueError('Invalid ELF program headers')
    matches=[]
    for i in range(count):
        kind,flags,file_at,virtual,physical,file_size,mem_size,alignment=struct.unpack_from('<II6Q',elf,off+i*stride)
        if kind==1 and virtual<=address and address+size<=virtual+file_size:
            at=file_at+address-virtual
            if at+size>len(elf):raise ValueError('ELF load mapping outside file')
            matches.append(elf[at:at+size])
    if len(matches)!=1:raise ValueError('Unique file-backed syscall-table mapping required')
    return matches[0]


def check(build, expected_config_sha256=CONFIG_SHA):
    result=verify(build)
    if result['artifacts']['.config']['sha256']!=expected_config_sha256:raise ValueError('Exact native configuration required')
    elf=(build/'vmlinux').read_bytes()
    nm=subprocess.run(['aarch64-linux-gnu-nm','--defined-only',str(build/'vmlinux')],capture_output=True,text=True,check=True).stdout
    syms={f[2]:int(f[0],16) for l in nm.splitlines() if len(f:=l.split())==3}
    for name in ['sys_call_table','sys_kexec_load','kernel_kexec','sys_reboot']:
        if name not in syms:raise ValueError('Native kexec/reboot symbol missing: '+name)
    pointer=struct.unpack('<Q',mapped_bytes(elf,syms['sys_call_table']+104*8,8))[0]
    if pointer!=syms['sys_kexec_load']:raise ValueError('ARM64 syscall104 does not dispatch to kexec_load')
    def dis(name):return subprocess.run(['aarch64-linux-gnu-objdump','-d','--disassemble='+name,str(build/'vmlinux')],capture_output=True,text=True,check=True).stdout
    machine=dis('machine_kexec')
    if '<mt_kexec_secondary_off_gate>' not in machine:
        if '<mt8163_kexec_final_gate>' not in machine:raise ValueError('Native final CPU gate call absent')
        machine+=dis('mt8163_kexec_final_gate')
    if '<mt_kexec_secondary_off_gate>' not in machine:raise ValueError('Final gate cannot reach off-state check')
    # GNU objdump may select SyS_reboot as the canonical syscall alias.
    reboot='\n'.join(dis(n) for n in syms if n in ['sys_reboot','SyS_reboot'] and syms[n]==syms['sys_reboot'])
    if '<kernel_kexec>' not in reboot:raise ValueError('Reboot syscall does not call native kexec')
    for marker in [b'valethon-kexec\0',b'KXHANDOFF init_reboot_route=1',b'no firmware fallback']:
        if marker not in elf:raise ValueError('Orderly-route namespace/diagnostic absent')
    result.update(scope='Linked native kexec syscall/CPU-gate/orderly-route checks; not boot acceptance',
      arm64_syscall_104_is_kexec_load=True,native_final_gate_reaches_off_check=True,
      orderly_reboot_namespace_linked=True,handoff_gate_wired=True,
      failed_jump_logging_is_pretrial_blocker=False,kernel_boot_tested=False,hardware_execution=False)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=check(a.build);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
