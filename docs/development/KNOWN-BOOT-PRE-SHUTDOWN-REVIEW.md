# Known-stack recorder repair — pre-shutdown control 2

Issue346 / parent344 / PR453. Source and offline package only. No device action,
source export, new kernel build, owner approval or availability is implied.
Control1's approval is consumed; its original boot/recovery remain restored/TWRP.

## Changed contract

Control1 reached the home screen but produced no target record. Its cause is not
proved. The next candidate repairs three concrete source/placement defects rather
than repeating that unchanged control:

1. Cache-off was rejected even though it is a valid card state. The new path uses
   fresh clean/ready CMD13 status before and after each completed write barrier,
   with no CMD6 when the observed cache flag is off. It never enables/disables the
   cache. Cache-on retains its one FLUSH_CACHE plus fresh completion status.
   Clock/deadline/poll caps, R1 errors, identity/mutation and permanent failure
   guards remain. This follows the conditional-cache rule in
   [Linux3.18 mmc_flush_cache](https://raw.githubusercontent.com/torvalds/linux/v3.18/drivers/mmc/core/core.c).
   The actual loader cache state in control1 is unknown; recovery's cache flag is
   not evidence of that earlier state.
2. The archived normal path calls the IRQ-mask helper at4bd3e3f8 before the old
   final hook4bd3e524. Actual helper instructions set CPSR.I. Our old hook declines
   storage I/O with I set. The replacement site4bd3e3e8 is before that mask call
   and the intervening later shutdown calls, preserving the original final SMC
   call bytes. This placement mismatch does not explain the missing earlier MODE
   records by itself and is not a retrospective runtime IRQ observation.
3. An unsafe read observation used to permanently consume initialization without
   even attempting I/O. In this profile it is skipped without an attempt; one
   later safe pre-shutdown initialization is allowed. A failed real module load,
   hash, identity, command or write still latches permanently and is never retried.
   Null/unaligned/overflowing device globals stop before any module read.

The new stage is explicitly **pre_shutdown**, not pre_handoff or kernel entry.
It captures proposed entry from r11 and DT address from caller SP+8 before shutdown.
The fixed VLOG0001 mailbox, tag/body layout and existing reader stay compatible;
loader metadata decoding adds stage4. Historical stages remain supported. MODE
means the mode sampled at the eligible read or safe late initialization point.

## Exact package and preserved bytes

- Control fullp5 (16MiB):
  `e1f2a73bb1fef09605b938b42993ad93b5fe5de7d681e62211816944741722e6`.
- Normal observer range (492544B):
  `3313d00c51d9960a3f24c8f4a87c3ee532119f4f48113512ad5deda0d8cdd20f`.
- Original fullp5:
  `08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e`.
- Original normal/return bootstrap range:
  `4c6f355c735b9302b0d421ef38f94a9974214d531fa974a41edd8132af7ac092`.
- Unchanged fullp6:
  `3c9bafcbfc4a0b12cb1a3f372af0cfd49ffec5b3e01a0b070465b49bd8435f11`.

All7796736 declared original header/kernel/appended DT/ramdisk bytes remain exact.
The9216B module is in verified-zero12MiB padding; state8744B and private stack4096B
use the existing exact allocator. Fresh nonce/prefix/seed are outside original
components. Bootstrap1572B fits only the proven console-owned spans (1587B total),
with live globals preserved and no guessed RAM. The changed embedded normal-LK
instruction is the pre-shutdown PC-relative load; its original literal load is
replayed. The original final call remains byte-identical.

Inline BL changes LR, which is dead here: each original fall-through path overwrites
LR with a BL/BLX before reading it. All r0–r12/SP/APSR are replayed, including the
original r3 literal load. Snapshot arguments, module integrity/load/cache publication,
late initialization and invalid-device stops are exercised by the full replay.
Controller/storage/clock/initialized heap/IRQ services/cache effects and the complete
prefix digest remain modeled; this is not physical acceptance. Original raw data
transfer termination, actual heap capacity, worst-case stack and durability are
still unqualified. Masked or active-controller contexts remain refused.

## Procedure and outcome criteria

The physical operations and two-visit/manual-return protocol are the same bounded
operations in [control1 review](KNOWN-BOOT-CAPTURE-CONTROL-REVIEW.md), using this
fresh exact artifact pair and scope `known-boot-pre-shutdown-control-2`:

1. Stage/hash-check the20-file private profile, selected Linux device and original
   fullp5/p6/bootstrap/header/GPT/aliases. Scope/hash-bound authorization remains
   absent until exact approval and current availability. Install observer once,
   then control p5 once; full readbacks/RAM cleanup and installed checks before boot.
2. Observation only:600s travel window, then330s host metadata history after USB
   departure; at least five minutes before any return. No automatic helper, reset,
   reboot or restore. Owner selects TWRP Reboot/System once and reports at the desk.
3. Only then prepare manual return when the owner is ready to leave: disconnect USB,
   hold Power40s, release/wait5s, reconnect once, wait up to180s and desk report.
   Original return waiter900s/helper90s, one original helper maximum. If a host
   window expires without a launch, preserve it; do not silently repeat a boot or
   write. The prior missed windows are historical and not reused.
4. In validated TWRP collect once before restoring. Complete recorder criterion is
   fresh nonce/prefix-bound `pre_shutdown`, sequence≥3, no invalid slots, exact p5
   target18432 and original-stack entry40080000/DT48000000. HOSTCONTROL and stale/
   partial records fail the complete criterion; retain and identify partial stages.
   An observed record still does not prove SMC completion or kernel entry.
5. Archive/hash-match the full readout and private receipts on lab/controller.
   Verify an already-original normal bootstrap without writing, or restore the
   exact observer range once under the actual current p5 hash. Restore original
   fullp5 once under validated returned hash, verify fullp5/p6/bootstrap/header/
   GPT/aliases/RAM cleanup; leave TWRP running/no reboot. Preserve its repair.

No return bootstrap/header, recovery, GPT, preloader, standalone LK/security,
userdata or policy writes. No old OS installation or account interaction. No cache
mode or interrupt-enable change. Read-only collection and original restoration
remain available independently of a logging success. No modern-kernel trial or
kernel-side/USB logging admission follows automatically from a loader record.

## Validation and admission boundary

The private package is built and independently verified. All four guard bindings
(candidate, observer, prefix, seed) are generated and checked from its manifest,
with a unique scope; the old control's authorization cannot admit it. Approval
and availability templates are false. Exact-byte ARM replay, relocated frontend,
source tests and required current PR checks are recorded in
[the repair receipt](../../evidence/independent-recovery/pre-shutdown-recorder-repair-result.json).
No new control has been staged on the lab, installed, armed or physically tested.
Fresh exact review approval and availability are required before that next action.
