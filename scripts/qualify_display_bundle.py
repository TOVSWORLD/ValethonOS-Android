#!/usr/bin/env python3
"""Qualify unmodified display Image entry/return safeguards offline."""
import hashlib,json,struct
from pathlib import Path
from unicorn import arm64_const as r
from qualify_ack_combined import machine,BASE,ENTRY,CONSOLE
from build_ack_combined_entry import integrity_marker
from build_ack_trampoline import marker
from verify_display_bundle import verify
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def qualify(bundle,kernel,baseline,component,vm_reports,out):
    nonce=(component/'trial-nonce-private.bin').read_bytes()
    verify(bundle/'report.json',kernel,baseline,component,nonce=nonce)
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
    vms=[json.loads(p.read_text()) for p in vm_reports]
    checks['both_vm_modes_enforcing']=len(vms)==2 and {v['virtualization'] for v in vms}=={'off','on'} and all(v['passed'] and v['kernel_sha256']==digest(bundle/'image.bin') and v['selinux_enforcing'] and v.get('display_kernel_snapshot_probe') is True and v['tablet_commands'] is False for v in vms)
    sources=['scripts/qualify_display_bundle.py','scripts/qualify_ack_combined.py','scripts/build_ack_combined_entry.py','scripts/verify_display_bundle.py','scripts/prepare_display_bundle.py','scripts/display_kernel_contract.py','scripts/display_dtb_profile.py','scripts/validate_lab_policy_vm.py','tests/fixtures/lab_policy_vm_probe.c','projects/firetabs-android/diagnostic-usb/display_errors.h','scripts/receive_display_errors.py','projects/firetabs-android/native-kexec/combined_sha256.c','projects/firetabs-android/native-kexec/ack_trampoline.S']
    result=dict(scope='Offline unmodified display entry and enforcing VM qualification',all_tests_passed=all(checks.values()),tests_skipped=0,checks=checks,image_sha256=digest(bundle/'image.bin'),metadata_sha256=digest(bundle/'metadata.bin'),source_sha256={p:digest(ROOT/p) for p in sources},vm_reports_sha256=[digest(p) for p in vm_reports],hardware_execution=False,physical_pixels_confirmed=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    if not result['all_tests_passed']:raise ValueError('Display qualification failed')
    return result
