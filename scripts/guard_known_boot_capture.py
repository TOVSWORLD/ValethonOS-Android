#!/usr/bin/env python3
"""Exact known-boot control bootstrap guard; no reboot/helper/trial arm.

The historical diagnostic hold remains unchanged. This module admits only the
separately reviewed exact known-stack calibration, with explicit authorization.

Install/restore are separate high-risk reviewed operations, never automatic.
Only the original-source payload span of boot_amonet may be written. Recovery
bootstrap, headers, GPT, bootloader/security partitions and userdata stay untouched.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import re
import struct
import subprocess
import zlib
from restore_diagnostic_boot import Adb,sha,update_receipt

STAGE='input'
TARGET='/dev/block/mmcblk0p17'
RETURN='/dev/block/mmcblk0p18'
OFFSET=223223
SECTORS=962
SIZE=SECTORS*512
ORIGINAL='4c6f355c735b9302b0d421ef38f94a9974214d531fa974a41edd8132af7ac092'
CANDIDATE='21a26da4e5c2baf29f46be3cd417d50abef4b314911775947bc231117be38851'
ORIGINAL_BOOT='08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e'
KERNEL_CANDIDATE='77d7453b3fde4764c3a8e8d9a29587ad5d8a2e726388ab411f80356147420a00'
RECOVERY='3c9bafcbfc4a0b12cb1a3f372af0cfd49ffec5b3e01a0b070465b49bd8435f11'
CONTROL_PREFIX='123e68fcd376d5a90e246dbbd87d66d6f7f6488b640aeea6b947beae30d67ea1'
CONTROL_SEED='e3cc7e5440f555239be811085ed1f25aa74578737d42b2ec1c74a34ba79acaf8'


def gpt_range(data):
    if len(data)!=17408 or data[512:520]!=b'EFI PART':raise ValueError('Exact GPT metadata required')
    h=bytearray(data[512:1024]);length=struct.unpack_from('<I',h,12)[0]
    if not 92<=length<=512:raise ValueError('GPT header length differs')
    crc=struct.unpack_from('<I',h,16)[0];struct.pack_into('<I',h,16,0)
    if zlib.crc32(h[:length])!=crc:raise ValueError('GPT header CRC differs')
    start,count,size,want=struct.unpack_from('<QIII',h,72)
    if (start,count,size)!=(2,128,128):raise ValueError('GPT table geometry differs')
    table=data[start*512:start*512+count*size]
    if zlib.crc32(table)!=want:raise ValueError('GPT entries CRC differs')
    entries=[]
    for i in range(count):
        e=table[i*size:(i+1)*size]
        if e[:16]==bytes(16):continue
        first,last=struct.unpack_from('<QQ',e,32)
        if last<first:raise ValueError('GPT interval invalid')
        entries.append((i+1,first,last,e[56:128].decode('utf-16le').split('\0')[0]))
    target=next((e for e in entries if e[0]==17),None)
    if target is None or target[3]!='boot' or (target[2]-target[1]+1)*512!=115343360:
        raise ValueError('Exact bootstrap container geometry required')
    first=target[1]+OFFSET;end=first+SECTORS
    if end>target[2]+1:raise ValueError('Payload exceeds container')
    for number,a,b,name in entries:
        if number!=17 and a<end and b+1>first:
            raise ValueError('Payload overlaps another GPT entry')
    recovery=next((e for e in entries if e[0]==18 and e[3]=='recovery'),None)
    if recovery is None or (recovery[2]-recovery[1]+1)*512!=115343360:
        raise ValueError('Independent recovery bootstrap entry absent')
    for number,first,size,name in [(5,18432,32768,'boot_x'),(6,51200,34816,'recovery_x'),(17,30325760,225280,'boot'),(18,30551040,225280,'recovery')]:
        if not any(e[0]==number and e[1]==first and e[2]-e[1]+1==size and e[3]==name for e in entries):
            raise ValueError('Exact checkpoint descriptor/GPT geometry differs')
    return {str(e[0]):(e[1],e[2]-e[1]+1) for e in entries if e[0] in [5,6,17,18]}


def range_read(adb,node):
    if node not in [TARGET,RETURN]:raise ValueError('Unreviewed range node')
    data=adb.run(['exec-out','sh','-c','dd if='+node+' bs=512 skip=223223 count=962 2>/dev/null'])
    if len(data)!=SIZE:raise ValueError('Exact payload-sector read required')
    return data


def preflight(adb,originals,current,boot):
    global STAGE
    STAGE="input_hashes"
    for name in ['boot_amonet','recovery_amonet']:
        if (originals[name]['header_sha256']!='c8a9f89481e871851193ed6e3446a9ba6aaf4ea85c51cd6a21032f94fee4872c'
                or originals[name]['payload_sector_sha256']!=ORIGINAL):
            raise ValueError('Pinned original bootstrap receipt required')
    if current not in [ORIGINAL,CANDIDATE] or not re.fullmatch('[0-9a-f]{64}',boot):
        raise ValueError('Exact reviewed current hashes required')
    STAGE='recovery_identity'
    if adb.run(['get-state']).strip()!=b'recovery':raise ValueError('Recovery required')
    for prop,want in [('ro.product.device',b'douglas'),('ro.twrp.version',b'3.3.1-0')]:
        if adb.run(['shell','getprop',prop]).strip()!=want:raise ValueError('Recovery identity differs')
    STAGE='partition_aliases'
    base='/dev/block/platform/mtk-msdc.0/by-name/'
    for name,node in [('boot_amonet',TARGET),('recovery_amonet',RETURN),('boot','/dev/block/mmcblk0p5'),('boot_x','/dev/block/mmcblk0p5'),('recovery','/dev/block/mmcblk0p6'),('recovery_x','/dev/block/mmcblk0p6')]:
        if adb.run(['shell','readlink',base+name]).strip()!=node.encode():raise ValueError('Partition alias differs')
    STAGE='gpt_geometry'
    geometry=gpt_range(adb.run(['exec-out','head','-c','17408','/dev/block/mmcblk0']))
    STAGE='kernel_partition_geometry'
    for number,(start,size) in geometry.items():
        for field,want in [('start',start),('size',size)]:
            value=adb.run(['exec-out','cat','/sys/class/block/mmcblk0p'+number+'/'+field]).strip()
            if not value.isdigit() or int(value)!=want:raise ValueError('Kernel/GPT partition mapping differs')
    STAGE='bootstrap_headers'
    for name,node in [('boot_amonet',TARGET),('recovery_amonet',RETURN)]:
        header=adb.run(['exec-out','head','-c','512',node])
        if len(header)!=512 or sha(header)!=originals[name]['header_sha256']:raise ValueError('Bootstrap header differs')
    STAGE='return_bootstrap_range'
    if sha(range_read(adb,RETURN))!=originals['recovery_amonet']['payload_sector_sha256']:
        raise ValueError('Independent recovery bootstrap differs')
    STAGE='target_bootstrap_range'
    if sha(range_read(adb,TARGET))!=current:raise ValueError('Current observer range differs')
    STAGE='normal_boot'
    normal=adb.read('/dev/block/mmcblk0p5',16777216)
    if sha(normal)!=boot:raise ValueError('Normal boot differs')
    if boot!=ORIGINAL_BOOT and (sha(normal[:15728640])!=CONTROL_PREFIX
            or sha(normal[15728640:15732736])!=CONTROL_SEED):
        raise ValueError('Exact known-stack control prefix/seed required')
    STAGE='normal_recovery'
    if sha(adb.read('/dev/block/mmcblk0p6',17825792))!=RECOVERY:raise ValueError('Normal recovery differs')
    return {'preflight':'passed','device_written':False,'rebooted':False}


def write_once(adb,data,originals,current,boot,receipt_path,authorization=None):
    target=sha(data)
    if len(data)!=SIZE or (current,target) not in [(ORIGINAL,CANDIDATE),(CANDIDATE,ORIGINAL)]:
        raise ValueError('Only exact reviewed install or rollback allowed')
    if target==CANDIDATE:
        authorize(authorization)
    preflight(adb,originals,current,boot)
    receipt={'operation':'bootstrap observer install' if target==CANDIDATE else 'bootstrap original restore','expected_before_sha256':current,'target_sha256':target,'write_started':False,'verified':False,'rebooted':False,'recovery_written':False}
    fd=os.open(receipt_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(receipt,f);f.flush();os.fsync(f.fileno())
    try:
        if adb.run(['exec-out','readlink','-f','/tmp']).strip()!=b'/tmp':raise ValueError('RAM path redirected')
        mounts=[x.split() for x in adb.run(['exec-out','cat','/proc/mounts']).splitlines()]
        match=[x for x in mounts if len(x)>=4 and x[1]==b'/tmp']
        if len(match)!=1 or match[0][2]!=b'tmpfs' or b'rw' not in match[0][3].split(b','):raise ValueError('Writable tmpfs required')
        folder='/tmp/valethonos-observer-'+secrets.token_hex(16);destination=folder+'/sectors.bin'
        if adb.run(['exec-out','mkdir','-m','700',folder]):raise ValueError('Exclusive RAM staging failed')
        receipt['private_ram_staging']=folder;update_receipt(receipt_path,receipt)
        adb.push(data,destination)
        if sha(adb.read(destination,SIZE))!=target:raise ValueError('RAM upload differs')
        preflight(adb,originals,current,boot)
        receipt['write_started']=True;update_receipt(receipt_path,receipt)
        adb.run(['exec-out','dd','if='+destination,'of='+TARGET,'bs=512','seek=223223','count=962','conv=notrunc'])
        adb.run(['exec-out','sync'])
        preflight(adb,originals,target,boot)
        receipt['verified']=True;update_receipt(receipt_path,receipt)
        adb.run(['exec-out','rm',destination]);adb.run(['exec-out','rmdir',folder])
        if adb.run(['shell','if [ -e '+folder+' ]; then echo LEFT; else echo RAM_CLEAN; fi']).strip()!=b'RAM_CLEAN':raise ValueError('RAM cleanup unconfirmed')
        receipt['ram_cleanup_verified']=True
    finally:update_receipt(receipt_path,receipt)
    return receipt


def authorize(value):
    """Only the reviewed known-stack calibration; never a general logging waiver."""
    expected={'scope':'known-boot-capture-control-1',
              'candidate_sha256':KERNEL_CANDIDATE,'observer_sha256':CANDIDATE,
              'owner_approved':True,'owner_available':True,
              'minimum_seconds':300,'automatic_return':False}
    if not isinstance(value,dict) or any(type(value.get(k)) is not type(v) or value.get(k)!=v for k,v in expected.items()):
        raise ValueError('Fresh exact control approval and availability required')
