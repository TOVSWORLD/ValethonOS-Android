.syntax unified
.thumb
.section .text.lbo_call,"ax",%progbits
.global lbo_call
.type lbo_call,%function
.thumb_func
lbo_call:
 push {r4,lr}
 mov r4,sp
 mov r12,r0
 mov r0,r1
 mov r1,r2
 mov r2,r3
 ldr sp,[sp,#8]
 blx r12
 mov sp,r4
 pop {r4,pc}
.size lbo_call,.-lbo_call
.macro hook name,kind
.section .text.\name,"ax",%progbits
.global \name
.type \name,%function
.thumb_func
\name:
 push.w {r0-r12,lr}
 mrs r0,APSR
 movs r1,#\kind
 push {r0,r1}
 mov r0,sp
 bl lbo_observe
 pop {r0,r1}
 msr APSR_nzcvqg,r0
 pop.w {r0-r12,lr}
.endm
#ifndef LBO_SCREEN_WITNESS
hook lbo_read,2
 /* Replay the original two overwritten instructions. */
 ldr r3,=0x4bcffb64
 mov r0,r6
 bx lr
.size lbo_read,.-lbo_read
#endif
#ifdef LBO_PRE_SHUTDOWN
hook lbo_pre_shutdown,4
 /* Replay the original PC-relative load at pinned LK 0x4bd3e3e8. */
 ldr r3,=0x4bd3eb0c
 ldr r3,[r3]
 bx lr
.size lbo_pre_shutdown,.-lbo_pre_shutdown
#else
hook lbo_handoff,3
 /* Replay the original call with the existing return LR. */
 b.w lbo_original_handoff
.size lbo_handoff,.-lbo_handoff
#endif

.section .rodata.lbo_load_plan,"a",%progbits
.balign 8
.global lbo_load_plan
lbo_load_plan: .space 72
.section .rodata.lbo_frontend,"a",%progbits
.balign 8
.global lbo_frontend
lbo_frontend: .space 112

/* Filled by the offline packer with the exact linked BL instruction. */
.section .rodata.lbo_hook_word,"a",%progbits
.balign 4
.global lbo_hook_word
lbo_hook_word: .word 0
