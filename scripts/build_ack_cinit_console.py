#!/usr/bin/env python3
"""Pinned diagnostic RAM early-console patch; no UART, storage or reset operations."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from build_ack_kernel_hooks import branch,SYSTEM_MAP_SHA
from prepare_ack_native_bundle import IMAGE_SHA
BASE=0x40000000
CAVE=0xbdc000
LIMIT=0x2000
SETUP=0x12bfd88
CAPACITY=4084
PREFIX='FIRETABS_CINIT_V3 nonce='

def sha(b):return hashlib.sha256(b).hexdigest()
def prefix(nonce):
 if not re.fullmatch('[0-9a-f]{64}',nonce):raise ValueError('Exact fresh PID1 identity required')
 return (PREFIX+nonce+'\n').encode()

def build(image,system_map,out,nonce):
 if sha(image)!=IMAGE_SHA or sha(system_map.encode())!=SYSTEM_MAP_SHA:raise ValueError('Pinned Image/System.map required')
 symbols={v[2]:int(v[0],16) for l in system_map.splitlines() if len(v:=l.split())==3}
 if not symbols['__hyp_text_end']-symbols['_text']<=CAVE<CAVE+LIMIT<=symbols['_etext']-symbols['_text'] or any(image[CAVE:CAVE+LIMIT]):raise ValueError('Permanent executable zero padding required')
 if struct.unpack_from('<II',image,SETUP)!=(0xd503233f,0xa9be7bfd):raise ValueError('Reviewed setup PAC/prologue required')
 for offset,word in [(SETUP+0x10,0xf9400c08),(SETUP+0x5c,0xf9000909),(0x704040,0xf9403408)]:
  if struct.unpack_from('<I',image,offset)[0]!=word:raise ValueError('Compiled early-console ABI differs')
 # Compiled ABI corroborated at early_serial8250_setup/write and PL011 write:
 # earlycon_device.con=0, port.membase=24; console.write=16, console.data=104.
 # FIX_EARLYCON_MEM maps one 4KiB page. Keep its complete DBGC ring inside
 # that page (12-byte header +4084-byte data); original ramoops accepts it.
 src='''
.section .text,"ax"
.balign 8
.global cinit_setup
cinit_setup:
 ldr x8,[x0]
 cbz x8,setup_bad
 ldr x9,[x0,#24]
 cbz x9,setup_bad
 ldr w10,[x9]
 ldr w11,signature
 cmp w10,w11
 b.ne setup_bad
 str wzr,[x9,#4]
 str wzr,[x9,#8]
 dsb sy
 adr x10,cinit_write
 str x10,[x8,#16]
 str xzr,[x8,#24]
 stp x29,x30,[sp,#-16]!
 mov x29,sp
 mov x0,x8
 adr x1,ready
 mov w2,#ready_end-ready
 bl cinit_write
 ldp x29,x30,[sp],#16
 mov w0,wzr
 autiasp
 ret
setup_bad:
 mov w0,#-19
 autiasp
 ret
.balign 8
.global cinit_write
cinit_write:
 bti c
 // Match ordinary console ABI; preserve all callee-saved registers and x18.
 // IRQ masking serializes the one-CPU diagnostic writer; no calls/allocations.
 mrs x3,daif
 msr daifset,#2
 ldr x8,[x0,#104]
 cbz x8,write_done
 ldr x9,[x8,#24]
 cbz x9,write_done
 ldr w10,[x9]
 ldr w11,signature
 cmp w10,w11
 b.ne write_done
 ldr w12,[x9,#4]
 ldr w13,[x9,#8]
 mov w14,#4084
 cmp w12,w14
 b.hs write_done
 cmp w13,w14
 b.hi write_done
 cmp w12,w13
 b.hi write_done
 // Each console write carries its fresh full PID1 identity. Keep the tail of
 // oversized writes, bounded below the ring size, so diagnostics stay finite.
 mov x4,#2048
 cmp x2,x4
 b.ls 1f
 sub x5,x2,x4
 add x1,x1,x5
 mov x2,x4
1:
 adr x15,identity
 mov w16,#identity_end-identity
 adr x17,after_identity
 b append
 after_identity:
 mov x15,x1
 mov x16,x2
 adr x17,write_finish
 cbz x16,write_finish
 b append
append:
 add w13,w13,w16
 cmp w13,w14
 csel w13,w14,w13,hi
2:
 ldrb w11,[x15],#1
 add x10,x9,x12
 strb w11,[x10,#12]
 add w12,w12,#1
 cmp w12,w14
 csel w12,wzr,w12,eq
 subs w16,w16,#1
 b.ne 2b
 br x17
write_finish:
 dsb sy
 str w12,[x9,#4]
 str w13,[x9,#8]
 dsb sy
write_done:
 msr daif,x3
 ret
.balign 8
signature: .long 0x43474244
identity:
.ascii IDENTITY
identity_end:
ready:
.ascii "retained_early_console_ready\\n"
ready_end:
'''.replace('IDENTITY',json.dumps(prefix(nonce).decode()))
 out.mkdir(mode=0o700);(out/'console.S').write_text(src)
 subprocess.run(['clang','-target','aarch64-none-elf','-c',str(out/'console.S'),'-o',str(out/'console.o')],check=True)
 subprocess.run(['aarch64-linux-musl-ld','-Ttext='+hex(BASE+CAVE),'-e','cinit_setup','-o',str(out/'console.elf'),str(out/'console.o')],check=True)
 subprocess.run(['aarch64-linux-musl-objcopy','-O','binary','--only-section=.text',str(out/'console.elf'),str(out/'console.bin')],check=True)
 code=(out/'console.bin').read_bytes()
 if len(code)>LIMIT:raise ValueError('Console exceeds permanent text padding')
 im=bytearray(image);im[CAVE:CAVE+len(code)]=code;struct.pack_into('<I',im,SETUP+4,branch(BASE+SETUP+4,BASE+CAVE))
 report=dict(base_image_sha256=IMAGE_SHA,patched_image_sha256=sha(im),setup_detour_offset=SETUP+4,setup_original_word='0xa9be7bfd',permanent_cave_offset=CAVE,code_bytes=len(code),code_sha256=sha(code),ring_capacity=CAPACITY,physical_page=0x444bf000,fixmap_earlycon=True,uart_mmio_accesses=False,storage_accesses=False,reset_operations=False,kernel_extent_unchanged=True,hardware_execution=False)
 (out/'Image').write_bytes(im);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');return bytes(im),report
