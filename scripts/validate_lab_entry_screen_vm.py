#!/usr/bin/env python3
"""Test exact marker instructions in emulated RAM; never access a physical device."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from apply_lab_entry_screen import contract, PORT, ROOT


def validate(output, cc='clang-18', qemu='qemu-system-aarch64'):
    lock=contract()
    if output.exists() or output.is_symlink():raise ValueError('Fresh emulator output required')
    output.mkdir(parents=True,mode=0o700)
    marker=(PORT/lock['overlay']).read_bytes()
    if hashlib.sha256(marker).hexdigest()!=lock['overlay_sha256']:raise ValueError('Marker source drift')
    source=marker.decode().replace('SYM_CODE_START_LOCAL(valethon_lab_entry_screen)',
        '.global valethon_lab_entry_screen\nvalethon_lab_entry_screen:').replace('SYM_CODE_END(valethon_lab_entry_screen)','')
    (output/'marker.S').write_text(source)
    (output/'layout.ld').write_text('ENTRY(_start)\nSECTIONS { . = 0x41000000; .text : { *(.text.start) *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } }\n')
    fixtures=[ROOT/'tests/fixtures/entry_screen_probe.S',ROOT/'tests/fixtures/entry_screen_probe.c']
    command=[cc,'--target=aarch64-none-elf','--ld-path=ld.lld-18','-nostdlib','-static','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-mgeneral-regs-only','-Wl,--build-id=none,-T,'+str(output/'layout.ld'),*[str(p) for p in fixtures],str(output/'marker.S'),'-o',str(output/'probe.elf')]
    r=subprocess.run(command,capture_output=True,timeout=30);(output/'compile-private.log').write_bytes(r.stdout+r.stderr)
    if r.returncode:raise ValueError('Entry emulator compilation failed')
    command=[qemu,'-machine','virt,gic-version=2','-cpu','cortex-a53','-m','1536','-nodefaults','-display','none','-serial','none','-monitor','none','-nic','none','-semihosting-config','enable=on,target=native','-device','loader,file='+str(output/'probe.elf')+',cpu-num=0']
    r=subprocess.run(command,capture_output=True,timeout=30);data=r.stdout+r.stderr;(output/'vm-private.log').write_bytes(data)
    if r.returncode or data!=b'ENTRY_SCREEN_EMULATED_SPAN_GATES_REGISTERS_PASS\n':raise ValueError('Entry emulator gates/span/register controls failed')
    report={'scope':'Actual marker instructions in emulator RAM only; no physical scanout/entry proof','passed':True,'marker_sha256':lock['overlay_sha256'],'probe_sources_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in fixtures},'negative_dtb_cases':8,'all_framebuffer_words_checked':True,'before_after_guard_words_checked':True,'boot_registers_checked':['x0','x19','x20','x21','sp'],'framebuffer_bytes':lock['framebuffer_bytes'],'device_written':False,'physical_ram_read':False,'no_network_or_disks':True,'wall_limit_seconds':30}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(validate(a.output.resolve()),indent=2))
