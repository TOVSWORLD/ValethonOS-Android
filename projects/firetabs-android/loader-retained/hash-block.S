.syntax unified
.thumb
.text
.global lh_block
.type lh_block,%function
.thumb_func
lh_block:
    cbz r0, fail
    cbz r2, empty
    cbz r1, fail
    ldr r3, =0x40000
    cmp r2, r3
    bhi fail
    lsls r3, r2, #6
    adds r2, r1, r3
    bcs fail
    /* Pinned generic ARM block entry expects r2=end and r3=dispatch base.
     * Enter past the feature dispatch, without reading/writing capability bits. */
    ldr r3, =0x4bd15600
    ldr r12, =0x4bd15620
    push {r4, lr}
    blx r12
    pop {r4, lr}
empty:
    movs r0, #0
    bx lr
fail:
    movs r0, #1
    rsbs r0, r0, #0
    bx lr
.size lh_block,.-lh_block
