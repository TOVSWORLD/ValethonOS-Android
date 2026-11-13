# CPU shutdown before device shutdown

## Hardware outcome — November 13, 2026

One source boot/restore and one load/jump ran. Fresh source capture proves the
early secondary-CPU hardware off gate passed before device shutdown. Target USB
never appeared during the 300-second window, so **target boot remains unproven**.
The ordering change was insufficient. The capture cannot establish completion
of device shutdown, the later final gate, relocation or target entry. Original
boot was restored before jumping; owner-assisted return is pending. No retry.

[Sanitized hardware receipt](../../evidence/independent-recovery/early-cpu-shutdown-runtime-result.json).

## Historical preparation

November 13, 2026. Target boot remains the required milestone. The CPU0-only
target experiment timed out and owner-assisted return has been fully verified.

This experiment changes the source handoff order. The current kernel calls
`kernel_restart_prepare`, including reboot notifiers and `device_shutdown`,
before migrating to CPU0 and offlining secondary CPUs. The experiment performs
normal secondary CPU hotplug and the existing physical off-state check while
platform drivers are still running, then shuts down devices and relocates.
Driver teardown interfering with CPU shutdown is a hypothesis, not an observed
cause. A negative result cannot locate the failure by itself.

The change applies only to MT8163, PID1 and a default loaded image, inside the
existing non-preserve-context branch under the kexec mutex. CPU-off failure,
wrong survivor, an unexpected online mask or physical off-state failure uses
the existing panic policy and cannot proceed to device shutdown or relocation.
Hotplug stays disabled after the early offlining operation. The later duplicate
CPU shutdown is skipped; the independent final hardware gate in machine_kexec
still runs after device shutdown and before any cache/MMU transition.

Other callers keep the original ordering. The CPU-off implementation,
firmware calls, relocation, exception-level switch and target payload layout
remain the tested implementations. The target will use its normal CPU startup,
so the failed CPU0-only target experiment is not combined with this change.
The existing console gives the early gate one second to drain before teardown.

The actual generated C sequence passed seven host controls covering ordering,
hotplug balance and fail-closed paths. Five trial controls require the distinct
scope, source capture and normal target CPU startup. The complete Python suite
passed 888 of 889 tests, with one optional Unicorn test skipped. The isolated
ARM64 Image and linked syscall/USB/final CPU gate checks passed. Full source-tree
comparison confirms only kernel/kexec_core.c changed. Read-only source preflight
passed with zero writes/reboots and normal ADB restored. Hardware execution and
target boot are still unqualified.

The hardware sequence requires one protected ordinary source boot, restoration
and readback of original boot, fresh source capture, one native load and one
orderly jump. Existing trial budgets remain consumed. The success criterion is
the fresh target nonce on its own USB console; an early CPU gate marker alone
does not satisfy it. Recovery remains owner-assisted if the target hangs.

[Exact prepared artifact receipt](../../evidence/independent-recovery/early-cpu-shutdown-preparation-result.json).
[Bounded trial policy](../../evidence/independent-recovery/early-cpu-shutdown-two-stage-authorization-template.json).
