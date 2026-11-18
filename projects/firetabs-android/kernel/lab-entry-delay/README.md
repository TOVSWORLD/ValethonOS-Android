# Earliest-entry checkpoint and dwell — private issue346 experiment

The old checkpoint was after boot argument preservation, identity-map construction
and exception-level setup, with a DT pointer/compatible gate. Its absence could not
answer whether execution reached the kernel's initial primary_entry at all.

This opt-in source patch makes the first primary_entry instruction call a leaf
probe, before record_mmu_state. It uses neither DT nor stack nor driver readiness.
Boot arguments, x18 and callee-saved registers/SP are preserved. With MMU off it
paints opaque64KiB bands only within the metadata-corroborated display allocation
98600000..991b8000. White/green/magenta encode entry at EL1/EL2/EL3 respectively.
If the data cache is enabled, bounded16..256-byte CTR line sizing and exact-span
clean-to-PoC precede the barrier. With MMU on it does not assume physical aliases
and skips painting. No pixels are read. Generic emulator validation backs that
address with1536MiB virtual RAM; ordinary profiles keep their previous RAM limit.

A valid1..100MHz architected frequency requests eight counter seconds, then returns
normally. Zero/out-of-range frequency or request skips the dwell. A finite2^31
iteration limit also exits a stopped counter, but no calibrated stopped-counter
wall bound is claimed. Timer access itself depends on the architectural entry
contract. Reset/controller cause is still unproven: the probe does not disable,
extend or write any watchdog/reset/thermal/security registers. An independent
watchdog can reset during the wait. This is not an intentional panic/halt test.

A visible uniquely colored pattern is positive kernel-entry evidence. Absence or
merely longer logo/black timing remains inconclusive: scanout persistence and entry
conditions are not physically qualified. It does not establish CPU initialization,
storage, a retained kernel record or failure-return acceptance. EL3 is diagnostic
only; the kernel boot protocol calls for non-secure EL1 or EL2. No exception-level
or security transition is added to work around a bad handoff.

The pinned ARM64 protocol is Documentation/arch/arm64/booting.rst at ACK
`d9318bdb4c34e8b2d997b4f67ced56b120b22b87`: x0 DTB/x1..3 reserved, interrupts
masked, non-secure EL1/EL2, MMU off, counter frequency and EL1 access initialized.
https://android.googlesource.com/kernel/common/+/d9318bdb4c34e8b2d997b4f67ced56b120b22b87/Documentation/arch/arm64/booting.rst

Actual instructions passed bare-metal emulator controls at EL1, EL2 and EL3:
all destination words/adjacent guards, register preservation, cache-enabled clean,
zero/out-of-range requests/frequencies and eight-counter-second wait. These are
software controls, not physical display/reset/kernel-entry proof. The existing
persistent record reader/control stays intact. No new physical action is admitted;
exact Image/size/VM/package and complete changed procedure review come first.
