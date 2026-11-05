#!/usr/bin/env python3
"""Decode loader metadata inside an already nonce/CRC-validated VLOG record."""
import struct
TAG=b'VALETHON LOADER CHECKPOINT v1\n'
BODY=struct.Struct('<9I4Q32s32s')
STAGES={1:'mode',2:'image_read',3:'pre_handoff'}


def decode(payload,nonce,prefix_sha256):
    if not payload.startswith(TAG):return None
    if len(payload)!=len(TAG)+BODY.size:raise ValueError('Loader checkpoint length differs')
    stage,mode,kind,partition,hwpart,size,destination,entry,dt,target,selected_first,requested,selected,prefix,bound_nonce=BODY.unpack_from(payload,len(TAG))
    if stage not in STAGES or mode!=0 or partition!=5 or hwpart!=8 or not target or prefix.hex()!=prefix_sha256 or bound_nonce!=nonce:
        raise ValueError('Loader checkpoint binding/identity differs')
    if stage==2:
        if kind not in [1,2]:raise ValueError('Loader read kind differs')
    elif any([kind,size,destination,selected_first,requested,selected]):raise ValueError('Unexpected non-read fields')
    if stage!=3 and (entry or dt):raise ValueError('Unexpected pre-handoff arguments')
    return {'producer':'loader','stage':STAGES[stage],'gpt_partition':partition,'mmc_hardware_partition':hwpart,
            'record_storage_first_sector':target,'selected_partition_first_sector':selected_first if stage==2 else None,
            'read_kind':{1:'header',2:'body'}.get(kind),'requested_read_offset':requested if stage==2 else None,
            'selected_read_offset':selected if stage==2 else None,'read_bytes':size if stage==2 else None,
            'read_destination':destination if stage==2 else None,'kernel_entry':entry if stage==3 else None,
            'dt_address':dt if stage==3 else None,'kernel_record':False,'kernel_entry_proved':False}
