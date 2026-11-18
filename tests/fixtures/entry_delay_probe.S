.section .text.start,"ax"
.global _start
_start:
 mov x0, #0x42000000
 mov sp, x0
 bl main
 sub sp, sp, #16
 mov x1, #0x26
 movk x1, #2, lsl #16
 stp x1,x0,[sp]
 mov x1,sp
 mov x0,#0x20
 hlt #0xf000
1:b 1b
.text
.global invoke_entry_delay
invoke_entry_delay:
 stp x19,x20,[sp,#-64]!
 stp x21,x30,[sp,#16]
 str x18,[sp,#32]
 mov x18,#0x1825
 mov x19,#0x1937
 mov x20,#0x2049
 mov x21,#0x215b
 mov x0,#0x1234
 mov x1,#0x5678
 mov x2,#0x9abc
 mov x3,#0xdef0
 bl valethon_entry_delay
 mov x4,#0x1234
 cmp x0,x4
 b.ne 8f
 mov x4,#0x5678
 cmp x1,x4
 b.ne 8f
 mov x4,#0x9abc
 cmp x2,x4
 b.ne 8f
 mov x4,#0xdef0
 cmp x3,x4
 b.ne 8f
 mov x4,#0x1825
 cmp x18,x4
 b.ne 8f
 mov x4,#0x1937
 cmp x19,x4
 b.ne 8f
 mov x4,#0x2049
 cmp x20,x4
 b.ne 8f
 mov x4,#0x215b
 cmp x21,x4
 b.ne 8f
 mov w0,#0
 b 9f
8:mov w0,#1
9:
 ldr x18,[sp,#32]
 ldp x21,x30,[sp,#16]
 ldp x19,x20,[sp],#64
 ret
