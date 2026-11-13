.section .text.start,"ax"
.global _start
_start:
 mov x0, #0x42000000
 mov sp, x0
 bl main
 sub sp, sp, #16
 mov x1, #0x26
 movk x1, #2, lsl #16
 stp x1, x0, [sp]
 mov x1, sp
 mov x0, #0x20
 hlt #0xf000
1: b 1b
.text
.global invoke_marker
invoke_marker:
 stp x19,x20,[sp,#-48]!
 stp x21,x30,[sp,#16]
 str x0,[sp,#32]
 mov x21,x0
 mov x19,#0x1937
 mov x20,#0x2049
 mov x0,#0x1234
 bl valethon_lab_entry_screen
 mov x12,#0x1234
 cmp x0,x12
 b.ne 8f
 mov x12,#0x1937
 cmp x19,x12
 b.ne 8f
 mov x12,#0x2049
 cmp x20,x12
 b.ne 8f
 ldr x12,[sp,#32]
 cmp x21,x12
 b.ne 8f
 mov w0,#0
 b 9f
8: mov w0,#1
9:
 ldp x21,x30,[sp,#16]
 ldp x19,x20,[sp],#48
 ret
