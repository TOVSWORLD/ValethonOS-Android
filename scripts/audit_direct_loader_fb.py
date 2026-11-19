#!/usr/bin/env python3
"""Offline exact-LK callback/libfdt emulation; never execute firmware on hardware."""
import argparse
import ctypes as c
import hashlib
import json
import struct
from pathlib import Path
from audit_trial_loader_contract import LK_SHA
from loader_fb_reservation import preserve


def audit(package,dtb,host_libfdt):
    from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
    raw=package.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=LK_SHA:raise ValueError('Exact original LK required')
    payload=raw[512:];word=lambda at:struct.unpack_from('<I',payload,at)[0]
    lib=c.CDLL(str(host_libfdt.resolve()));lib.fdt_open_into.argtypes=[c.c_void_p,c.c_void_p,c.c_int]
    lib.fdt_path_offset.argtypes=[c.c_void_p,c.c_char_p];lib.fdt_del_node.argtypes=[c.c_void_p,c.c_int]
    lib.fdt_getprop.argtypes=[c.c_void_p,c.c_int,c.c_char_p,c.POINTER(c.c_int)];lib.fdt_getprop.restype=c.c_void_p
    blob=dtb.read_bytes();fixed,change=preserve(blob)
    BASE=0x4bd00000;DT=0x48000000;DATA=0x50000000;STACK=0x51000000;END=0x52001000
    got=(word(0x25db8)+0x25c68+4)&0xffffffff
    def properties(data,path):
        b=c.create_string_buffer(data);node=lib.fdt_path_offset(b,path.encode())
        if node<0:raise ValueError('Preserved reservation missing')
        result={}
        for name in [b'reg',b'no-map',b'compatible']:
            n=c.c_int();ptr=lib.fdt_getprop(b,node,name,c.byref(n))
            result[name]=c.string_at(ptr,n.value) if ptr else None
        return result
    expected=properties(blob,change['old_path']);cases=[]
    for mode,source in [('original',blob),('preserved_rename',fixed),('removal_control_only',blob)]:
        buf=c.create_string_buffer(1024*1024)
        if lib.fdt_open_into(source,buf,len(buf)):raise ValueError('Cannot prepare FDT capacity')
        if mode=='removal_control_only':
            node=lib.fdt_path_offset(buf,change['old_path'].encode())
            if node<0 or lib.fdt_del_node(buf,node):raise ValueError('Control node removal failed')
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for at,size in [(BASE,0x100000),(DT,0x100000),(DATA,0x10000),(STACK,0x10000),(0x52000000,0x10000)]:uc.mem_map(at,size)
        uc.mem_write(BASE,payload);uc.mem_write(DT,buf.raw)
        # Synthetic runtime globals isolate callback behavior. They are NOT a
        # hardware boot-argument snapshot or proof of current framebuffer address.
        for at,value in [(word(got+word(0x25dbc)),DATA),
                         (word(got+word(0x25de0)),0x98600000),
                         (word(got+word(0x25de4)),0x1000000)]:uc.mem_write(at,struct.pack('<I',value))
        uc.reg_write(UC_ARM_REG_R0,DT);uc.reg_write(UC_ARM_REG_SP,STACK+0xfff0);uc.reg_write(UC_ARM_REG_LR,END|1)
        state={'returned':False,'instructions':0,'add_subnode_return':[]}
        signed=lambda v:v if v<0x80000000 else v-0x100000000
        def hook(u,address,size,user):
            off=address-BASE;state['instructions']+=1
            if address==END:state['returned']=True;u.emu_stop();return
            if off==0x25cf8:state['add_subnode_return'].append(signed(u.reg_read(UC_ARM_REG_R0)))
            if off in [0x44efc,0x45c04,0x45d10]:
                a,b,n=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
                if off!=0x44efc and n>1024*1024:raise ValueError('Memory service bound exceeded')
                if off==0x45c04:u.mem_write(a,bytes(u.mem_read(b,n)))
                if off==0x45d10:u.mem_write(a,bytes([b&255])*n)
                u.reg_write(UC_ARM_REG_R0,0 if off==0x44efc else a);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        uc.hook_add(UC_HOOK_CODE,hook);uc.emu_start(BASE+0x25c55,END,count=4000000)
        state['returned']=state['returned'] or uc.reg_read(UC_ARM_REG_PC)==END
        if not state['returned']:raise ValueError('Callback instruction bound exceeded')
        state.update(mode=mode,callback_return=signed(uc.reg_read(UC_ARM_REG_R0)))
        if mode=='original' and (state['callback_return']!=1 or state['add_subnode_return']!=[-2]):raise ValueError('Duplicate-node rejection not reproduced')
        if mode!='original' and (state['callback_return']!=0 or len(state['add_subnode_return'])!=1 or state['add_subnode_return'][0]<0):raise ValueError('Control callback failed')
        if mode=='preserved_rename':
            if properties(bytes(uc.mem_read(DT,1024*1024)),change['new_path'])!=expected:raise ValueError('Reservation property drift')
            state['reservation_properties_retained_after_callback']=True
        cases.append(state)
    return {'scope':'Exact LK memory-fixup callback/libfdt emulation; conditional offline proof, not observed hardware cause',
            'lk_sha256':LK_SHA,'input_dtb_sha256':hashlib.sha256(blob).hexdigest(),
            'audit_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'host_fixture_library_sha256':hashlib.sha256(host_libfdt.read_bytes()).hexdigest(),
            'host_library_role':'FDT fixture preparation/property comparison; LK callback/libfdt instructions run in emulator',
            'fix_changed_bytes':change['changed_bytes'],'cases':cases,
            'synthetic_runtime_globals':True,'firmware_hardware_executed':False,
            'hardware_reset_cause_proven':False,'all_controls_passed':True,
            'windows':[{'offset':hex(a),'bytes':b-a,'sha256':hashlib.sha256(payload[a:b]).hexdigest()}
                       for a,b in [(0x25c54,0x25dfc),(0x46d48,0x46e1e),(0x3dfd4,0x3dfe8),(0x3ec10,0x3ec22)]]}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['package','dtb','host-libfdt','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();result=audit(a.package,a.dtb,a.host_libfdt)
    a.output.write_text(json.dumps(result,indent=2)+'\n');print('Exact original/rename/removal callback controls passed; reservation retained.')
