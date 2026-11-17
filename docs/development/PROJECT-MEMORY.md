# FireTabs project memory

Updated November 17, 2026. This is the compact resume record, versioned with the
project. It does not claim to modify an account-wide ChatGPT memory service.
New user instructions and newer verified results supersede this snapshot.

## Objective and current reality

The objective is maintained Linux/Android on the 2017 Fire HD 8, douglas/KFDOWI,
ultimately a supported ValethonOS control panel. Interim Android is a working
recovery/development environment, not completion. The full ACK 6.18.34 draft
compiled and booted in a generic VM; **Linux startup on this tablet is unproven**.
Last verified tablet state: original Android boot complete, exact original boot
and config, unchanged recovery, normal unprivileged ADB. This is a November 16
observation, not a claim that hardware was checked again on November 17.

Current execution plan: [NEXT-MILESTONE-PLAN.md](NEXT-MILESTONE-PLAN.md).
The combined integrity/Linux-entry candidate and its protected single-attempt
package are offline-qualified and ready for owner-attended testing. UART is not a prerequisite. No tablet test ran
during November 17 preparation.

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
