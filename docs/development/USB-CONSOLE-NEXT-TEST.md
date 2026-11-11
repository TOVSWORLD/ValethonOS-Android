# USB console: next hardware test

> Historical test: completed November 10, 2026. Source boot passed; the target
> console did not appear after the one jump. Owner-assisted return to Android
> home and original boot/config/recovery were verified. That approval is consumed.
> [Actual result](../../evidence/independent-recovery/usb-console-jump-runtime-result.json).
> [Current source-plus-target capture test](SOURCE-USB-HANDOFF-NEXT-TEST.md).

November 10, 2026. USB kernel-marker→ACM→host capture already passed on the
working 4.9 kernel: 390 bytes received and synced. The initial host permission
failure was fixed; ADB-only and normal adbd restored in both tests. This is an
actual working transport, rather than another proposed retention mechanism.

The console-enabled native kernel now builds and passes linked checks. Source
boot package SHA256:
`d1b5fc85a5a560eab70a032ac11b88b0090b8ff98f5ff1af8960cc87b8746c26`.
Image SHA256:
`e74878db3abb4bca4acc18e312d66ac8648a9261ac6dff216af387676b38ecff`.
Resolved config:
`865d9beeb5c8c49af47aea818b341e48cbbd84f7669c0cccbc589b60d1699b31`.
Release remains exactly the installed 4.9.337-g72940eb733af.

Only USB_G_SERIAL, U_SERIAL_CONSOLE and selected USB_F_OBEX change from the
previous hardware-booted native config. Native syscall104, final CPU gate and
namespaced orderly reboot route remain linked. No watchdog or security change.
The original ramdisk, appended DTs, source boot arguments and load addresses stay
unchanged. Default serial binding is disabled so source Android retains ADB.
Target binding requires explicit `g_serial.ft_bind=1` plus an exact 32-hex
`g_serial.ft_trial`, and `console=ttyGS0` enables the kernel's existing console.

## One approval covers these two stages

Owner approval and availability are required for the complete bounded sequence.
No additional approval is needed between stages if all stated checks pass.

1. **Temporary source boot.** Use the profile-bound wrapper around the previously
   exercised one-boot/restore runner. Verify original full boot/config/recovery,
   install the exact source candidate once, verify readback, request one ordinary
   reboot, verify new config and empty kexec load state, and restore/verify the
   original full boot on flash immediately. Recovery is never written. The new
   kernel remains in RAM. The live read-only preflight already passed with zero
   writes/reboots and normal ADB restored.
2. **One USB-captured diagnostic jump.** Only after successful source boot and
   original-flash restoration, read fresh source FDT and System RAM metadata.
   Rebuild the target bundle with this exact Image and original ramdisk, one fresh
   nonce, and only two chosen-property changes: trial attribution and the exact
   USB console bootargs prefix. Preserve the original bootargs suffix, all other
   properties, memory reservation map, initrd addresses and pstore region. Check
   every segment against current System RAM and reserved regions. Bind the
   generated manifest and load-client hashes into the child authorization under
   this approved policy. Do not use the offline preview for device loading.

The load-only client source/ABI is unchanged; the preview compiled and passed
12 host controls with the new exact segment sizes. Generate/validate the final
client for the fresh manifest before loading. Host receiver arms on the same
physical USB port, accepting only the source-pinned builtin CDC ACM descriptor
0525:a4a7. Open privileges are limited to that character node; capture stays
unprivileged. Load once from CPU0, confirm native loaded state, then request
`reboot,valethon-kexec` once through Android init. No direct reboot syscall.
No boot/recovery writes occur in this second stage.

## What the receiver proves

The existing kernel console can replay buffered kernel messages when USB comes
up, without an Android logging daemon. It cannot transmit before its hardware
and driver initialize; a USB outage during shutdown/transition is expected.
The host keeps up to 2MiB privately, requires the fresh target nonce either in
its g_serial checkpoint or controlled kernel command-line prefix, and records
partial bytes even if that marker is absent. Split-marker, wrong-trial, byte-cap,
disconnect and no-endpoint cases have real fd controls. Kernel entry/capture is
separate from a complete Android boot and from modern-kernel USB qualification.
The host sends no shell commands or input over the console.

## Return and stop conditions

The diagnostic target's legacy serial gadget owns the USB controller, so target
ADB is not expected. After the capture window, the owner may need to perform the
known physical return: unplug USB, hold only Power40seconds even if black, release,
wait5seconds, reconnect the same cable/port, wait up to180seconds and report the
screen. Original boot is already back on flash before the jump. Verify original
boot/config/recovery after return. Leave any recovery menu untouched.

A source-boot failure stops before stage2 and uses the existing bounded rollback
attempt/recovery-only helper; do not retry uncertain writes or reboot commands.
A target USB failure stops after five minutes, preserving partial capture and
requiring owner return. No automatic jump/reboot retry, pstore deletion or retained-
logging baseline test is included. Existing physical/driver operations can stall;
independent automatic failure recovery remains unqualified.

The read-only preview validates the layout against previously captured source
metadata and is explicitly marked offline-only; the jump runner refuses it.
Fresh runtime source metadata and fresh child hashes are required. This policy
allows those data-dependent fields under one approval; it does not authorize
substituting another Image or changing the reviewed builder/receiver code.

[Build, artifact retention, preflight and controls](../../evidence/independent-recovery/usb-console-build-result.json).
[Two-stage approval template](../../evidence/independent-recovery/usb-console-two-stage-authorization-template.json).
[Source-stage child template](../../evidence/independent-recovery/usb-console-source-boot-authorization-template.json).
