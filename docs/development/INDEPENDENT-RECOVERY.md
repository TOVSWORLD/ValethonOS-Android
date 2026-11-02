# Issue346 — bounded independent recovery preparation

Current Phase1 work follows accepted entry347. Ordinary return and normal logs
are complete; failed-load return and348 retention are not. No device operation
is authorized merely by this document or a passed host test.

## One server-room visit

Owner chats from a separate desk and cannot reply beside the tablet. Prepare and
verify the supervisor before asking for a visit. Arm only on an explicit desk-side
start instruction. Allow up to10minutes for travel and manual disconnection;
then up to5minutes for manual shutdown/reconnection. Only after the verified
serial interface appears does the single90-second helper window begin. Never ask for a chat
reply from the server room. No automatic reboot, flashing, wipe or failure injection.

The original v1.2 FACTORYM helper is the only selected device command. Pin its
original archive and all local Python dependencies; require the physical USB port
recorded while authorized Android ADB was connected. Reject other or ambiguous
MediaTek serial interfaces. Never use original ttyACM auto-discovery. Run at most
one helper with an explicit verified port, kill its process group on deadline,
and leave private logs on Linux. A host exit0 is not recovery acceptance.

After reconnection, owner waits up to two minutes. If the existing TWRP menu
appears, leave it alone: no swipe, mount, reboot or install. On unexpected screen
or absent recovery, stop and return to desk without another attempt. Capture only
technical ADB/recovery metadata after owner returns; no account or user-data reads.
Existing TWRP may write its own logs/header maintenance; no whole-device zero-write
claim. No intentional failed-load trial is included. StageB artifact, return endpoint
and attributable retained logs require a separate review after StageA observation.

## Attempt1 timing correction

Owner observed Android home, also verified with technical ADB boot_completed1.
The original supervisor started90seconds at USB disconnection. Retained Linux
events show the MediaTek preloader appeared111.33seconds after disconnection,
after that window expired. The helper never launched. This was a host timing
design error, not proof that the recovery command failed. Separate the manual
shutdown/reconnection allowance from the actual helper deadline; no automatic
retry or new physical attempt is admitted by this correction.

## Required host verification

Test absent initial USB identity, wrong/ambiguous interfaces, changed helper hashes,
travel timeout, reconnect/handshake timeout, one-launch limit and no default execution.
Dry-run/preflight must not open a serial device or change tablet mode. Actual
qualification remains pending until observed. Preserve rollback assets and logs.

## StageA observed — 31 October2026

Corrected attempt2 completed original FACTORYM helper with exit0. Owner reported
the special recovery menu; technical USB ADB independently reports recovery,
TWRP3.3.1-0, douglas and kernel3.18.19-g51c2c8d5bfb. This demonstrates existing
recovery entry from the manually powered-off tablet without using Android ADB
for the transition. No intentional loading failure was introduced. The helper
receipt does not observe recovery itself; the separate technical observation
provides that proof. See sanitized attempt2-result.json in evidence/independent-recovery.

Device is left in existing TWRP; no menu action or automatic reboot selected.
Next is exact failed-load artifact/transport/return-endpoint and retained-log
review under346 then348. StageA does not close failed-load return or log retention.

## StageB prerequisite and execution boundary

The existing isolated diagnostic kernel receipt cannot supply retained logs:
PSTORE_RAM was modular and its initramfs includes no modules or loader. Require
PSTORE=y, PSTORE_RAM=y and PSTORE_CONSOLE=y in the current resolved configuration;
keep the block-device backend disabled. Pinned ACK pstore Kconfig defines these
symbols. A build must pass the current policy; the old compiled configuration
may only pass an explicitly labeled historical-policy audit.

Recovery metadata observed after StageA: /proc/last_kmsg, /sys/fs/pstore and
/proc/config.gz absent; /dev/kmsg present/readable. This is not proof of kernel
configuration or absence of every proprietary logging mechanism. Live kmsg alone
cannot establish retention across a failed boot.

The remaining concrete inputs before StageB are an exact combined kernel/DT/ramdisk
artifact and proven nonpersistent loading/placement contract, an isolated RAM-log
region with observed firmware/loader ownership, and a compatible post-failure
readout from the reachable recovery. No arbitrary RAM address, guessed DT property,
stock-DTB substitution, rejection-only fastboot test or deliberate crash of the
working recovery counts. No test is admitted until those inputs and the single
return action/timeout are reviewed. StageA demonstrated independent recovery entry;
it did not prove these image-specific properties.

This necessary logging source/build prerequisite is recorded under346 before
implementation. No new microissue or unrelated hardware scope; no firmware load,
crash, wipe, security weakening or recovery menu operation accompanies it.

Scoped recovery-DT reads confirm the legacy RAM-console reservation at0x44400000/
2MiB and low-level log reservation at0x44600000/128KiB. These firmware-owned
reservations are not free space for an arbitrarily placed ramoops region; no RAM
content was read and no buffer was assigned. The ll_log node name contains46600000
but observed reg is44600000, preserving the source/runtime distinction. Compatible
record format, reset survival and independent post-failure readout remain required.


### Legacy reservation is not a compatible ramoops reader

The cached legacy implementation confirms a concrete format obstacle, rather than
just a missing mount. In `sources/kernel-mt8163/drivers/misc/mediatek/ram_console/
mtk_ram_console.c`, `ram_console_buffer` has stage offsets, total-buffer size and
console offsets before its ring position/length. Its `ram_console_init()` saves an
old copy, then rewrites the stage/console metadata and clears the Linux area.
By comparison, cached `sources/kernel-mt8163/fs/pstore/ram_core.c` places signature,
ring start and ring size directly before data. Both cached implementations use
base signature `0x43474244`; matching that word therefore does not establish
format compatibility. A ramoops signature can additionally be XOR-adjusted.

Consequently, assigning generic ramoops to the existing legacy console reservation
cannot be justified by its name, size or signature. A legacy consumer can reinterpret
or overwrite a different layout. These are source observations, not proof that the
running recovery enables either path or that any bytes survive its reset route.
The next load/readout contract must identify a dedicated owned region and a reader
using the exact writer layout, or explicitly qualify a compatible legacy writer
and reader. No reservation, kernel load or RAM-content read is selected here.


### Match the loader before selecting a RAM-load command

The approved original archive's `amonet/bin/lk.bin` is485,988bytes,
SHA256 `7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056`.
The historical stock LK used by the registration/handler audits is485,552bytes,
SHA256 `4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08`.
They differ. The historical selected registration table therefore neither proves
nor excludes a RAM-boot command in the original-package LK with its runtime payload
patches. The payload's enlarged download limit alone is not such a command.
[Identity receipt](../../evidence/independent-recovery/loader-identity-result.json)
records this cached-file comparison. Before choosing transport, resolve command
registration and handoff against this exact package binary and applied patches;
no device transition or speculative command is needed for that source prerequisite.


The exact original-package registration function matches the historical function's
instruction window at its new payload offset0x3f600. Applying the existing Thumb
PC-relative-label/call decoder to its bounded registration region0x3f9ac–0x3fcac
resolves13 entries: getvar, OEM flags, signature, flash, erase, dump, continue,
reboot, reboot-bootloader, download, relock, p2u and off-mode-charge. No `boot`
entry appears in this selected region. The receipt pins the windows and individual
call offsets. This is not a whole-image absence claim or runtime permission test;
it means the selected exact-binary evidence still provides no nonpersistent boot
command. Do not substitute `download` plus `continue` without a proven RAM handoff.


### Direct recovery loading check — 1 November2026

Read-only ADB reports recovery state and `uname -m=aarch64`. The original TWRP
kernel also expands from its512-byte MediaTek/gzip wrapper to an ARM64 Image;
the ARMv7 installed Android userspace must not be used to infer recovery kernel
architecture. Its embedded configuration was not found. Current recovery exposes
none of `/sys/kernel/kexec_loaded`, `/sys/kernel/kexec_crash_loaded` or
`/proc/sys/kernel/kexec_load_disabled`. This establishes no supported kexec route;
it does not replace a resolved configuration or prove absence of every custom
loader. No load syscall, module injection, RAM content read or reboot was tried.
[Capability receipt](../../evidence/independent-recovery/recovery-ram-load-capability.json).

The immediate engineering dependency is therefore a concrete supported transport,
not another generic kernel compile. Neither the selected original fastboot command
registrations nor the current recovery capability check provides one. An additional
loader implementation or an explicitly reviewed alternative loading procedure is
needed before image placement and retained-reader qualification can be exercised.


Follow-up reader metadata: `/sys/kernel/uevent_seqnum` exists, so the missing
kexec attributes are not simply explained by an absent kernel sysfs directory.
`/proc/filesystems` lists no pstore filesystem; the narrowly filtered current
recovery initialization log supplies no ram-console/pstore initialization line.
No virtual filesystem was mounted. These observations supply no built-in compatible
reader, while remaining narrower than a complete resolved kernel configuration.
A manual full power-off, as used in StageA, also cannot establish volatile RAM-log
survival: StageB must specify a qualified reset/retention lifecycle or a reviewed
persistent logging mechanism. Repeating StageA cannot close that gap.

## Owner-directed boot-partition alternative — 2 November2026

Owner requested concrete preparation of a reversible persistent diagnostic boot
image after no supported direct RAM route was established. This preparation stays
inside346/PR453. It does not repeat unlock/ROM/GApps installation, replace recovery,
write bootloader/security partitions, or admit a physical failure test.

### Actual rollback inputs, not a donor-image assumption

Current recovery readback resolves both boot and boot_x aliases to physical
mmcblk0p5,16MiB. Recovery and recovery_x resolve to mmcblk0p6,17MiB; the separate
boot_amonet/recovery_amonet aliases must not be confused with these destinations.
Two complete binary-clean reads of each selected partition match. Full private
copies on Linux and the controller match those hashes. Exact sizes/digests and
limits are in [boot-trial-rollback.json](../../evidence/independent-recovery/boot-trial-rollback.json).
No personal-data partition was read. Backups are not committed or published.

The first attempted dd reads were rejected because their stdout included transfer
summaries beyond the expected partition size. No bytes were trimmed or accepted.
Binary-clean cat reads, exact length and two independent hashes established the
accepted copies. No tablet write occurred.

The installed boot kernel is gzip ARM64 followed by two DTBs, without the512-byte
MediaTek wrapper used by the current recovery kernel. Both use2048-byte header
pages and kernel load address0x40080000, but their ramdisk addresses differ. The
installed boot's component SHA1 differs from its header ID, and its partition
contains8,980,480 trailing bytes beyond the aligned components. Their meaning is
not established. Recovery's component SHA1 matches. Do not blindly clone boot
metadata, transplant recovery addresses, append a stock DTB or discard an unknown
trailer as though loader compatibility had been proved. Full rollback preserves
all bytes, including the current trailer. These findings prevent calling an
arbitrary v0 repack a reviewed trial image.

### Prepared exact rollback tool

`scripts/restore_diagnostic_boot.py` runs on Linux with an explicit private ADB
selector file, private full boot backup and pinned manifest. Default execution is
read-only. It checks recovery transport/douglas/TWRP3.3.1-0, all four aliases,
full recovery hash, full backup size/hash and the explicitly expected current boot
hash. Default preflight was run successfully on the real tablet. This is not a
physical restore execution test.

Only an explicit --restore plus a fresh private receipt selects a single full p5
write. The expected current hash must be the exact separately reviewed full trial
partition hash, not a guessed boot-image prefix. The tool never writes p6, stages
files on userdata, reboots or retries. A write uses an exact full backup first
uploaded to an exclusively named directory on a confirmed /tmp tmpfs mount. It
verifies the full RAM copy and both partition preconditions again, then selects
one file-to-p5 dd copy, sync and full boot/recovery hash readbacks.
An interrupted or mismatched write leaves a failed receipt and must leave TWRP
running. The write branch remains device-untested; seven host tests cover RAM corruption, target and
backup rejection, exact rollback, interrupted/mismatched write, reused receipt and
already-restored no-op. Host tests do not qualify the physical block-write branch.

### Proposed execution sequence and remaining engineering

1. Resolve one explicit maintained-kernel/board-DT/initramfs/header placement and
   compressed-image format against the selected loader. The successful generic
   uncompressed Image is28,645,888bytes, larger than p5; the compressed image is
   9,204,813bytes, but that alone proves neither full-package fit nor load placement.
   Produce the actual combined image and its resolved config, component sizes,
   hashes and exact intended full partition bytes only after the contract is fixed.
2. Replace speculative volatile retention with a proposed independent host log
   file. Implement an actual bounded kernel-log stream, attributable to the exact
   build/trial, and make the host durably store the stream before a deliberate
   post-handshake failure can be selected. Capture must survive tablet power-off.
   The existing73-byte ACM status frame is not a kernel-log stream. Current
   diagnostic config disables USB and all block/storage interfaces, so the completed
   logging-kernel compile cannot supply this mechanism. Existing denied USB source
   and fixed-frame fixtures do not grant admission; transport/role/DT/security
   prerequisites must be resolved within346 as necessary trial prerequisites.
3. Review the exact boot-only write, tested binary-write transport, independent
   capture, one bounded failure and one complete owner trip before execution.
   Preserve recovery, system and userdata. Do not arm StageA again from this text.
   A future use of its established return mechanism needs a separately prepared
   one-trip supervisor and an explicit owner availability/start instruction.
4. Return to existing TWRP, verify its exact identity/hash, restore the full p5
   backup using a fresh receipt and verify full readback. Booting Android again is
   a separate explicitly selected action, not an automatic consequence of rollback.

This proposed host capture covers only a failure after an attributable stream
starts and its evidence is stored. A silent failure before USB/log initialization
is not covered and cannot be relabeled as retained first-kernel failure logs.
The intended failure case must meet346's actual acceptance before any test is
selected; if an earlier failure is required, a separate working early capture
mechanism remains necessary.346/344/348 stay open. There is no ready candidate,
new kernel build, physical write or owner trip pending from this preparation.

### Legacy ADB transport correction — 2 November2026

A no-file-write binary echo test rejected the original --restore command path:
the running recovery refuses `adb shell -T` because it only supports PTY allocation.
An EOF-dependent raw cat probe also timed out. Neither was a block write. Do not
use PTY allocation for binary rollback or label default read-only preflight as
write-transport qualification. The earlier shell-stdin restore path was removed
before any physical restore attempt.

The corrected RAM staging path was exercised on the actual tablet: /tmp resolves
to itself and is explicitly mounted tmpfs; an exact16MiB rollback image uploaded
there, two complete RAM readbacks matched the verified backup, and the temporary
RAM file/directory were removed. The boot partition remained unchanged by full
hash readback. The final RAM-file-to-block dd operation remains unexecuted. No
recovery replacement, firmware write, automatic reboot or new owner trip occurred.

## Separate private log-bringup candidate — 2 November

The reversible p5 alternative now has a separate source candidate, not a granted
legacy admission flag. Its PID1 embeds an exact compiled nonpermissive SELinux
policy, requires initial enforcement, refuses replacement of an existing policy,
loads once and remounts selinuxfs read-only. Compiler negative controls reject
policy reload, enforcement toggle, block reads and reboot capability. No policy
was loaded on the tablet. Actual kernel policy loading remains a first-trial test.

The current Linux-host component build produced a static ARM64 PID1 (49,832B,
SHA2561209db3fe7232918cb3ba0ddd65ddecce76346033bb0c78398cf69f943e0089a)
and12,026B initramfs (SHAbc4d69834385b17698cb22232b2ae441290b677a86734ab750becfa43667352f).
The private generated nonce and full report remain in private lab output. The
archive has only the PID1, virtual mount directories, console and readonly kmsg
nodes; no storage nodes, shell, module loader, failure or reboot interface.

The own-source lab DT compiles without diagnostics and compares all190 nodes;
artifact27,408B/d58d4b26bc65bebda14067145558625013c9ff3db66978db238d1b7456f4798c.
It preserves source MMIO/clocks and observed firmware reservations, uses observed
RAM banks, disables unused device nodes and secondary-CPU entry, and requests one
CPU. PID1 requires online/possible CPU sets both exactly0 before USB setup. No
stock DTB substitution, new ramoops address or thermal-threshold change is made.

The original package selected gzip path supplies28MiB decoded capacity. The prior
41,699,840B USB Image cannot fit. The separate `lab-log` profile combines the
restricted no-storage diagnostic policy with builtin USB/SELinux, selects only
the MediaTek platform and size optimization, and disables unrelated device code.
Security enforcement/bootparam restrictions remain intact. Future exact bytes are
retained seven days. This is a necessary prerequisite within346, not a new task.

`kernel/lab-log/package-contract.json` and `pack_lab_log_boot.py` define a
conditional offline candidate: Androidv0/page2048, unwrapped deterministic gzip,
aligned own hvt DT suffix, and the observed0x43480000 initrd placement. Entry is
observed RAM base0x40000000 plus the fresh ARM64 header text_offset; never blindly
copy the old kernel's0x40080000 entry. Decoded file and runtime footprint are
checked separately against loader capacity, inflate stack, observed RAM,
reservations and other components. Fullp5 padding replaces the unexplained old
tail only after concrete review; the full original rollback preserves it.

The private test descriptor1209:0001 is permitted for in-house experimentation
by [pid.codes](https://pid.codes/1209/0001/), is nonunique, and is forbidden for
redistribution/manufacture here. The receiver must bind the approved physical USB
path and exact private nonce, never accept a VID/PID alone. Ten seconds of kmsg
records follow durable identity ACK; each record is fsynced on the lab host.
ACK is not permission for deliberate failure. The first trial is normal log
bringup; failures preceding initialization remain outside its coverage. No
physical boot, USB logs, failed-load return or348 retention is claimed yet.

Host-side preparation now includes a separate explicit lab receiver, a default
read-only candidate-staging preflight and retained-record inspector. The receiver
requires owned private plan/report/nonce, exact physical USB parent plus ACM
interface00, one port open, nonblocking raw9600 duplex settings and a fresh private
output directory. It durably creates the raw file before identity ACK and never
retries a disconnected trial or issues boot/reboot/failure commands. The retained
inspector requires nonempty correctly sequenced kmsg records and matching built
kernel release; missing sequence0/version is reported as an incomplete initial
prefix, not early-log acceptance.

`write_lab_boot_candidate.py` verifies both the full original rollback and exact
candidate report before invoking the same tested RAM-staged one-write transport.
Default is read-only; explicit candidate writing remains unexecuted on hardware.
Write intent and final receipts are fsynced. Fixture tests cover candidate→original
rollback, bad report/hash rejection and no recovery write/reboot. Linux native
checks for all12 new lab tests pass; this still cannot qualify physical restore.
