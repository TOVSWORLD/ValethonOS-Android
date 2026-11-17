# Combined maintained-kernel trial

Prepared November 17, 2026 under #346; evidence/capture tracked in #348 and
phase outcome in #344. This supersedes UART-first as the immediate execution
plan. Hardware/source reference: [Douglas contract](DOUGLAS-HARDWARE-CONTRACT.md).
No new tablet attempt has run during preparation. Linux on Douglas remains unproven.

## Concrete change

One full ACK 6.18.34 diagnostic Image contains five startup detours: actual
primary_entry, before MMU, after MMU, virtual entry and start_kernel (after its
PACIASP). Each replays the displaced instruction and branches back. The BL
replay restores the original LR; the ADRP replay adjusts its PC-relative target.
Only five instructions and proven-zero executable init-text padding change.
x0–x8, x18 (shadow stack), x19–x30 survive the common marker writer. The image
extent, drivers and kernel configuration are unchanged. This is an instrumented
Image, not a claim that the original Image is byte-identical.

The metadata entry arms/readbacks the existing 31-second reset-only deadline,
then checks SHA-256 of the **entire padded relocated Image extent** (28,049,408
bytes). A mismatch emits image_corrupt and requests reset without entering Linux.
A match emits image_verified before the old handoff-only marker and ARM64 entry.
The deadline is refreshed immediately before entering Linux. Timeout behavior
on every possible hardware failure is not guaranteed by software validation.

Before the MMU transition, the hook adds a Normal-NC identity mapping of the
existing 64KiB retained console at0x444bf000. It discovers the MAIR slot and checks
the kernel idmap root/table bounds, geometry and empty destination descriptor.
An unexpected map emits map_refused and requests reset. The new L3 table and
SHA stack are reserved with metadata in0x42000000–0x42028000. This adds a memory
mapping; it does not enable a new physical logger or require UART hardware.

## Comparison with the older working kernel

The live working DT uses legacy `arm,psci` SMC methods with explicit IDs
0x84000001–04. The earlier ACK target copied those methods but retained a disabled
PSCI status; the combined candidate makes it explicitly available. Whether that
status caused any failure is unproven (lookup code may ignore it).

The working DT itself declares an old512MiB memory range overlapping its actual
bootloader-provided ranges. The old target concatenated those declarations.
The combined target normalizes overlaps and preserves adjacency and the exact
source RAM union:0x40000000–0x80000000 and0x80000000–0x99600000. It invents no RAM.
This is a contract correction, not an established diagnosis of the old failure.
GIC MMIO/IRQ and architectural timer IRQ data matched the source comparison.
Firmware reservations, USB0 and source boot-state checks remain required.
All target MMC controllers, target watchdog driver and disk-logger opt-in stay
disabled. The target uses one CPU and the existing enforcing RAM PID1 policy.

## Completed offline qualification

See [qualification receipt](../../evidence/independent-recovery/ack-combined-qualification.json)
and [VM off](../../evidence/independent-recovery/ack-combined-vm-off.json)/
[VM on](../../evidence/independent-recovery/ack-combined-vm-on.json).

The exact instrumented Image boots in generic Cortex-A53 QEMU with virtualization
off and on. All five kernel checkpoints appear in order and the enforcing PID1
filesystem/configfs probe passes. Real MMU transitions execute in QEMU. Those
VMs omit the metadata integrity stub and do not test Douglas USB; the actual
full padded Image is separately executed through that stub in instruction
emulation. Corruption in the first page and final padding byte must reset before
Linux. Ring wrap/invalid headers, deadline readback failure, kernel argument/SCS/
callee-save/LR preservation and invalid idmap-root refusal have separate controls.

Two harness faults were resolved without touching the tablet: padded QEMU DTs
were expanded beyond ARM64's FDT size limit, and asynchronous HMP capture could
miss the retained file. The harness now compacts FDT capacity and uses acknowledged
QMP stop/pmemsave commands. Those failed VM runs are not tablet failures.

## One hardware attempt and discriminating outcomes

1. Confirm the owner is present. Use a fresh authorization for
   `ack-linux-combined-two-stage-2`; never reuse the consumed previous trial.
2. One protected source boot. Restore/read back original boot before the RAM
   experiment; never write recovery. Read fresh source FDT/iomem and recheck bounds.
3. Reproduce the prequalified Image using its unspent reference token; a different
   Image hash aborts. Rebuild the fresh DT/metadata and load-only client, verify
   every segment, then perform at most one load and one jump.
4. Capture within the existing bounded window. After jump, use read-only return
   queries until a different boot ID reaches completed Android. No reboot/root/
   unload commands into a hung or partly shut-down device; no automatic retry.
5. After a fresh completed return, collect retained records once and verify
   original boot/config, unchanged recovery and normal ADB. If the tablet does
   not return, owner-assisted Power recovery may be necessary.

A fresh image_verified establishes the checked destination bytes, not Linux.
A complete unique ordered chain through start_kernel establishes Linux C entry,
not controlled userspace or USB. The enforcing PID1 wire witness is still the
userspace acceptance gate. Missing markers are inconclusive because later
ramoops writes can overwrite the ring. A corrupt/refused marker or duplicate/
out-of-order chain cannot pass. A successful return alone is insufficient.

Update the same issues, runtime receipt, memory and queue after the attempt.
