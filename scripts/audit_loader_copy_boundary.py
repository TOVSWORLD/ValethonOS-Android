#!/usr/bin/env python3
"""Sparse replay of exact Android bootstrap kernel-copy extent, no device."""
import argparse,hashlib,json,struct
from pathlib import Path
from validate_loader_allocator import EXPECTED
PAYLOAD_SHA='e10fdf770a5be2c2adc3cce0d03b8e296eac3b31e18ebdce5b56dc5491f4e7e8'
PAYLOAD_BLOCK=223223
LK=0x4bd00000
SITE=0x4bd3e3e8

def materialize(header,payload,original_lk):
 if header[:8]!=b'ANDROID!':raise ValueError('Android bootstrap header required')
 count,base=struct.unpack_from('<II',header,8);page=struct.unpack_from('<I',header,36)[0]
 if (count,base,page)!=(0x6d003c8,0x45000000,2048):raise ValueError('Unreviewed bootstrap copy contract')
 mapped=base+PAYLOAD_BLOCK*512-page;end=base+count
 assert mapped==0x4bcfe600 and end==LK+0x3c8
 if len(payload)!=492544:raise ValueError('Full bootstrap sector span required')
 resident_prefix=payload[:LK-mapped]
 ram=bytearray(original_lk[512:]);n=end-LK
 ram[:n]=payload[LK-mapped:LK-mapped+n]
 return resident_prefix,ram,{'payload_ram_start':hex(mapped),'kernel_copy_end':hex(end),'embedded_lk_bytes_copied':n}

def audit(header,payload,lk,old_observer):
 h=header.read_bytes();p=payload.read_bytes();b=lk.read_bytes()
 assert hashlib.sha256(b).hexdigest()==EXPECTED
 assert hashlib.sha256(p[:492132]).hexdigest()==PAYLOAD_SHA
 _,original,extent=materialize(h,p,b)
 o=old_observer.read_bytes();_,replayed,_=materialize(h,o,b)
 file_at=0x1a00+SITE-LK
 assert o[file_at:file_at+4]!=p[file_at:file_at+4]
 assert replayed[SITE-LK:SITE-LK+4]==original[SITE-LK:SITE-LK+4]==bytes.fromhex('dff82037')
 return {'scope':'Exact header and archived payload sparse copy replay. Pre-existing LK bytes supplied from pinned package, not an observation of physical RAM.',
 'header_sha256':hashlib.sha256(h).hexdigest(),'original_lk_sha256':EXPECTED,
 'old_observer_sha256':hashlib.sha256(o).hexdigest(),**extent,
 'old_embedded_hook_site':hex(SITE),'old_hook_copied_to_ram':False,
 'resident_main_calls_app_without_reloading_full_lk':True,
 'corrective_action':'Install late BL from resident main before its original whole-LK cache clean/app; validate the copy model, not a direct synthetic RAM hook.',
 'explains_all_missing_earlier_records':False,'kernel_entry_or_runtime_cause_proved':False,'device_accessed':False}
if __name__=='__main__':
 a=argparse.ArgumentParser()
 for n in ['header','payload','lk','old-observer','output']:a.add_argument('--'+n,type=Path,required=True)
 x=a.parse_args();r=audit(x.header,x.payload,x.lk,x.old_observer);x.output.write_text(json.dumps(r,indent=2)+'\n');print('Confirmed: only LK first968B copied; embedded late hook is outside real copy extent')
