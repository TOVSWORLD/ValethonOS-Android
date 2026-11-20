# Integrated Android T1 candidate and rollback checklist

## First attended attempt — November20

The approved candidate was installed in one system-image pass, verified in full,
then boot was written and verified. One test boot was requested. Owner observed
a Linux console with a kernel panic; no usable Android UI or authorized Android
ADB was observed. Cause/initialization stage are not established.

After the five-minute window, the original return helper ran once and succeeded.
Owner reported TWRP was already present on returning; a manual Power sequence was
not reported and the reset mechanism is unproven. Actual post-return boot/system
digests and unchanged original recovery pass. Candidate is retained in TWRP;
original backups remain ready. Scope android-t1-1 is consumed: no automatic retry.

See android-t1-runtime-result.json. Existing retained console data do not identify
the fresh panic. Preserve the owner's panic photo if available, identify the exact
failure, then prepare a correction. Reuse the verified system image when possible;
do not repeat a full build, full system write, or old logging proof without cause.
Preparation details below describe this consumed attempt, not permission to rerun.


This prepares one grouped Android session under docs/development/STAGED-TEST-PLAN.md.
It is not installation authorization or evidence that unfinished images pass.
The complete image build and installed-output audit pass. No standalone display, cube or logging test.

## Finish T0 when artifacts exist

1. Record exact published source plus applied repair hashes, locked platform manifest,
   qualified kernel Image/config/DT and graphics ELF/package hashes. Retain failed
   graph attempts. Verify system.img, ramdisk.img and module-info.json are from
   that same build; run check_android_product_contents.py with built aapt2.
2. Check actual installed WebView, readiness app, launcher and com.android.adbd APEX.
   Retain enforcing policy/VINTF build results and filesystem build evidence for
   the configured 16 MiB reserve. Expanded image size must fit existing p14;
   sparse file length is insufficient. Current data profile remains volatile.
3. Assemble an Android boot-v0 container through the qualified LK entry path,
   reusing the completed kernel and known working display/touch/GPU DT resources.
   Verify compressed bytes, loader decode bound, runtime Image footprint, actual
   ramdisk compression/unpacked bound, addresses, memory exclusions and reserved
   regions. Do not assume the standalone graphics packer's 7/30 MiB ramdisk bounds
   fit Android, or silently relax them. Android ramdisk layout is not yet measured.
4. Retain a private hash-bound candidate manifest, boot/system images, original
   rollback images, device selection, original recovery proof and scoped installer.
   Exact install/return commands and bounded observation window are finalized from
   that measured package before requesting a tablet session. A build-host system.img
   is not yet a qualified tablet boot image.

## Prepare rollback before any device write

In original TWRP, identify the selected tablet and independently verify retained
original boot/recovery against the existing baseline. Before replacing p14, obtain
and verify its full original backup, partition capacity and hash. Preserve original
userdata and recovery; do not format, repartition, adopt encrypted userdata or write
recovery. Verify complete candidate and rollback transfer hashes on the lab.

The concrete installer must allow only the reviewed original boot and system
partitions, reject a mismatched device/partition/image/hash, and support one final
return to original TWRP followed by the agreed restore. Do not reuse an old trial's
identity, authorization or successful receipt as permission for this candidate.

## One owner-observed T1 session

Say “watch now” immediately before the integrated boot. Expected sequence is Amazon
loader, Valethon interruptible animation if Android graphics reaches it, then usable
setup/home. Animation is activity, not a measured completion percentage. Keep the
owner's movement to/from the lab in mind; no short-lived interaction window that
expires before they can reach the tablet.

On the same boot check display/backlight, touch/drag, home/app navigation, Settings,
keyboard input, and the manually launched Valethon Readiness nine-tile/HTML test.
Use the large UI rather than requiring tiny kernel text to be read. Source-ready
extra checks may share this session; unresolved radio/audio/suspend are not assumed
ready and do not add standalone boots.

Using already authorized ADB, collect read-only identity/boot-complete properties,
`getenforce` (must be Enforcing), authorized USB/ADB state, compositor/provider
identity and bounded logs. `adb shell am start -n
com.valethon.readiness/.ReadinessActivity` launches the ordinary readiness app.
No permissive-policy workaround or new diagnostic proof gate.

After the agreed window, execute the prepared return once, verify original TWRP
and the required exact installation/rollback state, and record each checkpoint as
pass/fail/not_run. Main milestone requires usable Android UI, display/touch,
Enforcing SELinux, authorized USB/ADB and verified recovery. A build, animation,
app launch or successful restore alone does not complete it.

## Current prepared package — November20

The compiled system/ramdisk and retained Android-support kernel are packaged.
Existing original-loader roundtrip and RAM checks pass. The boot payload is
10,909,696bytes inside the original16MiB partition; Android cpio expands to
2,683,392bytes and is re-encoded losslessly for the working XZ path. Only chosen
boot arguments/initrd/identity fields change; hardware nodes and reservation map
are unchanged. Header and DT select hardware douglas and enforcing SELinux.

Official simg2img independently matches the prepared raw system image. Read-only
e2fsck returns0; actual free space522,743,808bytes exceeds the16MiB margin.
The original system partition has a full independently verified backup and a
second verified local copy. The selected original TWRP boot/recovery/system
read-only preflight passes. Exact candidate identities and source checks are in
evidence/android-integration-source/android-t1-preparation-result.json.

The guarded installer stages8MiB chunks in verified recovery tmpfs, writes only
the exact existing system partition, verifies its full digest, then writes boot
last through the existing checked boot writer. An incomplete system transfer
cannot advance to the boot write. Recovery and original userdata are excluded.
Owner authorization binds exact boot/system/backup, nonce, runner/support files,
case manifest and selected return configuration. Default preflight writes nothing.

One boot is separate from installation so the owner receives “watch now” first.
Keep USB connected through installation. Observe actual animation/setup/home,
touch/drag, keyboard, readiness app and authorized ADB/Enforcing state. The return
helper cannot arm until the five-minute boot observation has elapsed; it admits
only one original recovery-entry call on the selected physical port. Return once
to original TWRP and verify candidate/recovery state. Retain candidate there for
follow-up if successful; exact original boot/system rollback is prepared if needed.

Remaining: owner availability and exact test authorization, the physical Android
boot/UI/Enforcing/authorized-ADB checkpoints, and final recovery verification.
No physical Android pass, automatic rollback, extra boot or new full build is claimed.
