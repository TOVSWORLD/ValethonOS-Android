# First-jump recovery and post-failure logging

November 10, 2026: owner reported a black screen and no response to ordinary
Power after the first kexec request. ADB was absent. After physical recovery
instructions, owner reported the Android home screen. Read-only checks verified
the exact original full boot, original config and unchanged recovery. Normal
UID2000 ADB restored after each collection. No additional reboot, load, jump,
partition write or log deletion was performed by the collector.

The kexec-capable source kernel is no longer running; original config has KEXEC
disabled. The trial approval is consumed. No retry is authorized by recovery.
This is an observed owner-assisted return, not independent automatic recovery.

Pstore is mounted, its console is enabled and the expected 0x44410000/0xe0000
reservation and 64KiB console are active. Its record directory is empty; there
are zero current or retained handoff lines. No records were deleted by us.
The successful earlier orderly-reboot retention test does not establish survival
through this hang and physical recovery. Power loss, firmware/kernel clearing
and an uninspected userspace consumer are not distinguished. Top-level init
file searches found no consumer, but that search was not exhaustive. The hang
cannot yet be assigned to init shutdown, CPU parking, relocation, entry or target.

## Concrete recovery gap found in source

The bound platform driver is `mtk-wdt` at `10007000.toprgu`. Exact source
`drivers/watchdog/mtk_wdt.c` lines540–546 calls `mtk_wdt_stop` during device shutdown
when its watchdog is active or hardware-running. Stop clears WDT_MODE_EN.
The normal native route calls kernel_kexec → kernel_restart_prepare →
device_shutdown before machine_shutdown and machine_kexec. Thus a watchdog
armed in ordinary userspace is not automatically a surviving handoff deadline.
There is no evidence establishing that this trial reached that callback; this
is a source-level recovery gap, not the proven hang location or cause.

## Next implementation scope

Prepare a handoff-scoped hardware reset deadline that survives shutdown, with
attributable phase markers and a warm-reset readout. Audit all remaining kicker
paths so they cannot extend the deadline. Restrict arming to the reviewed route;
ordinary reboot targets must retain their current behavior. Verify register
readback and a bounded timeout, safe source-load refusal, and successful-target
watchdog ownership/disable behavior. Keep original boot on flash and recovery
unchanged. Do not add persistent boot flags or reuse consumed approvals.

Qualify the exact reset-to-original and marker-retrieval path as post-failure
work before repeating this failed handoff. This follows the owner's requested
sequence: experiment first, investigate failed-jump logging afterward. It does
not call for repeating the already-passed ordinary console-retention baseline.
No recovery-timer source change, new build or hardware test has yet been made.

[Recovered-device and source-audit receipt](../../evidence/independent-recovery/native-first-jump-recovery-result.json).
[Original failed trial receipt](../../evidence/independent-recovery/native-first-jump-runtime-result.json).
