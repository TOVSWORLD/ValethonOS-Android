/* Private board-only earliest checkpoint. No DT, stack, driver or reset writes.
 * x0-x8/x18-x30/SP preserved. EL1 white, EL2 green, EL3 magenta opaque bands.
 * Only paint with MMU off. If C is on, validate line size and clean exact FB to PoC.
 * Valid architected counter: <=8s dwell; otherwise skip. Finite instruction budget
 * protects a stopped counter, but is not a calibrated wall limit in that case.
 */
.balign 8
SYM_CODE_START_LOCAL(valethon_entry_delay)
 mrs x9, CurrentEL
 cmp x9, #4
 b.eq 1f
 cmp x9, #8
 b.eq 2f
 cmp x9, #12
 b.ne 5f
 mrs x10, sctlr_el3
 mov w13, #0x00ff
 movk w13, #0xffff, lsl #16
 b 3f
1:
 mrs x10, sctlr_el1
 mov w13, #-1
 b 3f
2:
 mrs x10, sctlr_el2
 mov w13, #0xff00
 movk w13, #0xff00, lsl #16
3:
 mov x17, x10
 tbnz x10, #0, 5f
 tbz x10, #2, 7f
 mrs x14, ctr_el0
 ubfx x14, x14, #16, #4
 cmp x14, #2
 b.lo 5f
 cmp x14, #6
 b.hi 5f
 mov x15, #4
 lsl x14, x15, x14
7:
 orr x13, x13, x13, lsl #32
 mov w12, #0xff000000
 orr x12, x12, x12, lsl #32
 mov x9, #0x98600000
 mov x10, #0x8000
 movk x10, #0x991b, lsl #16
4:
 tst x9, #0x10000
 csel x11, x13, x12, eq
 stp x11, x11, [x9], #16
 cmp x9, x10
 b.lo 4b
 tbz x17, #2, 7f
 mov x9, #0x98600000
8:
 dc cvac, x9
 add x9, x9, x14
 cmp x9, x10
 b.lo 8b
7:
 dsb sy
5:
 adr x9, valethon_entry_delay_seconds
 ldr x9, [x9]
 cbz x9, 9f
 cmp x9, #8
 b.hi 9f
 mrs x10, cntfrq_el0
 mov x11, #0x4240
 movk x11, #0x000f, lsl #16
 cmp x10, x11
 b.lo 9f
 mov x11, #0xe100
 movk x11, #0x05f5, lsl #16
 cmp x10, x11
 b.hi 9f
 mul x11, x10, x9
 isb
 mrs x14, cntpct_el0
 mov x16, #0x80000000
6:
 isb
 mrs x15, cntpct_el0
 sub x15, x15, x14
 cmp x15, x11
 b.hs 9f
 subs x16, x16, #1
 b.ne 6b
9:
 ret
SYM_CODE_END(valethon_entry_delay)
.balign 8
.global valethon_entry_delay_seconds
.type valethon_entry_delay_seconds, %object
valethon_entry_delay_seconds:
 .quad 8
.size valethon_entry_delay_seconds, 8
