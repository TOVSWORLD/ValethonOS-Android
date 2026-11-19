# Current milestone — interactive GPU achieved; next maintained Android setup/home, November19,2026

## Bionic graphics compiled; Douglas Android product staged — November 19, 2026

The pinned Mesa 26.2.7/libdrm 2.4.133 sources now compile as ARM32 Bionic with
NDK r30/API34. Four real EGL/GLES/Panfrost runtime libraries passed ARM ELF,
Android ABI-note, dependency and SONAME checks; generated Soong modules retain
strict ELF checking. Source scripts, package examples and build-result hashes are
in scripts/, projects/firetabs-android/android-integration/ and
evidence/android-integration-source/bionic-graphics-build-result.json.
This is a graphics library build, not a full Android image or tablet Android boot.

Douglas product/BoardConfig/init/fstab inputs and verified graphics package staged
successfully in an isolated control tree. Full AOSP build graph is not yet run.
The candidate builds bounded p14 system plus ramdisk, with vendor/product/system_ext
co-located and a volatile 256-MiB /data; original userdata/recovery are excluded.
Pinned RenderEngine has GLES2 fallback; select skiaglthreaded/Ganesh GL and advertise
GLES2 only. Keep enforcing SELinux and authenticated ADB. VINTF/HAL closure, memory,
image fit and integrated Android execution remain unqualified.

The source-only kernel build is active. Isolated Kconfig preflight resolved all
requested Android/APEX features; pinned NFS Kconfig explains its existing pNFS
helper promotion when device-mapper becomes built-in. This is not final compile
or hardware execution. Integration includes BinderFS, built-in
FUSE/FunctionFS and source-derived loop/dm-verity/EROFS APEX requirements. Preserve
the working hardware configuration and check the resolved bounded delta. No new
tablet test or writes have occurred. Next: finish kernel compile, validate the full
Android product graph and build system/ramdisk; then one prepared T1 session with
concrete backup/rollback approval. Do not repeat cube/logging proof. Build operations
and resource blockers remain tracked privately, outside this public repository.

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

[Actual receipt](../../evidence/independent-recovery/ack-storage-readonly-runtime-result.json):
maintained6.18/enforcing PID1 read original boot p5 exactly16MiB, checked EOF and
matched its known SHA-256. Fresh120-byte VSTORE01 success received on the selected
physical USB endpoint, independently decoded: stage5/flags31/error0. Original
boot restored/read back before jump; recovery untouched. Different completed
Android boot, original installation checks and normal ADB verified afterward.
Owner confirmed Power untouched; automatic return observed, exact reset cause
unqualified. Scope6 consumed.
One source boot/restore, one load/jump, no retry, no owner recovery needed.

[Next plan](NEXT-MILESTONE-PLAN.md): #18 clock/reset dependencies, #19/#20 pins/
power, then display/touch/graphics and maintained Android under #333/#24. Preserve
the achieved kernel/RAM/PID1/USB/storage foundation. Complete custom kernel-log
streaming remains non-blocking; no logging-only re-proof or repeated storage
milestone. Read-only known-p5 integrity does not qualify general/writable
filesystems or Android UI. Earlier preparation:985 tests,14 qualification controls,
11 compiler negatives and four VM checks passed. Source at d6f3c5a; raw trial
private under out/recovery-linux-pivot/ack-storage-readonly-trial-runtime-1.

## Active first intermediate outcome — display/backlight

Owner agreed to three outcomes before maintained Android setup/home: display/
backlight, touch/input, Android graphics/userspace. Clock/pin/power substeps are
internal dependencies, not extra owner-facing milestones. Actual DRM pipeline,
gamma/mutex and TPV panel sources implemented;999 local tests pass. Hosted full
kernel compile, DT closure and fresh RAM package remain; no display hardware
claim or new device action. Keep proven storage/PID1/USB and consumed scope6.


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

# Historical selection — UART bench preparation, November 16, 2026

Owner requested a route out of blind boot trials. Receive-only UART capture and
an exact-hash ACK UART DT preview are prepared; five host controls pass. No
new tablet commands or trial ran. The tested ACK DT had UART0 disabled and no
UART console arguments; built-in driver support exists. Source console suppression
and earlycon's dependence on inherited hardware initialization are explicit.

Actual board TX pad, voltage and a readable baseline are still unknown. Next is
one competent bench session to identify/measure TX and capture the known-working
boot, using receiver RX/ground only after electrical compatibility is established.
Owner has no test instruments or UART adapter. The earlier annotated Douglas
board recovery reference has been recovered and linked; it does not establish
UART pads or voltage. Reuse it for bench layout identification. No purchase, booking, opening or probe connection
has been performed. Do not label physical UART or Linux boot as qualified.

[Prepared bench procedure and capture commands](UART-FIRST-CAPTURE.md).
[Preparation receipt](../../evidence/independent-recovery/uart-test-preparation.json).

# Completed attempt — full 6.18 kernel/PID1 RAM boot, November 16, 2026

Owner requested Linux boot after the reset-payload milestone. The complete
pinned 6.18.34 draft is prepared for the proven native RAM path at its required
zero-offset aligned address. The target now uses the live legacy PSCI contract
rather than the draft assumption of PSCI 0.2. Fresh enforcing PID1, all live
firmware reservations and USB0 are retained. Storage/display bootstrap probes
and the disk-log opt-in are disabled. The maintained Image is not flashed.

A 31-second reset-only hardware deadline is armed at entry, with its target
driver disabled. Its physical behavior remains unqualified; owner-assisted
return may still be needed. The source boot image is restored before jumping.

One protected source boot/restore and one native load/jump have now run. The
original boot was verified before jumping. The metadata entry/readback marker
was recovered; no attributable 6.18 kernel records or PID1 USB endpoint appeared.
Android returned on a different completed boot, with exact original boot/config,
unchanged recovery and normal ADB verified. Owner confirmed Power was untouched, establishing automatic return;
precise watchdog reset cause remains unqualified. No retry; authorization consumed.

The current result is **ACK boot unproven**, not a Linux milestone. Investigate
the full Image entry and early architecture startup boundary before proposing
another device test. The entry marker cannot verify the full relocated Image,
its first kernel instructions, MMU enable or later driver initialization. Do not
spend another trial on USB/logging settings without evidence of that failure.

Post-trial offline audit completed without tablet commands: the actual linked
relocator copied every destination byte across all three full-size segments and
14 list pages; the exact kernel reached MMU-enable entry in Cortex-A53 emulation.
Corrupt-source and broken-entry controls were detected. No concrete defect or
tablet Linux boot was established. Actual hardware destination integrity and
Linux entry/MMU progression remain the gap. The next native experiment must
combine those checks in one package; that package is not yet prepared. No more standalone USB-settings or stub-only trial is selected.

[Offline audit](../../evidence/independent-recovery/ack-full-image-offline-audit.json).

[Runtime receipt](../../evidence/independent-recovery/ack-native-runtime-result.json).

[Concrete Linux test](ACK-LINUX-RAM-BOOT.md).

# Passed milestone — target payload executed and reset automatically, November 16, 2026

One reset-payload jump recovered exactly one target-only retained marker that
was absent before loading. This proves execution of the one-page target. A
different boot returned to original Android with full boot/config, recovery and
normal ADB verified. Owner explicitly confirmed no intervention: the deliberate
payload reset and automatic return are qualified. No retry; trial budget consumed.

Linux target boot and full-size Image relocation remain unproven. Do not infer
that a small-payload pass proves every stage of the prior Linux handoff. The
failure-triggered bolder fallback is not activated because this experiment passed.
Automatic recovery from arbitrary Linux hangs remains unqualified.

[Exact target-execution receipt](../../evidence/independent-recovery/reset-payload-runtime-result.json).

# Historical current plan — one attributable reset target, then boot-strategy decision, November 16, 2026

Owner authorized this final narrow handoff probe and requested a bolder plan if
it fails. A one-page reset target, separate from the proven source kernel,
appends a target-only nonce to the existing retained console and requests the
normal hardware reset. Exact marker recovery, a fresh verified original boot
and owner confirmation of no Power intervention are required. A reboot alone
is insufficient. Linux target boot remains unproven.

The package, offline native layout/load client, instruction controls and
read-only tablet preflight pass. No reset-payload jump has run. Owner presence
for the actual test is pending. After one failed/inconclusive jump, pivot to a
bootloader-loaded minimal Linux environment and remove kexec from the critical
path; do not automatically try another small handoff variation.

[Test and terminal rule](MINIMAL-RESET-PAYLOAD-TEST.md).
[Bolder fallback](BOOT-STRATEGY-PIVOT.md).

# Verified return — November 16, 2026

Android boot complete, original full boot/config, unchanged recovery and normal
unprivileged ADB verified after owner-assisted return. The early CPU-off gate
passed in the November 13 experiment; target boot remains unproven. No new
source boot, load or jump has run. All previous trial budgets remain consumed.
Continuing read-only investigation of the remaining handoff interval.

# Historical current result — early CPU-off gate passed; target still absent, November 13, 2026

The handoff-order experiment ran once. Source boot and original-boot restoration
passed, followed by one load and one jump. Captured hardware evidence proves
secondary CPUs were off before device shutdown. Target USB timed out, so target
boot remains unproven and this ordering change was insufficient. Later source
phases are hidden by USB teardown; do not infer their success or failure.
Owner-assisted return and separate post-return verification are pending. No
automatic retry; this trial budget is consumed.

[Exact hardware result](../../evidence/independent-recovery/early-cpu-shutdown-runtime-result.json).

# Historical current experiment — CPU shutdown before device shutdown, November 13, 2026

Original Android, full boot/config, recovery and normal ADB were verified after
owner-assisted return. The next candidate changes source handoff ordering,
parking secondaries while platform drivers are still running. Existing final
CPU gates and relocation remain in place; target startup returns to its normal
CPU configuration. This is a hypothesis under test, not a proven fix. Seven
actual-C controls and five distinct-scope controls pass. The isolated ARM64
Image, linked gates and read-only preflight passed; only kernel/kexec_core.c
differs from the boot-tested source. Owner availability for the prepared test
is pending. Hardware execution remains unqualified and target USB entry is
still required.

[Scope and validation](EARLY-CPU-SHUTDOWN-TEST.md).

# Historical current work — CPU0-only trial failed; resolve handoff boundary, November 12, 2026

The hardware trial below has now run once. Source prerequisites passed, but
the target supplied no USB endpoint or nonce within 300 seconds. **Target boot
is still unproven.** Original boot was restored before the jump; recovery was
not written. Owner-assisted return completed November 13. Post-return checks verified Android boot complete, original boot/config, unchanged recovery and normal unprivileged ADB.
No automatic retry. The next investigation covers device shutdown, CPU-off,
restart/relocation and early target execution; this result does not locate the
failure. Do not repeat the same CPU0 trial or re-count source native entry.

[Actual CPU0-only result](../../evidence/independent-recovery/single-cpu-target-runtime-result.json).

## Executed hypothesis and scope

Owner requested continued work toward a real boot milestone. Source native entry
is a prerequisite; it is not being counted again as target progress. The next
test changes only target boot arguments (`nr_cpus=1 maxcpus=1`) to bypass normal
secondary CPU restart before USB initialization. Exact source review found the
firmware/power-on startup path and unbounded secondary power waits. This is a
testable hypothesis, not a claimed cause of the failed handoff.

The already boot-tested kernel, source package, source CPU shutdown and relocation
remain unchanged. The new mode has a distinct guarded scope, rejects existing CPU
boot controls and requires the proven source capture profile. Actual target data
is regenerated after source boot; the offline preview cannot be loaded. Proceed
with one protected source boot/restore and one captured jump. Only a fresh target
kernel nonce qualifies as the next milestone. Prior trial approvals stay consumed.

[Concrete target-boot test and physical return](SINGLE-CPU-TARGET-TEST.md).

# Previous milestone — accepted native kexec entry, November 12, 2026

Host capture positively proves the kernel entered kernel_kexec with its mutex
acquired and a loaded image accepted. Fresh source USB proof, nonce-bound
FunctionFS last-close retention, namespace route and the native-entry marker
were all captured. The 8,600-byte source file was synced and independently
hash-verified. This passes the requested next milestone beyond init shutdown.

One source boot succeeded; original boot was restored/read back on flash and
recovery verified unchanged before the one actual load/jump. Initial source
capture gate failed with zero loads/jumps. Ordering/cleanup corrections passed
50 controls; the corrected gate passed on the same source boot, then one load
verified and one jump was requested. No source-boot or jump retry.

The target USB console did not appear in five minutes. Device shutdown, CPU-off,
relocation and target entry are still unqualified. Do not infer a specific failed
phase from missing messages after USB teardown. The next engineering interval
is **after accepted native entry**, rather than init routing or a live logging
baseline. Independent automatic return is still unqualified.

Owner returned the tablet physically. November 12 post-return verification
passed: Android boot complete, original boot/config, unchanged recovery and
normal unprivileged ADB restored. This is owner-assisted return. The trial
budget is consumed. No further load, jump or reboot is being requested.

[Actual result and limits](../../evidence/independent-recovery/ffs-native-entry-runtime-result.json).

# Historical milestone — native-entry test prepared, November 12, 2026

Resumed at owner request. New diagnostic kernel built and passed linked native
checks. Default-off nonce-guarded FunctionFS hold addresses the concrete ADB
last-close path that removes sibling ACM. Actual C controls reproduced/fixed the
console completion race. The controller quiets printk reversibly. A new marker
inside kernel_kexec, after mutex/image admission, gets a one-second drain
opportunity before device shutdown. The existing dispatcher and CPU/relocation
logic are unchanged. This tests native entry, beyond the captured init shutdown.

Source-package read-only preflight passed with zero writes/reboots and normal
ADB restored. New kernel/hold/jump has not run. Offline target preview is marked
non-loadable; actual target metadata must be regenerated after source boot.
Ready for one owner-attended approval covering source boot/restore and at most
one captured jump. Target entry and automatic return remain unqualified.

[Concrete milestone test and return procedure](FFS-NATIVE-ENTRY-NEXT-TEST.md).

# Historical paused checkpoint — verified return and offline capture audit, November 11, 2026

Paused at owner request for a gear switch. Android boot complete, original full
boot/config, unchanged recovery and normal unprivileged ADB were verified after
hard-boot return. No new hardware trial or background operation is running.
Latest capture proves init entered shutdown; target entry remains unproven.

Offline audit found a concrete FunctionFS path that can unregister the entire
ADB+ACM gadget when ADB closes, an 8 KB lossy console buffer, and a potential
completion-ordering race needing reproduction. None proves the hang location.
No new kernel patch, build or test is ready. Resume the audit before choosing a
small follow-up; prior trial approvals are consumed. Earlier pending-return and
readiness statements below are historical.

[Full resume checkpoint, evidence and remaining work](FIRETABS-RESUME-2026-11-11.md).

# Historical state — source shutdown captured; owner return pending, November 10, 2026

The source-plus-target trial ran. Source boot passed and original boot was
restored/read back on flash. A fresh kernel-only USB marker arrived before
loading. One native load verified and one jump was requested. Source capture
retained 20,957 bytes, including Android init receiving the exact kexec target
and entering shutdown. No kernel-handoff checkpoint or target USB console was
observed. The five-minute target wait ended; no retry was made. Collector final
receipt failed, but the raw source file was separately preserved and hash-verified.

The bootloader placed the source-console argument after its own parameters;
the initial builder refused before any load. Position handling was corrected
without changing remaining arguments, Image or layout; source boot was not
repeated. Separate disconnect/final-receipt robustness fixes pass controls and
have not triggered another hardware test. Thirty focused Python controls pass.

Owner physical return was requested; post-return boot/config/recovery verification
is pending. Keep target entry and independent return unqualified. Next: verify
return, then examine source-console buffering/verbosity and USB teardown around
the missing kernel-route messages before selecting another discriminating test.
Do not repeat this experiment unchanged or claim a failed phase from silence.

[Actual receipt and capture limits](../../evidence/independent-recovery/source-usb-handoff-runtime-result.json).

# Historical state — source shutdown capture prepared, November 10, 2026

The target-only USB trial finished: source boot passed, original flash restored,
one native load verified and one jump requested. Source USB disconnected; no
target console appeared in five minutes. Target entry remains unproven. Owner
held Power after a black screen and confirms Android home; original boot/config,
unchanged recovery and normal ADB verified. Prior approval is consumed.

Next candidate retains the same Image and CPU/relocation code, enabling ttyGS0
on the source. Before loading, a fresh kernel-only marker must arrive over
source USB ACM. Capture source shutdown and target enumeration in one bounded
trial. Offline controls and source-package read-only preflight passed; new
source-console boot/capture/jump has not run. This needs one new owner-attended
test approval. USB teardown limits later source-phase visibility; no hang phase
has been proven. Earlier pending-test statements below are historical.

[Exact next test](SOURCE-USB-HANDOFF-NEXT-TEST.md).

# Historical state — USB console test ready, November 10, 2026

Live kernel→USB serial→host capture is working. Console-enabled native kernel
built; syscall/CPU gates and builtin console verified in linked Image. Original
source ramdisk/DTs/args preserved; exact source-boot read-only preflight passed.
Ready for one owner-approved two-stage sequence: source boot with original-flash
restoration, then one fresh USB-captured console-target jump. No new boot/jump
has run. Retention/watchdog work is not the critical path.

[Exact two-stage test, limits and physical return](USB-CONSOLE-NEXT-TEST.md).

# Historical current priority — USB capture, November 10, 2026

Owner correction: prioritize USB logging/capture for faster boot/handoff diagnosis.
Live working-kernel kernel→ACM→host capture PASSED (390 bytes, exact kernel
marker, synced private capture). Initial host serial-open permission failure
fixed without group/ACL changes. Both tests restored ADB-only and normal adbd;
no reboot or boot/recovery write. Next: builtin USB kernel console for early
target boot; isolated build in progress. Watchdog/retention work is not the
critical path. Earlier reset-first scope below is superseded as a priority.

[Working capture path and evidence](../../projects/firetabs-android/usb-live-capture/README.md).

# Historical current state — manually recovered, November 10, 2026

Original Android, full boot/config and recovery verified after owner-assisted
recovery. Normal ADB restored. Pstore mounted/enabled but record directory empty;
handoff stage remains unknown. Next work is post-failure recovery timer and phase
logging/readout: exact watchdog driver can stop its timer during device_shutdown.
No new jump, boot write or automatic reboot; approvals consumed.

[Recovery evidence and next implementation scope](NATIVE-KEXEC-POSTFAILURE.md).

# Historical current state — first jump trial stopped, November 10, 2026

Native load succeeded and one orderly kexec request was issued. Target Android
was not observed within 300 seconds; ADB is absent afterward. No partition
writes or automatic retry. Original boot was verified restored on flash before
the trial; post-trial readback and target entry are unverified. Owner screen
observation and recovery are needed. Next: post-failure logging/readout diagnosis.
Earlier pending-approval/preparation status below is historical and superseded.

[Actual trial receipt](../../evidence/independent-recovery/native-first-jump-runtime-result.json).

# Historical current state — successful native source boot, November 10, 2026

Owner-approved temporary native source boot PASSED: Android home screen, native
config verified, original full boot restored on flash, recovery unchanged, normal
ADB restored. First experimental jump bundle/client and read-only live preflight
are prepared; no jump/load yet. Await owner approval for the actual jump.
Failed-jump logging remains post-failure follow-up, not a prerequisite.

[Exact first-jump scope and evidence](NATIVE-KEXEC-FIRST-JUMP.md).

# Historical current direction — November 10, 2026

Native kexec handoff kernel built and linked gates verified. Temporary source-boot
package and corrected live read-only preflight complete; awaiting owner-attended
source-kernel boot test. This enables subsequent experimental jump preparation.
Failed-jump logging follows a failed experimental jump, per owner direction,
and is no longer a prerequisite. Historical stricter sequencing below is superseded.

[Exact next test, rollback and evidence](NATIVE-KEXEC-NEXT-TEST.md).

# Active work queue — ordered delivery

## Existing-kernel console survives orderly reboot — November 10, 2026

One owner-approved run of runner SHA-256
`4c4e56c06ffdd8c8ec73a23dd4d7532bd2486ec8365257400ae46fdc3e0b8388`
wrote one unique console marker and requested one ordinary reboot into the same
installed4.9 kernel. Exactly one retained console-ramoops line matched the source
line byte-for-byte. Boot identity changed, normal Android returned, original full
boot/config hashes and backend geometry matched again, and UID2000 ADB restored.
No boot-image write, module load, experimental jump, failure injection, pstore
record deletion or nonmatching/PMSG/account-log collection. Approval consumed;
no automatic repeat. Private marker-only result/approval archive retained with hashes.

This qualifies console retention through this exact orderly software-reboot route,
not failure/power-loss retention, target early-entry coverage or the older TWRP
reader/layout. Keep #346/#348 open. Next engineering remains final CPU gate wiring
under serialization, partial-shutdown recovery/readout, and preservation of this
existing writer region in source/target RAM layouts alongside DMA/cache/MMU/EL
and early logging contracts. No new hardware test selected by this result.

[Actual retained-marker result](../../evidence/independent-recovery/pstore-warm-reboot-runtime-result.json).

## Combined source kernel Image built and retained — November 9, 2026

Approved isolated full-kernel compilation PASSED with the corrected legacy affinity
binding and bounded MT8163 secondary-off candidate linked together. Image is
15266304 bytes, SHA-256
`3df1bd6cd206b102b20c302b976db85a4103bdbad9e7e88c1f2f2ce45caf292b`;
header text_offset524288, memory extent16490496, flags10. Release remains
4.9.337-g72940eb733af. Original source, original build configuration and isolated
resolved configuration remain unchanged (configb0871996…f3859).

Linked verification confirms the CPU-kill callback calls bounded secondary-off,
the final gate calls the independent off-state checker, and legacy affinity uses
the selected conduit. Six actual source-admission controls pass, including corrupt
binding/core/config/boot-mode inputs and output inside original source. Combined
patch dry-runs cleanly against original pinned source. Local kexec suite63 tests
passes with one existing emulator skip; earlier Linux instruction checks remain
separately attributed.

Strict GCC13 compilation exposed baseline vendor compatibility errors. Five failed
build attempts/log hashes are preserved in the receipt. The final recipe includes
four whitespace-only indentation repairs (audio, CPU frequency, sensor mutex
unlock, USB), two getter return definitions aligned with existing enum declarations,
and a display header reusing its primary enum-return API declarations. ARM64 static
checks verify the enums' underlying integer type and width; function bodies are
unchanged by those type fixes. No warning policy was relaxed. These checks do not
qualify existing external-module CRC compatibility or the new kernel at runtime.

Retained Image/vmlinux/System.map/config, combined patch, source manifest, controls
and all build-attempt logs in a private archive on the lab and locally:15928406 bytes,
all archive/file hashes verified. Build timestamp/identity metadata were not frozen;
this retained artifact is attributable but bit-identical rebuilding is unqualified.
No boot image packaged, tablet command, CPU hotplug, reboot, flash or handoff.

Next engineering gates: wire the final off-state gate while hotplug stays serialized
through relocation; define partial-shutdown recovery with independent attributable
logs; preserve source-memory ownership and complete device/DMA/filesystem/cache/MMU/
EL contracts and target early/failure logging (#348). The linked final gate currently
has no handoff caller. Full compilation alone cannot veto generic restart paths or
admit this Image to a hardware boot/handoff test. Independent failed-load recovery
remains open under #346.

[Full build, failed-attempt trail and retained-artifact receipt](../../evidence/independent-recovery/kexec-source-integration-build-result.json).

## Corrected legacy affinity binding verified — November 9, 2026

Owner-approved transfer and exact ARM64 object compilation completed. psci.o is
19488 bytes, SHA-256
`89bdad7138c5ea831f12948d3b65dbcce80b6d0a14c720b17e7fa60f9138ff7d`;
original matched source remains unchanged. Corrected generated source hash is
`c52aa352263e0777a38d12ec6eda0958b1738c1d9c7ad75a9f5be411c463d9e4`.
17 native checks execute the actual generated initializer/callback text with
mocked APIs: no firmware call during initialization, positive OF match scores
accepted, wrong board/conduit/property/FID rejected, callback bounds and errors
preserved. 20 actual ARM64 callback instruction cases pass under Linux Unicorn,
with conduit stubbed: exact SMC32 FID/target/level/zero arguments, results forwarded,
invalid targets/levels rejected without calls. These are offline checks; live
query capability was separately observed in the earlier approved probe.

Added reproducible pinned-source/config builder and both validation scripts.
The build-only module wrapper has21 unresolved-symbol warnings from partial
symvers; it MUST NOT be loaded. This is object compilation, not full source-kernel
or boot-image acceptance. No tablet change or additional firmware call occurred.

Next prepared action: isolated full-kernel compile combining the verified legacy
binding and previously compiled bounded CPU-off candidate. Use a separate source
copy/build directory, preserve originals/config, record Image/config hashes and
errors. No deployment, boot-image write, reboot, CPU hotplug or handoff. Automatic
approval review rejected this as a broader integration than the approved binding
build; that combined build did not execute. Await explicit approval for the
combined offline build. Hotplug serialization/final gate wiring, partial-shutdown
recovery and independent target/failure logging #348 remain open.

[Binding compile and validation receipt](../../evidence/independent-recovery/kexec-legacy-affinity-build-result.json).

## Live affinity query accepted — November 9, 2026

One approved insertion of module SHA-256
`a41314b4afcf554343bea7ff80c7a5ca902f3068713d3d22e9ee1ed3a7441828`
completed exactly four SMC32 AFFINITY_INFO queries. CPU0/CPU1 returned ON (0);
CPU2/CPU3 returned OFF (1). Current CPU0 was ON and the online mask was 0x3,
consistent with those observations. This qualifies the legacy query capability
on the installed firmware; it does not qualify active secondary shutdown or
power-controller readback. Module unloaded, RAM file removed and normal UID2000
ADB shell restored. No CPU hotplug, reboot, flash or jump. Approval consumed;
no automatic rerun. Private source logs archived with hashes in the sanitized
[kernel query runtime receipt](../../evidence/independent-recovery/kexec-affinity-runtime-result.json).

Next source integration is the corrected legacy affinity binding, followed by
CPU-off/final-gate integration and recovery/logging contracts. Attempt to transfer
and compile that binding on the established host was rejected by automatic
approval review as broader than the approved probe build. The rejected transfer
and build did not execute. Await explicit approval for source-kernel binding
transfer/compilation; no additional tablet test selected or authorized. Earlier
source-transfer approval is retained with its original probe scope. Logging #348
and independent failed-load recovery #346 remain unqualified.

## Affinity query artifact ready for hardware review — November 9, 2026

Owner approved updated source transfer to the existing Linux lab host. Corrected
module rebuilt against the matched kernel/config with all 18 imported symbol CRCs
and module_layout verified against 19 exact providers. Module SHA-256:
`a41314b4afcf554343bea7ff80c7a5ca902f3068713d3d22e9ee1ed3a7441828`
(9088 bytes). Actual compiled ARM64 initializer emulation passes ten cases with
kernel/SMC APIs stubbed: valid topology issues exactly four SMC32 AFFINITY_INFO
queries, invalid board/conduit/FID/topology cases issue none. Unsupported firmware
responses remain unqualified; no real firmware was called. Eleven Linux probe
tests pass. Local suite remains 63 tests, one existing emulator skip.

Fresh read-only tablet preflight matched release/config/full original boot hash,
RAM-backed /dev, absent module and no prior KXAFF records. Zero insertions and
firmware queries. Temporary root adbd restored to UID2000. Historical transfer
blocker below is resolved; stale earlier module remains excluded. Corrected legacy
binding has been generated offline, but that source-kernel binding has not been
compiled after its Boolean-normalization correction and is not selected for this
runtime test.

Next: owner approval and availability for one insertion, four affinity queries,
fresh source-log capture, unload/RAM cleanup and normal-shell restoration. No
CPU OFF/ON/SUSPEND, power writes, reboot, flash or jump. A nonreturning firmware
call could require a physical power cycle; a host timeout cannot interrupt it.
Query success alone does not prove secondary shutdown, retained logs, independent
recovery or handoff. Those gates remain open under #346/#348.

[Exact build/emulation/preflight receipt](../../evidence/independent-recovery/kexec-affinity-development-result.json).

## Legacy firmware affinity prerequisite — November 9, 2026

The exact kernel's legacy PSCI initializer ignores the live device-tree
`affinity_info=0x84000004` property. Consequently the bounded secondary-off
candidate cannot establish firmware OFF and must refuse admission. Generic PSCI
support cannot be assumed. Prepared an exact-source, board/conduit/FID-gated
binding and a separate four-query capability module; neither is hardware qualified.
The query module uses SMC32 AFFINITY_INFO only, validates CPU0–3 topology, and
performs no CPU OFF/ON/SUSPEND, power writes, reboot, flash or handoff. Its runner
requires exact artifact approval, permits one insertion, preserves logs and
requires unload/RAM cleanup. A nonreturning firmware call still cannot be bounded.

Local suite: 63 tests pass, one existing ARM64 emulator test skipped locally
(previously passed on Linux). Eleven new tests cover policy, report parsing and
mocked one-shot execution/cleanup. Offline patched-source generation passes.
Initial module build and CRC review exposed OF compatibility match scores being
positive integers rather than Boolean one; corrected both callers with `!!`.
The earlier binary is stale and must not be tested. The corrected module rebuild,
compiled-instruction emulation, and fresh read-only tablet preflight remain pending.
Automatic approval review rejected source transfer to the existing Linux lab host;
no rejected transfer or tablet test ran. Await source-transfer approval before
continuing lab verification. Hardware approval must refer to the final rebuilt
hash; no approval request for a stale artifact. Logging/retention and failed-load
recovery (#348/#346) remain open. Earlier bounded-shutdown and staging receipts
retain their original limited scope.

## Bounded MT8163 secondary-off candidate compiled — November 9, 2026

Implemented the matched secondary shutdown core/adapter, pinned patch generator,
compile verifier and final read-only off-state gate. Unlike the old wrapper, the
candidate requires explicit firmware OFF, retains failures, checks regmap return
codes, uses nonblocking acquisition of the existing MTCMOS lock, and caps total
steps plus elapsed time across WFI/SRAM/power-status waits. Rechecks WFI under
lock before any write, preserves the vendor register sequence/other bits, and
requires both power-status banks OFF. No rollback/retry after partial power-down.
The final gate requires exactly four possible CPUs, CPU0 alone online, firmware
OFF for all three secondaries, both status banks OFF, and no sticky prior failure.
Its I/O adapter has no writer; it cannot initiate power sequencing.

Compiled actual ARM64 mtcmos.o/mt_psci.o and combined object against unchanged
source72940eb733af and exact configb0871996…f3859/release4.9.337-g72940eb733af.
Disassembly confirms the kill callback calls the bounded path and final gate exists.
Fifteen native C fault tests pass (frozen/backward clock, busy lock, WFI loss,
SRAM/status timeout, every successful-path read/write failure, every step-boundary
exhaustion, topology/sticky/final-gate errors). Linux suite24 entry/shutdown tests
passes including actual ARM64 entry emulation. Local kexec suite52 tests passes
with one local emulator skip independently passed on Linux. Original vendor source
hashes verified unchanged. Candidate objects are compile-only: the external-module
build emits15 unresolved-symbol warnings with the partial symvers table; its .ko
wrapper is NOT a loadable/runtime-qualified deliverable. No tablet operations.

Remaining integration: call the final gate while hotplug remains serialized through
relocation; preserve the source-memory ownership until then; bind survivor/masks,
handle partial-shutdown abort/recovery, and integrate device/DMA/filesystem/EL/cache
state and target logging. The core's4096-step/100ms policy is not calibrated hardware
timing. Poll budgets cannot interrupt a stuck firmware call, regmap/bus transaction,
or clock callback, nor bound the entire generic cpu_down lifecycle. A working
replacement source-kernel build/qualification remains necessary; this patch is not
an approved runtime module for the existing kernel. No kernel jump admitted.

[Compile/source/fault-test receipt](../../evidence/independent-recovery/kexec-cpu-off-build-result.json).


## Linux Image entry candidate implemented — November 9, 2026

Implemented a separate 40-byte/six-instruction ARM64 argument trampoline for the
matched relocator's zeroed x0-x3 entry. It loads the selected physical DTB into x0,
zeros x1-x3 and branches to the Image entry without stack use or memory writes.
It is not linked into the hardware-tested staging module and has no device runner.
Offline builder verifies exact assembled code/no unresolved relocations, ARM64
Image header/text_offset/full image_size, FDT header bounds, alignments and mutual
nonoverlap. It does not qualify the FDT tree, RAM ownership or a boot-ready layout.

Nine Linux tests pass, including actual GNU-assembled ARM64 instructions emulated
at six combinations of relocation/Image addresses (including above4GiB), poisoned
incoming registers, unmapped stack/DTB, no writes and exact branch/argument checks.
Local host suite37 tests passes with the emulator test skipped; local Unicorn
crashed before a result, so instruction execution was verified on Linux instead.
The real known-good Image/first appended DTB were extracted from hash-matched
original boot08fcf345…aa1e using bounded gzip/EOF checks. Builder exercised against
those actual bytes with hypothetical, explicitly unqualified addresses. The Image
file15137280B declares16363520B memory extent; collision checks reserve the latter.

Read-only live CPU nodes all select mt-boot; exact config enables MTK_PSCI and
HOTPLUG_CPU. Traced actual mt_cpu_psci_ops to MT8163 mt_psci.c/mtcmos.c: kill logs
PSCI failure then returns MTCMOS result, and WFI/SRAM/power-status busy waits have
no timeout. Generic affinity_info absence also permits success without off proof.
Do not use generic PSCI assumptions or call this unbounded path as a qualified
handoff. Next implement/review bounded failure-propagating secondary shutdown
against the matched power-controller contract; bind observed power status before
relocation and preserve source-memory ownership until every secondary is proven
released. Cache/MMU/EL, DMA/device/filesystem shutdown and independent target
logging/failure retrieval remain open. No CPU hotplug, firmware call or jump ran.

[Entry build/validation receipt](../../evidence/independent-recovery/kexec-entry-build-result.json).
[Live CPU/source audit](../../evidence/independent-recovery/kexec-cpu-shutdown-audit.json).


## Prepare-only staging passed on hardware — November 9, 2026

One exact approved module insertion and one client run passed on the installed
4.9 kernel. Three segments totaling 16 KiB matched independent CRCs including zero
padding; seven owned pages returned to zero. Execute stayed disabled. Module
unload, misc node/class removal and both RAM-file removals were verified. Normal
shell UID was restored. No reboot, flash or kernel handoff. Complete private
logs/approval receipts were archived on lab/controller with matching SHA256.
Approval consumed; no module/helper/test remains armed.

Fresh preflight also passed. It initially stopped before device access because
lab runner/verifier copies lacked the committed client-ELF and node-removal checks;
reviewed differences and synchronized those two scripts, preserving exact approved
module/client bytes. Runtime receipt qualifies allocation/copy/CRC/discard only.

Next source work: resolve matched handoff and independent target logging/recovery.
Further exact-source review confirms cpu_soft_restart's EL2 switch is conditional
on is_kernel_in_hyp_mode/is_hyp_mode_available; observing CurrentEL1 alone does
not select an HVC route. In arch/arm64/kernel/smp.c, op_cpu_kill returns success
without a callback, and __cpu_die logs some shutdown failures rather than returning
a veto. Therefore one online CPU alone is insufficient proof that firmware has
released every secondary CPU before overwriting source memory. Bind actual CPU
operations and validate a failure-propagating parking contract; do not inherit the
upstream false stuck-CPU stub. DTB/x0 trampoline, Image placement, cache/MMU,
device/DMA shutdown and filesystem quiescing remain open. Source ADB ends at
handoff; no target early/failure log or retention route is yet qualified.

[Actual hardware staging receipt](../../evidence/independent-recovery/kexec-stage-runtime-result.json).


## Prepare-only kexec loader port built — November 8, 2026

Continued source work beyond the successful logging probe. Ported the generic
kexec allocation/copy machinery to the exact tested4.9 kernel. The19,960B module
b2113b08…e3b9 contains no restart/relocation/hypervisor module, links no shutdown
callback, and its unused execute stub is exact return-EOPNOTSUPP. All30 required
symbol CRCs match exact-source providers; compiled instruction/import checks pass.
Repaired an orphan source-page allocation failure edge and added bounded copied
segment checks,3-segment/32MiB payload caps,24,592 owned-page hard cap and actual
copied-page CRC/zero-padding reports with count-to-zero discard/close cleanup.

Built a native static client4eea0326…290d for one16KiB three-segment staging cycle,
independent checksum comparison, blocked execute/duplicate-prepare requests and
verified discard. Guarded runner requires fresh module/client/boot-bound approval,
exact current release/config/boot, root adbd, executable RAM /dev, clean staging
state and available memory; no flash/reboot/CPU shutdown/handoff.28 tests pass
including the earlier probe suite. These checks are source/build/preflight evidence,
not actual hardware RAM-staging acceptance.

Read-only live preflight passed with631800KiB MemAvailable. No module insertion,
client execution or RAM file upload occurred; temporary root adbd ended and normal
shell UID restored. New stage runtime approval is pending separately; the prior
logging-probe approval is consumed. No actual kernel jump is admitted.

Further source review found the native4.9 relocator clears x0 before kimage_start;
a direct Linux Image branch therefore needs the appropriate DTB-carrying entry
trampoline. CPU parking, EL/HVC behavior, device/DMA shutdown and clean filesystem
quiescing still require explicit handoff contracts. No new jump binary selected.

[Build review receipt](../../evidence/independent-recovery/kexec-stage-build-result.json).
[Exact module/client/procedure](../../projects/firetabs-android/kexec-stage/README.md).


## Actual Linux compatibility probe succeeded — November 8, 2026

The exact logging-only module371fe33c…e889 loaded once into the installed
4.9.337-g72940eb733af kernel, passed normal ABI/version checks, produced all ten
fresh kernel records over ADB, and unloaded successfully. Runtime observations:
EL1,4KB pages,3 online CPUs at the sample instant; all8 queried symbols present,
including set_cpu_boot_mode_flag. This is actual hardware execution/log capture,
not a model result. It qualifies this module ABI and current-kernel printk/ADB
transport only, not kexec, CPU parking, firmware state, new-kernel entry or logs.

The first preflight stopped with rooted debugging disabled; owner enabled it.
Two exec-out stream staging attempts timed out with0 module insertions and verified
RAM cleanup. Standard adb push into verified RAM-backed /dev solved the host
transfer problem without changing module bytes. One actual insmod, no force-load,
verified unload/module absence and RAM cleanup.13 runner/verifier tests pass.
Private evidence archives match lab/controller. Original boot/recovery/bootstrap
were verified before the one approved normal boot; no flash or handoff occurred.
LineageOS remains running; temporary root adbd ended, user shell restored. No
watcher/helper/module remains armed, no owner action is pending, approval consumed.

Next source stage: adapt a matched4.9 kexec loader, keeping execution disabled
until allocation, CPU/DMA shutdown and entry contracts are independently reviewed.
Do not reuse the probe approval for a handoff or an additional module execution.

[Actual hardware receipt](../../evidence/independent-recovery/kexec-probe-runtime-result.json).


## Linux-to-Linux stage1 probe built — November 7, 2026

The actual original normal boot image runs 4.9.337-g72940eb733af, not the 3.18
TWRP kernel. Extracted its embedded config (b0871996…f3859) and located exact public
source commit72940eb733af8df948cc216cb977cd8be9cba5a9 in amazon-oss. A stale cached
3.18 vendor config is not the installed normal kernel configuration. No attempt
was made to load a module into the unmatched TWRP kernel.

Built a6144B logging-only ARM64 probe with exact release/ABI flags and zero config
option changes. Six CRC providers were generated from individual exact-source
objects; the partial table is not a complete kernel build's Module.symvers.
Controller/lab artifact hashes match; all required CRCs/imports pass verification.
Actual disassembly has40 instructions, one CurrentEL read and no privileged write,
SMC/HVC, indirect jump or cache/MMU maintenance opcode. External calls are limited
to the reviewed logging/read helpers. GCC13.3 differs from the original GCC6.3.1;
runtime module-version checks remain mandatory and no force-loading is permitted.

Thirteen verifier/runtime boundary tests pass, covering wrong architecture/release,
missing/mismatched CRCs, handoff imports, current TWRP rejection, wrong live config,
wrong approval, preflight-only behavior, rejected insertion with no retry, complete
fresh-report attribution, RAM cleanup and unload. The runner performs no reboot,
flash or kernel handoff. Execution requires fresh exact approval/current availability
and a live normal-kernel release/config/fullboot hash match with existing root.
Probe staging is only in RAM-backed /dev; a rejected module is never forced.

This is a completed compatibility-test artifact, not a working kexec implementation.
No new image, module insertion or reboot has occurred. Next is one separately
approved boot of existing LineageOS and one probe load/unload, then a matched kexec
port using the observed compatibility report. The initial probe cannot establish
DMA shutdown, stopped secondary CPUs, firmware entry or target logging.

[Build receipt](../../evidence/independent-recovery/kexec-probe-build-result.json).
[Source and concrete review](../../projects/firetabs-android/kexec-probe/README.md).


## New investigation: Linux-to-Linux handoff, November 7, 2026

Owner rejected further development of the failed LK mailbox/screen avenue.
Selected a distinct source investigation: use the running 64-bit Linux recovery
as the image loader, with a matched ARM64 kexec port. This bypasses custom LK
hooks, LK allocation/storage services, and its 32-bit-to-64-bit entry transition.
It does not replace secure firmware or establish PSCI/SMP compatibility.

Read-only live facts: recovery 3.18.19-g51c2c8d5bfb is aarch64 with root access;
modules_disabled is 0. Captured 130938 bytes of current dmesg over existing ADB;
this qualifies that live recovery read path only. Kexec core symbols are absent.
Pinned and Git-blob/SHA256-verified 21 upstream module files at
4ba956fd60b29d2fea324515596b392afdcfa2c5. All seven named dynamic dependencies
are present in live kallsyms, and kallsyms_lookup_name has an export symbol.
This is symbol-name evidence, not compatible signatures or a working module ABI.

Do not load upstream unchanged: its default detect_el2 path dereferences the
missing set_cpu_boot_mode_flag helper; it stubs the stuck-CPU test false, has
unqualified CPU-mode decoding/identity mappings, and lacks a matched recovery
build configuration here. Missing source/config provenance must be resolved or
a reproducible matched first-stage kernel built before module qualification.

Next milestones are distinct: (1) resolve build ABI and compile a no-handoff
compatibility probe; (2) audit memory placement, CPU parking, cache/MMU state,
DMA/device shutdown and firmware entry; (3) if admitted, chainload an already
working kernel before changing to the modern kernel. Preparation/load errors
must be retrieved over the source Linux's working host log connection. That
connection will disconnect at handoff; target early logs, reserved-memory ownership
and failure retrieval still require independent qualification. No claim of
continuous ADB across kexec, retained RAM across power-off or guaranteed target logs.
No physical test, module insertion, boot-image change or reboot selected.

Upstream: https://github.com/fabianishere/kexec-mod . Latest MT8163 upstream work
also explicitly requires custom TF-A/U-Boot/OP-TEE for its Echo Dot target; it is
not a drop-in douglas firmware alternative. Do not transplant its firmware or
reserved memory to this tablet.

[Read-only source/compatibility receipt](../../evidence/independent-recovery/recovery-linux-kexec-route.json).


## Actual copy-control3 result — November 7, 2026

The approved corrected known-stack control reached the home screen, but full
collection again returned HOSTCONTROL only (sequence 1, 85 bytes), with no loader
record or invalid slot. No attributable screen pattern was captured; the owner
was not watching closely, so physical absence is not established. Hardware capture
acceptance failed. Do not repeat this method unchanged or admit a custom-kernel
trial on these results. The cause of missing loader records remains unresolved.

The single original FACTORYM return helper exited 0 after USB reseating. Complete
readout and receipts were archived on lab/controller with matching SHA256. Normal
bootstrap was already original; no bootstrap restore write was needed. Original
full boot restored once, readback and final boot/bootstrap/recovery/header/GPT/alias
checks passed, RAM staging cleanup verified. TWRP remains running, no reboot,
watcher/helper running, pending owner action or armed test. Exact approval consumed.

The next decision is whether to change the boot/observability approach or end the
modern-kernel port effort. This failed capture is not proof that the hardware is
incapable of a port. No further physical test is selected.

[Actual trial receipt](../../evidence/independent-recovery/loader-copy-control3-trial-result.json).


## Copy-corrected capture control — recovered November 7, 2026

The former tail-hook model was invalid for physical delivery: the bootstrap copies
only 968 bytes of embedded LK. The late hook is outside that span. This explains
the placement error, not every historical missing record or a kernel boot failure.
The corrected resident code installs the exact branch before the original LK cache
clean/app. All linked bootstrap bytes fit in the copied prefix (1898/2304 bytes).
The native timer-dependent display routine is replaced by bounded mirrored pixel
writes. Framebuffer visibility and cache/controller effects remain hardware assumptions.

Recovery validation: source rebuild is byte-identical to the packaged bootstrap;
12 exact-copy/execution controls, eight pixel phases, ten synthetic photo controls,
five decoder/guard unit tests and independent artifact verification pass. On this
Mac the sandbox terminates ARM emulation with signal 4; the same replay passes
outside the sandbox. Pillow is required for the controller photo decoder.

Exact review pair:
- Boot: `b9377fdb1c8ca78e627d19db0d0eee7fc84228acc54f248edc98ebec3e05ea1f`
- Observer: `2dd2de6bb6b07b5c616621cd4ed65f1a4a023cb695a41c896496cc67f1229188`
- Screen token: `d73d`; scope: `known-boot-copy-control-3`.

The private local bundle contains original rollback images, exact hash guards,
collection/restore scripts and the camera decoder. It is unapproved, unexported and
unarmed. Earlier approvals are consumed. Historical embedded-tail packers now reject
use. No new custom-kernel boot or claim of qualified physical logging follows.

The remaining dependency is a physical observation of this changed known-stack
control, with the owner available for recovery and a camera recording the entire
screen from before boot through the observation. This is a separate calibration
boot; the standing restriction against separate diagnostic trials must be explicitly
resolved before installation. Do not treat the general request to make progress as
exact approval or owner availability. First read-only preflight must confirm the
current original hashes, recovery identity and partition geometry; old TWRP state
is historical, not a fresh device observation.

If explicitly selected: install the exact observer and known-stack boot once using
the bundled guards, verify readbacks, and have the owner perform the agreed boot.
Capture the screen continuously; decode still frames locally with the exact token.
Collect the full mailbox before restoration, then restore and verify originals with
the existing scripts. No automatic reboot/return or retry is authorized here.
Phase 1 establishes resident arrival/install result; phase 2 establishes late-hook
arrival; later rows identify rejection/recorder results. A screen record alone does
not qualify durable logging or prove kernel entry. A blank/unreadable capture cannot
locate execution. If no attributable screen or mailbox record is recovered, stop
this capture approach and reassess the boot route rather than repeat it unchanged.

Local decoder:
```sh
out/loader-audit-venv/bin/python scripts/decode_loader_screen_photo.py \
  --image /absolute/path/to/frame.png --token d73d \
  --quad TL_X TL_Y TR_X TR_Y BR_X BR_Y BL_X BL_Y
```
Corners are in logical portrait order. Private images/nonces stay out of git.


Offline source delta: independent arrival/first-rejection witness implemented.
New analysis-only late profile uses1547/1587 proven console bytes and preserves
original read redirection. Eleven actual ARM controls pass, including exact
resident main and archived formatter, register/SP/APSR replay and distinct failure
codes. Display pixels/hardware remain modeled. Native display update can reach
an uncapped tick-dependent wait: actual wait replay returns with advancing samples
and remains in the loop with frozen samples. Both physical packers reject this
profile pending independent display-path qualification. No candidate/device action
or new kernel build; originals remain verified/TWRP/unarmed.


Actual control2 complete: owner confirmed original home screen, but collection
passed with only HOSTCONTROL seq1/85B, no loader/kernel record or invalid slot.
One original FACTORYM helper exited0. Evidence archive and supplement matched
lab/controller. Normal bootstrap already original: no agent bootstrap restore write.
Original fullp5 restored once; fullp5/p6, bootstrap/header/GPT/alias/RAM cleanup
verified. TWRP left running, no reboot; all workers stopped, no owner action pending.
One bounded /proc/last_kmsg read returned No such file; no fallback log recovered.
Exact approval consumed. No repeat trial, new kernel build or control3 selected.
Next: establish active bootstrap reachability and expose the first rejected gate
before another mailbox writer test. Logging and custom kernel entry remain unproved.
[Actual control2 result](../../evidence/independent-recovery/pre-shutdown-control2-trial-result.json).


Historical control1 result follows.

Latest actual result: known-stack capture control1 is complete. Owner confirms home
screen with unchanged original header/kernel/DT/ramdisk, but full collection found
only HOSTCONTROLseq1/85B and no target record. This fails recorder qualification;
prior silence cannot locate a modern-kernel failure. One original FACTORYM helper
exit0; expired pre-helper return window preserved with0 launches. Original normal
bootstrap was already original, so no agent bootstrap restore write. Original fullp5
restored once; fullp5/p6, headers/ranges/GPT/aliases/RAM cleanup verified. TWRP left
running/no reboot; no watcher/helper/owner action pending. Exact approval consumed;
no unchanged control/kernel build/trial or rearm selected.
[Actual control result](../../evidence/independent-recovery/known-boot-capture-control-trial-result.json).

Historical installation snapshot (superseded by completed result above): exact approved known-stack control p5+normal observer installed
once, readbacks/p6/RAM cleanup verified. Copied guard's stale trial8 prefix/seed pins
were corrected atd19f37e without changing firmware bytes; failed receipt retained,
all five required checks and corrected-source installed preflight passed. One
observation-only watcher durably armed/helper0; no automatic return/reboot. Owner
Reboot/System +≥5min observation/desk report pending. Originals not currently
restored. No rewrite/rearm or historical approval reuse.

## Latest selection — known-stack recorder calibration

Owner selected the known-boot capture control after the complete modern draft
produced no attributable output. The exact control package preserves the original
header/kernel/appended DTs/ramdisk and adds the existing loader recorder only in
unused padding plus a fresh mailbox. Separate install/observe/manual-return/collect/
assess/rollback tools and the [complete review](KNOWN-BOOT-CAPTURE-CONTROL-REVIEW.md)
are prepared. Actual read-only lab preflight passed full original boot/recovery,
normal/return bootstrap/header/GPT/aliases. Original images/TWRP remain; no write,
arm, helper or physical trial. Exact approval and current availability are the
remaining physical gate. This selection supersedes older no-control selections
below for this exact calibration only; trial8 and the failed modern draft stay held.
No loader result qualifies kernel entry, modern USB or kernel-side retention.


Actual first-draft test1 is complete. Original full boot restored once and full
boot/recovery/RAM cleanup verified; TWRP left running, no reboot, no process armed
and no owner action pending. USB capture0B/no matching endpoint; returned image
unchanged from candidate, only HOSTCONTROLseq1/73B, no kernel record. Logo/black
loop does not prove kernel entry/reset cause. One original FACTORYM helper exit0
after a host-only receipt-permission failure stopped the first waiter before any
helper launch; guarded return-only continuation corrected mode600. Evidence
archives match lab/controller. Approval consumed; no repeat/new trial selected.
See [actual result](../../evidence/independent-recovery/first-draft-trial-result.json).

Completed first kernel draft: **6.18.34-valethon-draft1+**. Combined build
42091153900 succeeded at dfdd080; enforcing VM and independent final package
checks passed. The complete16MiB boot image and private delivery archive are in
out/valethon-first-draft-1. The source receipt is
[evidence/independent-recovery/first-kernel-draft-result.json](../../evidence/independent-recovery/first-kernel-draft-result.json).
USB streaming and retained boot-tail logs are included; no automatic-recovery
engineering was added. No tablet boot/logging acceptance, installation or trial
is claimed. The next test must prioritize capture/retrieval before restoration.
This completed draft supersedes older no-build/minimal-control selections below.

Latest owner direction: finish the complete first kernel draft and prioritize
test results/retrievable logs over automatic recovery engineering. A combined
first-draft build is selected: existing board ports, enforcing PID1, USB streaming
and retained kernel logs. Existing rollback stays available; no new recovery
automation, physical trial, install or reboot is selected. Positive hardware
logging remains unconfirmed. This supersedes older “no build selected” text below.

Latest owner requirement: next tablet test uses a complete best-supported kernel
candidate with logging positively confirmed beforehand. No separate partial
diagnostic-kernel/observer test is selected. Qualification is still absent;
see the latest constraint in [the plan](LOADER-UNBLOCK-PLAN.md).

Testing-process correction: physical candidate writes and arming are held until a
reviewed known-kernel control qualifies the actual logging path. No custom kernel
boot or kernel log is confirmed. Read-only collection and original rollback remain
available. See [measurement repair plan](LOADER-UNBLOCK-PLAN.md).

Current346: actual trial7 complete, originals verified/TWRP and unarmed. Only
HOSTCONTROLseq1/85B retained; no exact kernel entry/handoff or kernel record. TWRP
repair restored normal bootstrap; approved fullp5 restoration/readbacks verified.
Host collector read-size failure remains unexplained. No owner action pending.

Current decision: hold custom-observer trial8 unarmed after owner research request.
Primary Douglas port evidence reports boot/display/touch/USB networking on vendor
3.18. Our known-normal backup is ARM64. Correction: exact diagnostic DT enables
USB0/peripheral and its port0 PHY; only USB1/port1 is disabled. Missing USB remains
unattributed. Next: offline ABI/compatible-enforcing-policy
profile for a minimal logging control on the already-booted matched kernel/DT and
existing USB driver. No old OS installation, stock-DT graft into mainline, policy
bypass, build, device access or new physical trial is selected. Trial8 artifacts
remain retained. See [revised plan](LOADER-UNBLOCK-PLAN.md).

Owner priority correction,29 October2026. Read the
[ordered roadmap](ORDERED-ROADMAP.md), [stable task/dependency contract](ordered-roadmap.json)
and [Project4](https://github.com/users/TOVSWORLD/projects/4) before selecting work.
The board is the source of live state. Do not resume historical peripheral queues.

## Current selection

- Administrative task#438/PR448 is complete; ordered board readback passed.
- Existing-work exception#440/PR436 is source-accepted after six exact-head checks
  at8ff8731 and actual PWM object/config/final Image run40881461603. No new PWM
  binding/peripheral scope follows. The source receipt is in
  evidence/pwm-kernel-integration/build-result.json; hardware remains unqualified.
- **Decision#439 is complete:** owner approved the reviewed persistent software
  unlock and destructive lab-host/device work on29 October, with immediate
  reporting of breakage or unexpected state. Do not ask that approval again.
- **Execution#347/PR452 has reached actual TWRP3.3.1-0.** Original full BootROM
  stage and original fastboot recovery stage both exited0. Post-full fastboot
  identified Douglas; recovery_x capacity was corroborated against decoded GPT.
  ADB reports recovery/douglas/TWRP3.3.1-0, kernel3.18.19; recovery and kernel logs
  were retrieved. [Runtime receipt](../../evidence/approved-lab-entry/runtime-result.json).
  The case stayed closed and no short was applied. [Entry acceptance review](ENTRY-ACCEPTANCE.md) accepts the selected route and
  observed interim Android endpoint; independent failed-load stock return#346 and retained
  failure logs#348 remain separate unpassed gates. No maintained-kernel or
  app-QA boot is claimed; Android11 runtime is recorded separately below. Host sudo and temporary USB/service setup
  are complete; do not resurrect those resolved blockers or repeat approval.
- **Android11 ROM and ARM Google services are now installed**, with actual
  updater RC0 and recovery-menu return for both. Read-only system inspection
  confirms API30/ARMv7. First Android boot and initial setup are now
  confirmed by owner home-screen observation and authorized ADB boot_completed=1.
  Android runtime reports encryption unsupported and SELinux Permissive; owner
  reports device-policy enrollment failure. No policy/security bypass was applied.
  App/provider QA remains unmeasured. The GApps installer has a tested local ABI
  compatibility correction; unchanged app payloads and exact receipts are in
  [qa-install-result.json](../../evidence/approved-lab-entry/qa-install-result.json).
  [Runtime receipt](../../evidence/approved-lab-entry/android-runtime-result.json)
  records installed package/browser/security facts. Google Play services20.45 and
  no Chrome are current prerequisites to resolve before passkey/browser acceptance.
  Do not repeat unlock, wipes, installations or first-boot request.
- **Owner correction,30 October: platform release before app QA.** Do not select,
  build or install Connect/passkey QA candidates on the interim ROM. First deliver
  the stable, supported, updated project OS. #333 owns explicit upstream/version/
  security/update-path selection, reproducible integration, stability and branding;
  #354 retains attribution/distribution review; #340 packages the branded release;
  #341 admits feature QA only afterward. The current LineageOS18.1 baseline is not
  that final release. Branding covers boot/setup/wallpaper/launcher/About, with
  truthful Android/security-patch fields and upstream notices. No parallel branding
  task or unrelated peripheral off-ramp is opened. Current #347 entry milestone is accepted;
  phase344 now has observed Android-independent TWRP entry under reopened#346.
  First normal diagnostic trial produced no kernel logs/diagnostic USB identity.
  Existing recovery returned and the full original boot image was restored/verified;
  owner confirms TWRP. No maintained-kernel entry is inferred. Generic enforcing
  VM tests reproduced and corrected ARM64 open flags, device/configfs labels and
  PID1/kernel-thread domain handling. A second normal trial also produced no logs; original boot was again restored.
  The inherited-watchdog handoff correction now has a successful retained kernel
  build and enforcing VM run. Candidate3 was tested once and also produced no logs/diagnostic endpoint.
  Its pending manual return step was completed separately without another boot
  trial; original boot was restored/verified and owner confirms TWRP. Nothing is
  armed under draft PR453; watchdog hardware handoff remains unobserved. Ordinary return
  remains complete; intended failed-load and348 retention remain unqualified.
  #345 is closed not planned because no inspection was needed.

The completed admission decision identified one operational route or state why none is safely
available, the minimum diagnostic package and entry/memory/CPU/transport contract,
pretrial recovery/log/power/thermal provisions, stop criteria and one concrete
reviewable next action/owner decision. Do not repeat stock/cable/photo captures,
LK microtraces or synthetic readiness wrappers. A closed NO-GO does not admit entry.

## Required sequence

1. #439 decision → explicit GO → #347 bounded entry/trial → #346 independent
   failed-load stock return → #348 useful retained diagnostic logs.
2. #22 diagnostic memory/UART/internal storage → #18 clocks/reset → #19 pinctrl/EINT
   → #20 PMIC/domains.
3. #329 display/backlight → #330 touch → #331 GPU/composition → #333 Android candidate.
4. #334 Wi-Fi → #442 audio → #335 charging/thermal → #443 suspend/wake → #336 USB
   → #444 SD → #446 video → #441 Bluetooth → #445 sensors → #447 cameras.
5. #27 final DT/dependency validation → #353/#354 licensing/distribution → #340 exact
   beta/recovery handoff → #341 actual QA admission review.

Issue#345 is closed not planned; its conditional inspection branch was not selected.
Normal recovery/current-kernel log capture is complete. Task#348 names only the
remaining failed-boot retention/retrieval qualification. Issue#346 is reopened for remaining failed-load qualification;
ordinary return alone is not failed-load evidence, which remains explicit
in phase344/release acceptance. Historical phase#106 has100 sub-issues; preserve its source evidence and
open runtime exit, but put operational work under#344. Do not create more source
micro-scopes there or mistake completed child counts for recovery qualification.

## Execution contract

One primary Task issue per PR; one implementation task Active at a time. Use an
issue-numbered branch and Updates #N; Fixes #N only after actual acceptance. Every
required check must pass at the exact head before merge to development; main only
through releases. Source/build completion is distinct from device qualification.

Follow the recorded predecessor gate. If blocked, record the condition and work
only inside that issue or on a documented necessary prerequisite inserted ahead
of it. Update order/dependencies before coding. Never bounce to an unrelated
peripheral. Owner-approved scope exclusions remain explicit and do not become
hardware passes. Parent rollups do not themselves authorize forward execution.

Synchronize/read back Status=Delivery state, labels, native parent, execution order,
dependency, acceptance gate, primary PR, latest result, next action and blocker at
selection, PR changes, merge and acceptance. Preserve completed scopes in the
unfiltered default view. No continuous background-agent claims or rough-percentage
updates; report measured entry/boot/log/return milestones.

Standing low-risk read-only lab authorization remains valid. High-brick-risk
unlock/downgrade/bootloader/security writes/electrical actions require explicit
approval of a concrete reviewed procedure. Do not weaken SELinux/security for logs.
No large/paid resource without the existing gate. Raw logs/selectors/identifiers
stay private in ignored out/; publish sanitized exact revision/artifact receipts.

## Actual qualification boundary

Stock recovery entry/ordinary return and a capped320KiB Android USB export are
observed. Experimental loading, independent failed-return, retained first-kernel
logs and the14 hardware groups on the new kernel remain unqualified. Current full
DT contexts30/24 still fail; DSI/PHY source nodes stay disabled and PWM source status
is okay, unchanged. All seven PID1/host-serial admission gates remain denied.
Source/build successes are real groundwork, not first-boot or beta admission.

The previous detailed source queue is retained as
[historical evidence](history/ACTIVE-WORK-QUEUE-2026-10-29-pre-roadmap.md), not a list
of next actions. Old pre-CI sentences there are historical. The ordered live board
and current entry decision take precedence.
