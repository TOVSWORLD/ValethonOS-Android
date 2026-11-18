> Owner-assisted recovery completed; original boot/config/recovery verified.
> Pstore record directory empty. [Post-failure findings](NATIVE-KEXEC-POSTFAILURE.md).

> Trial executed November 10: native load verified, one orderly jump request,
> no target Android observed within five minutes. ADB absent afterward; owner
> screen observation/recovery needed. No partition writes or automatic retry.
> [Runtime result](../../evidence/independent-recovery/native-first-jump-runtime-result.json).
> Historical preparation protocol follows; its approval is consumed.

# First experimental native kexec jump

## Current state — November 10, 2026

The approved temporary source-kernel boot passed. Android returned to its home
screen with native config SHA256
`71184d29b986824d086f9a0cb0ce6bb00d2d63723e0476a49d3381cb00603ac9`.
One candidate write, one ordinary reboot and one original boot restoration were
performed. Original p5 and untouched p6 were verified; normal UID2000 ADB restored.
The kexec-capable kernel remains in RAM. An ordinary restart returns to the
original kernel and loses this temporary capability. Do not reboot before the trial.

[Source boot result](../../evidence/independent-recovery/native-source-boot-runtime-result.json).

## Exact next hardware test

Requires fresh owner approval and availability for one experimental jump.
`run_native_jump.py` defaults to read-only; completed live preflight performed
zero loads/jumps/writes and restored normal ADB. The approval binds runner,
private manifest and load-client hashes and a unique target trial ID. It is
consumed before runtime action. No automatic repeat is allowed.

1. Verify native source config/live DT, original full boot/recovery hashes,
   RAM capacity and empty native kexec load state.
2. Upload the reviewed client and three hash-verified segments to private RAM.
   Load once through native ARM64 syscall104 from CPU0. The client has no execute
   or reboot command. Before a shutdown request, a failure permits one cleanup
   unload of this run's image; pre-existing images are never replaced/unloaded.
3. Request `reboot,valethon-kexec` once through Android's `sys.powerctl`, invoking
   init's existing shutdown before the PID1-only native kernel route. Do not
   substitute a direct reboot/kexec syscall. Filesystem unmount and device/DMA
   shutdown sufficiency remain experimental, rather than guaranteed by a request.
4. Wait up to five minutes. Success requires a changed boot identity, completed
   Android startup, original working target kernel config, unchanged full boot
   and recovery hashes, and exact `/chosen/valethon,kexec-trial` value. A changed
   boot identity or home screen without that marker does not prove a kexec jump.

No boot/recovery writes, failure injection, pstore deletion, automatic recovery
reboot, or logging baseline repeat is included. Failed-jump logging diagnosis
follows a failed jump, per owner direction; it is not a pretrial requirement.
No jump has run as of this preparation receipt.

## Target and layout

Target Image and gzip ramdisk come from the pinned, working original full boot.
Current native source live DT properties and reservation map are retained; only
one chosen string, `valethon,kexec-trial`, is added for attribution. Original
initrd start/end remain unchanged. All segment pages fit current System RAM and
avoid DT static reservations and FDT reservation-map entries. The dynamic RAM
hole is excluded by current `/proc/iomem`. Existing pstore reservation is preserved.

Image at `0x40080000`, metadata at `0x42000000`, six-instruction entry trampoline
at `0x42018000`, and page-aligned initrd segment at `0x69244000`. Initrd content
starts at its original `0x69244e00` address. The trampoline supplies DTB in x0,
zeros x1–x3 and branches to Image; native relocation/cache/MMU/EL handling is used.
The native allocator owns staging/relocation/control pages, including overlap
with the old source kernel. The complete target Image memory extent is staged,
with kernel-managed zero padding beyond file data.

## Failure and recovery

If Android does not return, or returns without the unique marker, stop. Do not
retry the property request or issue another reboot automatically. The original
boot is already on flash, so physical restart can return to it; this is not a
proven independent recovery mechanism for every hung state. Owner action may
be required. Existing recovery remains untouched. If a physical recovery is
needed, observe the screen/transport first, then use the documented existing
recovery and exact-original rollback procedure only if identity guards match.
Keep #346/#348 open and retain failed-trial evidence for subsequent logging work.

## Validation and historical trail

39 native Python tests pass, including refusal of pre-existing images, uncertain
load cleanup, shutdown-request transport uncertainty without retry, target-marker
absence, timeout and reserved-memory/overlap faults. Twelve Linux host controls
compile the actual C client with mocked files/syscalls, verify passed segment ABI
and flags, and cover load/unload failures and invalid execution arguments. These
are offline checks; the actual syscall/jump remains untested.

An initial lab GNU cross build failed because cross libc headers were missing.
The existing local Linux/musl cross compiler built the retained static ARM64 client
without installing packages or disabling checks. An initial macOS harness compile
lacked Linux affinity types; the actual harness passed on Linux. Both attempts
are retained in the preparation receipt. No failed hardware jump is being hidden.

[Bundle, client, preflight and controls](../../evidence/independent-recovery/native-first-jump-preparation-result.json).
[Unapproved exact authorization](../../evidence/independent-recovery/native-first-jump-authorization-template.json).
