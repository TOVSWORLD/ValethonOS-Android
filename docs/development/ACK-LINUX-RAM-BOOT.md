# Full 6.18 kernel and PID1 through the native RAM path

Prepared November 16, 2026 after the attributable reset-payload test passed.
One full ACK RAM-boot jump ran on November 16. It did not establish Linux
startup or PID1. Android returned on a different completed boot, with original
boot/config, recovery and normal ADB verified. Owner Power confirmation is
pending. The target entry/readback marker survived; USB capture was empty.
The 31-second deadline's exact reset cause remains unqualified. No retry.

[Runtime receipt](../../evidence/independent-recovery/ack-native-runtime-result.json).

The required result is the pinned **6.18.34-valethon-draft1+ kernel and its
enforcing PID1 executing on the tablet**, with a fresh nonce-bound USB stream.
This is maintained-kernel bring-up, not an Android framework, desktop, display,
storage or finished-release acceptance claim.

## Concrete changes from the historical draft

The complete existing ACK Image is 26,532,352 bytes with a 28,049,408-byte memory
extent and text_offset zero. Native relocation places it at 0x40000000, its
required 2 MiB-aligned base, and the metadata entry stub supplies x0=0x42000000
and x1/x2/x3=0. The prior one-page pass did not qualify this full-size copy.
The metadata entry remains 0x42018000; a fresh RAM-only initramfs is placed at
0x69244000. The maintained Image is never written to the boot partition.

The old draft DT declares PSCI 0.2. The observed working source DT instead
declares `arm,psci`, SMC and explicit IDs 0x84000001 through 0x84000004. The new
target copies that exact live contract; pinned ACK psci.c implements its v0.1
initializer. This addresses a concrete assumption mismatch, not a proven cause
of the historical unobserved boot. Target CPU count is one and cpuidle is off;
CPU OPP references are removed for this bootstrap.

Live DRAM banks replace the draft's static memory declaration. The target's
reservation map incorporates all live firmware reservations without importing
vendor phandles into the target driver graph. All three MMC controllers, display
pipeline, GPU and audio controller are disabled for the USB/PID1 milestone.
USB0 remains peripheral, with its clock/PHY providers retained. This does not
qualify any disabled peripheral.

The historical kernel disk-log worker is opt-in through the exact
`/chosen/valethon,trial-nonce` property. That property is removed and verified
absent. The pinned source's zero-nonce guard exits before starting its worker;
the compiled object identity is also bound. Disabled MMC controllers provide a
second barrier to disk access. The enclosing original boot image is restored
and read back before the native load. The target PID1 policy also denies block
access and reboot capability.

## Bounded attempt and existing retained console

After source device/CPU shutdown and native relocation, the new entry stub arms
the existing reset-only hardware watchdog for 31 seconds and checks its mode
and length readback. A failed readback requests the normal software reset
instead of entering Linux. The target watchdog DT node is disabled and has no
reset-provider phandle dependencies, so the target driver cannot take over or
extend the deadline. No agent reboot command is sent after the jump.

The hardware timer's expiration, clock continuity and RAM retention remain
unqualified until this actual whole-kernel attempt; the reset-payload software
reset does not substitute for those observations. If it fails to return, the
owner-assisted hard restart remains the known route after the bounded window.
There is no separate watchdog calibration boot and no automatic repeat.

Both kernels use the existing 12-byte DBGC retained-ring header with ECC off.
ACK ramoops module parameters map a console-only 64 KiB zone at 0x444bf000,
matching the vendor backend's current-console zone. Dumps, ftrace and pmsg are
disabled in that target backend. The entire existing firmware reservation is
preserved. The entry stub appends a fresh handoff marker; **that marker proves
only the entry stub/readback, not Linux startup**. Linux's later ramoops probe
may replace it with the new kernel's console, so its absence does not locate a
failure. Raw retained files are archived privately without deletion.

## Capture, acceptance and return

The fresh static PID1 retains the exact previously VM-tested enforcing policy.
It is rebuilt with AArch64 GCC, its ELF/archive are inspected, and its new nonce
is bound to the package. This is not a claim of a new VM or device pass.
The private in-house ACM identity remains 1209:0001, interface 00.

The target receiver arms durably after the full native load is verified and
before the single jump. It pins the physical USB port and interface and uses
the existing VLOG0002/nonce protocol. Each accepted record is synced before its
acknowledgment. A privileged fd-only opener is available without changing host
groups/ACLs. Capture is bounded to 90 seconds for discovery and 30 seconds once
opened; the original-Android return poll is bounded to five minutes.

Acceptance requires kernel-facility records with the exact 6.18 release and
fresh command-line identity in the nonce-bound stream from the selected port.
That stream is emitted only after the controlled PID1 has loaded policy and
initialized USB. An interrupted stream can prove completed authenticated
records; it does not become a complete log-transport pass. A userspace echo of
a release, a handoff marker, ordinary Android reboot or zero-byte capture is
insufficient. Retained kernel release plus fresh identity can establish kernel
startup separately, but it does not prove PID1.

Only bounded reads are sent while waiting. Root/readout resumes after a
different boot has reached Android boot complete. Exact original full
boot/config, unchanged recovery and normal ADB are checked again. Owner Power
intervention and automatic return are reported separately from Linux evidence.

The budget is one protected source boot/restore and one load/jump. A failure
preserves the evidence and selects the next action from actual kernel output;
it does not authorize a repeated blind variant.

Validation: 936 full regression tests passed with ARM64 emulation and no skips;
the updated 11-case jump supervisor controls also passed. Four entry tests
exercise 21 register/ring/ABI cases, including injected EL2/state branches.
Twelve actual C load-client controls passed with the new aligned header using a
host CPU-set shim. The offline full-image layout/client is explicitly not
loadable. Read-only tablet preflight passed with zero writes/reboots and normal
ADB restored. Firmware/deadline source checks use the pinned ACK commit
d9318bdb4c34e8b2d997b4f67ced56b120b22b87, not an assumed current upstream API.

[Exact policy](../../evidence/independent-recovery/ack-native-two-stage-authorization-template.json).
[Prepared artifacts](../../evidence/independent-recovery/ack-native-preparation-result.json).
[Entry instruction qualification](../../evidence/independent-recovery/ack-native-entry-qualification.json).
