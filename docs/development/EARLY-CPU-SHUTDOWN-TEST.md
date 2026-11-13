# CPU shutdown before device shutdown

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
hotplug balance and fail-closed paths. The complete Python suite passed 883 of
884 tests, with one optional Unicorn test skipped. An isolated ARM64 Image build
is in progress. Hardware execution and target boot are still unqualified.

The hardware sequence requires one protected ordinary source boot, restoration
and readback of original boot, fresh source capture, one native load and one
orderly jump. Existing trial budgets remain consumed. The success criterion is
the fresh target nonce on its own USB console; an early CPU gate marker alone
does not satisfy it. Recovery remains owner-assisted if the target hangs.
