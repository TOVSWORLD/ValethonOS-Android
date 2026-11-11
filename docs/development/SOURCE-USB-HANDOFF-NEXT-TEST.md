# Next test: source shutdown and target USB console in one trial

> Completed trial, November 10, 2026: source boot passed and original boot was
> restored on flash. A fresh USB kernel-console challenge passed before loading;
> one load verified and one jump was requested. Source capture retained 20,957
> bytes proving Android init received the exact target and entered shutdown.
> No kernel-handoff checkpoint or target USB console was observed. The source
> collector's final receipt failed; the raw bytes were separately preserved and
> hash-verified. Owner-assisted return and original boot/config/recovery were
> verified November 11; normal ADB was restored. Work is now paused at owner
> request. [Resume checkpoint](FIRETABS-RESUME-2026-11-11.md).
> [Actual runtime receipt](../../evidence/independent-recovery/source-usb-handoff-runtime-result.json).
> This trial's approval is consumed. The preparation and procedure below are history.

November 10, 2026. Prepared; not executed. The previous target-only USB trial
loaded once and requested one jump. The source USB disappeared; no target USB
endpoint appeared in five minutes. The owner recovered from a black screen by
holding Power, and confirms Android home. Original boot/config, recovery and
normal ADB were verified. See the [actual result](../../evidence/independent-recovery/usb-console-jump-runtime-result.json).

## Audit findings and selected change

The exact linked source route is Android init → the namespaced reboot dispatcher
→ kernel_kexec → kernel_restart_prepare/device_shutdown → machine_shutdown
(disable_nonboot_cpus) → the final hardware CPU-off gate → cache preparation,
conditional exception-level transition and relocation → the entry trampoline.
The six trampoline instructions supply the DT physical address in x0, clear
x1–x3 and branch to the Image. The previous bundle checks its complete Image
memory extent, segment ownership and DT reservations, including pstore.
These source checks have not established where the hardware stopped or proved
DMA shutdown sufficient. No CPU, cache, MMU, exception-level or relocation fix
is justified by the missing USB endpoint alone.

The linked config accepts the bootloader DT command line, rather than forcing
CONFIG_CMDLINE. The vendor controller pullup sets USB readiness and can start
the controller; the serial console attaches through gserial_alloc_line and
gserial_connect. No mandatory userspace readiness gate was found in that path.
This is source analysis, not proof that target USB initialization ran.

The previous source boot did not request ttyGS0 as a kernel console. It kept
Android ADB and listened only for the target's different USB identity. The next
source package adds only `console=ttyGS0 ` before the original boot-header
command line. It uses the **same built Image and configuration** as the previous
successful source boot. Appended board DTs, original ramdisk, addresses and
original argument suffix are retained. Legacy g_serial binding remains disabled
on the source. Android continues to own its normal configfs gadget.

Before loading, temporarily add the existing ACM port to the source's ADB USB
configuration. The host opens the exact source ACM endpoint, and the controller
writes a fresh priority-zero kernel marker to /dev/kmsg. Only a matching marker
received through the kernel's USB console admits the load. The helper does not
copy that marker to the tty. Thus an unproven source console means **no load and
no jump**, rather than another blind attempt.

## One new approval covers the bounded sequence

The old trial approval is consumed. This is a different source boot candidate
and runner. Use the [new policy](../../evidence/independent-recovery/source-usb-two-stage-authorization-template.json)
and [driver](../../scripts/run_source_usb_trial.py), with the owner available for
possible physical return. The default driver path performs only source-package
read-only preflight; it does not switch USB, load, write boot or reboot.

1. Temporarily install the exact source candidate once and request one ordinary
   boot. Verify the expected kernel and **restore/read back the original boot
   on flash before proceeding**. Verify recovery unchanged. Stop on a failed
   source stage using the existing bounded rollback path.
2. Collect fresh source DT/RAM data. Generate a fresh target nonce and exact
   load-only client. The target uses the same Image and reviewed layout. Strip
   only the controlled leading source console argument before forming the
   target prefix; preserve the original suffix and all other DT properties
   except the existing two chosen-property changes. Never load an offline preview.
3. Arm and prove source kernel-console capture before any load. A temporary ACM
   helper retains the proven restoration code. Without handoff intent it
   restores ADB-only after its fixed 180-second deadline. Before the jump, it
   must acknowledge that it will make no further configfs writes. No tty-frame
   forwarding, descriptor change, host ACL/group change or persistent USB setup
   is included.
4. Keep source capture running, arm the existing target receiver, load once,
   verify loaded state and original boot/recovery again, acknowledge handoff
   intent, then issue one orderly jump. Preserve both captures privately with
   verified hashes. No automatic jump/reboot retry or post-request tablet command.
5. If needed, return physically: unplug USB, hold only Power for 40 seconds,
   release, wait 5 seconds and reconnect the same cable/port. Original boot is
   already on flash. Verify Android/original boot/config/recovery and normal ADB.

The parent approval binds the source candidate, fixed Image/config, helper,
capture report and code hashes. It permits the fresh source-dependent target
manifest/client hashes as child fields, not a different Image or different
procedure. Each execution authorization is single-use. A source-proof or
pre-jump failure aborts and unloads an attempted load; uncertain cleanup is
reported rather than retried. If USB ownership is uncertain after intent,
physical return may still be needed even if no jump was issued.

## What the evidence can distinguish

Positive, fresh source messages can establish entry into the kernel reboot
route and, if received, progression beyond device shutdown. Source capture
ends when USB disconnects. The vendor controller's shutdown callback normally
stops USB before CPU-off and relocation; a missing later source marker cannot
locate a hang or prove that a phase was not reached. No promise of console
coverage after USB teardown is made. Buffered old messages before the fresh
challenge are excluded from phase classification.

Target entry still requires the fresh target nonce on its own USB console.
Source-console success alone is not a successful handoff. If the target remains
absent, the last positively observed source phase guides a smaller follow-up;
do not infer a particular failed phase from silence or repeat this test unchanged.
This combined experiment does not repeat the live userspace logging baseline
or make watchdog/retention qualification a prerequisite.

[Package, audit source hashes and validation](../../evidence/independent-recovery/source-usb-handoff-preparation-result.json).
