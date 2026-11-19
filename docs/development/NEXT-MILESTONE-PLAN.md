# Next milestone execution plan

## Shared staged testing — November 19, 2026

Owner requested grouping issues into staged tests to reduce work time. The
[shared test plan](STAGED-TEST-PLAN.md) and ordered-roadmap.json now map every
hardware issue to candidate checkpoints. T0 offline integration/package gate
feeds T1 one integrated Android boot/UI session. Selected ready T2 connectivity,
media/input/storage and lifecycle checks can run on that same image before one
final recovery. T3 full release validation follows later. The next first-home
milestone needs T0/T1, not all peripheral/soak/release gates.

Source/offline implementation readiness remains serial with one active primary
task/PR. Runtime acceptance can be co-qualified in one approved session; no
one-issue-one-boot requirement or circular331-runtime-before333-source gate.
Preserve acceptance and actual prerequisites (including335 before suspend443),
record unready checks as not_run/blocked, and do not close issues without their
actual evidence. Current standalone animated GPU/touch and original TWRP return
are verified; all helpers stopped. Next is Android userspace/composer integration
and one complete candidate, no repeat standalone cube/logging-proof gate.

## Three grouped work packages to maintained Android setup/home — November 19, 2026

Owner explicitly requested grouping the remaining steps. The next major outcome
is333: maintained Android setup/home on the observed kernel, usable display/touch,
enforcing SELinux, USB/ADB and verified recovery. Standalone animated GPU/touch
is achieved and original TWRP/retained exact p5/original p6 are verified.

1. INTEGRATE ONE ANDROID STACK (active331, feeding333): pin platform/device/ABI,
   Binder, firmware/HAL sources; connect allocator/composer/EGL, Android init/adbd
   and enforcing policy to the working maintained kernel. Resolve the documented
   T720 API compatibility limits in this integration, preserving working hardware.
   Exit: a coherent pinned source/device configuration and buildable integration.
2. BUILD AND QUALIFY ONE COMPLETE CANDIDATE: reproducible Android/kernel images,
   artifact/source manifest, offline/package/interface checks and concrete exact
   storage/backup/rollback procedure. Establish actual host capacity before bulk
   source downloads/builds. Exit: a reviewable integrated test package; obtain any
   necessary concrete resource/device-write approval only after preparation.
3. RUN THE INTEGRATED SETUP/HOME TEST: one attended end-to-end candidate attempt,
   checking setup/home, touch/graphics, SELinux enforcing, USB/ADB and recovery.
   Fix failures within these packages and repeat only when a concrete change needs
   physical qualification. Exit: recorded major outcome, or explicit remaining
   failures. Full release/update/security/peripheral/soak acceptance remains open.

These are three work packages, not a promise of three physical tests or dates.
Source changes, builds and offline checks stay internal to the packages; do not
turn each provider or repair into a new owner milestone. No repeat standalone
cube/logging proof for achieved hardware. Record new findings in existing331/333
and preserve prior failed experiments. Primary active PR456/331 remains open for
Android composer/API integration; do not claim333 or stable release complete.

## Interactive GPU milestone achieved; original TWRP verified — November 19, 2026

Owner confirms animated cube responds to taps and dragging on exact maintained
kernel candidate628a164112f5c4d09d7c55478b7e57b991933f10eb406945bf1f4502d946a34b.
The installed program rejects non-T720/software renderers and validates GPU
pixels before scanout. USB stayed connected; portable unplugged operation was
not exercised. Start prompt was not seen; record that UX detail without another
cube-only test. This qualifies standalone functional GPU interaction, not full
API conformance, measured frame rate, broad stability or Android composition.

One candidate write/full readback and one software-requested test boot ran.
The300second host observation after owner report finished. Original recovery
helper ran exactly once/exited0. Selected original TWRP3.3.1-0, retained exact
interaction p5 and unchanged original p6 verified by full bounded reads. All
workers ended. Original Android restoration remains deferred by owner direction;
no more Power steps or additional test selected. Receipt:
evidence/graphics-source/graphics-interaction-runtime-result.json.
Private final state: out/graphics-source-preparation-1/test-case-3/.

NEXT MAJOR: maintained Android boots to usable setup/home on this kernel with
working display/touch, enforcing SELinux, USB/ADB and verified recovery (#333).
Next engineering work stays within331 graphics/userspace integration: pin the
Android source/device/ABI/Binder/firmware/HAL inputs against existing audits;
integrate allocator/composer/EGL and Android init/adbd/enforcing policy; build
reproducible artifacts and a concrete storage/rollback plan; then qualify one
integrated setup/home candidate. Resolve documented T720 GLES2 limitations
against actual Android rendering/declared compatibility, without pretending the
standalone demo passes Android API/composer requirements. Carry achieved kernel,
read-only storage, display, touch and GPU forward. No repeat cube/logging-proof
gate, old-kernel detour or new standalone hardware milestone. Broader330/331 and
full333 release/update/security acceptance stay open.

## Interactive GPU rendering achieved; recovery return armed — November 19, 2026

Owner confirms cube animation and tap/drag response on exact candidate628a1641...
This qualifies the standalone functional GPU interaction foundation. USB stayed
connected; portable unplugged operation was not tested. TAP TO START was not
seen; do not invent a cause or require another cube test for that UX detail.
The300second host observation after owner report finished. It is not a measured
frame-rate/full-duration stability proof; broad stability/API/Android composer
remain open. Existing kernel/display/touch/GPU should move into Android userspace
integration toward333 setup/home, not another cube/logging-proof gate.

Original recovery helper armed once after window; owner instructed to unplugUSB,
hold onlyPower40seconds, release/wait5seconds/reconnect same lab cable. TWRP
return/p5/p6 verification pending. No Android restore or extra test selected.
Private active return supervisor77420, out/graphics-source-preparation-1/test-case-3/.

## Animated GPU cube responds to touch; USB stayed connected — November 19, 2026

Owner confirms moving cube responds to taps and dragging. This is observed
functional animated/touch-controlled GPU rendering on exact candidate628a1641...
Program rejects non-T720/software renderers and validates first-frame pixels.
TAP TO START was not seen; record without inferring its disappearance cause.
Owner explicitly says USB was never unplugged; desk-disconnected operation is
not qualified and no reconnect trip is required. Owner first-tap report started
controller's300second observation. No recovery helper is armed yet. Finish the
window, then arm exactly one original recovery helper before Power instructions;
verify retained exact interaction p5 and original p6 in original TWRP. No Android
restoration, automatic test retry or repeated cube/logging-proof gate.
Do not call full stability/API/Android composer qualified. Next is Android
userspace/composer integration toward333 setup/home, carrying working hardware
forward within331. Raw state: out/graphics-source-preparation-1/test-case-3/;
active controller93075. Signal first-tap-observed-private already created.

## First-tap desk test installed; waiting for owner tap — November 19, 2026

Owner approved staging and one attended graphics-direct-3 test. Exact selected
TWRP/retained corrected graphics p5/original recovery preflight passed. Candidate
628a164112f5c4d09d7c55478b7e57b991933f10eb406945bf1f4502d946a34b
was installed once/full readback verified; original recovery unchanged and RAM
cleanup verified. One direct boot requested after WATCH NOW. Controller waits
up to15minutes for owner's first-tap report before starting300second observation.
Owner may unplug USB after TAP TO START, carry tablet to desk, tap/drag there.
Do not create first-tap-observed-private until owner confirms actual first tap.
Screen/prompt/animation/touch reports are pending; no interaction pass claimed.
No recovery helper is armed; wait for owner to reconnect same lab cable before
arming one return helper and giving Power instructions. No Android restoration.
Private case: out/graphics-source-preparation-1/test-case-3/; active controller
session93075. Previous corrected cube case is fully returned/verified in TWRP.

## GPU cube observed; original TWRP verified; desk interaction test ready — November 19, 2026

Owner confirmed purple/orange cube after arriving late. Exact tested program
rejects non-T720/software renderers and checks rendered pixels before scanout:
first-frame GPU rendering is observed. Animation/touch/stability are unqualified
because old demo deliberately idles after90seconds and owner did not watch then.
Original TWRP3.3.1-0, exact corrected graphics p5 and original p6 are now verified.
Initial recovery wait expired with zero calls; renewed waiting preserved that
receipt and one-call limit. Helper subsequently ran once/exited0. All workers
finished; no Android restoration requested and no more Power steps needed.

Next first-tap candidate628a164112f5c4d09d7c55478b7e57b991933f10eb406945bf1f4502d946a34b
is qualified offline. TAP TO START waiting frame, up to15minutes arrival with no
repeated GPU rendering; first valid touch starts five-minute animation/input.
All hardware DT properties, kernel/libraries/enforcing policy unchanged from
observed cube. Fresh scope graphics-direct-3 expects exact retained741696e2...
Both exact-kernel VM modes and all1051 repository tests pass; original-LK,
partition/RAM checks and fresh-scope guard controls pass. Payload15,007,744B.

Prepared private package/controllers under out/graphics-source-preparation-1/
{direct-interaction-package-1,test-case-3,first-tap-lab-results}/. No actual next
owner authorization, private staging, candidate write or boot has run. Next:
obtain attendance/staging/test approval; install once from existing TWRP; owner
may disconnect USB after TAP TO START and carry tablet to desk; first tap/report
starts interaction observation. USB loss does not gate rendering. Reconnect to
same lab cable before arming recovery helper and requesting restart, avoiding
an expired helper while owner is away. Return to original TWRP. No logging gate.
Receipts: evidence/graphics-source/graphics-power-runtime-result.json,
first-tap-preparation-result.json and direct-interaction-preparation-result.json.
Android composer/setup/home remain open; do not close331 or broader330.

## GPU frame confirmed; first-tap demo compiled; recovery pending — November 19, 2026

Owner observed purple/orange cube after walking over late, without watching the
first90seconds. This supports first-frame GPU rendering beyond GBM2. Old demo
intentionally idles after90seconds, so late still/no-touch is not a demonstrated
animation/touch failure. Full interactive rendering remains unqualified.
First-tap demo now shows TAP TO START, waits up to15minutes with one rendered
waiting frame, then runs animation/input for five minutes from first valid tap.
Component6 compiled; both exact-kernel VM modes and ten graphics tests passed.
Unchanged kernel/libraries/enforcing policy and corrected two-domain DT remain
selected. Next package/controller needs fresh scope and must start observation
on owner tap, permit USB disconnect after startup for desk use, reconnect for
recovery. No next boot image is qualified/staged/installed yet.

Current recovery: initial listener timed out with zero helper launches. Renewed
only the waiting window, preserved timeout receipt, same maximum one helper call.
Owner reported restart done and booting; lab still observed experimental USB
1209:0001. Original TWRP/p5/p6 return is not verified. Existing renewed listener
is waiting; no additional software boot/install or Android restoration. Asked
owner current screen. Inspect private execution/helper receipt before acting:
out/graphics-source-preparation-1/test-case-2/ (renewed supervisor session36331).
First-tap component/VM copies: out/graphics-source-preparation-1/first-tap-lab-results/.
Receipts: graphics-power-runtime-result.json and first-tap-preparation-result.json
under evidence/graphics-source/. No logging-proof gate.

## Late cube observation clarified; next demo waits for first tap — November 19, 2026

Owner clarified they walked over just before reporting and did not watch the
first90seconds. The purple/orange cube was observed after the full five-minute
host window, when the old program deliberately idles. This confirms visible
first-frame rendering; it is not evidence of failed animation or broken touch.
Animation/touch/stability remain unqualified. Current original-TWRP return is
still pending; keep existing helper/owner instructions, no further tablet boot.

Fixed demo.c now draws the initial cube with large TAP TO START text, waits up
to15minutes for a valid first touch without repeatedly rendering, then animates
and handles touch for five minutes from that touch. Component6 compiled in the
existing approved lab; ten graphics tests passed. Both exact-kernel VM checks
are running. No next image has been prepared/staged or installed yet.
Next procedure allows unplugging USB after the prompt to carry the tablet to
the desk; graphics has no USB dependency after startup. Begin host interaction
observation when owner taps, not at boot; reconnect for original TWRP return.
Private build: out/graphics-source-preparation-1/component-6-build-private.log.

## GPU cube observed; animation/touch timing unresolved — November 19, 2026

Owner reports a purple/orange cube, still and not movable. Exact installed
program rejects non-T720/software renderers and validates GPU pixels before
scanout, so this supports first-frame GPU rendering beyond the former GBM2
failure. Animation/interaction is not qualified. Critically, demo.c deliberately
stops its rendering/input loop after90seconds and retains the last frame. Owner
observation timing is unknown; a late static frame does not establish a hang.
Asked owner to clarify timing and complete the already-instructed restart to
original TWRP. Existing one-shot return helper was armed; inspect its receipt
and selected device before further action. Do not run another test or restore
Android. Next functional test design must keep touch/animation active for the
entire owner observation window and visibly mark completion; no logging gate.

## Corrected graphics window finished; owner action pending — November 19, 2026

Corrected candidate741696e2b5c0ea6152e3ed7e65218158808d5790d629111ae3e0002aaf1b4faf
was installed once/full-readback verified and booted once. Original recovery
remained unchanged and RAM staging cleanup verified. Full five-minute window
finished. Owner screen report has not arrived, so cube/GPU result is unknown;
no graphics pass is claimed. Original recovery return helper was armed once
with a15-minute wait. Owner was instructed to note the screen, then unplugUSB,
hold onlyPower40seconds, release/wait5seconds/reconnect same cable. Screen result,
Power-untouched confirmation and selected original TWRP return are pending.
Do not install/reboot another candidate or restore Android while awaiting this.
Private helper/session state: out/graphics-source-preparation-1/test-case-2/.
Public pending receipt: evidence/graphics-source/graphics-power-runtime-result.json.
Next: collect owner result, finish/inspect existing helper, verify exact retained
corrected p5 and original p6 in original TWRP, then update result. No logging gate.

## Corrected graphics test installed and running — November 19, 2026

Owner approved staging and one attended graphics-direct-2 test. Selected
original TWRP and exact previous graphics p5/original p6 preflight passed.
Corrected candidate741696e2b5c0ea6152e3ed7e65218158808d5790d629111ae3e0002aaf1b4faf
was written once; full p5 readback, unchanged original recovery and RAM staging
cleanup verified. One direct boot requested after WATCH NOW. The five-minute
cube/touch window is running; owner observation pending. No hardware graphics
pass claimed. Return to original TWRP afterward, no Android round trip.
Private execution: out/graphics-source-preparation-1/test-case-2/.

## GPU power-domain correction qualified; next attended test ready — November 19, 2026

The failed graphics DT enabled GPU but left MFG_ASYNC6 and nested MFG7 disabled.
Pinned mtk-pm-domains.c scpsys_probe iterates available top-level children, so
it skips6 and never registers its7 child requested by GPU. This is a concrete
source-established omission consistent with GBM failure2, not proof that no
additional faults exist. The corrected preview enables just those two domains.
Direct comparison with the failed candidate confirms exactly two hardware
property changes; display MM0, touch, memory and every other hardware property
are unchanged. The exact kernel, renderer, dynamic libraries and enforcing
policy are unchanged. Fresh identity; both exact-kernel VM modes pass, all20
policy denial controls retained, all1051 repository tests pass, original-LK
roundtrip and RAM/partition placement checks pass. Payload15,007,744B fits16MiB.

Qualified corrected candidate SHA256:
741696e2b5c0ea6152e3ed7e65218158808d5790d629111ae3e0002aaf1b4faf.
Fresh scope graphics-direct-2 expects previous graphics p5 a09bbb9f..., never
touch/original p5. Disposable offline controls accept exact candidate and reject
consumed graphics scope, wrong predecessor, unapproved or missing authorization.
No actual next-test owner authorization, staging or tablet command has run.
Tablet last verified original TWRP with old graphics p5 and unchanged original p6;
owner may have disconnected/moved it. Original rollback ready; all workers ended.

Next: owner attendance/reconnect, stage corrected package and recovery tools in
existing SSH lab, preflight exact retained graphics p5 and original recovery,
install once, say WATCH NOW, test actual rotating T720 cube/touch for one bounded
window, then return to TWRP. No Android round trip or logging-proof gate.
Hardware rendering, Android composer/setup/home remain unqualified. Receipts:
evidence/graphics-source/power-domain-correction.json and
evidence/graphics-source/direct-power-preparation-result.json. Local exact state:
out/graphics-source-preparation-1/{direct-power-package-1,power-lab-results}/.

## Graphics test complete; original TWRP verified — November 19, 2026

One attended direct graphics attempt displayed the orange failure screen with
large2 (GBM device creation/surface setup), as reported by the owner. No cube or
accelerated rendering pass. Candidate a09bbb9fa8f0be11a25233510dc4dd49fc93e41f251ff975bd8ca1ca928ad042
was written once/full-readback verified and booted once. The full five-minute
window ended; original recovery helper ran once/exited0. Selected original
TWRP3.3.1-0, retained exact graphics p5 and unchanged original p6 were verified
with full bounded reads. Original Android restoration remains deferred by owner
instruction. All observation/return workers ended. Owner may disconnect/move the
tablet. Power-untouched confirmation remains unknown; do not invent it.

Next: narrow the GBM device-versus-surface return using the exact shipped source;
check MediaTek-to-Panfrost render-node discovery and the actual GPU probe before
changing clocks, kernel or policy. Stage2 alone does not identify the cause.
Keep proven display/touch and original rollback. Any next image needs fresh exact
qualification and attended execution; no repeat logging-proof gate. Published
runtime receipt: evidence/graphics-source/graphics-runtime-result.json.

## First physical graphics test stopped at GBM stage 2 — November 19, 2026

Owner observed an orange screen with a large2 and error text. No cube appeared;
GPU rendering and touch-controlled rendering are not achieved. This maps to GBM
device creation or surface setup, before EGL/shaders. Exact Mesa source shows
MediaTek display GBM creation must discover a compatible Panfrost render node.
Do not claim which subcall failed until evidence distinguishes them. Preserve
working display/touch and unchanged graphics kernel while narrowing this path.
One candidate write/full readback and one boot ran. Full five-minute window
finished. Existing USB receiver selected/opened endpoint but retained zero bytes;
that does not negate the observed stage or create a logging-proof gate.
Original recovery return helper is armed for one call. Owner was instructed to
restart/reconnect; return to TWRP is pending, no Android restoration requested.

## Graphics candidate installed; attended boot running — November 19, 2026

One graphics candidate write completed and its full16MiB readback matched
SHA256 a09bbb9fa8f0be11a25233510dc4dd49fc93e41f251ff975bd8ca1ca928ad042.
Original recovery hash remained unchanged and temporary RAM staging cleanup
verified. One direct reboot from original TWRP was requested after the owner's
watch cue. The five-minute observation window is running; physical cube/touch
result is pending. No hardware graphics pass is claimed. Return to original
TWRP after the window; no Android round trip or original restoration is planned.

## Attended graphics test authorized — November 19, 2026

Owner explicitly approved private staging and one attended graphics test in the
existing SSH lab direct-test-1 directory. Build/VM approval had previously been
insufficient for private test staging; no transfer bypass was attempted.
Selected original TWRP and exact retained touch p5/original p6 preflight passed.
First installation stopped before any partition write: ExactReadAdb admitted
partitions but omitted the existing installer RAM staging file. The durable
receipt confirms write_started=false. Preserve that receipt. The read guard now
also admits only the installer's exact /tmp/valethonos-rollback-<32 hex>/boot.img
path and full16MiB read; unrelated paths remain rejected. All9 graphics tests
pass, including full/short RAM reads and invalid-path rejection. The graphics
image itself is unchanged. The corrected installation and one attended direct
boot remain the current execution; no test reboot has occurred yet.

## Graphics candidate qualified offline; ready to load from TWRP — November 18, 2026

The next functional test is a colored GPU-rendered cube that rotates and moves
with touch. Actual non-T720/software renderers are rejected. Large failure digits
1-7 identify the failed stage without asking the owner to read tiny kernel text.
Kernel run44451450892 passed at source4d534e81905130dd496e0eba2f3034aca4beca2f.
Image c8fd42b8cad42b75246a5d757b3de80b151076fa4a6a344fcc278fe0912880f5;
only Panfrost/DRM scheduler/shmem move from modules to builtin versus proven touch.
The authenticated artifact, all17 manifest files and source merge tree verified.
Initial kernel compilation succeeded but export requested a nonexistent combined
panfrost.o; retaining three actual builtin translation units fixed it.

Mesa26.2.7/libdrm2.4.133 host tools and AArch64 runtime compiled. Mesa26.2 uses a
unified libgallium and gbm/dri_gbm.so, not per-driver DRI files; packing follows
that actual layout. All20 enforcing-policy denial controls passed, preserving
PID1 fork denial. Both virtualization modes pass the final exact kernel/component:
real EGL/Gallium/GBM loading, shared-memory RW, and denied executable memory,
fork, input write and block write. All1049 repository tests pass.
The30.2MB runtime compresses to5.6MB with kernel-supported XZ/8MB dictionary/CRC32.
The separate graphics packer places it at0x46000000 and checks the full compressed
kernel staging span, raw archive span and every observed reservation. Existing
small diagnostic packers stay unchanged. Complete payload15,007,744B fits16MiB p5.
Original-LK static audit and disposable authorization-guard controls pass.

Current tablet is original TWRP with the exact successful touch candidate on p5;
original p6 is unchanged and rollback is ready. The owner explicitly requested
preparing/loading the next test rather than returning to Android between tests.
No graphics candidate has been written or booted yet. Use new graphics-direct-1
scope; the guard expects the retained touch SHA, never assumes original p5.
Reads check exact sysfs partition size and bounded full bytes/hash, with no trim.
Next: publish final source/receipt, stage/install once from TWRP, say watch now,
run one direct graphics test, then return to TWRP without an Android round trip.
No logging proof gate. Receipts: evidence/graphics-source/kernel-build-result.json
and direct-preparation-result.json. Private qualified package/component/VM state:
out/graphics-source-preparation-1/. Primary task#331 / draft PR#456.

## Touch grid achieved; remain in TWRP for graphics test — November 18, 2026

Owner confirmed all nine touch panels turned green and that the green grid was
still displayed after the full five-minute window. One candidate write/full
readback and one direct boot ran. The original recovery helper ran once/exited0.
The original-boot restore preflight stopped at a recovery read-size check before
any write or operation receipt. Subsequent exact bounded full reads verified the
touch candidate on p5 and unchanged original p6. Owner then explicitly directed:
"Just work on the next test and load that." Keep original TWRP running and the
qualified touch candidate on p5; do not reboot to Android or perform the deferred
original restoration. Original rollback image remains ready. All helper/restore
workers have stopped. Power-untouched confirmation was not explicitly supplied.

The physical display/touch foundations are achieved. Full pixel-edge accuracy,
simultaneous contacts and suspend/wake acceptance remain open; do not close#330.
Next outcome is#331 Android graphics/userspace: source-match Mali-T720 resources,
Panfrost/Mesa and DRM display composition, build one coherent visible rendering
candidate, qualify it offline, then use the existing TWRP for its installation.
Keep current display/touch and original rollback; no repeat touch-only or logging
proof gate. No next graphics candidate is qualified or loaded yet. Receipt:
evidence/touch-input-source/touch-runtime-result.json. Private current device and
execution state: out/touch-input-1/test-case-1/parked-twrp-state-private.json.

## Touch candidate built; exact-kernel VM checks passed — November 18, 2026

The maintained Goodix kernel build succeeded in GitHub run 44438104081.
Source 1525308e981f48a6abd4a8122093f478053382a0 and workflow merge commit
ccb8f413cb657d31e2110d0296736982ee25d03f have the same tree. The downloaded
artifact digest and all 14 manifest files verified. Goodix is the only kernel
configuration change from the observed display baseline: module to builtin.
The source-backed DT uses GPIO35/EINT46, reset46, I2C0 pads75/76 and VGP2 at
3.0V with VIO18 at1.8V. RAM reservations and the corrected loader framebuffer
node survive. Enable the existing watchdog driver for inherited heartbeat;
this does not establish the prior reset cause or stable hardware operation.

The enforcing touch component compiled in the approved isolated lab directory.
All 1,041 repository tests pass in the final source regression run.
All16 forbidden-privilege compiler controls passed. On the exact new kernel,
both virtualization modes pass real virtual-evdev read-only open/idle-read,
denied ioctl, denied relabel and denied write-open checks. The first VM fixture
incorrectly assumed no virtual input device; its failed result is retained.
These results are VM policy checks, not physical Goodix qualification.

A fresh direct touch package is prepared offline. Static original-loader audit
and disposable authorization-fixture checks pass; missing approval and the
historical display scope are rejected. No real owner authorization file was
created and no tablet command was run. Original Android remains restored.
The visible acceptance is all nine large blue panels turning green as the owner
touches them. USB display status is sent before the touch window, its send result
does not gate the grid, and it cannot prove touch. No raw events are stored.
Next: publish the exact preparation, obtain fresh attendance/staging/test
approval, run one direct test, then restore and verify original Android.
No new logging proof gate. Receipts: evidence/touch-input-source/
kernel-build-result.json and touch-preparation-result.json.

## Touch/input source integration started — November18,2026

Work moved to codex/issue-330-touch-input, stacked on observed display foundation.
Read-only restored-OS metadata confirms Goodix-TS at I2C0x5d/goodix,gt9xx and
input goodix-ts; capability axes800/1280, direct multitouch. Cached186-byte
configuration exactly matches pinned public hvt groups0-3. Sensor/chip ID is not
claimed from the all-zero live-read section; it is unusable evidence.
Pinned working driver/DTS and maintained Goodix source retained. GPIO35 maps to
EINT46 (not IRQ35); resetGPIO46, falling edge from profile. Working driver sets
VGP2 analog3.0V; IO1.8V. Preserve source profile, not guessed coordinates/config.
Minimal maintained driver change adds legacy goodix,gt9xx compatible alias; its
runtime chip-ID selection remains. Dedicated touch-provider build keeps observed
display setup and makes GOODIX builtin, retaining Goodix/watchdog object evidence.
Public configuration generator reproduces the known cached186-byte profile and
rejects changes. All1035 tests pass; no new Image build or touch hardware pass yet.
Next run exact touch kernel build while preparing DT/supplies/EINT, enforcing
read-only evdev access and large visual3x3 feedback. Handle inherited watchdog
alongside this test; no new logging proof gate or physical test authorized.
Original Android remains restored; raw working-OS metadata private in out/touch-input-1.
Source contract: projects/firetabs-android/kernel/touch-port/contract.json.

## Visible display/backlight achieved; touch/input next — November18,2026

Corrected direct scope2 ran once after explicit staging/test approval. Owner
confirmed VALETHON DISPLAY TEST and labelled red/green/blue bands physically
visible. Maintained kernel/PID1 reached the actual display test. Carry this
foundation forward; do not demand another screen or logging proof before touch.
Some small error text was reported but unreadable; do not invent its contents.
Target USB endpoint appeared five times about65.6–65.8s apart. Captured120 bytes
fail the display-status header; no valid USB status or kernel snapshot. Physical
visual evidence is affirmative; the packet is NOT a valid nonce-bound proof.
Repeated boot resets, their cause, stable operation, brightness endpoints and
suspend/resume remain unqualified; full#329 acceptance is not closed.
One candidate p5 write/readback and one direct boot request; full300s observation.
Afterward original helper ran once, original TWRP returned, original p5 restored
once/full readback, p6 unchanged. Original Android boot/config/recovery, fresh
completed boot and normal ADB verified. Current installation is original Android.
No recovery/bootstrap/bootloader write, test replay or active capture/helper.
Receipt direct-fbfix-runtime-result.json; private checkpoint out/display-direct-fbfix-2.
Next agreed implementation is#330 Goodix touch/input: working source declares
I2C0x5d, reset46, IRQ35. Check active controller/config/orientation before porting;
current maintained GOODIX is modular, INPUT_EVDEV/I2C_MT65XX builtin. Prepare
visual touch feedback on the achieved display, then one fresh qualified test.
Alongside that, inspect inherited watchdog handling for repeated resets. Current
Image has MEDIATEK_WATCHDOG builtin and boot-enabled handoff support, but the RAM
bootstrap-derived DT disables watchdog@10007000. Historical watchdog candidate3
predated observed kernel entry; reuse its source/VM findings, not its old test.
Watchdog reset cause is not established and no watchdog-only/logging trial is
selected. Keep invalid USB packet tracked separately; do not reopen logging gate.

## Concrete direct-loader framebuffer-node collision fixed — November18,2026

The direct input DT already contains fb-reserved-memory@98600000, imported from
the live OS reservation map. Exact original LK callback25c54 unconditionally
adds fb-reserved-memory. Its libfdt name lookup also matches unit-address suffixes;
add returns-2/EXISTS, callback returns1, caller3dfe4 branches to failure return,
and wrapper3ec20 loops before kernel handoff. This is a deterministic violated
contract on that selected path, not proof it was the sole physical reset cause.
Exact pinned LK callback AND libfdt instruction emulation reproduce failure on
the tested DT. Renaming the preserved node to fw-reserved-memory@98600000 passes
(return0); reg/no-map/compatible survive the callback unchanged. Removal is only
a negative/control fixture, never the candidate fix. Runtime globals are modeled,
not measured firmware state; receipt direct-loader-fb-collision-audit.json.
Implemented a one-byte input node-name change in direct packaging. No reservation,
RAM exclusion, phandle, panel setting, kernel, policy or capture is removed/changed.
Builder verifies every other board property. Fresh unchanged enforcing PID1 built;
1031 regression tests pass and all three exact-code callback controls pass.
Fresh corrected package and exact-LK static loader audit passed; offline device
guard accepts exact inputs under a disposable test authorization fixture, rejects
unapproved templates and consumed scope1. Scope display-direct-fbfix-2 is ready
locally for fresh owner attendance/approval, not staged to the lab. No new tablet
action or test approval. Original Android remains verified restored.
Receipt direct-fbfix-preparation.json; private checkpoint out/display-direct-fbfix-2.
Consumed first direct test and unknown owner visual result stay historical.

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
