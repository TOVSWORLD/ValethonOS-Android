# MT8163 firmware affinity capability probe

Development candidate for issue #346. **One approved runtime test passed; approval consumed.**

The installed kernel uses the legacy `arm,psci` binding, whose initializer does
not populate `psci_ops.affinity_info`. This blocks the new explicit-OFF guard.
The device tree names SMC32 AFFINITY_INFO `0x84000004`; firmware support remains
unknown. This module queries affinity level zero for targets 0 through 3 once.
It validates the exact board, conduit, FID and CPU topology first. It reports
unsupported/error responses without attempting to alter CPU state.

Build with `scripts/build_kexec_affinity.py` against the exact matched source,
configuration and release. Verify import CRCs and disassembly using
`scripts/verify_kexec_affinity.py`. Run actual compiled initializer emulation with
`scripts/validate_kexec_affinity_instructions.py` on the Linux Unicorn environment;
its kernel APIs and firmware calls are stubbed, so this establishes control-flow
properties rather than firmware behavior. `scripts/prepare_legacy_affinity.py`
generates the separately reviewed source-kernel binding; it performs no probe.

The runner defaults to read-only preflight. Hardware execution requires an exact
final module hash and explicit owner availability/approval. One insertion only;
no automatic retries. Preserve fresh KXAFF logs, unload, remove the RAM copy and
restore normal adbd with an external finally block. A stuck SMC cannot be
interrupted by a host timeout and could require a physical power cycle.

Reviewed artifact SHA-256:
`a41314b4afcf554343bea7ff80c7a5ca902f3068713d3d22e9ee1ed3a7441828`
(9088 bytes). All import CRCs match exact providers. Ten actual ARM64 initializer
emulation cases and eleven Linux tests passed. Read-only tablet preflight passed;
normal ADB shell restored. Runtime test completed: CPU0/1 ON, CPU2/3 OFF; online mask 0x3, current CPU0.
Module unloaded, RAM removed, normal ADB restored. No state changes or jump.
Do not rerun without new exact approval. Owner approval
of source transfer resolved the earlier automatic-review blocker.

The earlier `affinity-ready` binary predates the OF compatibility-score fix and
must never be executed. Only the hash above is proposed. The separate legacy
source-kernel binding remains an offline generated candidate.

The corrected separate source-kernel binding now has matched ARM64 object
compilation, 17 mocked generated-function checks and 20 actual ARM64 callback
emulation cases. See `scripts/build_legacy_affinity.py`,
`scripts/validate_legacy_affinity.py` and
`scripts/validate_legacy_affinity_instructions.py`. Its generated module wrapper
has unresolved symbols and must never be loaded. Combined full-kernel integration
has not run and awaits explicit approval after automatic review rejection.

The isolated combined full-kernel build has now passed. Its retained Image and
linked call-target checks are recorded in
`evidence/independent-recovery/kexec-source-integration-build-result.json`.
The earlier combined-build approval blocker is resolved. This does not authorize
a new hardware test or qualify CPU-off, failed-load recovery or retained logs.
