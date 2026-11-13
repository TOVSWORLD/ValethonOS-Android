#!/usr/bin/env python3
"""Verify linked CPU-off/legacy binding integration; never accesses a device."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path


def verify(build, objdump='aarch64-linux-gnu-objdump', nm='aarch64-linux-gnu-nm'):
    image=(build/'arch/arm64/boot/Image').read_bytes()
    if len(image)<64 or image[56:60]!=b'ARMd':raise ValueError('ARM64 Image required')
    offset,size,flags=struct.unpack_from('<QQQ',image,8)
    if not size or size<len(image) or flags&1 or flags&~15:
        raise ValueError('Unsupported Image header/extent')
    elf=build/'vmlinux'
    data=elf.read_bytes()
    kind,machine=struct.unpack_from('<HH',data,16) if len(data)>=20 else (0,0)
    if data[:6]!=b'\x7fELF\x02\x01' or kind not in (2,3) or machine!=183:
        raise ValueError('Linked ARM64 executable required')
    output=subprocess.run([nm,'--defined-only',str(elf)],capture_output=True,text=True,check=True).stdout
    names={l.split()[2] for l in output.splitlines() if len(l.split())==3}
    required=['mt8163_legacy_affinity_info','mt_kexec_secondary_off_gate',
      'mt_psci_cpu_kill','spm_mtcmos_secondary_off_bounded','spm_mtcmos_secondary_off_check','psci_ops']
    if any(n not in names for n in required):raise ValueError('Linked integration symbols absent')
    dis={}
    for name in ['mt_psci_cpu_kill','mt_kexec_secondary_off_gate','mt8163_legacy_affinity_info']:
        dis[name]=subprocess.run([objdump,'-d','--disassemble='+name,str(elf)],capture_output=True,text=True,check=True).stdout
        if '<'+name+'>:' not in dis[name]:raise ValueError('Linked function absent: '+name)
    if '<spm_mtcmos_secondary_off_bounded>' not in dis['mt_psci_cpu_kill']:
        raise ValueError('CPU kill does not call bounded secondary-off')
    if '<spm_mtcmos_secondary_off_check>' not in dis['mt_kexec_secondary_off_gate']:
        raise ValueError('Final gate does not call independent off-state check')
    if not re.search(r'\bblr\s+x\d+',dis['mt8163_legacy_affinity_info']):
        raise ValueError('Legacy callback lacks its validated conduit call')
    if re.search(r'\b(smc|hvc)\s',dis['mt8163_legacy_affinity_info']):
        raise ValueError('Legacy callback bypasses selected conduit')
    files=['arch/arm64/boot/Image','vmlinux','System.map','.config']
    return {'scope':'Linked Image/symbol/call-target verification only; not boot acceptance',
      'artifacts':{n:{'sha256':hashlib.sha256((build/n).read_bytes()).hexdigest(),
                      'bytes':(build/n).stat().st_size} for n in files},
      'image_header':{'text_offset':offset,'image_size':size,'flags':flags},
      'kernel_release':(build/'include/config/kernel.release').read_text().strip(),
      'required_linked_symbols':required,'kill_calls_bounded_off':True,
      'final_gate_calls_off_state_check':True,'legacy_callback_uses_selected_conduit':True,
      'handoff_gate_wired':False,'hardware_qualified':False,'handoff_admitted':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=verify(a.build);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
