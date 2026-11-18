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
