/* SPDX-License-Identifier: GPL-2.0-only
 * One maintained-kernel RAM handoff. Existing source shutdown/relocation remain
 * unchanged. Arm a reset-only 31-second hardware deadline after shutdown, append
 * a handoff-only retained marker, then supply the ordinary ARM64 Image ABI.
 * Target DT must disable its watchdog and all disk controllers/log writers.
 */
.section .text.ack_trampoline, "ax"
.balign 8
.global ack_trampoline
ack_trampoline:
 msr daifset, #15
 mrs x20, CurrentEL
 cmp x20, #4
 b.eq .Lel1
 cmp x20, #8
 b.ne .Lhalt
 mrs x21, sctlr_el2
 b .Lstate
.Lel1:
 mrs x21, sctlr_el1
.Lstate:
 mov x22, #5
 tst x21, x22
 b.ne .Lhalt
 ldr x9, .Lwatchdog
 ldr w10, [x9]
 mov w11, #0x6b             /* EN, polarity, IRQ, IRQ-level, dual */
 bic w10, w10, w11
 mov w11, #0x22000000
 orr w10, w10, w11
 orr w10, w10, #4           /* external reset */
 orr w10, w10, #0x10        /* normal auto-start */
 str w10, [x9]             /* disabled while programming length */
 mov w11, #0xf808           /* 31 seconds, LENGTH key 8 */
 str w11, [x9, #4]
 mov w11, #0x1971
 str w11, [x9, #8]
 orr w10, w10, #1
 str w10, [x9]
 dsb sy
 ldr w11, [x9]
 and w11, w11, #0x7f
 cmp w11, #0x15
 b.ne .Lreset
 ldr w11, [x9, #4]
 and w11, w11, #0xffe0
 mov w12, #0xf800
 cmp w11, w12
 b.ne .Lreset

 ldr x9, .Lconsole
 ldr w10, [x9]
 ldr w11, .Lsignature
 cmp w10, w11
 b.ne .Lenter
 ldr w12, [x9, #4]
 ldr w13, [x9, #8]
 mov w14, #65524
 cmp w12, w14
 b.hs .Lenter
 cmp w13, w14
 b.hi .Lenter
 cmp w12, w13
 b.hi .Lenter
 adr x15, .Lmarker
 mov w16, #(.Lmarker_end - .Lmarker)
.Lappend:
 ldrb w18, [x15], #1
 add x19, x9, x12
 strb w18, [x19, #12]
 add w12, w12, #1
 cmp w12, w14
 csel w12, wzr, w12, eq
 subs w16, w16, #1
 b.ne .Lappend
 dsb sy
 add w13, w13, #(.Lmarker_end - .Lmarker)
 cmp w13, w14
 csel w13, w14, w13, hi
 str w12, [x9, #4]
 str w13, [x9, #8]
 dsb sy
.Lenter:
 ldr x9, .Lwatchdog
 mov w10, #0x1971
 str w10, [x9, #8]          /* full deadline starts at Linux entry */
 dsb sy
 ldr x0, .Lfdt
 mov x1, xzr
 mov x2, xzr
 mov x3, xzr
 ldr x16, .Limage
 br x16
.Lreset:
 mov w10, #0x1209
 str w10, [x9, #0x14]       /* do not enter Linux after bad readback */
 dsb sy
.Lhalt:
 wfe
 b .Lhalt
.balign 8
.Lwatchdog: .quad 0x10007000
.Lconsole: .quad 0x444bf000
.Lfdt: .quad 0x42000000
.Limage: .quad 0x40000000
.Lsignature: .long 0x43474244
.Lmarker:
.include "ack_marker.inc"
.Lmarker_end:
