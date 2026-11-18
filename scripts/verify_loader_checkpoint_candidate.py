#!/usr/bin/env python3
"""Independent offline byte/seed/descriptor checks; no physical operations."""
import argparse,hashlib,json,struct,gzip,zlib
from pathlib import Path
import retained_log_mailbox as m
from validate_loader_console_reclaim import SPANS
from validate_loader_complete import raw_elf,BASE
from validate_loader_relocation import relative_references
from validate_loader_checkpoint import elf
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB

def sha(b):return hashlib.sha256(b).hexdigest()
def components(image):
 page=struct.unpack_from('<I',image,36)[0];k=struct.unpack_from('<I',image,8)[0];r=struct.unpack_from('<I',image,16)[0];kernel=image[page:page+k];dec=zlib.decompressobj(31);decoded=dec.decompress(kernel);used=len(kernel)-len(dec.unused_data);dt=kernel[(used+3)&~3:];at=page+((k+page-1)//page)*page;ramdisk=image[at:at+r]
 digest=hashlib.sha1()
 for data in [kernel,ramdisk,b'']:digest.update(data);digest.update(struct.pack('<I',len(data)))
 assert image[576:596]==digest.digest()
 return kernel[:used],decoded,dt,gzip.decompress(ramdisk)
def dt_nonce(dt):
 magic,total,off,strings=struct.unpack_from('>4I',dt);assert magic==0xd00dfeed and total==len(dt);nodes=[];values=[]
 while off<len(dt):
  token=struct.unpack_from('>I',dt,off)[0];off+=4
  if token==1:
   end=dt.index(b'\0',off);nodes.append(dt[off:end]);off=(end+4)&~3
  elif token==2:nodes.pop()
  elif token==3:
   n,name=struct.unpack_from('>II',dt,off);off+=8;end=dt.index(b'\0',strings+name)
   if dt[strings+name:end]==b'valethon,trial-nonce' and nodes==[b'',b'chosen']:values.append(dt[off:off+n])
   off=(off+n+3)&~3
  elif token==4:continue
  elif token==9:break
  else:raise ValueError('Unexpected DT structure')
 assert len(values)==1 and len(values[0])==32;return values[0]
def verify(folder,base,original,bootstrap,module,parent=None):
 manifest=json.loads((folder/'manifest.json').read_text());report=json.loads((folder/'report.json').read_text());image=(folder/'boot-full.img').read_bytes();obs=(folder/'observer-payload-sectors-private.bin').read_bytes();blob=(folder/'module.bin').read_bytes();nonce=(folder/'nonce.bin').read_bytes();old=base.read_bytes();orig=original.read_bytes()
 if parent:
  before=parent.read_bytes();old_gzip,old_kernel,old_dt,old_archive=components(before);new_gzip,new_kernel,new_dt,new_archive=components(image);old_nonce=dt_nonce(old_dt)
  assert dt_nonce(new_dt)==nonce and old_nonce!=nonce and old_gzip==new_gzip and old_kernel==new_kernel
  assert old_dt.count(old_nonce)==1 and new_dt==old_dt.replace(old_nonce,nonce) and old_archive.count(old_nonce)==1 and new_archive==old_archive.replace(old_nonce,nonce)
 assert sha(image)==manifest['candidate_sha256']==report['partition_sha256'] and sha(obs)==manifest['observer_sha256'] and sha(orig)==manifest['original_bootstrap_sha256']
 page=struct.unpack_from('<I',image,36)[0];sizes=[struct.unpack_from('<I',image,x)[0] for x in [8,16,24,40]];declared=page+sum((n+page-1)//page*page for n in sizes);assert page==2048 and image[:declared]==old[:declared] and declared<12*1024*1024
 offset=manifest['module_file_padding_offset'];assert image[declared:offset]==old[declared:offset] and image[offset:offset+len(blob)]==blob and image[offset+len(blob):m.BASE]==old[offset+len(blob):m.BASE]
 assert sha(blob)==manifest['module_blob_sha256'] and len(blob)==manifest['module_bytes']
 state=m.inspect(image,nonce,manifest['prefix_sha256']);assert not state['invalid_slots'] and state['latest']['sequence']==1 and state['latest']['payload'].startswith(b'VALETHON HOST CONTROL v1\n')
 assert sha(image[m.BASE:m.SLOT_BASE])==manifest['seed_sha256']
 sections,symbols=raw_elf(bootstrap);at=0xa00+symbols['lbo_load_plan']-BASE;plan=struct.unpack_from('<6I32sQQ',obs,at)
 assert plan[:3]==(len(blob),manifest['state_bytes'],4096) and plan[3]==plan[4] and plan[5]==1 and plan[6]==hashlib.sha256(blob).digest() and plan[7:]==(18432,offset)
 at=0xa00+symbols['lbo_frontend']-BASE;config=struct.unpack_from('<32s32sQQ5I4xI',obs,at);assert config==(nonce,bytes.fromhex(manifest['prefix_sha256']),18432,30325760,m.PARTITION,5,8,1,1,BASE+9)
 pre_shutdown=manifest.get('snapshot_stage')=='pre_shutdown'
 site=0x3e3e8 if pre_shutdown else 0x3e524
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
 for file_at,address,target in [(0xa72,BASE+0x72,symbols['lbo_read']&~1),
                               (0x1a00+site,0x4bd00000+site,symbols['lbo_pre_shutdown' if pre_shutdown else 'lbo_handoff']&~1)]:
  decoded=list(md.disasm(obs[file_at:file_at+4],address))
  assert len(decoded)==1 and decoded[0].size==4 and decoded[0].mnemonic=='bl' and int(decoded[0].op_str.removeprefix('#'),16)==target
 for address,data in sections:
  expected=bytearray(data)
  for name,size in [('lbo_load_plan',72),('lbo_frontend',112)]:
   start=symbols[name]
   if address<=start and start+size<=address+len(data):
    offset=start-address;file_at=0xa00+start-BASE;expected[offset:offset+size]=obs[file_at:file_at+size]
  assert obs[0xa00+address-BASE:0xa00+address-BASE+len(data)]==bytes(expected)
 allowed={i for lo,hi in SPANS for i in range(0xa00+lo,0xa00+hi)}|set(range(0x1136,0x113a))|set(range(0x1178,0x117c))|set(range(0xa72,0xa76))|set(range(0x1a00+site,0x1a00+site+4))
 if pre_shutdown:assert obs[0x1a00+0x3e524:0x1a00+0x3e528]==orig[0x1a00+0x3e524:0x1a00+0x3e528]
 assert {i for i,(a,b) in enumerate(zip(orig,obs)) if a!=b}<=allowed and len(obs)==len(orig)==492544
 kinds={};objects={}
 for p in module.parent.glob('*.o'):
  objects[p.name]=sha(p.read_bytes())
  for k,n in relative_references(p.read_bytes()).items():kinds[k]=kinds.get(k,0)+n
 seg,entries=elf(module,('lfo_frame_dispatch',));assert plan[3]==(entries['lfo_frame_dispatch']-0x41000000)|1
 flat=bytearray(len(blob))
 for address,data in seg:flat[address-0x41000000:address-0x41000000+len(data)]=data
 assert bytes(flat)==blob
 return {'scope':'Independent exact candidate/descriptor/padding/seed/object checks; no physical acceptance','candidate_sha256':sha(image),'observer_sha256':sha(obs),'fresh_base_declared_image_unchanged':True,'parent_kernel_instructions_unchanged':bool(parent),'parent_dt_pid1_only_nonce_bytes_changed':bool(parent),'prefix_seed_exact':True,'new_prefix_differs_from_base':sha(image[:m.BASE])!=sha(old[:m.BASE]),'no_old_prefix_record_reused':True,'module_objects':objects,'allocated_relocation_types':kinds,'private_device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();
 for n in ['folder','base','original','bootstrap','module','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--parent',type=Path);a=p.parse_args();r=verify(a.folder,a.base,a.original,a.bootstrap,a.module,a.parent);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Independent exact checkpoint candidate checks passed')
