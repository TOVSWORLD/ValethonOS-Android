#!/usr/bin/env python3
"""Actual earliest probe in emulated RAM at EL1/EL2/EL3; no tablet access."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
from apply_lab_entry_delay import contract, PORT, ROOT


def validate(output,cc='clang-18',qemu='qemu-system-aarch64'):
    lock=contract()
    if output.exists() or output.is_symlink():raise ValueError('Fresh probe output required')
    output.mkdir(parents=True,mode=0o700)
    marker=(PORT/lock['overlay']).read_bytes()
    if hashlib.sha256(marker).hexdigest()!=lock['overlay_sha256']:raise ValueError('Probe source drift')
    source=marker.decode().replace('SYM_CODE_START_LOCAL(valethon_entry_delay)','.global valethon_entry_delay\nvalethon_entry_delay:').replace('SYM_CODE_END(valethon_entry_delay)','')
    (output/'probe.S').write_text(source)
    (output/'layout.ld').write_text('ENTRY(_start)\nSECTIONS { . = 0x41000000; .text : { *(.text.start) *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } }\n')
    fixtures=[ROOT/'tests/fixtures/entry_delay_probe.S',ROOT/'tests/fixtures/entry_delay_probe.c']
    cmd=[cc,'--target=aarch64-none-elf','--ld-path=ld.lld-18','-nostdlib','-static','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-mgeneral-regs-only','-Wl,--build-id=none,-T,'+str(output/'layout.ld'),*[str(p) for p in fixtures],str(output/'probe.S'),'-o',str(output/'probe.elf')]
    r=subprocess.run(cmd,capture_output=True,timeout=30);(output/'compile-private.log').write_bytes(r.stdout+r.stderr)
    if r.returncode:raise ValueError('Earliest-probe compilation failed')
    def run(el):
        machine='virt,gic-version=2'+(',virtualization=on' if el>=2 else '')+(',secure=on' if el==3 else '')
        cmd=[qemu,'-machine',machine,'-cpu','cortex-a53','-m','1536','-nodefaults','-display','none','-serial','none','-monitor','none','-nic','none','-semihosting-config','enable=on,target=native','-device','loader,file='+str(output/'probe.elf')+',cpu-num=0']
        r=subprocess.run(cmd,capture_output=True,timeout=45);data=r.stdout+r.stderr;(output/f'el{el}-private.log').write_bytes(data)
        expected=f'ENTRY_DELAY_EL{el}_SPAN_GATES_REGISTERS_8S_PASS\n'.encode()
        if r.returncode or data!=expected:raise ValueError(f'Earliest probe EL{el} control failed')
        return el
    with ThreadPoolExecutor(max_workers=3) as pool:levels=list(pool.map(run,[1,2,3]))
    report={'scope':'Actual earliest probe instructions in emulator RAM only; no physical entry/reset/display proof','passed':True,'exception_levels':levels,'overlay_sha256':lock['overlay_sha256'],'registers_preserved':['x0','x1','x2','x3','x18','x19','x20','x21','sp'],'all_framebuffer_words_and_adjacent_guards_checked':True,'cache_enabled_paint_and_clean_checked':True,'zero_out_of_range_frequency_and_delay_controls_checked':True,'eight_counter_seconds_checked':True,'counter_stopped_wall_bound_qualified':False,'reset_or_watchdog_register_writes':False,'network_or_disks':False,'device_accessed':False}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(validate(a.output.resolve()),indent=2))
