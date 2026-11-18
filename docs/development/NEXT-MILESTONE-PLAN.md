# Next milestone execution plan

Updated November17,2026 after the C-init hardware attempt.
**Achieved:** maintained Linux entry/MMU/start_kernel on Douglas and attributed
retained kernel output. **Goal remains:** complete initialization and prove fresh
enforcing RAM PID1 through physical USB. Neither PID1 nor USB is yet proven.

## Concrete next correction

[Live RAM fix](ACK-LIVE-RAM-FIX.md): fresh source System RAM excludes
98400000–98600000, but the target DT left it allocatable. The captured stack-
overflow panic faults in show_pte at a VA corresponding, under the A53 linear-map
geometry, to a physical page inside that gap. Nested fault reporting may obscure
the first fault; resolving the panic through this correction is not yet proven.

The candidate preserves every source non-System-RAM gap as no-map, independently
binds/verifies fresh iomem and rechecks all load segments. Existing firmware
reservations, full padded Image SHA, permanent console, enforcing PID1 and
31-second reset deadline remain. No logger-only/stub trial or guessed USB fix.
Both VM modes using target RAM/no-map geometry reach enforcing PID1.

All13 qualification controls,963 regression tests and bound offline policy
validation pass. The candidate is ready: publish and request owner presence
for one protected source boot/restore and one RAM jump under fresh scope4.
Original boot restored/read back before jump; recovery never written; bounded
read-only return checks; no retry. Previous approvals are consumed. Success still
requires the fresh enforcing PID1 USB witness. If unsuccessful, collect once,
verify original state and use the attributed failure to select the next change.

## History and continuity

C-init [runtime result](../../evidence/independent-recovery/ack-cinit-runtime-result.json)
preserves the panic and source RAM intervals. Prior combined entry/MMU milestone
remains passed. Do not downgrade it because the legacy banner/PID1 gate remains
false. Do not repeat equipment/board-history questions; UART is supporting work.
