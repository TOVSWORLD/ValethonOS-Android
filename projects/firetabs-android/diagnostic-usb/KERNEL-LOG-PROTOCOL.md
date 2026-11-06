# Trial kernel-log transport protocol

Updates #346. `kernel_log_stream.h` implements the bounded device producer;
`scripts/kernel_log_protocol.py` implements durable receipt and an actual
nonblocking raw TTY fd adapter. The separate private lab PID1 now wires the producer to validated kmsg and
duplex ACM adapters. Physical USB and the combined boot image remain untested. No existing
admission flag is changed. A test peer is not an observed tablet kernel.

Wire bytes: `VLOG0002`,32 raw nonzero nonce bytes, then records with big-endian
uint32 sequence and uint32 length followed by payload. Sequence starts zero;
records contain1..8192 bytes, total payload at most256KiB. A zero-length record
at the expected sequence is the explicit successful end marker. Wrong identity,
sequence, bounds or premature EOF cannot produce complete=true. Raw capture,
nonce and invalid input remain private. The nonce must be unique to the selected
exact image/trial manifest; it is attribution, not cryptographic authentication.

The host requires a fresh owned0600 regular output fd with no shared hard links.
It fsyncs the identity header before returning `VACK0002` plus nonce, then fsyncs
each complete record. After fsyncing the terminal frame it sends `VDON0002`
plus nonce. The producer waits for that exact final receipt before successful
return and gadget cleanup, so unbind cannot race unretained terminal bytes. The producer sends no log records before the exact ACK.
ACK proves receipt of the identity header only; it never authorizes failure
injection. Intentional failure must wait for separately reviewed attributable
kernel records and a durable host receipt. No crash/reboot interface is provided.

The TTY adapter requires an already opened caller-owned nonblocking raw9600,
8-bit/CREAD/CLOCAL/no-flow/no-hangup TTY. It does not discover/open ports, change
termios or close the caller's fds. select/read/write attempts use a shared deadline
and retry budgets. File writes and fsync can still stall in the host kernel;
a successful receipt also checks elapsed time after sync, but cannot preempt that
syscall. API-level read callbacks must obey their own nonblocking/deadline contract.

The producer similarly requires bounded send/ACK/read and deadline callbacks.
The actual lab kmsg adapter treats EPIPE as lost evidence, not a clean end. EAGAIN
is not silently successful. Zero means an explicitly selected clean snapshot end;
live duration/end policy must be implemented by the actual kmsg adapter. A real
failure that disconnects the stream leaves incomplete evidence; preserved records
must not be advertised as complete first-kernel coverage. A failure before USB
initialization is outside this proposed transport's coverage.

Verification exercises the actual C producer under ASan/UBSan against the Python
fsync receiver, arbitrary binary records/split reads, invalid identity/sequence/
length/truncation, deadline/sync failure and an actual software PTY round trip.
No tablet USB log stream, SELinux policy, endpoint binding or runtime gate is
qualified by these tests. Remaining integration is real engineering work.
