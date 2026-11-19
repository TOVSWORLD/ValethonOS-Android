# Next milestone execution plan

## Direct test complete; original Android restored and verified — November18,2026

Owner approved staging/test explicitly. One direct candidate p5 write/readback,
one normal-loader boot and full300s observation ran from original TWRP. No kexec
jump, recovery/bootstrap/bootloader write or automatic trial retry. First read-only
preflight size mismatch was preserved; exact-size reads and strict full-hash
recheck passed before the sole candidate write.
No target endpoint appeared and zero capture bytes arrived. Selected-port metadata
shows five boot-chain enumerations about65.6–65.8s apart. This establishes repeated
returns to the boot chain, NOT reset cause, Linux entry, PID1 or a panel fault.
Owner was not watching; visual result is UNKNOWN, not a confirmed blank screen.
Do not repeat this test solely to recover that observation. Direct boot did not
yet achieve display and does not
invalidate previous successful maintained Linux/PID1/USB/storage RAM boots.
After observation, original FACTORYM helper ran exactly once and returned to
original TWRP. Original p5 restored once with full readback; p6 unchanged. Original
Android boot/config/recovery, different completed boot and normal ADB all passed.
No more owner power steps needed. Current installation is original Android.
Next compare direct-loader runtime entry/DT/initrd fixups with working boot and
successful RAM-entry contracts; find a concrete discrepancy before another test.
Do not repeat unchanged candidate, guess panel timings or reopen logging as a gate.
Receipt direct-boot-runtime-result.json; private checkpoint out/display-direct-1.

## Direct-loader test prepared; lab staging approval pending — November18,2026

Owner authorized setting up/running a direct-loader comparison, accepting recovery
restoration. Fresh enforcing display component and direct16MiB boot image built;
exact installed/original LK static audit and unchanged board-resource comparison
pass. Same authenticated PWM Image/panel/MM0/GPIO/policy; only initrd location and
fresh direct identity differ in chosen. All1025 tests pass, no skips. Existing
VM proof reused for unchanged kernel/runtime/policy. No native trampoline/deadline.
Original Android boot/config/recovery and pinned original helper sources verified
read-only. Planned procedure: original TWRP identity/rollback preflight; one exact
p5 write/readback; one bootloader-path boot and bounded observation; return to
original recovery; one original p5 restore/readback; verify original Android.
No recovery/bootstrap/bootloader write and no automatic trial retry.
Automatic review rejected transferring images, nonce, selector/config and recovery
tools to the isolated existing SSH lab because that payload/destination required
specific user approval. Approval requested; no staging, reboot or tablet write.
Local prepared package out/display-direct-boot-1; controller out/display-direct-1.
Receipt evidence/display-pipeline-source/direct-boot-preparation.json. Never flash
the earlier consumed-nonce offline comparison in display-direct-boot-review-1.

## Direct-boot comparison selected for preparation — November18,2026

Owner questioned warm kexec handoff and requested a direct boot to remove that
variable. Do not repeat the unchanged RAM jump or turn missing diagnostics into
another logging milestone. Historical normal-boot failures predate later kernel,
RAM and display fixes; they do not rule out a current-candidate comparison.
Exact archived LK audit establishes no nonpersistent fastboot boot command.
Current Image fits selected original LK capacity; an offline16MiB Android boot
package round-trips the same Image/initramfs and relocates chosen initrd pointers
to the existing direct-loader layout, with required DT alignment. This is only
packaging feasibility, NOT loader execution, a fresh test candidate or admission.
Private comparison: out/display-direct-boot-review-1. It reuses a consumed nonce
for offline comparison only and must never be flashed as a new experiment.
Direct boot bypasses the native trampoline and its31s deadline. Automatic return
to original Android is NOT qualified: original p5 must be restored before normal
Android can boot. Recovery p6 remains untouched. Next prepare exact current-loader
handoff validation and current original-recovery/restore procedure, fresh nonce,
then present one concrete direct-boot test and return plan before any p5 write.
No new physical test authorized or armed. Scope11 result remains failed display,
verified automatic Android return, Power untouched; no valid target status.

## Scope11 actual result — November18,2026

Owner saw Android home with no test banner and confirmed Power untouched.
Display remains failed. One protected source boot/restore and one RAM jump ran;
original Android returned with original boot/config/recovery checks and normal
ADB passing. Scope11 consumed; no retry or new test authorized.
The selected USB endpoint delivered120 bytes that fail the display-status
magic/version check; no valid target status or kernel snapshot was received.
Do not claim this attempt proves target PID1, pinconf success or a new display
failure cause. Existing kernel/PID1/USB/storage achievements remain historical
successes. Saved pstore has no maintained-release/panic evidence for this attempt.
Next audit existing packet provenance and active display DMA/resource behavior
against working source; establish a concrete cause before another candidate.
Do not redesign logging or repeat an unchanged experiment.
Receipt: evidence/display-pipeline-source/pinconf-runtime-result.json.
Raw data: out/display-pinconf-trial-runtime-1/jump (private).

Boot sequence explained to owner: Amazon -> Lineage/source Android boot ->
protected original-boot restore -> RAM jump (no Amazon logo) -> test display
if working -> automatic reset -> Amazon -> Lineage -> original Android home.
No test banner was observed at the RAM-jump stage. Display remains the current
intermediate outcome; usable maintained Android remains the major outcome.

## Scope10 result and pinconf correction — November18,2026

MM-power correction took effect: DRM matched ovl/rdma/color/ccorr/aal/gamma/dsi,
OVL/RDMA joined IOMMU group0 and larb0 bound. Still no framebuffer/banner.
242 target records/18236 bytes arrived caught up without loss/error. Android
returned with original installation checks; owner Power untouched, no bands.
Scope10 consumed, one source boot/restore and one load/jump, recovery untouched.
Actual next error: pin_config_group_set failed for group43. Our panel group
requested slew-rate=1; pinned ACK generic parser maps this to SLEW_RATE, which
mtk_pconf_parse_conf does not support (default-EINVAL). Actual dispatcher C
test reproduces the rejection and accepts LEVEL0/1, the output-low/high mapping.
Owner challenged deviation from working behavior. Exact working4.9 source
shows SLEW_RATE is a vendor GPIO-direction alias, not pad-slew programming;
output-low/high already select output direction. Actual working dispatcher/
helper C comparison preserves final levels/direction with or without that alias.
Correction removes only the redundant unsupported request; GPIO levels, PWM/MM0, kernel
Image, enforcing policy and working capture remain. Fresh nonce/scope11
package and load-only client built; all 1021 tests and seven entry/VM controls
passed. Exact unchanged Image VM proofs reused. Final offline controller
validation passed. Scope11 ready, unapproved/unconsumed; scope10 consumed.
No new tablet action/approval. Raw scope10 capture/inspection stays under
out/display-mm-power-trial-runtime-1. Receipts mm-power-runtime-result.json
and pinconf-correction-preparation.json preserve result and source proof.

## Scope9 result and MM-power ancestry correction — November18,2026

PWM-corrected scope9 still had no framebuffer/banner.229 target records/16439
bytes arrived caught up without loss/error; LP8557 errors are gone. Original
Android returned and installation checks passed; owner Power untouched, no
banner/bands. Scope9 consumed; one source boot/restore and one load/jump.
The tested DT still has /soc/syscon@10006000 status=disabled, inherited from
build_lab_log_dtb.py DISABLED. Its power-controller child provides domain0/MM
required by the display pipeline, so the provider cannot populate.
Correction implemented locally: enable that parent/controller and only MM0,
disable the other seven domains; verify MM_SEL clock51 and selected-device
ancestor availability. Pinned mtk-pm-domains.c probe iterates AVAILABLE domain
children, so disabled unrelated domains are not initialized. No new kernel or
capture change: use exact PWM Image60f8780 and existing two generic VM reports;
fresh nonce/component and scope10 package/control qualification passed:1018
tests, seven controls, final offline validation and load-only client compiled.
Fresh scope10 is ready for owner availability, unapproved/unconsumed.
No new tablet action or approval. Raw scope9 logs private under
out/display-pwm-trial-runtime-1/inspection-private. Receipt pwm-runtime-result.json.

November18,2026. **Achieved on Douglas:** maintained6.18 initialization,
controlled enforcing PID1, fresh USB identity and read-only internal eMMC.
[Actual storage receipt](../../evidence/independent-recovery/ack-storage-readonly-runtime-result.json).
The kernel read exactly16MiB from original boot p5, matched its known SHA-256,
and sent fresh VSTORE01 success over the selected physical USB path. Android
returned with original boot/config/recovery and normal ADB checks passing.
Owner confirmed Power untouched; automatic Android return observed. Exact reset
cause remains unqualified.

## Three intermediate outcomes agreed with the owner

1. Display and backlight, including required clock/pin/power support.
2. Touch/input.
3. Android graphics and userspace integration.

Then the major outcome: maintained Android reaches usable setup/home with
SELinux enforcing, USB/ADB and a verified return path. This is a sequence of
outcomes, not a promise of three physical tests. Provider source/build steps
stay inside the first outcome; do not promote them to more minor milestones.

## PWM correction implementation — November18,2026

Owner authorized replacing the incorrect LP8557 dependency. DT now connects
panel to pwm-backlight/DISP_PWM0, pin59 function1,39385ns period from1024
26MHz clocks/divider0; GPIO43 remains solely panel-owned. Old LP8557 nodes
are disabled, no backlight I2C probe enabled. Exact main26M/MM suppliers and
builtin BACKLIGHT_PWM are required. Pinned ACK pwm_bl.c confirms referenced
off backlight remains off until its panel consumer enables it.
Builtin PWM kernel source616de1891cbb2af1e89fa651ec68e5feedd54616/run44273014513
passed; pwm_bl.o and its Image/config/map hashes are verified against the
GitHub artifact digest. Only compiled config delta is BACKLIGHT_PWM=m -> y.
Corrected DT built with actual new config preserves RAM/reservations. Both
enforcing VM modes passed on the new Image;1016 tests pass without skips.
Fresh unchanged capture PID1 with new nonce built in out/display-pwm-initramfs-1.
All seven entry/VM controls and exact final offline controller validation pass;
load-only client compiled. Corrected scope9 candidate is ready for owner
availability. Do not use old scope8 package/approval.
Fresh scope9 only; scopes7/8 consumed. No new tablet action or approval.
Private checkpoint: out/display-pwm-1/resume-private.json.

## Actual scope8 display diagnosis — November18,2026

Fresh VDISP002 plus VKMSG001 delivered233 target-kernel records/16817 bytes,
caught up with no truncation/ring loss/read error. Error capture is achieved;
no separate logging milestone or repeat is needed. fb0 still timed out.
Concrete target error: lp855x0-002c cannot read register0x00, returns-6/ENXIO,
then fails pre-init/config. Backlight registration blocks the panel path.
Underlying I2C/power cause is NOT yet established; do not claim a rail fix.
Source boot/restore passed; original Android returned with boot/config/recovery
and normal ADB checks passing. Owner confirmed Power untouched and no banner/bands; automatic return observed.
Scope8 consumed; one source boot/restore and one load/jump, no recovery write
or automatic retry. New trial requires concrete correction/fresh qualification.
Private runtime out/display-errors-trial-runtime-1; parsed errors in its
inspection-private directory. Public receipt error-capture-runtime-result.json.
Read-only returned-OS check:0-002c device exists but has NO bound driver.
lcd-backlight instead binds leds-mt65xx. Saved actual working DT led_mode=5;
pinned working enum/callback proves CUST_BLS_PWM -> disp_bls_set_backlight ->
DISP_PWM0,1024 period counts/divider0. Mandatory LP8557 panel dependency is a
confirmed implementation error, not proof the working backlight rail is absent.
Next correction: use display-PWM backlight and make BACKLIGHT_PWM builtin
(current display Image has it modular). Keep existing error capture, no logging
requalification. Working-backlight-path-correction.json pins source/observations.

## Display error-capture correction — November18,2026

Owner authorized fixing the actual display attempt's missing target errors.
Scope7 sent VDISP001 only: storage_init.c never opened/read /dev/kmsg in that
branch. Saved pstore/source console contains old Android/handoff output, not
the maintained kernel's display probe errors. Do not claim those errors exist.
Owner's current-OS loading animation is the working panel/backlight/graphics
reference; preserve and compare its pinned driver/board setup.
New candidate keeps the exact display Image/DT recipe/enforcing policy, sends
fresh VDISP002 status first and a bounded VKMSG001 kernel snapshot afterward
over the owned USB endpoint. No ACK/full-stream prerequisite or debugfs.
Explicit read error, truncation, ring loss and deadline state; raw output private.
Actual capture C read real kmsg under enforcing policy in both VM modes;1014
tests pass without skips. All seven entry/VM controls and final offline
two-stage controller validation passed; load-only client compiled. Candidate
is ready for fresh owner availability.
Fresh scope8 only; scope7 stays consumed, no new hardware action/approval yet.
Private inputs: out/display-errors-{1,initramfs-1,bundle-1,client-1}.

## Display runtime result — November18,2026

Scope7 consumed one protected source boot/restore and one load/jump on source
d5596c9. Fresh120-byte VDISP001 received on selected physical USB: stage1,
flags1,error-110. Enforcing display PID1 ran, but fb0 did not appear within the
bounded probe; banner was not written. Display milestone NOT achieved. Original
Android returned; original boot/config/recovery and normal ADB checks passed.
Owner confirmed no banner/bands and Power untouched throughout; automatic
Android return observed. No recovery write or automatic retry.
Receipt: evidence/display-pipeline-source/functional-runtime-result.json.
Private trial: out/display-functional-trial-runtime-1. Do not replay scope7 or
repeat logging/storage. Next source work audits display component/provider
binding and dependency closure; require a concrete fix before another trial.

## Display/backlight implementation in progress

The DRM master/gamma/mutex port and TPV-only panel are implemented;999 tests pass.
Working boot data/source resolve TPV/MP, power43/reset83 and LP8557 register-based
backlight. Source tables match compiled legacy C. Full hosted compilation and the generic enforcing-policy VM regression passed.
DT dependency closure and a display-only PID1/RAM bundle are implemented; final
controller/package qualification and the attended visual test remain.
No display pass is claimed; no new physical test has run. Existing source pins,
implementation and build contract are in
[display integration](../../projects/firetabs-android/kernel/display-port/README.md).

## Next execution: providers needed by display/touch and Android

Advance the existing order to #18 clock/reset, then #19 pinctrl/EINT and #20
PMIC/power domains, feeding #329 display/backlight, #330 touch/input and #331
graphics. Use the working4.9 source and consolidated
[hardware contract](DOUGLAS-HARDWARE-CONTRACT.md) to carry the actual board's
clock parents/rates, reset ownership, pin groups, rails and power sequences into
the maintained tree. Reuse existing source/build/VM work and the proven eMMC/
USB paths. Their success qualifies the resources they used, not every provider
or peripheral. Prepare a functional display/touch candidate rather than repeat
standalone proof of kernel/PID1/USB/storage or require complete log streaming.

The major outcome remains #333 / phase #24: a reproducible maintained-Android
ValethonOS build reaching setup/home with usable display/touch, enforcing SELinux,
USB/ADB and a verified return path. Pin Android/Binder/firmware/HAL/graphics inputs
and the supported update/security baseline before claiming that outcome.
Maintained Android userspace/init/adbd integration follows the existing provider
and display dependencies; the interim Lineage installation is the development/
recovery environment, not that milestone.

## Consumed storage trial and boundaries

Scope6 used one protected source boot, one original-p5 restore/readback, one
native load and one RAM jump; recovery untouched. Read-only p5 digest/status
acceptance passed. No userdata mount, block write/ioctl, general filesystem,
storage performance or writable-storage qualification is claimed. The exact
[prepared template](../../evidence/independent-recovery/ack-storage-readonly-authorization-template.json)
is historical and consumed. Do not replay it or any earlier scope.

Preserve RAM exclusions, firmware reservations, enforcing policy, original boot
restoration before any future RAM jump and bounded read-only return checks.
Prepare/qualify a fresh exact package before requesting the next attended device
test. No logging-only prerequisite; incomplete custom log-record transfer stays
a non-blocking follow-up under #348.
