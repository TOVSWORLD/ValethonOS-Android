# Known-boot capture calibration — control 1

Issue346 / parent344 / PR453. This is the owner-selected recorder calibration,
after the complete modern draft produced no USB output or retained kernel record.
It supersedes the older prohibition on a separate control **for this exact known
boot stack only**. Historical trial8 and the failed modern draft remain held.

## What this test answers

Can the actual loader recorder write a fresh checkpoint to eMMC and can the actual
recovery collector retrieve it after a normal boot and manual return? The kernel,
appended DTs, ramdisk and entire declared header/image are the already-booting
original stack, unchanged. No new kernel is compiled and no old OS is installed.

A passing control qualifies this loader-to-mailbox-to-collector path. It does not
qualify the modern PID1 USB logger, a kernel-side writer, execution after the secure
monitor call, or the cause of a logo/black loop. A partial mode/read record is useful
evidence but does not pass the complete pre-handoff control. No record means the
recorder remains unqualified; it must not be reported as modern-kernel failure.

## Exact package

- Original full p5, 16,777,216 bytes:
  `08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e`.
- Control full p5, same size:
  `77d7453b3fde4764c3a8e8d9a29587ad5d8a2e726388ab411f80356147420a00`.
- Normal observer range, 492,544 bytes:
  `21a26da4e5c2baf29f46be3cd417d50abef4b314911775947bc231117be38851`.
- Original normal/return bootstrap range, same size:
  `4c6f355c735b9302b0d421ef38f94a9974214d531fa974a41edd8132af7ac092`.
- Recovery full p6, 17,825,792 bytes:
  `3c9bafcbfc4a0b12cb1a3f372af0cfd49ffec5b3e01a0b070465b49bd8435f11`.

All 7,796,736 declared original boot-image bytes are identical. The unchanged
9,216-byte PIC module occupies verified-zero padding at file offset12MiB; the
fresh loader-only nonce, prefix binding, seed and HOSTCONTROL fixture occupy the
reserved final1MiB mailbox. Original kernel and ramdisk contain no added nonce or
code. The loader descriptor binds the new prefix/nonce and exact p5/GPT/MMC target.

The normal p17 bootstrap payload range changes only previously reviewed console
spans/read-hook bytes and one embedded normal-LK pre-SMC call. The whole exact range
is copied once; unchanged surrounding bytes are included in that range. No normal
bootstrap header, return p18 bootstrap/header, GPT, preloader, standalone LK/security
partition or recovery image is written. Live resident globals are preserved.

The independent verifier checks actual component preservation, module ELF/blob,
all15 object relocations, descriptor fields, prefix/seed and changed spans.
Seven exact packed ARM controls and the original entry40080000/DT48000000 handoff
argument replay passed. Controller/storage, initialized heap, IRQ/CP15 effects and
prefix digest in that complete replay are modeled. Physical driver termination,
heap capacity, worst-case stack, cache visibility and durability remain unqualified.
The existing raw data driver can stall: bounded command completion does not bound
every data transfer. This is a calibration risk, not a claim about a prior failure.

## Deployment and observation protocol

1. Verify the private source/artifact deployment manifest and selected Linux lab
   device. Exact original p5, full p6, both bootstrap ranges/headers, GPT geometry
   and aliases must pass. No write on mismatch; no retry or alternate selector.
2. After exact approval and current availability, create the private authorization
   for this candidate/observer pair, five-minute minimum and automatic_return=false.
   Install normal observer range once, then control p5 once. Each operation owns an
   exclusive durable0600 receipt, RAM upload/hash, prewrite check, full readback and
   RAM cleanup. Verify the complete installed state before the owner boots.
3. Start the host metadata watcher once. It opens no TTY and launches no helper.
   It gives600s to reach the tablet, then observes330s after recovery USB departs.
   It never returns/restores/reboots the tablet when that interval ends.
4. First visit: TWRP **Reboot → System** once. Observe for at least five minutes.
   Report whether the familiar installed system appeared, the last screen, and any
   loop. Do not sign in, inspect account contents or change Android settings. Return
   to the desk before any manual return procedure starts.
5. If already in TWRP, use it directly. Otherwise, after the desk report and the
   measured five-minute minimum, explicitly start the original return-only waiter.
   Second visit: disconnect USB, hold Power40s, release/wait5s, reconnect once,
   wait up to180s, then return to desk. No new normal boot or test is started.
   One original FACTORYM helper maximum, bounded900s wait/90s execution. No helper
   launches at capture arm or from a boot timer. Helper failure/uncertainty stops.

Five minutes is a minimum observation window, not an automatic reset deadline.
The original installed system may access its normal existing userdata during boot;
the test tools do not mount, read or copy userdata/account information. The existing
baseline's security state is unchanged; it is not the final supported project OS.

## Collection, interpretation and rollback

In actual TWRP, run the prepared read-only collector once. It verifies identity,
aliases, full p6, the entire candidate prefix, fresh nonce/seed, slot CRCs and guard.
Keep the full returned p5, raw record and report privately. Failed reads preserve
the existing response bytes/length/digest privately; no trimming/full-read retry.

Complete loader capture criteria: sequence≥4, no invalid slots, recognized
nonce/prefix-bound loader `pre_handoff`, target sector18432, entry40080000 and
DT48000000. The assessment explicitly leaves kernel entry/logging and modern-kernel
admission false. HOSTCONTROL, a stale record or approximate screen recall fails.
Retain partial attributable records and identify their exact stage.

Archive/hash-match the raw readout and operation receipts on lab/controller before
original p5 restoration. Read the normal bootstrap range: if it is already original,
verify it and do not write. TWRP's existing repair may legitimately restore it; do
not disable that repair or modify the return bootstrap. If it is the exact observer,
restore the original range once using the actual returned p5 hash. Any other hash
stops. Then restore original full p5 once, bound to the validated returned image
hash (including a changed record tail). Verify full original p5/p6, normal/return
bootstrap/header and RAM cleanup; leave TWRP running, no reboot.

If preparation stops before the p5 install, the separate original-p5-bound bootstrap
restore is available. An uncertain write is never retried. Readout/transport failure
does not waive original restore guards; establish a separately validated current
hash rather than restoring from partial bytes. Original rollback is not gated on a
logging success or on renewed trial approval.

## Prepared entry points and current state

Private case commands call `known_boot_capture_device.py` for preflight, the two
installs, installed preflight, collection, both bootstrap-return branches, original
p5 restore and final verification. `known_boot_control_watch.py` only observes;
`known_boot_control_return.py` requires a subsequent explicit desk-return request;
`assess_known_boot_control.py` independently assesses the collected record.
The legacy diagnostic gate/installers are unchanged.

The source and private package are prepared. Approval templates are false; no
authorization file, device write, watcher, helper, physical trial or owner action
is armed by this review. Read-only Linux staging/preflight passed:21 source/artifact files matched; exact
original p5/p6, normal/return bootstrap/header, GPT and aliases passed. Original
helper sources and selected cached USB metadata were verified, ModemManager inactive.
681 controller tests passed, including10 new calibration controls; the historical
logging-hold regressions passed. Exact-head required checks are recorded on PR453. Physical action requires this complete exact review and
fresh owner approval/availability, not a historical trial's approval.
