#!/usr/bin/env python3
"""Independent byte/copy/placement verifier; no writes to candidate or device."""
import argparse,hashlib,json,struct
from pathlib import Path
from validate_loader_complete import raw_elf,BASE
from validate_loader_observer import bl
from audit_loader_copy_boundary import materialize,SITE,LK
import retained_log_mailbox as m
PREFIX=0x4bcfe600
def sha(b):return hashlib.sha256(b).hexdigest()
def verify(folder,module,bootstrap,header,lk,original_sectors,original_boot):
 manifest=json.loads((folder/'manifest.json').read_text());image=(folder/'boot-full.img').read_bytes();obs=(folder/'observer-payload-sectors-private.bin').read_bytes();nonce=(folder/'nonce.bin').read_bytes();before=original_sectors.read_bytes();boot=original_boot.read_bytes()
 assert sha(before)=='4c6f355c735b9302b0d421ef38f94a9974214d531fa974a41edd8132af7ac092' and sha(boot)=='08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e'
 assert sha(image)==manifest['candidate_sha256'] and sha(obs)==manifest['observer_sha256']
 assert sha(module.read_bytes())==manifest['module_sha256'] and sha(bootstrap.read_bytes())==manifest['bootstrap_sha256']
 assert sha(nonce)==manifest['nonce_sha256'] and f'{int.from_bytes(nonce[:2],"little"):04x}'==manifest['screen_token']
 assert image[:7796736]==boot[:7796736] and len(image)==16777216
 assert image[7796736:12*1024*1024]==boot[7796736:12*1024*1024]
 m.validate_seed(image,nonce,manifest['prefix_sha256']);assert m.inspect(image,nonce,manifest['prefix_sha256'])['latest']['sequence']==1
 assert sha(image[m.BASE:m.SLOT_BASE])==manifest['seed_sha256']
 module_bytes=(folder/'module.bin').read_bytes();assert sha(module_bytes)==manifest['module_blob_sha256'] and image[12*1024*1024:12*1024*1024+len(module_bytes)]==module_bytes
 assert image[12*1024*1024+len(module_bytes):m.BASE]==boot[12*1024*1024+len(module_bytes):m.BASE]
 sections,bs=raw_elf(bootstrap);expected=bytearray(before)
 for at,data in sections:
  assert PREFIX<=at and at+len(data)<=PREFIX+0x900
  expected[at-PREFIX:at-PREFIX+len(data)]=data
 # Independently bound load descriptors to actual ELF entries and exact image.
 _,ms=raw_elf(module);entry=(ms['lfo_frame_dispatch']-0x41000000)|1
 replacements={'lbo_load_plan':struct.pack('<6I32sQQ',len(module_bytes),manifest['state_bytes'],4096,entry,entry,1,hashlib.sha256(module_bytes).digest(),18432,12*1024*1024),
 'lbo_frontend':struct.pack('<32s32sQQ5I4xI4x',nonce,bytes.fromhex(manifest['prefix_sha256']),18432,30325760,16777216,5,8,1,1,BASE+9),
 'lbo_hook_word':bl(SITE,bs['lbo_pre_shutdown']&~1)}
 for name,data in replacements.items():
  start=bs[name]-PREFIX;assert obs[start:start+len(data)]==data;expected[start:start+len(data)]=data
 expected[0xd86:0xd8a]=bl(BASE+0x386,bs['lbo_arrival']&~1)
 expected[0x1136:0x113a]=expected[0x1178:0x117c]=bytes.fromhex('00207047')
 struct.pack_into('<II',expected,0x964,PREFIX,0x1a00)
 assert obs==expected and obs[0x1a00:]==before[0x1a00:] and obs[0xa72:0xa76]==before[0xa72:0xa76]
 prefix,ram,extent=materialize(header.read_bytes(),obs,lk.read_bytes())
 assert ram[SITE-LK:SITE-LK+4]==bytes.fromhex('dff82037')
 assert all(prefix[at-PREFIX:at-PREFIX+len(data)]==obs[at-PREFIX:at-PREFIX+len(data)] for at,data in sections)
 assert struct.unpack_from('<7I',obs,0x960)==(0x4bd72a5f,PREFIX,0x1a00,0x4bd3c740,0x4bd00151,0xdead,BASE)
 return {'scope':'Independent exact candidate/nonce/seed/module/bootstrap/descriptor/ROP/copy verifier; no candidate mutation or device access',
 'candidate_sha256':sha(image),'observer_sha256':sha(obs),**extent,
 'all_original_declared_boot_bytes_preserved':True,'all_embedded_lk_bytes_unchanged':True,
 'late_hook_requires_runtime_installer':True,'all_executable_bytes_within_proven_copy_and_cache_span':True,
 'headers_gpt_return_bootstrap_and_live_globals_unchanged':True,'fresh_seed_only_hostcontrol':True,
 'physical_execution_admitted':False,'device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for key in ['folder','module','bootstrap','header','lk','original-sectors','original-boot','output']:p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();r=verify(a.folder,a.module,a.bootstrap,a.header,a.lk,a.original_sectors,a.original_boot);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Independent exact candidate/copy/ROP/descriptor checks passed')
