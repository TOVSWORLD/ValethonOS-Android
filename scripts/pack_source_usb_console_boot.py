#!/usr/bin/env python3
"""Offline variant: enable ttyGS0 on the source, leaving g_serial unbound."""
import argparse, hashlib, json
from pathlib import Path
from pack_usb_console_boot import pack

PREFIX = b'console=ttyGS0 '

def enable_source_console(candidate):
    # Legacy Android header: cmdline[512], followed by id[32]. Do not touch
    # appended board DTs, ramdisk, addresses or the optional extra cmdline.
    if candidate[:8] != b'ANDROID!' or len(candidate) != 16777216:
        raise ValueError('Exact legacy full boot image required')
    field = candidate[64:576]
    if b'\0' not in field or any(candidate[608:1632]):
        raise ValueError('Single terminated legacy command line required')
    args = field.split(b'\0', 1)[0]
    if any(field[len(args):]) or b'ttyGS' in args or b'g_serial.' in args:
        raise ValueError('Unmodified source command line required')
    new = PREFIX + args
    if len(new) >= 512:
        raise ValueError('Source command line capacity exceeded')
    result = candidate[:64] + new.ljust(512, b'\0') + candidate[576:]
    assert result[:64] == candidate[:64] and result[576:] == candidate[576:]
    return result

def prepare(original, image, linked):
    candidate, report = pack(original, image, linked)
    candidate = enable_source_console(candidate)
    report.update(candidate_sha256=hashlib.sha256(candidate).hexdigest(),
                  scope='Source ttyGS0 console; Android configfs retains USB ownership',
                  source_ramdisk_and_cmdline_unchanged=False,
                  original_header_changes_only_kernel_size_and_id=False,
                  original_header_changes_only_kernel_size_id_and_cmdline=True,
                  source_cmdline_prefix=PREFIX.decode().strip(),
                  original_cmdline_suffix_preserved=True,
                  legacy_serial_bind_enabled=False,
                  source_shutdown_capture_qualified=False)
    return candidate, report

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['original-boot','image','linked-report','out']:
        p.add_argument('--'+n, type=Path, required=True)
    a = p.parse_args()
    original = a.original_boot.read_bytes()
    candidate, report = prepare(original, a.image.read_bytes(), json.loads(a.linked_report.read_text()))
    a.out.mkdir(mode=0o700)
    for name, data in [('boot-full.img',candidate),('original-boot.img',original),
                       ('report.json',(json.dumps(report,indent=2)+'\n').encode())]:
        f=a.out/name;f.write_bytes(data);f.chmod(0o600)
    print(json.dumps(report,indent=2))
