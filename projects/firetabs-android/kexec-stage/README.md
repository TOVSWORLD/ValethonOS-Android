# Prepare-only Linux kexec staging

This port implements allocation, segment copying, CRC verification and discard in
the already-running Linux kernel. **It cannot hand off to another kernel.** The
architecture restart module, relocation assembly, hypervisor shim, MMU changes and
shutdown implementation are not linked. Its unused `kernel_kexec()` symbol is an
exact `return -EOPNOTSUPP` stub; no ioctl exposes execution.

## Hardware acceptance — November 9, 2026

The exact pair below passed one 16 KiB hardware staging cycle: all three CRCs
matched, seven owned pages returned to zero, execution remained disabled, module
unload/device-node removal/RAM-file cleanup passed, and normal shell UID was
restored. No reboot, flash or handoff. Evidence archives match on lab/controller.
[Runtime receipt](../../../evidence/independent-recovery/kexec-stage-runtime-result.json).
The older proposed-test/preflight notes below describe preparation history;
the one staging-test approval is now consumed. Handoff/target logs remain unqualified.

## Exact review pair

- Target: the installed `4.9.337-g72940eb733af` LineageOS kernel, never the 3.18 TWRP.
- Module: `b2113b08c2b940f31594f346e8f139f37dd78689f8b58afc739493577c4ee3b9` (19,960 bytes).
- Static AArch64 client: `4eea03266cfb9a7eae532e7acdf4f4ee56f3380473fc624f449294518408290d` (143,392 bytes).
- Scope: `kexec-prepare-only-1`.
- Original boot and configuration pins are the same as the hardware-tested
  [compatibility probe](../kexec-probe/README.md).

The source adaptation preserves the generic kexec allocator from
[fabianishere/kexec-mod at 4ba956fd](https://github.com/fabianishere/kexec-mod/tree/4ba956fd60b29d2fea324515596b392afdcfa2c5).
`prepare_kexec_stage.py` verifies its pinned source hashes, applies bounded
adaptations and records the patch. The four derived generic files remain in the
ignored build cache with original GPL notices. This directory contains the
module wrapper, UAPI, limits, refusal stub and self-test client.

## What the module permits

`/dev/kxstage` is root-owned mode0600, requires CAP_SYS_BOOT, and allows only one
open and one admitted prepare per module lifetime. It supports status, prepare,
and discard. Close automatically discards; unload performs final cleanup.
Unknown ioctls, including the historical execute request, are refused. No compat
ioctl is provided: use the compiled native64-bit client even on32-bit Android.

Copied descriptors must have1–3 nonoverlapping page-aligned nonempty destination
ranges, at most32MiB total, valid source sizes, and an aligned entry within the
first source segment. Crash/preserve-context flags are rejected. The generic
allocator only writes pages it has allocated and owns; destination fields are
metadata for a future relocation, not permission to overwrite live physical RAM.
This port does not qualify any destination layout for a future handoff.

All allocations, including control/skipped/indirection pages, are counted and
capped at24,592 pages. GFP_NORETRY/NO_WARN limit allocator pressure; native Linux
allocation can still sleep, so this is not proof of an independent elapsed-time
bound. CRC32 is calculated over the actual copied pages including zero padding.
An upstream failure edge was repaired to free a source page if adding its relocation
entry fails. The counters and positive self-test are not exhaustive fault-injection
coverage of Linux memory-management behavior.

The target4.9 LSM read-file hook is retained rather than omitted. Its NULL-file
handling was inspected in the exact SELinux/IMA source. Normal kernel module ABI
and security checks remain enabled; no force-loading or policy changes.

## Concrete proposed runtime test

**Historical preflight before the successful November 9 test.** Read-only target preflight passed:
exact release/live config/full boot, executable RAM-backed `/dev`, no old staging
records/node/module, and more than32MiB MemAvailable. Temporary root adbd was ended.

The small self-test uses three patterned source buffers with total destination
size16KiB. It checks execution refusal, one admitted allocation/copy, all three
kernel CRCs and zero padding against independent host expectations, discard to
zero owned pages, and refusal of a second prepare. It then closes the device.
The kernel wrapper is unloaded, node removal is checked by module absence and
accounting logs, and the two RAM staging files are removed. No reboot, boot-image
write, kernel jump or raw storage operation is performed by the test.

`scripts/run_kexec_stage.py` defaults to read-only preflight. Executing the test
requires fresh exact module/client/boot hash-bound approval and current owner
availability; the prior logging-probe approval is consumed and cannot admit it.
The runner uses standard adb push, not an exec-out stdin stream, and requires
root adbd through the already-enabled rooted-debugging capability. It never
installs root, changes a policy, or starts a helper/recovery timer. Failure preserves
logs and attempts unload/cleanup, without repeating insertion or client execution.
A client alarm/host timeout cannot recover a kernel that becomes stuck; the existing
reviewed physical recovery remains the fallback if that occurs.

Passing would qualify this allocation/copy/checksum/discard path only. It would
not prove a Linux Image boots, that CPUs/DMA stop, firmware/EL compatibility,
retained logs, or new-kernel USB. Those remain separate before any real handoff.

## Reproduce and check

```sh
python3 scripts/prepare_kexec_stage.py --upstream /path/pinned-kexec-mod \
  --own projects/firetabs-android/kexec-stage --out /path/stage-source
python3 scripts/build_kexec_stage.py --source /path/pinned-vendor-kernel \
  --kernel-build /path/exact-config-build --stage /path/stage-source \
  --report /path/stage-build-result.json
# Cross-compile the client statically with AArch64 Linux/musl GCC.
aarch64-linux-musl-gcc -static -O2 -Wall -Wextra -Werror \
  projects/firetabs-android/kexec-stage/stage_client.c -o /path/kxstage-client
python3 scripts/verify_kexec_stage.py --module /path/stage-source/kxstage.ko \
  --provider /path/stage-source/stage-provider.symvers --client /path/kxstage-client \
  --output /path/stage-verified.json
python3 -m unittest discover -s tests -p 'test_kexec*.py'
```

All30 required symbol CRCs are bound to exact-source provider objects. Artifact
checks also require the tested release/ABI flags, a narrow memory/security/misc
import allowlist, the exact refusal stub, a static native client and absence of
restart/shutdown symbols or privileged-control/indirect-branch instructions.
These are necessary artifact checks, not a complete safety proof or runtime result.
The28 current tests include the prior probe tests and15 staging bounds, CRC,
artifact-gate and runner tests; host tests do not establish tablet acceptance.

## Next handoff contracts identified in the matched source

The exact4.9 `arch/arm64/kernel/relocate_kernel.S` zeroes x0–x3 before branching to
kimage_start. Its normal userspace loader must provide the appropriate entry
trampoline/purgatory; using that branch directly on a Linux Image would discard
the required x0 DTB argument. A future port must explicitly carry the selected
physical DTB pointer and honor each Image's text_offset/image_size, not copy the
old boot address blindly. None of this assembly is linked into this stage module.

The exact `machine_shutdown()` uses disable_nonboot_cpus, and machine_kexec refuses
multiple online/stuck CPUs. Those checks cannot be replaced by the upstream
module's unconditional false stuck-CPU stub. CurrentEL1 from the hardware probe
is not proof that an EL2 HVC restart path is usable. Source-kernel device/DMA
shutdown and Android filesystem quiescing must also be resolved before execution:
the generic kexec loader explicitly does not sync/unmount filesystems itself.
No firmware reset, HVC, CPU hotplug or reboot notifier was executed in this review.

## Offline Image entry candidate

`entry_trampoline.S` is a separate, unlinked six-instruction/40-byte candidate
that restores x0=DTB, x1-x3=0 and branches to the Image address after the native
relocator clears its incoming arguments. It does not stop CPUs or set CPU state.
`scripts/prepare_kexec_entry.py` accepts the assembled ELF object (no relocations)
or exact template bytes and emits a patched binary plus a plan marked
`device_execution_allowed=false`. It checks Image placement/full memory extent,
FDT header bounds and mutual overlap only; full FDT/board, RAM/reservations,
control-page/relocation integration and handoff/logging remain separate.

Example offline compilation (addresses must be explicitly reviewed; no defaults):

```sh
clang --target=aarch64-none-elf -c \
  projects/firetabs-android/kexec-stage/entry_trampoline.S -o /tmp/entry.o
python3 scripts/prepare_kexec_entry.py --template /tmp/entry.o \
  --image /path/uncompressed-Image --dtb /path/selected.dtb \
  --image-address IMAGE_ADDRESS --dtb-address DTB_ADDRESS \
  --entry-address TRAMPOLINE_ADDRESS --out /path/new-offline-output
# Linux with Unicorn 2.1.3 installed; executes compiled instructions in emulator:
KXENTRY_CC=aarch64-linux-gnu-gcc python3 -m unittest discover \
  -s tests -p 'test_kexec_entry.py' -v
```

Nine Linux checks passed, including six actual instruction emulations. A sample
plan using bytes from the verified working original boot is recorded in
`evidence/independent-recovery/kexec-entry-build-result.json`; its addresses remain
hypothetical. No candidate was uploaded or executed on the tablet.

The live CPU DT selects `mt-boot` on all four cores. This uses MediaTek PSCI plus
MTCMOS power sequencing, with unbounded WFI/SRAM/power-status waits and a PSCI
kill-error propagation gap. See `kexec-cpu-shutdown-audit.json`. Treat safe,
bounded secondary shutdown as the next handoff implementation prerequisite.

## Bounded secondary shutdown — compile-only candidate

`bounded_secondary_off.h` implements the matched CPU1–3 power-down sequence using
injected I/O and firmware callbacks. `bounded_secondary_adapter.inc` binds it to
the original kernel's regmap and shared MTCMOS lock, with compile-time assertions
for every used register/bit. Firmware OFF is mandatory; missing affinity-info is
an error. Every regmap error propagates. All polls share a step/time budget; WFI
is rechecked after nonblocking lock acquisition, both power banks must report OFF,
and every exit releases an acquired lock. Failure after a partial sequence does
not automatically retry or power the core back on.

`prepare_kexec_cpu_off.py` verifies pinned vendor mtcmos.c/mt_psci.c/mtcmos.h hashes,
generates an overlay/patch, changes the kill callback to this bounded core, and
retains errors in a sticky bitmap. It also provides
`mt_kexec_secondary_off_gate()`: a read-only final check requiring CPU0 as the sole
survivor, exact topology, all secondary firmware/power status OFF and no prior
error. **A future handoff must invoke this gate while hotplug stays serialized
through relocation.** The generic kernel only warns on kill errors; compiling a
new kill callback alone does not veto all generic restart paths.

```sh
python3 scripts/prepare_kexec_cpu_off.py --source /path/pinned-mt8163-files \
  --own projects/firetabs-android/kexec-stage \
  --audit evidence/independent-recovery/kexec-cpu-shutdown-audit.json \
  --out /path/new-overlay
python3 scripts/build_kexec_cpu_off.py --source /path/matched-vendor-tree \
  --kernel-build /path/exact-tested-config-build --candidate /path/new-overlay \
  --report /path/compile-result.json
python3 -m unittest discover -s tests -p 'test_kexec_cpu_off.py' -v
```

Fifteen C fault tests pass; all24 entry/shutdown tests pass on Linux. Exact ARM64
objects compile. The build-only module wrapper has15 unresolved-symbol warnings
with the partial provider table: **never load it**. This is a source integration
candidate, not a runtime replacement for the hardware-tested staging module. No
source kernel, boot image or tablet was changed. See the receipt at
`evidence/independent-recovery/kexec-cpu-off-build-result.json`.

The4096-step/100ms policy is uncalibrated. Budgets cannot preempt firmware or bus
accesses that never return, or establish an elapsed bound for the whole OS CPU
hotplug lifecycle. Full source-kernel integration, hotplug serialization, failure
recovery and actual hardware power-off acceptance remain required.

## Isolated full source-kernel integration

The legacy affinity binding and bounded secondary-off candidate now link into a
full ARM64 Image with the original configuration. The final off-state gate is
present but not called by a handoff path. No boot/handoff is admitted by this build.
The Image is retained privately; its SHA-256 is
`3df1bd6cd206b102b20c302b976db85a4103bdbad9e7e88c1f2f2ce45caf292b`.

```sh
python3 scripts/prepare_kexec_source_integration.py --source /path/pinned-kernel \
  --kernel-build /path/original-matched-build --cpu-off /path/cpu-off-overlay \
  --legacy /path/corrected-legacy-binding \
  --audit evidence/independent-recovery/kexec-cpu-shutdown-audit.json \
  --out /path/new-isolated-root --gcc13-compat
make -C /path/new-isolated-root/source O=/path/new-isolated-root/build \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j4 Image
python3 scripts/verify_kexec_source_integration.py \
  --build /path/new-isolated-root/build --output /path/linked-verification.json
python3 scripts/validate_kexec_source_integration.py --source /path/pinned-kernel \
  --kernel-build /path/original-matched-build --cpu-off /path/cpu-off-overlay \
  --legacy /path/corrected-legacy-binding \
  --audit evidence/independent-recovery/kexec-cpu-shutdown-audit.json \
  --prepared /path/new-isolated-root --output /path/admission-controls.json
```

`--gcc13-compat` applies pinned vendor compatibility corrections only in the
copy: four indentation changes, two getter definitions matched to their declared
enum return types, and a display header reusing primary API declarations. Original
files and compiler warning policy stay unchanged. ARM64 enum width/type controls
passed; external-module CRC and boot compatibility remain unqualified. Six
admission controls and an actual patch dry run passed. The build recipe does not
freeze Kbuild timestamp/user metadata, so it does not promise bit-identical bytes.
See `evidence/independent-recovery/kexec-source-integration-build-result.json` for
the exact linked artifacts, source hashes and all five prior failed build attempts.
