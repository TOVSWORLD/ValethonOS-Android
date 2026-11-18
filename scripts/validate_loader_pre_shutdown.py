#!/usr/bin/env python3
"""Analysis-only pre-shutdown bridge replay; firmware never exported or installed."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_CPSR, UC_ARM_REG_LR, UC_ARM_REG_SP, UC_ARM_REG_PC
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from validate_loader_complete import Complete, raw_elf, elf, REGS, BASE
from validate_loader_allocator import EXPECTED, POOL
from validate_loader_physical import STOP
from loader_checkpoint_record import decode
import retained_log_mailbox as mailbox

SITE = 0x4bd3e3e8


def validate(module, bootstrap, lkpath, payload, packed=None):
    lk = lkpath.read_bytes()
    assert hashlib.sha256(lk).hexdigest() == EXPECTED
    body = lk[512:]
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    before = list(md.disasm(body[0x3e3e8:0x3e400], SITE))
    assert before[0].mnemonic == 'ldr.w' and before[0].op_str == 'r3, [pc, #0x720]'
    assert any(i.address == 0x4bd3e3f8 and i.mnemonic == 'blx' and i.op_str == '#0x4bd3c76c' for i in before)
    assert any(i.address == 0x4bd3e3f6 and i.mnemonic == 'bne' and i.op_str == '#0x4bd3e3fc' for i in before)
    assert any(i.address == 0x4bd3e3fc and i.mnemonic == 'bl' for i in before)
    assert all('lr' not in i.op_str for i in before if i.address < 0x4bd3e3fc)
    # Execute the actual ARM mask helper independently, without the allocator's
    # modeled IRQ-service intercept. This is instruction proof, not trial state.
    u = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    u.mem_map(0x4bd00000, 0x80000); u.mem_write(0x4bd00000, body)
    u.mem_map(0x50000000, 0x10000)
    u.reg_write(UC_ARM_REG_CPSR, 0x13); u.reg_write(UC_ARM_REG_LR, STOP)
    u.emu_start(0x4bd3c76c, STOP, count=10)
    assert u.reg_read(UC_ARM_REG_CPSR)&0x80
    segments, _ = elf(module, ('lfo_frame_dispatch', 'lfo_state_bytes'))
    _, symbols = raw_elf(module)
    full = payload.read_bytes()
    assert hashlib.sha256(full).hexdigest() == 'e10fdf770a5be2c2adc3cce0d03b8e296eac3b31e18ebdce5b56dc5491f4e7e8'
    resident = full[0xa00:0x1800]

    def fixture(cache=1):
        f = Complete(segments, symbols, lk, bootstrap, resident, packed=packed)
        f.cache_enabled = cache; f.u.mem_write(0x4bd7e2ed, bytes([cache]))
        return f

    def point(f, irq=False):
        u = f.u
        regs = [0xabc00000+i for i in range(13)]; regs[11] = 0x40080000
        for r,v in zip(REGS,regs): u.reg_write(r,v)
        sp = 0x41fff000; u.mem_write(sp+8, struct.pack('<I', 0x48000000))
        cpsr = 0x980a00b3 if irq else 0x980a0033
        u.reg_write(UC_ARM_REG_CPSR,cpsr); u.reg_write(UC_ARM_REG_SP,sp)
        u.reg_write(UC_ARM_REG_LR,STOP|1)
        def stop(uc, at, n, data):
            if at == SITE+4: uc.emu_stop()
        hook = u.hook_add(UC_HOOK_CODE, stop)
        u.emu_start(SITE|1, STOP, count=80000000, timeout=40000000)
        u.hook_del(hook)
        expected = list(regs); expected[3] = struct.unpack_from('<I',body,0x3eb0c)[0]
        assert u.reg_read(UC_ARM_REG_PC) == SITE+4
        assert [u.reg_read(r) for r in REGS] == expected and u.reg_read(UC_ARM_REG_SP) == sp
        assert u.reg_read(UC_ARM_REG_CPSR)&0xf80f00c0 == cpsr&0xf80f00c0
        # Inline BL necessarily changes LR. Both original fall-through paths
        # overwrite LR with a BL/BLX before reading it; it is not live here.
        assert u.reg_read(UC_ARM_REG_LR) == (SITE+4)|1

    cases = []
    for cache in [0,1]:
        f = fixture(cache); point(f)
        latest = mailbox.inspect(f.stable,f.nonce,f.prefix)['latest']
        record = decode(latest['payload'],f.nonce,f.prefix)
        assert latest['sequence'] == 3 and record['stage'] == 'pre_shutdown'
        assert record['kernel_entry'] == 0x40080000 and record['dt_address'] == 0x48000000
        assert not record['kernel_entry_proved']
        commands = [v&63 for off,v in f.writes if off==0x34]
        assert commands == ([13]*12 if cache==0 else [13,6,13,13,13]*6), (cache,commands)
        cases.append('late_first_initialization_cache_'+str(cache))
    f = fixture(0); f.native_read(irq_disabled=True)
    assert not f.loaded and not f.writes
    point(f); assert mailbox.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3
    cases.append('unsafe_read_no_io_then_one_safe_late_initialization')
    f = fixture(0); f.native_read(); point(f)
    assert mailbox.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==4
    cases.append('earlier_read_then_pre_shutdown_without_reinitialization')
    f = fixture(); point(f,True)
    assert not f.loaded and not f.writes and not f.events
    cases.append('masked_pre_shutdown_still_no_io')
    for device in [0,1,0xfffffff0]:
        f = fixture(); f.u.mem_write(0x4bd7e038,struct.pack('<I',device)); point(f)
        assert not f.loaded and not f.writes and not f.events
    cases.append('invalid_device_global_stops_before_blob_read')
    f = fixture(2); point(f); assert not f.writes
    events=len(f.events); point(f); assert len(f.events)==events and not f.writes
    cases.append('invalid_identity_cache_latches_without_storage_writes')
    f = fixture(); f.image[12*1024*1024]^=1; point(f)
    assert not f.loaded and not f.writes
    events=len(f.events); point(f); assert len(f.events)==events and not f.writes
    cases.append('module_hash_failure_not_retried')
    return {'scope':'Actual archived mask helper and linked pre-shutdown hook/module replay; controller/block/clock/heap/IRQ services/cache effects/prefix digest modeled',
            'cases':cases,'case_count':len(cases),'original_irq_mask_helper_executed':True,
            'new_site':hex(SITE),'old_site':hex(0x4bd3e524),'original_literal_load_replayed':True,
            'r0_r12_sp_apsr_preserved_except_original_r3_load':True,
            'lr_replaced_by_inline_bl_dead_until_next_original_call':True,
            'snapshot_stage':'pre_shutdown','kernel_entry_proved':False,
            'state_bytes':f.state_size,
            'module_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),
            'bootstrap_sha256':hashlib.sha256(bootstrap.read_bytes()).hexdigest(),
            'packed_candidate_sha256':hashlib.sha256((packed/'boot-full.img').read_bytes()).hexdigest() if packed else None,
            'device_accessed':False,'physical_candidate_ready':False,'hardware_acceptance':False}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for key in ['module','bootstrap','lk','payload','output']:p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--packed',type=Path)
    a = p.parse_args(); result = validate(a.module,a.bootstrap,a.lk,a.payload,a.packed)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print('Pre-shutdown replay controls passed:',result['case_count'])
