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

### Exact assembled candidate and prepared first normal trial

Corrected kernel run41528041827 succeeded at repositoryde64394dea3bd3f07a19170fed0f9a33f7d25fba,
ACKd9318bdb4c34e8b2d997b4f67ced56b120b22b87. Actual retained bytes were downloaded
and every manifest hash verified. Image15,424,000B, gzip6,488,090B, runtime footprint
15,925,248B, text_offset0; release6.18.34-gd9318bdb4c34-dirty. The dirty suffix
reflects the recorded local source-port overlays, not an unrecorded kernel revision.

The v2 logging component supersedes the earlier component: static init49,944B,
SHAa77706b167542a14e785dc4cada9d10799b56edc20d2a99a5a44070feb0114e6;
initramfs12,062B/SHAdabfef5991a447f56fb6b017f5f569bbe48f1ed5c843e2f7e3ea8b62af9e4420.
VLOG/VACK/VDON0002 adds a final host fsync acknowledgment before device success
and USB cleanup; missing/wrong final ACK fails the producer. The old version and
its component remain historical, never silently substituted into this candidate.

Offline packing passed: payload6,531,072B, fullp5 image16,777,216B,
SHAdde5d2bb3151a73b83a823639d3790416ac2321f3194b04ae57ddad731d7b429.
Kernel runtime occupies0x40000000..0x40f30000, initramfs placement0x43480000,
DT destination0x48000000 and bounded staging0x45000000. These regions avoid every
observed firmware reservation. The new header component ID is calculated, not
copied from the mismatching old p5. Both existing boot/recovery ramdisks begin
with plain gzip; the new ramdisk does too. The old p5 tail is explicitly replaced
by full candidate bytes and preserved exactly in rollback, not assumed understood.
Candidate and private nonce are copied/hash-verified on Linux and controller;
receiver input preflight passed unarmed, without a TTY open.

`run_lab_log_trial.py` is a distinct first-normal-trial supervisor, not StageA
replay. It validates the already-installed exact candidate/recovery and pinned
original helper, then only explicit arm claims a fresh receipt. It gives600s for
owner travel/manual TWRP boot, captures once with45s entry/30s transfer bounds,
ignores the first90s of normal boot, then gives300s for manual power-off/reconnect
before at most one90s FACTORYM helper. No candidate write, reboot or failure is
issued by this supervisor. Read-only recovery/candidate checks follow the helper.
The old StageA receipt remains completed and is never reused.

The concrete review must cover this complete one-trip sequence before any write:
from the desk, verify the current original p5/p6 and backup copies; explicitly
write only the full reviewed p5 candidate with fresh receipt and full readbacks;
check postwrite recovery/p5, then arm the exact private receiver/return plan only
when the owner is available. At the tablet, select TWRP Reboot→System once, decline
any installer prompt, wait90s, unplug USB, hold only Power until off (at most40s),
release, wait5s, reconnect the same cable/port without pressing other buttons.
Wait up to180s for the existing TWRP/special menu, leave it unchanged and return to
the desk with the observation. No retry, wipe, reset, install, unlock or new menu
selection. A frozen old framebuffer is not kernel-entry evidence. If shutdown or
return does not work, stop and report; do not improvise. The supervisor is unarmed
until this review/start and does not promise that force-off/failed-return works.

Amazon's [power-button guidance](https://digprjsurvey.amazon.com/csad/help/node/GXM4KLEMVLFM36CB)
provides a general40s shutdown provision; it is not evidence of this custom-kernel
return. The factory-reset sequence is not part of the trial. On return, read-only
receipts/log inspection and actual recovery identity are checked from the desk;
then explicitly restore the full original p5 and verify both partitions, leaving
TWRP running. Intended post-handshake failure qualification is a later reviewed
step after this normal log bringup. Early failures before logging stay uncovered.

## Post-trial correction — ARM64 flags, labels and PID1 domain

The empty capture does not prove that the tablet kernel never entered. A generic
ARM64 VM using the exact retained Image reproduced deterministic software blockers
inside the trial PID1, independently of the tablet loader/controller:

- The adapter's generic O_DIRECTORY00200000 is ARM64 O_DIRECT, so opening the UDC
  directory returns EINVAL. ARM64 O_DIRECTORY is0040000; O_NOFOLLOW is0100000,
  not the generic00400000. The prior ABI validator checked only asm-generic and
  therefore falsely accepted these values. The exact ARM64 override header is now
  pinned, checked before generic fallbacks, and former wrong values are negatives.
- Rootfs/configfs are not in the pinned kernel's per-path GENFS handling list.
  Preloaded/dev,/dev/console,/dev/kmsg retain rootfs_t, rather than the per-path
  labels assumed by the first policy. A VM probe observed enforcing denials for
  kmsg reading and creating the ACM node. PID1 now verifies exact object type and
  device numbers, labels only these three static objects with valid contexts,
  and reads their labels back. No forced label/MAC_ADMIN/permissive mode is used.
- Configfs has a uniform configfs_t label. The corrected policy permits the real
  required operations on that isolated filesystem; PID1 first requires a USB-only
  configfs root and an empty gadget namespace. Every mutating adapter still uses
  its fixed path allowlist, with no arbitrary path or preexisting gadget adoption.
- A longer VM run caught delayed kernel-worker fork denial. The old compiler's
  policy lacks userspace_initial_context support, so initial userspace and kernel
  workers both map to kernel_t. PID1 now uses the pinned LSM self-context API to
  enter init_t once and verify the returned SELinux context/enforcement. Proc stays
  read-only. Kernel-worker fork is permitted; PID1 fork, reverse domain transition,
  setcurrent, policy reload, enforcement toggle, raw/block IO and reboot remain
  forbidden. Six actual compiler-negative mutations are rejected. No kernel LSM
  change, new compiler or general proc write permission is introduced.

The reproducible `validate_lab_policy_vm.py` regression runs20s on one emulated
Cortex-A53/512MiB, no disks/network, bounded logs. It checks enforcing policy and
PID1 context, corrected directory access, real kmsg reads, real ACM configfs
creation/attributes/link and cleanup, empty namespace afterward, and the former
flags' EINVAL negative control. Only the final UDC bind is intercepted in the
VM-only fixture; this is explicitly not USB hardware/loader acceptance. All
markers pass and no AVC denial is observed over the full interval. Future lab-log
kernel workflows run this regression after retaining compiled artifacts.

The revised private fullp5 image is
4ec14bf8774949ff36ad2173fb9267f6d5dffb2d155f8be485521863dd10741b,
16,777,216B with6,533,120B aligned payload. Init52,800B and initramfs13,686B
replace only userspace/policy; the retained kernel and own DT are unchanged.
Independent header-ID/padding/gzip/DT/initramfs and memory-range checks pass.
See corrected-candidate-result.json, corrected-policy-build.json and
abi-label-vm-result.json under evidence/independent-recovery. The failed original
candidate and receipts remain historical; its old approval/arm receipt must not
be reused. Revised bytes are offline and unarmed. Any future physical test requires
review of this changed exact candidate, fresh read-only preflight/receipts and owner
availability. Tablet remains original boot restored/TWRP running. Physical entry,
USB capture and intended failed-load/348 acceptance remain open.

### Revised candidate2 — staged review and one-trip procedure

The revised4ec14bf8774949ff36ad2173fb9267f6d5dffb2d155f8be485521863dd10741b
full16MiB image/component8 is now hash-verified in a fresh private Linux trial2
directory with current tools and a distinct nonce, capture plan and unused
stage/trial/restore receipt paths. Receiver input preflight passes without opening
a port. Candidate-writer default read-only preflight confirms actual TWRP identity,
all four aliases and complete original p5/p6 hashes. Original full backups match on
Linux and controller. Original helper sources are verified without launch. The
exact physical-port USB rule is prepared privately but not installed; no udev
change, device write, supervisor arm, helper or reboot occurred in this preparation.
The supervisor's candidate-installed preflight is intentionally deferred until a
reviewed write has passed. See revised-trial-preparation-result.json.

This review admits only one normal log-bringup trial, not an intentional kernel
failure. The expected success is attributable kernel logs durably acknowledged on
the host, manual return to existing TWRP, then full original boot restoration.
Generic VM validation cannot prove board boot, USB binding or safe return. This
still writes the boot partition temporarily; a hang or failure before logging is
possible, and an inaccessible recovery would prevent immediate software restore.
The separate recovery partition is never written. Existing security policy remains
enforcing; no storage interface, automatic reboot or failure injection is added.

After owner approval of this exact revised image/rollback and current availability:

1. From the desk, recheck the exact assets/tools and current original p5/p6. Install
   only the scoped temporary host TTY rule and reload without a broad trigger.
2. Write the reviewed full p5 once with an exclusive fresh receipt; require full
   candidate readback and unchanged full p6. Stop on any mismatch, without retry.
3. Run the supervisor's installed-candidate preflight, then arm its fresh one-shot
   receipt only when the owner is ready to leave. Confirm armed before the trip.
4. At the tablet within600s, choose TWRP **Reboot → System** once. Decline any
   installer prompt. Wait90s; screen appearance alone is not kernel evidence.
5. Unplug USB, hold only Power until off, at most40s; release, wait5s, reconnect the
   same cable/port without pressing any other button. Do not repeat this sequence.
6. Wait up to180s for TWRP/special recovery menu. Leave it unchanged and return to
   the desk to report the screen. If shutdown/return fails or anything unexpected
   occurs, stop and report; do not reset, wipe, install or improvise.
7. From the desk, inspect private capture/return receipts and actual recovery;
   explicitly restore the entire original p5 once with fresh preflight, full p5/p6
   readbacks and RAM cleanup, leaving TWRP running. Remove only the exact temporary
   trial TTY rule and reload without trigger. Preserve private logs and rollback.

Capture has45s entry plus30s transfer bounds, the supervisor ignores the initial
90s normal-boot preloader and allows300s for the owner's later reconnect, with at
most one90s original FACTORYM helper. No physical instruction starts until the
separate armed confirmation. No automatic retries, old trial reuse, recovery write,
reinstall or StageA replay. Intended failed-load/retention qualification remains a
later reviewed gate after actual normal logging succeeds.

### Trial2 reset lead and inherited watchdog handoff

The exact scoped host timeline has a further preloader enumeration49.35s after
normal-boot recovery disconnect, before the instructed90s owner wait. This is a
reset lead, not a measured reset cause or proof that the maintained kernel entered.
The tested resolved config disables WATCHDOG. The own-source DT watchdog node
uses mediatek,mt8163-wdt, absent from the pinned ACK driver's match table.

The next changed kernel contract enables builtin MediaTek watchdog/core and
WATCHDOG_HANDLE_BOOT_ENABLED with open_timeout0, adding only the exact board
compatible to the existing base driver (NULL extension data). Pinned legacy/ACK
MODE/LENGTH/reload offsets, enable bit and keys agree; sources are retained under
watchdog-source. The upstream init only marks/services an already-enabled timer;
it does not start a disabled one. The kernel worker services inherited hardware
until userspace takeover; this PID1 has no watchdog node/open or takeover. There
is no new userspace permission, raw memory access, SW reset invocation,
reset-controller variant data, thermal-request write or enforcement relaxation.
It does not establish the prior reset cause or guarantee entry before the driver.
Manual shutdown/recovery provisions and subsequent complete review remain required.

The patch applies only in lab-log mode against exact source/output hashes. Tests
execute the actual upstream init with enabled/disabled register fixtures, reject
wrong revisions/reapplication and require the explicit builtin handoff config.
The build must compile/hash watchdog translation units, retain full kernel bytes,
check the same loader memory/capacity contract and run the enforcing VM regression.
No old candidate is reusable. No tablet operation is authorized by this source
change; future exact combined-image/rollback review follows successful compilation.

The prospective host supervisor now waits at most30s for metadata-only recovery
readiness after helper success, with each probe capped at2s and two stable exact
recovery/douglas/TWRP observations. It then performs the full existing alias and
partition validation once. Timeout/mismatch stops; no full-read, helper, write or
reboot retry is added. Both prior initial failures remain unexplained, rather than
being retroactively declared readiness races. Synthetic clock/probe tests cover
delayed readiness, persistent mismatch and hung metadata commands. This host change
does not alter the kernel build inputs or dispatch another build.

### Exact watchdog candidate3 — complete review before execution

Changed kernel run41552296163 succeeded at repository18abfbf3ef3673df14e59c97d7d913811b502cf8
and pinned ACKd9318bdb4c34e8b2d997b4f67ced56b120b22b87. Watchdog/core objects compiled,
final System.map contains the probe/driver/core symbols; resolved builtin boot-enabled
handoff config, loader size and full20s enforcing VM checks pass. Retained manifest
hashes all match. Image15,424,000B, gzip6,500,631B, runtime15,925,248B, text_offset0.
The VM still intercepts final UDC binding: no board watchdog/USB behavior is proven.

Exact new full16,777,216B boot image SHA256:
09ca6e2be60cc508fc5b93b7f577e5b0ef861e5c89486c18fda40b078075c3b7.
Aligned payload6,545,408B. Own hvt DT and placements are unchanged. Fresh component9
has init52,800B SHA6a468360e002bed308193a8bba5bcd1e2999e02fdf1476dcd589198253066890,
initramfs13,686B SHA2d26dd738b2c610619d568c6625e4117b063f2a5c154c7fe3e0c385edbaa2553;
private fresh nonce. Independent header ID, component/gzip/DT suffix, padding and
memory-range checks pass. Fresh private trial3 assets/current tools/commands are
staged and hash-verified. Receiver input preflight and actual read-only original
TWRP/aliases/fullp5+p6 checks pass; Linux/controller rollback copies match. Distinct
stage/trial/restore receipts are unused. TTY rule is prepared but not applied.
No candidate write, serial open, helper, arm or reboot occurred in preparation.

The changed behavior is kernel handoff of an already-running firmware watchdog:
the kernel keeps that counter serviced until userspace takeover, which this PID1
does not perform. A disabled timer is not started by init. This may prevent an
inherited timeout reset, but the previous reset cause is unproven. It can also
leave a hung userspace waiting for manual shutdown rather than an inherited timer
reset. No thermal-request bits or security enforcement are changed. Failure before
the driver or USB logger remains uncovered. Recovery could be inaccessible, making
immediate software rollback impossible. Approval of an older image is not approval
of this changed exact image/behavior. This is only normal logging, no deliberate
failure and no closure of346/344/348.

After approval of this exact candidate/rollback and owner availability:

1. From the desk, freshly verify exact assets/tools and original p5/p6; install only
   the scoped temporary TTY rule and reload without a broad trigger.
2. Write only fullp5 once with exclusive fresh receipt. Require full candidate
   readback and unchanged fullp6; stop on mismatch, no retry or recovery write.
3. Run installed-candidate supervisor preflight; arm the fresh one-shot receipt and
   confirm it is armed before the owner leaves. No automatic boot command.
4. At the tablet within600s, choose TWRP Reboot→System once, decline installers,
   wait90s. Unplug USB; hold only Power until off, at most40s. Release, wait5s,
   reconnect the same cable/port without pressing any other button. Do not repeat.
5. Wait up to180s for TWRP/special menu. Leave it unchanged, return to the desk and
   report the screen. If shutdown/return fails or anything unexpected occurs,
   stop/report; no reset, wipe, install, unlock or improvised menu sequence.
6. From the desk, inspect private capture/return and actual recovery. The supervisor
   allows30s metadata readiness (2s/probe,two stable identities) then full validation
   once; this is no helper or write retry. Explicitly restore the original fullp5
   once with fresh preflight, complete p5/p6 readbacks and RAM cleanup. Leave TWRP.
7. Remove only the exact temporary71 trial rule, reload without trigger and retain
   private evidence/original rollback. Older host preparation remains separately
   tracked without disrupting authorized ADB.

Capture45s entry/30s transfer, initial normal-preloader guard90s, manual reconnect
window300s and at most one90s original FACTORYM helper remain unchanged. No old
trial/candidate/receipt reuse or StageA replay. See watchdog-candidate-result.json.

### Independent early display checkpoint prerequisite

The three zero-byte captures leave kernel entry unobserved. Exact original-package
loader inspection found a conditional K64 compressed-image/DT path, without a
concrete mismatch. The next diagnostic separates entry from USB using the
firmware-owned display allocation rather than another receiver-timing change.

Read-only FBIOGET_FSCREENINFO/FBIOGET_VSCREENINFO metadata and the firmware
videolfb tag agree on0x98600000. Only the API's12,288,000B allocation is selected,
within the16MiB display reservation. No pixel/physical RAM content was read;
temporary metadata executable was removed. Source and sanitized metadata live in
`evidence/independent-recovery/entry-screen-source/`.

The lab-log-only source overlay calls a bounded marker after init_kernel_el and
before __cpu_setup. It requires the expected DT handoff address, FDT bounds and
exact root board compatible before writing alternating64KiB black/white stripes.
It preserves x0/x19/x20/x21/SP, issues a store barrier and returns to normal boot.
It does not enable display rails/clocks, change scanout registers, halt, inject a
failure or expose storage/security controls. Actual marker instructions passed
emulator checks of eight negative FDT cases, every buffer word and adjacent guards.

A visible unique pattern is a positive kernel checkpoint only. Whether firmware
scanout survives the custom boot is not physically qualified; absence cannot
identify a failed stage. There is no new device-write/boot authorization here.
The complete new image, logs/rollback procedure and owner availability must be
reviewed before staging a physical trial. Keep346/344/348 open.
