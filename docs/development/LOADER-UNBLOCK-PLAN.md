# Loader retained-checkpoint delivery plan

Owner direction: finish one usable candidate; component test counts are not delivery.
Current device baseline is trial7 complete, original bootstrap/full boot/recovery
verified, TWRP unarmed. No physical step is authorized by this source plan.

## Latest owner constraint — complete candidate and positive logging

The next owner-assisted tablet test must use a complete best-supported kernel
candidate with logging positively confirmed beforehand. Do not schedule a separate
partial diagnostic-kernel or observer trial. Trial8 remains held.

Qualify as much of the collection path as possible using existing retained evidence
and the already-running known recovery, subject to the existing read-only scope.
Recovery logs can qualify only the exact recovery collection transport; they cannot
qualify the custom PID1 USB producer or retained-mailbox writer. Do not borrow that
qualification across backends. A new control boot is not selected by this plan.
If the intended candidate logging path cannot be positively demonstrated without a
separate physical boot, record that concrete dependency before proposing a test;
do not silently substitute a source/model check or another blind trial.

Prepare the complete candidate offline: coherent kernel/config/matched DT, enforcing
ramdisk/policy, enabled compatible logging transport, exact manifests and guarded
rollback. Only a complete changed review satisfying the logging prerequisite may
advance to fresh exact approval and availability. Current logging remains
unqualified; this owner constraint does not clear the code hold.


1. Integrate one runtime frontend. Discover the current device/card binding without
   lazy initialization; initialize once from an immutable descriptor; dispatch mode,
   redirected read and final handoff records on the private module stack.
2. Resolve resident placement. Redirect console formatting to a return-only sink;
   reclaim only console code/data demonstrated unreachable by static references and
   the original mode/read matrix. Preserve globals, GPT/flag/string helpers and the
   recovery path. Link bridge, hash/cache bindings, descriptor and hook replay there.
3. Validate the complete linked path. Exercise load/hash/cache publication, actual
   selected-field reads, writer initialization, checkpoint emission, register/flag/SP
   replay and failure stops. Explicitly identify modeled hardware and existing raw
   data-driver termination risk; never promote those to hardware acceptance.
4. Package one fresh candidate and observer, with independent manifest/prefix/seed
   checks. Prepare guarded install, one-arm collection and current-hash-bound rollback
   for both supervisor/manual outcomes. Preserve TWRP bootstrap repair.
5. Synchronize PR453/346/344, pass five distinct exact-head checks, and present the
   complete changed review. Only then request exact physical approval/availability.

Exit: a complete concrete candidate/recovery review, or an evidenced blocker that
cannot be resolved by authorized local source work. No unchanged trial/build loops.

## Execution outcome

Steps1–4 are implemented in the complete runtime frontend, console-owned bootstrap,
full-path validator and exact fresh-nonce candidate/private command package. The
trial review records residual hardware risks rather than treating model assumptions
as qualification. Step5 records final PR/check synchronization, then owner review and
availability under the standing physical-trial rule. No tablet action has occurred.

## Owner redirection — use a demonstrated baseline before another custom trial

Trial8 is held, unarmed, after the owner requested research into known/proven routes.
The original [Douglas port report](https://gitlab.com/postmarketOS/pmaports/-/merge_requests/1304)
explicitly reports boot/display/touch/USB networking with Amazon's vendor kernel.
The [Douglas device recipe](https://github.com/hexdump0815/pmaports-amazon/blob/main/device-amazon-douglas/deviceinfo)
uses ARM64 and the established v0/2048-byte boot-image layout. This supports a
vendor-stack positive control, not a claim of working modern mainline support.

Read-only comparison of our actual backup confirms an ARM64 kernel and text_offset
0x80000. The current mainline Image has text_offset0; its entry must follow its own
header, not copied legacy constants. The current exact diagnostic DT disables the
USB controller and PHY, so absent USB is not evidence that the kernel never entered.
The public vendor reference supports SELinux policy30 while our current diagnostic
policy is33: blindly combining that ramdisk with the legacy profile is invalid.
The exact policy ceiling of the separately built owned normal kernel is not yet
proved. No enforcement/security bypass or old OS installation is selected.

The next concrete work is an offline compatibility profile for a self-contained
logging control using the already-booted matched kernel/DT and existing USB driver:
1. Preserve the known image/DT/loader route and determine its userspace/policy ABI.
2. Prepare only the minimal compatible enforcing diagnostic ramdisk, reusing the
   existing host log reader. Mount no system/userdata and preserve recovery.
3. Demonstrate the control's boot packaging and source/ABI constraints before a
   complete changed physical review. Do not transplant a stock DT into mainline.
4. Establish host-captured kernel logs on that positive control; change one kernel/
   DT dependency at a time toward the maintained branded platform.

The old kernel is a temporary diagnostic reference. It does not meet the final
supported/updated-platform goal. Trial8 artifacts are retained as a fallback, not
selected or awaiting an approval request. No build, device access, flash, helper,
arm or reboot was performed for this research. See the sanitized
[comparison](../../evidence/independent-recovery/proven-douglas-baseline-result.json).

## Measurement repair — required before another kernel trial

No project-built kernel has a confirmed tablet boot or a verified kernel log.
HOSTCONTROL is a preinstalled fixture, not execution evidence. A loader checkpoint
cannot qualify kernel entry. Recovery return cannot establish the reset cause.

The physical candidate installer, observer installer and supervisor arm entry points
now stop before device preflight while the measurement path is unqualified. There
is no command-line override or receipt boolean that clears this hold. Read-only
collection and the existing original restoration paths remain usable. Trial8 stays
held. This is a stop against blind trials, not a completed positive control.

Follow this sequence; each step has an observable exit:

1. Finish the offline compatibility profile for the already-booted matched kernel/DT
   and minimal enforcing diagnostic ramdisk. Establish the exact policy ABI and USB
   driver requirements. Do not build another custom kernel to calibrate the test.
2. Prepare a separate complete control review: exact component hashes, boot layout,
   fresh nonce, actual host collector, one-trip instructions and guarded rollback.
   Replace this unconditional hold only with a narrowly scoped control admission
   validator in that review. Fresh exact approval and availability are required.
3. Historical proposal only, superseded by the latest owner constraint above: a
   separate known-kernel control boot is not selected. Any eventual qualification
   must exercise the actual physical collection path.
   Accept only fresh nonce-bound raw kernel output, with a kernel boot record
   matching the selected kernel release. Verify wire framing, sequence, terminal
   completion and raw digest independently. Empty output, host fixtures, loader
   records, approximate screen recall and modeled execution all fail qualification.
4. Bind the accepted qualification to the collector/producer versions and transport.
   Admit a new kernel only with its observation transport enabled and compatible.
   USB qualification cannot qualify the retained-mailbox backend. A silent trial is
   an unobserved measurement and stops kernel iteration; it is not a kernel failure
   diagnosis. USB output still cannot prove execution before USB initialization.

Failed partition-size validation now preserves the existing response privately,
with expected/received lengths and its digest, without retrying or trimming it into
an accepted image. Retention is capped at32MiB. Failed output has no valid report or
rollback image. This improves future diagnosis; discarded historical responses
cannot be reconstructed and their causes remain unknown.

## Offline capture acceptance implementation

`scripts/assess_kernel_log_capture.py` independently replays an existing private
VLOG0002 raw capture through the original bounded receiver. It requires exact fresh
nonce, frame ordering, terminal completion, receipt counts/digest and a kernel
facility0 Linux-version record matching the expected release. It rejects host or
loader text, userspace banners, empty/truncated/trailing captures and stale nonce.
It opens no device and exports no raw banner. Even a valid synthetic capture returns
physical_origin_verified=false, device_qualified=false and test_admission=false.
The physical hold is unchanged. Five synthetic regression controls passed.

Concrete unresolved dependency: neither custom USB PID1 nor retained-mailbox writer
has actual hardware output in the archived trials. Offline validation can reject
bad evidence but cannot manufacture positive logging. Recovery ADB logs use a
different producer/transport and cannot close this dependency. No separate control
boot or new physical procedure is selected. The complete next candidate cannot be
presented as meeting the owner's positive-logging prerequisite until attributable
hardware evidence for its chosen path exists.
