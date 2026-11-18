# Next milestone execution plan

November17,2026. **Achieved on Douglas:** maintained kernel initialization,
/init execution, SELinux policy loading and USB gadget enumeration/CDC ACM bind.
The live RAM exclusion correction got execution past the prior panic.
[Hardware result](../../evidence/independent-recovery/ack-ramfix-runtime-result.json).

## Complete the existing USB transfer

[Concrete action](ACK-USB-END-TO-END.md): repair the receiver lifecycle and its
missing outcome, then run the full end-to-end attempt with fresh PID1 identity.
No logging-only hardware gate or re-proof of kernel/PID1. Owner explicitly
requested this focus. Keep the kernel/RAM correction and remove verbose
initcall tracing; continue to the fresh USB protocol witness.

The receiver now uses one detached bounded worker with atomic ready/result
files, private stderr/exit preservation and durable-result recovery after SSH
loss. It still selects the exact physical endpoint and verifies fresh protocol
identity; it never reopens a port or automatically retries.

One fresh scope5 source boot/restore and RAM jump, original boot restored/read
back before jump, recovery never written,31-second target reset deadline and
bounded read-only return checks. Earlier approvals remain consumed. Owner is
available and said “Do it”; complete authorized preparation and the full attempt.
Afterwards verify original state, update the same issues/evidence/memory and move
to the next functional milestone. If transfer fails, use its actual receiver
outcome without reclassifying the achieved kernel/PID1 stages as unproven.
