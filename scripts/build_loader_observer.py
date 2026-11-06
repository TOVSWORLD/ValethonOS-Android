#!/usr/bin/env python3
"""Prepare a private offline observer payload; no device/flash/boot operations."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile
from validate_loader_observer import object_code,fixture,bl,PLACEMENT
from audit_resident_loader_payload import payload,BASE,SHA


def build(archive,analysis_object,current,output):
    if output.exists() or output.is_symlink():raise ValueError('Fresh private output required')
    code,symbols=object_code(analysis_object)
    if hashlib.sha256(code).hexdigest()!='190fd48d9a981737c2637bbbab1cbac0ce77c1fe486c24c4c6dcacb4885844d6':
        raise ValueError('Exact reviewed observer instructions required')
    resident=payload(archive)
    with zipfile.ZipFile(archive) as z:original=z.read('amonet/bin/boot.payload')
    if len(current)!=492544 or current[:len(original)]!=original:
        raise ValueError('Exact current archived payload sectors required')
    # Existing ROP cleans this resident span before entry. Main cleans the LK
    # span before app(); neither instruction sequence is changed by this patch.
    words=struct.unpack_from('<7I',original,0x960)
    if words!=(0x4bd72a5f,BASE,0x1000,0x4bd3c740,0x4bd00151,0xdead,BASE):
        raise ValueError('Original resident cache chain differs')
    final_offset=0x1a00+0x3e524
    if original[final_offset:final_offset+4]!=bytes.fromhex('fff7a0fc'):
        raise ValueError('Final handoff anchor differs')
    candidate=bytearray(current)
    candidate[0xa00:0x1800]=fixture(resident,code,symbols)
    candidate[final_offset:final_offset+4]=bl(0x4bd3e524,PLACEMENT+symbols['observer_handoff'])
    spans=[(0xa72,4),(0xd30,4),(0x15b8,len(code)),(final_offset,4)]
    allowed={i for start,length in spans for i in range(start,start+length)}
    changed={i for i,(x,y) in enumerate(zip(current,candidate)) if x!=y}
    if not changed or not changed<=allowed:raise ValueError('Unexpected candidate mutation')
    if candidate[0xa00+0xb84:0xa00+0xbb8]!=current[0xa00+0xb84:0xa00+0xbb8]:
        raise ValueError('Live globals/alignment were changed')
    output.mkdir(mode=0o700,parents=False)
    p=output/'observer-payload-sectors-private.bin';p.write_bytes(candidate);p.chmod(0o600)
    report={'scope':'Offline bootstrap payload observer only; not installed or armed',
            'original_payload_sha256':SHA,'rollback_sector_bytes':len(current),
            'rollback_sector_sha256':hashlib.sha256(current).hexdigest(),
            'candidate_sector_sha256':hashlib.sha256(candidate).hexdigest(),
            'stub_bytes':len(code),'stub_sha256':hashlib.sha256(code).hexdigest(),
            'stub_span':[hex(PLACEMENT),hex(PLACEMENT+len(code))],
            'unused_zero_bytes':584-len(code),'allowed_patch_spans':[{'payload_file_offset':hex(x),'bytes':n} for x,n in spans],
            'changed_bytes':len(changed),'all_other_bytes_identical':True,
            'live_globals_unchanged':True,'header_and_original_recovery_chain_unchanged':True,
            'existing_cache_coverage':{'resident':[hex(BASE),hex(BASE+0x1000)],'lk':[hex(0x4bd00000),hex(0x4be00000)],'span_containment_checked':True,'hardware_visibility_qualified':False},
            'new_security_reset_watchdog_or_storage_operations':False,
            'physical_execution_admitted':False,'device_written':False}
    (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--object',type=Path,required=True);p.add_argument('--current-sectors',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(build(a.archive,a.object,a.current_sectors.read_bytes(),a.output),indent=2))
