# FireTabs project memory

Updated November 18, 2026. This is the compact resume record, versioned with the
project. It does not claim to modify an account-wide ChatGPT memory service.
New user instructions and newer verified results supersede this snapshot.

## Objective and current reality

The objective is maintained Linux/Android on the 2017 Fire HD 8, douglas/KFDOWI,
ultimately a supported ValethonOS control panel. Interim Android is a working
recovery/development environment, not completion. The full ACK 6.18.34 draft
completes initialization and executes its controlled enforcing PID1 on Douglas.
**The prepared PID1's exact fresh VLOG0002+32-byte nonce was received over USB.**
This is the agreed kernel/PID1/USB-identity milestone, not a VM/stub-only pass.
Pinned PID1 emits that header only after enforcing-policy readbacks/RO remount,
labels/domain/namespace, UDC, duplex serial and kmsg-open gates. Kernel/RAM setup
and userspace execution must not be reopened as pending because record transfer
is incomplete.

Latest runtime: [USB identity milestone](../../evidence/independent-recovery/ack-usb-end-to-end-runtime-result.json).
Original Android boot/config/recovery and normal ADB verified after return.
Owner confirmed Power untouched throughout the latest attempt; automatic Android
return is established, as for the prior corrected-RAM and C-init attempts. Exact reset cause remains unqualified. One source
boot/restore and one load/jump consumed per attempt, no automatic retries.

**Read-only internal eMMC is now achieved:** the maintained kernel read the
original16MiB p5 boot partition, matched its SHA-256 and sent fresh VSTORE01
status over USB. Original Android then returned with installation checks and
normal ADB passing. [Storage runtime receipt](../../evidence/independent-recovery/ack-storage-readonly-runtime-result.json).
**Next product work:** #18 clock/reset dependencies, then #19/#20 pin/power
for display/touch/graphics and maintained Android userspace under #333/#24. Complete log-record transfer is a
non-blocking follow-up, not another proof gate.
The capture has40 bytes, zero complete records and no terminal frame. This does
not erase the fresh PID1 USB identity. The old target_pid1_proven metric bundles
release/cmdline log payloads and stays false for that stricter stream criterion.
Use the separate pid1_usb_identity_proven hardware milestone, with its recorded
physical-writer/gated-source proof basis.

Owner correction: do not get stuck on logging to prove working components.
No logging-only tablet gate or repeated kernel/PID1/USB-enumeration proof. Next
is an integrated read-only storage/status result using the existing USB path,
with a fresh package/owner presence if a hardware attempt is needed. Storage
scope6 and all prior authorizations are consumed; never replay them.


## Display functional package progress — November18,2026

Hosted full display build44253355044 passed on source90655a3. Direct GitHub
artifact ZIP digest and all manifest artifacts verified. Linked Image includes
master/gamma/mutex, TPV panel, host lane APIs, LP8557 and framebuffer console.
Receipt: evidence/display-pipeline-source/kernel-build-result.json. Earlier
packaging-only failure remains historical, not current build status.
Display-only enforcing PID1 compiled using unchanged proven policy; VDISP001
reports framebuffer metadata/banner write, never physical pixel proof. Generic
enforcing ABI/labels/configfs VM passed on the exact new unmodified Image.
Fresh final RAM bundle3 passes seven integrity/deadline/both-VM controls.
Actual display C metadata/short-write tests and controller visual-pending test
pass. Fresh unapproved display scope7 template prepared; final offline controller
validation/publishing underway before the attended visual test.
Current private inputs: out/display-kernel-1, out/display-initramfs-1,
out/display-functional-bundle-3 (current; earlier1/2 superseded). Build lab
/tmp/firetabs-display-functional-build-20261118-1/out/init-2. No tablet action,
no fresh authorization, no display hardware pass. Issues18/329 updated directly.
Next is visible VALETHON DISPLAY TEST plus labelled RGB bands and protected
Android return; no repeated storage or complete-log prerequisite.

## Active display/backlight implementation — November18,2026

Owner accepted exactly three intermediate outcomes before the major Android UI:
(1) display/backlight including needed providers, (2) touch/input, (3) Android
graphics/userspace integration. Provider substeps are internal to those outcomes,
not additional owner-facing milestones. Keep the major setup/home commitment.

MT8163 DRM master/gamma/mutex source port and TPV-only DRM panel are implemented.
Existing saved working boot DT identifies TPV/MP; no new device query needed.
Working board pinctrl proves GPIO43 power/GPIO83 reset, correcting stale110/65
comments. Working LP8557 is REGISTER_BASED at I2C0x2c, device control0x47; generic
PWM-backlight is not sufficient. The board's epprom_data property is ignored by
its eeprom_data-reading driver; do not activate the dormant ROM table writes.
The172 TPV packets/two delays match compiled original C byte-for-byte. Actual C
failure matrix covers every packet/short write, regulator errors and state cleanup.
All999 tests and Android source-evidence checks pass. No display hardware trial.

Draft PR454, branch codex/issue-18-display-foundation, is stacked on the
unchanged proven storage/native branch. First compile run44250389319 on source1b0d1b5 compiled the actual display
objects and linked Image, then failed final packaging because the size-report
writer requires a fresh filename. Fix uses display-image-size-report.json,
preserving the dependency report. Failed receipt is versioned; no artifact or
runtime pass inferred. Follow-up implements explicit MT8163 lane prepare/unprepare:
rails settle before lane exit from ULPM and reset; lane shutdown precedes power
off, with retained rail ownership on cleanup failure. These follow-up sources
need an updated full build before admission. DT preview now closes the
display/SMI/IOMMU/I2C0/panel/backlight graph, preserves RAM/no-map/reserve-map
data, uses verified I2C0 pins75/76 and panel43/83, and strips the old RAM-console
hook arguments. Explicit offline-preview marker/no executable metadata prevents
misuse as a physical candidate. New Image package/VM and attended screen test
still remain; source/DT checks are internal steps of the display outcome. Never treat the older build as
qualification of a newer head.

Full hosted kernel build uses the draft PR: existing GitHub connector has
no workflow-dispatch action and local gh is not authenticated; do not ask owner
to redo connector setup. PR-open triggers the explicit display-provider scope.
Source/issue publishing stays on the connector. Keep source-only DT-disabled
build separate from later functional RAM-test admission. Never relabel this as
achieved display or add a logging-only proof gate. See display-port/README.md.

## Read-only eMMC hardware milestone — November18,2026

[Actual receipt](../../evidence/independent-recovery/ack-storage-readonly-runtime-result.json).
One source boot/restore and one native load/jump completed. Enforcing storage
PID1 read exactly16777216 bytes from the immutable block179:5 p5 node using
O_RDONLY, checked EOF and matched the original boot SHA-256. Fresh120-byte
VSTORE01 result independently decoded; selected physical USB endpoint, stage5,
flags31, error0. No block write/ioctl or userdata mount. Original p5 was restored
and read back before jump; recovery untouched. A different completed Android
boot returned with original boot/config/recovery and normal ADB checks passing.
Storage acceptance is achieved; do not re-prove it through kernel-log transfer.
Owner confirmed Power untouched throughout; automatic original Android return
is observed. Exact reset cause remains unqualified.

Source code at d6f3c5ae67dc66d41665b0170005efc61608eae2. Private trial:
out/recovery-linux-pivot/ack-storage-readonly-trial-runtime-1. Parent/child
scope6 authorizations are consumed. No replay/retry or owner recovery needed.
The prior preparation's985 tests,14 controls,11 compiler negatives and four VM
checks passed; repository integrity still flags the unchanged empty helper at
tests/test_source_usb_shutdown.py:201. No new source change required for runtime.
Next is the documented #18/#19/#20 display/touch provider path toward #333/#24
usable maintained Android; broad hardware, writable filesystems and Android UI
remain unqualified. Reuse the working kernel/RAM/storage/PID1/USB foundation.

## Historical storage preparation — before the successful hardware test — November18,2026

[Preparation receipt](../../evidence/independent-recovery/ack-storage-readonly-preparation.json).
Dedicated enforcing storage PID1/policy and fresh VSTORE01 functional status are
built. Only internal MMC0 is enabled, at26MHz with exact existing pins/supplies,
clock parents and MediaTek sysirq. The working4.9 mt8163 and mt2701 quirks match
the maintained fallback. No speculative host-driver rewrite or new logging gate.
The fixed archive block179:5 node is0400; PID1 uses O_RDONLY, exact16MiB/EOF and
known original boot SHA verification. Policy denies block writes/ioctls/new nodes
and reads of other block types. No userdata mount or block payload over USB.
The120-byte one-way status carries fresh identity, stages/errors and a verified
expected digest; it needs no VLOG ACK or kernel-record transfer.

All11 compiler negatives pass. Both synthetic read-only storage VM modes pass:
full read/hash, bad-hash rejection, write/ioctl/other-block/mknod denial, unchanged
fixture. The exact fresh Image reaches enforcing PID1 in both target RAM-layout
VM modes, including the live2MiB exclusion. All14 entry/console/corruption/VM
controls and985 unit tests pass, no skips. Android source-evidence check passes.
Repository integrity still stops on unchanged tests/test_source_usb_shutdown.py:201
empty test helper; it is not claimed passing. No tablet command or trial ran.

The source/three ABI transfers were approved and completed. Lab compilation and
VM qualification are finished. At preparation time scope6 was unapproved/unconsumed; now consumed, as above;
prior approvals remain consumed. Next requires owner presence for one protected
source boot/restore and one RAM jump; original p5 restored/read back before jump,
recovery untouched,31-second target deadline and bounded read-only Android-return
checks. No automatic retry. Hardware storage is not yet achieved.

Private resume inputs: out/recovery-linux-pivot/ack-storage-readonly-candidate-1,
storage-built-1/out/init, ack-storage-readonly-qualification-1.json,
ack-storage-readonly-client-1, storage-qualification-artifacts-1. Isolated build
lab: /tmp/firetabs-storage-readonly-build-20261117-1. Public trial template:
evidence/independent-recovery/ack-storage-readonly-authorization-template.json.
Use --ramfix --storage-readonly in run_ack_native_trial.py, never --usb-end-to-end.
The storage mode requires its own exact scope, component verification and
functional status plus original Android return; the old log-specific metric
remains separate. Reuse no consumed scope5 wrapper. Do not run read-only device
preflight while merely checking the offline parent validate() function.

## Receiver result and offline cleanup fix

The detached worker delivered the identity, but its outcome was masked by
termios.error during post-disconnect restoration (not caught by except OSError).
The old supervisor then reported endpoint_selected false and rejected the wire
assessment. Raw40-byte evidence was independently parsed against the fresh nonce
and host digest. Preserve the original failed controller report; the sanitized
runtime receipt distinguishes identity proof from incomplete records.

Cleanup now catches termios.error, preserves the original capture outcome and
accepts a completed transfer's expected vanished-TTY restoration. Offline tests
cover incomplete/complete capture plus cleanup error, fresh header without log
records, detached-parent loss and stdout-loss recovery. No new device test ran
for this cleanup fix. Primary reason the record stream ended after identity is
still unknown; do not invent a kernel/PHY regression or claim terminal success.

[Next plan](NEXT-MILESTONE-PLAN.md), [end-to-end history](ACK-USB-END-TO-END.md).
Private latest trial: out/recovery-linux-pivot/ack-usb-end-to-end-trial-runtime-1.
Its scope5 approval and children are consumed; do not rerun the wrapper.

## C-init hardware result and live RAM correction

[Receipt](../../evidence/independent-recovery/ack-cinit-runtime-result.json),
[correction plan](ACK-LIVE-RAM-FIX.md). The single C-init attempt returned to
verified original Android; Power attestation remains in the receipt. Fresh
retained console reports stack overflow, PC show_pte+0x1d0, ESR96000006,
FARffff0000585ff008. Nested fault reporting may hide the first exception.
No PID1/USB proof. A no-map gap98400000–98600000 was missing: source live
System RAM excludes it, but target DT allowed allocations there. Under the A53
linear map the fault address implies physical985ff008 in that gap; inference,
not a directly observed physical address. Gap ownership and causality unproven.

The corrected allocator contract uses fresh iomem, not only static/live DT.
Preserve every non-System-RAM gap as no-map, keep all existing reservations,
and independently bind/recompute the source ranges. Both target-memory-geometry
VM modes now reach enforcing PID1 with the fresh corrected Image. All13 controls,
963 regression tests and bound offline policy validation pass. No additional
tablet commands ran while preparing the fix. Scope4 requires new owner presence.
Private reference ack-ramfix-candidate-1; PID1 ack-ramfix-initramfs-1; prepared
runner run-ack-ramfix-trial-1-private.py under out/recovery-linux-pivot.

## Historical preparation — C-init/PID1 candidate (now executed)

[Exact trial](ACK-CINIT-TRIAL.md), scope ack-linux-cinit-two-stage-3. Full Image
93722d1fd0d6d7f53b351fba8508bce7d1923fb21a9e92a5911a2acfc4742476.
Both VM modes reach /init with enforcing PID1 probe and retained run-init output
after init-memory cleanup. All12 offline controls and958 regression tests pass.
Permanent executable padding hosts a RAM-only early console callback; one
8250 early setup detour installs it without UART register operations. Existing
fixmap covers one reserved4KiB console page; ring4084 bytes, full fresh PID1
identity each write, bounded lengths/header checks and preserved registers/DAIF.
Target ramoops params are removed to avoid a conflicting writer. keep_bootcon,
initcall_debug/loglevel8/ignore_loglevel capture complete-kernel progress. The
previous five entry hooks/Normal-NC identity map are absent. Existing full padded
Image SHA and31-second reset deadline stay. No storage or recovery enablement.

The missing old banner did NOT bound a fault to pre-banner C code: normal printk
was not retained that early. SHADOW_CALL_STACK is disabled in the pinned config;
do not present shadow-stack failure as a diagnosis. A specific stopping C
instruction/driver remains unknown. This candidate runs the complete kernel and
fresh enforcing PID1, not an isolated logger/payload. Hardware PID1/USB is unproven.

Private reference: out/recovery-linux-pivot/ack-cinit-candidate-2; fresh userspace:
ack-cinit-initramfs-1; prepared runner: run-ack-cinit-trial-1-private.py in that
same parent. No new tablet commands ran during this preparation. Obtain owner
presence and fresh cinit authorization for one source boot/restore and one jump;
never reuse the completed combined trial's consumed approval.

## November 17 hardware milestone

Receipt: evidence/independent-recovery/ack-combined-runtime-result.json.
One protected source boot/restore, one load, one jump. Original boot restored and
read back before jump; recovery never written. Fresh marker chain was absent
before load and recovered once, unique and ordered: image_verified, linux_entry,
before_mmu, after_mmu, virtual_entry, start_kernel. No map_refused/corrupt marker.
The retained trace ends at start_kernel. This does not identify the next failing
instruction or prove full initialization. Target USB endpoint/PID1 did not appear.
The legacy controller outcome ack-boot-unproven refers to its stricter banner/
PID1 acceptance; it must not erase the independently proven Linux C milestone.
Do not repeat relocation, entry, MMU or metadata-only tests as unresolved work.
Private runtime: out/recovery-linux-pivot/ack-combined-trial-runtime-1.
Trial authorization and its source/jump children are consumed.

## November 17 combined candidate

[Concrete trial](ACK-COMBINED-TRIAL.md): complete padded-Image SHA at destination,
five markers inside actual Linux entry/MMU/start_kernel, existing enforcing PID1.
Exact instrumented Image a548bff1b6d8b67ffe1b45ed112c16c64db35fdcfc7ff592357c959758677f2e
passed both Cortex-A53 QEMU virtualization modes with all five stages in order
and enforcing PID1 probe. All11 offline qualification controls and953 regression
tests pass, with no skipped tests; Android evidence check passes. Repository
integrity still flags the unchanged empty test helper at
tests/test_source_usb_shutdown.py:201. This is VM evidence, not tablet Linux/USB acceptance.
Source-derived DT corrections enable legacy PSCI status and normalize overlapping
RAM declarations without changing their union; neither is a proven diagnosis.
New scope ack-linux-combined-two-stage-2 binds the prequalified unspent reference
Image/token, fresh PID1 and single-attempt controller. Old approvals stay consumed.
Private candidate: out/recovery-linux-pivot/ack-combined-candidate-2; PID1:
ack-combined-initramfs-1 in that same parent. Do not print nonce/raw metadata.

## Hardware knowledge base

The owner requires a complete kernel-facing hardware reference on GitHub,
derived from board documentation and older working kernels. Use
[DOUGLAS-HARDWARE-CONTRACT.md](DOUGLAS-HARDWARE-CONTRACT.md), covering20
subsystem areas, plus the allowlisted resource inventory for430 working-source
and152 ACK DT nodes. This is the starting point for implementation; do not reduce
the project back to UART alone or repeat component discovery already recorded.
Unknowns remain explicit rather than invented. Historical source matrices are
not live build/runtime status.

## Owner decisions that must survive a restart

- Use the direct GitHub connector for GitHub. Do not fall back to the browser or
  gh CLI when the connector supports the operation.
- Preserve historical attempts and failures in the existing open issues. Current
  issue/project status must describe actual work, not an abandoned plan.
- The owner wants progress toward actual Linux boot, not endless logging gates,
  repeated approvals or another tiny experiment without a decisive question.
- The owner has **no multimeter, oscilloscope, logic analyzer or UART adapter**
  (November 16 answer). Do not ask this equipment question again.
- No existing internal-board photos or PCB revision records were available
  (October 27 answer). Do not ask that historical question again.
- The owner correctly recalled that annotated Douglas board documentation was
  already found. Reuse the reference below; do not present it as new research.
- November 17 correction: do not assume missing facts require measurement or a
  technician. First trace the older working kernels, board documentation and
  electrical specifications. A failed search or inaccessible page does not prove
  that documentation does not exist. No hardware-versus-software route choice was
  made in response to the last multiple-choice question.
- Hardware planning has been acceptable, but no equipment purchase, booking,
  physical wiring or opening has been performed in the UART preparation.

## Completed experiments: do not propose them as new

1. Normal bootloader diagnostic/modern-kernel trials, early screen and delay
   markers, and retained-record experiments were already attempted. They did not
   establish maintained-kernel entry. See `entry-screen-trial-result.json`,
   `entry-delay-trial-result.json`, `first-draft-trial-result.json` and
   `known-boot-capture-control-trial-result.json` under `evidence/independent-recovery/`.
2. The diagnostic source kernel's USB console works. Native entry was observed;
   secondaries were shut down before devices with a final off-state gate.
3. A one-page target reset payload executed, left its fresh retained marker and
   returned automatically. Owner confirmed Power was untouched. This proves
   target payload execution, not full Linux startup or recovery from every hang.
4. One full ACK 6.18 RAM attempt then ran: one protected source boot/restore,
   one load, one jump. Original boot was restored before the jump; recovery was
   untouched. The metadata entry marker survived. No attributable Linux/PID1
   records or target USB endpoint appeared. Android returned without Power
   intervention and original state was verified. Exact reset cause is unproven.
   Receipt: `evidence/independent-recovery/ack-native-runtime-result.json`.
5. Offline exact-artifact audit copied all three segments correctly across 14
   indirection pages, including the 28,049,408-byte Image memory extent. The exact
   Image reached MMU-enable entry in Cortex-A53 emulation; corrupt-source and bad
   branch controls were detected. No concrete production defect was found. Actual
   hardware destination integrity, warm firmware state and MMU/later execution
   remain unqualified. Receipt: `ack-full-image-offline-audit.json` in that directory.

The consumed trial authorizations stay consumed. Do not repeat a load/jump or
replay the original BootROM/unlock/install procedure as a routine resume action.

## Board/UART references and facts

The already-found [maintainer annotated board fallback](https://xdaforums.com/posts/90488396/)
is recorded in `CURRENT-STOCK-ENTRY-RETURN.md` and
`evidence/douglas-original-route/report.json`. The saved review calls it a
hardware recovery/BootROM reference; it does not establish a UART TX/voltage map.
Its earlier image must not be relabeled a UART pinout without inspection/evidence.

The legacy 3.18 tree at `e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74` and the exact
working 4.9 tree at `72940eb733af8df948cc216cb977cd8be9cba5a9` are primary sources.
Both inspected DT definitions name UART0 at 0x11002000, 26 MHz input,
RX GPIO79 and TX GPIO80 with function1. The default GPIO state is empty; the
vendor driver has separate RX/TX set/clear states and can switch pins during
power transitions. Preserve this distinction from the modern driver's behavior. Match live DT
compatible and compiled config before attributing source behavior to the running
kernel; a vendor UART file existing in the tree is not a runtime driver pass.
The November 17 trace did resolve the implementation: the working source config
has MTK_SERIAL and MTK_SERIAL_CONSOLE=y; vendor console/baud/probe functions
are present in the linked source kernel; the archived live UART0 DT is enabled
and includes `mediatek,mtk-uart`. Physical UART output is still untested. Do not
repeat these implementation-selection checks as if they remain unresolved.
Legacy console configuration requests 921600; the vendor console setup defaults
to 115200 unless options override it. Pin input-enable/Schmitt grouping for79–82
is not proof of that group's supply voltage or an accessible PCB contact.

The previously tested ACK DT disabled UART0 and had no UART console arguments;
its needed driver is built in. A verified offline preview enables UART0/stdout/
earlycon/console only. The ACK earlycon callback sets MMIO width/stride but does
not program baud; inherited initialization matters. The archived source boot also
contains `printk.disable_uart=1`. Silence cannot establish a wiring or kernel fault.

The source contains USB-to-UART PHY-switch code, but the tested source config
has it disabled. UART alternate pins87/88 are MSDC2, whereas the board's removable
card pinctrl uses MSDC1 pins121–126. Neither is an established solderless UART route.

No exact-board TX pad or electrical level has yet been verified in this project.
This means **unresolved**, not necessarily undocumented or measurement-required.
Do not infer UART voltage from a VIO18 regulator used by another peripheral.

## Prepared artifacts and remaining task

- `scripts/capture_uart_receive_only.py`: bounded private POSIX recorder; five
  PTY controls pass. No adapter or physical UART pass. Output wires must remain
  physically disconnected in any future receive-only setup.
- `scripts/prepare_ack_uart_preview.py`: exact-hash offline DT preview;
  `loadable:false`, not a new admitted boot bundle.
- [UART preparation](UART-FIRST-CAPTURE.md): conditional procedure and source gaps.
  Its November 16 bench selection is superseded by the documentation-first plan.
- Current issues remain #344 (phase), #346 (current implementation/recovery) and
  #348 (capture evidence). Preserve history; do not create more micro-issues.

The next action is the combined software test after bound offline validation and
owner availability. Physical UART remains an optional supporting investigation;
do not make board contact/voltage resolution a gate for this candidate.
