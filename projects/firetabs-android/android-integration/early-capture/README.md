# Combined early Android boot capture

This is one diagnostic retry of the first Android boot failure, not a new
standalone logging milestone. The original failure was an owner-observed Linux
console panic; its exact cause remains unknown. The installed Android system is
reused. Only the boot image changes; original recovery and userdata are excluded.

Three paths are combined:

1. A static AArch64 `rdinit=/valethon-preinit` wrapper runs before the original
   static ARM32 Android `/init`. It emits milestones and makes a bounded eight
   second attempt to forward the existing kmsg ring over USB. It does not require
   a host acknowledgement, mount a block device, change policy or replace Android
   init. Temporary proc/sys mounts and device nodes are removed before exec.
2. Builtin `USB_G_SERIAL` and `U_SERIAL_CONSOLE` register `ttyGS0` during Linux
   driver initialization. `console=ttyGS0` requests printk replay. Controller/PHY
   initialization and host enumeration remain prerequisites. The console uses a
   bounded FIFO/workqueue: panic delivery and complete log replay are not
   guaranteed. This diagnostic keeps the serial gadget registered; Android's ADB
   gadget cannot simultaneously own the UDC. ADB is not an acceptance condition
   for this diagnostic boot.
3. Builtin ramoops uses the documented `0x44410000 / 0xe0000` pstore subregion
   within the unchanged reserved 2 MiB RAM area. Record and console sizes are
   64 KiB. No guessed RAM address or new RAM carveout is introduced. Existing
   guarded boot-tail logging is seeded for this exact candidate/nonce and can
   save twelve snapshots at five-second intervals. Its records start at sequence
   two; the preinstalled sequence-one control is explicitly not kernel evidence.
   Snapshots are normal worker I/O, not an atomic panic handler.

TWRP has no working reserved-RAM `/dev/mem` access. Existing pstore/last-kmsg
interfaces therefore must not be assumed to expose this kernel's ramoops data.
The wrapper can transmit previous-boot pstore records on a later Linux boot;
`valethon.capture_readout=1` selects a collection-only mode that never executes
Android init. That is a separately identified boot, not an automatic retry.
Records require the previous candidate's identity. Firmware/reset retention and
that readout route remain unqualified. Boot-tail records are independently
retrievable from original recovery, with prefix/seed/nonce/CRC validation.

The offline packager preserves original Android cpio entries and hardware DT
nodes, adds only the wrapper, chosen arguments/identity, and a ramoops platform
node inside the existing reservation. It rejects unrelated kernel config changes,
modified artifacts and boot-tail overlaps. Existing original-loader roundtrip,
size/RAM checks and a networkless VM handoff check are required before staging.
VM handoff success is not tablet boot, USB or retention qualification.

`android_early_capture_device.py` defaults to explicit read-only preflight. Exact
case authorization binds image, nonce, selector, manifest, receiver, return config
and supporting tools. One boot write uses the existing full-readback writer; one
exclusive durable boot request prevents retries after uncertain transport. System
is hash-checked but never written. After at least five minutes, the original
FACTORYM helper may be armed once. Recovery readout preserves the full boot
privately, validates immutable prefix and bounded mailbox records, and checks
unchanged recovery/system. No original case is reused.

## Tablet result — November 20, 2026

One approved boot-only install/readback and one explicit boot request completed.
Owner observed repeated Amazon/black/Amazon cycles, then TWRP. The 300-second USB
receiver captured zero bytes without receiver errors. Recovery collection found
only the preinstalled sequence-one host control, no kernel-written snapshot.
Existing recovery retention interfaces contained no fresh trial identity.
Original TWRP return and unchanged recovery/system/immutable boot prefix verify.
This does not prove fresh Linux/init execution or establish a panic/reset cause.
The consumed attempt, private raw records and rollback are preserved; candidate
is left in TWRP. No automatic retry or collection-only boot was performed.
See `evidence/android-integration-source/early-capture-runtime-result.json`.
