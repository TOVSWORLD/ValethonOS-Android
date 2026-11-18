# Preserve live RAM exclusions before the next full kernel/PID1 attempt

November17,2026. The C-init hardware attempt produced an attributed panic,
not a PID1/USB milestone. [Runtime receipt](../../evidence/independent-recovery/ack-cinit-runtime-result.json).
The prior Linux entry/MMU/start_kernel milestone remains valid.

## Observed failure and concrete contract defect

The retained4084-byte console worked on Douglas. It reports kernel stack overflow,
PC show_pte+0x1d0/0x350, LR show_pte+0x188/0x350, ESR0x96000006 (current-EL data
abort, translation fault), FAR0xffff0000585ff008. The last record may describe a
nested fault while reporting an earlier exception, rather than the initial cause.
PID1 and target USB were not observed. No automatic retry occurred; original
boot/config/recovery and normal ADB were verified after a different completed
Android boot. Owner Power attestation is recorded in the runtime receipt.

Fresh working-source /proc/iomem gives these System RAM intervals (end exclusive):

- 0x40000000–0x43000000
- 0x43030000–0x98400000
- 0x98600000–0x99600000

The static/live source DT memory declarations covered the gap98400000–98600000.
Its imported no-map framebuffer starts at98600000 and did not cover that gap.
Our earlier target preserved the DT reservations and checked the three load
segments against live System RAM, but **did not prevent later kernel allocations
in every non-System-RAM gap**. That was an incomplete memory contract.

Under the pinned A53 runtime48-bit linear-map/DRAM-base geometry, the observed
fault VA corresponds to physical985ff008, inside the uncovered2MiB gap. This
physical conversion is an inference, not a read of a physical-address register.
The address correlation is strong, but whether the correction resolves the
panic remains unproven. We do not identify the gap's owner or the original
exception without evidence. No equipment purchase or physical measurement is
required to enforce the already-observed working-kernel RAM boundary.

## Exact correction

Compute the difference between the source DT RAM-bank union and **fresh live
System RAM**. Preserve existing no-map regions, then add no-map reserved-memory
nodes for uncovered gaps. The ATF gap43000000–43030000 is already covered. This
candidate adds98400000–98600000; it does not expand usable memory, remove old
firmware reservations or invent a peripheral's ownership.

Bind the private source iomem hash in the manifest. The independent verifier
recomputes all gaps, checks every one is covered by no-map, and rechecks all
load segments against actual System RAM. The fresh runtime bundle repeats this
from the current source boot; any changed Image hash or invalid layout aborts.

The complete ACK Image, fresh enforcing RAM PID1, permanent early console,
full padded destination SHA and31-second reset deadline remain. Image differences
from the previous attempt are its fresh console/PID1 identity; the functional
boot correction is in the DT allocator exclusions. No new logger mechanism,
UART register access, target storage or recovery write is added.

## Offline qualification and hardware acceptance

The exact fresh Image passes both Cortex-A53 VM boot modes. These VMs now use
the target's RAM banks and all six no-map ranges within a1.5GiB host RAM window,
retaining virt controllers for the enforcing PID1 probe. Both reach /init and
retain the run-init message after init-memory cleanup. This is a stronger memory
layout check than the earlier512MiB VM; it does not model the physical owner or
protection of the excluded gap, and does not establish causality on hardware.

[Qualification](../../evidence/independent-recovery/ack-ramfix-qualification.json),
[VM off](../../evidence/independent-recovery/ack-ramfix-vm-off.json),
[VM on](../../evidence/independent-recovery/ack-ramfix-vm-on.json),
[preparation](../../evidence/independent-recovery/ack-ramfix-preparation.json).
The interval controls cover the actual missing gap, ATF, bank boundaries,
invalid/overlapping source ranges and transplanted VM memory/no-map nodes.

Use a fresh ack-linux-ramfix-two-stage-4 authorization with owner present.
One protected source boot/restore and one native RAM load/jump, original boot
restored/read back before jump, recovery never written, bounded read-only return
checks and no retry. The previous C-init approval remains consumed.
The goal remains fresh enforcing PID1 identity on the physical USB wire.
If unsuccessful, collect once, verify original state and use the attributed
panic/last initcall to choose the next change; do not repeat unchanged trials.
