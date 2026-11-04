#!/usr/bin/env python3
"""Validate analysis-only stubs and in-memory patch fixture. No device operations."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from itertools import product
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from audit_resident_loader_payload import BASE, SHA, GLOBALS, SECTORS, DEVICE, STOP, payload, machine

PLACEMENT = BASE + 0xbb8
FLAGS = 0xf80f0000
REGS = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11, UC_ARM_REG_R12, UC_ARM_REG_LR]


def object_code(path):
    b=path.read_bytes()
    if b[:7]!=b'\x7fELF\x01\x01\x01' or struct.unpack_from('<HH',b,16)!=(1,40):
        raise ValueError('ARM32 little-endian relocatable analysis object required')
    at=struct.unpack_from('<I',b,32)[0];size,count,names=struct.unpack_from('<HHH',b,46)
    sections=[struct.unpack_from('<10I',b,at+i*size) for i in range(count)]
    strings=sections[names];strings=b[strings[4]:strings[4]+strings[5]]
    section_names=[strings[x[0]:].split(b'\0')[0].decode() for x in sections]
    text_index=section_names.index('.text');t=sections[text_index];code=b[t[4]:t[4]+t[5]]
    if not code or len(code)>0xe00-0xbb8:raise ValueError('Observer exceeds bounded zero span')
    if any(x[1] in [4,9] and x[5] for x in sections):raise ValueError('Unresolved relocation')
    symbols={}
    for sec in sections:
        if sec[1]!=2:continue
        st=sections[sec[6]];st=b[st[4]:st[4]+st[5]]
        for a in range(sec[4],sec[4]+sec[5],sec[9]):
            name,value,sz,info,other,idx=struct.unpack_from('<IIIBBH',b,a)
            label=st[name:].split(b'\0')[0].decode()
            if label.startswith('observer_'):
                if idx!=text_index:raise ValueError('Observer symbol section mismatch')
                symbols[label]=value & ~1
    if set(symbols)!={'observer_mode','observer_read','observer_handoff'}:raise ValueError('Missing entry')
    return code,symbols


def bl(pc,target):
    d=target-(pc+4)
    if d & 1 or not -(1<<24)<=d<(1<<24):raise ValueError('Thumb BL range/alignment')
    v=d & ((1<<25)-1);s=v>>24;i1=(v>>23)&1;i2=(v>>22)&1
    h1=0xf000|(s<<10)|((v>>12)&1023)
    h2=0xd000|((1^(i1^s))<<13)|((1^(i2^s))<<11)|((v>>1)&2047)
    sign=(h1>>10)&1
    decoded=(sign<<24)|((1^(((h2>>13)&1)^sign))<<23)|((1^(((h2>>11)&1)^sign))<<22)|((h1&1023)<<12)|((h2&2047)<<1)
    if sign:decoded-=1<<25
    if pc+4+decoded!=target:raise ValueError('BL decode differs')
    return struct.pack('<HH',h1,h2)


def fixture(resident,code,symbols):
    if resident[0xbb8:0xe00]!=bytes(584):raise ValueError('Reserved tail differs')
    expected={0x330:bytes.fromhex('00f001fa'),0x72:bytes.fromhex('204b3046')}
    r=bytearray(resident)
    for off,name in [(0x330,'observer_mode'),(0x72,'observer_read')]:
        if r[off:off+4]!=expected[off]:raise ValueError('Archived patch anchor differs')
        r[off:off+4]=bl(BASE+off,PLACEMENT+symbols[name])
    r[0xbb8:0xbb8+len(code)]=code
    return bytes(r)


def validate(resident,code,symbols):
    altered=fixture(resident,code,symbols)
    # Adversarial video service clobbers integer registers/flags. Stack is left
    # intact, as required of a callable firmware service. No actual video runs.
    controls=[]
    for name,alignment,flag_pattern,boot_mode in product(symbols,[0,4],[0,FLAGS,0xa0050000],[0,2,99]):
        uc,state,word=machine(altered, lk_mode=boot_mode, suppress=(BASE+0x736,0x4bd3de68))
        sp=0x41fff000+alignment
        values=[0x40000000,0x42000000]+[0x12340000+i for i in range(2,len(REGS))]
        values[-1]=STOP|1
        uc.reg_write(UC_ARM_REG_SP,sp)
        for reg,value in zip(REGS,values):uc.reg_write(reg,value)
        uc.reg_write(UC_ARM_REG_CPSR,(uc.reg_read(UC_ARM_REG_CPSR)&~FLAGS)|flag_pattern)
        uc.mem_write(sp,struct.pack('<6I',DEVICE+0x4000,2048,8,0x55,0x33445566,0x11223344))
        seen=[];done=[]
        call=PLACEMENT+code.index(bytes.fromhex('9847'),symbols[name])
        def before(u,addr,size,data):
            if addr==call:
                assert u.reg_read(UC_ARM_REG_SP)%8==0
                seen.append([u.reg_read(x) for x in REGS[:3]])
            if addr==call+2:
                for i,reg in enumerate(REGS[:-1]):u.reg_write(reg,0xaabb0000+i)
                u.reg_write(UC_ARM_REG_CPSR,u.reg_read(UC_ARM_REG_CPSR)^FLAGS)
            if addr in [BASE+0x736,0x4bd3de68]:
                done.append(addr);u.emu_stop()
        uc.hook_add(UC_HOOK_CODE,before)
        uc.emu_start((PLACEMENT+symbols[name])|1,STOP,timeout=2000000,count=10000)
        got=[uc.reg_read(x) for x in REGS]
        expected=values[:]
        if name=='observer_read':expected[0]=values[6];expected[3]=BASE+0xb64
        assert got==expected,(name,got,expected)
        assert uc.reg_read(UC_ARM_REG_SP)==sp,name
        assert (uc.reg_read(UC_ARM_REG_CPSR)&FLAGS)==flag_pattern,name
        assert bytes(uc.mem_read(sp,24))==struct.pack('<6I',DEVICE+0x4000,2048,8,0x55,0x33445566,0x11223344)
        assert len(seen)==(1 if boot_mode==0 else 0),name
        if seen:
            if name=='observer_read':assert seen[0][1:]==[0x11223344,0x33445566]
            elif name=='observer_handoff':assert seen[0][1:]==values[:2]
            else:assert seen[0][:2]==values[:2]
        assert done==([] if name=='observer_read' else [BASE+0x736 if name=='observer_mode' else 0x4bd3de68])
        assert not state['writes']
        controls.append({'stub':name,'stack_mod8':alignment,'flags':hex(flag_pattern),'boot_mode':boot_mode,'added_video_calls':len(seen),'passed':True})
    # Execute the real patched final call, not just its stub entry.
    uc,state,word=machine(altered,suppress=(0x4bd3de68,))
    uc.mem_write(0x4bd3e524,bl(0x4bd3e524,PLACEMENT+symbols['observer_handoff']))
    uc.reg_write(UC_ARM_REG_SP,0x41fff000)
    uc.reg_write(UC_ARM_REG_R0,0x40000000);uc.reg_write(UC_ARM_REG_R1,0x42000000)
    reached=[]
    def final(u,addr,size,data):
        if addr==0x4bd3de68:
            reached.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR]])
            u.emu_stop()
    uc.hook_add(UC_HOOK_CODE,final)
    uc.emu_start(0x4bd3e525,STOP,timeout=2000000,count=10000)
    assert reached==[[0x40000000,0x42000000,0x4bd3e529]]
    # Full main and actual read hook run with the observers injected in RAM.
    for original,mode in [(0,0),(0,2),(4,0),(6,0)]:
        uc,state,word=machine(altered,original,mode)
        uc.emu_start(BASE,STOP,timeout=2000000,count=250000)
        assert state['app'] and not state['writes']
        assert state['cache_cleans']==[[0x4bd00000,0x100000]]
        assert word(0x4bd7c3a0)==(99 if original==4 else 2 if original==6 else mode)
    for name,target in [('boot','boot_x'),('recovery','recovery_x'),('lk','lk')]:
        for extra in [0,0x800,0x1000,0x100000000]:
            uc,state,word=machine(altered)
            for k,off in GLOBALS.items():
                uc.mem_write(BASE+off,struct.pack('<Q',SECTORS['MISC' if k=='g_misc' else k[2:]]))
            requested=SECTORS[name]*512+extra;sp=0x41fff000
            for reg,v in zip(REGS[:4],[DEVICE,0,requested&0xffffffff,requested>>32]):uc.reg_write(reg,v)
            uc.reg_write(UC_ARM_REG_SP,sp);uc.reg_write(UC_ARM_REG_LR,STOP|1)
            uc.mem_write(sp,struct.pack('<III',DEVICE+0x4000,2048,8))
            observed=[]
            def read_marker(u,addr,size,data):
                if addr==0x4bd44b3c:observed.append([u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)])
            uc.hook_add(UC_HOOK_CODE,read_marker)
            uc.emu_start(BASE+9,STOP,timeout=2000000,count=20000)
            expected=SECTORS[target if extra in [0,0x800] else name]*512+extra
            assert observed==[[expected>>32,expected&0xffffffff]]
            assert state['reads']==[[expected,2048,8]] and not state['writes']
            assert uc.reg_read(UC_ARM_REG_SP)==sp
    return controls,altered


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--object',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    code,symbols=object_code(a.object);resident=payload(a.archive)
    negative=[]
    for offset in [0x72,0x330,0xbb8]:
        changed=bytearray(resident);changed[offset]^=1
        try:fixture(bytes(changed),code,symbols)
        except ValueError:negative.append(hex(offset))
        else:raise ValueError('Altered input accepted')
    for target in [PLACEMENT+1,PLACEMENT+(1<<25)]:
        try:bl(PLACEMENT,target)
        except ValueError:negative.append('branch_'+hex(target))
        else:raise ValueError('Invalid branch accepted')
    controls,changed=validate(resident,code,symbols)
    report={'scope':'Analysis-only ARM relocatable object and in-memory archived fixture; modeled services, no tablet access','stub_bytes':len(code),'available_bytes':584,'placement':hex(PLACEMENT),'stub_sha256':hashlib.sha256(code).hexdigest(),'entries':{k:hex(PLACEMENT+v) for k,v in symbols.items()},'controls':controls,'actual_final_call_replay_passed':True,'full_main_mode_cases':4,'full_read_hook_cases':12,'negative_controls':negative,'modeled_existing_lk_cache_span_checked':True,'cache_visibility_qualified':False,'observer_packaged':False,'device_written':False,'hardware_qualified':False}
    a.output.write_text(json.dumps(report,indent=2)+'\n');print('Observer preservation controls passed')
