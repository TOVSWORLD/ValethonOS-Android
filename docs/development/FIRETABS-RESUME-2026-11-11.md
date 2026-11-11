# FireTabs resume checkpoint — November 11, 2026

Paused at the owner's request for a gear switch. No new hardware test is ready
or authorized. No background build, capture, load or reboot was started during
the final audit. Resume with offline analysis, not another tablet jump.

## Confirmed device state

Owner returned the tablet with a hard boot. November 11 read-only verification
passed: Android boot complete, original full boot image, original running kernel
configuration, recovery unchanged, normal unprivileged ADB restored. The running
original kernel has kexec disabled. The diagnostic source kernel is no longer
running. The previous source boot and one-jump approvals are consumed.

Original boot SHA256:
`08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e`.
Original config SHA256:
`b087199622287207923f9449eedd820ee1940ee82157e77648e36b4b959f3859`.
Recovery SHA256:
`3c9bafcbfc4a0b12cb1a3f372af0cfd49ffec5b3e01a0b070465b49bd8435f11`.

## Latest experiment and what it proves

The source-console trial booted its prepared source kernel once and restored
the original full boot on flash before jumping. A fresh kernel-only marker
arrived over source USB ACM before loading. One native load verified; one
orderly jump was requested. Target USB never enumerated during 300 seconds.

20,957 source-console bytes were preserved. The fresh portion proves Android
init received `reboot,valethon-kexec` and entered shutdown. It does not prove
kernel_kexec entry, CPU-off, relocation or target entry. Source USB disappeared;
absence of later messages cannot locate the failure. This is confirmed
owner-assisted return, not independent automatic recovery.

The first bundle preparation refused a console token placed after bootloader
arguments. The corrected parser removes exactly that token without changing
other argument bytes/order. Source boot was not repeated. Collector finalization
failed, but the raw host capture was salvaged, fsynced and independently
hash-verified. Disconnect cleanup and missing-receipt salvage are now fixed.
The last focused validation ran 37 Python controls, all passing. These fixes
did not trigger another hardware run.

[Actual runtime receipt](../../evidence/independent-recovery/source-usb-handoff-runtime-result.json).

## Final offline audit findings

1. **FunctionFS can remove the combined gadget when ADB closes.** Exact build
   source: ffs_ep0_release → ffs_data_closed; on last close and with
   no_disconnect false, ffs_data_reset → ffs_data_clear → ffs_closed. A bound
   configfs instance then calls unregister_gadget_item, which unregisters the
   entire gadget, including the sibling ACM function. The mount parser defaults
   no_disconnect to false. This offers a concrete explanation for losing source
   capture during init's service shutdown, before the kernel reboot route.
   Actual live mount settings and the shutdown path still need verification;
   this is not a proven cause of the tablet hang or this exact disconnect.
2. **The source console can silently lose log data.** GS_CONSOLE_BUF_SIZE is
   8192. gs_buf_put truncates to available space and gs_console_write ignores
   the returned count. The last capture contains noisy teardown messages and
   ends during init shutdown. No runtime overflow counter was collected.
3. **Potential completion-ordering race.** gs_console_thread sets req_busy=1
   after usb_ep_queue returns; the completion callback clears it. A completion
   on another CPU before the post-queue assignment could leave a stale busy
   flag and stall the stream. This has not yet been reproduced with an actual
   C interleaving harness or shown to have happened on the tablet. No driver
   patch or new Image has been prepared for it.

Exact fetched source files remain in
`out/recovery-linux-pivot/handoff-audit-2/`, notably
`drivers/usb/gadget/function/{f_fs.c,u_serial.c}` and
`drivers/usb/gadget/configfs.c`. The FunctionFS file was fetched during this
final audit; no tablet operation was needed.

## Resume in this order

1. Verify current checkout/issue status and read this checkpoint plus the actual
   runtime receipt. Do not reuse the historical approval templates: their code
   pins describe consumed trials and later parser/collector fixes changed files.
2. Finish the FunctionFS/shutdown audit. Check actual mount options read-only
   and determine whether a temporary extra ep0 reference would survive the
   relevant init service-stop phase. Opening/holding ep0, stopping adbd, or
   changing the gadget are device experiments, not read-only verification.
3. Reproduce the request-completion ordering with the actual extracted C
   functions under controlled interleavings before deciding on a kernel patch.
   Keep any queue fix separate from a claim about the handoff failure.
4. Select the smallest discriminating capture change. Candidates to evaluate:
   retain FunctionFS ownership through adbd service stop, or remove ADB from
   the source capture gadget with a bounded authenticated on-device trigger
   and rollback. Neither is implemented or selected. Console verbosity can be
   reduced reversibly to favor priority-zero handoff checkpoints, but must be
   restored on abort. Do not assume larger buffers alone solve disconnects.
5. Prepare/build/check the chosen change offline, publish the exact scope and
   return procedure, then request one concrete owner-attended test approval.
   Preserve original boot restoration before any jump and the one-request limit.

Do not replay the already-passed live logging baseline, add watchdog/retention
qualification as a prerequisite, repeat the failed trial unchanged, or infer a
specific hang stage from silence. User priority remains USB capture for faster
handoff diagnosis and forward progress.

## Retained private artifacts in this workspace

All paths below are ignored local evidence; do not publish raw logs, live DTs,
boot arguments, serial identifiers or SSH arguments.

- `out/recovery-linux-pivot/source-usb-captured-jump-runtime-1/`: actual jump
  result, USB trace, salvaged source bytes and salvage receipt.
- `out/recovery-linux-pivot/source-usb-two-stage-runtime-1/`: successful source
  boot/restore result and initially rejected preparation data.
- `out/recovery-linux-pivot/source-usb-post-return-verification-private.json`:
  November 11 successful original-state verification.
- `out/recovery-linux-pivot/source-usb-resume-target-1/` and
  `source-usb-resume-client-1/`: actual fresh target manifest/client used once.
- `out/recovery-linux-pivot/usb-console-native-artifacts-1/`: retained fixed
  Image, linked verification and build artifacts. Image SHA256
  `e74878db3abb4bca4acc18e312d66ac8648a9261ac6dff216af387676b38ecff`;
  diagnostic config SHA256
  `865d9beeb5c8c49af47aea818b341e48cbbd84f7669c0cccbc589b60d1699b31`.
- `out/lab-ssh-args-private.json`: existing connector-independent lab transport;
  use without exposing its contents. Use the direct GitHub connector for GitHub.

GitHub: TOVSWORLD/ValethonOS-Android, branch
`codex/issue-346-bounded-recovery`; active issues #344, #346 and #348 remain open.
Last published trial/fix commit before this checkpoint:
`34c3216b40158e4c28d7e871e2f4b1933c6d4ff8`.
