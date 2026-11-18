#!/usr/bin/env python3
"""Verify pinned syscall/configfs/controller contracts; not a device test."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'evidence/usb-acm-userspace/source'


def integer(value):
    if value.startswith('0') and len(value)>1 and not value.startswith('0x'):
        return int(value,8)
    return int(value,0)


def file_flags():
    generic = (EVIDENCE/'fcntl-generic.h').read_text()
    arm64 = (EVIDENCE/'arm64-fcntl.h').read_text()
    linux = (EVIDENCE/'fcntl-linux.h').read_text()
    if '#include <asm-generic/fcntl.h>' not in arm64:
        raise ValueError('ARM64 fcntl include chain drift')
    numeric = r'^#define ([A-Z_]+)\s+(-?(?:0x[0-9a-f]+|[0-9]+))\b'
    flags = dict(re.findall(numeric, generic+'\n'+linux, re.M))
    overrides = dict(re.findall(numeric, arm64, re.M))
    if set(overrides) != {'O_DIRECTORY','O_NOFOLLOW','O_DIRECT','O_LARGEFILE'}:
        raise ValueError('ARM64 fcntl override set drift')
    for name in overrides:
        if '#ifndef '+name not in generic:
            raise ValueError('Generic fallback no longer guarded: '+name)
    flags.update(overrides)
    return {name: integer(value) for name,value in flags.items()}


def validate():
    receipt=json.loads((EVIDENCE/'sources.json').read_text())
    for entry in receipt['sources']:
        data=(ROOT/entry['local']).read_bytes()
        if len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
            raise ValueError('Pinned userspace contract source drift: '+entry['path'])
    if '#include <asm/unistd_64.h>' not in (EVIDENCE/'arm64-unistd.h').read_text():
        raise ValueError('ARM64 generated header selection drift')
    if not re.search(r'syscall_abis_64\s*\+=\s*common,64', (EVIDENCE/'Makefile.asm-headers').read_text()):
        raise ValueError('Default 64-bit syscall ABI selection drift')
    if 'syscalltbl = arch/arm64/tools/syscall_%.tbl' not in (EVIDENCE/'arm64-Makefile.syscalls').read_text():
        raise ValueError('ARM64 syscall-table path drift')
    if (EVIDENCE/'arm64-syscall_64.tbl').read_text().strip()!='../../../scripts/syscall.tbl':
        raise ValueError('ARM64 syscall-table link drift')
    table={name:int(n) for n,abi,name in re.findall(r'^(\d+)\s+(common|64)\s+(\w+)\s', (EVIDENCE/'syscall.tbl').read_text(), re.M)}
    header=(ROOT/'projects/firetabs-android/diagnostic-usb/acm_fs.h').read_text()
    macros=dict(re.findall(r'^#define (FT_[A-Z0-9_]+)\s+(-?(?:0x[0-9a-f]+|[0-9]+))$',header,re.M))
    checked={}
    for name,value in macros.items():
        if name.startswith('FT_NR_'):
            syscall=name[len('FT_NR_'):].lower()
            if table.get(syscall)!=integer(value):raise ValueError('Syscall ABI mismatch: '+name)
            checked[syscall]=integer(value)
    if len(checked)!=8:raise ValueError('Unexpected syscall adapter set')
    flags=file_flags()
    for name in ['O_WRONLY','O_DIRECTORY','O_NOFOLLOW','O_CLOEXEC','AT_FDCWD','AT_REMOVEDIR']:
        if flags.get(name)!=integer(macros['FT_'+name]):raise ValueError('File ABI mismatch: '+name)
    policy=(ROOT/'projects/firetabs-android/diagnostic-usb/lab_policy_load.h').read_text()
    match=re.search(r'^#define VP_NOFOLLOW\s+([0-9]+)$',policy,re.M)
    if not match or integer(match[1])!=flags['O_NOFOLLOW']:
        raise ValueError('Policy bootstrap ARM64 nofollow mismatch')
    configfs=(EVIDENCE/'configfs.c').read_text()
    for token in ["if (name[len - 1] == '\\n')", "name[len - 1] = '\\0';", 'if (!gi->composite.gadget_driver.udc_name)', 'return -ENODEV;', 'udc_name ?: ""']:
        if token not in configfs:raise ValueError('Configfs unbind/readback contract drift')
    if 'udc->dev.parent = gadget->dev.parent;' not in (EVIDENCE/'udc-core.c').read_text():
        raise ValueError('UDC parent contract drift')
    if 'usb_add_gadget_udc(musb->controller, &musb->g)' not in (EVIDENCE/'musb_gadget.c').read_text():
        raise ValueError('MUSB UDC parent contract drift')
    readdir=(EVIDENCE/'readdir.c').read_text()
    if 'ALIGN(offsetof(struct linux_dirent64, d_name) + namlen + 1,' not in readdir or 'sizeof(u64)' not in readdir:
        raise ValueError('Dirent alignment contract drift')
    return {'scope':'Pinned source/ABI checks only; no filesystem or gadget execution',
            'syscalls':checked,'arm64_file_flags':{n:flags[n] for n in ['O_DIRECTORY','O_NOFOLLOW','O_DIRECT','O_LARGEFILE']},'configfs_newline_unbind_and_empty_readback_checked':True,
            'expected_controller_parent_source_checked':True,'runtime_qualified':False}


if __name__=='__main__':
    print(json.dumps(validate(),indent=2))
