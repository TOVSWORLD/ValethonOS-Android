#!/usr/bin/env python3
"""Exact installed/package LK and candidate audit, offline only; never runs firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib
from trace_lk_handoff import thumb_call

LK_SHA = '7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056'
CANDIDATE_SHA = '8d3729e6869371ba80aa2da6e1c6d29dbbf1e84ba5ed6b431f1a66354141be16'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit(installed, package, candidate):
    if sha(package) != LK_SHA or len(package) != 485988:
        raise ValueError('Exact original-package LK required')
    if len(installed) != 524288 or installed[:len(package)] != package:
        raise ValueError('Installed LK executable does not match package')
    if sha(candidate) != CANDIDATE_SHA or len(candidate) != 16777216:
        raise ValueError('Exact tested candidate6 required')
    code = package[512:]
    def exact(at, raw):
        if code[at:at+len(raw)] != raw:
            raise ValueError('LK instruction anchor mismatch')
    # Normal boot-mode0 dispatch, actual original-package offsets (not old OTA).
    exact(0x3ec52, bytes.fromhex('dfe813f0'))  # TBH [pc,r3,lsl#1]
    target = 0x3ec56 + 2 * struct.unpack_from('<H', code, 0x3ec56)[0]
    if target != 0x3f0da:
        raise ValueError('Normal-mode dispatch differs')
    calls = []
    for at, want in [(0x3ef1c,0x24708),(0x3ef42,0x24e48),
                     (0x24776,None),(0x24ea8,None),(0x24f2a,None),
                     (0x3ee44,0x3ec10),(0x3ec1c,0x3deb4),
                     (0x3e6d0,0x3f59c),(0x3e524,0x3de68),(0x3de84,0x3c978)]:
        if want is None:
            exact(at,bytes.fromhex('8847'))  # dev->read, hook selected at runtime
        else:
            actual=thumb_call(*struct.unpack_from('<HH',code,at),at)
            if actual != want:raise ValueError('LK call target differs')
            calls.append({'offset':hex(at),'target':hex(actual)})
    exact(0x25824,bytes.fromhex('4ff08a407047')) # compressed input staging45000000
    exact(0x3e6c8,bytes.fromhex('4ff0e0733168c968')) #28MiB gzip output capacity
    exact(0x3e51c,bytes.fromhex('5846029900220123')) # entry r11, DT sp+8,0,1
    exact(0x3c978,bytes.fromhex('0340a0e10230a0e10120a0e10010a0e1'))
    exact(0x3c98c,bytes.fromhex('700060e1'))
    if struct.unpack_from('<I',code,0x3c998)[0] != 0x82000200:
        raise ValueError('SMC function differs')
    if candidate[:8] != b'ANDROID!':raise ValueError('Android header required')
    size,entry,ramdisk_size,ramdisk_addr,second,_,tags,page=struct.unpack_from('<8I',candidate,8)
    if page != 2048 or second or entry & 0x7ffff:raise ValueError('Header contract differs')
    kernel=candidate[page:page+size]
    decoder=zlib.decompressobj(31);image=decoder.decompress(kernel,29360129)
    if not decoder.eof or len(image)>29360128:raise ValueError('Gzip capacity/completeness differs')
    consumed=len(kernel)-len(decoder.unused_data);dt_offset=(consumed+3)&~3;dt=kernel[dt_offset:]
    if kernel[consumed:dt_offset] != bytes(dt_offset-consumed):raise ValueError('Alignment padding differs')
    if len(dt)<40 or struct.unpack_from('>II',dt)!=(0xd00dfeed,len(dt)):
        raise ValueError('Single aligned FDT suffix required')
    # Reproduce bounded backward FDT magic search; require the actual suffix to
    # be the final candidate, no accidental later magic in the copied DT.
    offsets=[i for i in range(max(0,len(kernel)-0x57800),len(kernel)-3)
             if kernel[i:i+4]==bytes.fromhex('d00dfeed')]
    if not offsets or offsets[-1]!=dt_offset:raise ValueError('Backward DT selection ambiguous')
    text_offset,runtime_size=struct.unpack_from('<QQ',image,8)
    if image[56:60]!=b'ARM\x64' or entry!=0x40000000+text_offset:
        raise ValueError('Decoded ARM64 entry/header mismatch')
    if entry+len(image)>0x42000000 or entry+runtime_size>ramdisk_addr:
        raise ValueError('Decoded/runtime placement overlaps stack/initrd')
    header=bytearray(candidate[:page]);header_id=bytes(header[576:596]);digest=hashlib.sha1()
    rd_offset=page+((size+page-1)//page)*page;rd=candidate[rd_offset:rd_offset+ramdisk_size]
    for item in [kernel,rd,b'']:digest.update(item);digest.update(struct.pack('<I',len(item)))
    if header_id!=digest.digest():raise ValueError('Android component digest differs')
    return {'scope':'Exact installed LK bytes and tested candidate6 selected-path static audit; no firmware execution',
            'installed_lk_package_prefix_match':True,'lk_sha256':sha(package),
            'installed_partition_sha256':sha(installed),'installed_partition_bytes':len(installed),
            'historical_ota_lk_used_as_substitute':False,'candidate_sha256':sha(candidate),
            'normal_bootmode0_dispatch_target':hex(target),'checked_calls':calls,
            'read_hook_source_contract':'Logical boot base and base+2048 redirected to boot_x; runtime hook/mode not observed',
            'candidate':{'page_bytes':page,'kernel_component_bytes':size,'entry':hex(entry),
                         'compressed_staging':hex(0x45000000),'gzip_consumed_bytes':consumed,
                         'decoded_bytes':len(image),'decoded_sha256':sha(image),
                         'runtime_bytes':runtime_size,'dt_suffix_offset':dt_offset,'dt_bytes':len(dt),
                         'dt_sha256':sha(dt),'dt_argument':hex(tags),'ramdisk_address':hex(ramdisk_addr),
                         'component_digest_verified':True,'selected_gzip_capacity_fits':True},
            'final_lk_smc_contract':{'function':'0x82000200','r1':'header kernel entry','r2':'selected DT address','r3':0,'r4':1},
            'concrete_package_mismatch_found':False,
            'unobserved':['Runtime normal boot mode and read-hook selection','Runtime completion of DT fixups/decompression','Secure monitor transfer and actual PC/EL/x0 at kernel entry','Physical scanout and timer preconditions'],
            'next_decision':'Do not rebuild or repeat candidate6. A loader-owned observation before SMC is required to distinguish loader rejection from post-handoff failure. Any instrumentation of the resident chain needs a separately reviewed exact implementation; none is admitted by this report.',
            'device_written':False,'runtime_entry_qualified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['installed-lk','package-lk','candidate','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();report=audit(a.installed_lk.read_bytes(),a.package_lk.read_bytes(),a.candidate.read_bytes())
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'audit_passed':True,'concrete_package_mismatch_found':False,'runtime_entry_qualified':False}))
