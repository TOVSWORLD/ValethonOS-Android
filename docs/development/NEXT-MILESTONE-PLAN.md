# Next milestone execution plan

Updated November17,2026 after the single combined hardware attempt.
**Achieved:** exact full relocated Image integrity, actual Linux primary entry,
MMU transition, virtual entry and start_kernel on Douglas.
[Runtime evidence](../../evidence/independent-recovery/ack-combined-runtime-result.json).
**Next goal:** finish early kernel initialization and reach controlled enforcing
PID1, then prove its identity on the target USB endpoint.

## Prepared next attempt

[Full C-init/PID1 trial](ACK-CINIT-TRIAL.md): the exact maintained Image now has a
RAM-only early console whose fixmap and permanent text callback survive paging
and init-memory cleanup. It retains initcall/error output during a complete
kernel/PID1 attempt, with fresh identity on every write. The old entry hooks are
absent; no driver fault or exact stopping instruction is yet established.

Both Cortex-A53 VM boot modes reached /init, passed the enforcing PID1 probe and
retained the run-init message after init-memory cleanup. All12 offline instruction/
corruption/console controls and958 regression tests pass without skips. The
[preparation receipt](../../evidence/independent-recovery/ack-cinit-preparation.json)
binds the exact reference, Image, policy and load-only client. This is offline
qualification, not a Douglas PID1/USB pass. No tablet commands ran in preparation.

Next action: owner-attended single protected source boot/restore and one RAM
load/jump, under a fresh ack-linux-cinit-two-stage-3 authorization. Original boot
restored/read back before jumping, recovery never written, existing31-second
reset deadline, bounded read-only return checks and no retry. Prior approvals
stay consumed. Success remains the fresh enforcing PID1 USB wire witness.
If unsuccessful, collect once and use the attributed last initcall/exception or
kernel messages to choose the next implementation change. UART is supporting
work, not a prerequisite. Do not repeat an unchanged black-screen trial.

## Recovery and history

The combined trial used one source boot/restore and one native load/jump. Original
boot was restored/read back before jumping; recovery was never written. A new
completed original Android boot, exact flash/config and normal ADB were verified.
Owner confirmed Power untouched: automatic Android return is established;
precise reset cause remains unqualified.
Retain the old failed trials in #344/#346/#348 and preserve this new milestone.
Any later attempt keeps single-attempt limits, a bounded capture/return window,
no post-jump mutations into a hung device and owner-assisted recovery if needed.
