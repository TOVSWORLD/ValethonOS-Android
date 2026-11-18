/* SPDX-License-Identifier: GPL-2.0-only
 * One-shot diagnostic target. Entered through the existing native relocation
 * and DT trampoline, with translation/data cache disabled. No Linux startup.
 * Append a target-only nonce to the existing, ECC-free retained console ring,
 * then use the platform driver's ordinary watchdog software-reset sequence.
 * Never touch NONRST/RTC flags, flash, boot arguments or arbitrary memory.
 */
.section .text.reset_payload, "ax"
.balign 8
.global reset_payload_image
reset_payload_image:
 b .Lentry
 .long 0
 .quad 0x80000
 .quad 4096
 .quad 10
 .quad 0, 0, 0
 .long 0x644d5241
 .long 0
.Lentry:
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
 mov x22, #5                 /* SCTLR.M | SCTLR.C must already be clear. */
 tst x21, x22
 b.ne .Lhalt

 ldr x9, .Lconsole
 ldr w10, [x9]
 ldr w11, .Lsignature
 cmp w10, w11
 b.ne .Lreset
 ldr w12, [x9, #4]          /* next write position */
 ldr w13, [x9, #8]          /* retained byte count */
 mov w14, #65524            /* 64 KiB minus the existing 12-byte header */
 cmp w12, w14
 b.hs .Lreset
 cmp w13, w14
 b.hi .Lreset
 cmp w12, w13
 b.hi .Lreset
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
 dsb sy                     /* Publish bytes before ring metadata. */
 add w13, w13, #(.Lmarker_end - .Lmarker)
 cmp w13, w14
 csel w13, w14, w13, hi
 str w12, [x9, #4]
 str w13, [x9, #8]
 dsb sy
.Lreset:
 ldr x9, .Lwatchdog
 ldr w10, [x9]
 mov w11, #0x49             /* clear dual, IRQ and enable, as reset handler */
 bic w10, w10, w11
 orr w10, w10, #0x10        /* ordinary restart's auto-start policy */
 mov w11, #0x22000000       /* WDT_MODE_KEY */
 orr w10, w10, w11
 str w10, [x9]
 dsb sy
 mov w10, #0x1209           /* WDT_SWRST_KEY */
 str w10, [x9, #0x14]
 dsb sy
.Lhalt:
 wfe
 b .Lhalt
.balign 8
.Lconsole: .quad 0x444bf000
.Lwatchdog: .quad 0x10007000
.Lsignature: .long 0x43474244
.Lmarker:
.include "reset_marker.inc"
.Lmarker_end:
