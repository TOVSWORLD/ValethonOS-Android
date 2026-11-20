#!/usr/bin/env python3
"""Offline graphics package bounds; preserve the original small-ramdisk packer."""
import hashlib, json, lzma, struct
from pathlib import Path
from measure_arm64_image import measure
from pack_lab_log_boot import CONTRACT, overlap

INITRD_ADDRESS = 0x46000000
MAX_ARCHIVE = 30*1024*1024
MAX_RAMDISK = 7*1024*1024


def assemble(image, compressed, dtb, ramdisk, metadata):
    contract=json.loads(CONTRACT.read_text());measured=measure(image,compressed)
    if not measured['decoded_file_fits_lk_capacity'] or len(image)>contract['decoded_image_limit_bytes']:
        raise ValueError('Graphics Image exceeds selected original loader capacity')
    entry=contract['ram_base']+measured['text_offset']
    if entry!=0x40000000 or measured['flags']!=10 or entry+len(image)>contract['inflate_stack']:
        raise ValueError('Preserved ARM64 entry/layout required')
    if not 40<=len(dtb)<=contract['dtb_limit_bytes'] or len(dtb)%4 or struct.unpack_from('>II',dtb)!=(0xd00dfeed,len(dtb)):
        raise ValueError('Aligned bounded graphics DT required')
    if not ramdisk or len(ramdisk)>MAX_RAMDISK: raise ValueError('Bounded graphics ramdisk required')
    decoder=lzma.LZMADecompressor(format=lzma.FORMAT_XZ,memlimit=64*1024*1024)
    raw=decoder.decompress(ramdisk,max_length=MAX_ARCHIVE+1)
    if len(raw)>MAX_ARCHIVE or not decoder.eof or decoder.unused_data or decoder.check!=lzma.CHECK_CRC32:
        raise ValueError('One bounded CRC32 XZ archive required')
    kernel=compressed+bytes((-len(compressed))%4)+dtb
    regions=[(entry,measured['image_size']),(INITRD_ADDRESS,len(raw)),
             (contract['tags_address'],contract['dtb_limit_bytes']),
             (contract['staging_address'],len(kernel))]
    banks=[(int(row['address'],16),row['bytes']) for node in metadata['memory'] for row in node['reg']]
    reserved=[(int(row['address'],16),row['bytes']) for node in metadata['reserved'] for row in node['reg']]
    for i,region in enumerate(regions):
        if not any(region[0]>=a and region[0]+region[1]<=a+n for a,n in banks): raise ValueError('Graphics runtime region outside observed RAM')
        if any(overlap(region,other) for other in reserved+regions[:i]): raise ValueError('Graphics region overlaps another component or reservation')
    page=contract['page_bytes']
    if page!=2048 or contract['header_version']!=0 or contract['mtk_kernel_wrapper']: raise ValueError('Original v0 loader format required')
    header=bytearray(page);header[:8]=b'ANDROID!'
    struct.pack_into('<10I',header,8,len(kernel),entry,len(ramdisk),INITRD_ADDRESS,0,0,contract['tags_address'],page,0,0)
    header[48:59]=b'ValethonLab';args=b'nr_cpus=1 maxcpus=0 clk_ignore_unused regulator_ignore_unused rdinit=/init';header[64:64+len(args)]=args
    digest=hashlib.sha1()
    for b in [kernel,ramdisk,b'']:digest.update(b);digest.update(struct.pack('<I',len(b)))
    header[576:596]=digest.digest();payload=bytes(header)
    for b in [kernel,ramdisk]:payload+=b+bytes((-len(b))%page)
    if len(payload)>contract['partition_bytes']: raise ValueError('Graphics candidate exceeds actual p5 partition')
    candidate=payload+bytes(contract['partition_bytes']-len(payload))
    return candidate,{'scope':'Graphics direct package; offline only','measurement':measured,'entry':entry,
        'initramfs_address':INITRD_ADDRESS,'ramdisk_compression':'xz-lzma2-8m-crc32',
        'runtime_regions':regions,'compressed_kernel_staging_included':True,'unpacked_archive_bytes':len(raw),
        'kernel_component_bytes':len(kernel),'payload_bytes':len(payload),'partition_bytes':len(candidate),
        'partition_sha256':hashlib.sha256(candidate).hexdigest(),'physical_execution_admitted':False}
