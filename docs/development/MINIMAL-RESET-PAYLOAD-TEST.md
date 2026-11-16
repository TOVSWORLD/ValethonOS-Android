# One reset-payload experiment, then a decision

Prepared November 16, 2026. The owner authorized this last narrow handoff probe
and requested a bolder plan if it fails. No reset-payload hardware jump has run.

The source is the already hardware-booted early-CPU-shutdown Image and boot
package. The target is a one-page AArch64 program, not a Linux kernel. It uses
the existing native allocator, three destinations and DT entry trampoline. The
first destination shrinks to one page; original initrd and memory reservations
remain unchanged. Source and target-only nonces are independent.

At entry the program requires EL1 or EL2 and disabled translation/data cache.
It validates the existing ECC-free retained-console ring, appends exactly one
64-byte target-only nonce marker and publishes its ring counters with barriers.
It then follows the existing watchdog driver's normal software-reset sequence.
Writes are limited to that console ring, WDT_MODE and WDT_SWRST. NONRST/RTC boot
flags and partitions are untouched by the payload. Invalid ring metadata causes
a reset without a marker, which is an inconclusive result, not success.

The reviewed geometry is the existing 0x44410000/0xe0000 reserved backend, with
4 KiB dump records, two 64 KiB console zones, 4 KiB ftrace and 64 KiB pmsg. The
current-console zone is 0x444bf000, with 65,524 data bytes after its 12-byte header.
The preflight requires those exact live values, ECC disabled and the existing
parameter-backed backend. The append follows ordinary ring behavior; it does
not clear records. Existing retained files are archived privately before load.

Success requires all of the following:

1. The exact target-only marker is absent before loading and appears exactly
   once in a recovered console-ramoops record after the jump.
2. A different boot identity reaches Android boot complete, with exact original
   full boot/config and unchanged recovery verified; normal ADB is restored.
3. The owner confirms that Power was not used during the bounded return window.

A reboot alone does not prove payload execution. A recovered marker proves
target payload entry, not Linux startup. Marker plus owner-assisted return does
not qualify automatic reset. Hardware reset retention is unqualified until this
actual test; the earlier orderly-reboot retention result is not substituted.

The sequence is one protected source boot and original-boot restoration, fresh
source DT/RAM/challenge, source USB proof, one load and one orderly jump. A
five-minute read-only return poll follows; there are no retry/reboot commands.
Root/readout resumes only after a different boot has completed. If it does not
return, owner-assisted Power recovery is requested after the window. All raw
records, source console and device identifiers remain private.

Validation: all 906 regression tests passed with Unicorn enabled, followed by
six additional two-stage policy controls. The payload controls include seven
native EL1 ring cases, seven injected-EL2 branch cases, five invalid rings and
seven injected unsafe-state cases. EL2/state injection tests branch behavior,
not physical EL2 operation. Twelve actual C load-client controls passed locally
with a host CPU-set compatibility shim. The load-only AArch64 client and an
explicitly non-loadable layout preview were built. Read-only tablet preflight
passed with zero writes/reboots/loads/jumps and normal ADB restored.

## Terminal decision

One failed or inconclusive actual jump activates the
[boot-strategy pivot](BOOT-STRATEGY-PIVOT.md). Do not run another reset-payload,
CPU-count, exception-level or console variation as an automatic follow-up.
Preparation errors can be fixed before a jump; they are not hardware outcomes.

[Exact trial policy](../../evidence/independent-recovery/reset-payload-two-stage-authorization-template.json).
[Instruction qualification](../../evidence/independent-recovery/reset-payload-emulation-result.json).
[Prepared artifacts](../../evidence/independent-recovery/reset-payload-preparation-result.json).
