.syntax unified
.thumb
.text
.global lb_cache_sync
.type lb_cache_sync,%function
.thumb_func
lb_cache_sync:
    cbz r1, cache_fail
    cbz r2, cache_fail
    movw r3, #8192
    cmp r2, r3
    bhi cache_fail
    adds r3, r1, r2
    bcs cache_fail
    push {r4, r5, r6, lr}
    mov r0, r1
    mov r1, r2
    ldr r3, =0x4bd3c740
    blx r3
    /* Firmware cleans D-cache lines, drains writes and invalidates I-cache.
     * Complete synchronization explicitly before the newly loaded code runs. */
    dsb sy
    isb sy
    movs r0, #0
    pop {r4, r5, r6, pc}
cache_fail:
    movs r0, #1
    rsbs r0, r0, #0
    bx lr
.size lb_cache_sync,.-lb_cache_sync
