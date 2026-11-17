#!/usr/bin/env python3
"""Instrument exact pinned ACK bytes at named startup instructions, offline only.

Five PC-relative detours use proven-zero padding inside executable init text.
Original instructions/semantics are replayed; x0-x8, x18(SCS), x19-x30 are kept.
The pre-MMU hook adds a normal-NC identity map of the existing retained console.
No driver, storage, USB, IRQ or kernel image extent is changed here.
"""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from prepare_ack_native_bundle import IMAGE_SHA
SYSTEM_MAP_SHA='b2cb269a5935fda3c3507f0ae18f3de396aa4df109a5da34cfdc54cb01c5e144'
BASE=0x40000000
CAVE=0x1322000
CAVE_BYTES=0x3000
TABLE=0x42020000
CONSOLE=0x444bf000
STAGES=['linux_entry','before_mmu','after_mmu','virtual_entry','start_kernel']

def sha(b):return hashlib.sha256(b).hexdigest()

def line(token,stage):
 if not re.fullmatch('[0-9a-f]{32}',token) or stage not in STAGES+['map_refused']:
  raise ValueError('Exact combined stage/token required')
 return ('FIRETABS_ACK_COMBINED_V2 nonce='+token+' stage='+stage+'\n').encode()

def branch(at,to,link=False):
 d=to-at
 if d%4 or not -(1<<27)<=d<(1<<27):raise ValueError('Branch outside imm26 range')
 return (0x94000000 if link else 0x14000000)|((d//4)&0x3ffffff)

def adrp(word,old,new):
 if word&0x9f000000!=0x90000000:raise ValueError('Expected original ADRP')
 imm=((word>>29)&3)|(((word>>5)&0x7ffff)<<2)
 if imm&(1<<20):imm-=1<<21
 dest=(old&~4095)+(imm<<12);d=(dest-(new&~4095))//4096
 if not -(1<<20)<=d<(1<<20):raise ValueError('ADRP range')
 return (word&0x9f00001f)|((d&3)<<29)|(((d>>2)&0x7ffff)<<5)

def build(image,system_map,out,token):
 if sha(image)!=IMAGE_SHA or sha(system_map.encode())!=SYSTEM_MAP_SHA:raise ValueError('Exact pinned base Image/System.map required')
 sym={v[2]:int(v[0],16) for l in system_map.splitlines() if len(v:=l.split())==3};vbase=sym['_text']
 sites=[sym['primary_entry']-vbase,sym['__enable_mmu']-vbase,sym['__primary_switch']-vbase+16,sym['__primary_switched']-vbase,sym['start_kernel']-vbase+4]
 expected=[0x94006eb8,0xd503245f,0x0,0xd503245f,0xd100c3ff]
 originals=[struct.unpack_from('<I',image,p)[0] for p in sites]
 if originals[:2]!=expected[:2] or originals[3:]!=expected[3:] or originals[2]&0x9f00001f!=0x90000001:
  raise ValueError('Reviewed startup instructions changed')
 if not sym['__inittext_begin']-vbase<=CAVE<CAVE+CAVE_BYTES<=sym['__inittext_end']-vbase or any(image[CAVE:CAVE+CAVE_BYTES]):
  raise ValueError('Reviewed executable zero padding required')
 out.mkdir(mode=0o700)
 # Generate a fixed-size wrapper per site; resolved instruction PCs are verified
 # after linking, then branch/replay words are substituted without relocations.
 text=['.section .text,"ax"','.balign 8','.global hook_0']
 for i,stage in enumerate(STAGES):
  text += [f'hook_{i}:']
  if i==1:text += ['b install_console_map','map_installed:']
  if i>=2:text += ['mrs x9,sctlr_el1','tbz x9,#0,halt']
  text += [f'adr x15,msg_{i}',f'mov w16,#{len(line(token,stage))}',f'adr x17,done_{i}','b append_ring',f'done_{i}:',f'replay_{i}:','.word 0']
  if i==0:text += ['restore_lr_0:','.word 0']
  text += [f'return_{i}:','.word 0']
 text += ['install_console_map:',
 'mrs x9,CurrentEL','cmp x9,#4','b.ne halt',
 'mrs x9,sctlr_el1','tbnz x9,#0,halt',
 'mrs x9,tcr_el1','and x10,x9,#0x3f','cmp x10,#16','b.ne map_bad',
 'tbnz x9,#59,map_bad','ubfx x10,x9,#14,#2','cbnz x10,map_bad',
 # Root/L0/L1 tables are all inside the verified kernel memory extent.
 'mov x9,x2','mov x10,#0x40000000','ldr x11,extent_end',
 'cmp x9,x10','b.lo map_bad','cmp x9,x11','b.hs map_bad',
 'tst x9,#4095','b.ne map_bad','ldr x9,[x9]',
 'and x12,x9,#3','cmp x12,#3','b.ne map_bad','and x9,x9,#0x0000fffffffff000',
 'cmp x9,x10','b.lo map_bad','cmp x9,x11','b.hs map_bad','ldr x9,[x9,#8]',
 'and x12,x9,#3','cmp x12,#3','b.ne map_bad','and x9,x9,#0x0000fffffffff000',
 'cmp x9,x10','b.lo map_bad','cmp x9,x11','b.hs map_bad',
 'add x9,x9,#272','ldr x12,[x9]','cbnz x12,map_bad',
 # Find Normal-NC (0x44) in the kernel's programmed MAIR, rather than assume ID.
 'mrs x10,mair_el1','mov x11,#0','1: and x12,x10,#255','cmp x12,#0x44','b.eq 2f',
 'lsr x10,x10,#8','add x11,x11,#1','cmp x11,#8','b.lo 1b','b map_bad',
 '2: lsl x11,x11,#2','orr x11,x11,#3','orr x11,x11,#0x700',
 'orr x11,x11,#0x60000000000000','ldr x10,table_page','mov x12,#512',
 '3: str xzr,[x10],#8','subs x12,x12,#1','b.ne 3b',
 'ldr x10,table_page','ldr x12,console_address','mov x13,#16',
 '4: ubfx x14,x12,#12,#9','orr x15,x12,x11','str x15,[x10,x14,lsl #3]',
 'add x12,x12,#4096','subs x13,x13,#1','b.ne 4b',
 'orr x10,x10,#3','str x10,[x9]','dsb sy','b map_installed',
 'map_bad:','adr x15,msg_bad',f'mov w16,#{len(line(token,"map_refused"))}','adr x17,reset','b append_ring',
 'reset:','ldr x9,watchdog','mov w10,#0x1209','str w10,[x9,#0x14]','dsb sy',
 'halt:','wfe','b halt',
 # Only x9..x17 are clobbered. x18 must retain the kernel shadow-stack pointer.
 'append_ring:','ldr x9,console_address','ldr w10,[x9]','ldr w11,signature','cmp w10,w11','b.ne ring_done',
 'ldr w12,[x9,#4]','ldr w13,[x9,#8]','mov w14,#65524','cmp w12,w14','b.hs ring_done',
 'cmp w13,w14','b.hi ring_done','cmp w12,w13','b.hi ring_done','add w13,w13,w16','cmp w13,w14',
 'csel w13,w14,w13,hi','5: ldrb w11,[x15],#1','add x10,x9,x12','strb w11,[x10,#12]',
 'add w12,w12,#1','cmp w12,w14','csel w12,wzr,w12,eq','subs w16,w16,#1','b.ne 5b',
 'dsb sy','str w12,[x9,#4]','str w13,[x9,#8]','dsb sy','ring_done:','br x17',
 '.balign 8','extent_end: .quad 0x41ac0000',f'table_page: .quad {TABLE}',f'console_address: .quad {CONSOLE}',
 'watchdog: .quad 0x10007000','signature: .long 0x43474244']
 for i,stage in enumerate(STAGES):text += [f'msg_{i}:','.ascii '+json.dumps(line(token,stage).decode())]
 text += ['msg_bad:','.ascii '+json.dumps(line(token,'map_refused').decode())]
 src=out/'hooks.S';src.write_text('\n'.join(text)+'\n')
 obj=out/'hooks.o';elf=out/'hooks.elf';raw=out/'hooks.bin'
 subprocess.run(['clang','-target','aarch64-none-elf','-c',str(src),'-o',str(obj)],check=True)
 subprocess.run(['aarch64-linux-musl-ld','-Ttext='+hex(BASE+CAVE),'-e','hook_0','-o',str(elf),str(obj)],check=True)
 subprocess.run(['aarch64-linux-musl-objcopy','-O','binary','--only-section=.text',str(elf),str(raw)],check=True)
 names=subprocess.check_output(['aarch64-linux-musl-nm','--defined-only',str(elf)],text=True)
 hs={v[2]:int(v[0],16) for l in names.splitlines() if len(v:=l.split())==3}
 code=bytearray(raw.read_bytes())
 if len(code)>CAVE_BYTES:raise ValueError('Hooks exceed proven padding')
 patches=[]
 for i,site in enumerate(sites):
  at=hs[f'replay_{i}'];ret=hs[f'return_{i}'];original=originals[i]
  if i==0:
   # Original BL record_mmu_state: replay as BL from wrapper, then branch back.
   # record_mmu_state returns through LR; it does not rely on original call PC.
   d=original&0x3ffffff
   if d&(1<<25):d-=1<<26
   replay=branch(at,BASE+site+4*d,True)
   lr_at=hs['restore_lr_0'];delta=BASE+site+4-lr_at
   if not -(1<<20)<=delta<(1<<20):raise ValueError('Original LR outside ADR range')
   adr_word=0x1000001e|((delta&3)<<29)|(((delta>>2)&0x7ffff)<<5)
   struct.pack_into('<I',code,lr_at-(BASE+CAVE),adr_word)
  elif i==2:replay=adrp(original,BASE+site,at)
  else:replay=original
  struct.pack_into('<I',code,at-(BASE+CAVE),replay)
  struct.pack_into('<I',code,ret-(BASE+CAVE),branch(ret,BASE+site+4))
  patches.append(dict(stage=STAGES[i],offset=site,original_word=hex(original),hook=hs[f'hook_{i}'],replay=hex(replay)))
 patched=bytearray(image);patched[CAVE:CAVE+len(code)]=code
 for i,p in enumerate(patches):struct.pack_into('<I',patched,p['offset'],branch(BASE+p['offset'],p['hook']))
 # All changes are the five declared instructions and the verified zero cave.
 rebuilt=bytearray(image);rebuilt[CAVE:CAVE+len(code)]=code
 for p in patches:struct.pack_into('<I',rebuilt,p['offset'],branch(BASE+p['offset'],p['hook']))
 if patched!=rebuilt:raise ValueError('Unexpected image changes')
 report=dict(base_image_sha256=IMAGE_SHA,patched_image_sha256=sha(patched),cave_offset=CAVE,cave_bytes=len(code),
             patches=patches,console_identity_map=hex(CONSOLE),table_page=hex(TABLE),kernel_extent_unchanged=True,
             x18_scs_preserved=True,hardware_execution=False,target_kernel_boot_proven=False)
 (out/'Image').write_bytes(patched);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 return bytes(patched),report
