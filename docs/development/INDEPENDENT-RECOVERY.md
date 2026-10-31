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
