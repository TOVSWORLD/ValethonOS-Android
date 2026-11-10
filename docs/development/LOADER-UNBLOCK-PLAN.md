# Loader retained-checkpoint delivery plan

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


## Independent arrival and first-rejection witness — offline implementation

Control2 did not establish that the patched observer was reached. Its loader-side
errors were also collapsed or silent. A further mailbox-only control would leave
that ambiguity intact. The next source work is a separate visible witness, without
changing the mailbox reader/format or pretending that it is a retained kernel log.

Implemented `bootstrap-witness.c` and the explicitly analysis-only
`--pre-shutdown --screen-witness` builder profile. It fits1547B in the already
proved1587B console spans. The original resident read hook is preserved, with no
new read observer. An arrival call replaces the dead-output printf at4bcff386,
after original read-hook installation and before original cache clean/app. The
late hook remains4bd3e3e8; registers/SP/APSR and the original literal load replay.
It keeps the incoming IRQ-mask decision, no interrupt-enable change, no failed-I/O
retry, unchanged storage limits and exact blob SHA check.

The fixed `VREC phase value CPSR` line distinguishes:

- 1: resident reached the point before original cache clean/app; value is mode.
- 2: pre-shutdown observer entered; value is checkpoint kind.
- 3/4/5: non-normal mode / incoming IRQ mask / invalid device global.
- 6: bridge result; -4 allocation, -6 blob read, -7 hash, -8 cache publication.
- 7: recorder result. New negative frontend codes distinguish device(-102),
  block layout(-103), redirect(-104), handoff arguments(-105), identity(-106),
  timed start(-107), first MODE commit(-108), not-ready(-109), device change(-110).
  These only replace generic negative returns; no extra I/O/relaxed guard/retry.
- 8: attempt already consumed; value is the loaded flag. No new initialization.

The new local execution checks run exact resident startup and the actual archived
LK video_printf variadic formatter. Only the final display sink is modeled; this
proves formatted arguments and distinct outcomes, not visible tablet pixels.
Positive composition still reaches modeled MODE/pre_shutdown sequence3; no claim
of actual kernel entry, durable logging or historical failure cause follows.

A concrete remaining dependency is the display sink itself. The archived sink
4bd44b08 calls display update4bd2266c, which can reach a timer wait through25f8c /
25eb8; the counter-based loop has no independent iteration cap. Hardware/display
initialization, maximum stack, IRQ effects and visibility are not yet qualified.
Do not export/boot this diagnostic merely because the formatter replay passes.
Both physical packers explicitly reject this profile. No candidate packaged,
new physical trial selected, device accessed or previous approval reused.

Next action: close that independent display-path contract or use a proven existing
capture channel before completing a changed physical review. If display evidence
is selected, an exact captured phase/value is required; approximate remembered text
cannot qualify the writer. A phase1-only observation would narrow reachability,
not prove why the later hook was absent. Kernel testing remains held until an
attributable target record is retrieved. Originals remain verified/TWRP/unarmed.


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


## Recorder repair action plan — source implementation complete

1. Use actual control1 evidence to keep boot success separate from recorder failure.
2. Implement valid cache-off completion without switching cache mode; retain checked
   cache-on flush, identity, timeout/error and no-retry guards. Done in source.
3. Move the final durable snapshot before the archived IRQ-mask/later shutdown path,
   name it pre_shutdown, and permit one safe late initialization only when earlier
   hooks performed no I/O. Done in source; no interrupt re-enable or failed-I/O retry.
4. Compile/link only in proven owned spans; replay exact instructions/arguments and
   fresh package; generate all guard hashes from the manifest. Done locally.
5. Synchronize PR/board, pass five exact-head checks, then obtain approval and current
   availability for the complete [changed review](KNOWN-BOOT-PRE-SHUTDOWN-REVIEW.md).
   No new physical work or kernel build is authorized by source/model results.

The old control's exact reason for producing no MODE/READ record remains unproved.
The IRQ-mask ordering explains why its final site was unsuitable on that path; it
is not proof that this was the only runtime failure. Kernel logging remains held.

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

## Capture repair selected after actual full-draft failure

The host collector succeeded in reading recovery/boot/seed/slots; the target
produced no new record. USB capture did not select/open a matching endpoint.
Both target producers are late: USB requires PID1/policy/configfs/UDC; boot-tail
requires eMMC and late init. Their silence cannot locate an earlier failure.

Implemented the first host repair: observe_selected_usb.py records connect/
disconnect, numeric descriptor IDs, interface classes, bound driver and ACM node
names for only the selected physical port. It never opens a TTY, reads serial
strings, changes udev/USB configuration or issues target commands. Future capture
runs record this private metadata alongside the wire capture, including unexpected
identities instead of silently filtering them out. Three native controls pass.
A new read-only control on already-running recovery saw two stable cached snapshots
and two usbfs interfaces. This qualifies the observer/current port mapping only,
not custom PID1, USB ACM, kernel entry or retained writes. No flash/reboot occurred.

Owner selected preparation of this calibration with “Do it”. Offline control 1 now
preserves all 7,796,736 declared original boot bytes exactly, adds the existing
9,216-byte recorder at verified-zero 12 MiB padding, and binds a fresh loader-only
nonce/prefix/mailbox seed. No original kernel, appended DT, ramdisk or header was
rebuilt. Physical deployment is not admitted by packaging. Exact packed ARM replay passed seven controls, and a separate replay preserved
the original 0x40080000 entry / 0x48000000 DT arguments. All 15 module objects
passed relative-reference checks. The [complete install/collection/restore review](KNOWN-BOOT-CAPTURE-CONTROL-REVIEW.md)
and separate exact operation tools are now prepared; these modeled controls do not
qualify physical logging. Actual read-only lab preflight passed original p5/p6,
bootstrap ranges/headers, aliases and GPT. No device write or arm occurred.

Next prerequisite is end-to-end recorder calibration on a known-working boot
stack. Existing original kernel/DT and the prepared loader-checkpoint implementation
are candidates for offline review; no new control boot is admitted here. Do not
put the modern ramdisk/policy onto the vendor kernel without matching its ABI.
A known-good boot that still produces no checkpoint diagnoses the recorder, rather
than being misreported as a modern-kernel failure. This calibration may require a
separately reviewed control boot, an explicit change to the prior no-control-trial
constraint, and fresh owner approval/availability. No current approval is reusable.

After that control, preserve the complete first draft and use attributable stages:
image read/decompression, pre-handoff arguments, kernel entry, early init, driver
init and PID1. The existing loader record covers pre-handoff, not execution after
SMC. A kernel-side entry marker needs demonstrably owned storage and a retrieval
path that survives the actual return sequence. Ramoops needs reserved persistent
RAM; the existing legacy ram-console reservation is not automatically a compatible
or retained backend. Do not guess RAM addresses or assume Power40 preserves data.

No new kernel build or physical control execution. The separate known-stack
control package is selected for review; older no-control constraints below are
historical for this explicit owner-selected calibration only.
Actual first-draft results remain unchanged and original boot/recovery stay restored.
Primary references: https://docs.kernel.org/arch/arm64/booting.html and
https://docs.kernel.org/admin-guide/ramoops.html. The original Douglas vendor-port
boot/USB report is https://gitlab.com/postmarketOS/pmaports/-/merge_requests/1304 .

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

Owner direction: finish one usable candidate; component test counts are not delivery.
Current device baseline is trial7 complete, original bootstrap/full boot/recovery
verified, TWRP unarmed. No physical step is authorized by this source plan.

## Latest owner constraint — complete candidate and positive logging

The next owner-assisted tablet test must use a complete best-supported kernel
candidate with logging positively confirmed beforehand. Do not schedule a separate
partial diagnostic-kernel or observer trial. Trial8 remains held.

Qualify as much of the collection path as possible using existing retained evidence
and the already-running known recovery, subject to the existing read-only scope.
Recovery logs can qualify only the exact recovery collection transport; they cannot
qualify the custom PID1 USB producer or retained-mailbox writer. Do not borrow that
qualification across backends. A new control boot is not selected by this plan.
If the intended candidate logging path cannot be positively demonstrated without a
separate physical boot, record that concrete dependency before proposing a test;
do not silently substitute a source/model check or another blind trial.

Prepare the complete candidate offline: coherent kernel/config/matched DT, enforcing
ramdisk/policy, enabled compatible logging transport, exact manifests and guarded
rollback. Only a complete changed review satisfying the logging prerequisite may
advance to fresh exact approval and availability. Current logging remains
unqualified; this owner constraint does not clear the code hold.


1. Integrate one runtime frontend. Discover the current device/card binding without
   lazy initialization; initialize once from an immutable descriptor; dispatch mode,
   redirected read and final handoff records on the private module stack.
2. Resolve resident placement. Redirect console formatting to a return-only sink;
   reclaim only console code/data demonstrated unreachable by static references and
   the original mode/read matrix. Preserve globals, GPT/flag/string helpers and the
   recovery path. Link bridge, hash/cache bindings, descriptor and hook replay there.
3. Validate the complete linked path. Exercise load/hash/cache publication, actual
   selected-field reads, writer initialization, checkpoint emission, register/flag/SP
   replay and failure stops. Explicitly identify modeled hardware and existing raw
   data-driver termination risk; never promote those to hardware acceptance.
4. Package one fresh candidate and observer, with independent manifest/prefix/seed
   checks. Prepare guarded install, one-arm collection and current-hash-bound rollback
   for both supervisor/manual outcomes. Preserve TWRP bootstrap repair.
5. Synchronize PR453/346/344, pass five distinct exact-head checks, and present the
   complete changed review. Only then request exact physical approval/availability.

Exit: a complete concrete candidate/recovery review, or an evidenced blocker that
cannot be resolved by authorized local source work. No unchanged trial/build loops.

## Execution outcome

Steps1–4 are implemented in the complete runtime frontend, console-owned bootstrap,
full-path validator and exact fresh-nonce candidate/private command package. The
trial review records residual hardware risks rather than treating model assumptions
as qualification. Step5 records final PR/check synchronization, then owner review and
availability under the standing physical-trial rule. No tablet action has occurred.

## Owner redirection — use a demonstrated baseline before another custom trial

Trial8 is held, unarmed, after the owner requested research into known/proven routes.
The original [Douglas port report](https://gitlab.com/postmarketOS/pmaports/-/merge_requests/1304)
explicitly reports boot/display/touch/USB networking with Amazon's vendor kernel.
The [Douglas device recipe](https://github.com/hexdump0815/pmaports-amazon/blob/main/device-amazon-douglas/deviceinfo)
uses ARM64 and the established v0/2048-byte boot-image layout. This supports a
vendor-stack positive control, not a claim of working modern mainline support.

Read-only comparison of our actual backup confirms an ARM64 kernel and text_offset
0x80000. The current mainline Image has text_offset0; its entry must follow its own
header, not copied legacy constants. Correction: the exact diagnostic DT enables USB0 at11200000 in peripheral mode,
with the referenced port0 PHY available under the enabled T-PHY. USB1 at11270000
and port1 are disabled. The earlier claim that diagnostic USB was disabled checked
the wrong instance. Missing USB remains unattributed; this is not runtime proof.
The public vendor reference supports SELinux policy30 while our current diagnostic
policy is33: blindly combining that ramdisk with the legacy profile is invalid.
The exact policy ceiling of the separately built owned normal kernel is not yet
proved. No enforcement/security bypass or old OS installation is selected.

The next concrete work is an offline compatibility profile for a self-contained
logging control using the already-booted matched kernel/DT and existing USB driver:
1. Preserve the known image/DT/loader route and determine its userspace/policy ABI.
2. Prepare only the minimal compatible enforcing diagnostic ramdisk, reusing the
   existing host log reader. Mount no system/userdata and preserve recovery.
3. Demonstrate the control's boot packaging and source/ABI constraints before a
   complete changed physical review. Do not transplant a stock DT into mainline.
4. Establish host-captured kernel logs on that positive control; change one kernel/
   DT dependency at a time toward the maintained branded platform.

The old kernel is a temporary diagnostic reference. It does not meet the final
supported/updated-platform goal. Trial8 artifacts are retained as a fallback, not
selected or awaiting an approval request. No build, device access, flash, helper,
arm or reboot was performed for this research. See the sanitized
[comparison](../../evidence/independent-recovery/proven-douglas-baseline-result.json).

## Measurement repair — required before another kernel trial

No project-built kernel has a confirmed tablet boot or a verified kernel log.
HOSTCONTROL is a preinstalled fixture, not execution evidence. A loader checkpoint
cannot qualify kernel entry. Recovery return cannot establish the reset cause.

The physical candidate installer, observer installer and supervisor arm entry points
now stop before device preflight while the measurement path is unqualified. There
is no command-line override or receipt boolean that clears this hold. Read-only
collection and the existing original restoration paths remain usable. Trial8 stays
held. This is a stop against blind trials, not a completed positive control.

Follow this sequence; each step has an observable exit:

1. Finish the offline compatibility profile for the already-booted matched kernel/DT
   and minimal enforcing diagnostic ramdisk. Establish the exact policy ABI and USB
   driver requirements. Do not build another custom kernel to calibrate the test.
2. Prepare a separate complete control review: exact component hashes, boot layout,
   fresh nonce, actual host collector, one-trip instructions and guarded rollback.
   Replace this unconditional hold only with a narrowly scoped control admission
   validator in that review. Fresh exact approval and availability are required.
3. Historical proposal only, superseded by the latest owner constraint above: a
   separate known-kernel control boot is not selected. Any eventual qualification
   must exercise the actual physical collection path.
   Accept only fresh nonce-bound raw kernel output, with a kernel boot record
   matching the selected kernel release. Verify wire framing, sequence, terminal
   completion and raw digest independently. Empty output, host fixtures, loader
   records, approximate screen recall and modeled execution all fail qualification.
4. Bind the accepted qualification to the collector/producer versions and transport.
   Admit a new kernel only with its observation transport enabled and compatible.
   USB qualification cannot qualify the retained-mailbox backend. A silent trial is
   an unobserved measurement and stops kernel iteration; it is not a kernel failure
   diagnosis. USB output still cannot prove execution before USB initialization.

Failed partition-size validation now preserves the existing response privately,
with expected/received lengths and its digest, without retrying or trimming it into
an accepted image. Retention is capped at32MiB. Failed output has no valid report or
rollback image. This improves future diagnosis; discarded historical responses
cannot be reconstructed and their causes remain unknown.

## Offline capture acceptance implementation

`scripts/assess_kernel_log_capture.py` independently replays an existing private
VLOG0002 raw capture through the original bounded receiver. It requires exact fresh
nonce, frame ordering, terminal completion, receipt counts/digest and a kernel
facility0 Linux-version record matching the expected release. It rejects host or
loader text, userspace banners, empty/truncated/trailing captures and stale nonce.
It opens no device and exports no raw banner. Even a valid synthetic capture returns
physical_origin_verified=false, device_qualified=false and test_admission=false.
The physical hold is unchanged. Five synthetic regression controls passed.

Concrete unresolved dependency: neither custom USB PID1 nor retained-mailbox writer
has actual hardware output in the archived trials. Offline validation can reject
bad evidence but cannot manufacture positive logging. Recovery ADB logs use a
different producer/transport and cannot close this dependency. No separate control
boot or new physical procedure is selected. The complete next candidate cannot be
presented as meeting the owner's positive-logging prerequisite until attributable
hardware evidence for its chosen path exists.

Collection diagnostics also retain existing ADB stdout/stderr for nonzero exits
and timeouts, privately and without another command. Public error strings exclude
command/selector/output text. Retention is capped at32MiB stdout and64KiB stderr;
full byte counts/digests and exit/timeout classification survive. These failed
captures never produce a valid readout or authorize restoration from partial data.
This source change is not deployed to the lab and establishes no physical logging.
