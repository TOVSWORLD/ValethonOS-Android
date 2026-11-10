#!/usr/bin/env python3
"""Adapt pinned generic kexec staging to the tested 4.9 ABI; no handoff code."""
import argparse
import difflib
import hashlib
import json
import shutil
from pathlib import Path
PIN = '4ba956fd60b29d2fea324515596b392afdcfa2c5'
FILES = ['kexec.c', 'kexec_core.c', 'kexec.h', 'kexec_internal.h']

def replace(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Upstream source anchor differs: ' + old[:80])
    return text.replace(old, new)

def prepare(upstream, own, output):
    index = json.loads((upstream / 'source-index.json').read_text())
    if index['commit'] != PIN:
        raise ValueError('Unexpected upstream revision')
    for item in index['files']:
        if hashlib.sha256((upstream / item['path']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Upstream source hash differs')
    output.mkdir(parents=True)
    before = {name: (upstream / 'kernel' / name).read_text() for name in FILES}
    after = dict(before)
    t = after['kexec.h']
    t = replace(t, '#include <linux/crash_core.h>\n', '')
    t = replace(t, '#define KEXEC_FLAGS    KEXEC_ON_CRASH', '#define KEXEC_FLAGS    0')
    t = replace(t, '#ifdef ARCH_HAS_KIMAGE_ARCH', 'u32 stage_crc[3];\n\n#ifdef ARCH_HAS_KIMAGE_ARCH')
    after['kexec.h'] = t
    after['kexec_internal.h'] = replace(after['kexec_internal.h'], '#include <linux/kexec.h>', '#include "kexec.h"')
    t = after['kexec.c']
    t = replace(t, 'security_kernel_load_data(LOADING_KEXEC_IMAGE)', 'security_kernel_read_file(NULL, READING_KEXEC_IMAGE)')
    after['kexec.c'] = t
    t = after['kexec_core.c']
    t = replace(t, '#include "kexec_internal.h"', '#include "kexec_internal.h"\n#include "stage_limits.h"\n#include <linux/crc32.h>')
    t = replace(t, 'DEFINE_MUTEX(kexec_mutex);', 'DEFINE_MUTEX(kexec_mutex);\nunsigned long kxstage_owned_pages;')
    t = replace(t, '       unsigned long total_pages = 0;', '       unsigned long total_pages = 0;\n       if (!kxstage_layout_ok(image->start, nr_segments, image->segment))\n               return -EINVAL;')
    t = replace(t, '       pages = alloc_pages(gfp_mask & ~__GFP_ZERO, order);',
        '       /* Hard bound includes staged, control, and skipped destination pages. */\n'
        '       if (order > 4 || kxstage_owned_pages + (1UL << order) > 24592)\n'
        '               return NULL;\n'
        '       pages = alloc_pages((gfp_mask & ~__GFP_ZERO) | __GFP_NORETRY | __GFP_NOWARN, order);')
    t = replace(t, '\t       count = 1 << order;', '\t       count = 1 << order;\n\t       kxstage_owned_pages += count;')
    t = replace(t, '       __free_pages(page, order);', '       kxstage_owned_pages -= count;\n       __free_pages(page, order);')
    t = replace(t, '       result = 0;\n       if (image->file_mode)', '       result = 0;\n       image->stage_crc[segment - image->segment] = ~0U;\n       if (image->file_mode)')
    t = replace(t, '\t       if (result < 0)\n\t\t       goto out;\n\n\t       ptr = kmap(page);',
                  '\t       if (result < 0) {\n\t\t       kimage_free_pages(page);\n\t\t       goto out;\n\t       }\n\n\t       ptr = kmap(page);')
    t = replace(t, '\t       kunmap(page);', '\t       if (!result)\n\t\t       image->stage_crc[segment - image->segment] = crc32_le(image->stage_crc[segment - image->segment], ptr, mchunk);\n\t       kunmap(page);')
    # Remove the complete execution function, including every shutdown callback.
    at = t.index('int kernel_kexec(void)\n{')
    t = t[:at] + '/* Execution implementation intentionally omitted; stage_arch.c refuses it. */\n'
    after['kexec_core.c'] = t
    patch = []
    for name in FILES:
        (output / name).write_text(after[name])
        patch += list(difflib.unified_diff(before[name].splitlines(True), after[name].splitlines(True), fromfile='upstream/kernel/'+name, tofile='stage/'+name))
    for name in ['stage_driver.c', 'stage_arch.c', 'stage_uapi.h', 'stage_limits.h', 'Makefile']:
        shutil.copyfile(own / name, output / name)
    (output / 'adaptation.patch').write_text(''.join(patch))
    manifest = {'upstream_commit': PIN, 'scope': 'Prepare-only generic staging port; no restart code linked',
        'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()},
        'max_staged_bytes': 33554432, 'max_segments': 3, 'max_owned_pages': 24592,
        'kernel_handoff_implemented': False, 'loaded_on_tablet': False}
    (output / 'source-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['upstream', 'own', 'out']: p.add_argument('--'+key, type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.upstream, a.own, a.out), indent=2))
