# Full kernel/PID1 attempt with retained C-initialization output

Prepared November17,2026. Goal: complete maintained-kernel initialization and
prove the enforcing RAM PID1 identity over physical USB. The prior hardware
trial already established full Image integrity and Linux entry through
start_kernel; this package does not reopen those milestones.

## Evidence and implementation decision

The previous trace ends at its start_kernel marker. An absent retained banner
does not locate a failure before the banner: normal printk initially uses its
in-memory log, while ramoops registration happens later. No specific failing C
instruction, driver or USB fault is established. The compiled config has
SHADOW_CALL_STACK disabled. Init-task/stack setup precedes the proven marker;
shadow-stack failure is not an evidenced diagnosis.

Pinned ACK sources used:

- [init/main.c](https://android.googlesource.com/kernel/common/+/d9318bdb4c34e8b2d997b4f67ced56b120b22b87/init/main.c): start_kernel, setup_arch, memory/scheduler/IRQ/time initialization, initcalls, init-memory cleanup and run_init_process.
- [earlycon.c](https://android.googlesource.com/kernel/common/+/d9318bdb4c34e8b2d997b4f67ced56b120b22b87/drivers/tty/serial/earlycon.c): CONFIG_FIX_EARLYCON_MEM maps a single persistent fixmap page; earlycon_init sets the console data pointer before driver setup.
- [8250_early.c](https://android.googlesource.com/kernel/common/+/d9318bdb4c34e8b2d997b4f67ced56b120b22b87/drivers/tty/serial/8250/8250_early.c): selected early setup and console callback ABI.
- [ram.c](https://android.googlesource.com/kernel/common/+/d9318bdb4c34e8b2d997b4f67ced56b120b22b87/fs/pstore/ram.c): no dummy ramoops device when mem_size remains zero.

The candidate replaces the selected early UART8250 **setup callback**, retaining
its PACIASP and restoring authentication on return. The shim installs a RAM
console writer; it never performs UART register accesses. One detour instruction
and450 bytes of proven-zero permanent executable text padding change. The
callback/data remain outside init memory, so keep_bootcon is safe after
free_initmem. The original five entry hooks and their temporary Normal-NC
identity mapping are absent from this Image.

The compiled field offsets are checked against exact disassembly: device con0,
port membase24, console write16 and console data104. The callback uses the
framework's mapped pointer, not a guessed runtime virtual address. It writes
only the existing reserved console's first4KiB: DBGC header12 plus4084 bytes.
It preserves x18/callee-saved registers/LR and restores DAIF. IRQ masking covers
the single-CPU bounded writer. Invalid headers are refused and a long write is
bounded to its final2048 bytes. Each write carries the fresh full PID1 identity.
Raw retained output and identities stay private.

The [exact working4.9 persistent-RAM reader](https://github.com/amazon-oss/android_kernel_amazon_mt8163/blob/72940eb733af8df948cc216cb977cd8be9cba5a9/fs/pstore/ram_core.c)
uses stored size/start to reconstruct the old ring, so a valid4084-byte ring
within its larger zone can be recovered without changing the source reader. Target ramoops module parameters are removed and its DT has no
ramoops device, preventing a second writer from reinitializing the same zone.
The original no-map firmware reservation remains unchanged. keep_bootcon,
initcall_debug, loglevel8 and ignore_loglevel retain initialization progress.
No storage controller or disk-log opt-in is enabled.

## Full attempt, not an isolated console test

The complete ACK Image and fresh enforcing RAM PID1 remain the execution target.
The existing metadata SHA verifies all28,049,408 padded bytes before entering
Linux. The same reset-only31-second hardware deadline remains in force; this
console does not service or disable it. No new target kernel is flashed.

The two Cortex-A53 VM boot modes both reached /init with the exact candidate
Image, passed the enforcing PID1 filesystem/configfs probe and retained the
run-init message after init-memory cleanup. This establishes the console's
mapping/lifetime path in a VM, not Douglas boot or physical USB acceptance.
The VM uses its PL011 normal serial console for probe output; early banner
visibility on that serial stream is not required when earlycon is retained RAM.

Exact [qualification](../../evidence/independent-recovery/ack-cinit-qualification.json),
[VM off](../../evidence/independent-recovery/ack-cinit-vm-off.json)/
[VM on](../../evidence/independent-recovery/ack-cinit-vm-on.json) and
[preparation receipt](../../evidence/independent-recovery/ack-cinit-preparation.json)
bind the candidate and offline controls. No new hardware attempt ran during
preparation. Previously consumed approvals remain consumed.

## Execution and acceptance

Use a fresh ack-linux-cinit-two-stage-3 approval only when the owner is present.
One protected source boot/restore and at most one native RAM load/jump. Restore
and read back original boot before jumping; never write recovery. Derive fresh
DT/iomem and reproduce the prequalified Image exactly; a different hash aborts.
Capture target USB by physical port and fresh PID1 identity. After jump, use
bounded read-only return checks, no reboot/root/unload into a hung device and
no automatic retry. Owner Power recovery remains the fallback after the window.

Success is the existing enforcing PID1 wire witness with exact target identity.
An early console, initcall message, run-init request or Android return alone
cannot close that goal. If unsuccessful, recover once, verify original state,
and use the last attributed kernel messages/initialization call or exception to
choose the next implementation change. Do not repeat unchanged black-screen
trials or infer a USB fault before reaching USB initialization. Preserve results
and old history in #344/#346/#348 and the repo memory before proceeding.
