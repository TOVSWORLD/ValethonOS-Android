# Next milestone execution plan

Updated November17,2026 after the single combined hardware attempt.
**Achieved:** exact full relocated Image integrity, actual Linux primary entry,
MMU transition, virtual entry and start_kernel on Douglas.
[Runtime evidence](../../evidence/independent-recovery/ack-combined-runtime-result.json).
**Next goal:** finish early kernel initialization and reach controlled enforcing
PID1, then prove its identity on the target USB endpoint.

## Work from the proven boundary

The retained trace ends at the start_kernel checkpoint; it does not identify the
following fault instruction. There is no attributed Linux banner or target PID1
wire. Analyze the pinned start_kernel prologue and pre-banner callees, stack and
shadow-stack initialization, CPU feature alternatives and early exception path.
Compare those with the working-source boot contract; choose the next change
from a concrete violated contract or one bounded discriminating C-init test.
Do not return to relocation, stub-only, entry or MMU experiments already passed.
UART investigation remains supporting work, not a prerequisite.

Use the [hardware contract](DOUGLAS-HARDWARE-CONTRACT.md) and exact ACK sources.
No new tablet test is currently authorized by the consumed combined approval.
Prepare and offline-validate any next candidate before requesting owner presence.
Do not infer a driver/USB fault before establishing execution reaches it.

## Recovery and history

The combined trial used one source boot/restore and one native load/jump. Original
boot was restored/read back before jumping; recovery was never written. A new
completed original Android boot, exact flash/config and normal ADB were verified.
Owner confirmed Power untouched: automatic Android return is established;
precise reset cause remains unqualified.
Retain the old failed trials in #344/#346/#348 and preserve this new milestone.
Any later attempt keeps single-attempt limits, a bounded capture/return window,
no post-jump mutations into a hung device and owner-assisted recovery if needed.
