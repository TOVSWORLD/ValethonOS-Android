# FireTabs project memory

## Integrated Android kernel compiled; complete Android image next — November 19, 2026

The ACK6.18 kernel with BinderFS, built-in FUSE/ADB FunctionFS and APEX
loop/device-mapper/dm-verity/EROFS/FS-verity support compiled and linked.
Downloaded artifacts passed independent hashes, parent/config-delta checks,
ARM64 header/footprint checks and exact gzip round-trip. Raw Image: 27,083,264
bytes; gzip: 9,556,029 bytes; runtime footprint: 28,573,696 bytes. Raw output
fits the existing 28-MiB LK decode capacity with 2,276,864 bytes spare.
Image SHA256: c83baf995268af14e0a4ba3faac683ee2ee4d6d1c4717a675d7eaccea20337b6.
Evidence: evidence/android-integration-source/android-kernel-build-result.json.
This is a completed kernel source build, not a full Android image or tablet boot.

The first integrated compile exposed an ACK FUSE cleanup conditional error on
ARM64 without FUSE_BPF. Exact-source repair preserves allocation lifetime and the
newer d_time initialization, guards BPF-only fields separately and keeps BPF off.
The failed attempt/source hashes and successful repair are retained in
android-fuse-build-repair.json. C cleanup tests cover 32/64-bit with BPF on/off
and null cleanup; exact patched-source resume passed. Repository suite: 1,074
tests, nine skipped, no failures. Existing hardware configuration is preserved;
no new tablet operation or repeated cube/logging proof occurred.

Real ARM32 Bionic EGL/GLES/Panfrost is compiled/packaged with strict ELF checks.
Douglas product/init/fstab plus verified graphics package staged in a control
tree; full AOSP checkout/product graph/system+ramdisk build remains pending.
The candidate uses bounded p14 system with co-located vendor/product/system_ext,
volatile /data, GLES2, enforcing SELinux and authenticated ADB; original userdata
and recovery are excluded. HAL/VINTF/policy closure, image fit, memory and actual
Android setup/home remain unqualified. Next is the full Android build discussion
and product graph/image work, then one prepared grouped T1 with backup/rollback.
Build operations/resources/caches remain private; reuse this completed kernel.

## Private build infrastructure — November 19, 2026

Owner directed runner provisioning, costs, caches and build operations to a separate
private GitLab project. Keep those operational issues and infrastructure details
out of this public repository. Continue Android T0 source/device integration here;
full Android build has not started. No repeat standalone GPU/logging test.

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

Updated November 18, 2026. This is the compact resume record, versioned with the
project. It does not claim to modify an account-wide ChatGPT memory service.
New user instructions and newer verified results supersede this snapshot.

## Objective and current reality

The objective is maintained Linux/Android on the 2017 Fire HD 8, douglas/KFDOWI,
ultimately a supported ValethonOS control panel. Interim Android is a working
recovery/development environment, not completion. The full ACK 6.18.34 draft
completes initialization and executes its controlled enforcing PID1 on Douglas.
**The prepared PID1's exact fresh VLOG0002+32-byte nonce was received over USB.**
This is the agreed kernel/PID1/USB-identity milestone, not a VM/stub-only pass.
Pinned PID1 emits that header only after enforcing-policy readbacks/RO remount,
labels/domain/namespace, UDC, duplex serial and kmsg-open gates. Kernel/RAM setup
and userspace execution must not be reopened as pending because record transfer
is incomplete.

Latest runtime: [USB identity milestone](../../evidence/independent-recovery/ack-usb-end-to-end-runtime-result.json).
Original Android boot/config/recovery and normal ADB verified after return.
Owner confirmed Power untouched throughout the latest attempt; automatic Android
return is established, as for the prior corrected-RAM and C-init attempts. Exact reset cause remains unqualified. One source
boot/restore and one load/jump consumed per attempt, no automatic retries.

**Read-only internal eMMC is now achieved:** the maintained kernel read the
original16MiB p5 boot partition, matched its SHA-256 and sent fresh VSTORE01
status over USB. Original Android then returned with installation checks and
normal ADB passing. [Storage runtime receipt](../../evidence/independent-recovery/ack-storage-readonly-runtime-result.json).
**Next product work:** #18 clock/reset dependencies, then #19/#20 pin/power
for display/touch/graphics and maintained Android userspace under #333/#24. Complete log-record transfer is a
non-blocking follow-up, not another proof gate.
The capture has40 bytes, zero complete records and no terminal frame. This does
not erase the fresh PID1 USB identity. The old target_pid1_proven metric bundles
release/cmdline log payloads and stays false for that stricter stream criterion.
Use the separate pid1_usb_identity_proven hardware milestone, with its recorded
physical-writer/gated-source proof basis.

Owner correction: do not get stuck on logging to prove working components.
No logging-only tablet gate or repeated kernel/PID1/USB-enumeration proof. Next
is an integrated read-only storage/status result using the existing USB path,
with a fresh package/owner presence if a hardware attempt is needed. Storage
scope6 and all prior authorizations are consumed; never replay them.


## Display functional package progress — November18,2026

Hosted full display build44253355044 passed on source90655a3. Direct GitHub
artifact ZIP digest and all manifest artifacts verified. Linked Image includes
master/gamma/mutex, TPV panel, host lane APIs, LP8557 and framebuffer console.
Receipt: evidence/display-pipeline-source/kernel-build-result.json. Earlier
packaging-only failure remains historical, not current build status.
Display-only enforcing PID1 compiled using unchanged proven policy; VDISP001
reports framebuffer metadata/banner write, never physical pixel proof. Generic
enforcing ABI/labels/configfs VM passed on the exact new unmodified Image.
Fresh final RAM bundle3 passes seven integrity/deadline/both-VM controls.
Actual display C metadata/short-write tests and controller visual-pending test
pass. Fresh unapproved display scope7 template prepared; final offline controller
validation/publishing underway before the attended visual test.
Current private inputs: out/display-kernel-1, out/display-initramfs-1,
out/display-functional-bundle-3 (current; earlier1/2 superseded). Build lab
/tmp/firetabs-display-functional-build-20261118-1/out/init-2. No tablet action,
no fresh authorization, no display hardware pass. Issues18/329 updated directly.
Next is visible VALETHON DISPLAY TEST plus labelled RGB bands and protected
Android return; no repeated storage or complete-log prerequisite.

## Active display/backlight implementation — November18,2026

Owner accepted exactly three intermediate outcomes before the major Android UI:
(1) display/backlight including needed providers, (2) touch/input, (3) Android
graphics/userspace integration. Provider substeps are internal to those outcomes,
not additional owner-facing milestones. Keep the major setup/home commitment.

MT8163 DRM master/gamma/mutex source port and TPV-only DRM panel are implemented.
Existing saved working boot DT identifies TPV/MP; no new device query needed.
Working board pinctrl proves GPIO43 power/GPIO83 reset, correcting stale110/65
comments. Working LP8557 is REGISTER_BASED at I2C0x2c, device control0x47; generic
PWM-backlight is not sufficient. The board's epprom_data property is ignored by
its eeprom_data-reading driver; do not activate the dormant ROM table writes.
The172 TPV packets/two delays match compiled original C byte-for-byte. Actual C
failure matrix covers every packet/short write, regulator errors and state cleanup.
All999 tests and Android source-evidence checks pass. No display hardware trial.

Draft PR454, branch codex/issue-18-display-foundation, is stacked on the
unchanged proven storage/native branch. First compile run44250389319 on source1b0d1b5 compiled the actual display
objects and linked Image, then failed final packaging because the size-report
writer requires a fresh filename. Fix uses display-image-size-report.json,
preserving the dependency report. Failed receipt is versioned; no artifact or
runtime pass inferred. Follow-up implements explicit MT8163 lane prepare/unprepare:
rails settle before lane exit from ULPM and reset; lane shutdown precedes power
off, with retained rail ownership on cleanup failure. These follow-up sources
need an updated full build before admission. DT preview now closes the
display/SMI/IOMMU/I2C0/panel/backlight graph, preserves RAM/no-map/reserve-map
data, uses verified I2C0 pins75/76 and panel43/83, and strips the old RAM-console
hook arguments. Explicit offline-preview marker/no executable metadata prevents
misuse as a physical candidate. New Image package/VM and attended screen test
still remain; source/DT checks are internal steps of the display outcome. Never treat the older build as
qualification of a newer head.

Full hosted kernel build uses the draft PR: existing GitHub connector has
no workflow-dispatch action and local gh is not authenticated; do not ask owner
to redo connector setup. PR-open triggers the explicit display-provider scope.
Source/issue publishing stays on the connector. Keep source-only DT-disabled
build separate from later functional RAM-test admission. Never relabel this as
achieved display or add a logging-only proof gate. See display-port/README.md.

## Read-only eMMC hardware milestone — November18,2026

[Actual receipt](../../evidence/independent-recovery/ack-storage-readonly-runtime-result.json).
One source boot/restore and one native load/jump completed. Enforcing storage
PID1 read exactly16777216 bytes from the immutable block179:5 p5 node using
O_RDONLY, checked EOF and matched the original boot SHA-256. Fresh120-byte
VSTORE01 result independently decoded; selected physical USB endpoint, stage5,
flags31, error0. No block write/ioctl or userdata mount. Original p5 was restored
and read back before jump; recovery untouched. A different completed Android
boot returned with original boot/config/recovery and normal ADB checks passing.
Storage acceptance is achieved; do not re-prove it through kernel-log transfer.
Owner confirmed Power untouched throughout; automatic original Android return
is observed. Exact reset cause remains unqualified.

Source code at d6f3c5ae67dc66d41665b0170005efc61608eae2. Private trial:
out/recovery-linux-pivot/ack-storage-readonly-trial-runtime-1. Parent/child
scope6 authorizations are consumed. No replay/retry or owner recovery needed.
The prior preparation's985 tests,14 controls,11 compiler negatives and four VM
checks passed; repository integrity still flags the unchanged empty helper at
tests/test_source_usb_shutdown.py:201. No new source change required for runtime.
Next is the documented #18/#19/#20 display/touch provider path toward #333/#24
usable maintained Android; broad hardware, writable filesystems and Android UI
remain unqualified. Reuse the working kernel/RAM/storage/PID1/USB foundation.

## Historical storage preparation — before the successful hardware test — November18,2026

[Preparation receipt](../../evidence/independent-recovery/ack-storage-readonly-preparation.json).
Dedicated enforcing storage PID1/policy and fresh VSTORE01 functional status are
built. Only internal MMC0 is enabled, at26MHz with exact existing pins/supplies,
clock parents and MediaTek sysirq. The working4.9 mt8163 and mt2701 quirks match
the maintained fallback. No speculative host-driver rewrite or new logging gate.
The fixed archive block179:5 node is0400; PID1 uses O_RDONLY, exact16MiB/EOF and
known original boot SHA verification. Policy denies block writes/ioctls/new nodes
and reads of other block types. No userdata mount or block payload over USB.
The120-byte one-way status carries fresh identity, stages/errors and a verified
expected digest; it needs no VLOG ACK or kernel-record transfer.

All11 compiler negatives pass. Both synthetic read-only storage VM modes pass:
full read/hash, bad-hash rejection, write/ioctl/other-block/mknod denial, unchanged
fixture. The exact fresh Image reaches enforcing PID1 in both target RAM-layout
VM modes, including the live2MiB exclusion. All14 entry/console/corruption/VM
controls and985 unit tests pass, no skips. Android source-evidence check passes.
Repository integrity still stops on unchanged tests/test_source_usb_shutdown.py:201
empty test helper; it is not claimed passing. No tablet command or trial ran.

The source/three ABI transfers were approved and completed. Lab compilation and
VM qualification are finished. At preparation time scope6 was unapproved/unconsumed; now consumed, as above;
prior approvals remain consumed. Next requires owner presence for one protected
source boot/restore and one RAM jump; original p5 restored/read back before jump,
recovery untouched,31-second target deadline and bounded read-only Android-return
checks. No automatic retry. Hardware storage is not yet achieved.

Private resume inputs: out/recovery-linux-pivot/ack-storage-readonly-candidate-1,
storage-built-1/out/init, ack-storage-readonly-qualification-1.json,
ack-storage-readonly-client-1, storage-qualification-artifacts-1. Isolated build
lab: /tmp/firetabs-storage-readonly-build-20261117-1. Public trial template:
evidence/independent-recovery/ack-storage-readonly-authorization-template.json.
Use --ramfix --storage-readonly in run_ack_native_trial.py, never --usb-end-to-end.
The storage mode requires its own exact scope, component verification and
functional status plus original Android return; the old log-specific metric
remains separate. Reuse no consumed scope5 wrapper. Do not run read-only device
preflight while merely checking the offline parent validate() function.

## Receiver result and offline cleanup fix

The detached worker delivered the identity, but its outcome was masked by
termios.error during post-disconnect restoration (not caught by except OSError).
The old supervisor then reported endpoint_selected false and rejected the wire
assessment. Raw40-byte evidence was independently parsed against the fresh nonce
and host digest. Preserve the original failed controller report; the sanitized
runtime receipt distinguishes identity proof from incomplete records.

Cleanup now catches termios.error, preserves the original capture outcome and
accepts a completed transfer's expected vanished-TTY restoration. Offline tests
cover incomplete/complete capture plus cleanup error, fresh header without log
records, detached-parent loss and stdout-loss recovery. No new device test ran
for this cleanup fix. Primary reason the record stream ended after identity is
still unknown; do not invent a kernel/PHY regression or claim terminal success.

[Next plan](NEXT-MILESTONE-PLAN.md), [end-to-end history](ACK-USB-END-TO-END.md).
Private latest trial: out/recovery-linux-pivot/ack-usb-end-to-end-trial-runtime-1.
Its scope5 approval and children are consumed; do not rerun the wrapper.

## C-init hardware result and live RAM correction

[Receipt](../../evidence/independent-recovery/ack-cinit-runtime-result.json),
[correction plan](ACK-LIVE-RAM-FIX.md). The single C-init attempt returned to
verified original Android; Power attestation remains in the receipt. Fresh
retained console reports stack overflow, PC show_pte+0x1d0, ESR96000006,
FARffff0000585ff008. Nested fault reporting may hide the first exception.
No PID1/USB proof. A no-map gap98400000–98600000 was missing: source live
System RAM excludes it, but target DT allowed allocations there. Under the A53
linear map the fault address implies physical985ff008 in that gap; inference,
not a directly observed physical address. Gap ownership and causality unproven.

The corrected allocator contract uses fresh iomem, not only static/live DT.
Preserve every non-System-RAM gap as no-map, keep all existing reservations,
and independently bind/recompute the source ranges. Both target-memory-geometry
VM modes now reach enforcing PID1 with the fresh corrected Image. All13 controls,
963 regression tests and bound offline policy validation pass. No additional
tablet commands ran while preparing the fix. Scope4 requires new owner presence.
Private reference ack-ramfix-candidate-1; PID1 ack-ramfix-initramfs-1; prepared
runner run-ack-ramfix-trial-1-private.py under out/recovery-linux-pivot.

## Historical preparation — C-init/PID1 candidate (now executed)

[Exact trial](ACK-CINIT-TRIAL.md), scope ack-linux-cinit-two-stage-3. Full Image
93722d1fd0d6d7f53b351fba8508bce7d1923fb21a9e92a5911a2acfc4742476.
Both VM modes reach /init with enforcing PID1 probe and retained run-init output
after init-memory cleanup. All12 offline controls and958 regression tests pass.
Permanent executable padding hosts a RAM-only early console callback; one
8250 early setup detour installs it without UART register operations. Existing
fixmap covers one reserved4KiB console page; ring4084 bytes, full fresh PID1
identity each write, bounded lengths/header checks and preserved registers/DAIF.
Target ramoops params are removed to avoid a conflicting writer. keep_bootcon,
initcall_debug/loglevel8/ignore_loglevel capture complete-kernel progress. The
previous five entry hooks/Normal-NC identity map are absent. Existing full padded
Image SHA and31-second reset deadline stay. No storage or recovery enablement.

The missing old banner did NOT bound a fault to pre-banner C code: normal printk
was not retained that early. SHADOW_CALL_STACK is disabled in the pinned config;
do not present shadow-stack failure as a diagnosis. A specific stopping C
instruction/driver remains unknown. This candidate runs the complete kernel and
fresh enforcing PID1, not an isolated logger/payload. Hardware PID1/USB is unproven.

Private reference: out/recovery-linux-pivot/ack-cinit-candidate-2; fresh userspace:
ack-cinit-initramfs-1; prepared runner: run-ack-cinit-trial-1-private.py in that
same parent. No new tablet commands ran during this preparation. Obtain owner
presence and fresh cinit authorization for one source boot/restore and one jump;
never reuse the completed combined trial's consumed approval.

## November 17 hardware milestone

Receipt: evidence/independent-recovery/ack-combined-runtime-result.json.
One protected source boot/restore, one load, one jump. Original boot restored and
read back before jump; recovery never written. Fresh marker chain was absent
before load and recovered once, unique and ordered: image_verified, linux_entry,
before_mmu, after_mmu, virtual_entry, start_kernel. No map_refused/corrupt marker.
The retained trace ends at start_kernel. This does not identify the next failing
instruction or prove full initialization. Target USB endpoint/PID1 did not appear.
The legacy controller outcome ack-boot-unproven refers to its stricter banner/
PID1 acceptance; it must not erase the independently proven Linux C milestone.
Do not repeat relocation, entry, MMU or metadata-only tests as unresolved work.
Private runtime: out/recovery-linux-pivot/ack-combined-trial-runtime-1.
Trial authorization and its source/jump children are consumed.

## November 17 combined candidate

[Concrete trial](ACK-COMBINED-TRIAL.md): complete padded-Image SHA at destination,
five markers inside actual Linux entry/MMU/start_kernel, existing enforcing PID1.
Exact instrumented Image a548bff1b6d8b67ffe1b45ed112c16c64db35fdcfc7ff592357c959758677f2e
passed both Cortex-A53 QEMU virtualization modes with all five stages in order
and enforcing PID1 probe. All11 offline qualification controls and953 regression
tests pass, with no skipped tests; Android evidence check passes. Repository
integrity still flags the unchanged empty test helper at
tests/test_source_usb_shutdown.py:201. This is VM evidence, not tablet Linux/USB acceptance.
Source-derived DT corrections enable legacy PSCI status and normalize overlapping
RAM declarations without changing their union; neither is a proven diagnosis.
New scope ack-linux-combined-two-stage-2 binds the prequalified unspent reference
Image/token, fresh PID1 and single-attempt controller. Old approvals stay consumed.
Private candidate: out/recovery-linux-pivot/ack-combined-candidate-2; PID1:
ack-combined-initramfs-1 in that same parent. Do not print nonce/raw metadata.

## Hardware knowledge base

The owner requires a complete kernel-facing hardware reference on GitHub,
derived from board documentation and older working kernels. Use
[DOUGLAS-HARDWARE-CONTRACT.md](DOUGLAS-HARDWARE-CONTRACT.md), covering20
subsystem areas, plus the allowlisted resource inventory for430 working-source
and152 ACK DT nodes. This is the starting point for implementation; do not reduce
the project back to UART alone or repeat component discovery already recorded.
Unknowns remain explicit rather than invented. Historical source matrices are
not live build/runtime status.

## Owner decisions that must survive a restart

- Use the direct GitHub connector for GitHub. Do not fall back to the browser or
  gh CLI when the connector supports the operation.
- Preserve historical attempts and failures in the existing open issues. Current
  issue/project status must describe actual work, not an abandoned plan.
- The owner wants progress toward actual Linux boot, not endless logging gates,
  repeated approvals or another tiny experiment without a decisive question.
- The owner has **no multimeter, oscilloscope, logic analyzer or UART adapter**
  (November 16 answer). Do not ask this equipment question again.
- No existing internal-board photos or PCB revision records were available
  (October 27 answer). Do not ask that historical question again.
- The owner correctly recalled that annotated Douglas board documentation was
  already found. Reuse the reference below; do not present it as new research.
- November 17 correction: do not assume missing facts require measurement or a
  technician. First trace the older working kernels, board documentation and
  electrical specifications. A failed search or inaccessible page does not prove
  that documentation does not exist. No hardware-versus-software route choice was
  made in response to the last multiple-choice question.
- Hardware planning has been acceptable, but no equipment purchase, booking,
  physical wiring or opening has been performed in the UART preparation.

## Completed experiments: do not propose them as new

1. Normal bootloader diagnostic/modern-kernel trials, early screen and delay
   markers, and retained-record experiments were already attempted. They did not
   establish maintained-kernel entry. See `entry-screen-trial-result.json`,
   `entry-delay-trial-result.json`, `first-draft-trial-result.json` and
   `known-boot-capture-control-trial-result.json` under `evidence/independent-recovery/`.
2. The diagnostic source kernel's USB console works. Native entry was observed;
   secondaries were shut down before devices with a final off-state gate.
3. A one-page target reset payload executed, left its fresh retained marker and
   returned automatically. Owner confirmed Power was untouched. This proves
   target payload execution, not full Linux startup or recovery from every hang.
4. One full ACK 6.18 RAM attempt then ran: one protected source boot/restore,
   one load, one jump. Original boot was restored before the jump; recovery was
   untouched. The metadata entry marker survived. No attributable Linux/PID1
   records or target USB endpoint appeared. Android returned without Power
   intervention and original state was verified. Exact reset cause is unproven.
   Receipt: `evidence/independent-recovery/ack-native-runtime-result.json`.
5. Offline exact-artifact audit copied all three segments correctly across 14
   indirection pages, including the 28,049,408-byte Image memory extent. The exact
   Image reached MMU-enable entry in Cortex-A53 emulation; corrupt-source and bad
   branch controls were detected. No concrete production defect was found. Actual
   hardware destination integrity, warm firmware state and MMU/later execution
   remain unqualified. Receipt: `ack-full-image-offline-audit.json` in that directory.

The consumed trial authorizations stay consumed. Do not repeat a load/jump or
replay the original BootROM/unlock/install procedure as a routine resume action.

## Board/UART references and facts

The already-found [maintainer annotated board fallback](https://xdaforums.com/posts/90488396/)
is recorded in `CURRENT-STOCK-ENTRY-RETURN.md` and
`evidence/douglas-original-route/report.json`. The saved review calls it a
hardware recovery/BootROM reference; it does not establish a UART TX/voltage map.
Its earlier image must not be relabeled a UART pinout without inspection/evidence.

The legacy 3.18 tree at `e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74` and the exact
working 4.9 tree at `72940eb733af8df948cc216cb977cd8be9cba5a9` are primary sources.
Both inspected DT definitions name UART0 at 0x11002000, 26 MHz input,
RX GPIO79 and TX GPIO80 with function1. The default GPIO state is empty; the
vendor driver has separate RX/TX set/clear states and can switch pins during
power transitions. Preserve this distinction from the modern driver's behavior. Match live DT
compatible and compiled config before attributing source behavior to the running
kernel; a vendor UART file existing in the tree is not a runtime driver pass.
The November 17 trace did resolve the implementation: the working source config
has MTK_SERIAL and MTK_SERIAL_CONSOLE=y; vendor console/baud/probe functions
are present in the linked source kernel; the archived live UART0 DT is enabled
and includes `mediatek,mtk-uart`. Physical UART output is still untested. Do not
repeat these implementation-selection checks as if they remain unresolved.
Legacy console configuration requests 921600; the vendor console setup defaults
to 115200 unless options override it. Pin input-enable/Schmitt grouping for79–82
is not proof of that group's supply voltage or an accessible PCB contact.

The previously tested ACK DT disabled UART0 and had no UART console arguments;
its needed driver is built in. A verified offline preview enables UART0/stdout/
earlycon/console only. The ACK earlycon callback sets MMIO width/stride but does
not program baud; inherited initialization matters. The archived source boot also
contains `printk.disable_uart=1`. Silence cannot establish a wiring or kernel fault.

The source contains USB-to-UART PHY-switch code, but the tested source config
has it disabled. UART alternate pins87/88 are MSDC2, whereas the board's removable
card pinctrl uses MSDC1 pins121–126. Neither is an established solderless UART route.

No exact-board TX pad or electrical level has yet been verified in this project.
This means **unresolved**, not necessarily undocumented or measurement-required.
Do not infer UART voltage from a VIO18 regulator used by another peripheral.

## Prepared artifacts and remaining task

- `scripts/capture_uart_receive_only.py`: bounded private POSIX recorder; five
  PTY controls pass. No adapter or physical UART pass. Output wires must remain
  physically disconnected in any future receive-only setup.
- `scripts/prepare_ack_uart_preview.py`: exact-hash offline DT preview;
  `loadable:false`, not a new admitted boot bundle.
- [UART preparation](UART-FIRST-CAPTURE.md): conditional procedure and source gaps.
  Its November 16 bench selection is superseded by the documentation-first plan.
- Current issues remain #344 (phase), #346 (current implementation/recovery) and
  #348 (capture evidence). Preserve history; do not create more micro-issues.

The next action is the combined software test after bound offline validation and
owner availability. Physical UART remains an optional supporting investigation;
do not make board contact/voltage resolution a gate for this candidate.
