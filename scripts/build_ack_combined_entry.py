#!/usr/bin/env python3
"""Link a deadline-bounded RAM entry with full padded-Image SHA-256 verification."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from build_ack_trampoline import marker
ROOT=Path(__file__).resolve().parents[1]
ENTRY=0x42018000
END=0x42020000
STACK=0x42028000

def integrity_marker(token,ok):
 if not re.fullmatch('[0-9a-f]{32}',token):raise ValueError('Fresh exact token required')
 return ('FIRETABS_ACK_COMBINED_V2 nonce='+token+' stage='+('image_verified' if ok else 'image_corrupt')+'\n').encode()

def build(out,token,padded_image):
 if not 0<len(padded_image)<=32*1024*1024 or len(padded_image)%4096:raise ValueError('Full page-aligned Image extent required')
 out.mkdir(mode=0o700)
 source=(ROOT/'projects/firetabs-android/native-kexec/ack_trampoline.S').read_text()
 # Retain reviewed state/deadline/readback/ABI code; put integrity before marker.
 source=source.replace('.section .text.ack_trampoline, "ax"','.section .text.entry, "ax"')
 source=source.replace(' ldr x9, .Lconsole\n', ''' ldr x0, .Limage
 ldr x1, .Limage_extent
 adr x2, .Lexpected_hash
 ldr x9, .Lstack
 mov sp,x9
 bl combined_verify
 cbnz x0,.Limage_bad
 adr x15,.Lverified
 mov w16,#(.Lverified_end-.Lverified)
 adr x17,.Lverified_done
 b .Lappend_external
.Lverified_done:
 ldr x9, .Lconsole
''',1)
 # Share ring append without perturbing return register x30 after the SHA call.
 # A second bounded append entry accepts x15/x16 and returns through x17.
 source=source.replace(' adr x15, .Lmarker\n mov w16, #(.Lmarker_end - .Lmarker)', ' adr x15, .Lmarker\n mov w16, #(.Lmarker_end - .Lmarker)\n mov x17,xzr')
 source=source.replace(' dsb sy\n.Lenter:', ' dsb sy\n cbnz x17,.Lexternal_done\n.Lenter:')
 source=source.replace(' add w13, w13, #(.Lmarker_end - .Lmarker)', ' add w13, w13, w23')
 source=source.replace('.Lappend:\n',' mov w23,w16\n.Lappend:\n')
 # Original append uses x18/x19, which are free at metadata entry, not kernel hooks.
 source += '''
.balign 4
.Lappend_external:
 ldr x9,.Lconsole
 ldr w10,[x9]
 ldr w11,.Lsignature
 cmp w10,w11
 b.ne .Lexternal_done
 ldr w12,[x9,#4]
 ldr w13,[x9,#8]
 mov w14,#65524
 cmp w12,w14
 b.hs .Lexternal_done
 cmp w13,w14
 b.hi .Lexternal_done
 cmp w12,w13
 b.hi .Lexternal_done
 mov w23,w16
 b .Lappend
.Lexternal_done:
 br x17
.Limage_bad:
 adr x15,.Lcorrupt
 mov w16,#(.Lcorrupt_end-.Lcorrupt)
 adr x17,.Lcorrupt_done
 b .Lappend_external
.Lcorrupt_done:
 ldr x9,.Lwatchdog
 b .Lreset
.balign 8
.Lstack: .quad '''+hex(STACK)+'''
.Limage_extent: .quad '''+str(len(padded_image))+'''
.Lexpected_hash:
.byte '''+','.join(str(b) for b in hashlib.sha256(padded_image).digest())+'''
.Lverified:
.ascii '''+json.dumps(integrity_marker(token,True).decode())+'''
.Lverified_end:
.Lcorrupt:
.ascii '''+json.dumps(integrity_marker(token,False).decode())+'''
.Lcorrupt_end:
'''
 (out/'entry.S').write_text(source)
 line=marker(token)
 (out/'ack_marker.inc').write_text('.ascii '+json.dumps(line.decode())+'\n')
 subprocess.run(['clang','-target','aarch64-none-elf','-c',str(out/'entry.S'),'-Wa,-I,'+str(out.resolve()),'-o',str(out/'entry.o')],check=True)
 subprocess.run(['aarch64-linux-musl-gcc','-O2','-std=c11','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-stack-protector','-mgeneral-regs-only','-fno-asynchronous-unwind-tables','-c',str(ROOT/'projects/firetabs-android/native-kexec/combined_sha256.c'),'-o',str(out/'sha.o')],check=True)
 (out/'entry.ld').write_text('SECTIONS { . = '+hex(ENTRY)+'; .text : { *(.text.entry) *(.text*) *(.rodata*) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }')
 subprocess.run(['aarch64-linux-musl-ld','-T',str(out/'entry.ld'),'-e','ack_trampoline','-o',str(out/'entry.elf'),str(out/'entry.o'),str(out/'sha.o')],check=True)
 subprocess.run(['aarch64-linux-musl-objcopy','-O','binary',str(out/'entry.elf'),str(out/'entry.bin')],check=True)
 data=(out/'entry.bin').read_bytes()
 if len(data)>END-ENTRY:raise ValueError('Entry/hash code overlaps table page')
 if any(data.count(x)!=1 for x in [line,integrity_marker(token,True),integrity_marker(token,False)]):raise ValueError('Fresh markers missing or duplicated')
 report=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),deadline_seconds=31,
             image_extent_verified_bytes=len(padded_image),expected_padded_image_sha256=hashlib.sha256(padded_image).hexdigest(),
             stack_top=STACK,table_page=END,hardware_execution=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 return data,report
