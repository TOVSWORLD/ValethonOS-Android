# CPU0-only target boot experiment

The next required result is **a fresh target kernel boot nonce on USB**. The
already-proven source native-entry checkpoint is only a prerequisite, not a new
milestone or proof that the target executed.

The target currently performs SMP initialization before normal driver initcalls.
Its MT8163 secondary startup calls firmware CPU_ON and then platform power-on
code with unbounded hardware waits. That is a concrete candidate for losing the
target before USB initializes after a warm handoff. It is not the proven cause.

This experiment changes only the target command-line prefix by adding
`nr_cpus=1 maxcpus=1`. The exact kernel supports both early parameters. Its
possible mask starts empty, CPU0 is marked possible, and ARM64 setup respects
nr_cpu_ids when adding secondaries. The generic online path rejects CPUs outside
the possible mask. Source CPU configuration, shutdown, final CPU gate, relocation,
Image, ramdisk, addresses, DT reservations and boot/recovery images are unchanged.
The source still has four possible CPUs and must pass its existing load gate.

The Image is the hardware-booted b999644a…e2c287 profile. The source boot package
is unchanged (ce0e7a57…3977cc). No kernel rebuild or new logging framework is
included. Existing source USB proof, FunctionFS hold, settings journal and abort
cleanup are reused. Existing CPU-limit arguments are refused rather than silently
overridden; only the explicit target limit of one is supported.

The sequence is one temporary source boot with original-boot restoration and
verification, fresh source DT/RAM and trial nonce, a source USB challenge before
arming hold/quieting, one exact native load, and one orderly jump. Target scope
and authorization explicitly include the CPU limit. Recovery is never written.
No automatic boot/jump retry or post-request tablet commands are permitted.

Success requires the target's fresh g_serial marker or its exact nonce-bearing
kernel command line on the target USB console. Target userspace/Android readiness
will be assessed separately from kernel entry. If the target remains absent,
this change was not sufficient; it does not prove the hang happened before target
entry or eliminate every firmware/device initialization problem. Do not call a
repeat source checkpoint a passed target-boot milestone.

The target capture window is five minutes. Original boot is restored on flash
before jumping. If the tablet is black afterward, unplug USB, hold only Power
40 seconds, release, wait 5 seconds, reconnect the same cable/port and verify
original Android/boot/config/recovery and normal ADB. Owner assistance may still
be needed; automatic return remains unqualified.

[Exact trial policy](../../evidence/independent-recovery/single-cpu-target-two-stage-authorization-template.json).
[Preparation and source analysis](../../evidence/independent-recovery/single-cpu-target-preparation-result.json).
