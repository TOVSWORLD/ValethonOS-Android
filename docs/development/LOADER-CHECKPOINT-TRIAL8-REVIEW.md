# Exact retained loader checkpoint trial8 review

**Held after owner redirection to proven-baseline research.** This candidate is
retained unarmed as a fallback; it is no longer the selected next physical action.
See [the revised plan](LOADER-UNBLOCK-PLAN.md).

This is the complete changed procedure for owner review. It is unarmed. The last
actual device state is trial7 complete with original bootstrap/full boot/recovery
verified and TWRP running. Nothing in this review claims fresh live device state.

## What this trial changes

The normal loader writes attributable retained records instead of asking the owner
to remember console text. The resident read hook loads one hash-verified PIC module
into one allocator-owned code/state/private-stack allocation. It records normal
mode at the first redirected image read, then the header/body reads and the final
handoff call arguments when interrupts are enabled. It does not claim completion
of SMC or kernel entry. A kernel-produced record remains a separate required result.

The bootstrap bridge/descriptors/hooks occupy1530 bytes within1587 console-only
bytes and the previous resident tail. Poisoned-span replay preserved nine boot-mode
cases and twelve read/64-bit offset controls. Live globals, GPT names, memory/string
helpers, boot flags and the original recovery route remain intact. Console formatting
becomes return-only; no new banner, security/reset/watchdog write or failure injection
is added. Existing original bootstrap security code is unchanged.

The module is9216 bytes, state8744 bytes, private stack4096 bytes. Complete packed
replay observes776 bytes of private-stack use; this is not a hardware worst-case bound. It uses the
original allocator with finite failure checks and no retry/free of uncertain state.
Allocation/hash/cache failures leave the original read path running. It declines
observation when IRQs are masked; it never enables interrupts to obtain a checkpoint.
The existing raw data-driver error paths remain termination-unqualified. A stalled
firmware call may still require the already reviewed manual power/return sequence.
Real heap capacity, cache/controller effects, durability and hardware-driver worst-case
stack remain unqualified. Source/emulator results are not hardware acceptance.

The kernel instructions and gzip are byte-identical to candidate6. This trial has
one fresh nonce: only the named non-executable PID1 nonce constant and the DT chosen
nonce property are rebound. PID1 instructions, policy, archive headers and every
other DT/initramfs payload byte are unchanged. The Android header/component ID is
recomputed. The module occupies previously zero file padding and the retained tail
is freshly seeded. No kernel or PID1 instructions are rebuilt.

Exact p5 candidate SHA256:
`891ef137024e9b6712894dcbe1c2e398023b45598f56480b666b001147b1f5b3`.
Exact normal-bootstrap payload-range SHA256:
`0db009d6da24a8908df0c49769f3de81d11222ea31c6b42b6547df4bbfd6be41`.
The [public candidate receipt](../../evidence/independent-recovery/loader-trial8-candidate-result.json) records module, prefix and seed hashes. Independent
verification checks the named nonce binding, gzip, component ID, padding, descriptors,
module object relocations and seed. No old approval, receipt or record is reused.

## One installation and one visit, after exact approval and availability

Approval covers uploading the reviewed private trial8 tool/artifact package to the
existing Linux lab, fresh read-only identity/alias/GPT/full-original/backup preflights,
one exact p17 normal-bootstrap payload-range install, one full-p5 candidate install,
postwrite readbacks/preflights and one supervisor arm. Every mutation has a fresh
exclusive receipt. No automatic reboot occurs. Any unexpected identity, hash, size,
readback, partition mapping or uncertain-write state stops without retry.

The bootstrap write is only512-byte sectors223223..224184 relative to p17. It excludes
headers/GPT and leaves p18 return bootstrap and p6 recovery untouched. p5 is exactly
16MiB. The guard pins actual p5/p6/p17/p18 geometry and exact candidate prefix/seed.
No preloader, LK partition, security partition, userdata or account access is included.

Once armed and the owner is available, make one visit: TWRP Reboot/System. Wait90s.
No text, photo or banner recollection is needed. If TWRP has not returned, disconnect
USB, hold Power40s, leave off5s, reconnect once, then wait up to180s for TWRP. Return
to the desk and report. Do not repeat the boot, reconnect sequence or StageA entry.
The original FACTORYM helper may run once under the existing supervisor. Its exit0
alone does not prove recovery or explain a reset.

## Collection and restoration included in the same approval

After actual recovery validation, collect once. If the supervisor stops, use the
separate prepared read-only collector once; keep its stage/reason evidence. Preserve
all retained slots and private logs. No intentional failed-load trial follows.

Use the validated readout/current full-p5 hash. Check the normal bootstrap range:
if TWRP repair has already restored the exact original, verify and skip the write;
otherwise restore the exact original payload range once through the matching guard.
Do not disable TWRP repair or change p18 to keep an observer installed. Then restore
full original p5 once, verify full p5/p6, both bootstrap headers/return range and RAM
cleanup. Leave TWRP running with no reboot. If any current hash or write state is
uncertain, stop and report; no assumed-safe second write.

The private execution package has distinct supervisor/manual restore commands,
including changed kernel-record tails. All previous approvals/receipts are consumed
and are not reused. No physical operation has been executed for trial8.
