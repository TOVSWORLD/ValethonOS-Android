> Completed successfully November 10, 2026. Original boot is restored on flash;
> native kernel runs in RAM. [Next: first experimental jump](NATIVE-KEXEC-FIRST-JUMP.md).

# Next test: temporary native kexec source kernel

Prepared November 10, 2026. No experimental jump has run. Failed-jump logging
qualification follows a failed experimental jump, per owner direction; it does
not block preparation or repeat the successful console-retention baseline.

The installed kernel has CONFIG_KEXEC disabled. The built candidate enables
CONFIG_KEXEC and CONFIG_KEXEC_CORE, wires the final MT8163 CPU-off gate before
relocation, and adds a PID1-only `valethon-kexec` orderly reboot target. The native
syscall table and final linked gates were checked. Generated C controls passed
13 CPU cases and 22 reboot-route cases. Android init's orderly shutdown route
can continue despite failed unmounts; successful filesystem quiescence is not
claimed. The running userspace binary's equivalence to the inspected Lineage18.1
init source remains unqualified.

Candidate full boot SHA256:
`43ac32df0cf0b8195e70b0bc596b9a9b33750d1a6a14305640ff05cf12501327`.
Original boot SHA256:
`08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e`.

The package preserves original ramdisk, both appended DTBs, header addresses
and command line. Bootloader acceptance is untested. The original component ID
does not match the standard Android SHA1 calculation; no signature validity is
inferred from repacking. Raw images and device metadata remain private.

## Exact owner-attended trial

Run `scripts/run_native_source_boot.py` with the private lab package and exact
current authorization. Its default mode is read-only. The completed live
preflight verified original boot/recovery/config hashes, RAM staging capacity,
and current aliases: boot→p17, boot_x→p5, recovery→p18, recovery_x→p6.
Only physical p5 is a write target; p6 is verified and never written.

The approved execution permits one candidate p5 write and readback, one ordinary
reboot, then one original p5 restoration and readback. On successful Android
return, verify the new config, changed boot identity, unchanged recovery and
empty kexec load state. Restore the original boot image on flash immediately,
leaving the native kernel running in RAM for subsequent jump preparation.
No experimental kexec jump, failure injection, extra reboot, recovery write,
pstore deletion or general log collection is included.

If candidate installation fails, attempt the one bounded original restoration
without rebooting. If Android does not return within 300 seconds, do not issue
another reboot. Restore only if normal ADB and identity guards are available;
otherwise stop for the owner to enter existing recovery. The existing
`scripts/restore_diagnostic_boot.py` recovery-only guards and original backups
provide the manual rollback path. A boot failure can require physical owner
action; software recovery is not guaranteed. Approval requires owner availability.
The approval is consumed before execution; no automatic repeat.

[Build and live preflight receipt](../../evidence/independent-recovery/native-kexec-handoff-build-result.json).
[Unapproved authorization template](../../evidence/independent-recovery/native-source-boot-authorization-template.json).

## History

The first preflight refused before writes because it expected obsolete recovery
alias paths. Read-only inspection established the current Android mapping; the
corrected second preflight passed. Both runs restored normal UID2000 ADB and
performed zero partition writes and zero reboots. Earlier build failures and
logging experiments remain in the existing worklog and issue history.
