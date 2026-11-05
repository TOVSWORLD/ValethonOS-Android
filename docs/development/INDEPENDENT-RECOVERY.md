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

### Exact early-screen candidate4 — complete review before execution

This supersedes prior ready candidates. Run41566321777 at source
4ef0bc8c1175f548e965286f636001efa6113d48 succeeded, including the exact-marker
emulator and20s enforcing PID1 VM. All retained manifest hashes verified. Actual
Image marker459bytes exactly matches the emulator-tested instructions. Image
15,424,000B SHA2c82fd024682f47b50cdb84abb3aa476801a462a52273e685895eff23fe4e4fa;
gzip6,500,129B SHA85f5e3c613e8cefb80e2eca364f443b9065576adf658a24a2107434531ce2ccd.
Runtime15,925,248B fits the selected loader28MiB decoded limit.

Exact full16,777,216B candidate4 SHA256:
fba4edca641182a77aa385a7b137e8e2834586a53f974d1ddc38aa0f1035cb9e.
Payload6,545,408B. Own DT/placement unchanged: entry40000000/runtime ends40f30000,
initrd43480000, tags48000000, bounded DT staging45000000. Fresh component10 has
init52,800B SHA0c4f0121e9901aa0c1dc0aca2e15f7c3f3928b96e3f8c6a6306bad7dde0ad072,
initramfs13,686B SHA85184f1d3c9c38db70aa5f127e36dc65cf30d28c1b9c0b4c95dfd4e101b6b50a,
unchanged enforcing policy and a fresh private nonce. Independent header ID,
gzip/components/DT suffix/padding/range checks pass. Fresh trial4 assets/tools are
hash-verified, receiver-input and actual read-only original TWRP/allaliases/fullp5+p6
checks pass; lab/controller rollback match. Rule is prepared but not installed;
stage/trial/restore receipts unused. No serial open, write, helper, reboot or arm.

New physical behavior for review: the kernel writes alternating64KiB black/white
bands into the corroborated intended display allocation98600000..991b8000 after
MMU-off normalization, before CPU setup and USB. It reads bounded DT metadata,
never pixels, changes no display-control registers and continues normal boot.
Firmware scanout could be disabled, replaced or cleared; absent bands do not prove
failure to enter. Visible distinctive bands prove only reaching this early
checkpoint, not userspace/logging success. Watchdog inherited-counter servicing
from candidate3 remains; a hung kernel/userspace may require manual Power hold.
Recovery return can fail, leaving immediate software rollback unavailable. There
is no intentional failure, security relaxation, storage interface or acceptance of
346/344/348. Full original boot tail/partitions remain retained for exact rollback.

After approval of this exact changed image/framebuffer behavior/rollback and owner
availability, the complete sequence is:

1. At the desk, recheck fresh assets, original fullp5/p6 and tools; install only the
   exact scoped temporary71 TTY rule, reload without trigger. Write fullp5 once,
   verify full candidate readback and unchanged fullp6. No retry/recovery write.
2. Run installed-candidate preflight, arm the fresh one-shot supervisor and confirm
   armed before the owner leaves. No automatic boot command;600s travel budget.
3. At TWRP choose Reboot→System once. If any installer prompt appears, decline it;
   no prompt is expected or required. Watch the screen for the full90seconds from
   choosing System, noting whether black/white bands appear even briefly and what
   follows. Amazon logo or black alone are not success/failure indications.
4. After those90seconds, unplug USB. Hold **only Power for40seconds even if the
   screen is already black**; release, wait5seconds, reconnect the same cable/port
   without other buttons. Do not merely reconnect at the first black screen.
5. Wait180seconds. Leave any TWRP/special menu unchanged and return to the desk to
   report bands/no bands, final screen and any deviation. If anything unexpected
   happens or return fails, stop/report; no retry, wipe, install or improvised reset.
6. At the desk inspect private capture/return and actual recovery. Supervisor has
   capture45s entry+30s transfer, initial90s normal-preloader guard,300s reconnect
   window, at most one90s pinned original FACTORYM helper,30s metadata stability
   then full validation once. No helper/write/boot retry or StageA replay.
7. After actual recovery verification, restore exact original fullp5 once using
   fresh guarded preflight/receipt, fullp5+p6 readbacks and RAM cleanup. Leave TWRP
   running without reboot. Remove only exact71 rule/reload without trigger; retain
   private logs and original backups. Older host preparation remains tracked.

No step is armed by this document or prior approval. See entry-screen-candidate-result.json.

### Retained boot-tail path — implementation contract, not device approval

This is a separate lab-retained build, not another USB logging/timing trial.
Original boot/recovery remain restored and nothing is armed. Necessary346/344
prerequisite was recorded before implementation. Legacy reader/raw-memory path
metadata checks found no installed endpoint; no RAM/partition contents were read.

The new builtin kernel worker snapshots printk independently of PID1/USB. Root
board compatible and exact32-byte chosen nonce are required. Target must be
exclusive mmcblk0p5, partition5,16MiB, writable. Seed nonce/CRC and complete first
15MiB SHA256 must match before any data write. Normal block BIO/flush APIs are used;
no credentials, SELinux mode/policy, userspace block interface or generic target
control is added. Existing PID1 block-device neverallows remain intact.

Proposed on-disk geometry inside the experimental image only:

- Immutable boot prefix:0..0xf00000, SHA256-bound.
- Offline seed:0xf00000..0xf01000, nonce/prefix digest/checksum, never kernel-written.
- Slot0:0xf01000..0xf80000; slot1:0xf80000..0xfff000,127pages each.
- Final guard:0xfff000..0x1000000, zero and never written.
- Each slot:4KiB header, up to516,096B payload; VLOG0001/version, sequence,
  nonce, length and independent header/payload CRC32. No filesystem/GPT/other
  partition writes. Unexplained original tail remains in the full rollback backup.

The inactive slot header is invalidated/flushed, payload written/flushed, then
header committed/flushed. Writes are4KiB-aligned with zero padding only inside the
chosen slot. Any failed/partial I/O stops, never retries. Twelve snapshots at
5-second intervals are proposed after bounded storage discovery. Before first
successful storage initialization/commit, a failure remains uncovered; this is
not a panic/crash handler and cannot promise every printk message survives.

A preinstalled HOST CONTROL sequence1 is explicitly not a kernel log. A kernel
producer/release prefix with sequence2+ is reported separately. Returning only the
host control proves readout of the known preinstalled record, not kernel execution.
A newer valid kernel record survives a torn subsequent slot in the offline tests.
This control distinguishes broken retrieval from no kernel commit.

Minimal own-source DT enables only mmc0/pio/pwrap,26MHz, removes HS200/highspeed/
hardware-reset caps and adds nonce; exact semantic comparison preserves all other
nodes/firmware reservations. The config adds block/eMMC/GPT/MT6323 supply
prerequisites only in the explicit lab-retained mode. This allows normal driver
pin/clock/rail/card initialization and changes physical behavior. Timing, voltage,
DMA and power-loss behavior remain device-unqualified and require complete review.
No MMC feature/hardware task is closed by this necessary logging prerequisite.

Actual C codec and BIO frontend pass regular-disk fixture writes with an independent
Python decoder, unaligned payload padding, seed/guard/prefix bounds, stale/corrupt
records and all six write/flush cuts. Kernel compile41573826310 exposed a current
macro collision; corrected and covered by a real-macro C regression. Corrected
kernel41574337098/source035f197 is the single current build; no unchanged retry.

The persistent-only host supervisor makes no diagnostic serial capture/open and
needs no new TTY rule. It retains the90s initial normal-entry guard, allows a
reviewed900s manual reconnect window and at most one original return helper.
After actual recovery, the read-only collector verifies identity/aliases/fullp6,
exact candidate prefix/seed and extracts the best attributable record. It stores
full post-trialp5 privately and its current hash. `restore_retained_trial.py`
validates that independent readout; default only fresh device preflight. Explicit
restore uses that exact current hash with the existing one-write full-originalp5
transport, full boot/recovery readbacks/RAM cleanup, no reboot or recovery write.

This contract is implementation groundwork. Actual kernel object/Image/config/
loader-size/VM checks, fresh seeded combined image, staged read-only preflight and
complete exact physical collection/rollback review are required before approval.
Source/fixture successes are not runtime admission;346/344/348 remain open.

### Exact retained candidate5 — complete physical review, UNARMED

Build41574337098 succeeded at source035f197fa4c46f16e53eacdbe1775f09af069278
and ACKd9318bdb4c34e8b2d997b4f67ced56b120b22b87. Actual recorder/eMMC objects,
final recorder symbols, all retained manifest hashes, loader-size checks and20s
enforcing PID1 VM pass. Generic VM does not exercise physical eMMC recording.
Image16,912,896B SHA940398b2949fae104e3b0db1aa192a3f0b08593b59bccb6ad6f3856819473fea;
gzip7,251,746B SHA3846e9d6c9de0a170f0acab7175b82538b6b5b686876779b6b456710b2d9a738.
Runtime17,432,576B, entry40000000/end410a0000, below selected loader28MiB limit.

Exact full16,777,216B candidate5 SHA256:
423ed64dc2a24e4ffc23c48f4a71246a1694dc98896f6465a8ad3c5357a4099e.
Aligned boot payload7,297,024B ends before the15MiB mailbox boundary. Initrd43480000,
tags48000000/1MiB and DT staging45000000 are unchanged and reservation-checked.
Fresh component12 init52,800B SHA2cd05634dce53bcd7a18b4f3159f4bacb35c7f1482a8acf6d64ae98398ff81b3;
initramfs13,685B SHA61f0caa4460bb9ce26e0e331bc064bd3e61c98ff4bea4194f88232407105add9.
Own retained DT27,376B SHAfb4ad1f5b022ba196c9a65d2205a01714f9b1a685808ce2c03f07faa9bed5b6a.
Initial enforcing policy unchanged. Independent header ID/gzip/component/DT suffix/
padding/seed/control/nonce/range checks pass. First15MiB prefix SHA256:
de658015aeb9cf65ab1fec05daf95996fd6b7c3f36e281ee9d277e36e53c8823.

Fresh trial5 assets/current tools and concrete commands are staged/hash-verified.
Actual original recovery/aliases/fullp5+p6 read-only preflight passes; original full
rollback copies match lab/controller. Fresh stage/trial/restore/readout receipts
are unused. No candidate write, helper, arm, new TTY rule or reboot occurred.

**Changed physical behavior requiring this review:** normal eMMC/PMIC/pin/clock
initialization at the source-described controller,26MHz cap without HS200/
highspeed/hardware-reset caps; builtin kernel worker reads the experimental p5
prefix/seed then writes only its record slots with flushes. This is new hardware
access beyond prior candidates. A source/driver failure could prevent boot/return
or damage data despite software bounds. Backups do not guarantee recovery access.
No new kernel userspace storage permissions, filesystem, credential or SELinux
change is introduced. Original/recovery images are never initialized as mailboxes.
There is no deliberate panic/failure injection. Twelve snapshots per kernel
invocation are bounded; a spontaneous firmware restart is not a host retry and
may start the kernel again. No automatic host reboot/retry is issued.

This trial has an explicit result decision:

- Host control alone: known stored record/readout works; no kernel commit proved.
  Investigate kernel startup/storage initialization, not another USB logger trial.
- Kernel producer sequence2+ with attributable printk: kernel/storage recorder and
  post-return retrieval observed; inspect actual contents before any acceptance.
- Missing/invalid control or immutable-prefix mismatch: stop, no pass or automatic
  retry; inspect the exact storage/collection failure before further action.

USB logging remains an additional available kernel/userspace channel. The main
result does not depend on USB enumeration, live capture or a diagnostic TTY rule.
This host procedure uses the persistent-only supervisor; it collects after actual
recovery. No full-log, early-crash or failed-load-retention pass is inferred from
source, VM, host control or normal return.346/344/348 remain open.

After explicit approval of this exact image/new hardware-write behavior/rollback
and owner availability, all work is one trip:

1. At the desk freshly recheck hashes/tools and original fullp5/p6. Write only full
   p5 once with a fresh receipt, require exact full readback and unchanged fullp6.
   No write retry or recovery write. No diagnostic TTY rule is installed.
2. Run installed-candidate persistent supervisor preflight. Arm once and confirm
   running before the owner leaves;600s travel budget, no automatic boot command.
3. In TWRP select Reboot→System once; decline an installer prompt only if shown.
   Wait the full90seconds from selecting System regardless of Amazon/black screen.
   Bands may be noted if seen, but are not required for retained-record collection.
4. Unplug USB. Hold only Power for40seconds even if black. Release, wait5seconds,
   reconnect the same cable/port without other buttons. Do not repeat this sequence.
5. Wait180seconds. Leave TWRP/special menu unchanged and return to the desk to report
   the final screen. Unexpected/no return: stop/report, no improvised reset/menu.
   The supervisor has a90s initial guard and900s manual reconnect window, at most
   one90s original FACTORYM helper,30s metadata readiness and full collection once.
6. At the desk verify actual recovery and use the read-only collector: identity/
   aliases/fullp6, exact immutable p5 prefix/seed, best nonce-bound record, private
   full post-trialp5/hash. Distinguish preinstalled host control from kernel output.
   If the initial collection fails, stop and diagnose; no automatic read/write
   retry. A separately verified fresh read-only collection can supply rollback.
7. `restore_retained_trial.py` validates that independently collected image/hash.
   Default is read-only fresh device preflight. Explicit approved restore writes
   exact full originalp5 once with fresh receipt, fullp5+p6 readbacks/RAM cleanup.
   Leave TWRP running, no reboot. Retain private logs and original backups; older
   host preparation remains tracked without disrupting authorized ADB.

No new physical operation is authorized by this document or previous approvals.
Public receipt: retained-candidate-result.json. Private concrete commands are
lab-log-trial-5/private/execution-private.json; no host/selectors/raw records public.

### Exact earliest-entry candidate6 — complete physical review, UNARMED

This replaces the old late, DT-gated checkpoint with a call as the first
`primary_entry` instruction, before boot-argument/page-table/exception-level setup.
Kernel run41583240596 succeeded at7b519b0619e6633194bfbc15515ab773880561a6 and
ACKd9318bdb4c34e8b2d997b4f67ced56b120b22b87. All retained hashes and gzip roundtrip
pass. The actual Image first instruction calls the probe; all296 probe bytes and
its eight-second literal match the independently emulated EL1/EL2/EL3 code.
The20s enforcing VM passes, with framebuffer addresses backed by virtual RAM;
this does not establish physical display, timer, storage or kernel entry.

Exact full16,777,216B candidate6 SHA256:
8d3729e6869371ba80aa2da6e1c6d29dbbf1e84ba5ed6b431f1a66354141be16.
Image16,912,896B SHA34353b23cfbfa3f28a0a99283583ceb5126d5cafe159231ac58546bf63c7c64f;
gzip7,252,168B SHAa43e1eb0bff30f7859b82915f48bd366b4a8ee66f13da0c51fa772198fddeb18.
Runtime17,432,576B, entry40000000/end410a0000; payload7,297,024B precedes15MiB.
Initrd43480000, tags48000000/1MiB, DT staging45000000 and reservations unchanged.
Fresh component13 init52,800B SHAd3b956d6858e1fc5b871a96412b37fb607e7f4b4f71c313dbdaf77e70857d4d7;
initramfs13,687B SHAe304b28e2bf0f9eaebe3b22c29c54acbc8b0260104693429a4f6931d19e188af.
Own nonce-bound DT27,376B SHA104c4015fc8ab9389b8572c741b003486c908a2e811e14b8c35aae464dc7bad3.
Independent header-ID/gzip/DT/initramfs/padding/seed/control checks pass.
Initial enforcing policy, persistent record format and storage prerequisite remain
as reviewed for candidate5. Fresh tools/assets/unused receipts staged; read-only
actual TWRP/aliases/full originalp5+p6 and rollback hashes pass. Nothing armed.

**New physical behavior:** with MMU off, the earliest probe writes only the
corroborated framebuffer allocation98600000..991b8000, alternating64KiB opaque
black and EL1-white/EL2-green/EL3-magenta bands. Cache-on entry cleans this exact
span to PoC with validated line size. It preserves entry arguments/x18/SP and
continues boot after eight architected-counter seconds for valid frequency.
MMU-on entry skips painting. Invalid frequency skips dwell; a finite iteration
budget prevents an endless stopped-counter loop but has no calibrated wall bound.
Counter access or physical memory assumptions can fail on an incompatible handoff.
EL3 color is diagnostic only, with no security transition or workaround.

No watchdog/reset/thermal/security/credential register writes are introduced.
An external watchdog can reset during this pause; no promise of delaying that reset
is made. A visible unique pattern establishes this probe executed and reports EL.
Absence or a timing change alone remains inconclusive because scanout, timer access
and early handoff are not yet physically qualified. This trial does not deliberately
panic or halt. Normal eMMC initialization and bounded persistent slot writes remain
active; errors could prevent boot/return or damage data despite software bounds.
Backups do not guarantee recovery access. No kernel-record acceptance from control.

After explicit approval of this exact image, framebuffer/cache/dwell behavior,
retained storage behavior and full-original rollback, and confirmed availability:

1. At the desk recheck current tools and full originalp5+p6. Guarded fullp5 write
   once, exact readback and unchangedp6; no retry/recovery write/reboot command.
2. Run postwrite persistent supervisor preflight; arm once and confirm running
   before owner leaves,600s travel. No diagnostic TTY rule or live USB dependency.
3. In TWRP select Reboot→System once; decline installer only if one appears. Watch
   for white/green/magenta-and-black bands and note color. Wait the full90seconds
   regardless of Amazon logo, bands or black intervals; do not infer off from black.
4. Unplug USB; hold ONLY Power40seconds even if black. Release, wait5seconds,
   reconnect same cable/port without buttons. Do not repeat the sequence.
5. Wait180seconds, leave TWRP unchanged and return to desk with observed pattern/
   final screen. Unexpected/no return: stop/report; no improvised reset or menu.
   Supervisor uses90s initial guard,900s reconnect window, one90s original helper,
   then30s metadata stability and full collector once. No automatic retry.
6. Verify actual recovery and collect private currentp5, exact prefix/seed/fullp6
   and nonce-bound record. Host controlseq1 remains preinstalled; only attributable
   kernel producerseq2+ establishes a kernel record. Initial collector failure
   stops; separately reviewed fresh read-only collection can supply rollback.
7. Fresh read-only restore preflight binds independently collected current hash;
   explicit approved restore writes full originalp5 once, verifies fullp5+p6,
   cleans RAM upload and leaves TWRP running without reboot. Preserve private logs.

No firmware operation is authorized by this document or prior candidate approval.
Private commands: lab-log-trial-6/private/execution-private.json. Public receipt:
entry-delay-candidate-result.json.346/344/348 remain open pending physical evidence.

### Actual candidate6 outcome — complete, original restored

On4 November2026 the owner approved this exact trial and confirmed availability.
One guarded candidate write/readback and one arm completed. Owner saw no colored
bands and TWRP returned after about90s or slightly longer without manual power-off.
The original return helper launched once/exited0; do not infer spontaneous return
or reset cause. Initial collection failed ValueError; the separate prepared
read-only collection passed and recovered only preinstalled HOSTCONTROLseq1/85B.
Fullp5 was unchanged candidate6. No kernel entry or storage-writer pass follows.
Approved full originalp5 restored once/fullp5+p6 readbacks/RAM cleanup verified;
TWRP left running/no reboot. Nothing armed or physical action pending. Candidate6
approval is consumed; no retry/rearm. Public result: entry-delay-trial-result.json.

### Trial6 unblock audit — exact loader and collection boundary

The read-only named LK alias resolves to /dev/null in TWRP. A bounded primary-GPT
read uniquely identified the lk partition; its524288B readback contains the exact
485988B original-package LK prefix, SHA7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056.
No firmware/device write occurred. The old4ca0cca7 OTA binary was not substituted.
`audit_trial_loader_contract.py` pins actual instruction anchors/call targets and
candidate6 SHA, verifies normal-mode0 dispatch, Android component digest, bounded
gzip output, final aligned FDT suffix and entry/DT SMC forwarding. Compressed
staging45000000, output40000000 and actual decoded16,912,896B fit the selected
28MiB capacity/42000000 stack boundary. DT suffix27376B is the last FDT magic in
the bounded search. Root versionhvt matches retained metadata. No concrete package
mismatch was found. These are conditional machine-code/byte checks, not execution.
See trial6-loader-contract.json; no kernel rebuild or unchanged trial follows.

The initial collector receipt discarded the ValueError message and failed check.
Exact original/candidate/nonce/returnedp5/recovery-byte replay passes with modeled
valid identity/alias responses for both fresh output paths. It does not reproduce
or explain the historical transport failure; those original failing responses
were not retained. The collector now emits safe stage/type/reason codes, including
alias mismatch versus full-partition read length versus digest mismatch; supervisor
receipts retain them. No retries, extra reads, weakened validation or physical
readiness claim were added. Failure injection verifies one read at most/no writes
and no private transport text in the error. See trial6-collector-diagnosis.json.

**Next implementation decision: loader-owned observations, before another kernel
candidate.** Required discriminators are (1) chosen normal/recovery mode, (2) actual
redirected boot_x header/body reads, (3) reaching the last LK→SMC branch with entry
and DT arguments. A fixed firmware-rendered marker would use existing video_printf
at4bd44b3d, not new kernel framebuffer/USB/storage initialization. Final selected
BL at4bd3e524 targets4bd3de68, which forwards to SMC at4bd3c98c/function82000200.
A proposed observer must preserve r0-r3/SP/LR and replay that exact branch, never
change bitness/security/reset/watchdog or perform additional storage writes.
Each marker would prove only that loader checkpoint, not kernel entry. No dwell
or timing-only success criterion is selected.

This is a source-design decision, not an admitted firmware operation. Before
creating a runnable observer image, prove resident code/data/BSS ownership and
space, exact archived payload equivalence and all branch targets; emulate argument
preservation and reject altered inputs. Zero padding alone is not free space.
The archived boot.payload embeds a modified LK copy (eight pointer bytes differ),
so changing the standalone lk partition alone is not a justified instrumentation
route. Do not patch either chain copy, boot_amonet, recovery_amonet or bootloader
partitions as an experiment. Any eventual changed bootstrap procedure needs a
complete exact rollback/review; none is currently ready or armed. This prerequisite
stays within346; no broader unlock, fastboot or microtrace audit is reopened.

### Resident payload audit and concrete checkpoint sites — 4 November 2026

The pinned original boot.payload SHAe10fdf77 contains the resident code at file
0xa00, linked at0x4bcff000. Embedded LK begins with its MTK prefix at file0x1800
(runtime0x4bcffe00); its executable follows atfile0x1a00/runtime0x4bd00000. The
embedded LK differs from original-package LK only in the eight known pivot bytes.
Initialized resident bytes end at0x4bcffb84, followed by four alignment bytes and
six live64-bit globals: recovery_x:b88, boot:b90, misc:b98, lk:ba0, boot_x:ba8,
recovery:bb0 (offsets from0x4bcff000). Observed BSS ends at0x4bcffbb8. The remaining
584 zero bytes before the LK prefix are a bounded candidate span, not admitted
injection space; do not reuse the earlier636-byte zero-tail estimate as free RAM.

`scripts/audit_resident_loader_payload.py` pins the archive member and cached
source hashes, then executes the actual archived ARM/Thumb instructions in Unicorn
2.1.3 with modeled firmware services. Nine mode/flag cases and twelve read cases
passed, including missing boot_x fallback, normal/recovery redirects atbase/base+800,
nonmatching+1000 and high64-bit offsets, return value, callee-saved registers/SP,
read-only hook behavior and BSS values/write boundary. Existing MISC flag writes
are modeled only; no tablet service is called. Source behavior agrees within these
cases. The archive has no original ELF/map/compiler provenance; compiler-level
byte-for-byte source equivalence is NOT established. Use the pinned archived binary
as the observation baseline rather than substituting a rebuilt original.

The next observer now has three specific design sites:

- **Selected mode:** resident+0x330/runtime0x4bcff330 has `00f001fa`, the BL to
  resident printf for the existing `g_boot_mode %u` message. A reviewed direct call
  to existing firmware video_printf can expose the selected mode before app entry;
  it needs no new resident data or reconstructed compiler layout.
- **Actual read arguments:** resident+0x72/runtime0x4bcff072 has `204b3046`
  (`ldr r3` of the original_read pointer address, then `mov r0,r6`). This shared
  continuation reaches the original reader after redirect selection. A future
  trampoline must report the selected64-bit offset from originalSP+16/+20,
  preserve the original stack arguments/registers/flags, replay those four bytes,
  and return to+0x76. Do not replace the two-byte BLX at+0x80 with an oversized
  branch or report temporary comparison registers as the selected offset.
- **Final handoff:** original LK code+0x3e524/runtime0x4bd3e524 has `fff7a0fc`,
  the BL to0x4bd3de68. A future checkpoint must preserve entry/DT arguments and
  original LR, then tail-forward to that original target. It proves reaching LK's
  handoff site; it does not prove the secure monitor entered the new kernel.

Before packaging any observer, assemble only analysis stubs and verify exact
register/flag/SP/argument replay, bounded span, branch encodings and cache visibility
with positive and negative emulator controls. Preserve every other archived byte,
including original security/boot-mode behavior; add no security/reset/watchdog or
persistent writes. No observer image, new firmware write, trial or physical action
is admitted by this audit. Report: resident-loader-payload-result.json. The Mac
emulator failed in host cache initialization; controls instead used the exact
payload already present on the authorized lab host, with no firmware export.

### Exact normal-only loader observer — trial7 review

**Prepared and unarmed.** This changed procedure writes a previously untouched
bootstrap payload range and therefore needs new exact owner approval and explicit
availability. Prior candidate6 approval was consumed by trial6. This review does
not admit a write or arm; all preparation below was read-only or offline.

**Exact bundle.** The observer sector image is492,544B, SHA256
`6a34b1a55d3b9c6de8e87e21f8b6cc3eaef18576583f66750ef6e012d0d1c10c`.
Its280-byte Thumb stubs occupy0x4bcffbb8..0x4bcffcd0, leaving304 bytes before the
embedded LK prefix. Original payload sector SHA is
`4c6f355c735b9302b0d421ef38f94a9974214d531fa974a41edd8132af7ac092`.
Only four payload-file spans may change:0xa72/4B,0xd30/4B,0x15b8/280B,
0x3ff24/4B;266 bytes differ. All remaining payload/sector-tail bytes, live globals,
headers, original pointer pivots and existing security/boot behavior are retained.
No new watchdog/reset/security or storage operations exist in the stubs.

The existing normal kernel candidate6 is deliberately reused byte-for-byte:
SHA8d3729e6869371ba80aa2da6e1c6d29dbbf1e84ba5ed6b431f1a66354141be16.
No kernel rebuild, new DT/initramfs, or speculative seventh kernel variant was
made. A new full installation resets its retained slots to the known HOSTCONTROL
seed before this changed-loader trial. Its existing nonce is not represented as
new; fresh trial7 operation/output/receipt paths are unused. No old kernel record
was observed in that candidate's prior trial. New observer plus this exact kernel
is the approval unit; previous kernel approval is not reused.

**What the checkpoints prove.** Normal mode0 adds the existing `g_boot_mode %u`
message on the firmware console, the actual selected64-bit read offset as
`LK read high:low`, and `LK handoff entry=... dt=...` immediately before the original
handoff wrapper. The read stub uses originalSP+16/+20, replays the overwritten
ldr/mov and preserves caller state; mode retains original UART printf; handoff
retains the original LR and tail-forwards to0x4bd3de68. All additional display calls
are bypassed when mode is not0, preserving the existing recovery/fastboot display
work. Reaching the handoff checkpoint does not prove SMC completion or kernel entry.
No pattern, time-only change or absent marker is an acceptance signal.

**Validation completed.** Apple clang21 assembled a relocatable ARM analysis
object with no unresolved relocations.54 hostile-service preservation/gating cases
plus4 full-main,12 full-read-hook and1 real-final-call fixture passed in Unicorn:
r0-r12/LR, arithmetic flags includingGE/Q, original stack arguments and SP are
preserved, with video-call SP aligned at both incoming alignments. Recovery2 and
fastboot99 make no added video call. Five altered-anchor/tail/branch controls and
three package rejection controls passed. Six guard tests cover GPT CRC/overlap,
changed state after RAM upload, exact one-span copy, and uncertain-write no-retry.
Existing collector/rollback and lifecycle controls also pass.

Original ROP cache coverage includes the entire new resident span; the existing
main cache-clean call covers the modified embedded LK call site. These are checked
address/instruction contracts, not hardware cache/display qualification. New display
calls can add latency or hang on real hardware; no watchdog deadline extension or
reliable rendering is promised. Bypassing added display calls in recovery reduces
risk but does not prove an independent physical return from a broken bootstrap.

**Actual current originals and target.** TWRP recovery/douglas identity, full original
p5/p6 hashes and selected USB identity pass. Both installed bootstrap payload prefixes
exactly match the archivede10fdf77 bytes; headers and full962-sector payload ranges
are backed up privately on both lab and controller. Only each512-byte header and
source-defined payload range was read; no full115MiB bootstrap container or userdata
content was read. TWRP aliases boot_amonet/recovery_amonet point atp17/p18, whose
GPT names areboot/recovery. Primary GPT header/table CRC and exact geometry pass; the write guard also
requires the kernel partition start/size metadata to match those GPT entries.
The p17 payload range atsector223223,962 sectors does not overlap p5, p6, p18 or
any other GPT entry, including userdata. Recovery bootstrap and both headers must
remain exact originals throughout. No GPT, preloader, LK partition, security
partition, recovery or userdata write is part of this procedure.

**Prepared execution, after new approval and availability only:**

1. At the desk with TWRP already running, execute the fresh read-only bootstrap
   preflight, then one guarded observer-range installation. The guard requires
   original current hashes, an exclusive receipt, verified tmpfs upload, a second
   complete preflight, one file-to-p17 dd atseek223223/count962, sync, full range/
   header/p5/p6 readbacks and verified RAM cleanup. No reboot. If it stops, do not
   retry or arm. If normal-kernel installation cannot proceed after a verified
   observer install, the prepared current-hash-bound original bootstrap restore
   is the bounded abort action while TWRP remains running.
2. Install exact candidate6 once using the existing reviewed fullp5 guard. Run both
   bootstrap and normal-candidate postwrite preflights. Only then arm the fresh
   trial7 supervisor once when the owner is available. No helper launches at arm.
3. One owner trip: use TWRP Reboot/System, note the last visible checkpoint and
   approximate timing, wait90 seconds. If not already returning to recovery, use
   the reviewed disconnect/Power40s/off/wait5s/reconnect sequence once. The existing
   original FACTORYM helper may launch once only; no StageA/unlock/retry. After
   reconnecting, wait180 seconds for the return. Return to the desk and report the last visible text and recovery state. Do not add timing
   experiments or intentional failure injection.
4. Collect retained p5 once after actual recovery validation. If the supervisor
   stops, use the independently prepared read-only collector, preserving its safe
   stage/reason. Preserve all private receipts and attributable record bytes before
   rollback. HOSTCONTROL alone is not a kernel/log qualification.
5. Restore original p17 payload sectors once through `restore_loader_observer.py`,
   bound to the validated supervisor readout (or independent manual readout after
   a supervisor stop) and exact observer current hash. Separate prepared command
   paths cover both outcomes, including a changed kernel-record tail. Then restore original fullp5 once through the existing validated
   readout/current-hash guard. Both operations verify unchangedp6 and original
   recovery bootstrap/headers as applicable. Leave TWRP running; no final reboot.

Private fresh commands are staged underlab-log-trial-7/private/execution-private.json.
No install/restore receipt exists and no write, arm, supervisor or helper was run.
`scripts/guard_loader_observer.py` defaults to read-only; its explicit write mode
and the restore wrapper are not authorization. Any identity/hash/alias/GPT/staging/
readback error stops the procedure without retry or reboot. A bootstrap failure
could obstruct the ordinary return path; an untouched recovery copy and emulator
success are not a hardware recovery guarantee. Original full unlock/BootROM stages
remain prohibited. #346/#344/#348 stay open until their actual runtime gates pass.

### Actual trial7 result — originals verified, no further trip

Owner approved the exact observer/kernel bundle and availability. Observer and
normal candidate were each installed once, verified, and postwrite checks passed;
one fresh supervisor was armed. Owner reports somewhat different lower-left
console messages, approximately about mode and reading, but cannot recall exact
strings; explicitly confirms TWRP menu. This is consistent with changed loader
output, but no exact checkpoint/address/last handoff or kernel entry is qualified.
Do not infer the manual power sequence, timing, spontaneous return or reset cause
from “same outcome.” One original FACTORYM helper exited0.

The supervisor's stopped collection now has a precise stage:
full_recovery_read_and_hash / partition_read_size_mismatch. The failed output's
actual byte count was not retained, so the transport/root cause is still unknown;
this does not retroactively diagnose earlier trials. The separate prepared
read-only collector passed identity/aliases/fullp6/prefix/seed: HOSTCONTROLseq1,
85B only, no invalid slots or kernel record. Full posttrialp5 exactly matched the
installed candidate6. Reader/format/control remain useful; kernel entry/storage
writer/failed-load-log acceptance do not pass.

The bootstrap restore precheck correctly stopped BEFORE a write because the range
no longer matched the observer. A single preserved readback instead matched the
EXACT ORIGINAL sector image, with original recovery bootstrap too. Offline audit
of unchanged fullp6 found /fix-bootpatch.sh SHA07f4353c, called by /amonet-fixup.sh:
when normal bootstrap header/payload differ, it copies the recovery header/payload
back to normal bootstrap and emits /tmp/restore_bootpatch.log. This boot's capped
status file exactly matched that restoration message. This explains the verified
original state as existing TWRP repair, not an agent rollback or unexplained
corruption. TWRP's own script copies its header and payload span; the agent issued
no second bootstrap write. Do not disable that repair or modify recovery bootstrap
to retain an observer. Future rollback plans must recognize an already-original
bootstrap and verify it without a redundant write.

A complete read-only already-original guard passed. Then approved fulloriginalp5
was restored once via independently validated readout/current hash, fullp5+p6 and
RAMcleanup verified. TWRP left running/no reboot; no active supervisor/helper,
no arm or physical action pending. Private trial7 archive and later repair-proof
supplement have matching lab/controller hashes. Public loader-observer-trial-result.json
and twrp-bootstrap-repair-source.json retain provenance and limits.346/344/348 open.

The next engineering contract needs attributable durable loader-stage/read/handoff
evidence using the working mailbox format/reader, with a distinct loader payload
tag that cannot be called a kernel record. Approximate screen recall is not enough
to locate the remaining boundary. First design and review the exact normal-only
writer/guard/recovery contract; no unchanged trial or new kernel build is selected.

### Durable loader checkpoint integration — analysis result, not trial admission

The C producer and reader now implement mode/header/body/pre-handoff records in
VLOG0001 with a distinct loader tag. Exact actual selected offsets/arguments are
metadata; record writes remain pinned to the admitted p5 mailbox. Native10,
collector8, existing codec5 and linked ARM13 controls pass. See
[core result](../../evidence/independent-recovery/loader-checkpoint-core-result.json)
and [source/reproduction](../../projects/firetabs-android/loader-retained/README.md).

The actual recovery eMMC capability read reports a1MiB enabled cache. Its temporary
read-only debugfs mount was removed; raw capability bytes remain private. No
physical cache command was issued. Archived SWITCH instruction replay shows its
timeout returns zero like success, so this routine alone cannot certify a flush.
[Exact replay result](../../evidence/independent-recovery/loader-switch-audit.json).
The timeout boundary case reduces its loop counter explicitly; other command and
status callbacks are models, not runtime hardware evidence.

Physical readiness is false: implement independent bounded completion/error
checking, bind exact immutable firmware/card/target callbacks, and establish owned
code/context/stack lifetime and hook replay/cache visibility. The3595B core plus
context does not fit the old584B gap. No guessed free RAM or no-op flush may satisfy
these gates. Preserve TWRP repair/recovery and original rollback. No new install,
arm, helper, kernel build or owner trip is selected by these analysis results.

Checked completion adapter source is now implemented in loader-retained/mmc_flush.c:
one raw CMD6 with retry0, fresh CMD13 ready/TRAN, conservative status errors,
bounded polls and elapsed-time rejection.9 native and9 linked ARM controls pass;
ARM replay uses exact archived LK command wrapper with modeled driver/clock.
[Adapter result](../../evidence/independent-recovery/loader-flush-adapter-result.json).
This closes the source-level false-success handling, not hardware persistence.
Real driver timing/clock/card/target bindings and owned memory remain prerequisites.
No physical command or new trial is selected.

Integrated module source now connects the writer to the checked adapter. Four
native controls pass, including command-boundary failures and repeat-init refusal.
Hidden PIC builds remove fixed-address references on tested paths; separate
core relocation controls execute at three modeled bases. The4307B integrated
module and8584B state use a dynamic allocation route, not the old584B gap.
Exact archived memalign/allocator controls demonstrate modeled owned regions,
null-on-exhaustion and invalid-alignment behavior. This does not measure the
actual heap's initialization/capacity or qualify a physical address/stack.
See loader-checkpoint-relocation-result.json, loader-allocator-result.json and
loader-status-sideeffect-result.json. A bounded load/integrity/cache bridge and
real firmware bindings remain required. No physical trial is selected.
