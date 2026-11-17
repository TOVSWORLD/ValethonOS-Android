# Next milestone execution plan

Updated November 17, 2026. Current milestone: attributable maintained Linux C
startup, then controlled enforcing PID1 on Douglas. Neither is yet proven on
the tablet. The complete kernel-facing [hardware contract](DOUGLAS-HARDWARE-CONTRACT.md)
and older working sources are the implementation basis. UART is supporting work,
not a prerequisite for this attempt. No equipment purchase or physical opening
is selected.

## Execute one combined candidate

[Concrete test and evidence](ACK-COMBINED-TRIAL.md). The full instrumented ACK
Image now passes both generic Cortex-A53 VM modes, all five kernel checkpoints
and the enforcing PID1 probe. Offline controls separately check full relocated
Image integrity and rejection/reset behavior. All11 qualification controls,953 regression tests and bound offline policy
validation pass. See the [preparation receipt](../../evidence/independent-recovery/ack-combined-preparation.json).
Ask owner availability for one
protected source boot/restore and one RAM jump. No further generic logging or
stub-only trial is the planned next step.

The source-derived corrections explicitly enable the legacy PSCI node and
normalize overlapping working memory declarations while preserving their union.
Neither is yet an established cause of the failed hardware boot.

## Acceptance and stopping conditions

A fresh complete ordered integrity/entry/MMU/start_kernel chain proves Linux C
entry. Controlled enforcing PID1 remains a separate, stricter physical USB
witness. A metadata marker, VM pass or automatic Android return cannot close the
hardware milestone. Missing retained markers are inconclusive.

Original boot must be restored/read back before the RAM jump. Recovery is never
written. One source boot and one load/jump only; no consumed approval reuse or
automatic retries. Follow the bounded read-only return/recovery procedure in the
test document. Collect once and update #344/#346/#348 plus project memory before
deciding any follow-up. Keep historical failures in those existing issues.
