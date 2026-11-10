/* SPDX-License-Identifier: GPL-2.0 */
/* Offline candidate only. Not linked into kxstage or exposed by any ioctl.
 * Entered by the matched relocator after it has zeroed x0-x3.
 * CPU/EL/cache/MMU/DMA/firmware state must already meet the Image protocol.
 * These six instructions establish arguments only, without a stack or writes.
 */
.section .text.kxentry,"ax",%progbits
.balign 8
.global kxentry_start, kxentry_dtb, kxentry_image, kxentry_end
kxentry_start:
 ldr x0, .Ldtb
 mov x1, xzr
 mov x2, xzr
 mov x3, xzr
 ldr x16, .Limage
 br x16
kxentry_dtb:
.Ldtb:
 .quad 0
kxentry_image:
.Limage:
 .quad 0
kxentry_end:
