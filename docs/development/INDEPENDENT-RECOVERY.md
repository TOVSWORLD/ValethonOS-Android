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
