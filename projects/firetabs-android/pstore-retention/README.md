# Existing-kernel console retention test

The next proposed test uses the working installed 4.9 kernel and its existing
pstore backend. The separately compiled source-kernel candidate is not deployed.

Read-only preflight passed: original full boot/config hashes match, pstore console
is enabled, console loglevel allows the marker, the mounted pstore directory is
empty, and active ramoops parameters match the existing DT reservation
`0x44410000 / 0xe0000` with a 64 KiB console. The legacy console reservation is
separate at `0x44400000 / 0x10000`. Normal UID2000 ADB was restored. No marker or
reboot has run. This does not prove firmware retention or authorize reusing the
region in another kernel/DT/recovery configuration.

`scripts/run_pstore_warm_reboot.py` runs locally through the existing private lab
SSH argument file. Default mode only preflights and restores normal adbd. Execution
requires fresh approval bound to the runner hash, original full boot hash, one
marker write, one reboot and current owner availability. Its approval file is
atomically consumed before any device mutation. It never retries a write/reboot.

The proposed execution writes one unique test line through `/dev/kmsg`, confirms
that exact source line, requests one ordinary `adb reboot`, uses a 240-second polling window
(with bounded command/cleanup timeouts) for the same installed Android with a changed boot identity, revalidates the boot
and backend, retrieves only matching `console-ramoops` lines, then unroots adbd.
No image flash, module load, experimental kernel jump, failure injection, policy
change or pstore deletion. PMSG/account logs and nonmatching console content stay
on the device. The owner may need to unlock the tablet after restart; lack of a
normal return stops the run for owner attention, with no second reboot.

Success requires exactly one attributable marker after that software reboot.
Absent/nonunique markers are inconclusive: firmware overwrites, ring-buffer wrap
or a boot-time consumer could remove evidence. This test cannot establish power-off
retention, failed-handoff readout or compatibility with the older TWRP reservation.
It does not close #346/#348.

```sh
python3 scripts/run_pstore_warm_reboot.py \
  --ssh-args out/lab-ssh-args-private.json --output /path/new-private-preflight
# Only after separate exact approval and availability:
python3 scripts/run_pstore_warm_reboot.py \
  --ssh-args out/lab-ssh-args-private.json --output /path/new-private-runtime \
  --authorization /path/new-exact-approval.json
python3 -m unittest discover -s tests -p 'test_pstore_warm_reboot.py'
```

The transport verifies an explicit shell status trailer because this older ADB
exec-out path can return host status zero for a failing target command. Twelve
mocked controls cover no-write preflight, one-shot success, missing marker,
write failure, failed unroot, wrong source/target, reboot-transport uncertainty,
return timeout, invalid/reused approval and bad status trailers.

## Hardware result — November 10, 2026

The approved test passed once: one marker write, one ordinary reboot, exactly one
retained line byte-identical to the source marker. Boot identity changed; normal
Android returned; full original boot/config and backend geometry reverified;
UID2000 ADB restored. Approval consumed. No new Image/module or kernel jump.
See `evidence/independent-recovery/pstore-warm-reboot-runtime-result.json` for
marker-only evidence and private-archive hashes. Failure/power-loss retention and
independent older-recovery readout remain unqualified; do not rerun this baseline
without a new reason and exact approval.
