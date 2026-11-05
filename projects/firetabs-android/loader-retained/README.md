# Retained loader checkpoint core

Analysis implementation for issue346. This directory is not an installable payload.
It has no device discovery, qualified firmware bindings, hooks, physical address layout or
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

## Checked command-completion adapter (analysis only)

`mmc_flush.c` replaces reliance on the flawed SWITCH poll with one raw CMD6 and
fresh CMD13 status checks. Before CMD6 the card must be selected/ready/clean;
after it, only fresh ready/TRAN status permits success. Upper status bits,
SWITCH_ERROR and EXCEPTION_EVENT fail conservatively. Every command has retry=0;
there are at most1000 post-command polls and a1000ms elapsed budget, checked
even when a command claims ready. Any error latches permanently without retry.

The command structure matches the archived LK constructor: response at+0xc,
timeout at+0x1c, retries at+0x20. Nine native controls and nine actual Thumb adapter
controls pass. The latter execute the exact archived command wrapper0x4bd395f4,
with only its hardware driver and clock modeled. The old SWITCH routine is never
called. The adapter alone links to356 bytes; this does not include the writer,
context, hash implementation or required firmware bindings.

Reproduce native controls with `python3 -m unittest discover -s tests -p
'test_loader_flush.py'`. Compile `mmc_flush.c` with the same flags above and
`-Wl,-e,lf_flush` (instead oflc_init), then run
`scripts/validate_loader_flush.py --elf <analysis ELF> --lk <private original LK>
--output <report>`, using the local Unicorn environment.

**Not physically qualified:** the underlying driver must honor its timeout and
single-attempt contract, the monotonic clock and exact card/RCA/cache bindings
must be proved, and memory ownership/stack/hook replay remain open. Admission
flags cannot establish these facts. No physical MMC command or new trial was run.

## Integrated position-independent module and allocation route

`module.c` connects the writer's flush callback to the checked adapter while
preserving independently bound physical read/write/prefix callbacks. A fresh zeroed
exclusive state is initialized once; a second initialization stops the module.
Four native integration controls cover commits and all nine first-commit command
failure boundaries. No physical bindings or boot hooks are installed by this API.

Build with `scripts/build_loader_module.py --zig <local Zig0.14.1 path> --out
out/loader-module`. The resulting `module.elf` is an analysis artifact. Run
`scripts/validate_loader_module.py --elf out/loader-module/module.elf --object
out/loader-module/checkpoint.o --object out/loader-module/mmc_flush.o --object
out/loader-module/module.o --object out/loader-module/freestanding.o --lk <private
original LK> --output <report>`. The validator checks allocated input relocations
(R_ARM_REL32, THM_CALL, THM_JUMP24, PREL31 only), then runs real module instructions
at three modeled addresses through the archived command wrapper. It does not
establish ownership of any of those physical addresses.

The archived aligned allocator entry0x4bd45bb8 tail-calls the allocation core at
0x4bd450dc. `validate_loader_allocator.py` runs those exact bytes with an explicitly
modeled initialized free list, demonstrating distinct aligned module/context/stack
allocations and fail-closed null returns for exhaustion or invalid alignment.
IRQ services and heap state are models; no actual free RAM is claimed. The intended
integration route is an owned allocation and PIC module rather than a fixed-address
writer in the old small gap. A bounded bootstrap load/integrity/cache bridge and
real heap lifecycle/driver/clock/card bindings are still required before packaging.
The4KiB modeled stack is capacity for a control, not a measured worst-case stack bound.

## Bounded allocation/load/integrity/cache bridge

`bridge.c` implements one allocation and one readonly blob load, SHA-256 equality,
zeroed module state/private stack, then cache synchronization. Callable entries
are published only after every step succeeds. Invalid sizes/offsets/Thumb entries,
missing bindings, allocation/read/hash/cache failure and repeated calls stop
without retry. The bridge never writes its source partition. The548B linked bridge
still needs descriptor/hook storage and qualified firmware bindings; code size alone
does not admit placement in the584B gap.

`pack_loader_module.py` produces a4608B standalone module blob from the tested ELF,
with exact object hashes and Thumb entries. It only inspects the candidate's
12MiB file interval: that interval is zero and lies after declared normal image
sections and before the mailbox. It does not change a candidate or select a write.
A new candidate would require a new prefix digest/seed and complete exact review.

Five native bridge controls pass. Five ARM controls execute the actual bridge,
archived allocator and loaded PIC module in modeled RAM. The success path uses
its allocated state/private stack to commit MODE and HANDOFF through the checked
adapter. Allocation/read/hash/cache failures publish no entries and never retry.
Driver, clock, storage, hash, cache and IRQ services remain models. No real heap
lifecycle, firmware hash/cache/timing/card bindings, hook replay or bridge placement
is yet qualified, and no physical observer is packaged.

## Pinned hash and cache bindings

`hash.c` and `hash-block.S` now bind SHA-256 framing to the archived generic ARM
compression entry0x4bd15620. The thunk supplies its end-pointer/table-base ABI,
bypassing only CPU feature dispatch to select the generic integer algorithm. It
changes no capability/global/security register. Twelve controls execute the actual
compression instructions against hashlib vectors, including padding boundaries,
the4608B blob, wrong digest and unadmitted/oversize inputs. Firmware reads are
confined to round constants; ordinary writes are private stack only. Hashing itself
is no longer modeled in the bridge's `--actual-hash` profile. Prefix streaming I/O
still needs its separate immutable target adapter.

`cache.S` bounds the range, calls the pinned0x4bd3c740 clean/drain/I-cache sequence,
then explicitly executes DSB/ISB and normalizes its void return to success. Seven
controls execute the wrapper/firmware loop and record CP15 maintenance order; the
hardware effects remain modeled. This is code visibility maintenance, not a measured
hardware visibility pass. No physical cache command was executed.

Build both into the analysis bridge with `build_loader_bridge.py --zig <Zig0.14.1>
--out <output>`. Retain callback roots with `-Wl,-u,lh_equal`, `-Wl,-u,lh_block` and
`-Wl,-u,lb_cache_sync`. The combined bridge is968B before descriptors/hooks. Replay
`validate_loader_bridge.py` with `--actual-hash --actual-cache`: five controls pass,
including loading/committing the module on allocated state/stack. Readonly storage,
driver, clock, IRQ, prefix hash and cache effects remain models. Real card/target
read/write, prefix streaming, driver timing/clock and bridge/hook placement remain
required before a physical bundle is admitted.

## Immutable storage target and streamed prefix integration

`physical.c` freezes device/first-sector/size/GPT5/MMC8 and pinned raw byte routines
at initialization. It normalizes exact byte counts, rejects32-bit-LBA truncation,
limits writes to aligned mailbox blocks, and latches short/uncertain I/O without
retry. Partial payload reads use the module's owned4KiB buffer and an aligned raw
read; they do not depend on the firmware's global partial-read buffer and never
overrun the requested output. Absolute blob reads stay in the admitted prefix.

`hash-stream.c` hashes fixed-size whole-block chunks with the actual generic
compression binding and exact final length/padding. The prefix path reads exactly
15MiB in4KiB chunks without a second large allocation. Its digest must not alias
the read buffer. Nine native adapter controls include full prefix extent/padding
with modeled compression; ten ARM stream controls use actual compression through
32KiB, chunk grouping, wrong digest and bounds. Ten ARM I/O controls execute the
exact archived byte read/write wrappers with modeled block hardware.

`firmware-module.c` composes these callbacks with the writer and checked flush,
requiring the independent record target/configuration to agree. It reuses only the
writer's separate output block for storage scratch. Four native composition controls
exercise the full prefix loop and retained records; seven ARM composition controls
exercise pinned byte/command wrappers at two PIC bases, fail-stop and non-normal
mode guards. Prefix digest is explicitly modeled in that ARM composition and tested
separately in the native full-prefix and actual ARM stream controls.

Build this analysis profile with `build_loader_module.py --profile firmware`.
It is5826B with8656B state; the old core-only blob/packer profile is not a new
firmware-profile trial bundle. Block hardware/DMA, real card/device identity,
monotonic timing/driver termination and bridge/hook placement remain unqualified.
No physical read/write or new candidate is selected by these tests.

## Bounded flush-command lane and read-only clock

`clock.c` binds the pinned three-read GPT4 sampler at0x4bd25dfc. It extends32-bit
13MHz ticks with wrap/remainder handling, rejects missing initial progress or
backward jumps, and never configures/resets a timer. This pins the LK delay contract;
real counter values/rate remain a hardware admission assumption.

An exact legacy wait audit found an unbounded R1b DAT0 loop and a reset-failure
self-loop. An outer deadline cannot preempt these calls. `command.c` therefore
implements a narrow command-only lane for FLUSH_CACHE/CMD13. It sends CMD6 with an
R1 response and checks busy completion separately in the existing flush adapter,
as supported by the Linux MMC R1 fallback. It permits only command argument,
command and command-interrupt acknowledgment writes, with ARM MMIO ordering.
No reset, DMA configuration, timer or security register is written. It refuses an
active DMA engine or enabled command-interrupt consumer, unrelated pending events,
wrong arguments and retries. Both loops have tick deadlines and65536-iteration
caps, including a stalled-counter case; every failure latches. Programming-state
CMD13 replies are paced by at least one clock millisecond with their own finite
spin/deadline guard; the1000ms outer budget now has1000 polls rather than the early
eight-poll source prototype, which could end before a real flush completed.

Ten native and fourteen actual ARM clock/command controls pass. Counter/controller
values are models; archived GPT sampling instructions are executed. The `timed`
module profile composes this lane with the writer/target adapter:6996B/state8728B,
four native and nine ARM controls, including two PIC placements and clock/controller
failure cases. ARM composition explicitly models prefix digest and block hardware;
separate native full-prefix/actual SHA-stream controls retain their stated scope.

The original raw data read/write driver is still used. Its error paths are not
termination-qualified, and this command-only lane does not preempt them. A complete
trial review must disclose that recovery risk; no fully bounded data-I/O guarantee
is claimed. Real card/device/DMA identity and bridge/descriptors/hooks ownership,
IRQ lifecycle/replay/cache visibility remain requirements before packaging.
A possible console-only code reclamation route is only a private analysis proposal,
not an admitted span. No physical observer, candidate modification or trial follows
from these source controls.
