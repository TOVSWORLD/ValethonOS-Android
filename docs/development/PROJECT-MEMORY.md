# FireTabs project memory

Updated November 17, 2026. This is the compact resume record, versioned with the
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
Latest owner Power confirmation pending; prior corrected-RAM and C-init returns
were explicitly untouched. Exact reset cause remains unqualified. One source
boot/restore and one load/jump consumed per attempt, no automatic retries.

**Next product work:** read-only internal eMMC bring-up under #22, then
maintained Android userspace/init/adbd. Complete log-record transfer is a
non-blocking follow-up, not another proof gate.
The capture has40 bytes, zero complete records and no terminal frame. This does
not erase the fresh PID1 USB identity. The old target_pid1_proven metric bundles
release/cmdline log payloads and stays false for that stricter stream criterion.
Use the separate pid1_usb_identity_proven hardware milestone, with its recorded
physical-writer/gated-source proof basis.

Owner correction: do not get stuck on logging to prove working components.
No logging-only tablet gate or repeated kernel/PID1/USB-enumeration proof. Next
is an integrated read-only storage/status result using the existing USB path,
with a fresh package/owner presence if a hardware attempt is needed. All prior authorizations remain consumed.

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
