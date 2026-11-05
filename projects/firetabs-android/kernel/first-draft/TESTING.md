# First draft test protocol — results before recovery automation

This is a review protocol, not permission to install or boot. No trial is armed.
The exact draft package, independent layout/hashes and retrieval checks must be
reviewed before fresh owner approval and availability. Prior approvals are spent.

1. Identify one complete package by Image/config/DT/ramdisk/full-image hashes and
   its fresh nonce. Retain the original full boot/recovery backups. Confirm the
   actual candidate's logging paths and coverage limits. Source/VM success is not
   positive target logging and must not be labeled as such.
2. Prepare the existing USB receiver on the selected physical connection, with
   durable private output and the exact candidate nonce. It captures only; it does
   not reboot the tablet, invoke a return helper or trigger an intentional fault.
   A kernel boot record must match the exact draft release. Completed framing and
   matching nonce/counts/digest are checked with assess_kernel_log_capture.py.
3. Perform one normal full-candidate boot under the final approved procedure.
   Observe the receiver and allow the logging window to run. The kernel uses
   panic timeout0, no explicit failure injection or automatic reboot request.
   The inherited watchdog service remains necessary; no guarantee is made that
   hardware cannot reset. Never infer reset cause from a logo or black screen.
4. Return to the existing recovery using only the separately reviewed known route
   when needed. Recovery is a way to retrieve results, not the measurement goal.
   Do not repeat the boot or rearm after silence. Do not start an automatic return
   loop while useful logs may still be arriving.
5. Run the existing read-only retained collector once. It verifies recovery,
   aliases, whole recovery hash, immutable candidate prefix and nonce-bound seed,
   then decodes the boot-tail slots. Preserve the full post-test boot image and
   raw records privately. HOSTCONTROL is not kernel output; loader records are
   not kernel entry. Failed-size/transport evidence is preserved without retry.
6. Copy the evidence archive to the controller and verify its digest before any
   original-boot restoration. Report the last actual kernel/initcall/driver line,
   errors, record sequence/size, observed USB endpoint and owner timing separately.
   Use validated current-image hashes for the already-reviewed original restore.
   Leave recovery running after verified restoration; no automatic reboot.

Acceptance: a fresh attributable kernel record with the selected release and
candidate nonce, retrieved through the real path. Record whether PID1, enforcing
policy, UDC bind and user-visible functions actually ran. Partial logs are useful
failure evidence, but do not become a complete transport or OS acceptance pass.
If neither backend yields a kernel record, report the run as unobserved; do not
call it a proven kernel failure, recovery success criterion or permission to run
another blind variant. Positive hardware logging remains a required open gate.

Coverage: USB begins only after userspace policy/configfs/UDC initialization.
Retained snapshots begin after the kernel eMMC driver and late-init worker, at
5-second intervals for12 commits. Neither proves earliest instruction execution
or captures a hang before its prerequisites. No guessed reserved-RAM logger or
unqualified pstore address is used. Collectors never read system/userdata/accounts.
