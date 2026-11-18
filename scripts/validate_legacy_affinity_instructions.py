#!/usr/bin/env python3
"""Emulate the compiled ARM64 legacy callback, intercepting its firmware conduit."""
import argparse
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path


def validate(obj):
    from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
    from unicorn.arm64_const import (UC_ARM64_REG_X0, UC_ARM64_REG_X1,
      UC_ARM64_REG_X2, UC_ARM64_REG_X3, UC_ARM64_REG_X30, UC_ARM64_REG_SP, UC_ARM64_REG_PC)
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)
        (p/'layout.ld').write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.init.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.comment) *(.note*) *(.modinfo) } }')
        subprocess.run(['aarch64-linux-gnu-ld','--unresolved-symbols=ignore-all','-T',str(p/'layout.ld'),str(obj),'-o',str(p/'binding.elf')],capture_output=True,check=True)
        subprocess.run(['aarch64-linux-gnu-objcopy','-O','binary',str(p/'binding.elf'),str(p/'binding.bin')],check=True)
        code=(p/'binding.bin').read_bytes()
        output=subprocess.run(['aarch64-linux-gnu-nm',str(p/'binding.elf')],capture_output=True,text=True,check=True).stdout
        symbols={l.split()[2]:int(l.split()[0],16) for l in output.splitlines() if len(l.split())==3}
    cases=[(cpu,0,state) for cpu in range(4) for state in [0,1,2,-1]]
    cases += [(4,0,0),((1<<64)-1,0,0),(0,1,0),(0,(1<<64)-1,0)]
    results=[]
    for target,level,response in cases:
        u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
        u.mem_map(0x100000,0x100000);u.mem_write(0x100000,code)
        u.mem_map(0x300000,0x1000);u.mem_map(0x600000,0x10000);u.mem_map(0x900000,0x1000)
        u.mem_write(symbols['invoke_psci_fn'],struct.pack('<Q',0x300000))
        u.mem_write(symbols['mt8163_legacy_affinity_id'],struct.pack('<I',0x84000004))
        u.reg_write(UC_ARM64_REG_SP,0x60f000);u.reg_write(UC_ARM64_REG_X30,0x900000)
        u.reg_write(UC_ARM64_REG_X0,target);u.reg_write(UC_ARM64_REG_X1,level)
        calls=[]
        def hook(emu,pc,size,_):
            if pc==0x900000:emu.emu_stop()
            if pc==0x300000:
                a=[emu.reg_read(r) for r in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3]]
                if a!=[0x84000004,target,0,0]:raise ValueError('Unexpected compiled firmware arguments')
                calls.append(a);emu.reg_write(UC_ARM64_REG_X0,response&((1<<64)-1))
                emu.reg_write(UC_ARM64_REG_PC,emu.reg_read(UC_ARM64_REG_X30))
        def write(emu,access,address,size,value,_):
            if not (0x600000<=address and address+size<=0x610000):
                raise ValueError('Native callback wrote outside its stack')
        u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
        u.emu_start(symbols['mt8163_legacy_affinity_info'],0x900004,count=100)
        allowed=target<=3 and level==0
        expected=response if allowed else -22
        if (u.reg_read(UC_ARM64_REG_PC)!=0x900000 or len(calls)!=int(allowed) or
            u.reg_read(UC_ARM64_REG_X0)&0xffffffff!=expected&0xffffffff):
            raise ValueError('Compiled callback count/return/termination differs')
        results.append({'target':target,'level':level,'response':response,'conduit_calls':len(calls),'passed':True})
    return {'scope':'Actual ARM64 legacy callback; conduit stubbed; unused external symbols unresolved to zero',
      'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'cases':results,
      'real_firmware_calls':0,'hardware_qualified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['object','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();r=validate(a.object);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
