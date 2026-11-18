#!/usr/bin/env python3
"""Repack the pinned installed boot with verified native-kexec Image; offline only."""
import argparse
import gzip
import hashlib
import json
import struct
import zlib
from pathlib import Path
from inspect_boot_image import inspect
from run_kexec_probe import BOOT_SHA
from verify_native_kexec_build import CONFIG_SHA

PARTITION=16777216


def sha(data):return hashlib.sha256(data).hexdigest()


def split_kernel(data):
    d=zlib.decompressobj(31);image=d.decompress(data,64*1024*1024+1)
    if not d.eof or d.unconsumed_tail or len(image)>64*1024*1024:
        raise ValueError('Bounded original gzip Image required')
    suffix=d.unused_data;at=0;dtbs=[]
    while at<len(suffix):
        if len(suffix)-at<40 or len(dtbs)>=32:raise ValueError('Invalid appended DT suffix')
        h=struct.unpack_from('>10I',suffix,at);magic,size,structure,strings,reserve,version,compat,_,strings_size,structure_size=h
        if magic!=0xd00dfeed or not 40<=size<=2*1024*1024 or at+size>len(suffix) or version!=17 or compat>17:
            raise ValueError('Unsupported original FDT suffix')
        if reserve<40 or reserve+16>size or structure<40 or structure+structure_size>size or strings<40 or strings+strings_size>size:
            raise ValueError('FDT blocks outside original suffix')
        dtbs.append({'bytes':size,'sha256':sha(suffix[at:at+size])});at+=size
    if not dtbs:raise ValueError('Original appended DTs required')
    return image,suffix,dtbs


def assemble(original,image,linked,expected_original=BOOT_SHA,expected_config_sha256=CONFIG_SHA):
    if len(original)!=PARTITION or sha(original)!=expected_original:raise ValueError('Pinned full original boot required')
    layout=inspect(original,PARTITION);kernel,ramdisk,second=layout['components']
    if layout['page_size']!=2048 or second['bytes'] or not ramdisk['bytes']:raise ValueError('Unreviewed original boot layout')
    for field in ['arm64_syscall_104_is_kexec_load','handoff_gate_wired','orderly_reboot_namespace_linked']:
        if linked.get(field) is not True:raise ValueError('Native linked validation required: '+field)
    if linked['artifacts']['arch/arm64/boot/Image']['sha256']!=sha(image) or linked['artifacts']['.config']['sha256']!=expected_config_sha256:
        raise ValueError('Image/config differs from native validation')
    old_kernel=original[kernel['offset']:kernel['offset']+kernel['bytes']]
    old_image,suffix,dtbs=split_kernel(old_kernel)
    if len(image)<64 or image[56:60]!=b'ARMd' or old_image[56:60]!=b'ARMd':raise ValueError('ARM64 Image required')
    offset,size,flags=struct.unpack_from('<QQQ',image,8)
    old_offset,_,old_flags=struct.unpack_from('<QQQ',old_image,8)
    if offset!=old_offset or flags!=old_flags or flags&1 or flags&~15 or size<len(image):raise ValueError('Unreviewed ARM64 protocol change')
    if kernel['load_address']!=0x40000000+offset or kernel['load_address']+size>0x42000000:
        raise ValueError('Image exceeds the previously selected loader entry/capacity')
    packed=bytearray(gzip.compress(image,mtime=0));packed[9]=255;packed=bytes(packed)+suffix
    rd=original[ramdisk['offset']:ramdisk['offset']+ramdisk['bytes']]
    page=layout['page_size'];header=bytearray(original[:page]);struct.pack_into('<I',header,8,len(packed))
    identifier=hashlib.sha1()
    for component in [packed,rd,b'']:
        identifier.update(component);identifier.update(struct.pack('<I',len(component)))
    header[576:596]=identifier.digest()
    payload=bytes(header)
    for part in [packed,rd]:payload+=part+bytes((-len(part))%page)
    if len(payload)>PARTITION:raise ValueError('Candidate exceeds original boot partition')
    candidate=payload+original[len(payload):]
    parsed=inspect(candidate,PARTITION);newk,newrd,_=parsed['components']
    decoded,newsuffix,newdtbs=split_kernel(candidate[newk['offset']:newk['offset']+newk['bytes']])
    if decoded!=image or newsuffix!=suffix or newdtbs!=dtbs:raise ValueError('Repacked Image/DT verification failed')
    if candidate[newrd['offset']:newrd['offset']+newrd['bytes']]!=rd:raise ValueError('Original ramdisk changed')
    changed_header={i for i,(a,b) in enumerate(zip(original[:page],candidate[:page])) if a!=b}
    if changed_header-(set(range(8,12))|set(range(576,596))):raise ValueError('Unexpected original header change')
    old_id=hashlib.sha1()
    for c in layout['components']:
        old_id.update(original[c['offset']:c['offset']+c['bytes']]);old_id.update(struct.pack('<I',c['bytes']))
    report={'scope':'Offline native-source boot candidate; no hardware admission',
      'original_boot_sha256':sha(original),'candidate_sha256':sha(candidate),'partition_bytes':len(candidate),
      'image_sha256':sha(image),'image_file_bytes':len(image),'image_memory_bytes':size,
      'resolved_config_sha256':expected_config_sha256,'appended_dtbs':dtbs,'original_dt_suffix_preserved':True,
      'original_ramdisk_sha256':sha(rd),'original_ramdisk_and_header_addresses_preserved':True,
      'original_header_changes_only_kernel_size_and_id':True,'new_declared_end':len(payload),
      'original_declared_end':second['padded_end'],'original_tail_after_new_declared_end_preserved':True,
      'original_standard_component_id_matched':original[576:596]==old_id.digest(),
      'new_standard_component_id':identifier.hexdigest(),'signature_verified':False,
      'original_rollback_bytes_retained':True,'boot_tested':False,'experimental_jump_executed':False,
      'failed_jump_logging_is_pretrial_blocker':False}
    return candidate,report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['original-boot','image','linked-report','out']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();candidate,r=assemble(a.original_boot.read_bytes(),a.image.read_bytes(),json.loads(a.linked_report.read_text()))
    a.out.mkdir(mode=0o700)
    for name,data in [('boot-full.img',candidate),('original-boot.img',a.original_boot.read_bytes()),('report.json',(json.dumps(r,indent=2)+'\n').encode())]:
        f=a.out/name;f.write_bytes(data);f.chmod(0o600)
    print(json.dumps(r,indent=2))
