#!/usr/bin/env python3
"""Execute the actual query object's ARM64 control flow with stubbed kernel/SMC APIs.
No firmware calls occur: __arm_smccc_smc is intercepted before execution.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path


def validate(obj):
    from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
    from unicorn.arm64_const import (UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,
      UC_ARM64_REG_X3,UC_ARM64_REG_X4,UC_ARM64_REG_X5,UC_ARM64_REG_X6,
      UC_ARM64_REG_X7,UC_ARM64_REG_X30,UC_ARM64_REG_SP,UC_ARM64_REG_PC,
      UC_ARM64_REG_SP_EL0,UC_ARM64_REG_TPIDR_EL1)
    regs=[UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3,
          UC_ARM64_REG_X4,UC_ARM64_REG_X5,UC_ARM64_REG_X6,UC_ARM64_REG_X7]
    undefined=subprocess.run(['aarch64-linux-gnu-nm','-u',str(obj)],capture_output=True,text=True,check=True).stdout
    names=sorted(l.split()[-1] for l in undefined.splitlines() if l.split())
    data={'__cpu_possible_mask':0x400000,'__cpu_online_mask':0x400100,
          'cpu_number':0x400200,'__stack_chk_guard':0x400300}
    addresses={n:data.get(n,0x300000+i*0x100) for i,n in enumerate(names)}
    functions={v:k for k,v in addresses.items() if k not in data}
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)
        (p/'layout.ld').write_text('SECTIONS { . = 0x100000; .text : { *(.init.text) *(.text*) *(.exit.text) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.comment) *(.note*) *(.modinfo) } }')
        args=['aarch64-linux-gnu-ld','-T',str(p/'layout.ld'),'-e','init_module',str(obj),'-o',str(p/'query.elf')]
        args+=['--defsym=%s=0x%x'%(n,v) for n,v in addresses.items()]
        subprocess.run(args,capture_output=True,check=True)
        subprocess.run(['aarch64-linux-gnu-objcopy','-O','binary',str(p/'query.elf'),str(p/'query.bin')],check=True)
        code=(p/'query.bin').read_bytes()
        symbols=subprocess.run(['aarch64-linux-gnu-nm',str(p/'query.elf')],capture_output=True,text=True,check=True).stdout
        entry=int(next(l.split()[0] for l in symbols.splitlines() if l.endswith(' init_module')),16)
    cases=[('compatible-score',{},4),('other-current-cpu',{'current':2},4),
      ('unsupported-query',{'states':[-1]*4},4),('state-changing-fid-rejected',{'fid':0x84000002},0),
      ('wrong-board',{'board':False},0),('wrong-conduit',{'method':'hvc'},0),
      ('wrong-cells',{'cells':2},0),('missing-cpu-node',{'missing_cpu':2},0),
      ('wrong-cpu-reg',{'bad_reg':2},0),('wrong-topology',{'possible':7},0)]
    results=[]
    for name,changes,expected in cases:
        c={'board':True,'compat':32767,'fid':0x84000004,'method':'smc','cells':1,
           'missing_cpu':None,'bad_reg':None,'possible':15,'online':15,'current':0,
           'states':[0,0,0,0]};c.update(changes)
        uc=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
        for addr in [0x100000,0x300000,0x400000,0x500000,0x600000,0x700000]:uc.mem_map(addr,0x10000)
        uc.mem_map(0x900000,0x1000);uc.mem_write(0x100000,code)
        uc.mem_write(0x400000,struct.pack('<Q',c['possible']))
        uc.mem_write(0x400100,struct.pack('<Q',c['online']))
        uc.mem_write(0x400200,struct.pack('<I',c['current']))
        uc.mem_write(0x400300,struct.pack('<Q',0x123456789abcdef))
        uc.mem_write(0x700000,c['method'].encode()+b'\0')
        uc.reg_write(UC_ARM64_REG_SP,0x60f000);uc.reg_write(UC_ARM64_REG_SP_EL0,0x500000)
        uc.reg_write(UC_ARM64_REG_TPIDR_EL1,0);uc.reg_write(UC_ARM64_REG_X30,0x900000)
        calls=[];logs=[];native_writes=[];locks=[0]
        def string(at):
            b=bytearray()
            while len(b)<512:
                v=uc.mem_read(at+len(b),1)[0]
                if not v:return b.decode()
                b.append(v)
            raise ValueError('Unterminated emulated string')
        def hook(emulator,pc,size,_):
            if pc==0x900000:emulator.emu_stop();return
            if pc not in functions:return
            fn=functions[pc];a=[emulator.reg_read(r) for r in regs];ret=0
            if fn=='of_machine_is_compatible':ret=32767 if c['board'] else 0
            elif fn=='of_find_node_opts_by_path':ret={'/psci':0x800010,'/cpus':0x800020}.get(string(a[0]),0)
            elif fn=='of_property_read_string':emulator.mem_write(a[2],struct.pack('<Q',0x700000))
            elif fn=='of_device_is_compatible':ret=c['compat']
            elif fn=='strcmp':ret=0 if string(a[0])==string(a[1]) else 1
            elif fn=='of_get_cpu_node':ret=0 if a[0]==c['missing_cpu'] else 0x800100+a[0]*0x100
            elif fn=='of_property_read_variable_u32_array':
                prop=string(a[1])
                if prop=='affinity_info':value=c['fid']
                elif prop=='#address-cells':value=c['cells']
                elif prop=='reg':
                    value=(a[0]-0x800100)//0x100
                    if value==c['bad_reg']:value+=1
                else:raise ValueError('Unexpected property '+prop)
                emulator.mem_write(a[2],struct.pack('<I',value));ret=1
            elif fn=='__sw_hweight64':ret=a[0].bit_count()
            elif fn=='get_online_cpus':locks[0]+=1
            elif fn=='put_online_cpus':locks[0]-=1
            elif fn=='printk':logs.append((string(a[0]),a[1:4]))
            elif fn=='__arm_smccc_smc':
                if a[0]!=0x84000004 or a[1] not in range(4) or any(a[2:]):
                    raise ValueError('Compiled code attempted unexpected firmware call '+repr(a))
                calls.append(a)
                stack=emulator.reg_read(UC_ARM64_REG_SP)
                result_ptr=struct.unpack('<Q',emulator.mem_read(stack,8))[0]
                emulator.mem_write(result_ptr,struct.pack('<4Q',c['states'][a[1]]&((1<<64)-1),0,0,0))
            elif fn=='preempt_schedule':raise ValueError('Unexpected schedule during controlled test')
            elif fn=='__stack_chk_fail':raise ValueError('Compiled stack protector failed')
            else:raise ValueError('Unmodeled external call '+fn)
            emulator.reg_write(UC_ARM64_REG_X0,ret&((1<<64)-1))
            emulator.reg_write(UC_ARM64_REG_PC,emulator.reg_read(UC_ARM64_REG_X30))
        def write(emulator,access,address,size,value,_):
            native_writes.append(address)
            if not (0x600000<=address<0x610000 or address==0x500010):
                raise ValueError('Unexpected native write 0x%x'%address)
        uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_WRITE,write)
        uc.emu_start(entry,0x900004,count=10000)
        if uc.reg_read(UC_ARM64_REG_PC)!=0x900000:raise ValueError('Compiled initializer did not finish')
        if len(calls)!=expected or (expected and [a[1] for a in calls]!=list(range(4))):
            raise ValueError('Wrong compiled firmware query count/order in '+name)
        if locks[0]!=0 or struct.unpack('<I',uc.mem_read(0x500010,4))[0]!=0:
            raise ValueError('Compiled code left hotplug lock/preempt count held')
        if expected:
            if len(logs)!=6 or logs[0][1][0]!=c['current']:raise ValueError('Missing compiled report')
            summary=logs[-1][1]
            if summary[0]!=sum(0<=v<=2 for v in c['states']) or summary[1]!=(c['states'][c['current']]==0):
                raise ValueError('Compiled query classification differs')
        elif calls:raise ValueError('Rejected DT still queried firmware')
        results.append({'case':name,'queries':len(calls),'completed':True,'native_writes':'stack/thread-preempt only'})
    return {'scope':'Actual compiled ARM64 query initializer emulation; all external kernel/SMC APIs stubbed',
      'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'cases':results,
      'real_firmware_calls':0,'hardware_qualified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--object',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=validate(a.object);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
