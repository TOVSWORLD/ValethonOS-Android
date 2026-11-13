# Private retained-log prerequisite — issue346

Not physically admitted or tested. No existing approval authorizes this new
kernel block-I/O / PMIC / eMMC behavior. Existing original p5/p6 remain restored.

This mode adds a builtin kernel logging worker, outside PID1/USB. It requires root
board compatible and an exact32-byte chosen trial nonce; absent either it exits.
Only mmcblk0 partition5,16MiB and exclusive access are allowed. Kernel SHA256 must
match the entire first15MiB against the seed and nonce. Writes are confined to two
127-page record slots in the last1MiB; the seed and final4KiB guard stay untouched.
Original images lack this seed/nonce and cannot be initialized by the worker.

The host seeds the experimental image offline, after assembly. Both implementations
use VLOG0001, little-endian header fields, nonce/sequence/length, header/payload CRC32,
header-last commits with explicit flushes. The inactive slot is invalidated/flushed,
then payload/flushed, then header/flushed. Short/failed I/O stops; no write retry.
Twelve bounded snapshots at5-second intervals are proposed, not a crash handler.
Before first successful storage initialization/commit, failure remains uncovered.
A power loss may interrupt a snapshot; the previous valid slot is retained. This
is not proof of eMMC power-loss behavior. It cannot promise every printk message.

The kernel backend uses normal block-driver BIO and flush APIs. It neither changes
credentials nor SELinux mode/policy nor exposes a userspace block write API. The
existing PID1 block-device neverallows and one-way domain transition remain intact.
No security denial is to be bypassed to force logging. The worker has no reset,
reboot, panic, userspace control or generic target interface.

The separate lab-retained config enables only the necessary eMMC/block/GPT and
MT6323 supply driver prerequisites; old lab-log remains storage disabled. The own
DT re-enables only mmc0/pio/pwrap, limits eMMC to26MHz without HS200/highspeed or
hardware-reset capabilities, keeps observed reservations and all other disabled
nodes. This permits normal driver rail/clock/pin setup and is new physical behavior
requiring review; no timing/voltage qualification is claimed.

`pull_retained_mailbox.py` reads only exact recovery identity, aliases and fullp5/p6;
it verifies unchanged recovery and exact immutable candidate prefix/seed, extracts
attributable valid records, and records the resulting fullp5 hash. That verified
hash becomes the explicitly expected current image for the existing guarded full
original-boot restore. It never writes a device or reads userdata. All record bytes
and device selectors stay private. No trial is ready until actual kernel compile,
size/VM checks, fresh complete package and reviewed collection/rollback procedure.

A preinstalled **HOST CONTROL**, sequence1, is included in the proposed candidate.
It is explicitly not a kernel log. Kernel commits start at sequence2 and carry a
separate producer/release prefix. The reader reports host-control-only separately
from kernel output. This provides a positive retention/readout control even when
the new kernel does not commit, without mislabeling host bytes as boot evidence.
