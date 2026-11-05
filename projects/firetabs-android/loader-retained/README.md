# Retained loader checkpoint core

Analysis implementation for issue346. This directory is not an installable payload.
It has no device discovery, firmware adapter, hooks, physical address layout or
physical admission command. `analysis.ld` addresses belong only to the emulator.

`checkpoint.c` calls the existing VLOG0001 codec unchanged. It emits a distinct
loader producer for normal mode, header/body reads and pre-handoff arguments.
The actual selected partition/offset and handoff arguments are recorded as data,
including unexpected values; they do not redirect record storage or dereference
those addresses. A pre-handoff record does not prove kernel entry.

The adapter must bind the exact candidate prefix/nonce and p5 target independently
from intercepted read arguments. It must prove exclusive ownership, synchronous
bounded reads/writes and a genuine persistence barrier. Admission flags are
requirements, not probes or substitutes for that proof. Missing admission stops
before I/O. Each write is padded to a 4 KiB record block, confined to the existing
two slots. Seed/prefix/final guard remain unchanged. Commit order is invalidation,
flush, payload, flush, header, flush, readback. Failure latches permanently without
retry. The first commit requires exact HOSTCONTROLseq1 and an otherwise empty tail;
subsequent commits require the preceding exact loader record. Eight commits maximum.
The existing kernel producer can subsequently advance the same mailbox sequence.

## Reproduction

Native and collector controls:

```sh
python3 -m unittest discover -s tests -p 'test_loader_checkpoint.py'
python3 -m unittest discover -s tests -p 'test_pull_retained_mailbox.py'
python3 -m unittest discover -s tests -p 'test_retained_log_mailbox.py'
```

Local ARM build used Zig0.14.1, target Thumb Cortex-A9:

```sh
zig cc -target thumb-freestanding-eabi -mcpu=cortex_a9 -Oz -g \
  -ffreestanding -fno-builtin -fno-stack-protector \
  -fno-unwind-tables -fno-asynchronous-unwind-tables -nostdlib \
  -Wl,--build-id=none \
  -Wl,-T,projects/firetabs-android/loader-retained/analysis.ld -Wl,-e,lc_init \
  projects/firetabs-android/loader-retained/checkpoint.c \
  projects/firetabs-android/loader-retained/freestanding.c -o out/loader-checkpoint-core.elf
PYTHONPATH=scripts python3 scripts/validate_loader_checkpoint.py \
  --elf out/loader-checkpoint-core.elf --output out/loader-checkpoint-arm-report.json
```

The validator needs Unicorn2.1.3. On this Mac its host cache discovery requires
unsandboxed local execution; this grants no tablet access and changes no host setting.
The callbacks model storage/flush and prefix hashing. Actual hardware persistence,
physical placement, firmware ABI and instrumentation replay remain unqualified.

## Firmware integration gates

The exact archived LK SWITCH routine at0x4bd39b80 builds CMD6 correctly for
FLUSH_CACHE, but its poll-expiry path returns zero, also used for ready success.
`scripts/audit_loader_switch.py` replays these bytes with command/status models;
the timeout boundary test explicitly reduces the counter to two iterations.
A direct return-value-only flush binding is rejected. A future adapter must verify
fresh status/command errors and ready/non-programming completion within a bounded
budget, preserving the normal loader's state and refusing all writes when the
contract cannot be established. No physical CMD6 was executed by this work.

The current compiled core is3595 bytes before firmware/SHA integration, with a
separate context measured in the ARM report. It cannot fit the old584-byte gap.
An owned allocation/load span, lifetime, stack and branch/cache visibility must be
proved before linking an observer. Zero-filled bytes are not ownership evidence.
TWRP's existing bootstrap repair remains enabled and recovery is unchanged.
