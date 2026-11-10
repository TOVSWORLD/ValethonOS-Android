# Current state — manually recovered, November 10, 2026

Original Android, full boot/config and recovery verified after owner-assisted
recovery. Normal ADB restored. Pstore mounted/enabled but record directory empty;
handoff stage remains unknown. Next work is post-failure recovery timer and phase
logging/readout: exact watchdog driver can stop its timer during device_shutdown.
No new jump, boot write or automatic reboot; approvals consumed.

[Recovery evidence and next implementation scope](NATIVE-KEXEC-POSTFAILURE.md).

# Current state — first jump trial stopped, November 10, 2026

Native load succeeded and one orderly kexec request was issued. Target Android
was not observed within 300 seconds; ADB is absent afterward. No partition
writes or automatic retry. Original boot was verified restored on flash before
the trial; post-trial readback and target entry are unverified. Owner screen
observation and recovery are needed. Next: post-failure logging/readout diagnosis.
Earlier pending-approval/preparation status below is historical and superseded.

[Actual trial receipt](../../evidence/independent-recovery/native-first-jump-runtime-result.json).

# Current state — successful native source boot, November 10, 2026

Owner-approved temporary native source boot PASSED: Android home screen, native
config verified, original full boot restored on flash, recovery unchanged, normal
ADB restored. First experimental jump bundle/client and read-only live preflight
are prepared; no jump/load yet. Await owner approval for the actual jump.
Failed-jump logging remains post-failure follow-up, not a prerequisite.

[Exact first-jump scope and evidence](NATIVE-KEXEC-FIRST-JUMP.md).

# Current direction — November 10, 2026

Native kexec handoff kernel built and linked gates verified. Temporary source-boot
package and corrected live read-only preflight complete; awaiting owner-attended
source-kernel boot test. This enables subsequent experimental jump preparation.
Failed-jump logging follows a failed experimental jump, per owner direction,
and is no longer a prerequisite. Historical stricter sequencing below is superseded.

[Exact next test, rollback and evidence](NATIVE-KEXEC-NEXT-TEST.md).

# Active work queue — ordered delivery

## Existing-kernel console survives orderly reboot — November 10, 2026

One owner-approved run of runner SHA-256
`4c4e56c06ffdd8c8ec73a23dd4d7532bd2486ec8365257400ae46fdc3e0b8388`
wrote one unique console marker and requested one ordinary reboot into the same
installed4.9 kernel. Exactly one retained console-ramoops line matched the source
line byte-for-byte. Boot identity changed, normal Android returned, original full
boot/config hashes and backend geometry matched again, and UID2000 ADB restored.
No boot-image write, module load, experimental jump, failure injection, pstore
record deletion or nonmatching/PMSG/account-log collection. Approval consumed;
no automatic repeat. Private marker-only result/approval archive retained with hashes.

This qualifies console retention through this exact orderly software-reboot route,
not failure/power-loss retention, target early-entry coverage or the older TWRP
reader/layout. Keep #346/#348 open. Next engineering remains final CPU gate wiring
under serialization, partial-shutdown recovery/readout, and preservation of this
existing writer region in source/target RAM layouts alongside DMA/cache/MMU/EL
and early logging contracts. No new hardware test selected by this result.

[Actual retained-marker result](../../evidence/independent-recovery/pstore-warm-reboot-runtime-result.json).

## Combined source kernel Image built and retained — November 9, 2026

Approved isolated full-kernel compilation PASSED with the corrected legacy affinity
binding and bounded MT8163 secondary-off candidate linked together. Image is
15266304 bytes, SHA-256
`3df1bd6cd206b102b20c302b976db85a4103bdbad9e7e88c1f2f2ce45caf292b`;
header text_offset524288, memory extent16490496, flags10. Release remains
4.9.337-g72940eb733af. Original source, original build configuration and isolated
resolved configuration remain unchanged (configb0871996…f3859).

Linked verification confirms the CPU-kill callback calls bounded secondary-off,
the final gate calls the independent off-state checker, and legacy affinity uses
the selected conduit. Six actual source-admission controls pass, including corrupt
binding/core/config/boot-mode inputs and output inside original source. Combined
patch dry-runs cleanly against original pinned source. Local kexec suite63 tests
passes with one existing emulator skip; earlier Linux instruction checks remain
separately attributed.

Strict GCC13 compilation exposed baseline vendor compatibility errors. Five failed
build attempts/log hashes are preserved in the receipt. The final recipe includes
four whitespace-only indentation repairs (audio, CPU frequency, sensor mutex
unlock, USB), two getter return definitions aligned with existing enum declarations,
and a display header reusing its primary enum-return API declarations. ARM64 static
checks verify the enums' underlying integer type and width; function bodies are
unchanged by those type fixes. No warning policy was relaxed. These checks do not
qualify existing external-module CRC compatibility or the new kernel at runtime.

Retained Image/vmlinux/System.map/config, combined patch, source manifest, controls
and all build-attempt logs in a private archive on the lab and locally:15928406 bytes,
all archive/file hashes verified. Build timestamp/identity metadata were not frozen;
this retained artifact is attributable but bit-identical rebuilding is unqualified.
No boot image packaged, tablet command, CPU hotplug, reboot, flash or handoff.

Next engineering gates: wire the final off-state gate while hotplug stays serialized
through relocation; define partial-shutdown recovery with independent attributable
logs; preserve source-memory ownership and complete device/DMA/filesystem/cache/MMU/
EL contracts and target early/failure logging (#348). The linked final gate currently
has no handoff caller. Full compilation alone cannot veto generic restart paths or
admit this Image to a hardware boot/handoff test. Independent failed-load recovery
remains open under #346.

[Full build, failed-attempt trail and retained-artifact receipt](../../evidence/independent-recovery/kexec-source-integration-build-result.json).

## Corrected legacy affinity binding verified — November 9, 2026

Owner-approved transfer and exact ARM64 object compilation completed. psci.o is
19488 bytes, SHA-256
`89bdad7138c5ea831f12948d3b65dbcce80b6d0a14c720b17e7fa60f9138ff7d`;
original matched source remains unchanged. Corrected generated source hash is
`c52aa352263e0777a38d12ec6eda0958b1738c1d9c7ad75a9f5be411c463d9e4`.
17 native checks execute the actual generated initializer/callback text with
mocked APIs: no firmware call during initialization, positive OF match scores
accepted, wrong board/conduit/property/FID rejected, callback bounds and errors
preserved. 20 actual ARM64 callback instruction cases pass under Linux Unicorn,
with conduit stubbed: exact SMC32 FID/target/level/zero arguments, results forwarded,
invalid targets/levels rejected without calls. These are offline checks; live
query capability was separately observed in the earlier approved probe.

Added reproducible pinned-source/config builder and both validation scripts.
The build-only module wrapper has21 unresolved-symbol warnings from partial
symvers; it MUST NOT be loaded. This is object compilation, not full source-kernel
or boot-image acceptance. No tablet change or additional firmware call occurred.

Next prepared action: isolated full-kernel compile combining the verified legacy
binding and previously compiled bounded CPU-off candidate. Use a separate source
copy/build directory, preserve originals/config, record Image/config hashes and
errors. No deployment, boot-image write, reboot, CPU hotplug or handoff. Automatic
approval review rejected this as a broader integration than the approved binding
build; that combined build did not execute. Await explicit approval for the
combined offline build. Hotplug serialization/final gate wiring, partial-shutdown
recovery and independent target/failure logging #348 remain open.

[Binding compile and validation receipt](../../evidence/independent-recovery/kexec-legacy-affinity-build-result.json).

## Live affinity query accepted — November 9, 2026

One approved insertion of module SHA-256
`a41314b4afcf554343bea7ff80c7a5ca902f3068713d3d22e9ee1ed3a7441828`
completed exactly four SMC32 AFFINITY_INFO queries. CPU0/CPU1 returned ON (0);
CPU2/CPU3 returned OFF (1). Current CPU0 was ON and the online mask was 0x3,
consistent with those observations. This qualifies the legacy query capability
on the installed firmware; it does not qualify active secondary shutdown or
power-controller readback. Module unloaded, RAM file removed and normal UID2000
ADB shell restored. No CPU hotplug, reboot, flash or jump. Approval consumed;
no automatic rerun. Private source logs archived with hashes in the sanitized
[kernel query runtime receipt](../../evidence/independent-recovery/kexec-affinity-runtime-result.json).

Next source integration is the corrected legacy affinity binding, followed by
CPU-off/final-gate integration and recovery/logging contracts. Attempt to transfer
and compile that binding on the established host was rejected by automatic
approval review as broader than the approved probe build. The rejected transfer
and build did not execute. Await explicit approval for source-kernel binding
transfer/compilation; no additional tablet test selected or authorized. Earlier
source-transfer approval is retained with its original probe scope. Logging #348
and independent failed-load recovery #346 remain unqualified.

## Affinity query artifact ready for hardware review — November 9, 2026

Owner approved updated source transfer to the existing Linux lab host. Corrected
module rebuilt against the matched kernel/config with all 18 imported symbol CRCs
and module_layout verified against 19 exact providers. Module SHA-256:
`a41314b4afcf554343bea7ff80c7a5ca902f3068713d3d22e9ee1ed3a7441828`
(9088 bytes). Actual compiled ARM64 initializer emulation passes ten cases with
kernel/SMC APIs stubbed: valid topology issues exactly four SMC32 AFFINITY_INFO
queries, invalid board/conduit/FID/topology cases issue none. Unsupported firmware
responses remain unqualified; no real firmware was called. Eleven Linux probe
tests pass. Local suite remains 63 tests, one existing emulator skip.

Fresh read-only tablet preflight matched release/config/full original boot hash,
RAM-backed /dev, absent module and no prior KXAFF records. Zero insertions and
firmware queries. Temporary root adbd restored to UID2000. Historical transfer
blocker below is resolved; stale earlier module remains excluded. Corrected legacy
binding has been generated offline, but that source-kernel binding has not been
compiled after its Boolean-normalization correction and is not selected for this
runtime test.

Next: owner approval and availability for one insertion, four affinity queries,
fresh source-log capture, unload/RAM cleanup and normal-shell restoration. No
CPU OFF/ON/SUSPEND, power writes, reboot, flash or jump. A nonreturning firmware
call could require a physical power cycle; a host timeout cannot interrupt it.
Query success alone does not prove secondary shutdown, retained logs, independent
recovery or handoff. Those gates remain open under #346/#348.

[Exact build/emulation/preflight receipt](../../evidence/independent-recovery/kexec-affinity-development-result.json).

## Legacy firmware affinity prerequisite — November 9, 2026

The exact kernel's legacy PSCI initializer ignores the live device-tree
`affinity_info=0x84000004` property. Consequently the bounded secondary-off
candidate cannot establish firmware OFF and must refuse admission. Generic PSCI
support cannot be assumed. Prepared an exact-source, board/conduit/FID-gated
binding and a separate four-query capability module; neither is hardware qualified.
The query module uses SMC32 AFFINITY_INFO only, validates CPU0–3 topology, and
performs no CPU OFF/ON/SUSPEND, power writes, reboot, flash or handoff. Its runner
requires exact artifact approval, permits one insertion, preserves logs and
requires unload/RAM cleanup. A nonreturning firmware call still cannot be bounded.

Local suite: 63 tests pass, one existing ARM64 emulator test skipped locally
(previously passed on Linux). Eleven new tests cover policy, report parsing and
mocked one-shot execution/cleanup. Offline patched-source generation passes.
Initial module build and CRC review exposed OF compatibility match scores being
positive integers rather than Boolean one; corrected both callers with `!!`.
The earlier binary is stale and must not be tested. The corrected module rebuild,
compiled-instruction emulation, and fresh read-only tablet preflight remain pending.
Automatic approval review rejected source transfer to the existing Linux lab host;
no rejected transfer or tablet test ran. Await source-transfer approval before
continuing lab verification. Hardware approval must refer to the final rebuilt
hash; no approval request for a stale artifact. Logging/retention and failed-load
recovery (#348/#346) remain open. Earlier bounded-shutdown and staging receipts
retain their original limited scope.

## Bounded MT8163 secondary-off candidate compiled — November 9, 2026

Implemented the matched secondary shutdown core/adapter, pinned patch generator,
compile verifier and final read-only off-state gate. Unlike the old wrapper, the
candidate requires explicit firmware OFF, retains failures, checks regmap return
codes, uses nonblocking acquisition of the existing MTCMOS lock, and caps total
steps plus elapsed time across WFI/SRAM/power-status waits. Rechecks WFI under
lock before any write, preserves the vendor register sequence/other bits, and
requires both power-status banks OFF. No rollback/retry after partial power-down.
The final gate requires exactly four possible CPUs, CPU0 alone online, firmware
OFF for all three secondaries, both status banks OFF, and no sticky prior failure.
Its I/O adapter has no writer; it cannot initiate power sequencing.

Compiled actual ARM64 mtcmos.o/mt_psci.o and combined object against unchanged
source72940eb733af and exact configb0871996…f3859/release4.9.337-g72940eb733af.
Disassembly confirms the kill callback calls the bounded path and final gate exists.
Fifteen native C fault tests pass (frozen/backward clock, busy lock, WFI loss,
SRAM/status timeout, every successful-path read/write failure, every step-boundary
exhaustion, topology/sticky/final-gate errors). Linux suite24 entry/shutdown tests
passes including actual ARM64 entry emulation. Local kexec suite52 tests passes
with one local emulator skip independently passed on Linux. Original vendor source
hashes verified unchanged. Candidate objects are compile-only: the external-module
build emits15 unresolved-symbol warnings with the partial symvers table; its .ko
wrapper is NOT a loadable/runtime-qualified deliverable. No tablet operations.

Remaining integration: call the final gate while hotplug remains serialized through
relocation; preserve the source-memory ownership until then; bind survivor/masks,
handle partial-shutdown abort/recovery, and integrate device/DMA/filesystem/EL/cache
state and target logging. The core's4096-step/100ms policy is not calibrated hardware
timing. Poll budgets cannot interrupt a stuck firmware call, regmap/bus transaction,
or clock callback, nor bound the entire generic cpu_down lifecycle. A working
replacement source-kernel build/qualification remains necessary; this patch is not
an approved runtime module for the existing kernel. No kernel jump admitted.

[Compile/source/fault-test receipt](../../evidence/independent-recovery/kexec-cpu-off-build-result.json).


## Linux Image entry candidate implemented — November 9, 2026

Implemented a separate 40-byte/six-instruction ARM64 argument trampoline for the
matched relocator's zeroed x0-x3 entry. It loads the selected physical DTB into x0,
zeros x1-x3 and branches to the Image entry without stack use or memory writes.
It is not linked into the hardware-tested staging module and has no device runner.
Offline builder verifies exact assembled code/no unresolved relocations, ARM64
Image header/text_offset/full image_size, FDT header bounds, alignments and mutual
nonoverlap. It does not qualify the FDT tree, RAM ownership or a boot-ready layout.

Nine Linux tests pass, including actual GNU-assembled ARM64 instructions emulated
at six combinations of relocation/Image addresses (including above4GiB), poisoned
incoming registers, unmapped stack/DTB, no writes and exact branch/argument checks.
Local host suite37 tests passes with the emulator test skipped; local Unicorn
crashed before a result, so instruction execution was verified on Linux instead.
The real known-good Image/first appended DTB were extracted from hash-matched
original boot08fcf345…aa1e using bounded gzip/EOF checks. Builder exercised against
those actual bytes with hypothetical, explicitly unqualified addresses. The Image
file15137280B declares16363520B memory extent; collision checks reserve the latter.

Read-only live CPU nodes all select mt-boot; exact config enables MTK_PSCI and
HOTPLUG_CPU. Traced actual mt_cpu_psci_ops to MT8163 mt_psci.c/mtcmos.c: kill logs
PSCI failure then returns MTCMOS result, and WFI/SRAM/power-status busy waits have
no timeout. Generic affinity_info absence also permits success without off proof.
Do not use generic PSCI assumptions or call this unbounded path as a qualified
handoff. Next implement/review bounded failure-propagating secondary shutdown
against the matched power-controller contract; bind observed power status before
relocation and preserve source-memory ownership until every secondary is proven
released. Cache/MMU/EL, DMA/device/filesystem shutdown and independent target
logging/failure retrieval remain open. No CPU hotplug, firmware call or jump ran.

[Entry build/validation receipt](../../evidence/independent-recovery/kexec-entry-build-result.json).
[Live CPU/source audit](../../evidence/independent-recovery/kexec-cpu-shutdown-audit.json).


## Prepare-only staging passed on hardware — November 9, 2026

One exact approved module insertion and one client run passed on the installed
4.9 kernel. Three segments totaling 16 KiB matched independent CRCs including zero
padding; seven owned pages returned to zero. Execute stayed disabled. Module
unload, misc node/class removal and both RAM-file removals were verified. Normal
shell UID was restored. No reboot, flash or kernel handoff. Complete private
logs/approval receipts were archived on lab/controller with matching SHA256.
Approval consumed; no module/helper/test remains armed.

Fresh preflight also passed. It initially stopped before device access because
lab runner/verifier copies lacked the committed client-ELF and node-removal checks;
reviewed differences and synchronized those two scripts, preserving exact approved
module/client bytes. Runtime receipt qualifies allocation/copy/CRC/discard only.

Next source work: resolve matched handoff and independent target logging/recovery.
Further exact-source review confirms cpu_soft_restart's EL2 switch is conditional
on is_kernel_in_hyp_mode/is_hyp_mode_available; observing CurrentEL1 alone does
not select an HVC route. In arch/arm64/kernel/smp.c, op_cpu_kill returns success
without a callback, and __cpu_die logs some shutdown failures rather than returning
a veto. Therefore one online CPU alone is insufficient proof that firmware has
released every secondary CPU before overwriting source memory. Bind actual CPU
operations and validate a failure-propagating parking contract; do not inherit the
upstream false stuck-CPU stub. DTB/x0 trampoline, Image placement, cache/MMU,
device/DMA shutdown and filesystem quiescing remain open. Source ADB ends at
handoff; no target early/failure log or retention route is yet qualified.

[Actual hardware staging receipt](../../evidence/independent-recovery/kexec-stage-runtime-result.json).


## Prepare-only kexec loader port built — November 8, 2026

Continued source work beyond the successful logging probe. Ported the generic
kexec allocation/copy machinery to the exact tested4.9 kernel. The19,960B module
b2113b08…e3b9 contains no restart/relocation/hypervisor module, links no shutdown
callback, and its unused execute stub is exact return-EOPNOTSUPP. All30 required
symbol CRCs match exact-source providers; compiled instruction/import checks pass.
Repaired an orphan source-page allocation failure edge and added bounded copied
segment checks,3-segment/32MiB payload caps,24,592 owned-page hard cap and actual
copied-page CRC/zero-padding reports with count-to-zero discard/close cleanup.

Built a native static client4eea0326…290d for one16KiB three-segment staging cycle,
independent checksum comparison, blocked execute/duplicate-prepare requests and
verified discard. Guarded runner requires fresh module/client/boot-bound approval,
exact current release/config/boot, root adbd, executable RAM /dev, clean staging
state and available memory; no flash/reboot/CPU shutdown/handoff.28 tests pass
including the earlier probe suite. These checks are source/build/preflight evidence,
not actual hardware RAM-staging acceptance.

Read-only live preflight passed with631800KiB MemAvailable. No module insertion,
client execution or RAM file upload occurred; temporary root adbd ended and normal
shell UID restored. New stage runtime approval is pending separately; the prior
logging-probe approval is consumed. No actual kernel jump is admitted.

Further source review found the native4.9 relocator clears x0 before kimage_start;
a direct Linux Image branch therefore needs the appropriate DTB-carrying entry
trampoline. CPU parking, EL/HVC behavior, device/DMA shutdown and clean filesystem
quiescing still require explicit handoff contracts. No new jump binary selected.

[Build review receipt](../../evidence/independent-recovery/kexec-stage-build-result.json).
[Exact module/client/procedure](../../projects/firetabs-android/kexec-stage/README.md).


## Actual Linux compatibility probe succeeded — November 8, 2026

The exact logging-only module371fe33c…e889 loaded once into the installed
4.9.337-g72940eb733af kernel, passed normal ABI/version checks, produced all ten
fresh kernel records over ADB, and unloaded successfully. Runtime observations:
EL1,4KB pages,3 online CPUs at the sample instant; all8 queried symbols present,
including set_cpu_boot_mode_flag. This is actual hardware execution/log capture,
not a model result. It qualifies this module ABI and current-kernel printk/ADB
transport only, not kexec, CPU parking, firmware state, new-kernel entry or logs.

The first preflight stopped with rooted debugging disabled; owner enabled it.
Two exec-out stream staging attempts timed out with0 module insertions and verified
RAM cleanup. Standard adb push into verified RAM-backed /dev solved the host
transfer problem without changing module bytes. One actual insmod, no force-load,
verified unload/module absence and RAM cleanup.13 runner/verifier tests pass.
Private evidence archives match lab/controller. Original boot/recovery/bootstrap
were verified before the one approved normal boot; no flash or handoff occurred.
LineageOS remains running; temporary root adbd ended, user shell restored. No
watcher/helper/module remains armed, no owner action is pending, approval consumed.

Next source stage: adapt a matched4.9 kexec loader, keeping execution disabled
until allocation, CPU/DMA shutdown and entry contracts are independently reviewed.
Do not reuse the probe approval for a handoff or an additional module execution.

[Actual hardware receipt](../../evidence/independent-recovery/kexec-probe-runtime-result.json).


## Linux-to-Linux stage1 probe built — November 7, 2026

The actual original normal boot image runs 4.9.337-g72940eb733af, not the 3.18
TWRP kernel. Extracted its embedded config (b0871996…f3859) and located exact public
source commit72940eb733af8df948cc216cb977cd8be9cba5a9 in amazon-oss. A stale cached
3.18 vendor config is not the installed normal kernel configuration. No attempt
was made to load a module into the unmatched TWRP kernel.

Built a6144B logging-only ARM64 probe with exact release/ABI flags and zero config
option changes. Six CRC providers were generated from individual exact-source
objects; the partial table is not a complete kernel build's Module.symvers.
Controller/lab artifact hashes match; all required CRCs/imports pass verification.
Actual disassembly has40 instructions, one CurrentEL read and no privileged write,
SMC/HVC, indirect jump or cache/MMU maintenance opcode. External calls are limited
to the reviewed logging/read helpers. GCC13.3 differs from the original GCC6.3.1;
runtime module-version checks remain mandatory and no force-loading is permitted.

Thirteen verifier/runtime boundary tests pass, covering wrong architecture/release,
missing/mismatched CRCs, handoff imports, current TWRP rejection, wrong live config,
wrong approval, preflight-only behavior, rejected insertion with no retry, complete
fresh-report attribution, RAM cleanup and unload. The runner performs no reboot,
flash or kernel handoff. Execution requires fresh exact approval/current availability
and a live normal-kernel release/config/fullboot hash match with existing root.
Probe staging is only in RAM-backed /dev; a rejected module is never forced.

This is a completed compatibility-test artifact, not a working kexec implementation.
No new image, module insertion or reboot has occurred. Next is one separately
approved boot of existing LineageOS and one probe load/unload, then a matched kexec
port using the observed compatibility report. The initial probe cannot establish
DMA shutdown, stopped secondary CPUs, firmware entry or target logging.

[Build receipt](../../evidence/independent-recovery/kexec-probe-build-result.json).
[Source and concrete review](../../projects/firetabs-android/kexec-probe/README.md).


## New investigation: Linux-to-Linux handoff, November 7, 2026

Owner rejected further development of the failed LK mailbox/screen avenue.
Selected a distinct source investigation: use the running 64-bit Linux recovery
as the image loader, with a matched ARM64 kexec port. This bypasses custom LK
hooks, LK allocation/storage services, and its 32-bit-to-64-bit entry transition.
It does not replace secure firmware or establish PSCI/SMP compatibility.

Read-only live facts: recovery 3.18.19-g51c2c8d5bfb is aarch64 with root access;
modules_disabled is 0. Captured 130938 bytes of current dmesg over existing ADB;
this qualifies that live recovery read path only. Kexec core symbols are absent.
Pinned and Git-blob/SHA256-verified 21 upstream module files at
4ba956fd60b29d2fea324515596b392afdcfa2c5. All seven named dynamic dependencies
are present in live kallsyms, and kallsyms_lookup_name has an export symbol.
This is symbol-name evidence, not compatible signatures or a working module ABI.

Do not load upstream unchanged: its default detect_el2 path dereferences the
missing set_cpu_boot_mode_flag helper; it stubs the stuck-CPU test false, has
unqualified CPU-mode decoding/identity mappings, and lacks a matched recovery
build configuration here. Missing source/config provenance must be resolved or
a reproducible matched first-stage kernel built before module qualification.

Next milestones are distinct: (1) resolve build ABI and compile a no-handoff
compatibility probe; (2) audit memory placement, CPU parking, cache/MMU state,
DMA/device shutdown and firmware entry; (3) if admitted, chainload an already
working kernel before changing to the modern kernel. Preparation/load errors
must be retrieved over the source Linux's working host log connection. That
connection will disconnect at handoff; target early logs, reserved-memory ownership
and failure retrieval still require independent qualification. No claim of
continuous ADB across kexec, retained RAM across power-off or guaranteed target logs.
No physical test, module insertion, boot-image change or reboot selected.

Upstream: https://github.com/fabianishere/kexec-mod . Latest MT8163 upstream work
also explicitly requires custom TF-A/U-Boot/OP-TEE for its Echo Dot target; it is
not a drop-in douglas firmware alternative. Do not transplant its firmware or
reserved memory to this tablet.

[Read-only source/compatibility receipt](../../evidence/independent-recovery/recovery-linux-kexec-route.json).


## Actual copy-control3 result — November 7, 2026

The approved corrected known-stack control reached the home screen, but full
collection again returned HOSTCONTROL only (sequence 1, 85 bytes), with no loader
record or invalid slot. No attributable screen pattern was captured; the owner
was not watching closely, so physical absence is not established. Hardware capture
acceptance failed. Do not repeat this method unchanged or admit a custom-kernel
trial on these results. The cause of missing loader records remains unresolved.

The single original FACTORYM return helper exited 0 after USB reseating. Complete
readout and receipts were archived on lab/controller with matching SHA256. Normal
bootstrap was already original; no bootstrap restore write was needed. Original
full boot restored once, readback and final boot/bootstrap/recovery/header/GPT/alias
checks passed, RAM staging cleanup verified. TWRP remains running, no reboot,
watcher/helper running, pending owner action or armed test. Exact approval consumed.

The next decision is whether to change the boot/observability approach or end the
modern-kernel port effort. This failed capture is not proof that the hardware is
incapable of a port. No further physical test is selected.

[Actual trial receipt](../../evidence/independent-recovery/loader-copy-control3-trial-result.json).


## Copy-corrected capture control — recovered November 7, 2026

The former tail-hook model was invalid for physical delivery: the bootstrap copies
only 968 bytes of embedded LK. The late hook is outside that span. This explains
the placement error, not every historical missing record or a kernel boot failure.
The corrected resident code installs the exact branch before the original LK cache
clean/app. All linked bootstrap bytes fit in the copied prefix (1898/2304 bytes).
The native timer-dependent display routine is replaced by bounded mirrored pixel
writes. Framebuffer visibility and cache/controller effects remain hardware assumptions.

Recovery validation: source rebuild is byte-identical to the packaged bootstrap;
12 exact-copy/execution controls, eight pixel phases, ten synthetic photo controls,
five decoder/guard unit tests and independent artifact verification pass. On this
Mac the sandbox terminates ARM emulation with signal 4; the same replay passes
outside the sandbox. Pillow is required for the controller photo decoder.

Exact review pair:
- Boot: `b9377fdb1c8ca78e627d19db0d0eee7fc84228acc54f248edc98ebec3e05ea1f`
- Observer: `2dd2de6bb6b07b5c616621cd4ed65f1a4a023cb695a41c896496cc67f1229188`
- Screen token: `d73d`; scope: `known-boot-copy-control-3`.

The private local bundle contains original rollback images, exact hash guards,
collection/restore scripts and the camera decoder. It is unapproved, unexported and
unarmed. Earlier approvals are consumed. Historical embedded-tail packers now reject
use. No new custom-kernel boot or claim of qualified physical logging follows.

The remaining dependency is a physical observation of this changed known-stack
control, with the owner available for recovery and a camera recording the entire
screen from before boot through the observation. This is a separate calibration
boot; the standing restriction against separate diagnostic trials must be explicitly
resolved before installation. Do not treat the general request to make progress as
exact approval or owner availability. First read-only preflight must confirm the
current original hashes, recovery identity and partition geometry; old TWRP state
is historical, not a fresh device observation.

If explicitly selected: install the exact observer and known-stack boot once using
the bundled guards, verify readbacks, and have the owner perform the agreed boot.
Capture the screen continuously; decode still frames locally with the exact token.
Collect the full mailbox before restoration, then restore and verify originals with
the existing scripts. No automatic reboot/return or retry is authorized here.
Phase 1 establishes resident arrival/install result; phase 2 establishes late-hook
arrival; later rows identify rejection/recorder results. A screen record alone does
not qualify durable logging or prove kernel entry. A blank/unreadable capture cannot
locate execution. If no attributable screen or mailbox record is recovered, stop
this capture approach and reassess the boot route rather than repeat it unchanged.

Local decoder:
```sh
out/loader-audit-venv/bin/python scripts/decode_loader_screen_photo.py \
  --image /absolute/path/to/frame.png --token d73d \
  --quad TL_X TL_Y TR_X TR_Y BR_X BR_Y BL_X BL_Y
```
Corners are in logical portrait order. Private images/nonces stay out of git.


Offline source delta: independent arrival/first-rejection witness implemented.
New analysis-only late profile uses1547/1587 proven console bytes and preserves
original read redirection. Eleven actual ARM controls pass, including exact
resident main and archived formatter, register/SP/APSR replay and distinct failure
codes. Display pixels/hardware remain modeled. Native display update can reach
an uncapped tick-dependent wait: actual wait replay returns with advancing samples
and remains in the loop with frozen samples. Both physical packers reject this
profile pending independent display-path qualification. No candidate/device action
or new kernel build; originals remain verified/TWRP/unarmed.


Actual control2 complete: owner confirmed original home screen, but collection
passed with only HOSTCONTROL seq1/85B, no loader/kernel record or invalid slot.
One original FACTORYM helper exited0. Evidence archive and supplement matched
lab/controller. Normal bootstrap already original: no agent bootstrap restore write.
Original fullp5 restored once; fullp5/p6, bootstrap/header/GPT/alias/RAM cleanup
verified. TWRP left running, no reboot; all workers stopped, no owner action pending.
One bounded /proc/last_kmsg read returned No such file; no fallback log recovered.
Exact approval consumed. No repeat trial, new kernel build or control3 selected.
Next: establish active bootstrap reachability and expose the first rejected gate
before another mailbox writer test. Logging and custom kernel entry remain unproved.
[Actual control2 result](../../evidence/independent-recovery/pre-shutdown-control2-trial-result.json).


Historical control1 result follows.

Latest actual result: known-stack capture control1 is complete. Owner confirms home
screen with unchanged original header/kernel/DT/ramdisk, but full collection found
only HOSTCONTROLseq1/85B and no target record. This fails recorder qualification;
prior silence cannot locate a modern-kernel failure. One original FACTORYM helper
exit0; expired pre-helper return window preserved with0 launches. Original normal
bootstrap was already original, so no agent bootstrap restore write. Original fullp5
restored once; fullp5/p6, headers/ranges/GPT/aliases/RAM cleanup verified. TWRP left
running/no reboot; no watcher/helper/owner action pending. Exact approval consumed;
no unchanged control/kernel build/trial or rearm selected.
[Actual control result](../../evidence/independent-recovery/known-boot-capture-control-trial-result.json).

Historical installation snapshot (superseded by completed result above): exact approved known-stack control p5+normal observer installed
once, readbacks/p6/RAM cleanup verified. Copied guard's stale trial8 prefix/seed pins
were corrected atd19f37e without changing firmware bytes; failed receipt retained,
all five required checks and corrected-source installed preflight passed. One
observation-only watcher durably armed/helper0; no automatic return/reboot. Owner
Reboot/System +≥5min observation/desk report pending. Originals not currently
restored. No rewrite/rearm or historical approval reuse.

## Latest selection — known-stack recorder calibration

Owner selected the known-boot capture control after the complete modern draft
produced no attributable output. The exact control package preserves the original
header/kernel/appended DTs/ramdisk and adds the existing loader recorder only in
unused padding plus a fresh mailbox. Separate install/observe/manual-return/collect/
assess/rollback tools and the [complete review](KNOWN-BOOT-CAPTURE-CONTROL-REVIEW.md)
are prepared. Actual read-only lab preflight passed full original boot/recovery,
normal/return bootstrap/header/GPT/aliases. Original images/TWRP remain; no write,
arm, helper or physical trial. Exact approval and current availability are the
remaining physical gate. This selection supersedes older no-control selections
below for this exact calibration only; trial8 and the failed modern draft stay held.
No loader result qualifies kernel entry, modern USB or kernel-side retention.


Actual first-draft test1 is complete. Original full boot restored once and full
boot/recovery/RAM cleanup verified; TWRP left running, no reboot, no process armed
and no owner action pending. USB capture0B/no matching endpoint; returned image
unchanged from candidate, only HOSTCONTROLseq1/73B, no kernel record. Logo/black
loop does not prove kernel entry/reset cause. One original FACTORYM helper exit0
after a host-only receipt-permission failure stopped the first waiter before any
helper launch; guarded return-only continuation corrected mode600. Evidence
archives match lab/controller. Approval consumed; no repeat/new trial selected.
See [actual result](../../evidence/independent-recovery/first-draft-trial-result.json).

Completed first kernel draft: **6.18.34-valethon-draft1+**. Combined build
42091153900 succeeded at dfdd080; enforcing VM and independent final package
checks passed. The complete16MiB boot image and private delivery archive are in
out/valethon-first-draft-1. The source receipt is
[evidence/independent-recovery/first-kernel-draft-result.json](../../evidence/independent-recovery/first-kernel-draft-result.json).
USB streaming and retained boot-tail logs are included; no automatic-recovery
engineering was added. No tablet boot/logging acceptance, installation or trial
is claimed. The next test must prioritize capture/retrieval before restoration.
This completed draft supersedes older no-build/minimal-control selections below.

Latest owner direction: finish the complete first kernel draft and prioritize
test results/retrievable logs over automatic recovery engineering. A combined
first-draft build is selected: existing board ports, enforcing PID1, USB streaming
and retained kernel logs. Existing rollback stays available; no new recovery
automation, physical trial, install or reboot is selected. Positive hardware
logging remains unconfirmed. This supersedes older “no build selected” text below.

Latest owner requirement: next tablet test uses a complete best-supported kernel
candidate with logging positively confirmed beforehand. No separate partial
diagnostic-kernel/observer test is selected. Qualification is still absent;
see the latest constraint in [the plan](LOADER-UNBLOCK-PLAN.md).

Testing-process correction: physical candidate writes and arming are held until a
reviewed known-kernel control qualifies the actual logging path. No custom kernel
boot or kernel log is confirmed. Read-only collection and original rollback remain
available. See [measurement repair plan](LOADER-UNBLOCK-PLAN.md).

Current346: actual trial7 complete, originals verified/TWRP and unarmed. Only
HOSTCONTROLseq1/85B retained; no exact kernel entry/handoff or kernel record. TWRP
repair restored normal bootstrap; approved fullp5 restoration/readbacks verified.
Host collector read-size failure remains unexplained. No owner action pending.

Current decision: hold custom-observer trial8 unarmed after owner research request.
Primary Douglas port evidence reports boot/display/touch/USB networking on vendor
3.18. Our known-normal backup is ARM64. Correction: exact diagnostic DT enables
USB0/peripheral and its port0 PHY; only USB1/port1 is disabled. Missing USB remains
unattributed. Next: offline ABI/compatible-enforcing-policy
profile for a minimal logging control on the already-booted matched kernel/DT and
existing USB driver. No old OS installation, stock-DT graft into mainline, policy
bypass, build, device access or new physical trial is selected. Trial8 artifacts
remain retained. See [revised plan](LOADER-UNBLOCK-PLAN.md).

Owner priority correction,29 October2026. Read the
[ordered roadmap](ORDERED-ROADMAP.md), [stable task/dependency contract](ordered-roadmap.json)
and [Project4](https://github.com/users/TOVSWORLD/projects/4) before selecting work.
The board is the source of live state. Do not resume historical peripheral queues.

## Current selection

- Administrative task#438/PR448 is complete; ordered board readback passed.
- Existing-work exception#440/PR436 is source-accepted after six exact-head checks
  at8ff8731 and actual PWM object/config/final Image run40881461603. No new PWM
  binding/peripheral scope follows. The source receipt is in
  evidence/pwm-kernel-integration/build-result.json; hardware remains unqualified.
- **Decision#439 is complete:** owner approved the reviewed persistent software
  unlock and destructive lab-host/device work on29 October, with immediate
  reporting of breakage or unexpected state. Do not ask that approval again.
- **Execution#347/PR452 has reached actual TWRP3.3.1-0.** Original full BootROM
  stage and original fastboot recovery stage both exited0. Post-full fastboot
  identified Douglas; recovery_x capacity was corroborated against decoded GPT.
  ADB reports recovery/douglas/TWRP3.3.1-0, kernel3.18.19; recovery and kernel logs
  were retrieved. [Runtime receipt](../../evidence/approved-lab-entry/runtime-result.json).
  The case stayed closed and no short was applied. [Entry acceptance review](ENTRY-ACCEPTANCE.md) accepts the selected route and
  observed interim Android endpoint; independent failed-load stock return#346 and retained
  failure logs#348 remain separate unpassed gates. No maintained-kernel or
  app-QA boot is claimed; Android11 runtime is recorded separately below. Host sudo and temporary USB/service setup
  are complete; do not resurrect those resolved blockers or repeat approval.
- **Android11 ROM and ARM Google services are now installed**, with actual
  updater RC0 and recovery-menu return for both. Read-only system inspection
  confirms API30/ARMv7. First Android boot and initial setup are now
  confirmed by owner home-screen observation and authorized ADB boot_completed=1.
  Android runtime reports encryption unsupported and SELinux Permissive; owner
  reports device-policy enrollment failure. No policy/security bypass was applied.
  App/provider QA remains unmeasured. The GApps installer has a tested local ABI
  compatibility correction; unchanged app payloads and exact receipts are in
  [qa-install-result.json](../../evidence/approved-lab-entry/qa-install-result.json).
  [Runtime receipt](../../evidence/approved-lab-entry/android-runtime-result.json)
  records installed package/browser/security facts. Google Play services20.45 and
  no Chrome are current prerequisites to resolve before passkey/browser acceptance.
  Do not repeat unlock, wipes, installations or first-boot request.
- **Owner correction,30 October: platform release before app QA.** Do not select,
  build or install Connect/passkey QA candidates on the interim ROM. First deliver
  the stable, supported, updated project OS. #333 owns explicit upstream/version/
  security/update-path selection, reproducible integration, stability and branding;
  #354 retains attribution/distribution review; #340 packages the branded release;
  #341 admits feature QA only afterward. The current LineageOS18.1 baseline is not
  that final release. Branding covers boot/setup/wallpaper/launcher/About, with
  truthful Android/security-patch fields and upstream notices. No parallel branding
  task or unrelated peripheral off-ramp is opened. Current #347 entry milestone is accepted;
  phase344 now has observed Android-independent TWRP entry under reopened#346.
  First normal diagnostic trial produced no kernel logs/diagnostic USB identity.
  Existing recovery returned and the full original boot image was restored/verified;
  owner confirms TWRP. No maintained-kernel entry is inferred. Generic enforcing
  VM tests reproduced and corrected ARM64 open flags, device/configfs labels and
  PID1/kernel-thread domain handling. A second normal trial also produced no logs; original boot was again restored.
  The inherited-watchdog handoff correction now has a successful retained kernel
  build and enforcing VM run. Candidate3 was tested once and also produced no logs/diagnostic endpoint.
  Its pending manual return step was completed separately without another boot
  trial; original boot was restored/verified and owner confirms TWRP. Nothing is
  armed under draft PR453; watchdog hardware handoff remains unobserved. Ordinary return
  remains complete; intended failed-load and348 retention remain unqualified.
  #345 is closed not planned because no inspection was needed.

The completed admission decision identified one operational route or state why none is safely
available, the minimum diagnostic package and entry/memory/CPU/transport contract,
pretrial recovery/log/power/thermal provisions, stop criteria and one concrete
reviewable next action/owner decision. Do not repeat stock/cable/photo captures,
LK microtraces or synthetic readiness wrappers. A closed NO-GO does not admit entry.

## Required sequence

1. #439 decision → explicit GO → #347 bounded entry/trial → #346 independent
   failed-load stock return → #348 useful retained diagnostic logs.
2. #22 diagnostic memory/UART/internal storage → #18 clocks/reset → #19 pinctrl/EINT
   → #20 PMIC/domains.
3. #329 display/backlight → #330 touch → #331 GPU/composition → #333 Android candidate.
4. #334 Wi-Fi → #442 audio → #335 charging/thermal → #443 suspend/wake → #336 USB
   → #444 SD → #446 video → #441 Bluetooth → #445 sensors → #447 cameras.
5. #27 final DT/dependency validation → #353/#354 licensing/distribution → #340 exact
   beta/recovery handoff → #341 actual QA admission review.

Issue#345 is closed not planned; its conditional inspection branch was not selected.
Normal recovery/current-kernel log capture is complete. Task#348 names only the
remaining failed-boot retention/retrieval qualification. Issue#346 is reopened for remaining failed-load qualification;
ordinary return alone is not failed-load evidence, which remains explicit
in phase344/release acceptance. Historical phase#106 has100 sub-issues; preserve its source evidence and
open runtime exit, but put operational work under#344. Do not create more source
micro-scopes there or mistake completed child counts for recovery qualification.

## Execution contract

One primary Task issue per PR; one implementation task Active at a time. Use an
issue-numbered branch and Updates #N; Fixes #N only after actual acceptance. Every
required check must pass at the exact head before merge to development; main only
through releases. Source/build completion is distinct from device qualification.

Follow the recorded predecessor gate. If blocked, record the condition and work
only inside that issue or on a documented necessary prerequisite inserted ahead
of it. Update order/dependencies before coding. Never bounce to an unrelated
peripheral. Owner-approved scope exclusions remain explicit and do not become
hardware passes. Parent rollups do not themselves authorize forward execution.

Synchronize/read back Status=Delivery state, labels, native parent, execution order,
dependency, acceptance gate, primary PR, latest result, next action and blocker at
selection, PR changes, merge and acceptance. Preserve completed scopes in the
unfiltered default view. No continuous background-agent claims or rough-percentage
updates; report measured entry/boot/log/return milestones.

Standing low-risk read-only lab authorization remains valid. High-brick-risk
unlock/downgrade/bootloader/security writes/electrical actions require explicit
approval of a concrete reviewed procedure. Do not weaken SELinux/security for logs.
No large/paid resource without the existing gate. Raw logs/selectors/identifiers
stay private in ignored out/; publish sanitized exact revision/artifact receipts.

## Actual qualification boundary

Stock recovery entry/ordinary return and a capped320KiB Android USB export are
observed. Experimental loading, independent failed-return, retained first-kernel
logs and the14 hardware groups on the new kernel remain unqualified. Current full
DT contexts30/24 still fail; DSI/PHY source nodes stay disabled and PWM source status
is okay, unchanged. All seven PID1/host-serial admission gates remain denied.
Source/build successes are real groundwork, not first-boot or beta admission.

The previous detailed source queue is retained as
[historical evidence](history/ACTIVE-WORK-QUEUE-2026-10-29-pre-roadmap.md), not a list
of next actions. Old pre-CI sentences there are historical. The ordered live board
and current entry decision take precedence.
