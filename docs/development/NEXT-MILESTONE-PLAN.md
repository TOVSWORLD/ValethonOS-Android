# Next milestone execution plan

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
