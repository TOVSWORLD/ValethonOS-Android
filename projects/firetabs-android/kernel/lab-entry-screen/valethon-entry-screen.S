/* Private lab-only display checkpoint, after MMU-off normalization.
 * Preserve x0 and x19-x21. Read bounded FDT metadata, never framebuffer pixels.
 * Write only the firmware/API-corroborated framebuffer allocation.
 */
SYM_CODE_START_LOCAL(valethon_lab_entry_screen)
 mov x9, #0x48000000
 cmp x21, x9
 b.ne 9f
 ldr w9, [x21]
 mov w10, #0x0dd0
 movk w10, #0xedfe, lsl #16
 cmp w9, w10
 b.ne 9f
 ldr w9, [x21, #4]
 rev w9, w9
 cmp w9, #40
 b.lo 9f
 mov w10, #0x100000
 cmp w9, w10
 b.hi 9f
 add x9, x21, x9
 ldr w10, [x21, #8]
 rev w10, w10
 cmp w10, #40
 b.lo 9f
 tst w10, #3
 b.ne 9f
 ldr w11, [x21, #36]
 rev w11, w11
 add x10, x21, x10
 add x11, x10, x11
 cmp x11, x9
 b.hi 9f
 add x15, x10, #8
 cmp x15, x11
 b.hi 9f
 ldr w15, [x10]
 rev w15, w15
 cmp w15, #1
 b.ne 9f
 ldrb w15, [x10, #4]
 cbnz w15, 9f
 ldr w12, [x21, #12]
 rev w12, w12
 cmp w12, #40
 b.lo 9f
 ldr w13, [x21, #32]
 rev w13, w13
 add x12, x21, x12
 add x13, x12, x13
 cmp x13, x9
 b.hi 9f
 add x10, x10, #8
 mov w7, #64
1:
 subs w7, w7, #1
 b.eq 9f
 add x15, x10, #4
 cmp x15, x11
 b.hi 9f
 ldr w9, [x10], #4
 rev w9, w9
 cmp w9, #4
 b.eq 1b
 cmp w9, #3
 b.ne 9f
 add x15, x10, #8
 cmp x15, x11
 b.hi 9f
 ldr w17, [x10]
 rev w17, w17
 ldr w16, [x10, #4]
 rev w16, w16
 add x14, x10, #8
 add x10, x14, x17
 add x10, x10, #3
 and x10, x10, #-4
 cmp x10, x11
 b.hi 9f
 add x15, x12, x16
 add x16, x15, #11
 cmp x16, x13
 b.hi 9f
 adr x16, 5f
 mov w17, #11
3:
 ldrb w9, [x15], #1
 ldrb w8, [x16], #1
 cmp w9, w8
 b.ne 1b
 subs w17, w17, #1
 b.ne 3b
 ldur w17, [x14, #-8]
 rev w17, w17
 cmp w17, #16
 b.ne 9f
 mov x15, x14
 adr x16, 6f
 mov w17, #16
4:
 ldrb w9, [x15], #1
 ldrb w8, [x16], #1
 cmp w9, w8
 b.ne 9f
 subs w17, w17, #1
 b.ne 4b
 mov x9, #0x98600000
 mov x10, #0x8000
 movk x10, #0x991b, lsl #16
2:
 tst x9, #0x10000
 csetm x11, eq
 stp x11, x11, [x9], #16
 cmp x9, x10
 b.lo 2b
 dsb sy
9:
 ret
.balign 4
5: .asciz "compatible"
6: .asciz "mediatek,mt8163"
SYM_CODE_END(valethon_lab_entry_screen)
