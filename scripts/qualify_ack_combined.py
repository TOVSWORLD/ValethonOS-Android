#!/usr/bin/env python3
"""Execute exact combined entry controls offline; never opens a tablet connection."""
import argparse, hashlib, json, struct, subprocess
from pathlib import Path
import unicorn as u
from unicorn import arm64_const as r
from build_ack_combined_entry import integrity_marker
from build_ack_kernel_hooks import line
from build_ack_trampoline import marker
from verify_ack_combined_bundle import verify

ROOT = Path(__file__).resolve().parents[1]
BASE, ENTRY, CONSOLE, WDT = 0x40000000, 0x42018000, 0x444bf000, 0x10007000

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def machine(image, metadata, header=(0x43474244, 0, 0), arm=True):
    m = u.Uc(u.UC_ARCH_ARM64, u.UC_MODE_ARM)
    m.ctl_set_cpu_model(r.UC_CPU_ARM64_A53)
    m.mem_map(BASE, 0x4000000); m.mem_map(CONSOLE, 65536); m.mem_map(WDT, 4096)
    m.mem_write(BASE, image); m.mem_write(0x42000000, metadata)
    m.mem_write(CONSOLE, struct.pack('<III', *header))
    m.reg_write(r.UC_ARM64_REG_PSTATE, 0x3c5)
    m.reg_write(r.UC_ARM64_REG_CP_REG, (1, 0, 3, 0, 0, 0))
    state = {'reset': False}
    def read(c, access, at, size, value, _):
        if at == WDT:
            v = struct.unpack('<I', c.mem_read(at, 4))[0] & 0xffffff
            c.mem_write(at, struct.pack('<I', v if arm else v ^ 1))
        if at == WDT + 4: c.mem_write(at, struct.pack('<I', 0xf800))
    def write(c, access, at, size, value, _):
        if at == WDT + 20: state['reset'] = True; c.emu_stop()
    m.hook_add(u.UC_HOOK_MEM_READ, read, begin=WDT, end=WDT+255)
    m.hook_add(u.UC_HOOK_MEM_WRITE, write, begin=WDT, end=WDT+255)
    return m, state

def qualify(bundle, kernel, vm_reports, out):
    verify(bundle/'report.json', kernel)
    manifest = json.loads((bundle/'report.json').read_text()); token = manifest['trial_id']
    image = (bundle/'image.bin').read_bytes()
    padded = image + bytes(manifest['image_memory_bytes']-len(image))
    metadata = (bundle/'metadata.bin').read_bytes(); checks = {}
    for name, corrupt, header, armed in [
        ('full_image', None, (0x43474244,0,0), True),
        ('corrupt_first_page', 123, (0x43474244,0,0), True),
        ('corrupt_last_padding_byte', len(padded)-1, (0x43474244,0,0), True),
        ('ring_wrap', None, (0x43474244,65500,65500), True),
        ('invalid_ring_header', None, (0,0,0), True),
        ('deadline_readback_failure', None, (0x43474244,0,0), False)]:
        data = bytearray(padded)
        if corrupt is not None: data[corrupt] ^= 1
        m, state = machine(bytes(data), metadata, header, armed)
        m.emu_start(ENTRY, BASE, timeout=120000000, count=2_000_000_000)
        pc = m.reg_read(r.UC_ARM64_REG_PC); raw = bytes(m.mem_read(CONSOLE,65536))
        if corrupt is not None:
            ok = state['reset'] and pc != BASE and integrity_marker(token,False) in raw and marker(token) not in raw
        elif not armed: ok = state['reset'] and pc != BASE and integrity_marker(token,True) not in raw
        else:
            ok = pc == BASE and not state['reset']
            if name == 'full_image':
                ok &= integrity_marker(token,True) in raw and marker(token) in raw
                ok &= all(m.reg_read(reg) == val for reg,val in [(r.UC_ARM64_REG_X0,0x42000000),(r.UC_ARM64_REG_X1,0),(r.UC_ARM64_REG_X2,0),(r.UC_ARM64_REG_X3,0)])
            if name == 'invalid_ring_header': ok &= raw == struct.pack('<III',0,0,0)+bytes(65524)
            if name == 'ring_wrap':
                start,size=struct.unpack_from('<II',raw,4)
                recovered=raw[12+start:]+raw[12:12+start]
                ok &= size==65524 and integrity_marker(token,True) in recovered and marker(token) in recovered
        checks[name]=bool(ok)
    # Execute actual Image prefix, including original record_mmu_state and
    # kernel page-table construction. Stop before MSR SCTLR enables the MMU.
    m,_=machine(padded,metadata)
    m.reg_write(r.UC_ARM64_REG_X0,0x42000000)
    m.emu_start(BASE,0x4126e5dc,timeout=10000000,count=1000000)
    raw=bytes(m.mem_read(CONSOLE,65536))
    checks['actual_prefix_before_mmu']=m.reg_read(r.UC_ARM64_REG_PC)==0x4126e5dc and all(line(token,s) in raw for s in ['linux_entry','before_mmu']) and line(token,'map_refused') not in raw
    pte=struct.unpack('<Q',m.mem_read(0x42020000+((CONSOLE>>12)&511)*8,8))[0]
    checks['normal_nc_console_page']=pte==0x600000444bf70b
    # Exercise the common ring writer directly: kernel arguments, callee-saved
    # registers, LR and x18 shadow-stack pointer must survive every marker.
    names=subprocess.check_output(['aarch64-linux-musl-nm','--defined-only',str(bundle/'hooks-private/hooks.elf')],text=True)
    symbols={v[2]:int(v[0],16) for row in names.splitlines() if len(v:=row.split())==3}
    m,_=machine(padded,metadata)
    preserved=[getattr(r,'UC_ARM64_REG_X'+str(i)) for i in list(range(9))+list(range(18,31))]
    expected={reg:0x51000000+i*16 for i,reg in enumerate(preserved)}
    for reg,value in expected.items():m.reg_write(reg,value)
    m.reg_write(r.UC_ARM64_REG_X15,symbols['msg_0'])
    m.reg_write(r.UC_ARM64_REG_X16,len(line(token,'linux_entry')))
    m.reg_write(r.UC_ARM64_REG_X17,0x42000000)
    m.emu_start(symbols['append_ring'],0x42000000,count=10000)
    checks['kernel_arguments_scs_callee_saved_and_lr_preserved']=all(m.reg_read(reg)==value for reg,value in expected.items()) and line(token,'linux_entry') in bytes(m.mem_read(CONSOLE,65536))
    m,state=machine(padded,metadata)
    m.reg_write(r.UC_ARM64_REG_X2,0) # impossible idmap root must fail closed
    m.emu_start(manifest['kernel_hooks']['patches'][1]['hook'],BASE,count=10000)
    raw=bytes(m.mem_read(CONSOLE,65536))
    checks['invalid_idmap_root_resets_without_entering_linux']=state['reset'] and line(token,'map_refused') in raw and line(token,'before_mmu') not in raw
    # Each independent QEMU run boots this exact instrumented Image to enforcing
    # PID1 with real MMU transitions. Its integrity stub is not part of that run.
    vms=[json.loads(p.read_text()) for p in vm_reports]
    checks['qemu_both_exception_level_paths']=len(vms)==2 and {v['virtualization'] for v in vms}=={'off','on'} and all(v['passed'] and v['image_sha256']==digest(bundle/'image.bin') and v['stages_in_order'] and all(v['stages'].values()) and v['enforcing_pid1_filesystem_probe'] for v in vms)
    sources=['scripts/qualify_ack_combined.py','scripts/build_ack_kernel_hooks.py','scripts/build_ack_combined_entry.py','scripts/verify_ack_combined_bundle.py','scripts/validate_ack_combined_vm.py','projects/firetabs-android/native-kexec/combined_sha256.c','projects/firetabs-android/native-kexec/ack_trampoline.S']
    result=dict(scope='Offline exact combined candidate qualification; no tablet commands',all_tests_passed=all(checks.values()),tests_skipped=0,checks=checks,image_sha256=digest(bundle/'image.bin'),metadata_sha256=digest(bundle/'metadata.bin'),source_sha256={p:digest(ROOT/p) for p in sources},vm_reports_sha256=[digest(p) for p in vm_reports],hardware_execution=False,target_kernel_boot_proven=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    if not result['all_tests_passed']: raise ValueError('Combined qualification failed: '+','.join(k for k,v in checks.items() if not v))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,required=True);p.add_argument('--kernel',type=Path,required=True)
    p.add_argument('--vm-report',type=Path,action='append',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(qualify(a.bundle,a.kernel,a.vm_report,a.output),indent=2))
