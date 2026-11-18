# Complete the existing PID1 USB transfer

The full attempt ran November17,2026 and delivered the exact fresh PID1 USB
identity. [Identity milestone and stream limit](../../evidence/independent-recovery/ack-usb-end-to-end-runtime-result.json).
Scope5 is consumed; no replay. The40-byte header is verified, following record
transfer incomplete. Historical preparation follows. [Prior hardware result](../../evidence/independent-recovery/ack-ramfix-runtime-result.json).
The RAM-corrected maintained kernel completed initialization, executed /init,
loaded its SELinux policy and probed the gadget successfully. Host kernel events
show1209:0001 enumeration and CDC ACM binding during the attempt. Original
Android returned with exact boot/config/recovery and normal ADB verified; owner
confirmed Power untouched. Do not reopen kernel-entry, initialization or PID1
execution as pending milestones.

The pinned PID1 gates gadget creation behind enforcing-state readbacks, loaded
read-only policy, labels/domain and namespace checks. Reaching the gadget setup
therefore supports those gates by control-flow inference. A fresh nonce-verified
USB protocol record was not recovered; that specific end-to-end acceptance
remains open. Do not equate a missing capture result with no USB device.

## Receiver repair, not another logging gate

The last receiver left raw.bin empty and no completion receipt. Its SSH stdout
also had no final result, and the old supervisor discarded its stderr and exit
status. The exact reason that process failed is unproven. This is an operational
receiver defect, not evidence of a new kernel/PHY failure.

The repaired receiver starts one detached, bounded worker. The ready marker is
published atomically only after raw output is created/fsynced. The worker is
isolated from the SSH session, reads the same exact physical-port/VID/PID/
interface/fresh nonce profile, opens once and runs the existing durable framed
protocol. It has a125-second hard deadline; its supervising session is bounded
to135 seconds. There is no automatic restart, port reopen, descriptor override,
udev/group change or device reboot command.

Ready/result files, stdout/stderr and identities stay in private mode0600 files
under a fresh0700 directory. Atomic file publication avoids partial JSON races.
The controller preserves SSH exit status/stdout/stderr and recovers a durable
host result if stdout is lost. That recovery only reads files; it does not open
the transport again. The original endpoint-selection and fresh protocol checks
remain required. Offline controls kill the parent after readiness and verify
the detached worker still saves its outcome; another supervisor control recovers
a successful fixture transfer after SSH stdout loss without repeating the jump.

## Next action

One **full end-to-end attempt** under fresh scope
ack-linux-usb-end-to-end-two-stage-5, using the existing RAM correction and fresh
PID1 identity. No separate logging, kernel-entry or PID1-proof device test.
Verbose initcall tracing is removed; ordinary kernel output remains available.
The kernel code changes only in its fresh immutable identity, not its drivers or
RAM correction. The complete fresh Image was checked in both target-memory-
geometry VM modes. Standard integrity/guard checks bind the actual package.

[Qualification](../../evidence/independent-recovery/ack-usb-end-to-end-qualification.json),
[preparation](../../evidence/independent-recovery/ack-usb-end-to-end-preparation.json).

Original boot restored/read back before the RAM jump, recovery never written,
existing31-second target reset deadline, bounded read-only return checks and
no retry. Earlier trials remain consumed. Accept success on the fresh enforcing
PID1 USB protocol identity/records/terminal witness, then progress to the next
functional milestone. If transfer fails, use the receiver's actual outcome to
fix that boundary; do not require proof of already-working kernel/PID1 stages.

## Completed attempt and cleanup repair

The fresh exact VLOG0002+nonce header reached the host. Pinned PID1 gates
policy/enforcing/RO/domain/namespace/UDC/serial/kmsg before emitting it, so the
kernel/PID1/USB identity milestone is reached. Complete records0, terminal false:
full record transfer is not claimed. The earlier stricter wire payload flag
remains false; it must not downgrade this narrower achieved identity milestone.

The detached worker exposed a termios.error cleanup escape after disconnect,
which masked endpoint/result state. The controller's original ValueError is
preserved in the runtime receipt. Cleanup now preserves both incomplete-transfer
failures and completed-transfer outcomes when a vanished TTY cannot be restored.
A local software test covers both cases. No new tablet logging test is planned.
The original cause of the post-header transfer interruption is still open.
