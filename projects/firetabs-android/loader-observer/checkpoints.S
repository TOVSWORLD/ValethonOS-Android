/* Analysis-only Thumb stubs for the exact archived resident binary.
 * Never linked into, flashed to, or executed on a tablet by this source.
 * Placement is 0x4bcffbb8; all firmware addresses are exact-build inputs.
 */
.syntax unified
.cpu cortex-a9
.thumb
.section .text
.global observer_mode, observer_read, observer_handoff
.macro save
 push.w {r0-r12,lr}
 mrs r0, apsr
 mov r1,sp
 bic r2,r1,#7
 sub r2,r2,#8
 mov sp,r2
 str r0,[sp]
 str r1,[sp,#4]
.endm
.macro restore
 ldr r0,[sp]
 ldr r1,[sp,#4]
 msr APSR_nzcvqg, r0
 mov sp,r1
 pop.w {r0-r12,lr}
.endm
.macro normal_only
 ldr r3,boot_mode
 ldr r3,[r3]
 cmp r3,#0
 bne 1f
.endm
.thumb_func
observer_mode:
 save
 normal_only
 /* Original mode printf arguments are saved r0/r1 through the aligned frame pointer. */
 ldr r12,[sp,#4]
 ldr r0,[r12]
 ldr r1,[r12,#4]
 ldr r3,video
 blx r3
1:
 restore
 /* Retain the original UART printf and its return convention. */
 ldr pc,uart_printf
.thumb_func
observer_read:
 save
 normal_only
 /* Selected 64-bit offset is in original hook SP+16/+20. */
 adr r0,read_format
 ldr r12,[sp,#4]
 ldr r1,[r12,#76]
 ldr r2,[r12,#72]
 ldr r3,video
 blx r3
1:
 restore
 /* Replay the exact overwritten ldr/mov before returning to +0x76. */
 ldr r3,original_read_pointer
 mov r0,r6
 bx lr
.thumb_func
observer_handoff:
 save
 normal_only
 adr r0,handoff_format
 ldr r12,[sp,#4]
 ldr r1,[r12]
 ldr r2,[r12,#4]
 ldr r3,video
 blx r3
1:
 restore
 /* Tail-forward with the original call's LR and entry/DT arguments. */
 ldr pc,handoff_target
.balign 4
boot_mode: .word 0x4bd7c3a0
video: .word 0x4bd44b3d
uart_printf: .word 0x4bcff737
original_read_pointer: .word 0x4bcffb64
handoff_target: .word 0x4bd3de69
read_format: .asciz "LK read %08x:%08x\n"
handoff_format: .asciz "LK handoff entry=%08x dt=%08x\n"
.balign 4
