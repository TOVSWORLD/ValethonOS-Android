#!/usr/bin/env python3
"""Prepare/check an isolated full-kernel source overlay; never deploys or boots."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from build_kexec_probe import CONFIG_SHA
from prepare_legacy_affinity import SHA as PSCI_SHA
from prepare_kexec_cpu_off import PIN, PREFIX, HEADER_SHA, OPS_HEADER_SHA
from verify_kexec_probe import RELEASE


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


COMPAT_PATH='sound/soc/mediatek/mt_soc_audio_8163/mt_soc_pcm_dl1_bt.c'
COMPAT_SHA='125fdb038f21ca6c70c21e5ddec1ae0f98dbe40476a97eeb493762f5d8517c8d'


COMPAT_CPUPATH=PREFIX+'mt_cpufreq.c'
COMPAT_CPUSHA='5f45f1713b7e14bf7b2983efcc62444e4fe862ff9e1708af168b291ada776403'
COMPAT_BOOTPATH='drivers/misc/mediatek/boot/mtk_boot_common.c'
COMPAT_BOOTSHA='f561690bd9d8826615589c07dc4af8a0635c1dbec7578bb9858804c9b8359d96'
COMPAT_BOOTHEADER='drivers/misc/mediatek/include/mt-plat/mtk_boot_common.h'
COMPAT_BOOTHEADERSHA='c0409b3dc4df93bcd219c947f0bbe522f1cb741a2743bc9a8e8e1548d44857ad'
COMPAT_METAPATH='drivers/misc/mediatek/boot/mtk_boot.c'
COMPAT_METASHA='eeb3ebe9841466f1134424cb4a85ccd9682ee35e0bf893c286dbecd3518ccf8c'
COMPAT_METAHEADER='drivers/misc/mediatek/include/mt-plat/mtk_boot.h'
COMPAT_METAHEADERSHA='28c502ed5d1ac14a687cc3b0f2c4ba8a23528ec562892d014284e36e94555caa'
COMPAT_BATCHPATH='drivers/misc/mediatek/hwmon/batchsen/batch.c'
COMPAT_BATCHSHA='9a749a631e6aa61406bd416eaa3d3c5c959df59afdcfa948eee0d66441d48f02'
COMPAT_INPUTS={COMPAT_PATH:COMPAT_SHA,COMPAT_CPUPATH:COMPAT_CPUSHA,COMPAT_BOOTPATH:COMPAT_BOOTSHA,COMPAT_METAPATH:COMPAT_METASHA,COMPAT_BATCHPATH:COMPAT_BATCHSHA}

COMPAT_USBPATH='drivers/misc/mediatek/usb20/musb_gadget_ep0.c'
COMPAT_USBSHA='395ae5f9e87d28dd0b521db6756c46d871576f875f2a2578154984cd3ad68bc3'
COMPAT_DEBUGPATH='drivers/misc/mediatek/video/mt8163/videox/debug.h'
COMPAT_DEBUGSHA='50a22eb8abdba63fd18e085b444a232fb80247fbcd344fa7040bf313d8d315b1'
COMPAT_DALHEADER='drivers/misc/mediatek/video/mt8163/videox/disp_assert_layer.h'
COMPAT_DALSHA='81d22dfdcd10e3714a0851a6fdc132d687edbab49c01632b232cf9b6867ae64e'
COMPAT_INPUTS.update({COMPAT_USBPATH:COMPAT_USBSHA,COMPAT_DEBUGPATH:COMPAT_DEBUGSHA})


def compatibility_text(source, path=COMPAT_PATH):
    p=source/path
    if digest(p)!=COMPAT_INPUTS[path]:raise ValueError('Pinned compatibility input differs')
    if path==COMPAT_PATH:
        old='\t\tPRINTK_AUDDRV("mtkalsa_playback_constraints\\n");'
        new=old[1:]
    elif path==COMPAT_CPUPATH:
        old='\t\tcpufreq_ver("num_online_cpus = %d, cur_khz = %d\\n",\n\t\t\tnum_online_cpus(),\n\t\t\tcur_khz);'
        new='\n'.join(line[1:] for line in old.split('\n'))
    elif path==COMPAT_BOOTPATH:
        if digest(source/COMPAT_BOOTHEADER)!=COMPAT_BOOTHEADERSHA:
            raise ValueError('Pinned boot-mode header differs')
        old='unsigned int get_boot_mode(void)'
        new='enum boot_mode_t get_boot_mode(void)'
    elif path==COMPAT_METAPATH:
        if digest(source/COMPAT_METAHEADER)!=COMPAT_METAHEADERSHA:
            raise ValueError('Pinned metadata-port header differs')
        old='unsigned int get_meta_com_type(void)'
        new='enum meta_com_type get_meta_com_type(void)'
    elif path==COMPAT_BATCHPATH:
        old='\t\t\t\tBATCH_LOG("can not handle this fifo, err = %d, fifo_len = %d\\n", err, fifo_len);\n\t\t\t\tmutex_unlock(&batch_data_mutex);'
        new=old.replace('\n\t\t\t\tmutex_unlock','\n\t\t\tmutex_unlock')
    elif path==COMPAT_USBPATH:
        old='\t'*5+'if ((__ratelimit(&ratelimit)))\n'+'\t'*6+'DBG(0,\n'+'\t'*7+'"restarting the request\\n");'
        new='\n'.join('\t'+line for line in old.split('\n'))
    else:
        if digest(source/COMPAT_DALHEADER)!=COMPAT_DALSHA:
            raise ValueError('Pinned display assertion header differs')
        text=p.read_text()
        old='extern int DAL_Clean(void);\nextern int DAL_Printf(const char *fmt, ...);'
        if text.count(old)!=1:raise ValueError('Duplicate display declarations differ')
        return text.replace(old,'#include "disp_assert_layer.h"').encode()
    text=p.read_text()
    if text.count(old)!=1:raise ValueError('Indentation anchor differs')
    return text.replace(old,new).encode()


def prepare(source, kernel_build, cpu_off, legacy, audit, out, check_existing=False, gcc13_compat=False):
    source,kernel_build,cpu_off,legacy,out=map(Path.resolve,(source,kernel_build,cpu_off,legacy,out))
    if out==source or source in out.parents or out==kernel_build or kernel_build in out.parents:
        raise ValueError('Isolated output must be outside original source/build')
    checked=json.loads(audit.read_text());off=json.loads((cpu_off/'source-report.json').read_text())
    binding=json.loads((legacy/'binding-report.json').read_text())
    if checked['source_commit']!=PIN or off['source_commit']!=PIN:
        raise ValueError('Matched audited source revision required')
    originals={'drivers/firmware/psci.c':PSCI_SHA,
      PREFIX+'mtcmos.c':checked['files'][PREFIX+'mtcmos.c']['sha256'],
      PREFIX+'mt_psci.c':checked['files'][PREFIX+'mt_psci.c']['sha256'],
      PREFIX+'mtcmos.h':HEADER_SHA,PREFIX+'mt_cpu_psci_ops.h':OPS_HEADER_SHA}
    if gcc13_compat:
        originals.update(COMPAT_INPUTS);originals[COMPAT_BOOTHEADER]=COMPAT_BOOTHEADERSHA;originals[COMPAT_METAHEADER]=COMPAT_METAHEADERSHA;originals[COMPAT_DALHEADER]=COMPAT_DALSHA
    if any(digest(source/n)!=h for n,h in originals.items()):
        raise ValueError('Pinned original kernel input differs')
    if digest(kernel_build/'.config')!=CONFIG_SHA or (kernel_build/'include/config/kernel.release').read_text().strip()!=RELEASE:
        raise ValueError('Matched original build/config required')
    for name,h in off['files'].items():
        if digest(cpu_off/name)!=h:raise ValueError('CPU-off candidate differs: '+name)
    if (binding['source_sha256']!=PSCI_SHA or digest(legacy/'psci.c')!=binding['patched_sha256'] or
        digest(legacy/'legacy_affinity_policy.h')!=binding['policy_sha256']):
        raise ValueError('Generated legacy binding differs')
    overlay={PREFIX+n:cpu_off/n for n in ['mtcmos.c','mtcmos.h','mt_psci.c','bounded_secondary_off.h','bounded_secondary_adapter.inc']}
    overlay.update({'drivers/firmware/'+n:legacy/n for n in ['psci.c','legacy_affinity_policy.h']})
    compat={n:compatibility_text(source,n) for n in COMPAT_INPUTS} if gcc13_compat else {}
    if not check_existing:
        out.mkdir();(out/'build').mkdir();shutil.copytree(source,out/'source',symlinks=True)
        for name,p in overlay.items():shutil.copyfile(p,out/'source'/name)
        shutil.copyfile(kernel_build/'.config',out/'build/.config')
        for n,data in compat.items():(out/'source'/n).write_bytes(data)
    hashes={n:digest(p) for n,p in overlay.items()}
    hashes.update({n:hashlib.sha256(data).hexdigest() for n,data in compat.items()})
    if any(digest(out/'source'/n)!=h for n,h in hashes.items()):
        raise ValueError('Isolated overlay source differs')
    if digest(out/'build/.config')!=CONFIG_SHA:raise ValueError('Isolated configuration changed')
    result={'scope':'Isolated affinity/CPU-off source integration; no deployment',
      'source_commit':PIN,'original_source_hashes':originals,'overlay_sha256':hashes,
      'gcc13_compat':gcc13_compat,
      'compiler_compatibility_fix':'Whitespace-only indentation repairs and enum declarations matched to existing interfaces; no warning suppression' if gcc13_compat else None,
      'config_sha256':CONFIG_SHA,'original_release':RELEASE,
      'original_source_unchanged':True,'original_build_config_unchanged':True,
      'make_command':['make','-C','<isolated source>','O=<isolated build>','-j4','Image'],
      'hardware_execution':False,'handoff_gate_wired':False,'handoff_admitted':False}
    (out/'source-manifest.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['source','kernel-build','cpu-off','legacy','audit','out']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--check-existing',action='store_true');p.add_argument('--gcc13-compat','--gcc13-indent-fix',dest='gcc13_compat',action='store_true');a=p.parse_args()
    print(json.dumps(prepare(a.source,a.kernel_build,a.cpu_off,a.legacy,a.audit,a.out,a.check_existing,a.gcc13_compat),indent=2))
