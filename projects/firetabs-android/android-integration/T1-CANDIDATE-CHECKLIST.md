# Integrated Android T1 candidate and rollback checklist

This prepares one grouped Android session under docs/development/STAGED-TEST-PLAN.md.
It is not installation authorization or evidence that unfinished images pass.
The complete image build is active. No standalone display, cube or logging test.

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

## Not yet ready

Final image hashes, actual ext4 free space, ramdisk/container/RAM measurements,
original p14 backup verification, candidate-specific install/restore commands and
owner-approved test window await artifacts and preflight. Do not mark T0 or T1 passed.
