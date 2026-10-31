# Work log — 24 October 2026

## Commands and results

- Inspected the empty workspace; no applicable AGENTS.md found. Initialized outer
  Git repository on `port/douglas-bringup`. No remote added and nothing pushed.
- Initial sandbox network Git failed DNS resolution; approved network execution
  succeeded. This was an environment restriction, not an unavailable repository.
- Queried official Android/AOSP and Lineage release sources. Retrieved official
  Lineage changelogs with curl after web-reader 403 responses.
- Used `git ls-remote`, shallow `git clone --depth 1`, GitHub public REST metadata
  and selected raw source files. Exact clone commits/URLs are in the source lock.
- Inspected device/common/kernel/vendor/hardware sources, release notes, original
  and newer amonet source, current amazon-oss common/giza trees and compatibility
  patches. Never executed the exploit or repository installer scripts.
- Enumerated direct forks and searched related newer MT8163 work. Found explicit
  douglas board support in amazon-oss 4.9.337, including its lineage-22.2 branch.
- Read actual Android 17/Lineage 24 `NetBpfLoad.cpp` runtime gates. Copies saved.
  Lineage 24 Connectivity head inspected: `7c04d866538e6f689823b769fb5c1e614ca0e295`.
- Fetched official Play HTML, decoded its embedded JSON and checked the scraper
  field mapping. Extracted current Home minimum Android/version metadata.
- Created device branch `port/android11-bringup` at `4c557e6...`.
- Fixed wrong optional vendor inheritance (`vendor/douglas/douglas` →
  `vendor/amazon/douglas`) and made common BoardConfig inclusion mandatory.
  Saved the actual diff in `patches/0001-douglas-require-correct-vendor-and-common-paths.patch`.
  This prevents silently dropping device vendor files or common configuration.
- Probed all eight existing platform patches against pinned Android 11 touched
  files. Five failed, three applied. Initially Git skipped fixtures because it
  discovered the enclosing repository; corrected isolation with
  `GIT_CEILING_DIRECTORIES`, added a skipped-patch guard, and reran. Only the
  corrected results are retained as evidence.
- Rebased existing bitmap patch native paths to Android 11's `libs/hwui/jni/`.
  Its three-file applicability check passes. No new graphics behavior was invented;
  inherited workaround semantics still require review and hardware tests.
- Added restore, offline source checks, patch probe and host preflight scripts;
  pinned dependency manifests and an unbuilt Linux container recipe.
- User confirmed Fire OS 5.7.1.0, 12.33 GB internal capacity (16 GB SKU), separate
  30 GB SD card, CP4 lab on latest firmware, and full Home functionality required.

## Validation and limits

`python3 scripts/check_sources.py`: PASS for source pins, manifest paths, corrected
inheritance and six ARM/ARM64 graphics blob ELF headers.

`python3 scripts/probe_android11_patches.py`: saved independent applicability
results, including actual missing Android 11 bitmap paths and context failures.
The rebased bitmap patch passes. This is a partial source fixture, not a platform
checkout. It cannot validate module dependencies, compilation or runtime behavior.

`git -C sources/device-douglas diff --check`: passed.

`python3 scripts/preflight.py`: exit 2, expected; host is arm64 macOS, filesystem
is case-insensitive and free disk is ~42 GiB. RAM is 36 GiB.

Legacy kernel clone emitted case-collision warnings for netfilter headers/sources
and an rcutorture filename. Those apparent tracked modifications must not be
exported as development patches. Restore that repository on case-sensitive Linux.

No Android build, image generation, full repo sync, GApps download, APK download,
paid resource use, tablet connection, unlock, wipe, flash or physical test occurred.
The existing release ROM (~482 MB) was not downloaded. Inspection sources occupy
roughly 1.1 GB expanded before small source fixtures.

## Direction clarified after initial investigation

The user selected a current maintained Android kernel that moves with Android releases,
using the old kernel trees as hardware references. General-purpose tablet usefulness is
the primary goal; Crestron Home is one application requirement. Optional hardware-absent
features may be unavailable with accurate declarations. The prior old-kernel/intermediate-
Android progression is superseded. Updated README, maintenance direction, feasibility
conclusion and continuation notes to agree. No new porting/build/device work was started;
waiting for the user's next instructions.

## Crestron panel-mode scope

User added a separate question about native Crestron panel behavior and clarified that
the setup interface selects an application/use, then runs one app at a time. Official
TSW-70 documentation confirms this model. Added a panel-mode research track to the
maintenance document, distinguishing supported Android/web clients from an unverified
native-runtime port. Found official Android clients for Smart Graphics (Go) and
HTML5/Construct (ONE, documented Android 14+), plus Android browser Web XPanel support.
No claim that arbitrary native panel applications can run on douglas; no prototype,
firmware extraction, large download or device operation was undertaken.

## Crestron research completed after user authorization

- Verified the native single-selected-app model against TSW-70 documentation.
- Located the real public app-update manifest. Initial `70series` URL attempts
  returned 404; corrected `70-series` spelling using official release-note evidence.
- Checked archive sizes with HTTP HEAD and reported the approximately 79 MiB total
  before downloading HTML5 host, General Web and touchscreen Home archives.
- Preserved download/source metadata, hashes and extracted manifests under
  `evidence/crestron/`. APKs and full selected disassembly remain ignored under
  `work/crestron/`. No APK or native library was run or modified.
- Used installed Android SDK `apkanalyzer` and Java 25.0.2 for static inspection.
  Identified ARM32-only bundled native libraries, explicit loads of missing
  `cresstore_jsonJNI`/`SecureStorageJNI`, localhost signal transport, and General
  Web's signal bridge. These are observed dependency contracts, not runtime results.
- Public firmware manifest was readable and advertised `3.003.0021.001`; its exact
  firmware URL returned HTTP 404 on HEAD. An older tested URL also returned 404.
  Did not download a full PUF, BSP or emulator image. No emulator is configured here.
- Checked official Home/Go/ONE/Web XPanel deployment paths, native CH5 video
  architecture, Android lock-task APIs, Microsoft certification documentation,
  Zoom Android controller requirements, and current Crestron mobility-license status.
- Searched public repositories and inspected CrestronKeeper at pinned commit
  `6546f94d2864614c8cc5ca069fad0c39b3b75f69`; it targets the old mobile app and is
  a launcher/lifecycle reference, not a native-runtime port.
- Added `scripts/inspect_crestron_apps.py` to reproduce archive verification,
  manifest/native-library inventory and selected class inspection. Added
  `docs/CRESTRON-PANEL.md` with a project direction and gated native-service milestone.
- Retained the current-kernel/general-purpose Android objective. No OS/kernel
  implementation, physical testing, processor program change, account messaging,
  paid-resource provisioning or native compatibility prototype was performed.

## 2026-10-24 — GitHub project split and CI

User supplied TOVSWORLD/Firetab-Android and authorized publishing the starting repository.
Added two project entry points with separate scope, acceptance and validation records:
`projects/firetabs-android` and `projects/crestron-panel`. Shared evidence and tools retain
existing paths to preserve reproducible commands. These are repository projects, not
separate GitHub repositories or GitHub Projects boards.

Read actual Valethon AI guidance and CI checks as reference. Adapted verification,
anti-vaporware, canonical evidence, truncation detection, and focused blocking checks.
Added three read-only GitHub Actions jobs, offline checker and rejection-path tests.
No paid model service, privileged runner, large build/download or physical device action.
Firmware and panel execution stages remain explicitly `not_run`.

Published initial main revision `82c7fc4`; GitHub run 40158159017 passed all three
jobs and six rejection-path tests. Updated checkout to the pinned v6 revision after
reviewing the hosted runner warning about the v4 Node runtime.

## 2026-10-24 — Development-to-main release policy

User required main to be locked except for development-to-main releases. Created
`development`, enabled CI on integration pushes and added a metadata-only source-branch
check. Main requires release PRs from the same repository's development branch.
No PR code executes in the privileged-event workflow; token permissions stay read-only.

## 2026-10-24 — Public contribution and release process

Added public contribution, conduct, governance, security, support and provenance docs;
architecture, setup, testing, troubleshooting, roadmap, decision and release guides.
Defined independent product SemVer streams and source-workspace tags, with a conditional
monthly first-Tuesday window and explicit stable/LTS acceptance. No release was published.

Implemented release-manifest checks and rejection tests; added tracked documentation-link
and form/taxonomy checks to Repository integrity. Created seven issue forms, CODEOWNERS,
release-note categories and monthly Actions dependency PR configuration. License selection
is awaiting the owner; external code/doc merge acceptance is explicitly held meanwhile.

Applied 27 labels, three milestones and eight bounded native parent/sub-issues.
Seed identities are recorded in projects/github-setup.json; the reconciliation script
preserves existing issue bodies and states. Enabled private vulnerability reporting.
Active tag ruleset 25808738 blocks updates/deletion for all three release tag prefixes.
No model service, full build, firmware upload or physical test was performed.

## 2026-10-25 — Actual GitHub Projects

The earlier split created folders and parent issues, not GitHub Projects. Created
FireTabs Android (#4) and Crestron Panel (#5), linked both to the repository, and
added project-specific issues plus shared repository tasks. Recorded board identities
and preserved them across metadata reconciliation. Public visibility awaits explicit
owner approval after automatic approval review rejected that separate visibility change.

## 2026-10-25 — Issue #5 maintained-kernel candidate/support audit

Inspected pinned Android 17 ACK, recent bengris32 MT8163 work (including an explicit
douglas DTS), its separate upstream submission and LibreEcho 6.1 source references.
Recommended the Android 17 / 6.18 ACK family with an exact LTS-integration candidate,
recording development/release-ref version differences rather than claiming latest
security coverage from the name. Added twelve source-anchored component records.

Captured 78 source/listing records plus three upstream license/notice records with hashes; 16 MT8163 binding-header paths are absent
at the inspected ACK pin. Reproduced a clang preprocessing failure at the first missing
clock header and recorded the actual command/error. Added offline source verification
and rejection tests to CI. No complete kernel checkout/toolchain/AOSP sync or paid
resources; no kernel compilation, image packing, APK execution or physical device actions.

Documented stock mt-boot vs PSCI/power sequencing, memory/boot-envelope concerns,
32-bit EL0/userspace distinctions, graphics/CDD gaps and the next minimal compile/resource
plan. Hardware validation records remain not_run; this closes an audit, not a port.

## 2026-10-25 — Issue #14 DT dependency closure and actual compilation

Resolved 26 real pinned DTS/header inputs (20 donor, six ACK); built dtc 1.8.1 in an
isolated workspace with pinned small bootstrap inputs. The unmodified source failed
on missing thermal constants. Two patches add the real include and correct memory
unit naming/cooling declarations. The patched tree compiles without diagnostics to
a 26,283-byte DTB; fdtget inspection verifies board identity and preserves explicit
512 MiB/PSCI donor assumptions. These are not validated physical hardware facts.

Added a reproducible offline build/inspection command, Linux CI compilation and input/
artifact-integrity tests. No compiled DTB is committed or published. Kernel and device
validation stages stay not_run. A separate schema attempt used incomplete binding
context and is explicitly not passed despite the validator's zero exit code.
The tool-specific SWIG incompatibility was fixed by a compatible pinned dependency,
not by suppressing C errors. No full kernel/AOSP download or physical device action.

## 2026-10-25 — Issue #16 generic ACK compiler baseline

Reconciled closed issue #9's stale status and moved Android root #2 and task #16
into progress on the Android board. Added an isolated Linux CI experiment for
ACK d9318bdb4c34e8b2d997b4f67ced56b120b22b87 with Ubuntu LLVM 18.
The source's scripts/min-tool-version.sh requires LLVM >=15; Kconfig.ext is an
existing intentionally empty upstream placeholder, so no source stub is added.
Uses ARM64 defconfig, not GKI/douglas config. Source fetch shallow/no tags,
3 GiB post-transfer budget, 15 GiB free-disk and 7 GiB RAM gates, 60 minute timeout.
Runner compiler/package versions are recorded, not hermetically pinned. The
experiment logs the resolved config, ELF architecture, artifact sizes/hashes.
No boot image packaging, upload/release or device access. Compilation outcome
must be read from CI before marking any validation gate complete.

First Linux run 40168107152 stopped in host-tool preflight: pahole absent.
No kernel source was fetched. Added Ubuntu dwarves/libelf-dev/libssl-dev host
packages with installed versions logged; apt repositories remain host-dependent.

## 2026-10-25 — Start issue #18 source integration

#16 kernel compile is still pending; it remains open. Started #18's independent
source comparison on kernel/mt8163-clock-port, based on the unmerged #17 branch.
Retrieved 15 pinned source/API files (98,463 decoded bytes). Prepared nine real
clock drivers and eleven binding headers, donor build wiring, and lifecycle/factor
registration corrections documented in the overlay README. Added a clock compile
mode that verifies seven enabled symbols, builds affected objects with W=1 and
then a full generic Image. No clock compilation or hardware pass is yet claimed.
The Linux run uses the previously reported per-run 3 GiB source budget and host
resource gates; no full Android checkout, paid host or device access is involved.

Clock run 40168938776 reached real compilation and failed on missing direct-update
mux macros/ops and flags-selectable composite initializer. Backported the donor's
actual direct-update operations as a minimal ACK patch, leaving existing ACK ops
and allocation implementation intact. Preserved audio composite flags=0 rather
than silently substituting ACK's rate-propagating macro. Rebuild pending.

Generic ACK compile run 40168232549 succeeded: ARM64 4 KiB Image 41,286,144
bytes, vmlinux 440,617,560 bytes; ~16 min 34 sec including fetch/config/build.
Recorded result metadata and recovered the full config from CI logs; its SHA256
matches the compiler-run checksum. No compiler warning/error lines were found.
This generic config does not enable Android Binder/SELinux; it is not the target
Android/douglas config and does not advance that kernel validation record.
PR #17 merged to development. Full matching binding/schema work is now tracked
explicitly in #27; driver/configuration work in #18–#25. Exact transfer and
expanded checkout sizes were not emitted and remain unknown.

Rebuild 40169238323 compiled all nine MT8163 clock objects with W=1 and advanced
into the full kernel build before being superseded by the evidence-recording
commit. Full Image linkage with the overlay is still pending. A git-apply blank
line warning in generated Kconfig wiring was fixed; no warning flag was disabled.
Added per-PR concurrency cancellation to avoid duplicate obsolete builds.

## 2026-10-25 — Clock reference follow-through

Added a bounded source audit of nine provider files and 102 literal DT clock
references. Provider header/ID checks pass; three literal HDMI parents remain
unresolved and documented, not hidden with aliases/dummy clocks. This is not a
schema/register/runtime validation. Heavy kernel experiments now run on PR open,
ready-for-review or explicit workflow_dispatch, rather than on every documentation
push. Source-affecting updates require an explicit rebuild at the new revision;
repository validation continues on every PR update. Run 40169479688's clock source
is unchanged by this audit/documentation/workflow-trigger update.

## 2026-10-25 — Prepare pinctrl/EINT object probe (#19)

While the #18 full kernel compile runs, prepared the next source integration as
a separate stacked change: three unmodified donor files and real Kconfig/Makefile
wiring. ACK common APIs/data fields exist; donor declares 155 pins, six EINT
ports/169 AP interrupts/64 debounce entries. These are not hardware measurements.
A bounded Linux W=1 object-only probe will record actual ELF/hash/config results.
Full Image linkage, legacy routing comparison and schema/runtime tests remain
required. No pinctrl compilation pass is claimed before CI executes.

Pinctrl reference audit: all 155 donor pin names, literal mux functions and EINT
mappings match the pinned legacy Git object; 15 unique captured modern DT mux
references map to descriptor entries. Original legacy table and hashes retained.
This is a source comparison, not register/schema/electrical validation.

Pinctrl object run 40169973832 passed with W=1 and zero compiler warning/error
lines. ELF64 AArch64 object SHA256 recorded in evidence/pinctrl-port/object-result.json.
Git storage measured 291,136 KiB; source including Git 2,066,692 KiB. Transfer bytes
remain unknown. Source is unchanged by the subsequent audit/evidence/CI additions.
Added both bounded reference audits to ordinary repository CI. #19 remains open:
full Image integration, complete schema/register review and all runtime evidence
are still pending.

Expanded pinctrl audit: drive groups (3), pin-drive entries (119), special pulls
(46) and Schmitt entries (57) match legacy. The donor adds one input-enable entry
for GPIO87/MSDC2_DAT0, 0xcf0 bit 4; retained as an unvalidated donor delta and
recorded explicitly. No register value was changed to force an audit pass.

Added explicit workflow_dispatch mode clocks-pinctrl for full combined Image
integration after the object probe. It applies both pinned overlays, verifies
PINCTRL_MT8163=y and all clock symbols, compiles both directories with W=1 and
links Image/vmlinux. This is still a generic config, not a douglas boot claim.

## 2026-10-25 — Prepare #20 PMIC/power object integration

Prepared a minimal MT8163 wrapper/power-domain patch against actual pinned ACK
files. Wrapper donor differences are MT8163-specific. Power core keeps ACK's
implementation and imports only MT8163 include/match data and bus-protection
masks, excluding unrelated hardware-voter/SMC changes from donor 7.0. Eight-domain
header/binding retain donor licenses. Static wrapper register-offset comparison
against pinned legacy header is recorded; runtime sequencing is unverified.
Added bounded W=1 object probe; compilation result is not yet claimed.

Added a reproducible PMIC wrapper register-offset audit to ordinary CI; 79 shared
named offsets match the pinned legacy header. No initialization transactions or
power transitions are executed. This audit addition leaves probed driver source
unchanged from the initial #30 commit.

Power object run 40170813712 passed: actual wrapper and common power-domain
objects are AArch64 ELF, W=1, zero compiler warning/error lines. Hashes and
measured source/Git storage are recorded in evidence/power-port/object-result.json.
Full Image integration, binding dependencies and runtime power sequencing remain
open on #20. This does not advance any Android/douglas runtime validation gate.
## 2026-10-25 — Begin diagnostic boot-contract investigation (#21)

Captured pinned legacy runtime-memory readers and ACK PSCI implementation.
ACK supports old explicit-ID arm,psci as well as version-probed bindings; the
legacy vendor MTCMOS sequence remains a separate unresolved delta. Both legacy
and donor source DTs say 512 MiB; runtime DRAM/mblock inputs and actual loader
fixups must be resolved rather than guessing a RAM replacement. Recorded reserved
region discrepancies and a staged diagnostic/log/recovery plan. Inspected amonet
source only; no unlock/helper/device operation or image packing performed.
#21 remains open pending actual firmware/memory/loader and recovery evidence.

Clock Image run 40169479688 succeeded at 07:09 UTC, about 36 minutes including
setup/fetch/object/full build, with no compiler warning/error lines. Actual
AArch64 Image is 41,351,680 bytes; SHA256 and vmlinux/config metadata recorded in
evidence/kernel-compile/clock-image-result.json. Clock source is unchanged by
the later audit/documentation update. PR #26 merged to development. Schema #27
and parent resolution #29 remain open; no target boot/runtime gate is promoted.

## 2026-10-25 — Local boot image inspector (#32)

Implemented a regular-file-only, read-only header-v0 layout/hash/partition-fit
inspector supporting #21. Rejects ambiguous formats, malformed pages, oversized
or truncated input; counts unclassified tail bytes. Does not decompress, extract,
pack, access device nodes/USB or claim signatures/bootability. Ten synthetic
boundary/rejection tests added; 31 total tests pass. No real stock image inspected.

## 2026-10-25 — Combined clock/pinctrl Image passed

Run 40170429213 at c61bc28 completed at 07:26 UTC (~38 minutes): full AArch64
Image 41,363,968 bytes, with clock and pinctrl objects compiled under W=1 and
zero compiler warning/error lines. Result/hashes and recovered full config are
in evidence/pinctrl-port; config hash matches CI output. Later branch updates
are evidence/docs/CI/base synchronization, leaving these driver sources intact.
PR #28 refreshed against development for required checks; no policy bypass used.
No douglas boot, Android configuration, schema or hardware pass is claimed.

Added explicit providers workflow mode for the next full Image integration:
clock, pinctrl, PMIC wrapper and eight-domain controller candidates together.
Checks all resolved config symbols, compiles each affected object set with W=1,
then links the full generic Image. Same existing resource gates; no Android or
bootable device package is produced. Results pending until actual CI completion.
## 2026-10-25 — Console/MMC reuse investigation (#22)

Captured exact ACK UART/MMC drivers and schemas (133,433 decoded bytes). Prior
successful Image run 40170429213 actually compiled both built-in drivers;
compiler excerpts and configuration hash are retained. Donor fallbacks and
clock names match driver interfaces, while voltage/timing/DMA and physical log
capture remain unverified. ACK schemas do not list the MT8163 compatibles: an
explicit #27 follow-up, not a driver or hardware validation pass. No new kernel
build was launched to duplicate already-recorded compilation.

## 2026-10-25 — Full ACK binding corpus diagnostic (#27)

Retrieved the exact ACK bindings archive: 3,275,172 bytes, 5,186 YAML files,
SHA256 4d1108f17127afcb03d3f1b45a3721195572c8048078ebe821eb0edb94d1e526.
Added bounded/hash-verified archive recipe and full-context wrapper. Actual run
with dtschema 2026.9 reports 36 validation errors and 61 unmatched-schema entries.
Both upstream tools return zero despite diagnostics; wrapper returns 1 and
passed=false. One upstream Gunyah YAML file fails parsing and is preserved, so
this remains provisional corpus processing, not a complete matched schema pass.
Logs/structured errors expose real PMIC/interrupt-node mismatches and compatible
coverage gaps. No diagnostics suppressed and no hardware test performed.

## 2026-10-25 — Narrow PMIC DT structural fix (#27)

Added a separate candidate renaming three PMIC child nodes to the pinned binding
names, retaining labels/compatibles and all properties. DTB compiles without
diagnostics: 26,275 bytes / 119b6666a3caf217675d5aead3e9b0e0b21287d3e21f9d36e7d047f26698eddf.
Binary comparison confirms identical 880 property values across 186 nodes after
only allowed path substitutions. Full-context validation changes 36->34 errors,
61 unmatched unchanged, zero added diagnostic signatures; still passed=false.
Did not add domain cells to the PMIC shutdown node: reviewed driver provides a
sys-off handler, not genpd. Stored source evidence and retained this diagnostic
for semantic review. Added four comparison rejection tests; 35 total tests pass.

## 2026-10-25 — Full provider Image succeeded (#20)

Run 40173436578 at e4e4468 completed 08:13 UTC (~37 min), with real clock,
pinctrl, PMIC wrapper and power-domain objects built W=1 and full Image linked.
AArch64 Image 41,363,968 bytes / SHA256
8b8db531704f2f895e752ba1e22f1b6920b85426e1768a37730041f695afb39e.
Zero compiler warning/error lines. Config hash equals the retained pinctrl
combined config; provider source changes are real and Image/vmlinux hashes differ.
Result metadata retained. This generic configuration has no appended board DT,
qualified loader/ramdisk contract or hardware/Android runtime validation.

## 2026-10-25 — Prepare user-run read-only stock facts (#37)

Added explicit-serial/wrong-device refusal, fixed metadata command collection,
cmdline allowlisting, binary DT property handling, no serial/stderr persistence,
and enforced pipe/runtime limits. Six fake/host-only tests added; 41 total tests
pass. No real device transport executed. Checked installed SDK adb version only:
36.0.2-14143358 on shared Mac; this host-only command does not query devices.
Documented connection/debugging authorization separately from collector scope.
Actual stock facts remain needed for #21; no boot/test package is ready yet.


## 2026-10-25 — Classify PMIC shutdown schema selection (#27)

Traced the missing domain-cells diagnostic to the pinned generic power-domain
schema's node-name selector. The MFD binding itself calls the sys-off child
power-controller but does not require cells. Preserved the generic schema with
source hash and documented the selection overlap, MFD-provided memory resource,
and sys-off driver semantics. No permissive schema or DT change; counts remain
34 errors/61 unmatched. Actual stock-data collection still awaits the user's
computer choice; no tablet transport or settings change performed.

## 2026-10-25 — Sysirq node-name structural fix (#27)

Added isolated sysirq-node-name candidate on the PMIC candidate, preserving all
interrupt properties and compatibles. Clean DTC result 26,279 bytes / SHA256
78fd34cbe0c129da23dd2e296be0db9180e7d8b464e719b59304f09d01456bea.
Actual binary comparison retains 880 values across 186 nodes, permitting only
four reviewed path renames. Schema run removes one naming diagnostic with none
added after path normalization: 33 errors/61 unmatched remain, passed=false;
upstream YAML parse issue remains. Added CI compilation/property comparison and
rejection tests; 44 local tests pass. No physical device access or firmware pack.

## 2026-10-25 — Minimal diagnostic userspace experiment (#41)

Created separate freestanding AArch64 /init and deterministic newc/gzip builder.
Only console output, bounded kernel metadata reads, read-only virtual mounts and
controlled idle; no block nodes/storage mounts or reboot interface. Local Apple
Clang cross-object compile passes strict warnings; no local Linux linker present,
so full ELF/archive compilation is delegated to the existing Linux CI toolchain.
47 unit tests pass, including ELF rejection and actual archive metadata/content
parsing. Build is not a firmware package or a boot/runtime result. No tablet
transport or physical changes. Stock loader/memory/recovery gates remain #21.

Linux CI run 40181473575 at cb82cb8 passed the static ELF/archive build with
Ubuntu Clang 18.1.3; ELF checks confirm AArch64 ET_EXEC with no interpreter or
dynamic segment. Gzip/newc archive 1,248 bytes, SHA256
8d68234297e9ed50e025cb321d066b2d4ff8a4a09c57a654e09d9467c10e6ff4.
Exact command/compiler/source and artifact hashes retained in
 evidence/diagnostic-initramfs/compile-result.json. No runtime execution occurred.

## 2026-10-25 — Narrow local UART binding proposal (#27/#22)

Added opt-in mt8163-uart-proposed binding profile, preserving the original ACK
profile. Proposal adds only the exact MT8163 first compatible with required
MT6577 fallback, backed by pinned donor DT and matching ACK driver source.
Original schema/patch/proposed schema hashes checked before applying in a fresh
corpus extraction. Meta-validation clean; full-context diagnostic delta removes
four compatible errors and four unmatched entries without added signatures:
29 errors/57 unmatched remain, upstream YAML parse issue remains, passed=false.
49 tests pass, including real isolated patch application and rejection of changed
original schema input. No compatible deletion, permissive schema or hardware claim.

## 2026-10-25 — Restricted diagnostic kernel compile setup (#44)

Prepared separate diagnostic fragment and fail-closed resolved-config check.
Requires implemented providers/UART/initramfs, disables block/storage/network,
USB/display/audio/watchdog and power-policy subsystems. Adds deterministic gzip
Image size/hash reporting without packing firmware. Provider workflow defaults
to this integration mode; resource gate unchanged and reported before starting.
53 local tests pass including rejection of modular storage and missing console.
No configuration/compile success claimed until actual Linux CI resolves/builds
it; stock memory/loader/recovery/logging remain #21, no tablet access occurred.


## 2026-10-25 — Diagnose hidden BLOCK configuration prompt (#44)

Actual run 40183576290 at 14d1b21 failed policy check before Image compilation:
BLOCK resolved y. Pinned block/Kconfig makes its bool prompt conditional on
EXPERT, with default y; generic defconfig has EXPERT=n. Captured source/hash and
failure evidence. Added EXPERT=y, retained strict storage-disabled check, improved
all-mismatch diagnostics and rejected-config logging. Rebuild required; no
kernel/boot result claimed, no tablet access or firmware packing occurred.


## 2026-10-25 — Remove ACPI idle-policy selector (#44)

Second actual run 40184459476 resolves storage disabled but rejects CPU_IDLE=y
before Image compilation. Captured the rejected config from CI stdout and pinned
Kconfig source proving ACPI_PROCESSOR -> ACPI_PROCESSOR_IDLE -> CPU_IDLE. Fragment
now disables ACPI/processor idle policy for the donor-DT experiment; the strict
CPU_IDLE=n gate remains. No ARM_PSCI_FW/DT/stock-loader changes. Corrected build
still pending; no physical tablet access, firmware packing or runtime claim.


## 2026-10-25 — Restricted diagnostic Image compile succeeded (#44)

Actual run 40185547611 at 3bf1010f3f007bd3fd202da30b3483ca12933531 passed
in 23m16s with zero compiler warning/error lines. Resolved strict policy passes;
real clock/pinctrl/power objects W=1 and full Image/vmlinux compiled. Retained
complete resolved config reconstructed from CI and matched original SHA256
f5da34605d2ebc5f279269e59d56027acfefbfb346819d945c7dd7a6c3209eed.
Image 28,576,256 bytes; Image.gz 9,187,928 bytes / SHA256
a6ecd7444c9ffc8f47c4954902b23e15fd1f861b924ae9a082157652dc2ab1c1.
Report/log checksum and policy evidence retained. No DT/ramdisk integration,
firmware packing or published test package; stock #21 prerequisites and #27
schema validation remain. No tablet access or runtime result claimed.

## 2026-10-25 — Bounded stock OTA model/boot-image inspection (#46/#21)

Found discovery index HD8/HD10 5.7.1.0 links swapped; verified actual package
identity from CRC-checked properties, rejecting suez/KFSUWI and selecting
candidate douglas/KFDOWI/MT8163 build659664620. Marketing-version/installed-build
match remains unverified (embedded Fire OS property says5.3.7.3). Initial two
metadata probes used204800 bytes; reusable opt-in extractor used8612864 bytes,
within20MiB response-body budget, rather than whole907705758-byte OTA. Boot.img
8689664 bytes / SHA2568982fa50193acc764be69ee51027ee92e83614cee4b8235b07439d1f9e2db363.
Existing inspector confirms2KiB pages/header fields; bounded gzip-prefix check
finds AArch64 magic behind512-byte kernel prefix. Unclassified2KiB trailer and
all signatures remain unverified. Report/ranges/hashes retained, binaries ignored.
59 tests pass with synthetic archives/fake transport. No archive execution,
firmware packing, tablet access or physical change; no test package ready.

## 2026-10-25 — Actual candidate DTB memory/PSCI evidence (#21)

Added bounded local wrapped-gzip/concatenated-DTB inspector. Actual candidate
kernel gzip decompression16584856 bytes; suffix is exactly two DTBs pre_evt/hvt
(82277/82641 bytes), hashes and selected facts retained. Both corroborate static
512MiB memory, legacy explicit-ID PSCI and CPU0 mt-boot, plus all legacy firmware
and log reservations omitted from newer donor. Header reservation maps empty;
body reservations and dynamic CONSYS remain authoritative static declarations,
not runtime measurements. Collector now reads individual DT version property;
only fake transport tests ran. 63 tests pass, including gzip cap/truncation and
invalid wrapper/DT suffix rejection. No downloads, firmware changes, packing or
device access; #21 runtime/loader/log/recovery gates remain open.

## 2026-10-25 — Prepare generic ARM64 VM runtime test (#49)

Added bounded QEMU virt8.2/Cortex-A53/one-CPU/512MiB diagnostic userspace runner,
using existing restricted kernel/initramfs inputs. No disks/network/host shares,
software TCG,120s/2MiB console caps, required init/mount/metadata/idle markers and
5s continued execution; reject panic/read errors/early exit. Dependency installer
requires disposable Linux GitHub runner and <=200MiB APT package archive plan
before install; package versions logged. Existing ACK build resources unchanged.
68 local tests pass, including incomplete/panic/error console rejection and
package gate. Actual VM execution still pending; no douglas boot/hardware/Android
runtime claim. No tablet access, firmware packing or paid provisioning.

## 2026-10-25 — Generic diagnostic execution passed (#49)

Reviewed successful CI 40193403656 at project 2fc0da6d65371783c13bfd800b3a1630f7fa3511,
pinned ACK d9318bdb4c34e8b2d997b4f67ced56b120b22b87. QEMU virt8.2/Cortex-A53
ran restricted kernel plus unchanged diagnostic initramfs: proc/sysfs mounted,
four metadata reads completed, idle survived five seconds. Exact hashes/command,
ARM64 header and CI-log hash retained in evidence/qemu-diagnostic. All routine
checks also passed; 68 tests. Generic execution only; #21 physical loader/memory,
recovery and log qualification remain open. No tablet access or firmware packing.

## 2026-10-25 — Resolve conditional Image placement mismatch (#21)

Compared actual executed Image header with model-verified candidate boot header
and official ARM64 boot ABI. New text_offset=0 requires 2MiB-aligned entry; old
0x40080000 field is misaligned if honored unchanged. Recorded arithmetic and
pinned amonet LK source hashes; payload is not complete loader evidence and
MISC transitions can write persistently. No chosen addresses, firmware assembly,
helpers executed or tablet access. Actual loader relocation remains unresolved.

## 2026-10-25 — Include loader version identifiers in stock facts (#21)

The read-only collector omitted three preloader/LK/TEE version properties used
by pinned amonet step-1.sh. Added only those fixed names and internal Fire OS
version for later installed/candidate matching; serial remains excluded. Fake
transport verifies preservation and no serial query. No real ADB/device access
or helper execution. Property values alone do not authenticate loader binaries.

## 2026-10-25 — Audit diagnostic RAM logging gap (#21/#22)

Resolved config has PSTORE_RAM=m with console/pmsg disabled, while minimal init
cannot load modules. QEMU success is live PL011 output, not retained RAM logs.
Pinned legacy source has a custom multi-stage buffer and optional eMMC write
path; no wholesale logging backport or reservation reuse is justified yet.
Recorded exact hashes and requirements for an isolated backend/retention/reader
or qualified UART path. No config/device changes or helper execution.

## 2026-10-25 — Reject CRLF diagnostic error lines (#49 follow-up)

Found VM verdict parser matched UNAVAILABLE/READ_ERROR only between LF bytes;
serial CRLF translation could bypass that fatal override in an otherwise
complete transcript. Normalize CRLF only for verdict parsing, preserving raw
console bytes and hashes. Regression exercises both errors with LF and CRLF.
No kernel/initramfs/config changes, new heavy build or tablet access.

## 2026-10-25 — Reproducible offline Image placement audit (#21)

Added report-based auditor with cross-report stock hash checks, exact raw/decoded
new header consistency, bounded local JSON input and uint64 arithmetic guards.
Actual old text_offset=0x80000 aligns at the old address; new offset=0 does not.
Retained exact result plus input/auditor hashes. No replacement address selected,
loader behavior authenticated or firmware packed. All 72 tests pass.

## 2026-10-25 — Harden legacy ADB metadata reads (#21/#22)

Classify known remote shell error prefixes as unavailable even when old ADB
returns host status0; do not retain error text. Traverse the device-tree symlink
with a trailing slash and add proc/version for systems without uname. Fake
transport covers status-zero permission/missing-command failures and privacy
filtering. 73 tests pass. Device-specific evidence remains private locally.

## 2026-10-25 — Publish owner-approved sanitized runtime evidence (#21)

Owner explicitly approved sanitized publication. Selected firmware/build/loader
identifiers, runtime DT memory properties and provenance hashes reviewed; no
hardware serial, household data, raw logs or full local report published. Actual
runtime hvt DT reports two banks totaling1430MiB; installed build identity agrees
with inspected OTA candidate, not binary/signature equivalence. PL7/LK3/TEE262
exceed pinned helper6/2/259 maximums. No helper/device operation performed here.

## 2026-10-25 — Decode actual runtime memory handoff (#58)

Implemented strict offline decoder for big-endian DT reg and native little-endian
ARM64 vendor structs; pinned source and compiler layout retained. Actual ranks
total1536MiB, usable reg/mblocks agree at1430MiB, excluding106MiB at top. No
ownership inference or DT enlargement. Five malformed/actual-data test groups
added, all78 tests pass. Next: source-audit excluded/reserved intervals under#21.

## 2026-10-25 — Reservation interval/source audit (#60)

Added reproducible static-vs-runtime inventory and boundary tests. Four fixed
regions total5.3125MiB inside usable banks and have zero overlap with106MiB top
exclusion; dynamic CONSYS location unknown. Pinned memory/ATF/display consumers
identify missing tee/lca/framebuffer runtime fields; accounting equality check
is disabled. No ownership inferred. Exact residual remains#21; next independent
task#27 upstream schema parse/selector failures. All81 tests pass. No device
queries, firmware assembly, helper execution, downloads or paid resources.

## 2026-10-25 — Opt-in corpus YAML lexical repair (#62)

Three Gunyah indentation tabs replaced only in hash-locked opt-in extracted
corpus. Original preserved; no semantic relaxation/suppression. Actual full
context still29errors/57unmatched, passed=false/exit1. YAML parser issue removed,
but schema now explicitly ignored for invalid compatible shape; separate meta
errors retained. All82 tests pass. Next#27 semantic/schema-selector repair.

## 2026-10-25 — Exact PMIC sys-off/domain selection fix (#64)

Opt-in hash-locked generic-domain selector excludes only MT6323 sys-off compatible;
all original domain constraints and MFD binding unchanged. Actual meta-validation
clean; YAML/jsonschema controls preserve missing-cells rejection for real domains
and MFD wrong-compatible/unknown-property rejection. Full-context delta removes
one false domain-cells requirement, adds none:28errors/57unmatched remain.83
unit tests pass. Next#27 remaining schema failures; no device/hardware claims.

## 2026-10-25 — MT8163 sysirq binding coverage (#66)

Pinned ACK/legacy fallback driver evidence retained. Opt-in enum adds MT8163
first compatible requiring unchanged MT6577 fallback; no other constraints
changed. Meta clean; actual processed tuple negative controls reject wrong/
missing/extra fallback. Full delta removes2diagnostics/adds0, now27errors plus
56unmatched, overallfailed.84 tests pass. Next#27 timer or RDMA selector work.

## 2026-10-25 — MT8163 timer binding coverage (#68)

Source-backed exact first-compatible enum proposal requires existing MT6577 GPT
fallback. Pinned ACK/legacy source hashes retained. Meta clean, processed tuple
negative controls reject invalid fallbacks. Actual full delta removes2/adds0:
26errors/55unmatched remain, overallfailed.85 tests pass. Next#27 display-RDMA
node name/generic DMA selector conflict. No tablet access or firmware assembly.

## 2026-10-25 — Display RDMA node-name candidate (#70)

Canonical rdma@ name prevents generic DMA-provider misselection. Compiled alias
path rewrite explicitly checked; other879 property bytes across186nodes unchanged
after reviewed path substitutions. Clean DTC26259B hashc1824152...; CI fourth
variant added. Full delta removes1/adds0:25errors/55unmatched remain.88 tests
pass. No cells invented, schema relaxed, hardware tested or device accessed.
Next#27 RDMA compatible coverage/remaining boot-relevant gaps.

## 2026-10-25 — Storage/UART-DMA compatible coverage (#72)

Pinned ACK fallback evidence retained; two strict opt-in compatible proposals
keep all other constraints. Meta clean; processed controls reject invalid pairs
and preserve existing SoCs. Full delta removes8/adds0:21errors/51unmatched,
overallfailed.89 tests pass. No device/driver/DT/firmware or hardware claim.
Next#27 remaining peripheral fallback or display binding gaps.

## 2026-10-25 — Strict peripheral fallback coverage (#74)

Four opt-in compatible profiles preserve all other constraints; pinned fallback
drivers/source hashes retained. Meta clean, processed controls pass. Actual full
delta removes12/adds0:15errors/45unmatched remain, overallfailed.90 tests pass.
No bus/ADC/RNG hardware/security qualification. Next#21 cached loader/recovery
alternative audit to advance the physical diagnostic boot blocker.

## 2026-10-25 — Loader/recovery alternatives audit (#76)

Source/hash/line inventory distinguishes stock recovery, handshake, old software
unlock, BootROM chain, newer preloader exploit and post-unlock custom loaders.
Newer fork has explicit douglas target but requires older vulnerable preloader;
old minimal chain still modifies GPT/RPMB/preloader/boot. No qualified safe route
yet. Offline assessor and3tests added;93tests pass. Next bounded OTA preloader/LK
static inspection planned383684compressed bytes plus metadata, no fullOTA.
No helper/payload compiled/executed, reference modified or tablet accessed.

## 2026-10-25 — Bounded build-matched loader inspection (#78)

Explicit loader whitelist/model/build gate,2MiB transport body cap,1MiB entries
and capped static marker/header reports added. Actual452322B fetched; preloader
139352B/LK485552B hashes retained, binaries ignored/notexecuted. Heuristic marker
absent; exploitability remains unknown. LK wrapper485040B payload equals file
minus512.98 tests pass. Next#21 static entry/format audit, no tablet operations.

## 2026-10-25 — Exact loader container/address audit (#80)

GFH declaration gives preloader code view0x201000..0x222c34; LK prefix uses default
address sentinel, so old4bd00000base is unverified. Strict hash/bounds parser and
source-based hypothetical patch windows retained with compatibility=false. Old
helper donor binaries absent in pinned git.102 tests pass. Next#21 stock LK
control-flow analysis using existing LLVM, no new dependency or device operation.

## 2026-10-25 — Actual LK K64/secure-monitor instruction trace (#82)

Startup instructions substantiate linked4bd00000base. Checked Thumb chain passes
entry-slot/current-r5/0/1 through K64-labelled wrapper to ARM SMC#0 service82000200.
Exact offsets/bytes, PC-relative references, disassembly and hashes retained.
r5 lineage, upstream header/decompression producer and monitor behavior remain
unverified. Non-loadable static-analysis object only;106 tests pass. Next#21
trace entry-slot producer. No code/firmware execution, new download or tablet IO.

## 2026-10-25 — Header entry/decompression producer (#84)

Exact cached LK static trace joins three GOT references to header-pointer global
4bd841b0. Selected header+0xc supplies entry and gzip output; K64 checks512KiB
alignment and loops on failure; decompression call supplies28MiB capacity. Modern
diagnostic image_size equals that capacity (no margin, not success/failure proof).
Selected bytes/disassembly/hashes and mutation negative controls retained. No
firmware execution, downloads or tablet IO. Next: staging/input length and DT
handling before considering any test package; recovery remains unqualified.

## 2026-10-25 — Selected LK compressed input/DT sizing (#86)

Retained exact LK instruction windows connect staging45000000, prefix-present
read adjustment-512, backward FDT scan/suffix rounding and separate inflate
input/output lengths. Conditional stock DT-match arithmetic retained without
claiming actual selection. Stock gzip output16584856 leaves12775272 of28MiB
capacity. Clarified image_size is runtime memory requirement, not decoded file
length; modern actual byte length remains unmeasured here. No device/firmware
execution/download. Next: measure cached modern Image output versus reserved
runtime footprint; recovery and physical boot remain unqualified.

## 2026-10-25 — Exact keypad fallback schema coverage (#90)

While PR89's generic compile runs, independently validated cached donor keypad
fallback against pinned ACK driver/schema. Added opt-in single-enum binding
proposal with hashes and six processed-schema positive/negative controls.
Full-corpus diagnostic count60→58 (14validation/44unmatched), zero new diagnostics;
overall still fails, as expected.113 offline tests pass on this branch (PR89
measurement tests remain on that separate pending branch). No hardware DT/node
status change, device access or hardware claims. Parent27 remains open; next
independent binding candidate is efuse fallback coverage after source inspection.
## 2026-10-25 — Actual modern Image length evidence (#88)

Recovered original generic run40193403656 size/hash lines from1.47MB CI log:
Image28576256bytes, gzip9187924bytes, rawSHA08df8a73166bf5bd3a0fefdd9394d8f5d54b2822255e728c2c3873f2e1c56909.
Raw file fits selected28MiB output capacity with783872bytes margin; declared
runtime image_size is separately28MiB. Historical binaries remain absent, so no
new historical gzip round trip claimed. Added bounded single-member measurement
and exact Image comparison to existing diagnostic build/VM reports;115 offline
tests pass. Integration CI uses existing reported kernel resource gate. No tablet
IO, firmware assembly or physical destination. Recovery/entry alignment and
secure-monitor qualification still block a user test package.

## 2026-10-25 — Measurement integration validated; ordered PR merges

PR89 headb1f3c1fc2652f249db744f8997021ea7d7649fdb passed all required checks and
actual compile/QEMU run40250576526 (24m2s CI job). New rawSHA16c9e5e6947231070888dcba5467b79df20ef6eee060edd86b36ec6fd336bcb3,
28576256bytes; gzip9187928bytes, round trip verified; capacity margin783872bytes.
QEMU markers/read-only proc/sysfs reads and5s idle passed in5.94s. Retained exact
report plus full1.47MB log hash in evidence/image-measurements/validated-runtime-result.json.
Build hash differs from historical output; no bit-identical rebuild claim.
PR89 merged; issue88 closed. Merged development into keypad PR91, explicitly
preserving both appended WORKLOG sections, then added this validation evidence.
Tablet boot/hardware/app stages remain untested. Next merge91 after refreshed
required checks; independent efuse scope92 remains queued.

## 2026-10-25 — Generic efuse compatible and calibration constraints (#92)

Audited cached pinned ACK generic efuse driver against donor calibration cell.
Generic match has no MT8186 speedbin postprocessing; legacy fixed cells enabled.
Added opt-in exact tuple proposal preserving all other constraints. Nine actual
processed-schema controls pass; full-corpus diagnostics58→56 (13validation and
43unmatched), zero additions. Overall validation remains failed/exit1;117 offline
tests pass. Source/patch/schema hashes and complete delta retained. No calibration
correctness, efuse IO or hardware support claimed. Parent27 remains open. Next:
return to21's secure-monitor/CPU handoff source contract before more display work.

## 2026-10-25 — CPU startup / monitor source contract (#94)

Compared cached legacy mt-boot/PSCI and ACK CPU ops plus stock/donor DT contracts.
Legacy wrapper adds host-side MTCMOS power sequencing after PSCI; ACK DT table
has no mt-boot method. ACK still supports explicit legacy PSCI IDs, so old DT
format alone is not a hard blocker. Donor v0.2 ARM64 CPU_ON C4000003 differs from
stock explicit84000003; monitor acceptance remains unknown. LK primary82000200
is separate. Source hashes/line anchors and mutation controls retained. Legacy
reference not binary-matched to stock. Proposed primary-only diagnostic limit
requires boot-CPU path audit; no device/SMC/firmware execution. Next bounded task:
trace boot-CPU versus secondary setup and maxcpus=1 effects before choosing DT
CPU changes. Physical recovery/logging and hardware/runtime gates remain open.

## 2026-10-25 — Isolated primary-only DT/source experiment (#96)

Traced pinned setup_arch early parsing→PSCI discovery→boot-CPU ops/enumeration.
maxcpus=1 alone still probes PSCI and prepares secondaries. Added opt-in compiled
DT-only experiment: PSCI node disabled, chosen nr_cpus=1 maxcpus=0; preserves all
186nodes/880original properties and default experiments. Compiles cleanly to
26324bytes/SHAef23af15f7136613a98b450f3d1db7c860f581024d194e88e2ef8c3116f2eb43.
Source/hash guards and full semantic comparison/negative controls retained.
Loader preservation, boot MPIDR, other firmware paths, donor RAM and physical
boot remain unverified. No firmware packing/device/SMC/helper execution. Next:
trace actual LK bootargs rewriting before treating the limits as effective.

## 2026-10-25 — Actual LK chosen/bootargs replacement trace (#98)

Exact cached LK static trace connects file-backed command buffer4bd74cb8 and
header+40 format input to selected FDT bootargs write. Writer usesstrlen+1,
resizes existing property, sets new length and copies new buffer; DT bootargs
alone are not a preservation guarantee. Initial static150-byte buffer lacks
diagnostic limits; runtime mutations/all boot modes remain unqualified. Retained
instruction/call/string/hash evidence plus126 passing offline tests and mutation/
argument negative controls. No PSCI-status preservation or physical boot claim,
firmware/helper execution or tablet IO. Next: sanitized effective command-line/
CPU-count diagnostic reporting, keeping loader/recovery/logging gates open.

## 2026-10-25 — GCE fallback binding coverage (#102)

While PR101 actual init/kernel VM validation runs, audited pinned GCE fallback
pdata and cached legacy thread-count/security definitions. Added opt-in exact
MT8163/MT8173 tuple coverage preserving other schema constraints. Seven actual
processed-schema controls pass; full-corpus diagnostics56→54 (12validation and
42unmatched), zero additions; overall still fails/exit1.127 offline tests pass
on this independent branch; PR101's parser/runtime changes remain separate.
Source hashes/delta retained. No CMDQ execution, DT/hardware enablement or device
access. Merge after PR101 to avoid invalidating its expensive compile head, then
reconcile appended WORKLOG and rerun inexpensive required checks.
## 2026-10-25 — Sanitized CPU-contract init reporting (#100, runtime pending)

Implemented bounded private cmdline/CPU-online/live-DT status reads in minimal
init with allowlisted verdict-only output. Added shared C parsers exercised by
native host tests and distinct generic-observer/primary-contract evidence checks.
130offline tests and local AArch64 object compile with Werror pass. Builder
records header/source hashes; linked initramfs and generic VM integration remain
pending existing gated CI. No raw private argument emission, tablet/device access
or firmware assembly. Do not close100 until actual init/runtime integration is
validated. Recovery, usable physical logging and loader contract remain open.

## 2026-10-25 — Actual sanitized CPU init integration passed

PR101 head84c0392393eacf9dfef2b1d4e6b17d6bcc9c017b passed compile/initramfs/QEMU
run40259254917 in23m55s. Actual verdicts: both limits missing (expected generic
command line), one online CPU/CPU0 alone, PSCI status unavailable. Generic
observation passes; primary-only contract remains false. Retained exact runtime
report/artifact/log hashes in evidence/sanitized-cpu-report/generic-runtime-result.json.
PR101 merged/100 closed. Reconciled GCE PR103 against development preserving both
WORKLOG sections. Recovery work104 has started: declared PL7 mapping places an
old USB-descriptor patch address in a referenced string-literal pool and another
old entry in an interior block; exact trace/evidence is being prepared separately.
No tablet/helper/firmware execution or hardware qualification.

## 2026-10-25 — Recoverable loading priority / exact PL7 code (#104)

Prioritized recovery over more schema cleanup. Exact cached PL7/GFH mapping shows
old USB patch site217420 is a referenced string-literal word; old DA/TEE entry
sites lie in selected interior blocks. ARB entry201934 corroborated by diagnostic
strings and conditional caller20a7ce, not complete policy/compatibility. Retained
bounded static bytes/disassembly/hash/call controls;134 offline tests pass.
No replacement patches/payloads, helper/firmware execution, tablet IO or downgrade.
Compatible load/restore route remains unqualified. Next recovery task: qualify
older reference preloader/restore-material provenance and precise entry/restore
prerequisites rather than reuse stale offsets or infer exploitability from a
marker.100/102 completed with actual generic VM evidence and required checks;
physical boot/recovery/hardware/app gates remain open.

## 2026-10-25 — Reference material located, recovery not qualified (#106)

Located pinned mirror22.3MB archive; fetched only519984response bytes using strict
ranges. Older preloader138924B/SHAcefc66528a56626e65a553b7f97e0521e7939c195ce72794e7c4e14eab04619d
and LK485988B hashes retained; binaries ignored. Original author/Amazon-build
identity unverified (XDA403). Minimal mode still changes persistent GPT/boot0/
RPMB/boot/recovery/MISC; complete escrow/restore not established. Added bounded
probe and hash-only comparison;138offline tests pass. Approval review rejected
publication of copied helper code; removed it and raw code windows from public
changes, keeping only nonoperational summaries/metadata/hashes.106 remains open;
next official older OTA/original attachment match plus entry/restore validation.
No tablet/helper/firmware execution or physical changes.

## 2026-10-25 — Official-hosted older component provenance matched (#106)

Initial659658220 Amazon URL denied HEAD; retained status observations, no body.
Located other pinned index records and probed actual Amazon-hosted build metadata
before capped loader extraction.636558520 preloader+LK match older mirror hashes;
657611720 retains older preloader/current LK;659662320 has same PL/LK as current.
Read1356647body bytes total across three probes, no full~900MB OTA. Public reports
contain properties/metadata/digests/range hashes only, no helper/firmware code.
Added offline host/model/resource/digest verifier;141tests pass. Component source
provenance resolved, not signatures/antirollback/helper authenticity or restore.
106 remains open; next separate safe entry/backup escrow from persistent writes.
No tablet/helper/firmware execution, downgrade, flashing or device changes.

## 2026-10-25 — Recovery entry/escrow source audit (#106)

Merged PR108 after exact-head required checks passed (reran stale validation
job); development base03da5d38e477fc79ca7506512bc3d3dcb7191b34. Added AST-only
source audit and two regression tests:143 offline tests pass. Old minimal route
is not backup-first; conditional early writes and dropped size bound recorded.
Located pinned MTKClient MT8163/douglas configuration and Mac documentation as
a possible independent read-back alternative. Read APIs alone do not qualify
bootstrap/indirect persistence behavior; duplicate GPT filenames reuse data.
Retained source hashes/line summaries only, with helpers ignored locally.
No payload/dependency install, helper execution, tablet access or firmware changes.
106 remains open: next audit legacy DA/bootstrap side effects and minimal Mac
CLI requirements, then independent escrow/restore/log qualification.

## 2026-10-25 — Legacy backup selection/bootstrap audit (#106)

PR109 merged only after all four exact-head required checks passed; new base
102cb12 (full revision available in Git). Read111117B across six pinned source
files, no payloads or installs. Added source-hash-checked AST method closure and
regression tests:145 offline tests pass. Legacy upload/read closures do not
reach named write/format methods, but external protocol/agents remain unaudited.
Found a concrete escrow failure path: readflash ignores failed partition-select
acknowledgement and can proceed against an unconfirmed region. Dynamic DA mode
can override the configured legacy choice. FUSE imports have guarded fallbacks;
complete minimal Mac CLI import closure remains unverified. No tablet access.
106 stays open. Next offline deliverable: fail-closed escrow geometry/hash/GPT
validation with synthetic fixtures; safe entry, restoration and usable physical
boot-log capture still unqualified.

## 2026-10-26 — Offline escrow verifier (#106)

Merged PR110 exact head02df4b85ab6e8c5f0d69147b535448ef3a79443d after all four
required checks passed; basea8940c6. Implemented regular-file-only three-region
length/SHA verification plus GPT headers/arrays from actual primary/final-LBA
locations, CRCs, reciprocal geometry, partition bounds/overlap and consistency.
Caps metadata memory; no device protocols or restore actions. Seven synthetic
tests bring suite to152 passing, repository guard/diff check pass. Qualification
flags stay false even on valid files: collection region identity, restoration
and physical-test readiness are not established by checksums. UEFI2.11chapter5
is the format reference. No new downloads, installs or tablet access.
Next: define precise restore/boot-log evidence checklist and resolve safe entry/
agent provenance; do not close106 or any physical gate on synthetic tests.

## 2026-10-26 — Restore and first-log acceptance plan (#106/#21/#22)

Merged PR111 exact c6417a293f3f8483bc3224b1294f7696af63758b after all required
checks passed. Reconciled stale sequence inventory: older Amazon component byte
identity is resolved; signature/rollback/restore are not. Added modern read-back
candidate and offline verifier limits. Defined ordered entry/agent, acknowledged
escrow, restore reachability, security-state, Mac/re-entry and log gates with
precise missing evidence for UART, retained RAM and USB logging. No operation
commands, package readiness or runtime claims. Next source task is DA selection/
agent provenance, then source UART contract; no tablet access or new downloads.

## 2026-10-26 — Candidate download-agent selection/provenance (#106)

Merged PR112 exact eac4a371a4df30ab992403961cf9ee225abf1c02 after required checks
passed; base2f5b708. Inspected9558B pinned source +308770B Git-tree metadata only.
Separated600B security bootstrap from independently selected storage DA. Default
selector scans six filename candidates51,627,415B total; no binaries downloaded.
Found subcode deduplication self-comparison at daconfig:196 and no setup subcode
check; actual device failure/selected record unverified. Recorded metadata/SHA1
versus signature/SHA256 distinctions. AST-only tests bring suite to154 passing.
Next bounded metadata/header inspection for DA records if range-supported, or
independent cached UART contract; no helper execution/tablet access/dependencies.
Recovery/restore/logging gates stay open.

## 2026-10-26 — Exact candidate DA record metadata (#106)

Merged PR113 exact6fd9fa468bf54fe62ad39becf2fef0872b4b6486 after all required
checks passed; base5f82131. HTTP206-only bounded probe read36,080B container
headers/tables plus108B initial support check; no stage code/full pack. Two
MT8163 records found: V5index40 and mt6590index19, bothHW0xCA00/SW0/subcode0.
V5 expected first eligible default under audited version/order assumptions,
not runtime-selected/qualified. Recorded stage lengths/signature-tail sizes and
range hashes, not target addresses. Four new tests including ignored-range/
pre-request budget failures:158 tests pass. Next bounded stage-identity probe
~320KiB, static/hash only; actual entry/restore/logging remain open.

## 2026-10-26 — Original V5 stage identities (#106)

Merged PR114 exact1c344dc397dc7fe597066d1435e94bc3294f5b66 after required checks
passed; base2f3983c. Read320224B exact stage ranges +22383B extension source.
Original stage/code/signature-tail SHA256s retained, binary/helper bytes ignored.
No signature validation, execution, emulation or patches. AST review confirms
conditional extension/hash transformation before upload, so original digests
do not establish future uploaded identity. Added pinned bounded-cache repro
verifier and two synthetic tests:160 tests pass. Next cached UART source/driver
contract; entry/agent effects/restore and physical logging remain unqualified.

## 2026-10-26 — UART first-log source/DT/config contract (#106/#22)

Merged PR115 exact3709268020f9a36a3eb35491707b6f259373ee1d after required checks
passed; base4d83c96. Audited reviewed primary-onlyDTB against cached driver/config:
enabledUART0/11002000/stdout921600n8/fallback and built-in drivers present, but
no explicit earlycon/console in DT args and built-inCMDLINE empty. Actual loader
argument delivery remains unverified. Early driver setup does not establish
clock/pin initialization; normal probe has separate provider requirements.
Added source/DT audit +two tests:162 passing, no DT mutation/download/device IO.
Next authoritative douglas pad/electrical evidence search, then safe entry/log
transport qualification. No physical wiring action requested.

## 2026-10-26 — UART actual pinmux and physical evidence boundary (#106/#22)

Merged PR116 exact1be8f8bf2c8c8cf0449794d81305f3bc70572d85 after required checks
passed; base9c6c620. Followed actual reviewedDT phandle toGPIO79/80 function1,
consistent with cached UART0RX/TX source. Added ambiguous-reference rejection/
test and source hashes:163 offline tests pass. SoC indices are not PCB pads.
Bounded publicsearch found no established douglas pad/voltage map; XDA403 and
pmOS redirect inaccessible, not proof evidence absent. No physical request.
UART wiring gate now precisely documented; move to independent loader/earlycon
request-delivery work rather than repeating the search. No tablet IO/DT mutation.

## 2026-10-26 — Kernel-side diagnostic argument-delivery experiment (#106/#21)

Merged PR117 exact62522656df4963e9ae4f369364f04c54ce94d316 after required checks
passed; basefce7371. Read49,255B pinned ACK source only. FORCE source path can
bypass LK bootargs replacement if chosen exists; no-chosen path and discarded
firmware args remain constraints. Added opt-in fragment outside default compile
paths and strict resolved-config checker/two tests:165 tests pass. Rechecked
exactLK hash and allowlisted initialconsole/earlycon tokens: staticLK already
requests UART0 earlycon, not runtime proof. No compile/firmware/tablet execution.
Next audit firmware arguments discarded by FORCE before any gated build.

## 2026-10-26 — Forced argument discard constraint inventory (#106/#21)

Merged PR118 exact430133d624dc67d1bc92566573d715e4071356b3 after required checks
passed; base0c3e265. Hash-checked stockbootheader/LKinitial/twoappendedDTs expose
seven static keys, with no actual runtime cmdline available. Classified replacement
versus unresolved initrd/vmalloc/bootopt/platform effects; source ordering does
not validate memory handoff. Device FORCE profile remains uncompiled/unqualified.
Added key-only bounded audit/two tests:167 tests pass; no downloads/tablet IO.
Next actual generic-only FORCE experiment using PL011 and contradictory incoming
arguments, with existing resource gate (~0.3GiB/15GiB/7GiB/60min); no job started.

## 2026-10-26 — Independent Mac CLI source dependency inventory (#106)

PR121 genericcompile40279916842 remains running; did not alter its head or poll
unchanged CI as the only work. On independent development-base branch audited
67 pinned source modules,999718new source bytes under192KiB/file/2MiBtotal;
Gitblob identities/SHA256 verified, no helper imports or execution. Found
mandatory-source rootsCrypto/Cryptodome/colorama/serial/usb; Qt/FUSE imports
guarded and example/deferred contexts separated, not a verified minimal install.
No dependencies/security changes/device IO. Two new AST tests:169 tests on this
branch (does not yet include pendingPR121's two added tests). Next metadata-only
Mac dependency/backend resource plan; await genericbuild actual result separately.
## 2026-10-26 — Generic forced argument runtime experiment implemented (#119)

Merged PR120 exact7746edbb800d048b983549e39c4637f4ad998f44 after required checks
passed; based39fc2e. Implemented explicit generic-force profile in gatedbuilder
and PL011-only prelaunch checker; PR VM test injects contrarynr_cpus4/maxcpus3
and requires actual sanitizedvalid1/0 verdicts. PSCI/primary contract stays
separate. Manualdispatchdefaultsnone; no deviceprofileautoapply. Two new tests
bring suite169passing; shellsyntax/repository/diff guards pass. Actual compile/
VM result pending new PR;119 remains open. Existingreportedresources unchanged.
Next retain exact build/runtime hashes and result; physical gates stay open.

## 2026-10-26 — Actual generic forced-argument proof passed (#119)

Run40279916842/job121430735801 at710edcfdfa7c3f003ededf8e40643fde4707bbb1 passed
in23m47s; QEMU5.93s. Incominglimits4/3 overridden: actualinit verdictsvalid1/0,
oneonlineCPU/CPU0alone. PSCIstatusunavailable, separateprimarycontractfalse.
Retained exactconfig (hashmatched reconstructedCI), kernel/initramfs/console
digests and parsedrenderedverdicts in evidence/generic-forced-arguments. Raw
consolehash CI-reported, not independently reconstructed from renderedjoblog;
binariesnotarchived. Merged121 after all exactheadchecks, reconciled122worklog
and merged122 atab314ea79b5531c83620afe173cd1688a4ed2fb4 afterchecks. Current
suite173passing, retained verifier/repository/diffchecks pass.119scopeachieved;
close after evidencePR validation.106/21/22 physicalgatesremainopen. Next Mac
CLI wheel/nativeUSB resourceplan; no tablet IO/install/securitychanges.

## 2026-10-26 — Mac candidate wheel budget and USB discovery review (#106)

Currentdev299842c, allrecentCIhealthy. Version-specificPyPImetadata115387B pins
fivecandidatewheels5,126,579B; no wheelsdownloaded/installed. Fullhistoryquery
abortedat1MiBcap. LocalpiptagsonDarwinarm64/Python3.15.1acceptcandidate tags,
not runtime/APIproof. Matched3.24.1cryptonamespaces avoid unaudited4.xmigration.
PinnedhelperDarwinbranchhardcodesLinux-stylelibusb-1.0.so; resolutionunknown,
standardHomebrewpathsabsent but notfullhostinventory. Nolibraryload/USBenum.
Addedmetadataonlyplanner/twotests:175pass, nohelperexecution/securitychanges.
Next purehostMach-O/pathpreflight on syntheticfiles before install/adapter.

## 2026-10-26 — Host-only native USB library static preflight (#106)

Merged PR124 exactcd9b9747679fe88c7837dc9794640bf68bc8dbe2 after all checks
passed; base1bf092d. Implemented explicit regular-file ARM64 Mach-O dylib
preflight with FAT32/64, bounds/alignment/overlap/load-command identity checks.
Read local Apple SDK format definitions and retained hashes only. Three synthetic
tests bring suite178pass. StandardHomebrewfilesabsent; not wholehostinventory.
No native code loaded, backend/device instantiated or packages installed. No
tablet IO/securitychanges/downloads. Next native libusb artifact provenance/
resource metadata for possible isolated workspace staging, not system install.

## 2026-10-26 — Real native libusb candidate identified/statically inspected (#106)

Currentdev269b24b/healthyCI. OfficialHomebrewmetadata4810B pins1.0.30 arm64
golden_gate for observedMac27. HEADbudget191568B then boundedprivateartifact
fetch matchedSHA. Selecteddylib162720B/SHA95c5d6ec5e955b5fb83253963805a0e25a6b1253e9c4e217eaad68e31bb04f4a
passesrealMach-Opreflight; seven requirednmexportnamespresent. Staticotool has
Appledependencies and unrelocatedHomebrewidentityplaceholder, not runtimeproof.
Own boundedreproextractor/tworejectiontests:180tests pass. Binary/helperbytes
ignored; nonativecode/helperexecution/install/USBenum/tabletaccess/securitychange.
Next explicitpinnedlibrary +readack adaptercontract with syntheticofflinechecks.

## 2026-10-26 — Offline host readback safeguards (#127/#106)

Merged PR126 exact409afcb67a07d55f4f1658c5d9c4a222a4312f23 after allchecks
passed; base74f9429. OwnASTtransformer prepares explicitpinnedDarwinlibrary
lookup and exactTrue acknowledgement guard before legacyread; original caches
unchanged, modifiedhelpertext only ignored.review.txt. Actualpinnedinputs
transformed/ASTvalidated, neverimported/executed. Threesyntheticfixtures test
no-read-on-failure and platformselection/source-drift:183tests pass. No native
load/USBenum/deviceIO/download/install/securitychange.127 tracks only offline
sourcehardening;106 physicalgatesopen. Next read-only invocationallowlist and
acquisitionprecondition policy independent of broad upstreamdispatcher.

## 2026-10-26 — Transport-neutral acquisition integrity implementation (#106)

Currentbase4e33613, recentCIhealthy. Cachedlegacyread audit found reversed
remaining arithmetic1229, requested-sizeadvance1209, join/success1219 and locally
caughtwritererrors; geometrycanclip. Sourcehashes/arithmetic retained, nohelper
execution. Owncallback-onlyhostcapture enforces acknowledgedregion/exactbounded
chunks/hostdisk/exclusivecompletepublish+SHA; failuredoesnotpublishfinaloutput.
Four fault-injectiontests:187tests pass; no realbinding/library/USB/tabletIO.
Sourceandhostcontract complete; actual geometry/protocol/binding/restore open.
Next sourcebinding mustrejectclipping and prove offsets/errorpropagation offline.

## 2026-10-26 — Offline legacy read binding contract (#106)

Currentbaseda9f342, allrecentCIhealthy. Added owncallbackadapter for explicit
legacy/non-IoT/eMMC geometry, exactregionmapping/noclip, alignedboundedoffsets
and memorymodeAPIkwargs. Checksreturnedbytes/length and invalidatesselection
onerror. Fourend-to-endfake/hostfiletests:191testspass. Noactualhelperbinding
constructed/executed, native/USB/tabletIO/install/download. Internalreadflash
reselection stillrequires127guard; callbacksource/effects/protocoltimeouts remain
unqualified. Next sourcechecksum/transporterror and timeoutreview.

## 2026-10-26 — Transport deadline/checksum source contract (#106)

Currentbasea04999f/healthyCI. Pinnedhelperfastreadpasses initialtimeout0; exact
PyUSB1.3.1wheel58465BstaticZIPinspection confirmszero forwarded tolibusb, whose
API specifiesunlimited. Conditionalhangrisk, noactualhangobserved. Reader
checksumloggedbutalgorithm/comparisonunqualified; writeralgorithmnotassumed.
Ownpacketcallbackreader enforcespositiveboundedtimeouts/exactlength/tailbuffer/
monotonicdeadline and poisonsfailedstream. Fourfakeclock/packettests:195pass.
Nohelper/nativeexec/USB/tabletIO/install. Cannotpreemptbrokennativecall; next
quarantinedhostworker deadline supervision tested on syntheticprocesses only.

## 2026-10-26 — Owned synthetic worker deadline supervision (#106)

Currentbase7cbc67b/healthyCI. Ownspawnedsupervisor usesprivatequarantine/fixed
completionbytes/parentvalidation, deadlines<=30s and boundedterminate/kill of
ownedworkeronly. Real synthetic stalledchild ignoresSIGTERM then killed/reaped;
partialoutputunaccepted/removed; successremainsquarantined. Fourfocusedtests
passed1.499s/fullsuite199pass. Noactualhelper/nativeUSB/devicecallbackbinding.
NotOSsandbox or devicerecoveryproof; parentvalidator/logging/nativekillbehavior
stillrequirequalificationbeforeliveuse. Next synthetic-only session integration
of hostcontracts with explicitcomponentprovenance, no bootstrap/devicecallback.

## 2026-10-26 — Synthetic-only acquisition session integration (#106)

Currentbase3cf0710/healthyCI. Joined ownpacketdeadline, legacyAPIbinding, host
capture, worker supervision and hash/GPTverifier in built-in syntheticmodesonly.
No arbitraryworker/module/device/native/bootstrappathinput. Generated73728B
fixtures; source/component/reference-metadata digests gateparentvalidation.
Threeintegrationscenario tests bring suite202pass; faults reject/no completed
regionfiles, success staysquarantined. SharedownGPTfixture refactored from tests.
Physical-route planning question asked (USB-only vsownerhardwareaccess); no
physicalactionrequested and independentwork continues. Next retainedCLIscenario
results at exact committed source; all live/recovery/logging flags remainfalse.

## 2026-10-26 — Executed synthetic session scenarios retained (#137/#106)

At clean sourcee2b62d49840d7a162023dee83f845b2e2cc5051e, CLI success0.075s
validated threehostfixturecaptures/hashes/bothGPTs; short0.067s rejected; stall
1.006s timedout/reaped with noacceptedcapture. Exactcomponent/reference hashes
and resultJSON retained; no rawdevice/helper/nativeinputs used. Retainedproof
test brings suite203pass.137 covers syntheticintegration only;106 physical
gatesopen. Physical-route planning question remains unanswered; no inference
of permission or USB-only constraint, no tablet action.

## 2026-10-26 — Candidate entry-transition source boundary (#106)

Currentbase0f81de3/healthyCI. Pinnedfive-moduleASTaudit records crasher condition/
delegation/reinit, no terminalBROMassert, bootstrapRAMpath, conditionalwatchdog
and resetregisterwrites, hostidentifier/settings effects. Initialization is not
passiveenumeration; no whole-firmwarepersistencefree/USB-only success inferred.
Getterunpack mayraise before caller sentinelbranch; versionzero not a provenDA
compatibility.203existingtests/repository/diffguards pass; no new tests for
metadata glue, nohelper/native/deviceexec/download. Hardwarepreferencepending
without assumption. Next exactcachedPL7 EMI-format source/data inspection only.

## 2026-10-26 — Current-stock EMI data dependency (#106)

At development base316c9a4, inspected cached official currentPL7 and olderPL
without execution or downloads. Both contain identical188-byte EMI format0x10
data (digest4daa46c2...ae97); pinned helper has an explicit format0x10 branch.
Own bounded GFH/footer inspector emits metadata/digests only; two synthetic tests
bring suite205pass. Initial repository check rejected a symbolic base argument;
rerun with resolved exact SHA. No agent ACK/status/geometry or installed binary
equivalence observed. No old-preloader flash needed merely to source this data;
bootstrap/security/restore/logging still unqualified. Next initialization response
contract; pending hardware preference does not block this static work.

## 2026-10-26 — DRAM response control-flow review (#106)

Merged142 at exact8ff2b60307b64cd0e173aece0e13a277f44c894d after allfour
requiredchecks passed;141completed/projectDone. Base75a66c9. Static pinned
legacy initializer review finds unexpected/empty versionreply can fallthrough
toTrue, no format0x10 requested/local lengthcomparison, checksumloggedonly,
and unguarded geometryfieldreads. Retained metadata receipt/source citations
and failclosed acceptance requirements; no upstreamcode copied/executed,
physicalIO/downloads, or runtime success claim. Next caller propagation/stage
loading gate review. Existing205tests remain the validation suite; no test
added merely to repeat source-review prose.

## 2026-10-26 — DRAM caller stage-transfer gate (#106)

Merged144 after four exact-head77eb9a2700a81cfab6ddbb9ee4a853645c83a562
checks passed;143completed/projectDone. Base0ed87d3. Own pinned AST containment
audit proves reviewed upload_da1 stage transfer sits under truthy initializer
branch; False blocks it, no local try handlers, unexpected-reply True can pass.
Reviewed wrapper propagation; no claim of outer cleanup or observed execution.
Two synthetic AST tests, full207tests/repository/diff checks. No helper imports,
firmware/device access or downloads. Next owned offline initialization-evidence
state gate; bare Boolean cannot establish qualified stage-transfer readiness.

## 2026-10-26 — Offline initialization response decoder (#106)

Merged146 at passing exact502f407e5edd589f8f12d2569b60e818a77aaa21;145
closed. Base746d195. Implemented own field decoder rejecting unknown replies,
all field-size faults, length disagreement, nonzero status and zero reported RAM.
No transport/sender; successful decode never authorizes stage transfer or claims
checksum/geometry/provenance qualification. This is not yet an ordered state
gate or wire parser. Three synthetic tests/full210pass; repository/diff guards
run. No helper/firmware execution, tablet access or downloads. Next checksum
source evidence, then ordered capture/session invalidation before live binding.

## 2026-10-26 — Ordered offline DRAM response session (#106)

Merged148 at exactcdc6220120e86688f28eb920df1d005b1de35e28 afterfour
checks passed;147closed. Base7f1bbd0. Own response-event collector rejects
reorder/duplicate/partial/error events, clears data and permanently invalidates
aborted/consumed sessions. Three synthetic tests/full213pass. No sender/timer/
USB/helperbinding; all readiness/authorization flags remainfalse. Bounded cached
DA source search leaves DRAM checksum algorithm unknown; write checksum not
assumed applicable. No downloads or physical access. Next consolidated physical
prerequisite checklist/smallest owner evidence, not more synthetic qualification.

## 2026-10-26 — Consolidated physical recovery decision (#106)

Merged150 at passing exact7c8ea7291c8a4551968994afc028c7d14d360d5a;149
closed/projectDone. Based65dab3. Added one ordered NO-GO decision checklist
covering starting-state/entry, agent/RAM, readback origin, independent restore,
failure logs and exact package. Distinguished data-source resolution from live
acceptance and synthetic scope from physical gates. Pending hardware preference
is the only current owner input; no repeated request/action. Next minimal
mode/security collection effect review, static only. No tablet/helper execution,
downloads or new low-value tests; existing213tests/repository/diff guards pass.

## 2026-10-26 — Minimal observation source effects (#106)

Merged152 at passing4bfc7088a3ff2468643128905037758789c95de0;151closed/Done.
Basea12ecfa. Pinned initializer review: skipwdt/display are not passive-mode
contracts; unsupported target-config echo returns all securityflagsFalse.
Own six-byte zero-status offline decoder preserves missing/error as exception,
never bootstrap permission. Two synthetic tests/full215pass; metadata-only
source receipt, no helper/device execution/download. Next bounded handshake
source effects and observation-only adapter feasibility; physical gates open.

## 2026-10-26 — USB handshake/connect effect boundary (#106)

Merged154 at passing0a9a89c6bff43873a8d30b8e44dc88d42150fe4a;153closed.
Base859273e. Static exact-source review: active line-control/sync, conditional
write without explicit timeout, no default total deadline, connect configuration/
driver/interface effects; close can request reset. Metadata-only source receipt
and acceptance contract retained. No existing drop-in CLI qualified as minimal
observation. No helper/native/device execution or download. Existing215tests and
repository/diff guards pass; no tests merely repeating prose. Next owned bounded
synthetic observation orchestration, live binding still separately gated.

## 2026-10-26 — Offline bounded observation orchestration (#106)

Merged156 at passingef73e1e3fa37cf8f3d190d9d854996505d305ff0;155closed/Done.
Basee5fec79. Implemented own three-symbolic-query callback session with exact
length/zero-status checks, positive shared budget/percalltimeout, no retries or
fallbacks and sticky failure. No USB commands/backend/handshake/helper binding.
Four synthetic tests/full219pass; native preemption remains supervisor scope.
No physical mode/provenance/authorization inferred. Next source framing/status
review before exact live binding; recovery/logging gates remain open.

## 2026-10-26 — Getter framing and fresh-mode evidence (#106)

Merged158 at passing80b0bca0fee31edf297c634ccc6d6da77b7f761d;157closed/Done.
Base9632f64. Reviewed query echo/payload framing; source wrapper indexes echo
without exact-length guard. Mode query separate from three-query session and
setsTrue without clearing oldTrue on other reply. Own supplied-frame validator
requires exact echo/payload, two synthetic tests/full221pass. Zero fourthword
is explicit conservative policy, not full protocolspec. No helper/deviceexec or
download. Next fresh mode-evidence contract, preserving unknown and sessionorigin.

## 2026-10-26 — Fresh mode-reply evidence (#106)

Merged160 at passing88afb1b6280f7d50570ffb2ceab7af6362e1055a;159closed/Done.
Base806124b. Own supplied-query/reply classifier has fresh independent results,
non-echo staysunknown, missing/malformed raises; echoonlysourcecandidate, never
modeproof/bootstrapauthorization. Two synthetic tests/full223pass. No actual
query constants/USB/helper imports or tablet access. Next integrate existing
observation/frame/mode components in synthetic-only runnable host package with
source manifest; physical facts cannot be replaced by more policy extensions.

## 2026-10-26 — Runnable synthetic observation integration (#106)

Merged162 at passing6308fc4ecded6140d12241b1b4475dc964268b86;161closed/Done.
Base3d222dd. Joined fiveownedcomponents in synthetic-only CLI with invented
symbols and no device/helperinput. Executed success/bad-echo/late scenarios;
retained outputs/sourceSHA256 manifests. Faults stop firstquery/no accepted
results; late usesfakeclock, notnativepreemptionproof. Twointegrationtests/full
225pass. Next concrete live-binding design/effects/recoveryexit review, not more
syntheticreadinesslayers. Physical gatesopen; no tablet action/download/nativeexec.

## 2026-10-26 — Concrete minimal observation binding design (#106)

Merged164 at passinge0e4c213c9426cf8974610bd7d7310b94ef87c29;163closed.
Base710913c. Defined owned narrow binding instead of full initializer: unique
selection/activeconfig/claimonly, fixedqueryscope, fullwrites/exactreads, proposed
500ms/10s budgets, no fallback/reset/driver changes, cleanupuncertainty and public
allowlist. Explicitly distinguishes hostfailureexit from device recovery; no
entry/return qualified. Next fakebackend-tested actual adapter operationsequence,
not more synthetic Boolean layers. No new tests for prose; existing225pass and
repository/diff guards. No helper/native/device execution or downloads.

## 2026-10-26 — Owned observation adapter operation sequence (#106)

Merged166 at passing8ecbf6948cf53171b77aebf6e40a2981244c90cc;165closed/Done.
Base35d3e18. Implemented exact fakebackend validate/claim/threequery/release/
dispose sequence, completewrites/echo-beforepayload/exactfields, cleanupfailure
rejectsresult. Threefault/trace tests/full228pass. No nativebackend or protocol
constants/liveCLI; mode/handshake/worker supervision not integrated. No tablet/
helper/nativeexec/download. Next realstalledsyntheticprocess supervision around
this sequence; cleanup/ownership remain explicit backend trust boundaries.

## 2026-10-26 — Supervised observation adapter integration (#106)

Merged168 at passing4f9760753ca30d1020d238a850f6704851ae57b7;167closed.
Base1708182. Spawned owned adapter with synthetic successful, blockedwrite and
blockedrelease backends;1s supervisor reaps/rejects both realstalledchildren.
Parent validates success/sourcehashes; retained3CLIreports, twointegrationtests/
full230pass. No arbitraryworker/native/device input. Processdeath notcleanup/
recoveryproof. Next actual PyUSB binding implementation review and hostnative
load prerequisites, no enumeration; no downloads/helper/tablet execution.

## 2026-10-26 — PyUSB binding hidden-effects review (#106)

Merged170 at passing3f56ef9d45aacba9fc23c5a94ecc6bdc8bc37c35;169closed.
Base3b225d4. Reverified cachedPyUSB1.3.1source hashes. DeviceIO implicitlyclaims
endpointinterface, altsettingcachedefaults0, activeconfigcache notfresh, read
returnsarray, disposeignores some releaseerrors. Retainedmetadata and binding
requirements; no package/native import or enumeration. Existing230tests and
repository/diffguards pass; no tests for prose-only review. Next fakePyUSBtested
wrapper with explicit ownership/bytes/timeouts/release outcome; no live readiness.

## 2026-10-26 — Injected PyUSB-shaped wrapper (#106)

Merged172 at passingb8ca77b2d7f0153f82590c968316b05c6371a7fe;171closed.
Base097ded7. Own wrapper validates explicitinterface/unique bulkendpoints/alt0,
claim, boundedIO/arraytobytes and sticky releasefailure acrossdispose. Fourfake
objecttests/full234pass; no USB/native imports/discovery/actualhandles. Supplied
fresh/exclusive objects remain trustboundary, notruntimeproof. Next join wrapper
and adapter with fake-device uncertainclaim/cleanup fault tests; nativeABI later
withoutenumeration. No tablet/helper/nativeexec/download.

## 2026-10-26 — Wrapper/adapter integration and uncertain claims (#106)

Merged174 at passing04e793a25136a182705c324b6bde13c1d2f8d976;173closed.
Base099b002. Threeactual-layer integration tests validate selectedendpointIO/
arrayconversion and stop-onfault cleanup. Fixed uncertainclaim reporting: mark
beforeutilitycall, neverclear onexception/retry, disposal cannotclaimcleanup.
Full237tests/repository/diff pass. Fakeobjects only/no native/deviceexec. Next
host-only candidate nativeABIprobe effectreview, no context/enumeration/device
operations; physical entry/return/bootlogging gatesremainopen.

## 2026-10-26 — Executed host-only libusb version ABI probe (#106)

Merged176 at passing360723491ef218ad501e7091cbdafab543293f31;175closed.
Base95dd962. Exactcandidate noinitsection/LC_ROUTINES found in staticinspection;
tagged getversion returnsconstantstructure. Own hash-gated absolute-path ctypes
load+getversion only, bounded10s subprocess completed:1.0.30/nano12037. Retained
JSON, no contextinit/enumeration/open calls, installs/relocation/securitychanges.
This is first actual candidate native-load proof, not PyUSB/backend/deviceproof.
Existing237tests/repository/diff pass; probe not added to platform-independentCI.
Next PyUSB init/context boundary review before any backendexecution.

## 2026-10-26 — Native context/device-scan boundary (#106)

Merged178 at passingd227bf9062fef133ac35e08704000713682c5c54;177closed.
Base5a0d7e5. PinnedPyUSB get_backend constructsLibUSB/callsinit; upstreamtag
libusbDarwin init callsdevicescan. Therefore backendconstruction nothostonly
loadcheck; didnotexecute. Darwin driverdetach/attach maywholedevicereenumerate;
future auto-detachpolicy remains unqualified. Retainedsource links/metadata.
237tests/repository/diffpass. Next explicit injectedauto-detach attestation and
entry/return sourcework; no more nativecontextexecution underautomaticban.

## 2026-10-26 — Explicit injected-handle prerequisites (#106)

Merged180 at passing55075307cbe22a49f2d098d55a57e1c9ab53c704;179closed.
Base5585602. Wrapper nowrejects omitted/false/truthynonboolean callerattestations
for disabledautodetach and freshexclusiveobject beforeanyinjectedcall. One test/
full238pass; fake integrations updated. Attestationnotruntimeinspection or
permission; livefactorymissing. No device/native/helperexec/download. Next
currentstock entry/return sourcealternatives; no more syntheticpolicylayers.

## 2026-10-26 — Current-stock entry/return route refresh (#106)

Merged182 at passingdfbd0e28d6b604bd4b760660f6e8a96bb84d268f;181closed.
Basee9bad40. Refreshed primary guide at91f93505: author5.7.0.0/Linux route
intentionallybricks then modifiesboot/security; notpassiveentry or exactcurrent
returnproof. XDA502/pmOSredirect inaccessible, notnegativecompatibilityproof.
Recorded candidate-specific missingevidence and next cachedcurrentLK fastboot
handler/bootverification review. No tests added for researchprose; existing238
suite/repository/diffpass. No tablet/helperexec or firmwaredownloads.

## 2026-10-26 — Exact stock LK fastboot registrations (#106)

Merged184 at passingb1cd9cb55efee138ce7ff40a6d78911f94809ffb;183closed.
Basef8de804. Actual staticllvm inspection+own Thumbreference/call decoder resolves
13selectedregistrationlabels in exactcurrentLK, with hashes/offsets onlypublic.
Commoncallee storeslabel/length/flag/handler inlist. No bootlabel amongthose13;
notwholeimageabsenceproof or runtimepermission. No firmware/helper/deviceexec.
238tests/repository/diffpass. Next dispatcherflag and continue/reboothandler
trace; RAMboot remainsunverified, rawwindows ignoredprivateonly.

## 2026-10-26 — Stock dispatcher/filter and return-handler identities (#106)

Merged186 at passing6b8ff1ae0094a8ef4b0d2644b9e675e04b3546c4;185closed.
Base75ac7c6. ExactcachedLK pointerresolution identifiescontinue/reboot/rebootBL
handlers usingexplicitlinkedbaseassumption. Privatedisassembly shows predispatch
prefixfilter beforelistmatch/indirectcall; dynamicpolicy and +0xcfieldsemantics
unresolved. Continuebranchesdownstream, notdownloadedkernelproof; returneffects
unqualified. Metadata/windowhashes publiconly.238tests/repository/diffpass.
Next continue-to-imageproducer and filterproducer trace; no firmware/deviceexec.

## 2026-10-26 — Continue reaches boot-labelled header producer (#106)

Merged188 at passing590c2f272420f63c08f3e892b55891b2d15a0ac6;187closed.
Base24bf365. StaticexactLK trace matchescontinue-clearedglobal to downstream
selector; modezero tablecase reaches bootlabel calls24770(existingheaderproducer)
and24ce8. Ownaudit checksidentity/table/labels/calls; metadata/windowhashesonly.
Notdownloadbufferhandoff orsignaturepolicyproof; actualimageorigin/loadboundary
next.238tests/repository/diffpass; no firmware/helper/deviceexec/download.

## 2026-10-26 — Stock image named-record/callback source (#106)

Merged190 at passinga82e7a5d52f906818d25b4b2b1d7e350ce7f9681;189closed.
Base817e42a. ExactLK trace: header/load functions shareobjectprovider35da8,
bootlabel lookup35c40→20Bnamedtable search, recordoffset<<9 and callbackslot0x10.
Supportsblock/partitionstyle source, callbackactualbackend/runtimeunresolved.
Loadcallee invokes244c0; role/signaturepolicy unresolved. Owncheckedcalls and
windowhashes publiconly;238tests/repository/diffpass. Next providerinit/244c0,
no firmware/deviceexec/download. RAM diagnostic load remainsunqualified.

## 2026-10-26 — Early stock image range/size check (#106)

Merged192 at passing099defba6d64231168232c3ac444c28eeeb20a84;191closed.
Base9980a04. StaticexactLK244c0 rejects start+lengthcarry and length>16MiB,
thenfurtherplacementchecks; caller rejectsnonzero. Diagnosticlabels kernel-size
limit. Thisisnotcryptographicverifier. Metadata/windowhashes ownreceipt, runtime
lengthproducer/completepredicate unresolved, nouniversalhardwarelimitclaim.
238tests/repository/diffpass. Next lengthglobalassignments/latersecuritychecks;
no firmwarepatch/repack/deviceexec/download.

## 2026-10-26 — Resolved stock checked-length producer (#106)

Merged194 at passing26802fcf9d26270712b7871cb5e8e662eebdfa0a;193closed.
Base1b92dd6. ExactLK producer/consumerglobalidentity resolves16MiB input to
page*(ceil(kernel/page)+ceil(ramdisk/page)+2), normalnonoverflowcase. Ownbounded
model+exactstockboothash:7191666/1492335/2048→8689664B, underlimit. Two boundary
modeltests/full240pass; notfullplacement/signature/diagnosticacceptanceproof.
No firmwarepatch/repack/deviceexec. Next latersecuritychecks/providerassignment.

## 2026-10-26 — Later stock verification failure boundary (#106)

Merged196 at passinge61385edaee0158e7e380d425c3028bc6acc1ba1;195closed.
Base00574ed. ExactLK selectedpath calls1cf0c→1ce4c; wrapper mapsresult&9 tobool,
zero→explicitverifyfailure/-13. Underlyingroutine calls1cf24twice; resultbits/
keys unresolved.205ecselector alternatebranch preventsblanketpolicyclaim.
Owncall/reference/windowhash receipt;240tests/repository/diffpass. Next selector
input/resultbit/keyselection semantics; no patch/bypass/firmware/deviceexec.

## 2026-10-26 — Stock selector unlock-record input (#106)

Merged198 at passingfd6e2e203d0a942baad7ba82939d0145ca4d0349;197closed.
Base8762510. ExactLK205ec requests256B unlock_coderecord via3a4runtimecallback,
thenvalidator2080c→2062c; callbackstore/keys unresolved. No recordvalue retrieved.
Resultmask9 excludesbits10/20alone; no arbitrarynonzerostatusacceptedclaim.
Ownmetadata/call/windowreceipt,240tests/repository/diffpass. Next callback
registration/keysignaturecalls; no credentialmaterial/firmware/deviceexec.

## 2026-10-26 — Limited-unlock verifier boundary (#106)

Merged200 at passing10f1784ad4cff9841ed6dd1634a36851e6cf2282;199closed.
Base93a0601. ExactLK diagnosticsidentifylimitedunlock/RSA
transformfailure; signature/transformextent256B and subsequentverifyreturn==1
branches reviewed. Owncalls/windowmetadata only; no key/token export/execution.
Fullparameters/message/keyorigin unresolved, noavailableunlockrouteclaim.
240tests/repository/diffpass. Next retrievalcallbackregistration/backingstore;
no firmware/device/helperexec/download.

## 2026-10-26 — Unlock-record callback registration (#106)

Merged202 at passingfd5e9675ff574190fd445ae3484b43057d80a115;201closed.
Base1d304fb. ExactLK conditionalregistration resolvesgetterglobal to callbackab4,
which walks in-memorynamedrecords/copiesmin(stored,requested). Backingstore and
actualinstalledbranch unresolved; no actualrecord retrieved. Metadata/windowhash
receipt,240tests/repository/diffpass. Next containerloader3c370/callers; no
credentialexport/firmware/deviceexec/download.

## 2026-10-26 — Record container selected block-read provenance (#106)

Merged204 at passing39920fee4dab612fff16cf54ea9142d52fce361f;203closed.
Base4a2e630. ExactLK init→3c370→3aefc argscontroller0/block0/count30/selector2;
selector modifieslow3bit/configindex179 thenblockread. Wrapperdoesnotcheck
selectorreturn beforeread; sourcepathnotactualregionproof. Metadata/windowhashes
only;240tests/repository/diffpass. Next primaryregionmapping/containervalidation
identity and restoreimplication; no record/device read/helperexec/download.

## 2026-10-26 — Boot-region mapping and original-state restore scope (#106)

Merged206 at passing843dc2f5b7754d6af8d93d0180fdecd35570b2f6;205closed.
Baseb3e6d57. Linuxv6.18primaryMMC definitions/core mapaccess2 tosecondbootarea,
Linuxboot1/projectescrowboot2, distinctRPMB3. Staticinferenceonly/selectionstill
unobserved. Containerstaticmagictag notauthentication. Fulloriginalbothbootregions
required beyonduserGPT/genericimages; no newrecordread.240tests/repository/diff
pass. Next loadingalternatives affectedareas/RAMonly route decision, no more
credentialanalysisneeded forpreservation; physicalentry/return/loggingopen.

## 2026-10-26 — Loading route ranking and next RAM-stage scope (#106)

208GraphQLmergefailed504/502; confirmedopen, RESTexacthead817c021575967e324450b07e93601fe0cf1bfa93
merge succeeded8f4d5ba70ab9f458db3fb1a1a6754e49a0b86d87;207closed. Base8f4d5ba.
Selectedinvestigation: observationfirst/separatelyreviewedRAMbootstrap, notworking
route. Stockdownload+continue notprovenRAMboot; persistentarchivedchain deferred
forrestoregaps. Consolidatedstorage/logrequirements; next pinnedstage/plstage
actualeffect/exit trace, no morehostpolicywrappers. Repo/diffguards pass, existing
240testbaseline unchanged. No tablet/helper/firmwareexec/download.

## 2026-10-26 — Pinned RAM stage/plstage effects and exit (#106)

Merged210 at passing46d7a74b0e5ae800c29dc560a2f3e5d1a4d57bab;209closed.
Basea7504c5. Verifiedcachedmtk_mainSHA; stage invokesinit/crasher, writefailureloop
unbounded, marker/readbackmismatchnotabortbeforejump. Plstageconditionalbypass/
watchdog/inmemorypatch/execution meansnotpersistencefreeproof. Payloadcodeeffects
andstockreturnunknown. Retainedmetadata/sourcecitations only; no helper/payload
exec ordownloads. Repo/diffpass, existing240baselineunchanged. Next pinnedpayload
source/buildprovenance/effectaudit, notjusthostloopfix.

## 2026-10-26 — Payload source/build provenance (#106)

Merged212 at passing571ede648ce3f81879807ba9f83fd20384b57db3;211closed.
Base1e6eb13. Fetched48202B fourpinnedsources/GitblobSHAverified, nobinaries/build.
Stage1makeThumbA9/outputpath notshippedbinaryequivalence; Creadbackcasecommented
whilehostrequestsit. Cwatchdogwrites/functionjump notrecoverableLinuxhandoff.
Stage2/plsourcebuildrecipe notlocatedinnontruncatedtree, notglobalabsenceproof.
Retainedmetadata only, guards pass/existing240baselineunchanged. Next upstream
stage2/plsourceprovenance or markexactdependencymissing; no helper/payloadexec.

## 2026-10-26 — Stage2 source search and actual stage1 object compile (#106)

Merged214 at passing0fd013834bfab5ce5c0a109ec00513db76e55447;213closed.
Base4ea3f81. BoundedprimaryGitHubhistory/searchfound no stage2/static recipe;
packagedbinaryhistoryinitial65d8c4a noted, notuniversalabsenceproof. Actual
bundledclang ARMThumbA9 objectcompile succeeded0 with3nonprototypewarnings;
source/compiler/command/objecthashreceipt retained. Nolink/GCCequivalence/runtime
claim, no installs/downloads/deviceexec. Repo/diffpass,240baselineunchanged.
Next pinnedstartup/linker feasibility before any dependencydownload.

## 2026-10-26 — Actual startup assembly/link feasibility (#106)

Merged216 at passing989878ac1bce506bcff3b04960dd327b3a4c9add;215closed.
Based171d40.562Bverifiedpinnedstart/linksourcefetched. Actualclangstartupcompile0;
actualELFlink1 AppleldrejectsGNUoptions. CheckedPATH/xcrun/standardprefixes no
ELFlinker; notwholehostabsence. Receipt hashes/error retained, nolinkedpayload/
firmwareexec/install. Next existingLinuxCI smallprobe5min/1GiB/noinstall/16KiB
sourcecap, beforeanytoolchaindownload. Repo/diffpass,240baselineunchanged.

## 2026-10-26 — Bounded standalone stage1 CI link probe (#106)

Merged218 at passing2cc28bae282e24d206cc91e4ec4d423fc61f23a2;217closed.
Base96d85e4. Added ownpinnedsource compile/link driver and PRCI: preinstalled
clang/lldonly,5min/1GiB/16KiBsourcecap, metadataonlylogs/noartifactupload/noexec.
Actualsourceinputs11628B. Repo/diffguards pass; actualCIlink outcome pending,
existing240testbaseline unchanged. Next inspect exacthead joblogs/fixactualbuild
error orretainlinkedELFmetadata, neverequatewithboot/handoff.

## 2026-10-26 — Linux first-stage link succeeded; retain exact CI receipt (#106)

PR #220 merged after five passing checks at head
6d33a5543136c807798f0f8845d3ea7a7a6ddb09, merge
5256cb0c1a15a5271e0fd2a801d6a3e1cd9d2e5b. Run 40386637095 / job
121796533606 actually tested synthetic merge 15abe7c2eeb22554802ce3105321c883a75d9e1c.
clang/LLD 18.1.3 compiled and linked 11,628 source bytes with three warnings;
68,672-byte ELF SHA256 1508a0dd3979548cca178ee9f15c7492fd9a4a080ee8118ca884dfef8e7bae48.
Retained sanitized metadata, not raw logs or ELF. Entry zero is not a physical
load address. No installs, firmware execution or device access. Next: bounded
ELF layout/entry metadata, then transport protocol and restore/logging gates;
no boot/recovery/hardware issue closed from a successful link.

## 2026-10-26 — Add first-stage ELF load-layout gate (#223 / #106)

Merged #222 after all four exact-head checks passed at
92e77e8b5f4adeb4f2de94a19aef8820d8e59778, merge
465de695de5f7df18e9f7859c899fc4942b0de22; #221 closed.
Added owned bounded ELF parser and build-probe integration to validate PT_LOAD
extents/alignment and file-backed executable entry coverage. Metadata only;
no firmware execution, sections/disassembly or device access. All 243 host tests,
repository guard and diff check pass. Actual Linux layout result pending CI.
Next retain actual segment metadata, then resolve flat transport/source protocol
compatibility; restore and logging remain separate open gates.

## 2026-10-26 — Actual load footprint and zero-fill prerequisite (#225 / #106)

Merged #224 at passing head 26a73eafd347f8245ba604ae80f83261aedda240,
merge 0e15409e9110313b001968f523b5fbc9cf81ab6e; #223 closed. Run
40390989927 / job 121811611547 tested 9e33f04f31493384f5e654d394a2e504ac22249a.
Three PT_LOAD segments cover executable entry zero; virtual end 1600, file-backed
end 1576, 24-byte zero-fill tail. Same ELF SHA256 as prior receipt. Startup has
no BSS clear; flat loading initialization remains unproved, not a shipped-binary
failure claim. Metadata/source citations retained; no firmware/device execution.
Repository/diff checks pass; existing 243-test baseline unchanged by prose/receipt.
Next pinned sender padding/input/entry assumptions and initialization ownership.

## 2026-10-26 — Sender initialization boundary (#227 / #106)

Merged #226 after four checks passed at 0ed89e9e6f9ca0bcc86716baff679e4db7b71f82,
merge e26e47b41f5d6545909d8d4826ac7a03831c09a4; #225 closed. Verified four
cached sender source Git blobs against pinned 7cb40e727727dfe3faa065eefb29b16ed29bbdf1.
Selected raw-file/shared preparation/kamakiri2 path has four-byte padding, no
ELF/BSS size input; 1576 already aligned leaves the linked 24-byte zero tail
unprovided by alignment. Insecure DA signature padding is not initialization
proof. Final-word sentinel patching also needs an explicit owned image contract.
Metadata only; no helper import/execution, download or device access. Repository/
diff guards pass; existing 243-test baseline unchanged. Next owned host-only
load-image initialization contract, keeping device loader/restore/log gates open.

## 2026-10-26 — Owned zero-initialized host image constructor (#229 / #106)

Merged #228 at passing b63984e2a9f8a227cd56a1dca8108a77a439d8d0,
merge 35c76f8732b51e5c4249ea38a2764e37cd45565f; #227 closed. Added bounded
owned PT_LOAD image construction: preserve file bytes, zero tails/gaps, reject
overlap/nonzero-base/mismatched physical fields/>64KiB memory. No sentinel patch,
execution or transport. Integrated metadata-only image hash/size into Linux probe.
All 247 host tests pass; repository/diff guards pass. Actual CI image receipt
pending; next relocation/entry assumptions, keeping physical recovery/log gates open.

## 2026-10-26 — Host image receipt and relocation gate (#231 / #106)

Merged #230 after five passing checks at b22b1a4bc3ba2b65bf37bc9c8846e825224a7709,
merge ef7a1678e1b254d80b2b60698f662a658ef99669; #229 closed. Job
121834928446/run40397672319 actually constructed 1600-byte host image SHA256
fba4681457cdcf32a0a1541ff7a3dc429b35341ef97d1c1e05eddde40985e79e,
24 tail zeros plus two gap zeros. Metadata retained, no binary upload/execution.
Added section-table/REL/RELA/DYNAMIC rejection gate with malformed extent tests.
251 host tests pass; repository/diff guards pass. No relocations is not runtime
PIC proof. Pinned startup inherits stack/CPU state; main assumes BootROM mapping.
Next actual CI section metadata and static address/entry review, not device access.

## 2026-10-26 — Emitted address/stack dependency (#233 / #106)

Merged #232 after five passing checks at 7af6da7fd59430eb1cb01fe270a7bbae1f6abc7a,
merge 6629548e47b8a74dc4c9800ea46a7cbb9eb38e36; #231 closed. Linux job
121842687478/run40399916804: ten sections, no nonempty relocation/dynamic
sections, unchanged initialized image hash. Independently hash-verified cached
Apple clang object; static objdump counts 31 REL32 and ten THM_CALL references.
Main immediately reserves eight bytes and stores through inherited SP; not a
maximum-stack or whole-image PIC proof. Local compiler/object differs from Linux.
Retained metadata only; no raw code/disassembly or firmware/device execution.
Repository/diff checks pass; unchanged 251-test baseline. Next owned image-relative
stack/entry-marker diagnostic experiment, compile/inspect only, no upstream main.

## 2026-10-26 — Owned stack/marker diagnostic entry (#235 / #106)

Merged #234 at passing be5e8653b002c90b5eafe6c8bdb140a1dca9d71f,
merge cd4e46560e93e49cd8b75b811661e28e3ebacf29; #233 closed. Implemented
owned ARMv7 entry with image-relative 1KiB stack, in-image marker and final loop,
no upstream main/external calls/peripherals. Actual Apple clang object compile
passes; static inspection SP assignment precedes marker store, marker offset36,
stack top1064. Linker assertions and bounded Linux CI added; actual link pending.
No execution/USB/device access or return/recovery claim. Repository/diff guards
pass; unchanged 251-test baseline. Next actual Linux result and explicit caller/
return ABI; memory marker has no qualified readback/log transport yet.

## 2026-10-26 — Callable diagnostic leaf ABI (#237 / #106)

Merged #236 at passing e70e2d2ba4a1c84022d500fd22dbbdcfdf28b5ab,
merge a3aa8b6030840d6b27a90896bdeb3ec540d71ef4; #235 closed. Job
121864827490/run40406304083 tested fc3b2535c692f313512eff8f709038b2b58f30e3:
owned loop entry linked and passed host image gates. Receipt retained.
Added separate callable leaf preserving inherited SP/LR/r4-r11, setting private
stack before marker then restoring SP/bx LR; local object compile/static review
passes, marker offset48/stack top1080. No execution, device access or stock-return
claim. Linux builds both variants; callable result pending. Repository/diff guards
pass, unchanged 251-test baseline. Next supplied-snapshot marker/identity decoder
and actual loader caller-state qualification; restore/log gates remain open.

## 2026-10-26 — Supplied marker decoder and callable link evidence (#239 / #106)

Merged #238 after five passing checks at 4414763af2346435eb7c57112dff6eb4bf08883a,
merge 16cb3a9f6b32f3d0fd923c38215cec688d44b724; #237 closed. Linux job
121871790870/run40408334717 linked loop1064B and callable1080B, receipt/hashes
retained. Added bounded supplied-snapshot identity/marker decoder, immutable code/
padding checks and explicit no-runtime/freshness/return claims. 255 host tests pass;
repository/diff pass. CI synthetic mutation against linked images pending; no
firmware/device execution. Next real loader callable-return/readback source path,
not more marker features; restore/security/log transport gates remain unresolved.

## 2026-10-26 — Concrete loader return/readback incompatibilities (#241 / #106)

Merged #240 at passing 93bfda82c60fc0670e9b1a424804c1a0ef58bc1c,
merge 9c6fa17c874a6f803eee1ae6ac01b835ded49072; #239 closed. Verified cached
pinned stage C/host source identities. C callable return resumes command loop
without ACK while host awaits stage2 startup ACK. Active source lacks read;
unknown read command leaves address/length as next magic, which can reach final
infinite loop. Even commented read handler omits completion ACK expected by host.
Retained metadata/citations only, not packaged-binary/runtime claims. No helper/
firmware/device execution. Repo/diff pass; unchanged 255-test baseline. Next owned
bounded call/read specification and matching auditable agent, not upstream host
binding; restore/security/physical log gates stay open.

## 2026-10-26 — Owned offline call/read specification (#243 / #106)

Merged #242 at passing a9636d7287679aeaf37cfc5daf18fa3c1ec04ed0,
merge 20a0fd9f26b583239048ba8d05223742a6e41594; #241 source scope closed.
Implemented owned 16-byte version/sequence/status/range wire model, fixed-slot
single CALL explicit completion, <=256B READ within1080B, exact response lengths,
fail-sticky replay/error/abandon handling. No transport/agent/clock/execution.
259 host tests pass; repo/diff guards pass. Next matching injected host-only
command dispatcher, then statically compiled agent. Physical entry/restore/log
transport remain open; this is no upstream-compatible or runtime proof.

## 2026-10-26 — Matching injected host dispatcher (#245 / #106)

Merged #244 at passing d8df40151c8706743f5f38ab6b2bc7d5c6e2812c,
merge 6e41374167c046caeb1816109f7ef000c8e76a75; #243 closed. Implemented
owned host-only dispatcher, fixed-slot callback completion/exact reads, pre-callback
validation and fail-sticky callback/replay/reentrancy handling. Both ends bounded
to16transactions. Synthetic CALL+five READs retrieves1080B;263hosttests pass.
Repository/diff pass; no device/transport/ARM execution. Next owned freestanding C
dispatcher compile/static review and vector comparison, not physical loader binding.

## 2026-10-26 — Owned C dispatcher core (#247 / #106)

Merged #246 after four checks passed at 4c5edbfa80b4f06f2cb89d5c812cb84369035f4f,
merge af4261e2556bf3fa5c2aace70b94690abc2ed718; #245 closed. Implemented
owned freestanding C bounded CALL/READ core with injected callbacks, capacity/
order/range checks,16transaction budget and error invalidation/zero published
response length. Actual ARM compile with -Wall/-Wextra/-Werror passes, no undefined
symbols observed. ARM object never executed. Native host synthetic-array unit
executable passes;264hosttests pass. Source/header/object receipt retained.
Repo/diff checks pass. Next C/Python vector equivalence then explicit owned entry/
callback link; no transport/security/restore/log hardware qualification implied.

## 2026-10-26 — Direct C/Python protocol vectors (#249 / #106)

Merged #248 at passing b5f6c33e702f4a0e8184f85468f385a3a47bf5be,
merge 6591aa94e794fa5645e6f9aa737a3cca1c30ff4a; #247 closed. Added native
host runner and direct Python/C comparison:76sessions/171frames,64header mutations,
full1080B read, read/truncation/budget boundaries and host response acceptance.
All selected status/length/response bytes match;267hosttests pass. Source hashes/
counts retained, no exhaustive/target ABI/runtime proof. Repository/diff pass.
No ARM execution/device access. Next owned agent entry/context static link and
explicit injected transport ABI, leaving physical security/restore/log gates open.

## 2026-10-26 — Callable agent context/framing ABI (#251 / #106)

Merged #250 at passing aa55a900f61187e299b7af3a3adb7a51d1267fac,
merge 68e31eac2a328cda3f18427ea0a2668de2f315a4; #249 closed. Added owned
agent loop with versioned injected callbacks/count1..16, exact receive/send,
initialized local context and abort/no retry after partial completion. Native
host tests pass;268hosttests total. Actual ARM object compile passes with one
expected undefined diagnostic_dispatch, source/object hashes retained. No ARM
execution/device transport. Repository/diff pass. Next static agent+core link with
stack-preserving entry; callback deadlines/cleanup and physical restore/log gates open.

## 2026-10-26 — Owned agent stack-preserving entry/link probe (#253 / #106)

Merged #252 at passing 538c758d5e609b20de1efb23a3b85c3165690a41,
merge e60a1ac378a433306577ebc93b6eeecf2cd4d08d; #251 closed. Added Thumb
wrapper preserving SP/r4-r6/LR and r0 ABI pointer, private2KiB stack before push/
C call, restore-before-return. Actual local wrapper compile/static review passes.
Bounded Linux wrapper+agent+core link/image/relocation probe added; result pending.
Source/object hashes retained, no firmware execution or transport/device access.
Repository/diff pass; unchanged268testbaseline. Next actual link and static stack
requirements; callback deadlines/cleanup/security/physical restore/log gates open.

## 2026-10-27 — Actual agent link and static stack measurement (#255 / #106)

Merged #254 at passing f9316e72cb431cc66a8875e82f201724a6622787,
merge 0c802ad4b6e87eba1cb52c8a6298550a572ccb03; #253 closed. Linux job
121921673252/run40422978975 linked2608B image SHA256
d47572bcdfda9dcd9d66e7f07046f5903a1c3e647a2bec3d7a742d3a93c4d590,
Thumb entry1/six sections, metadata retained. Actual local ARM stack compilation
352B agent+32B dispatch+16B wrapper=400B owned;1648B before unknown callbacks/
interrupts, not whole-program bound. Added Linux static-frame gate/metadata;
actual Linux stack outcome pending. Repo/diff pass; unchanged268testbaseline.
No firmware execution/device access. Next Linux result and bounded transport/
cleanup contract; physical security/placement/restore/logging remain open.

## 2026-10-27 — Linux stack receipt and frozen callback ABI (#257 / #106)

Merged #256 at passing b67e5fa6379727e871e3f384d05fc5ad712f72a8,
merge 6f1cac28444daa9e601ffacce25292f0a3ab6c04; #255 closed. Linux job
121932357873/run40426169089 reports360B agent+40B dispatch+16B wrapper=416B,
1632B before unknown callbacks/interrupts; exact receipt retained. Found callback
ABI rereads during loop; snapshot validated fields before first callback.
Native regression mutates caller ABI but original2transactions complete safely;
268hosttests and actual ARM recompile pass. New link/stack result pending CI.
Repository/diff pass. No firmware/device execution. Next concrete transport
source deadline/error/cleanup investigation, no unqualified BootROM callback binding.

## 2026-10-27 — Concrete USB callback contract rejection (#259 / #106)

Merged #258 after five passing checks at c786c266c22228963720f442c53c996e96b45365,
merge61e5e8e233c852589941835e4eb6fc1c271702fb; #257 closed. Verified pinned
usblib blob. Write returnsbool, zero progress has no bound; fast read initial
argument0/nonfastdefault, no total monotonic deadline. close(reset=False) clears
RX and mayattach kernel driver0. Direct agent/host binding rejected; metadata/
source citations retained. No import/backend/device access. Repo/diff pass,
unchanged268tests. Next owned exact-count injected host framed transaction
integration, not upstream binding; BootROM-side timing/security/restore/logs open.

## 2026-10-27 — Injected framed host capture (#261 / #106)

Merged #260 at passing6b5061874d30e18e1bed25faa9724e966a39b5b2,
mergea8430a0a7130d5371dc84bad95a70862d4c0e7e4; #259 source scope closed.
Integrated CALL+1080B framed READs with injected exact-count backend, cooperative
5s/positive<=500ms I/O, header-before-payload checks and no partial-send retry.
Release/dispose gate publication, late-claim cleanup regression included.
272hosttests pass; repo/diff pass. No USB import/native backend/device access.
Clock cannot preempt blocking callbacks; next existing supervisor integration with
actual synthetic stalls and parent validation. Physical entry/restore/logs open.

## 2026-10-27 — Real spawned synthetic framed stalls (#263 / #106)

Merged #262 at passing ccb3b4cc66b5e9d7809298d44bb1a8c0814c213f,
merge e5945736869131be7957199166a56eea889e7524; #261 closed. Integrated
complete framed synthetic capture with existing supervisor and parent exact
snapshot/hash/source validation. Actual measured success0.060s; write/read/
cleanup stalls reaped/rejected1.003/1.005/1.004s.274hosttests pass; metadata
receipt retained, no firmware/device/native backend execution. Repo/diff pass.
Forced stop is not device cleanup/undo. Next concrete initial loader/return
qualification dependency check, not more host simulation; restore/log gates open.

## 2026-10-27 — Concrete initial loader ABI gap (#265 / #106)

Merged #264 at passing76fcb8cf0333ed6336e749938bee851081e20b5e,
mergeea74b9006a558842edf17bc14490e509aa434669; #263 closed. Verified cached
loader sources. Generic jump(0) cannot supply owned agent's required IO context;
native null-context rejection regression passes. Thumb entry differs from byte
base; direct JUMP_DA host address/status does not prove firmware register/LR ABI.
274hosttests/repo/diff pass. Source receipt/checklist retain concrete initialbridge
blocker, no runtime gates closed. No firmware/device execution. Next source-backed
initial bridge design, not more host framing; original restore/log channel open.

## 2026-10-27 — Owned ARM/context bridge compile (#267 / #106)

Merged #266 at passing9638262334a915a7ca1ff74731175dd89a143c2e,
merge939dea327d6ee0f2f2fa15e4ea6d2495d9f3c8a9; #265 source scope closed.
Added owned ARM-to-Thumb bridge, image-relative28B IO context/private stack,
caller SP/callee-state preservation. Context callbacks deliberately zero; native
regression rejects before activity. Actual local assembly and ARM C layout-assert
compilation pass;274hosttests pass. CI links both variants; bridge result pending.
Repo/diff pass; no firmware/helper/device execution or callback patching. Next
actual link/context installation source qualification; initial security/restore/logs open.

## 2026-10-27 — Actual ARM bridge and callback ABI mismatch (#269 / #106)

Merged #268 at passingd6565b24ea9873945c2bf72328249a8c7264e9e6,
mergeabb283349c889946bd6ae74d9708b0d412bd69d3; #267 closed. Linux job
121962950955/run40435462898 linked bridge2664B SHA256
d95c2fef63f30e5c891dfd9d50934e693a717a7f985cfdddcbf50d1e7dbbcdb7,
owned stack424B. Pinned source get/put lacks opaque argument, get used as zero
success while owned callbacks require counts, put return ignored. Direct pointer
binding rejected. Native zero-count regression/274tests pass; repo/diff pass.
No firmware/device/pointer installation. Next implementation provenance/alternative
transport source, not guessed adapters; security/restore/real logs still open.

## 2026-10-27 — Callback provenance and dispatch repair (#271 / #106)

Merged #270 at passingb51257a6125b9255df6be2184e7d93b5b8c87d08,
merge0d14b4a47c78922bc66224f57166a2e6332c0b38; #269 closed. Bounded cached
complete-tree inventory found no actual get/put ROM bodies, notglobalabsence.
Selected source discovery extracts runtime pointers and repairs USB dispatch slot
without saving prior slot in that block: additional return dependency, not passive
lookup. Source/tree metadata retained; no helper/ROM/device execution/acquisition.
Repo/diff pass; unchanged274tests. Next independent bounded UART logging source/
compile task using known register contract, hardware qualification still open.

## 2026-10-27 — Bounded independent UART log core (#273 / #106)

Merged #272 at passing3705c215aee1a82c5eac69964a3daaf1a8a8384d,
merge0a52854aa4dc9652a644d191e5485d243dec840d; #271 source scope closed.
Implemented owned <=64B UART polling core, shared<=4096status reads, actual partial
counts, DLAB guard, no configuration/reset/physical mapping. Actual ARM compile
passes; native fake-register tests/275hosttests pass. Source/object receipt
retained; repo/diff pass. No ARM firmware/physicalMMIO/device execution. Pollcount
is not time/fault bound, queuedbytes notcapturedlogs. Next sanitized fixed markers
and compile-only integration, physical entry/restore/UART hardware gates still open.

## 2026-10-27 — Fixed sanitized UART markers (#275 / #106)

Merged #274 at passingd43b036230f1c5aa97d42111782dc3b9b1fa6bea,
merge451cc67c93545ad3404c5cfd14c2b3770b5a3a89; #273 closed. Added enum-only
ENTRY/RETURN/ERROR fixed lines, no dynamic data, unknown marker rejection/partial
counts. Native newline assertion caught literal-length error; fixed with sizeof
literal before publication. Actual ARM compile and275hosttests pass. Linux links
logging code into both variants; no automatic UART calls/mapping. Receipt retained,
repo/diff pass. Next actual linked exports/layout; physical UART/entry/restore/logs open.

## 2026-10-27 — Explicit logged agent outcomes (#277 / #106)

Merged #276 at passingd1205173f064dbae3a300d3afd557c42fe864b7b,
merge938de492c81b1b5e096e00dceb482feb4f3c0171; #275 closed. Retained actual
marker-enabled link receipt. Added explicit opt-in logged runner, sharedpollbudget,
shortENTRY prevents agent, result preserves agent/partialexit outcome. Default
entry never autoUART/mapsphysicaladdress. Actual ARM compile/full276hosttests pass;
affected native tests rerun for exit-readiness-loss after agent completion. Repo/
diff pass. No firmware/physicalMMIO/device access. Next actual link and remaining
entry/restore/capture evidence inventory, not more logging features.

## 2026-10-27 — Integrated build versus physical readiness (#279 / #106)

Merged #278 at passinga3f3e843b5fd7bc149b4bad17d0af06405362055,
mergebba9892d6d4703f584ed0d3212f62cc726d0d409; #277 closed. Linux job
121986688898/run40442747715 linked direct3024B SHA256
3cc9853fc3d2ea082b67dcb8f62918e38f77570224e41185a030f2e1ebfe6f2c,
bridge3072B SHA256970f453dc8a6c802c899e0b341e6070ac4390cbe4ace1abb60e97df3405cfe9a.
Retained exact source/tested revision and six source-cited open physical gates;
removed stale host-test count from checklist. Build/config/boot/hardware/apps
kept separate. Repo/diff pass; unchanged276hosttests. No firmware/device execution.
Next current-build initial-entry/return alternatives, not more marker/synthetic
features. Existing hardware-vsUSB planning choice pending, no repeat/newphysicalask.

## 2026-10-27 — Actual initial-entry crash effects (#281 / #106)

Merged #280 at passing1f2fd2e6aa0a971bfb9b92773d5b753e07ec8369,
merge4875efc50528a7129563ada8dcc63db799c01c11; #279 closed. Reviewed actual
pinned crash implementation beyond prior delegate audit, verified blob and AST
call inventory. Modes0upload/1lowread/2upload+execute; explicit3reset absent from
default0..2loop. Exceptions swallowed/no positive transition result. Metadata
only, no payload code publication/helper import/device execution. Repo/diff pass,
unchanged276tests. Next explicit reset effect/return source assumptions, not mode
execution; current-build entry/failed-exit/restore/log gates remain open.

## 2026-10-27 — Explicit BootROM flag/reset distinction (#283 / #106)

Merged #282 at passing59d21af7ef8f4a03dc61f8dde81202aeeb8bed9e,
mergea3b8d9c3131716009ed4cd24b033a6a53d02464f; #281 closed. Verified pinned
reset/config blobs and AST calls. Four registerwrites, no savedoldvalues/checks,
no explicitresettrigger/positive transition result; default source no-timeout
encoding. MT8163 record has misc_lock, actualinstalledstate match unproved.
Metadata/sourcecitations only; no helper/deviceexecution. Repo/diff pass;
unchanged276tests. Next stock mode/return alternative avoidingflagmutation,
keeping physical observation/restore/log gates open.

## 2026-10-27 — Stock reboot common primitive (#285 / #106)

Merged #284 at passing8f329e0842d5cf3ff6c37aac211cb8abec3a3199,
merge407219243cf842f91e01b9a9426b18baf0b8d26d; #283 closed. Exact current LK
static windows show reboot/bootloader handlers tail to28410 argument1, latter
extra helper288e8. Common primitive MMIO/wait-helper/final-control write then
terminal selfloop; no observedreset/stockreturn. Retained hashes/offsets/manual
metadata with own hash-gated audit script, no raw windows/disassembly published.
Repo/diff pass; unchanged276tests. No command/firmware/device execution. Next
extra bootloader helper state effects; original restore/log/entry gates open.

## 2026-10-27 — Bootloader mode flag and commit wait (#287 / #106)

Merged #286 at passing4156915238590dafd41d34a9d7c12c304a94dc16,
mergede8c4e996777750542827889a0af75f864638b5b; #285 closed. Exact LK selected
helper288e8 read-modify-writes802c/bit2000 then284e8writes803c/polls8000bit40
without local bound; access status unchecked. Read/write wrappers share269c8,
physicalbackend/persistence unknown. Plain reboot selected handler omits helper;
narrower sourcecandidate, not observedreturn. Metadata-only own hashgated audit,
repo/diff pass, unchanged276tests. No commands/firmware/device execution. Next
backend and flagconsume/clear path; restore/log/initialentry gates stayopen.

## 2026-10-27 — Selected mode-flag consume/clear path (#289 / #106)

Merged #288 at passingeceb49366c087fc997e0d9fde2732047749c7b96,
mergeafa3e8ee03500d99ea370d88f90799510666720a; #287 closed. ExactLK reader
2892c extracts bit13/selector802c; caller243b2 nonzero branch24446 storesmode63
then tailcalls setter288e8 argument0. Staticclearpath found, access/clearstatus
unchecked; actualresetretention/clearunobserved. BackendprefixusesMMIO, identity
stillunknown. Own hashgated metadataaudit/repo/diff pass, unchanged276tests.
No commands/firmware/device execution/rawdisassembly publication. Next cached
platform backendidentity; physicalentry/return/restore/log gates remainopen.

## 2026-10-27 — Hardware route planning choice resolved (#291 / #106)

Merged #290 at passing1ea50ba3d397ece6e20e5d85a6d9af4cd69132ba,
merge75dbc4db1bfacc29b64f03b3659038f51a043ee9; #289 closed. Owner accepts
hardware access if needed for planning. Updated stale current preference gates;
no action/automatic-device authorization inferred. Scoped board revision/PCBpads/
voltage/entry-return/restore/log evidence separately from GPIO source. Primary
original XDA retrieval502, not incompatibilityproof; no images/helper/bigdownloads.
Repo/diff pass; unchanged276tests. Next traceable same-revision board/UART source,
then independent cached backend investigation if source inaccessible.

## 2026-10-27 — PMIC-wrapper/RTC mode backend identity (#293 / #106)

Merged #292 at passing335697c980d5b99bc16ed6edcf72259382ba7751,
merge8f3e3c72f286dc146c8d762286b92194ccc27de1; #291 closed. Bounded board
source search did not qualify PCBpads/electrical info; crossmodel claims excluded.
Independent cached platform task: verified five relevant files against pinned
Gitobjects; WACS2 base/offset/encoding matches selectedLK, RTC PDN1/FASTBOOTbit13,
WRTGR and BBPUbusybit6 allmatch. Strong sourcealignment, not exactbinaryprovenance/
retention/restore proof. Hashes/source links retained; repo/diff pass, unchanged
276tests. No downloads/helper/firmware/device execution; unrelated sourcechanges
untouched. Next RTC commit/error/retention source behavior and exact evidence needs.

## 2026-10-27 — RTC commit/error and restore boundary (#295 / #106)

Merged #294 at passing6fca2deff8439aab4a30410c86b250fa5099f70e,
merge4f5aae0e6b3ea0ebfb95fb86396142c5f8fd0f57; #293 closed. Verified RTC
source bytes against pinned Gitobjects: zero-initread discards pwrapstatus, void
write, unboundedCBUSY commitpoll, matchingFASTBOOTflag. Lowererror-aszero is
inference, notdeviceobservation; user/bootescrow doesnotprove RTCrestore. Metadata/
primarylinks retained; repo/diff pass, unchanged276tests. No firmware/device access.
Next least-state-change return/entry evidence needs; RTCretention/originalrestore/
security/real logs remainopen.

## 2026-10-27 — OS restart mode-state comparison (#297 / #106)

Merged #296 at passinga21f962a81b0ecc1caf21ddb1e8f78ba72f7ec80,
merge9f7f01edf6f5c11901bae1bc65ebaaf9003cc5d2; #295 closed. Verified cached
arch_reset/RTC Gitobjects: namedbootloader/recovery branchesmarkRTC, selected
ordinary branch omitsmarker then watchdogAPIreset. Not runningkernelidentity or
wholepathstatefree proof. Metadata/primarylinks retained; repo/diff pass,
unchanged276tests. No reboot/helper/firmware/device operations. Next minimal
mode/return evidence plan for hardware-acceptable route; physicalgates open.

## 2026-10-27 — Hardware identification evidence plan (#299 / #106)

Merged #298 at passinge8e2c7907c7a798071d071d2ba8c0be460d085a1,
merge available in repository history. Located firsthand exact-generation/KFDOWI
cover account and iFixit7thgen identification category; neither qualifies PCBpads/
voltage/entry. Added staged model/PCB/electrical/mode-return/log evidence plan,
explicit missing batteryisolation and sanitization. No photos copied or physical
steps/request/device access. Repo/diff pass; unchanged276tests. Next same-generation
internal board/battery-isolation provenance before concrete owner inspection proposal.

## 2026-10-27 — Exact-board isolation gap and existing-record question (#301 / #106)

Merged #300 at passing21f6cad9b692c9396daada45d8de16df30197007;
#299 closed. Source review: same-generation supplier battery compatibility does
not qualify connector isolation/UART voltage; mixed-generation manuals excluded.
FCCindex403 not inspected/absenceproof. Asked owner whether existing internal-board
photos/revision records exist, explicitly no opening/connection. Source-gap receipt
retained; repo/diff pass, unchanged276tests. No device/helper/firmware access.
Next use existingrecords ifavailable; independent sourcework otherwise, no guessed
physical procedure or gateclosure.

## 2026-10-27 — Cached official restore coverage (#303 / #106)

Merged #302 at passingb55ab72dc484a84404ce54a2bf9687a6e281b0e6,
mergeb8b8092d83ec64b6bb510c1e0ac129a506fd1497; #301 source scope closed,
existing-board-record answer stillpending withoutrepeat. Independentrestoretask:
rehash buildchecked cachedOTAindex/boot/preloader/LK; packagedcomponents/headers
not original user/bothbootregions/device-specific boot2records or RTC/RPMBrestore.
Coverage receipt retains sizes/hashes/limits, no newdownloads/physicalreads.
Repo/diff pass, unchanged276tests. Next exact original-region provenance/restore
requirements, use existingboardrecords ifprovided; no runtimegates closed.

## 2026-10-27 — Two-set offline escrow consistency (#305 / #106)

Merged #304 at passing86e47ed9fa1befd4a2435e55cc5d055ff16fa832,
merge5ecb7d2f2590b0e86876c51228dee26231760b71; #303 closed. Added actual
host two-set verifier reusing length/hash/GPT validation, six distinctinodes,
filechange/geometry/digest mismatch rejection, sanitized output. Synthetic tests
cover agreement/alias/differentvalidhash/GPT/symlink. No actual captures/device
reads or independence/RTC/RPMB/restore proof. Repo/diff checks pass. Existingboard
question pending withoutrepeat; next acquisitionprovenance/regionselection evidence.

## 2026-10-27 — Supplied eMMC geometry decoder (#307 / #106)

Merged #306 at passing3daeb6ff5a899e808d85a4b038b867a80bf2db38,
merge8ce664a5a0bddc8050f09c49bf399eed9a11c250; #305 closed. Added actual
supplied512B EXT_CSD geometrydecoder, revisions6..8, SEC_COUNT512Bunits independent
ofsector-size and BOOT_MULT128KiB, project/Linuxregion mapping/accessclassification.
Verified cached source Gitobjects/receipt, four synthetic tests/full284pass.
Repo/diff pass. No metadata/device acquisition/selector/helper execution; origin/
selection/independence/restore remainfalse. Existingboardrecord question pending;
next integrate suppliedgeometry into explicit escrow evidence validation, no physicalbinding.

## 2026-10-27 — Escrow versus supplied geometry (#309 / #106)

Merged #308 at passing34738376ef0717520fbea67b7c3db1a643b87398,
merge69514e8f1eec1cafbeac77d8d1ff35d7cf2f83bb; #307 closed. Added optional
supplied512B metadata cross-check for sector/three-region extents in both sets;
matchingwrongsize copies reject. Three newsynthetictests/full287hosttests pass;
repo/diff pass. Output geometryconsistency only, no origin/selection/independence/
restore claim or rawmetadata. No device/metadata acquisition. Existingboardquestion
pending withoutrepeat; next actual acquisitionprovenance/restore entry remainsopen.

## 2026-10-27 — Two synthetic owned-agent link bases (#311 / #106)

Merged #310 at passing20fc3ab74acf91a42c1374cf9fea11a422cfe879,
mergecf1fd5782ed0e2e1840e30833adb8a451b873695; #309 closed. Independentloading
work while boardrecordanswerpending: compile-only bothownedvariants atzero and
synthetic10000000, compare normalized validated loadbytes/relativeentry/state.
Three newcomparator tests/full290hosttests pass; actualLinuxcomparison pending.
Repo/diff pass. No execution/physicalplacement proposal; two-baseagreement would
not prove arbitraryruntimePIC/MMU/cache/callback/restore/log safety.

## 2026-10-27 — Actual two-base failure and marker fix (#311 / #312)

Run40470154989/job122075066145 failed comparison at head
41fb9974b93df73a608eb54e63cc9431060575f2; #312 notmerged. Separate local marker
object revealed3ABS32 pointertable relocations; linkedELFsection absence had not
proved baseindependence. Replaced switchpointerselection with fixedstride chars/
scalar lengths. Actual local ARM recompilation shows0ABS32 markerentries;
290hosttests pass. Retained failure/object/source metadata; Linuxconfirmation
pending. Repo/diff pass. No firmware/device execution. Next exacthead CI both
variants, no weakened comparison or runtime/restore claim.

## 2026-10-27 — Corrected Linux two-base result (#311 / #312)

Actual Linux job 40471752722/122080264532 passed at source head
`722f52846a9e1aafba65206c82f291af115fdceb`, tested merge
`0c7a7b78b76dfcc5f15102046e82322b5f1a3644`. Direct (3000 bytes) and bridge
(3040 bytes) have equal normalized load bytes at zero and synthetic `0x10000000`,
with unchanged relative entry and ARM/Thumb state. Exact image/source hashes,
tool versions and stack analysis are retained in
`evidence/owned-agent-link-bases/report.json`. This confirms the pointer-table
fix for these two linked bases; it does not prove arbitrary runtime relocation,
physical mapping, callback binding, security entry, original-state restoration
or captured UART output. No firmware or tablet execution occurred.

Next: original acquisition/restore provenance and board-specific logging
qualification under #106; existing board-record question remains pending.

## 2026-10-27 — Offline fixed-marker transcript reader (#313)

After #312 merged as 926a8aefe592e97b03e27a4498251ce40393000a, added a regular
host-file-only, 1 MiB capped reader for exact complete ENTRY/RETURN or ENTRY/ERROR
lines. Rejects ambiguous sequence qualification and never echoes raw transcript.
Three tests cover valid pairs, privacy, partial/reordered/repeated/corrupted markers
and the size cap; full 293 host tests pass. No physical acquisition, serial port,
helper or firmware execution. Next board-specific acquisition and restore
provenance remain open under #106; existing board-record question pending.

## 2026-10-27 — Source-level writable restore prerequisites (#315)

At cached kernel e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74, inspected exact git
objects for MMC block/core/header definitions. Retained whole-source SHA256 and
reviewed ranges in evidence/restore-write-protection/report.json. Host force_ro is
not a card unlock; power-lock setter can return input count despite logged switch
failure; cached partition selection is not independent readback, and initial
user selection tolerates EBADMSG. Matching backup bytes therefore leave writable
post-failure restoration unqualified. No device/sysfs/helper/firmware operation.
Next actual board/capture/restore provenance under #106; existing question pending.

## 2026-10-27 — Retained-console source route (#317)

Inspected cached kernel e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74 exact git objects:
ARM64 douglas config enables DRAM MTK RAM console; old-buffer copy and conditional
last_kmsg late-init form a possible retrieval chain. Stored source hashes/ranges.
Signature/size reset, allocation, conditional pstore branches and raw fallback
prevent treating this as proven retention or sanitized first-byte logs. No installed
binary match, cross-boot observation or device acquisition. Next actual config,
layout/retention and accessible recovery retrieval remain open under #106.

## 2026-10-27 — Exact stock ramdisk log-access policy (#321)

Inspected existing boot SHA8982fa50193acc764be69ee51027ee92e83614cee4b8235b07439d1f9e2db363
using component bounds, capped gzip and newc parsing only. Ramdisk 1492335 bytes;
decoded archive 2917376 bytes. Metadata receipt preserves hashes/line ranges.
Packaged init declares restricted pstore/last_kmsg and private copy permissions;
douglas init declares removing the copy. Actual action ordering/access/log survival
unverified. No raw upstream files/logs published and no execution/device access.
Next lifecycle and authorized retrieval evidence, independent of retained-memory
qualification. Repository/diff checks applied; no code changed.

## 2026-10-27 — Central recovery handoff (#324)

Corrected the checklist's stale 3024/3072-byte pre-marker-fix image reference to
explicitly supersede it with #312's 3000/3040-byte two-base receipt. Consolidated
source evidence and missing configuration, memory/retention, writable restore,
retrieval and board/UART prerequisites through #323. Existing owner board-record
question remains pending; no new physical request. No runtime gate closed.
Documentation-only repository/diff checks; next evidence provenance before any
concrete physical proposal, not additional marker/count work.

## 2026-10-27 — Owner board-record answer

Owner confirms no existing internal-board photos or PCB revision records. Removed
pending-question dependency from current hardware plan/checklist. Hardware planning
remains allowed, but no specific physical action is qualified/authorized. Next
source-qualify exact-generation mechanical/isolation evidence for a reviewable
inspection proposal; do not wait for absent photos or repeat the question. No
physical/runtime gate closed. Documentation repository/diff checks only.

## 2026-10-27 — Epic/Feature/Phase/Task beta delivery baseline (#343)

Reparented existing open scopes without closing hardware/runtime gates; created
concrete recovery, platform and QA admission phases/tasks. Added both boards'
Level/Delivery state fields and a Beta1 QA-admission milestone without invented
dates. Historical closed cards are reversibly archived, issues retained. Published
projects/delivery-plan.json and roadmap/workflow. Every PR now requires a real
Updates/Refs/Closes issue reference; parser rejection tests cover template examples,
missing issues and PR substitutions. Existing open PR descriptions linked to issues.
Main release policy remains unchanged. No device action or runtime pass.

Verified all41 native hierarchy nodes/parents; both boards now expose hierarchy,
phase gates, ready tasks and blocked tasks. Archived137 historical closed cards.
PR linkage check passed in actual GitHub run40525664117; added it to development
and main required checks, preserving strict mode and existing contexts. Issue forms
and checked-in taxonomy now support Epic/Feature/Phase/Task. All runtime gates stay
open; no beta date fabricated. Source audit history and linked PRs remain accessible.

Added phase352/tasks353–354 for the existing first-party license hold and exact
beta redistribution/source-obligation review. These are blocked policy inputs,
not permissions inferred from CI. Total current delivery map44 nodes; Android
and optional Crestron QA gates remain separate.

## 2026-10-27 — Cover-only inspection review proposal (#345)

Prepared a concrete review artifact in HARDWARE-EVIDENCE-PLAN.md using the
firsthand exact-generation cover account and actually viewed supplier frames.
Explicitly records video identity conflict, unknown connector mechanics and
energized-battery boundary. Scope is identification-only with observable stop
conditions/privacy handling; no physical action is approved. Updates345, not
closure: owner/operator review and exact mechanical safety remain unresolved.
Next independent work339 QA matrix while review/source gaps are pending. CI/PRs
inspected healthy; no device/helper/firmware action or new audit micro-issue.

## 2026-10-27 — Beta QA test definition (#339)

Defined admissionA01–A07 versus campaignQ01–Q04, recovery/log/memory-first
preconditions, proposed measured smoke thresholds, stop conditions, result format
and S0–S3 defect triage. All device cases NOT RUN. No test execution or physical
procedure authorized. Inspection345 remains pending review; matrix is independent
planned work under phase338, not a new micro-issue. Phase/beta admission remains
open. Documentation community/repository/diff checks applied.

## 2026-10-27 — Original douglas route and full/minimal correction (#347)

Broader search reached original XDA via browser despite text-fetch502. Read author
post80154797, maintainer90487831/90490714 and fallback90488396; recent failure
reports corroborate wrong brick/minimal pairing. Static full launcher inspection:
54bytes, SHA c7c93a2aff2b17bb2cd9fd1a90fcea7ac22699986f14c445d434668e56126799;
65557 response bytes within128KiB cap. Cached main non-minimal guards corroborated;
no upstream code copied publicly or helper executed. USB-first candidate now gets
priority, cover review is fallback. Exact-build execution/restore/log gates remain
open. Owner Linux host available (private alias excluded); second desk tablet is
Fire7, generation unknown and outside douglas route. Next original-package match
and full-stage write/restore inventory, not more case-only audit waiting.

## 2026-10-27 — Full-stage write/escrow boundary (#347/#346)

Static AST/range review of cached main SHA0fc1e6b2455503c98ccfd5954174f701e6b2011f85f30d6aa5e40ee842df13d5
found zero dump_binary calls in main and GPT writes before later region/security
checks. Retained full/shared write stages and readback limitations; no atomic
rollback or exhaustive imported-helper claim. Explicit preservation decision
required before any destructive test; Linux availability is not permission.
No device/helper execution. Existing tasks updated; no audit micro-issue created.

## 2026-10-27 — reconcile recovery route and host prerequisites (#347)

- Source baseline b51c24f1655a18890fb5422c09716aad21dab373; latest three CI
  runs successful, open PR11 is the dependency update.
- Corrected the main recovery plan's stale read-back-first and native-Mac
  prerequisites to the current original-author USB-first candidate and verified
  Linux tool inventory. USB transport, exact-build entry, restore and logs remain
  untested; no tablet, helper, service or firmware operation occurred.
- Owner approved original archives under a combined 31 MiB cap. Browser retrieval
  timed out, attachment navigation was blocked by client, and no archive was
  found in the approved output/download/temp locations checked. Approval is no
  longer the blocker. Next: original package identity and preservation decision;
  do not treat cached mirror hashes as original attachment verification.

## 2026-10-27 — stock-return reachability audit (#346 / #347)

- PR359 passed all five checks and merged to development.
- Read cached return-to-stock.sh and functions.inc at Git revision
  2d8a4e6f73d9dab42d313c9cd751802b23ea7d31 using nl/rg and SHA256; no
  source/import/helper execution. Retained metadata-only source receipt.
- Found ADB/root dependency, unbounded root fallback, reconstruction from current
  GPT rather than complete original escrow, and no selected-script post-write
  readback. Reboot request is not observed recovery. Original ZIP identity and
  independent failure-return remain unresolved. No tablet access occurred.

## 2026-10-27 — GPT return preservation boundary (#346)

- Baseline63d946a742d0ff1d44f9c857925755bdbbe9fceb after PR360 merged with
  all five exact-head checks successful.
- Read pinned modules/gpt.py ranges82–112,147–174,222–240,271–273,305–318;
  SHA256bef85112cecc80a96b72d47688ebd90951524c923a2ad74d9fbb7d92fd7c8fa7.
  No vendor code imported/executed. Metadata receipt records reconstruction
  assumptions, compacted empty slots and lack of original-sector comparison.
- Approved original attachment normal GET: curl --fail --location --max-time30
  --max-filesize19000000 to ignored out/recovery-originals: HTTP403, no saved
  ZIP. Browser/client bypass not attempted. Next original archive acquisition
  and independently reachable restore; no hardware/runtime gate closed.

## 2026-10-27 — offline original-archive intake (#347)

- Baseline7ab0e8de7f264729f028c1af8f868596fe157968 after PR361 passed all
  five exact-head checks and merged. Original archive directory remains empty.
- Added owned scripts/inspect_recovery_originals.py: local files only, combined
  31MiB cap, selected-content limits, SHA256/receipt comparison, missing entries
  and unverified origin/restore flags. No extraction, helper import or execution.
- Script SHA256: 8e3b67da0e91aabb518201f0f832e9069ed8e325019e9085e65d8b4b56064034.
- python3 -m unittest discover -s tests -q:299 tests passed, including hostile
  path/canonical duplication, compressed oversized selected entry, input symlink,
  combined budget and synthetic identity/non-execution cases. Repository guard
  against the exact baseline and git diff --check passed. Real originals remain
  unavailable; next run intake and original provenance review when supplied.

## 2026-10-27 — packaged retained-log lifecycle (#348)

- Reparsed cached stock boot SHA2568982fa50193acc764be69ee51027ee92e83614cee4b8235b07439d1f9e2db363;
  bounded gzip/newc walk under16MiB, decoded cpio2,917,376bytes. Own inspection
  command retained at ignored out/stock-log-lifecycle/inspect.py and report.json.
- Matched packaged file hashes to prior stock-log-access receipt. Assigned each
  declaration to its actual on-trigger: removal post-fs, copy post-fs-data.
  Traced packaged import declarations; no runtime property/event order inferred.
- New sanitized lifecycle receipt records hashes/ranges and all runtime flags
  false. No ramdisk execution, helper execution, raw log read or tablet access.
  Next exact backend/retention/access evidence; physical task348 remains open.

## 2026-10-27 — retained-console reservation proof (#348)

- Inspected pinned legacy generic FDT reservation and ram-console callback paths;
  verified the five inspected files have no working-tree diff despite unrelated
  preexisting case-collision changes elsewhere. Exact source hashes/ranges in
  evidence/retained-console-route/reservation-path.json.
- Fixed-reg first node remains saved on reservation failure; logging-only console
  callback can return success later. Callback/init banners cannot independently
  prove successful reservation. No runtime failure inferred or gate closed.
- Prior static config/candidate-region comparison receipt retained privately at
  out/stock-log-config/reservation-crosscheck.json. Original archives still absent.
  Next actual reservation/retention evidence and original package verification;
  no helper/firmware/device execution or source-tree mutation occurred.

## 2026-10-27 — offline legacy-console ring decoder (#348)

- Baselinefd5af92 after PR364 merged with all five exact-head checks passed.
- Reviewed legacy header/writer/reader layout at pinned sourcee0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74,
  ram-console source SHA256cc57dd6936a85f40fb59ded3ee45f66db7ee9dc6dbc415b1c4049591ac66779e;
  lines98–119,300–340,464–472. No upstream code imported/executed/modified.
- Added owned bounded host-file decoder with chronological hashes and no raw log
  output. Rejects counter underflow, invalid partial cursor and corrupt bounds.
  Origin/freshness/layout/retention/boot flags remain false; synthetic data only.
  Decoder SHA25673e002fd34b003bbd29420a958d356671c90323b573ce3dae6203391d1d48fab.
- python3 -m unittest discover -s tests -q:302 pass; repository guard against
  current development and whitespace check pass. Next approved supplied legacy
  buffers, not live acquisition; original ZIP intake remains blocked on files.

## 2026-10-27 — original package restore review (#347 / #346)

- Base0cd1594 current development; open dependency PR11 only, latest CI healthy.
- Original post attachments acquired through normal Chrome clicks, combined
  31,461,609bytes within approved31MiB cap; ignored ZIPs preserved locally.
  All eight prior selected mirror comparisons equal; launcher and cached
  functions/GPT/return script hashes match. No archive helper import/execution.
- Ran owned inspect_recovery_originals.py with pinned mirror receipt; streamed
  all non-directory entries through SHA256/ZIP CRC with128MiB per-entry and
  300MiB aggregate local caps (actual272,362,922bytes),1MiB chunks. Own
  inspect_boot_image.inspect parsed supplied recovery/TWRP bytes without execution.
  Exact hashes/layout/source URLs in original-package-review.json.
- Reviewed original launchers, main/common/load_payload and return dependencies.
  Found stale minimal-stage continuation, discarded write-size bound and
  unacknowledged selector method; opaque payload effects remain unproved.
- Original return package is recovery+script only, not full-state rollback.
  Packaged recovery kernel differs from current-stock boot kernel. Recorded
  reviewable effects, failure stop boundaries and remaining owner/physical gates.
  Next actual write geometry/binary and independent return/log qualification;
  no tablet/firmware/helper action occurred.

## 2026-10-27 — original write geometry and failure boundaries (#347 / #346)

- Baseline5c5f23c8dfd2a05de2aa4f4bfaccd4e260c500a5; no new feature PRs pending.
- Added owned pinned-metadata arithmetic audit. Selected boot0 extents disjoint;
  declared0x37000-sector exploit slots fit header/payload with560,640bytes slack.
  Actual GPT/target geometry still unknown; source helper's dropped bound remains.
- Sanitized internal-only block sizes from already authorized cached report
  SHA256f8521045dd891c20ea01a4baec9a3117edf6035a801b865fa2aeab5d8fe8f79a.
  No SD/household/device identifiers published. Kernel-reported sizes are not
  independently acquired EXT_CSD or GPT-name/address proof.
- Read cached native selector/RPMB dispatch source; exact hashes/ranges retained.
  Selector prints status without framed host acknowledgement. Shipped native
  binary/source equivalence unverified; no build/import/execution.
- Recorded pre-mutation, cleared-header, changed GPT/security and restored-header
  failure boundaries. No independent physical exit or original-state rollback
  demonstrated. Next exact selection/geometry and reachable return/log evidence.
- Validation:304 host tests pass; community/link, repository guard against exact
  baseline and staged whitespace checks pass. No runtime test was performed.

## 2026-10-27 — source-qualified minimal partition metadata (#347)

- CI healthy, open dependency PR11 only. Located cached proc partinfo source at
  pinnede0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74. Read-only0444 file reports
  names/start/size; source synthetic pgpt/sgpt rows are not raw backup GPT proof.
- Added partinfo to existing owner-run bounded metadata collector; no live run.
  Injected reader test covers available output and legacy zero-exit denial,
  absence of raw block reads or su fallback. Source receipt retains hashes/ranges.
- Prepared exact targeted read for separate owner review; actual availability and
  permission still unverified. Next approved supplied layout record, not another
  automatic device query. No tablet/helper/firmware activity occurred.

## 2026-10-27 — owner-approved named layout evidence (#347 / #346)

- Owner connected douglas, added plugdev membership, installed a narrow USB-mode
  rule and authorized the ADB host. Agent restarted only the account-owned host
  ADB server to clear cached permission state; no tablet reboot occurred.
- Authorized targeted property reads confirmed Amazon/KFDOWI/douglas.
  proc partinfo missing:64-byte error SHA256f33c257060bb942bb0298adb5b2aa67591e22a869092a04fbcec279e979e4b11.
- Read only sysfs mmcblk0 partition start/size/uevent metadata using a fixed shell
  loop, no root or block-device reads. Private2258-byte capture SHA256
  8bb1c0b3f59f89de6741c8069cdb9b83d8c9abf9f22668d9d8dbf20183f4a398.
  Published only normalized internal partition fields, no serial/host/household data.
- Offline assertions:16 unique consecutive-numbered/nonoverlapping named ranges;
  original LK/TEE/TWRP/recovery sizes fit reported capacities. Large-offset exploit
  payload does not fit original boot/recovery. Conditional source GPT projection
  shrinks userdata231,194,112bytes; no storage changed. Raw GPT/security escrow,
  selector and reachable failure-return/log qualification remain open.
- Baseline8d0a520d7cd102e1e971590690ad3c3635b4c9d9. Next independent failure
  return/logging with explicit preservation limits; automatic tablet access remains
  prohibited even while connected.

## 2026-10-27 — actual restore/log accessibility (#346 / #348)

- Owner requested restore and log qualification after named-layout capture.
  Verified douglas identity, current659664620/PL7/LK3/TEE262 via targeted properties.
- Read only shell identity, permission metadata, user sysfs capacity, bounded
  current dmesg attempt and exact SYSTEM_LAST_KMSG diagnostic archive metadata.
  No raw blocks, protected copied log contents, root, reboot or helper execution.
- dmesg denied; last_kmsg metadata denied; pstore/config.gz missing. Copied log
  exists0600/system but was not read. Tag-filtered archive query returned no entries.
  Exact sanitized receipts in observed-restore-log-access.json; raw outputs ignored.
- Downloaded32133-byte official AOSP5.1.1 DropBoxManagerService source to inspect
  tag filtering/DUMP gate before targeted query; no broad bugreport or app logs.
- Asked preservation requirement for current unit as a planning decision only:
  expendable/wipe/security changes versus preserve current data/state. Next target
  determines restore acceptance; no consent to firmware execution inferred.
  Both branches still require credible failure exit and independent log path.

- Owner replied wiped test unit acceptable. Updated current acceptance target:
  supported-stock return and independent logs; original-state preservation no
  longer required for this unit. Planning only, no execution approval inferred.
- Inspected exact-build OTA updater-script/ota.prop/system-devicepath via strict
  ETag/size-pinned ranges,512KiB cap,66,411bytes actual. Full OTA907,705,758bytes
  remains undownloaded/unauthenticated; selected script writes system,boot,LK,TEE
  and preloader aliases but does not explicitly restore recovery/RPMB. No updater
  binary execution. Next full-package resource gate and independent failure/log path.

## 2026-10-27 — approved full stock OTA verification (#346)

- Owner explicitly approved full866MiB stock download. Streamed exact907,705,758-
  byte Amazon object under910,000,000 cap, checked pinned ETag/status/encoding,
  saved ignored stock-return file; SHA2566e70792b002d5274286a8cd7e66da4b80e748a545b3303ab466795548d00f9ab.
- Parsed OTA footer/EOCD with duplicate-marker rejection. Detached DER1553bytes,
  signed prefix907,704,179bytes. OpenSSL4.1.0 CMS -verify -binary -inform DER
  -content /dev/stdin -noverify:success; no PKI trust inferred. Stream-only one-byte
  mutation correctly failed(exit4); original file unchanged. Own scripts and exact
  local receipts under ignored out/stock-return/signature/.
- Compared original return-recovery res/keys material to embedded signer:
  modulus/exponent3 and SHA1 profile match, n0inv/RR consistent. Bounded16MiB
  gzip/newc read; no image code execution. Candidate/installed trust kept distinct.
- Primary AOSP verifier source fetched at exact ec63d564a86ad5b30f75aa307b4bd271f6a96a56
  after a requested historical mirror URL returned404;11,291source bytes, retained
  hash/ranges. No binary/helper run or tablet access. Next recovery acceptance,
  failure entry/return and independent logs; task346 remains open.

## 2026-10-27 — cached exact-build recovery reconstruction (#346)

- CI healthy; dependency PR11 only. Owner stock-recovery entry/return approval
  remains pending; no device/USB query or reboot during this automatic run.
- Verified9 target-blocklist component hashes/lengths by bounded local streaming;
 1,543,191,816unique bytes under2GiB cap, no new downloads. Built local sparse
  analysis filesystem from new ranges with signed system caremap digest agreement.
- Owned bounded ext4 prototype found install-recovery.sh, recovery-from-boot.p
  and recovery-resource.dat; exact file hashes/sizes in reconstruction receipt.
  Read470,262bytes under64MiB cap, no mount, script/helper execution or raw-device
  access. Local prototypes/reports remain ignored system-inspection output.
- Script declares exact current recovery9,299,968bytes/SHA18e5e7f6f63fd77383c5721a13d818f880a1e70c9
  from exact stock boot plus patch/bonus. Packaged init.rc726 declares main-class
  oneshot flash_recovery service; class startup declarations are not execution proof.
- Source/asset-location gap resolved; exact patched bytes, live service acceptance,
  reachable post-failure return and usable real logs remain unqualified.

## 2026-10-27 — exact recovery result-byte verification (#346)

- CI healthy, dependency PR11 only. No owner recovery-mode approval received;
  automatic run did not access, enumerate or reboot the connected tablet.
- Read bounded primary AOSP IMGDIFF2 format source at
  b31f9ce6d150a264f584d9b38a54da0723fc249c; hash/URL retained in receipt.
  Implemented owned bounded file-only BSDIFF40/raw/deflate+bonus decoder; did not
  execute vendor applypatch/installer/unlock helper or mount a filesystem.
- Actual pinned inputs produced9,299,968bytes/SHA18e5e7f6f63fd77383c5721a13d818f880a1e70c9,
  exactly the signed OTA recovery target. SHA2564de74a18736f3652a96db33453b230b72b91a7dbbec7a4d046ee5c9408a167e2.
  Rechecked output bytes and boot-component layout; exact-stock kernel matches,
  size fits owner-reported recovery,2KiB trailer remains unclassified.
- Added malformed-format/capacity and exclusive publication controls; pinned
  output verification precedes fsync/exclusive host publication. Binary stays ignored.
  Next owner entry/return observation and independent failure/log qualification;
  no runtime hardware gate closed by this artifact result.
- Validation:309 host tests pass plus actual signed-target reconstruction and
  component/size checks; repository/community/link and whitespace guards pass.

## 2026-10-27 — exact recovery USB/log observation contract (#346 / #348)

- CI healthy; dependency PR11 only. Stock recovery-mode approval remains pending;
  no tablet/USB/network query or mode change in this automatic run.
- Bounded gzip/newc inspection of verified exact recovery records default.prop,
  recovery init, key file, adbd/recovery literals and fstab hashes under16MiB cap.
  Secure/nondebug defaults plus disabled adbd/conditional startup mean a normal
  shell must not be assumed. Static log menu/path literals are not runtime access.
- Exact current recovery res/keys hash equals the already checked bundled key
  file; candidate signer-material alignment persists, installed image not verified.
- Updated pending observation expectations: owner screen labels/ordinary return,
  no sideload/update selection or policy weakening to manufacture shell access.
  Raw static file data and private inspection script retained under ignored
  out/stock-return/recovery-inspection; public receipt is normalized metadata.
  No recovery/adbd/firmware/helper execution and no physical gate closed.

## 2026-10-27 — owner-observed stock recovery entry and ordinary return (#346/#347/#348)

- Owner explicitly approved the interactive recovery mode test. Identity reads
  confirmed douglas/KFDOWI and exact incremental build659664620.
- Command `adb reboot recovery` exited0. Private photo confirms stock recovery
  menu and view-recovery-logs label. Owner selected reboot-system and reported
  normal screen. Published only normalized metadata and source-photo SHA256.
- No firmware/helper execution, OTA upload, wipe or installation. Ordinary
  return passes; experimental failure recovery, OTA acceptance and usable
  retained boot-log capture remain untested. Next: owner log-view observation.

## 2026-10-28 — actual stock kernel log text observed (#348)

- Owner photos show recovery log selector and readable early kernel output.
  Published normalized text/photo hashes only, no raw household imagery.
- Actual visible low-level log reservation is128KiB at0x44600000, distinct from
  the legacy console candidate0x44400000. No freshness/backend format inferred.
- Interactive owner-approved adb get-state returned no device; narrow USB
  vendor enumeration found none. No bytes pulled. Owner cable reseat pending.
- No tablet actions in this automatic run. Full log/failure capture and physical
  UART qualification remain open. Source revision95df19f36e1b8f9134900a0525ae63896919f5ed.

## 2026-10-28 — targeted USB recovery-kernel archive export (#348)

- Owner returned to Android; interactive identity read reconfirmed douglas and
  build659664620. Tag-only --file listing367bytes; --print text663874bytes,
  SHA25625a703e1315c636794d26a586153d4051f4569bbf008e429eccff197bd3ba256.
- Two archived kernel entries; second matches five photographed markers. Both
  have trailing truncation markers, despite no local1MiB cap hit. Full log and
  exact session freshness not qualified; no experimental failure tested.
- Published normalized metadata and repeatable scoped procedure, raw text kept
  ignored/private0600. No broad bugreport or firmware/helper/security changes.
- Automatic run only analyzed supplied/captured local evidence, no tablet access.
  Next offline truncation/attribution investigation, then failure lifecycle gate.

## 2026-10-28 — reconcile acquired kernel layout with DT memory (#348/#106)

- Offline strict selected-line parsing of acquired second kernel archive entry;
  three PHY banks plus named ATF/consys regions form a contiguous partition of
  earlier DT usable banks. Kernel total1462080KiB plus2240KiB ATF/consys equals
  DT1464320KiB. Dynamic consys actual address0x98400000 now observed.
-2MiB console declaration/buffer initialization observed; old-valid contents and
  experimental retention remain unqualified. Top106MiB owner remains unknown.
- Normalized interval arithmetic asserts pass; no raw logs or household fields
  published and no tablet access during this automatic run. Next failure-lifecycle
  qualification, preserving truncation/freshness limits.

## 2026-10-28 — prevent blocked-task idle loops (#106)

- Owner requested a standing executable/fallback queue after repeated waiting
  turns. Added [active work queue](development/ACTIVE-WORK-QUEUE.md) with ordered
  tasks, acceptance criteria, current evidence and explicit external gates.
- Updated the existing heartbeat instructions: active work continues within turns;
  pending CI/owner input triggers independent queued work, not repeated polling.
  Preserved15-minute recovery trigger and meaningful-only notifications.
- Reconciled stale blanket device prohibition with owner standing low-brick-risk
  lab permission; high-brick-risk and large/paid resource gates remain.
- Current queue starts with exact320KiB truncation-stage investigation, then boot
  attribution, bounded loader-return rehearsal, diagnostic handoff and dependency-
  ready board work. No outstanding cable/photo/Android-return request.

## 2026-10-28 — identify packaged320KiB recovery archive collector (#348)

- Bounded static DEX instruction walk located BootReceiver in exact cached oat;
  user LOG_SIZE65536 and recovery last_kmsg call positive*5 feed unchanged maxSize
  into FileUtils.readTextFile with truncation marker. Both acquired normalized
  payloads equal327680bytes. This identifies packaged collector sizing.
- Initial private assertion used the wrong slice for final initializer words;
  corrected to last3:-1, then initializer and call-site word assertions passed.
- Public receipt contains hashes/offsets/semantic review only, no raw logs or DEX.
  Private purpose-specific parser is not a general verified disassembler; installed
  equivalence and cache-file completeness remain unverified. No device execution.
- Queue item1 source scope complete; next item2 archive attribution/coverage, then
  loading-return rehearsal. Do not repeat the same archive read for missing bytes.

- While archive-limit PR CI ran, queue item2 attribution/coverage analysis completed:
  second entry0..29.865148seconds/photo-consistent, first nonmonotonic. Collection
  Build/Kernel headers do not establish retained-boot identity. No tested
  experimental boot/failure and no lexical panic absence promoted to success.
  Normalized receipt updated. Next executable item3 loader-return rehearsal.

## 2026-10-28 — concrete loader/return rehearsal and diagnostic handoff (#346/#347/#348/#340)

- Queue3 source plan complete: R0 stock baseline passes, R1/R2 explicitly gate
  compatible bounded entry, region identity, independent failure return and
  attributable capture. First persistent effects and each unqualified exit are
  identified. No firmware/helper/electrical trial scheduled or approval requested.
- Standing low-risk read reconfirms douglas/build659664620 and boot_completed=1;
  direct cache/recovery/last_kmsg metadata denied and readability false. Captured
  normalized permissions only; no source log/raw block read or mode/security change.
- Queue4 source-review index complete with authenticated material, observed stock
  behavior/partialUSB capture, generic results and release/runtime gate separation.
  This does not close beta package/QA or high-risk recovery acceptance issues.
- Next executable queue5: select dependency-ready board task after live acceptance
  review; independently investigate one actual remaining R1 route prerequisite.

## 2026-10-28 — unresolved HDMI parent/consumer distinctions (#29)

- Selected live board task29 while recovery R1/R2 remain blocked. Reviewed pinned
  overlay/donor/legacy constructors and captured literal DT references.
- Legacy HDMI APLL aliases are1:1 aud_2_sel factors; captured audio uses distinct
  actual aud_apll2_div0 divider (shift28,width3,gate1,reg0x05a0). No substitution.
- Legacy CTS ends in clk_null; no valid hardware source/rate demonstrated. Captured
  direct DSI refs have different immediate edges, but no whole-board irrelevance
  inferred from absent literal HDMI/DPI refs. No provider behavior changed.
- Next trace matched CCF/non-DT consumers and HDMI PHY ownership/rates, then bound
  unavailable paths or implement valid relationships with compile evidence.
  Runtime support remains untested; project/issue stays Active with current result.

- During PR CI, traced actual legacy HDMI C probe and DT consumer: all named
  clocks requested with devm_clk_get and BUG_ON lookup failure. Legacy DT includes
  HDMI gates absent from captured candidate. Preserve PIXEL/PLLCK phandle/name
  ordering discrepancy; no validated driver mapping or hardware rate inferred.

## 2026-10-28 — matched HDMI PHY ownership and unavailable-consumer policy (#29)

- Donor directory metadata pinned; first source acquired then raw endpoint429.
  No immediate repeat. Read16195bytes from official matched ACK source; common
  probe/header Git blobs equal pinned donor, MT8173 implementation does not.
- Common provider needs real pll_ref, output name and matched PHY; supports
  MT2701/MT8173/MT8195, no MT8163 entry. Captured candidate has no HDMI PHY output.
  Legacy direct mode/deep-color PLL programming is not a fixed CTS rate proof.
- Existing CI audit now rejects7 unresolved dependent literal DT consumers while
  allowing real DSI/audio divider.3 targeted rejection tests added; no provider
  register/gating behavior changed. Full host/check results recorded with PR.
- Next evaluate exact aud_2_sel direct-parent equivalence for two legacy aliases,
  separate from unqualified CTS source. #29 remains Active; no hardware claim.

## 2026-10-28 — resolve real HDMI audio/SPDIF parent references (#29)

- Contracted two missing legacy ungated1:1 aliases to actual aud_2_sel in MMSYS.
  Gate IDs, bits11/12, registers and ops unchanged; no fixed rate or audsys divider
  substitution. All7 unqualified HDMI consumer restrictions retained.
- Textual orphan set now only hdmitx_dig_cts, still explicitly unavailable behind
  matched PHY/rate gate. This source change does not claim runtime HDMI/audio.
- Appropriate host/policy checks plus existing bounded generic kernel compile
  workflow are required before merge. No tablet/firmware operation.

## 2026-10-28 — exact topckgen binding coverage during provider compile (#27)

- #29 provider parent fix PR384 generic compile running; selected independent27
  cached exact-compatible work and synchronized issue/project/parent active state.
- Uncached MMSYS source request429; did not retry or invent its driver contract.
  Cached topckgen driver matches standalone MT8163 DT tuple; opt-in locked schema
  adds only that value. Actual full corpus53diagnostics (41unmatched/12validation),
  target unmatched removed, no added diagnostic; wrapper exit1 preserved.
-7 processed tuple controls pass; all non-compatible constraints exactly preserved.
  First extraction expected an id#suffix that processed corpus omits; corrected
  lookup before controls. No claimed full schema pass/runtime support.
- Next cached infracfg compatible/reset contract while exact-head provider compile
  continues. Raw source request limits do not block independent cached work.

## 2026-10-28 — infracfg compatible and required reset contract (#27)

- Continued independent source work while PR384 generic compile runs. Added
  opt-in exact MT8163+syscon and reset-required branch matching actual driver
  descriptor/probe. Two banks0x120/0x140; captured clock/reset cells1.
- Actual cached full corpus52diagnostics (40unmatched/12validation), target node
  unmatched removed with no added diagnostic; full wrapper exit1 preserved.
-11 processed-node controls pass, including missing/wrong reset rejection and
  preserved existing MT8173/MT8167 policies; all other constraints unchanged.
- Initial string replacement caught overmatching indentation before file writes;
  regenerated by exact complete-line identity and verified two enum additions.
  No runtime support claimed, no device/new corpus operation.

## 2026-10-28 — exact PLL binding and provider-instantiation gap (#27/#18)

- Added opt-in standalone apmixedsys compatible matching actual PLL probe/DT;
 9 processed-node controls pass, other constraints unchanged. Full cached corpus
 51diagnostics (39unmatched/12validation), target removed/no additions; exit1.
- Complete profile name exceeded255-byte component limit; preserve existing short
  names, hash long exact profile names with fullSHA256.3 path tests and actual
  compact-name full-context run pass. No new corpus/device operation.
- Small official ACK MMSYS parent source read15830bytes: no MT8163 match; child
  clock driver uses platformID clk-mt8163-mm and current port patches do not add
  parent creation. Generic compile is not provider instantiation. Recorded against
 18; needs matched SoC parent/routing/reset integration, not another schema count.
- PR384 still compiling; source work continues independently. Next actual parent
  integration investigation; never copy DRM display-path data into SoC match data.

## 2026-10-28 — four direct gate-provider exact contracts (#27)

- While actual parent fix compiled, qualified IMG/MFG/VDEC/VENC exact OF/syscon
  tuples against cached common schema and direct simple-probe drivers. New nodes
  require register mapping; old power-domain conditional preserved unchanged.
- Actual full cached context47diagnostics (35unmatched/12validation),4 target
  unmatched removed/no additions; wrapper exit1 preserved.31 processed-node
  controls pass, no media/GPU/runtime qualification implied.
- PR384 full generic Image and QEMU passed at18f2d5b; GitHub reports merge conflict
  after independent documentation/schema merges. Next resolve history, verify
  all compile inputs unchanged, and run required checks on final merged head.
  No unnecessary repeat full compilation of unchanged inputs is claimed as new.

- Generated patch context blank lines initially triggered whitespace diagnostics;
  reformatted context without altering applied YAML, verified isolated git apply
  output identity and reran full cached profile (47diagnostics/exit1 unchanged).
  Whitespace checks now pass before the correction commit.

## 2026-10-28 — actual parent-fix compile and merge-history resolution (#29)

- Generic compile/QEMU run40755681118 passed at18f2d5b. Image SHA256
  d7eb0fa46d5fe5141bcce9d9c48e774a15ce6cf9796efdd1c85005e6202942d9;
  config6a4c801a15e3e210948ccf7053bff6b83caffdcae5a431054af3dad1ed0ff8d5.
- Independent source work merged while compile ran. Resolved WORKLOG-only conflict
  preserving both histories;48 relevant build inputs match compiled revision byte
  for byte. No duplicate full compile of unchanged inputs claimed; final-head
  required repository/traceability/evidence checks rerun before merge.
- CTS remains deliberately unavailable behind tested consumer guard. Missing
  MMSYS parent creation is #18 integration, not corrected by generic compilation;
  no actual board boot/audio/HDMI or failure-return gate is closed here.

## 2026-10-28 — real MMSYS parent connection (#18)

- PR388 merged at532c20d after five exact-head checks;315 host tests passed.
- Acquired pinned routing header4157bytes/SHA256
  16a2ab928d4395a4b2463991c34e586ec39359143779cbfe26ab1a1221459489
  and reset header1489bytes/SHA256
  9fac0dd783e907ac8fdbbf1a32b660d18d890f828cff61f40ccc62e9b1f9802f.
- Added exact donor SoC descriptor/match and clock-child creation path via a
  hash-locked patch against ACK d9318bdb. Subsequent captured-consumer review found
  donor raw64 reset IDs conflict with compact DSI23. Corrected descriptor uses
  the34-entry map (DSI23 -> bit24); legacy LCM0x150 corrects donor bank2 to4.
  No DT consumers added. Original donor headers retained unchanged in evidence.
- Explicit MMSYS parent-object build now required. Isolated patch apply/hash
  check and reapply rejection pass. Generic Image/parent compile next via PR CI;
  board probe/reset/routing and failure recovery remain untested.

- Initial run40762643646 failed before C compilation: ACK modular CMDQ bounds
  MMSYS to module state. Pinned Kconfig confirms dependency; generic parent
  experiment disables CMDQ and requires MMSYS=y, preserving diagnostic isolation.
  Corrected-head run required; initial failure is not an Image result.

## 2026-10-28 — matched MMSYS schema during parent compilation (#27)

- PR389 parent integration is compiling independently. Cached ACK proposal adds
  exact MT8163 MMSYS/syscon tuple only; original constraints preserved structurally.
- Full profile46diagnostics (34unmatched/12validation), one target unmatched
  removed/no additions, wrapper exit1. Eleven processed-node controls pass.
  No source corpus download or device action. Does not prove reset IDs or probe.
- Next complete exact-head parent build/reset review under #18; full schema and
  actual device/recovery acceptance remain open. All evidence hashes and full
  profile command retained in evidence/mmsys-binding.

## 2026-10-28 — GPIO/EINT bank source acceptance (#19)

- While #389 builds, reviewed pinned ACK EINT17013bytes/SHA256
  c4c2fbdd4a34aa09c0db698328d7bcd80eaedfd98765392f37cdcf5a2ce92e39.
 18 register offsets,13 shared geometry fields and both masks match legacy/donor.
- Source-drift rejection controls cover changed EINT ACK address and AP capacity.
  Existing155 descriptors/15 mux references still checked; no runtime claim.
- Captured DT lists three parent SPIs; both ACK and actual legacy Git blob select
  index0. Inherited behavior, no new regression established. Parent-line ownership,
  delivery and GPIO87 input-enable delta remain unqualified. Next #18 actual
  compile result and #27 full binding work; no physical request is outstanding.

## 2026-10-28 — real pinctrl/EINT probe prerequisites (#27/#19)

- Exact MT8163 pinctrl tuple plus required reg/syscon/EINT/IRQ/cells declaration
  follows actual common probe. Old SoC/pin-group policies preserved structurally.
- Full cached context45diagnostics (33unmatched/12validation), one target removed,
  none added, wrapper exit1.19 controls use actual dtschema Draft201909/typeSize
  validation and four local processed dependencies, including phandle-array bounds.
- Parent IRQ delivery and GPIO87 remain unqualified; source matches do not close
  hardware gates. #389 real MMSYS Image build remains active, #391 bank audit
  merged after six exact-head checks including pinctrl object compile.

## 2026-10-28 — actual MMSYS parent/Image result (#18)

- Run40763077737 passed explicit MMSYS parent object, full generic ARM64 Image
  and QEMU diagnostic smoke at5c02907; MTK_MMSYS=y/CMDQ=n. No warning:/error:
  lines found in1481984byte private log; SHA256
  f80c5b785d16bd00dbdc72595ab26b1c68ce08860d59bf4455a98d32f2a8822d.
- Image SHA25627a9366144cf7e313af9132e94d75d3152cadb4bbc95739215e08c0d498f8436.
  Full artifact/config/QEMU receipts: evidence/clock-port/mmsys-parent/compile-result.json.
- Independent #390/#391/#392 merged while build ran. Verified all selected
  provider/source-lock/input/config/build inputs byte-identical to compiled head;
  no duplicate compile of documentation/schema changes claimed. Final-head checks
  rerun before parent merge. Actual device probe/reset/routes and recovery open.
- #27 exact pinctrl probe contract merged in #392; full context45diagnostics,
  not passed. Next executable dependency is #20 power/provider source integration
  review and matched schemas under #27; no physical action requested.

## 2026-10-28 — actual power/domain source contract (#20)

- Pinned legacy Git snapshots compare eight IDs,32 domain register/SRAM fields,
  three nonzero bus-protection masks and two status offsets to ACK plus the real
  candidate. All values match; original headers/provenance retained. Drift checks
  reject changed register/protection values and unknown expression guessing.
- Recorded two policy differences: eight legacy active-wakeup=true callbacks
  versus candidate capability absent; mfg clock moves from MFG to MFG_ASYNC.
  No runtime equivalence or voltage/order claim follows from equal bitmasks.
- Recorded concrete probe effects in diagnostic evidence index: available power
  domains turn on during registration; pwrap enables DCM/clocks and can reset/
  initialize transport if INIT_DONE2 clear. Experimental DT boot is not read-only
  log collection. No device/firmware/helper action or new download performed.
- Next: matched pwrap/scpsys/domain binding prerequisites under #27, plus source
  qualification of wakeup/clock-order deltas. Loading/independent return and actual
  hardware gates remain open; no owner cable/photo/approval action requested.

## 2026-10-28 — wrapper prerequisites and real PMIC parent-name failure (#27/#20)

- #393 power audit merged after six exact-head checks including object compile.
  Matched pwrap binding requires real reset/PMIC child and excludes bridge
  resources absent from MT8163 descriptor; old policies preserved structurally.
- Matching RDMA context first exposed two PMIC parent naming errors (46diagnostics).
  Retained failures; isolated parent rename candidate preserves all880 property
  and phandle values across186 nodes against RDMA. No DT baseline mutation.
- New candidate DTB26259bytes/SHA256
  b837e6cb439d43778527c834e534abddb271170fd29cb6b13b174272214d1411;
  zero compiler diagnostics. Full context44diagnostics (32unmatched/12validation),
  wrapper exit1.22 actual processed-node controls preserve original SoC policies.
- Added CI compile/property-equivalence gate and phandle/path drift controls.
  No transport/rail/device or failed-boot recovery qualification implied. Next
  existing source scope: matched scpsys parent/power-controller dependencies under
  #27/#20 and explicit qualification of active-wakeup/clock-order differences.

## 2026-10-28 — actual scpsys parent/child and bus prerequisites (#27/#20)

- Pinned ACK OF platform source22288bytes/SHA256
  5c670486e3ec04cfe976d40b3cd4758c2ae2abe2176551cba0a8b7b75a1a3c85
  verifies normal simple-mfd child-creation source path, not actual device probe.
- Matched parent/child proposals bound eight IDs, nested domain cell range and
  protected INFRACFG requirements. Reject modern access-controllers mode (SoC
  block count defaults0) and ignored domain supplies (capability absent).
-24 actual decoded-node controls pass; full cached context42diagnostics
  (30unmatched/12validation), two matched nodes removed/no additions, wrapper1.
- Fresh-DTB guard checks eight unique IDs, MFG under MFG_ASYNC, actual INFRACFG
  phandle and clock/name counts. Six drift tests include wrong target/flattened
  hierarchy/duplicates/disabling domains; no bypass to obtain a pass.
- Next queued source investigation: legacy active_wakeup callback versus ACK
  GENPD_FLAG_ACTIVE_WAKEUP mapping and explicit MFG clock-order rationale under
  #20. Hardware voltage/order/wakeup and failed-boot return remain unqualified.
  No device/helper/firmware action performed; one small pinned source read only.

## 2026-10-28 — observed stock clock ABI and transition-order gate (#20/#347)

- Authorized bounded normal-Android USB reads confirm douglas/known incremental/
  completed boot. Sysfs/proc DT properties agree: mfg/mm clocks<6 70 6 67>,
  topckgen phandle6/#clock-cells1. Raw data stays ignored; normalized receipt only.
  First head command was absent; rejected error bytes, cat+host bounds succeeded.
- Candidate IDs54/51 differ; candidate70/67 are SCAM/ATB. Added explicit fresh-DTB
  provider/ID checks rejecting stock IDs and wrong provider despite valid counts.
  Loader R1 must qualify actual matching DTB selection/handoff; no trial performed.
- Source MFG mux fields and unit-alias parent identities match, but clock ownership
  moves MFG->MFG_ASYNC. OFF reset/clock and ON/ON_2ND write orders differ. Literal
  traces/legacy Boolean models are not hardware or ACK implementation equivalence.
- ACK genpd implementation unavailable from capped pinned endpoints; cached header
  contract alone does not justify capability changes. Moved immediately to cached
  transition/clock analysis and safe ABI evidence; no root/reboot/helper/flash.
- Next queued source scope: #347 trace actual candidate DTB selection/handoff
  from cached LK/FDT/load artifacts (out/lk-instruction-audit, out/lk-fastboot-review,
  out/lk-bootargs), identifying exact artifact/revision and image/address/trust
  boundaries; do not equate original-route source with installed LK3. No execution.
  #20 wakeup equivalence awaits the pinned ACK genpd implementation, not just its
  header. Actual matching DTB handoff, independent failure return and logs stay open.

## 2026-10-28 — cached LK version-selection prerequisite (#347)

- Static exact-OTA LK trace anchors root version lookup, missing-property rescan,
  string equality and selected-suffix path; bounded excerpts/hashes published in
  evidence/lk-dtb-selection. Candidate b837e6cb root version is absent; stock
  variants are pre_evt/hvt. No guessed version or firmware execution.
- Reproduction command and exact input hashes: LK-DTB-SELECTION.md/report.json.
  Installed LK3 equivalence, selector runtime provenance, destination bounds, late
  fixups and actual failure return remain unqualified. Next executable source
  acceptance: trace these producer/fixup boundaries from cached artifacts.

## 2026-10-28 — FDT destination and late-write source boundaries (#347)

- Extended merged #397's exact-OTA static trace: header+0x20 supplies FDT r1,
  fallback constructs0x40000100; header+0xc remains the separate kernel address.
  Rounded suffix copy precedes the in-place open capacity limit of at most1MiB;
  pre-copy bounds/overlap and runtime addresses remain unqualified.
- Pinned /memory/reg and selected /chosen atag writes: input DTB contents are not
  assumed preserved. K64 call r1=r5 checked, complete intervening lineage/SMC and
  installed LK3 equivalence remain open. See LK-FDT-DESTINATION.md and bounded
  evidence/lk-fdt-destination receipts (same exact LK SHA256 as #397).
- Four host controls replay sparse evidence and reject instruction/reference drift
  or truncation. No device action, firmware/helper execution or new download.
- Next executable source acceptance: memory-tuple producer and reservation/PSCI
  callbacks, then complete selected FDT lineage/trust checks. Runtime loading,
  independent return and failure-log gates remain Blocked.

## 2026-10-28 — selected runtime memory layout and reservation metadata (#347)

- Pinned exact-OTA helper0x25ac4: runtime pointer-global0x4bd874c0, count+0x30,
  records+0x38/stride24; selected caller capacity4. Start/size become16-byte
  big-endian DT tuples. Runtime pointer writer and alternate branch unqualified.
- Callback0x25bbc copies original-DRAM/mblock/LCA/TEE metadata and adds framebuffer
  reservation from globals. Actual geometry/ownership and remaining PSCI/fixups
  unqualified. Evidence/lk-memory-fixups includes bounded excerpts/window hashes.
- Owned host tuple decoder and five drift/64-bit/boundary/truncation controls
  pass; no firmware execution or actual runtime decoding claim. Reproduce using
  LK-MEMORY-FIXUPS.md with cached exact LK hash; raw artifact remains ignored.
- Next executable source acceptance: pointer-global writer/lifetime, alternate
  tuple branch, remaining reservation/PSCI callbacks and selected FDT lineage.
  Experimental loading/return/log gates remain blocked; no owner action needed.

## 2026-10-28 — entry-r4 bootarg capture and local memory pointer (#347)

- Exact-OTA startup stores incoming r4 at linked0x4bd00020. Initializer0x23230
  assigns local buffer0x4bd87340 to pointer-global0x4bd874c0; matching0x504c504c
  magic selects384-byte copy from saved entry pointer. Slots/instructions pinned
  in evidence/lk-memory-pointer; complete tag conversion/lifetime still open.
- Absolute pointer store precedes conditional relocation copy; file pointer slot
  is zero. Arbitrary load placement/pointer preservation cannot be assumed.
  No firmware execution or runtime failure claim; see LK-MEMORY-POINTER.md.
- Three sparse replay/drift/truncation controls pass. Next executable source
  acceptance: alternate tuple branch0x3e17c, remaining reservation/PSCI callbacks,
  selected FDT lineage/trust boundaries. Installed LK3/physical return/log gates
  remain Blocked; no owner physical action requested.

## 2026-10-28 — alternate rank branch and IDME dispatcher boundary (#347)

- Alternate0x3e17c guard is function presence: pinned GOT+0x380 points to actual
  mblock helper0x4bd25ac5, not a runtime mode flag. Unchanged artifact takes helper
  path. Alternate ranks use32-bit pairs/last-size adjustment and save/restore FDT
  r5; host model reports wrap rather than validating physical geometry.
- Dispatcher0x140 callback/context storage traced; one conditional setup writes
  Thumb target0x4bd00d85. Target looks up /idme and writes value/permission from
  context. No actual identifiers read/published; raw final-DTB capture must remain
  private with normalized technical facts only. No PSCI identity inferred.
- Evidence/lk-alternate-memory and LK-ALTERNATE-MEMORY.md pin exact LK hash,
  selected instruction windows/GOT slots and five replay/arithmetic controls.
  Sparse replay initially exposed missing instruction bytes; corrected window
  bounds and regenerated from the pinned artifact before validation.
- Next executable source acceptance: selected dispatcher setup and remaining
  PSCI/reservation edits, then full selected FDT lineage/trust inventory. Actual
  installed LK3/loading/failure return/log-retention gates remain Blocked.

## 2026-10-28 — actual selected CPU-node edits (#347)

- Callback0x258ec selected by nonzero GOT function pointer; /cpus cpu-node reg
  low-byte threshold selects node removal, retained clock-frequency only capped
  downward. Pinned seven-entry core table and frequency arithmetic; separate
  helper reads modeled independently. No actual CPU/rate or PSCI inference.
- Evidence/lk-cpu-fixup and LK-CPU-FIXUP.md pin exact LK hash, full selected
  windows, calls/strings/table and five replay/drift/selector controls. No device
  read, firmware/helper execution or new download.
- Next executable source acceptance: finite final-DTB mutation/entry/handoff
  coverage inventory across receipts, unresolved dispatcher setup/trust and
  minimum installed-LK3 evidence. Physical loading/return/log gates stay Blocked.

## 2026-10-28 — finite LK handoff coverage and evidence admission (#347)

- Consolidated nine pinned exact-OTA receipts into evidence/lk-handoff-coverage/
  manifest.json and LK-HANDOFF-COVERAGE.md. Cached source is explicitly distinct
  from installed LK3. Five gates: installed identity, bounded entry, matching
  final DTB, independent failure return and attributable retained failure log.
  All remain unqualified; no beta/loading admission inferred from source checks.
- Validator verifies receipt content hashes/one LK identity/completeness and
  rejects source-only runtime promotion. Four controls cover drift, duplicate/
  missing/external/cross-artifact receipts and attempted gate promotion.
  Command: python3 scripts/validate_lk_handoff_coverage.py; all source tests.
- Linked checklist from rehearsal/index and placed next acceptance at queue top.
  Next: compare existing cached loading/trust alternatives against checklist,
  select one viable nonpersistent bounded route or rule out with exact blockers.
  No cable/approval/device action requested; no firmware/helper execution.

## 2026-10-28 — route admission verdict and independent next task (#347/#27)

- Compared retained routes against all five handoff gates. Seven route classes,
  zero qualified nonpersistent trials. Pinned ten existing receipts in
  evidence/route-admission/review.json; CURRENT-ROUTE-ADMISSION.md records exact
  version/write/entry/protocol blockers and resolved owner/material prerequisites.
- No firmware/helper/device execution or new download. Source evidence does not
  prove no future route exists. Runtime recovery gates remain Blocked.
- Owner beta estimate: roughly15% engineering progress, not measured task fraction
  or remaining-time prediction; actual maintained-kernel/Android/hardware QA open.
- Next independent source acceptance #27: cached watchdog provider/probe/reset
  binding with actual negative controls; preserve full42-diagnostic baseline and
  distinguish source reset contract from actual failed-boot return.

## 2026-10-28 — matched MT8163 watchdog provider/probe/reset binding (#27)

- Added opt-in hash-locked MT8163 compatible/2..31sec timeout contract; all old
  SoC constraints preserved. Cached source OF match/15-reset descriptor pinned.
  Five offsets/four keys match exact legacy Git header; bit5 naming alone is not
  a changed write. Probe may reprogram already-running watchdog, not passive.
-19 actual decoded-node Draft201909/typeSize controls pass, including optional
  IRQ and existing-SoC positives. Corrected timeout mutations to decoded cell
  representation before acceptance. No DTB/driver/device change or download.
- Full cached wrapper42→41 diagnostics (29unmatched/12validation), only watchdog
  unmatched removed/no additions; exit1/passedfalse retained. Evidence and exact
  commands/hashes under evidence/watchdog-binding and WATCHDOG-BINDING.md.
- Next #27 source acceptance: pinctrl syscfg-parent resource/binding matching
  with actual controls. Runtime IRQ/reset/independent return/log gates remain open.

## 2026-10-28 — pinctrl syscfg provider/linkage/extent (#27)

- Added opt-in exact MT8163 pctl-a-syscfg/syscon binding in both selector/tuple
  enums, with all old policies preserved. Actual consumer resolves phandle14 to
 0x10005000+0x1000; EINT reg is distinct. Source type1[155,155) uses one regmap.
- Reviewed155 pins/119drive/46pull/92IES-SMT entries plus generic port/mux models;
  conservative end0xf5c fits4KiB. Fresh-DTB CI guard rejects wrong/missing/extra
  maps, disabled provider and wrong/undersized/expanded resources. No all-MMIO
  or hardware qualification. Source hashes verified from existing input locks.
-12 actual decoded-node schema controls pass; corrected unknown-property control
  to observed processed-schema rejection before acceptance. Full41→40 diagnostics
  (28unmatched/12validation), only provider unmatched removed/no additions, exit1.
- Exact receipts/commands: evidence/pinctrl-syscfg-binding and
  PINCTRL-SYSCFG-BINDING.md. No driver/DTB/device change or new download.
- Next #27 source acceptance: actual IOMMU/SMI probe/resource dependencies, then
  source-matched contracts; keep40 diagnostics and all runtime recovery gates open.

## 2026-10-28 — actual IOMMU/SMI source integration prerequisites (#27)

- Retrieved only two bounded pinned official ACK files (57941/33691bytes),
  retaining URLs/hashes; compared to cached donor20951722. Added80-line MT8163-
  only patch, preserving shared ACK probe/error policies and unrelated SoCs.
- Apply tool verifies revision/input/donor/patch/output hashes. Existing provider
  build now requires IOMMU/SMI symbols and both objects before Image/generic-QEMU
  checks. Source/host results are not compilation or hardware claims.
- Fresh-DTB dependency guard checks four larbs/common SMI, exact phandle/clock/
  domain roles and resources. Initial uniform4KiB assumption rejected actual64KiB
  larb1 declaration; corrected reviewed model without changing DTB. No binding
  added prematurely; all40 schema diagnostics remain.
- Inputs/commands/source effects: kernel/iommu-port/README.md and
  evidence/iommu-smi-port. No device/firmware execution or local kernel archive.
- Next acceptance after exact-head build: matched IOMMU/SMI binding contracts and
  actual node controls; runtime DMA/display/return/log qualification remains open.

## 2026-10-28 — pinned genpd wakeup core comparison (#20)

- Retried obsolete drivers/base/power/domain.c:404; acquired actual relocated
  drivers/pmdomain/core.c102206bytes and pm_wakeup.h7474bytes at pinned ACK
  d9318bdb. Official URLs and SHA256 receipts in evidence/power-port/wakeup-core.
- Exact legacy Git object and modern core/header establish16 Boolean branch
  combinations. Equal active policy matches only under stated already-off/OOB
  assumptions; prepare, noirq callback ordering, stop/start and errors differ.
- Candidate omits active-wakeup capability while eight legacy domains enable it;
  no automatic flag edit from narrow predicate equivalence. Missing-source blocker
  resolved; desired modern device wakeup policy and runtime transitions remain open.
- Reproduce: python3 scripts/validate_genpd_wakeup_comparison.py. No device/firmware
  execution. Independent source task completed while PR407 provider build runs.
- Next #20 acceptance: derive intended modern wakeup configuration and power
  transition behavior before any capability change; #27 source/build then matched
  IOMMU/SMI contracts remains the current queue priority.

## 2026-10-28 — actual IOMMU/SMI build and matched contracts (#27)

- PR407 merged6821d31282f9d533456a321417c6a2bb87196bf0 after five PR checks plus
  exact-head302e51a run40794335163. Real provider objects/Image and generic QEMU
  pass; normalized hashes/URL in evidence/iommu-smi-port/build-result.json. No
  MT8163 hardware probe. Prior run superseded after worklog conflict resolution.
- Three opt-in hash-locked source-matched contracts;60 actual decoded-node
  controls and structural old-SoC preservation pass. Corrected larb-ID mutation
  from array to decoded scalar to test actual range, not accidental type failure.
- Full context40→38 (22unmatched/16validation): six unmatched nodes selected and
  four larb interrupt errors exposed, no other delta. Selected SMI driver consumes
  no IRQ; candidate rejection remains visible. Wrapper exit1/passedfalse retained.
- Reproduce/check commands, hashes, portable schema/node receipts and full output
  under evidence/iommu-smi-binding; IOMMU-SMI-BINDINGS.md describes limits.
  No new source downloads, DTB/driver/device/firmware changes in binding scope.
- Next executable #27 acceptance: trace source ownership/origin of four larb IRQ
  declarations from cached sources before any DT correction. Runtime DMA/display/
  independent failed-boot return and retained logs remain open.

## 2026-10-28 — source-backed optional larb IRQ resources (#27)

- Exact legacy DTS declares SPI205/213/217/207 at the four larb addresses; donor
  retains them. Legacy matching larb probe maps memory/clocks/common link without
  IRQ request, while M4U maps its own node SPI147 and requests MTK_M4U_isr.
  Exact paths/hashes/line excerpts retained in evidence/larb-irq-contract.
- Preserve vendor hardware declarations rather than delete unhandled resources.
  MT8163-only optional single-IRQ schema preserves old-SoC IRQ prohibition and all
  unrelated prior constraints. Fresh-DTB guard checks declared vendor IRQ tuple.
-40 actual decoded-node controls pass, including unchanged nodes, optional
  absence, excess IRQs and old-SoC prohibition. Cardinality controls are separate
  from board-specific type/number/polarity guard; no claim of handler support.
- Full38→34 diagnostics: exactly four larb property errors removed, no additions;
 22unmatched/12validation remain, wrapper exit1/passedfalse. Historical409 receipts
  unchanged. No DTB/driver/device/firmware change or download.
- Exact reproduction commands/full diagnostics/provenance in evidence directory
  and LARB-IRQ-CONTRACT.md. Next #27 source acceptance: USB MUSB/T-PHY actual
  driver/OF/probe prerequisites before binding support; loader/return/log runtime
  gates remain open.

## 2026-10-28 — actual USB fallback/probe and variant prerequisites (#27)

- Acquired only two capped official ACK files (13649/46869bytes), pinned revision/
  URL/SHA256; legacy source/hash/line receipts from cached e0a3a2b. Both candidate
  fallbacks match actual tables, without proving MT8163 variant equivalence.
- Legacy resource1 SIF->io_priv->macro+0x800 and calibration0xf00-0x800+0x0c
  derive0x11210f0c; selected generic V1 SIF+0x100+0x0c derives0x1121010c. Legacy
  formulaFRA48 vs V1 default26 also differs, but legacy calculated write is
  commented out: active code writes fixed byte0x60/SRCTRL6. ACK applies a computed
  field. No formula-only replacement or MMIO/device observation inferred.
- Actual candidate controller and PHY disabled; diagnostic fragment requests
  USB/GADGET disabled. Probe/PHY operations are not passive. No reset dependency
  copied from siblings, no guessed DT property, no enabling/binding/build claim.
- Added fresh-DTB metadata/source audit and negative controls for enablement,
  resource/IRQ/clock/phandle/PHY-type drift. Report keeps variant/build/device
  readiness false. Exact receipts/report/commands: evidence/usb-prerequisites and
  USB-PREREQUISITES.md. Candidate SHA/full34 diagnostics unchanged.
- Next bounded #27 source acceptance: USB2 bank/calibration arithmetic/timeouts
  comparison and justified MT8163-specific variant/resource definition before
  source/build integration. Runtime loading/independent return/log gates open.

## 2026-10-28 — finite USB2 variant/resource definition (#27)

- Compared actual byte write, ACK field/RMW and existing eye-src6 shortcut over
  all65536 isolated low16-bit states. Equal counts8192/4096 and difference masks
 0x700/0x8700 respectively; concrete counterexample0x8700. Not hardware sampling
  or whole sequence equivalence. High bits stable assumption remains explicit.
- Defined MT8163-only USB2 measure-then-vendor-fixed-byte policy,3*HZ deadline
  intent represented as3000000us, explicit zero/timeout cleanup and no dead divide.
  No calibration skip/EYE shortcut; existing SoC policies must remain unchanged.
- Separate frequency0x11210f00+0x100 resource disjoint from shared0x800 and child
  windows; negative controls reject naive4KiB parent expansion/ownership overlap.
  Missing bank must error, not fallback. One capped official helper-header read
  verifies mask/field RMW semantics; no archive or kernel/DT/device change.
- Reproduce scripts/validate_usb_variant_definition.py; exact hashes/results in
  evidence/usb-variant-definition and kernel/usb-port/README.md. Full34 schema
  diagnostics and candidate USB-disabled baseline unchanged.
- Next executable #27 acceptance: isolated actual MT8163 source implementation
  and source/build integration, preserving non-MT8163 behavior and explicit error
  paths. Remaining analog/role/clock policy and all runtime return/log gates open.

## 2026-10-28 — actual MT8163 USB2 source and USB-enabled build integration (#27)

- Implemented isolated exact MT8163 descriptor/USB2 port0 xlate; required separate
  named frequency resource/minimum window, SIF/common extent and EYE guards.
  Missing/invalid mappings error rather than selecting generic bank.
- New serialized measurement uses source-derived byte sequence and bounded3sec
  polling and explicit1024-cycle/channel0 field setup rather than reset-state
  assumptions; success/zero/timeout all clean up and apply vendor full-byte0x60. No
  dead formula/divide-by-zero or skip-calibration shortcut. Existing descriptors
  and generic calibration body preserved. Analog/role/clock behavior unqualified.
- Hash-lock apply validates exact ACK/source/helper/definition/patch/output.
  Host tests compile actual new C functions against RAM-only I/O/resource mocks:
  missing/small/busy mappings and success/zero/timeout/large readings checked.
- Explicit usb-providers profile enables/resolves USB/GADGET/MUSB/T-PHY and
  checks actual objects/config/Image; old USB-off diagnostic fragment unchanged.
  Path-based PR selector chooses one build; non-USB changes retain generic QEMU.
  Linux compilation must pass before build claims. No device/firmware execution.
- Two capped pinned Kconfig reads total7581bytes confirm NOP transceiver/role/PHY
  dependencies; receipts in evidence/usb-kernel-integration. Reproduce host tests,
  scripts/apply_usb_port.py and build_ack_baseline.sh usb-providers.
- Linux GCC caught stack-fixture addresses stored in global RAM-mock pointers;
  changed fixture storage to static lifetime and exposed compiler stderr. GNU
  cross-compile/link and native mock execution pass; no warning suppression or
  kernel-patch change. New-head Linux build remains required after this test fix.
- Next acceptance after exact-head Linux build: isolated disabled-DT frequency
  resource experiment and matched binding controls; baseline/full34 diagnostics,
  actual transport/loading/independent return/log gates remain unqualified.

## 2026-10-28 — USB build accepted and isolated disabled resource/bindings (#27)

- PR413 merged a387d72984736862777af376fa428abe1be11ec1 after five PR checks and
  exact-head179c920 run40805824866. Actual MUSB/T-PHY objects, USB/GADGET/dual-role/
  Inventra DMA config and Image pass. Object/config/Image hashes and exact run
  retained in evidence/usb-kernel-integration/build-result.json. No QEMU/device test.
- Registered explicit seven-patch/26-input disabled USB frequency experiment.
  Fresh compile26307bytes SHA4480f085cfb03c2cb6a1b2c9b0c6a7619f3f4c0e395833b93d623deffe65c5c4.
  Only parent reg/reg-names change across186nodes; all other values/phandles,
  child order and reserve table preserved. All USB nodes remain disabled.
- Two opt-in source-matched metadata schemas;25 actual decoded-node controls and
  structural old-SoC preservation pass. Explicit top-level minItems1 prevents
  dtschema inferring global minimum2; MT8163 requires two named resources only.
- Paired isolated context34→28 removes six USB metadata diagnostics/no additions;
 19unmatched/9validation remain, wrapper exit1/passedfalse. Canonical pwrap b837e6cb
  and its34-diagnostic context not replaced. Disabled USB1 metadata acceptance is
  not driver support: initial MT8163 xlate rejects its port1. No activation.
- Exact commands, source-DTB/property/schema receipts and negative controls in
  evidence/usb-resource-binding and USB-RESOURCE-BINDINGS.md. No new downloads
  or device/firmware execution. Next #27 source acceptance: finite USB0 analog/
  role/clock dependency comparison, with all physical loading/return/log gates open.

## 2026-10-28 — finite USB0 analog/role/clock source comparison (#27)

- PR414 merged fdeae38c02306a42cb396e3374d304cc6d89a88c after five exact-head
  checks at9212cb590536683a58304617856ad8ba1a1d96b8;401 tests/25 decoded controls.
- Pinned cached legacy e0a3a2b USB probe lines1325..1383 plus full-source hash,
  ACKd9318bdb PHY/MUSB, current USB patch/clock providers and actual isolated-DTB
  property inventory. No downloads/device or firmware execution.
- Finite source expressions: RX differs for all256 states (mask0x5); eye-no-props
  equals legacy in1024/65536 states, explicit7/7 inall65536; role-device equal2048/
  65536 (mask0x3c08), role-OTG equal0 (mask0x3e0a). Not measurements/probabilities
  or whole-sequence equivalence. Report/commands in evidence/usb0-transition-review.
- CCF prepares four clocks, PHY first-enable path uses usbpll/usb/usbmcu; no ICUSB
  CCF enable in pinned PHY. CLKMGR gates ICUSB separately. Modern MUSB bulk and
  optional PHY ref ownership differ; candidate ref14 is separate from UNIVPLL2.
- Next executable #27 implementation: isolated MT8163 RX/eye recovery policy,
  preserve bits/reject conflicts, actual C RAM mocks and exact-head USB build;
  role-force policy stays separate. Canonical34/isolated28 failing contexts and
  disabled DT unchanged; all physical transport/loading/return/log gates remain open.

## 2026-10-28 — actual MT8163 cold/recovery analog kernel policy (#27)

- PR415 source comparison merged2d839f3ce76783a28169eab0c265b48a9a1f265d after five
  exact-head checks at22b89c7ea67dc36d0a2a95288ea9dcdf96525e44.
- Actual USB patch now selects cold analog operation in init (OR6/preservebit3/0)
  and recovery in power_on (clearbit3/OR6/preserve0); both apply eye mask0x7700.
  Exact-descriptor branches only; generic bodies/descriptors and role-force policy
  unchanged. Explicit7 overrides accepted; conflict/malformed/slew bypass rejected.
- Actual C RAM mocks enumerate131072 states with upper-word/unrelated-byte guards,
  plus override negatives and previous calibration/resource tests.402 host tests
  pass. Pinned source/patch/test hashes and legacy-enable excerpt in
  evidence/usb-analog-policy; docs kernel/usb-port/ANALOG-POLICY.md.
- Pre-analog patch copied unchanged to evidence/usb0-transition-review so prior
  source receipt remains reproducible while actual USB patch advances.
- Required next acceptance: exact-head usb-providers object/config/Image build,
  not the older413 result. No device/firmware execution. DT/canonical34/isolated28
  binding contexts and all transport/loading/return/log gates remain unchanged.
- Next independent metadata task: MT8163-only eye override contract/decoded-node
  negative controls after successful source build. Physical role/clock/signal
  behavior is still unqualified and controllers/PHY stay disabled.

- Pre-merge review found read_u32 alone accepts the first cell of longer arrays.
  Added exact one-cell count guard and actual C negative for multi-cell input
  beginning with7. Old-head Linux run40813337073 is superseded; replacement
  exact-head usb-providers run required after this fix. No build claim made.

## 2026-10-29 — analog source build accepted and eye contract matched (#27)

- PR416 merged6ef265b37da10f329f3a4d3b961791ce2b55ac2a after five distinct
  final-head checks (successful reruns included), exact dad8de0 USB-enabled
  run40813924079/job123250444675. MUSB/T-PHY objects/config/Image pass;
  no QEMU/device test. Raw log ignored out/usb-analog-build-40813924079.log;
  hashes/run/config receipt evidence/usb-analog-policy/build-result.json.
- Replaced locked T-PHY proposal with MT8163-only eye-vrt/eye-term const7;
  absent properties allowed, eye-src forbidden, other SoCs/constraints preserved.
 30 actual decoded-node controls pass, including malformed/multi-cell-first7.
- Full matched5186-YAML context remains28 diagnostics (19unmatched/9validation),
  unchanged identities; known Gunyah mk-schema warning retained. Wrapperexit1/
  passedfalse. Canonical34 context and both disabled DTBs unchanged. Historical
  414 controls remain untouched. No new source/kernel build needed for binding-only.
- Exact inputs/commands/reports in evidence/usb-analog-binding; docs
  kernel/dtb/USB-ANALOG-BINDING.md. Next #27 source acceptance: finite controller
  gadget/device-role/init/config and initramfs prerequisites before any disabled
  mode experiment; all physical USB/loading/independent return/log gates open.

## 2026-10-29 — gadget role/config/package prerequisites (#27)

- PR417 merged414075c2c7dbabe6612a2f1150fcc8bfb22a7396 after five final-head
  checks at644691e3fa90a46d2b6ec716fa8232c93e1f179f,402tests/30controls.
- Pinned416 resolved gadget states: CONFIGFS/LIBCOMPOSITE/F_ACM/U_SERIAL=m,
  ROLE_SWITCH=y/CONFIGFS_ACM=y. Three capped official ACK Kconfig/Makefile reads
  total19703bytes verify selection/object links. No new kernel archive/device action.
- Actual cached controller role function compiled/executed with RAM mocks over18
  prior/target/error cases plus invalid-role negative: called PHY errors ignored,
  advertised role still updates/return0. No actual hardware failure observed.
- Fresh current PID1 cross-compiled with existing GNU AArch64 toolchain at O2;
  static ELF/newc inspected, never executed. GNU Os required an unavailable memcpy;
  O2 linked without added helpers. Canonical Clang builder unchanged. Actual package
  is only dev/proc/sys/dev-console/init, no modules/configfs gadget setup. Current
  sysfs mount read-only; console-only output does not establish USB logging.
- Host audit now runs after fresh diagnostic build in CI; require-ready exits1,
  default diagnostic reports source-package/transport false. Negative parser/config
  controls and all-builtin non-admission tested. Exact hashes/commands/receipts in
  evidence/usb-gadget-prerequisites; docs kernel/USB-GADGET-PREREQUISITES.md.
- Next actual implementation: MT8163-scoped role/init error propagation and rollback,
  actual C RAM tests and exact-head USB provider/Image build. Builtin ACM/profile
  and explicit gadget userspace remain separate. No kernel/DT/device changes here;
  canonical34/isolated28 failures and all loading/return/log gates remain open.

## 2026-10-29 — actual MT8163 role/init PHY error transactions (#27)

- PR418 merged19b5fb4af7c8a1881348aa29d8c6498003bdda8f after five final-head
  checks ate6b43a0e2f5d29471bb2a40b5bc4b115790d6201;406 tests/source audit.
- Added exact MT8163 MUSB match/data and scoped role/init/exit implementation;
  previous generic functions retained byte-identical as legacy helpers. Checks
  backend errors before controller/role commit; propagates caller errors; failed
  transactions latch fault even after best-effort mode/power restoration. Init
  handles failed set_mode/cleanup before interrupts; exit respects known refs.
- Pinned31489-byte official ACK phy-core.c confirms successful-reference and
  failure-count/mode semantics. Hardware partial change/physical rollback not
  qualified. No concurrent callback or safe reprobe qualification claimed.
-409 host tests, actual C RAM controls cover12 successful role/power combinations,
  idempotency, initial NONE-owned power without duplication, mode/power/exit
  cleanup failures, error preservation, no register/role commit, all init phases,
  caller/getter/fault behavior and non-OTG lifecycle. Generic behavior preserved.
- apply_usb_port now input-checks both source targets and every patch/helper;
  shadow-applies/output-checks all targets before real writes. Second-source and
  output drift negatives prove both real files unchanged. Exact hashes/commands
  evidence/usb-role-errors; docs kernel/usb-port/ROLE-ERRORS.md.
- Required next acceptance: new exact-head USB-enabled object/config/Image run;
  no current build claim. No device/mode/firmware execution. Both disabled DTs and
  canonical34/isolated28 failures unchanged. Next independent ready package work:
  explicit opt-in builtin ACM/configfs profile/gadget userspace after source build,
  retaining minimal diagnostic security/storage boundaries and all runtime gates.


## 2026-10-29 — #27 draft userspace adapters, pending profile build

- Actual bounded configfs transaction and syscall callback adapters plus unique
  expected USB0 discovery added outside the unchanged minimal PID1. All12 setup
  failure points, owned reverse cleanup, unbind-before-delete, readback-confirmed
  ENODEV, short/EINTR writes, close errors, malformed directory records, ambiguous
  UDCs and wrong controller/OTG metadata checked with actual C RAM callbacks.
- Native ASan/UBSan and GNU AArch64 object compilation pass. Pinned official ACK
  configfs/UDC/MUSB and generated syscall-table/dirent ABI receipts retained in
  evidence/usb-acm-userspace. No filesystem/device callback executes in tests.
- Draft only: matching PR420 headbd288c7 ACM/security build40828537870 pending.
  No PID1, syscall bridge, gadget archive, runtime policy/transport or physical
  return/log qualification. Next implement separate opt-in PID1 and admission;
  preserve no shell/ADB/storage and enforcing security prerequisites.
## 2026-10-29 — explicit builtin ACM compile profile (#27)

- PR419 merged37256b14f619b34018817ed0ac1fb11a7c5d6451 after six exact-head
  checks at93e62f84cc2d93b1970c755d543740f55c6c4c5f; run40822461567 actual
  MUSB/T-PHY objects/config/Image passed. No physical rollback/runtime/QEMU proof.
  Raw log ignored out/usb-role-build-40822461567.log; public source/artifact receipt
  evidence/usb-role-errors/build-result.json (object hashes pre-Image W=1).
- Added actual opt-in usb-acm-diagnostic apply/check/build mode: builtin configfs/
  libcomposite/ACM/u_serial, other configfs functions/Android uevents disabled.
  SELinux must remain builtin; no security configuration change or device action.
- Linux path applies before olddefconfig, verifies resolution, compiles/hashes three
  actual ACM objects in addition to providers, then Image. One build selected per
  profile PR; no QEMU/forced generic arguments. Old provider/minimal diagnostic
  scopes unchanged.412 host tests and shell/repository checks pass; model fixtures
  not claimed as actual Kconfig resolution. New exact-head ACM build required.
- Exact policy/source hashes/commands in evidence/usb-acm-profile; docs kernel/
  usb-acm/README.md. No DT change; canonical34/isolated28 failures stay open.
- Independent next userspace implementation: separate opt-in static gadget PID1/
  configuration/output with RAM cleanup/failure controls. Minimal PID1 remains
  unchanged; no current gadget setup or physical loading/return/log claim.

- First ACM run40826710226 at6bbdd03 failed before objects/Image: four ACM
  components resolved builtin, but generic defconfig SECURITY_NETWORK/SELinux
  absent and LSM list excluded SELinux. Earlier preservation assumption corrected.
  Security guard retained. Explicit dependency/SELinux requests and LSM membership
  added; SELinux boot-disable/development switches disabled. No runtime bypass.
  Exact rejected config/log receipt in evidence/usb-acm-profile; actual negative
  regression added. Replacement exact-head build required; no success claim.

- Replacement40827564991 ataade0fa passed actual ACM/security/LSM resolution and
  USB provider object checks, then failed at an invalid standalone builtin
  libcomposite.o aggregate probe. Corrected to nine actual translation units from
  hash-locked pinned Makefiles; Image link still required.414 host tests and target
  regression controls pass; another exact-head ACM build required, no Image claim.

PR420 final result: merged b68afe8 after exact-head bd288c7 run40828537870
passed USB provider/nine builtin ACM components, security/LSM configuration and
Image. No QEMU/device transport test. Normalized build receipt in
evidence/usb-acm-profile/build-result.json. Prior failures remain historical.


## 2026-10-29 — #27 separate static PID1 and source lifecycle

- Actual syscall bridge/static PID1 plus owned mount/security/discovery/configuration
  lifecycle implemented separately from minimal diagnostic init. Seven denied gates
  and empty physical descriptors are enforced by archive builder; no token enables
  runtime. Read-only proc/sysfs/selinuxfs precede security check; configfs only after
  enforcing/discovery. Cleanup stops on failed unbind/unmount and retains ownership.
- RAM sanitizer controls cover21 gate negatives, four mount/four unmount failures,
  security/discovery/output errors, bind/unbind failure with primary error preserved,
  no automatic cleanup retry, bounded console and guarded freestanding memory.
- GNU static link initially exposed missing memset; explicit tested compiler-support
  implementations added without suppressing warnings. Actual AArch64 static ELF
  and deterministic newc inspected, never executed. Separate Clang build wired inCI;
  exact-head result pending. No new Linux Image build needed for userspace-only code.
- No ACM serial output, device execution, DT change or runtime policy qualification.
  Canonical34/isolated28 failing contexts unchanged. Next: actual bounded serial
  endpoint/output with failure controls; loading/role/security/return/log gates open.


## 2026-10-29 — #27 actual bounded ACM status source

- PR422 acceptedb0f84d7 after five checks atbad648f; actual Clang18 static ELF2088B
  and archive914B inspected, never executed. Exact normalized receipt published
  in evidence/usb-acm-pid1/clang-build-result.json; historical GNU proof retained.
- Actual serial adapters now read owned function port_num and dynamic ttyGS dev,
  reject existing private node, verify opened fd via statx, snapshot/set/readback/
  restore raw termios, send one fixed status frame with bounded partial/EINTR/
  EAGAIN attempts and preserve primary plus cleanup failures. No assumed ttyGS0
  or device numbers. PID1 admitted emit mapping uses actual adapters.
-422 host tests/RAM sanitizers, pinned UAPI layout/hash/negative controls, GNU
  AArch64 object/static ELF/archive checks pass. Exact-head Clang CI required.
  Kernel/provider/config/Image unchanged; no repeated Linux build needed.
- Pinned u_serial close can wait15*HZ and discard queued data; writes queue without
  connection, acm_set_alt ignores gserial_connect result. Userspace attempt bounds
  are not strict wall-clock/host receipt proof. Fixed frame says unverified.
- All seven runtime gates stayzero, physical descriptors empty, minimal PID1/DTs
  and canonical34/isolated28 failures unchanged. No device action. Next actual
  source scope: host bounded capture/frame validation and private receipts with
  mocks, before physical loading/role/policy/independent return/retained-log gates.

- PR423 initial integrity check found raw Gitiles anti-XSSI-prefixed directory
  response mislabeled .json. Renamed raw evidence .txt and reader, preserving
  exact hash/bytes and strict repository JSON parsing. Local exact-base integrity
  and serial controls pass; source C unchanged. New exact-head CI required.


## 2026-10-29 — #27 actual private host frame capture

- PR423 merged8ca3a01 at766d648 after five checks; normalized actual Clang18 result
  now evidence/usb-acm-serial/clang-build-result.json. Denied artifacts identical
  to422; admitted paths remain RAM-only. No repeated kernel/Image build.
- Reused tested receiver core; actual private file/read adapters and CLI now enforce
  source/frame hash lock, denied serial profile, exclusive0700 output/0600 files,
  bounded reads/writes/deadlines, partial/EINTR/EAGAIN/error/owned cleanup controls.
  Failed raw bytes/selectors and invalid hashes stay private; stdout sanitized.
-446 host tests: four receiver/20 adapter controls plus existing suites. Actual
  offline CLI validated73 bytes, explicitly host_frame_observed=false/runtimefalse.
  Serial descriptor/raw-setting checks exercised only mocks; no physical opens,
  activation, termios writes or security bypass. Evidence/usb-acm-host.
- Queue audited: #340 requires actual integrated candidate/return/log qualification;
  no cached Image found and no new download attempted. #18 explicitly depends on
  unmatched AUDSYS contract under#27. Cached integrated parent/binding/DTS leads
  pinned ignored out/audsys-next-source.json; next actual source acceptance must
  establish parent probe/resource/child ownership before schema extension. Do not
  blindly reuse MT2701 audio child or suppress current failed corpus diagnostics.
- Recovery items' obsolete watchdog-next delivery fields corrected; loading/return/
  retained-log blockers and all seven PID1/host serial gates remain unqualified.
  No runtime gate closed. Exact current-head host CI required before merge.


## 2026-10-29 — #27/#18 actual AUDSYS parent contract

- Source-pinned integrated parent:13 gates/6 composites/19 IDs, highest0x5a4 word
  -> required0x5a8 inside4KiB. Fresh-DTB guard checks parent tuple/resource/phandle,
  actual clock-specifier IDs/15 references and disabled child; rejects unreviewed
  regmap/resource overrides. Cached provider build bd288c7/run40828537870 compiled
  AUDSYS=y and Image; relevant inputs byte-identical. No audsys.o hash invented.
- Three capped official ACK helper reads38779bytes establish gate regmap(no
  optional clock/reset management), default32-bit width and managed/disabled child
  population. Actual wrapper C RAM probe/populate-failure/remove-order controls
  plus GNU AArch64 object compile pass; devres/MMIO/runtime not emulated or passed.
- Opt-in schema requires MT8163 parent reg without inheriting unrelated MT2701
  child schema. No child schema/stub added.30 decoded parent controls and exact
  older-SoC structural preservation pass. Actual disabled AFE child remains
  unmatched in both full5186-YAML contexts; no audio function/build claim.
- Canonical34→33(21unmatched/12validation), isolated28→27(18/9): exactly parent
  unmatched removed, nothing added. Known Gunyah warning and wrapper exit1/false
  retained. DTBs/disabled states unchanged.450 host tests; exact-head CI pending.
- Prior424 host source mergedb2d8847 after five checks/446tests; exact normalized
  receipt now evidence/usb-acm-host/ci-result.json. Next existing unmatched board
  prerequisite is silergy,sym827 regulator:19,323-byte pinned ACK fan53555 source
  cached as a lead only (SYR table entry does not establish SYM ownership). Qualify
  actual driver/legacy variant/probe/selector constraints before changes; no
  voltage/device actions or guessed aliases. Runtime recovery/beta gates stay open.

- PR425 initial clean-CI failure40843369475: fresh canonical DTB guard passed,
  then actual schema controls could not import dtschema (DTC-only bootstrap does
  not install it). Added explicit16-artifact4,031,591-byte Linux/Python3.12 hash-
  locked bootstrap, real pylibfdt extension with required SWIG4.4.1 and offline
  dependency resolution. Controls remain enabled;452 host tests including lock/
  budget/platform/cache-drift rejection. Replacement exact-head CI required.


## 2026-10-29 — #27 actual isolated SYM827 source port

- PR425 final7d3208a accepted09bc5eb after five checks/452 CI tests/30 decoded
  parent controls/two fresh guards. Normalized final schema-toolchain receipt
  published evidence/audsys-binding/ci-result.json; prior pending text historical.
- Cached donor20951722 explicitly implements ID1/rev12/min600000/step12500;
  original ACK d9318bdb only supports SYR IDs8/9/min712500. Added separate appended
  SYM vendor rather than changing shared SYR acceptance. Exact source hashes and
  legacy manufacturer/voltage/GPIO provenance in evidence/sym827-port.
- Actual C helper requires legacy manufacturer4 and donor ID/revision, one scalar
  explicit selector0/1 and no ignored legacy GPIO ownership. Read errors retained;
  guard precedes setup/registration. No legacy GPIO/DVS/debug ABI copied. Physical
  active bank/GPIO34 handoff and voltage behavior remain unqualified.
- Actual C RAM ASan/UBSan controls cover65536 raw identities,256 decoded ranges,
  both banks/64 selectors and6144 prior-vendor full-state comparisons. Other prior
  integer functions except setup/probe byte-identical. Full kernel probe/physical
  behavior not simulated. Hash-locked shadow apply verifies output before writes;
  wrong revision/source/output/reapply fail without target changes.
- Separate sym827-provider wrapper retains build_ack_baseline.sh byte-identical
  (AUDSYS build pin), runs existing baseline then changed regulator W1 object and
  final Image/vmlinux. Earlier baseline Image precedes new patch. Required new
  exact-head Linux result pending; no source build or binding acceptance yet.
- DTBs/schema/canonical33/isolated27 failed contexts and all disabled states remain
  unchanged. No I2C/regulator/GPIO/device/voltage/security operations executed.


## 2026-10-29 — #27 SYM827 source build and matched metadata

- PR426 merged4e358045fd6a2fe2fa882100314c0b0f81e06084 after five host checks
  plus exact-head dec1a898 run40847835013/job123359594153. Actual changed-source
  SHA b3cc8c2daf66c36d72fce0b02d55b1aebccc15144406a46f639eb03a2a2c2e2d
  matches lock; final Image eb064096cb41fb4e82b9f06d04027abcfd387f922c5fe2fd84cc9acda5f76c11
  (28645888bytes), config REGULATOR_FAN53555=y. Normalized exact source/object/
  config/vmlinux/Image receipt published; raw build log private. W1 object hash
  is pre-Image probe, earlier baseline Image.gz not changed-source acceptance.
- Actual source-matched opt-in SYM binding adds exact compatible and conditional
  explicit scalar selector/no external GPIO ownership; older SoC policy retained.
 22 decoded controls pass; full5186-YAML canonical33→32(20unmatched/12validation),
  isolated27→26(17/9), only SYM unmatched removed/no additions. Full wrappers keep
  exit1/passedfalse/Gunyah warning and disabled unmatched AFE child.
- DTBs/disabled states unchanged. Physical ID/GPIO34/DVS/activebank/voltage/ramp/
  CPU handoff/loading/recovery/log gates remain unqualified; no hardware action.
  New binding exact-head checks required before merge, no repeated kernel build
  for schema-only scope. Existing task27/Phase328/Feature4/Epic2 remain Active.


## 2026-10-29 — #27 finite thermal source prerequisite audit

- PR427 final e2b07e238c4dfa829f39eaf473e0208d76de299c merged e56a1b7 after
  five exact-head checks/458 tests/22 decoded controls/fresh-DTB raw-node check.
  Final normalized receipt published evidence/sym827-binding/ci-result.json;
  prior pending-CI text historical. Current full failed contexts32/26 unchanged.
- Two capped pinned reads: ACK auxadc_thermal.c36490bytes (d9318bdb), donor38644
  bytes (20951722); exact URLs/hashes plus cached legacy e0a3a2b thermal/devinfo
  source in evidence/thermal-source. No large download or hardware operation.
- Actual C RAM ASan/UBSan functions prove callback aggregate/per-bank/private-data
  boundary difference; donor globally changes old SoCs. Actual legacy mux writes
  bank0[0,1],bank1[2,16],bank2[3,1,2,16] differ from donor table selections.
  Neither source establishes physical truth; stale comments are not acceptance.
- Actual legacy/V1 parsers on256 synthetic ID/sign/slope cases differ126 signed
  slope outputs when ID0; selected VTS/GE/DEGC fields agree given same word order.
  Legacy chosen atag,devinfo7/8/9 identity to candidate nvmem0x100+12 is unproven.
  No claim candidate offset wrong, whole conversion equivalent or calibrated.
- Executable audit validates source hashes and runs actual selected C under RAM
  mocks; drift rejects before compilation. No thermal source/binding admitted,
  no Image build needed for host audit. Task27 stays Active; thermal prerequisite
  recorded once and next independent MIPI-TX source qualification selected.
  Runtime recovery/thermal/clock/identity/voltage gates remain unqualified.


## 2026-10-29 — #27 finite MIPI-TX source contract

- PR428 merged12ba1852 after five exact-head checks at5840d29/460 CI tests;
  normalized receipt now evidence/thermal-source/ci-result.json. Thermal port
  remains unadmitted on exact calibration/bank/conversion prerequisites.
- Three bounded pinned donor files19012bytes plus cached ACK15578bytes and exact
  legacy e0a3a2b DSI/header inputs locked in evidence/mipi-source. Found distinct
  MT8163 prepare, PCW-change0x60 andpreservevalue2; not a guessed MT8173 alias.
- Actual C RAM ASan/UBSan selected functions/helpers:1201 integer-MHz rates50..1250
  PCW agree active legacy byte arithmetic,65536 lowword states8192 preserve results
  agree. Legacydeclaredfield7:14 vs donor7:11, genericcleanup8:15 differs. No samples,
  probabilities, electrical/whole-sequence equivalence or fractional-rate proof.
- Negative actual compiler control confirms donor callback reference lacks rate
  definition; retained ACK round_rate resolves fixture. Global donor reset/oldSoC
  rate ops changes must not be copied. Belowmin no I/O; direct prepare abovemax
  writes despite roundclamp, so scoped bounds/reference checks needed before MMIO.
- Definition/model chooses active legacy field8bits/value2,1ms delays/fixed RT8;
 26MHz formula/range50..1250MHz and0x6c extent. No kernel variant/DT/binding admitted.
  NEXT actual implementation, not another model-only scope: isolated functions,
  checked errors/resources/reset, unchanged oldSoCs, atomic patch+RAM negatives+
  explicit builtin PHY/object/config/Image checks. No device/reset/PHY execution.


## 2026-10-29 — #27 actual MIPI-TX kernel implementation

- PR429 merged44f5c87 atd292638 after five exact-head checks/462 CI tests; exact
  normalized receipt now evidence/mipi-source/ci-result.json. Its definition stays
  historical source intent, no retroactive kernel/runtime claim.
- Actual isolated three-target patch implements MT8163 descriptor/clock ops and
  mandatory scoped reset/resource/reference/override probe checks. Bounds and both
  actual/supplied parent26MHz checked before cached rate commit; prepare rechecks
  before MMIO. Resource0 must align/cover0x6c; unknown overrides rejected early.
- MT8163 prepare/cleanup uses legacy7:14/value2,1ms/fixedRT8/donorPCW0->1 and
  initialSSCoff. Existing SoC functions/ops byte-identical; actual original/patched
  old-probe success/error paths compared. Physical/whole-sequence behavior open.
-468 host tests pass: actual patched C RAM ASan/UBSan65536 field+cleanup states,
 1201 integer-MHz PCWs,64-bit bounds/reference/cache/no-I/O errors,nine probe
  failure stages/provider order/resource/override/power failures. Framework CCF,
  reset/devres/MMIO/delays are mocks, not hardware or cleanup qualification.
- All-target shadow preflight verifies every input/output before source patch;
  wrong source/header/helper/definition/patch/secondoutput/buildinput/reapply
  negatives preserve targets. Kconfig/Makefile3904B pinned official cached reads.
- New mipi-provider wrapper stages prior accepted diagnostic/SYM then applies MIPI,
  resolves actual PHY/reset/clock builtin, W1 compiles all three real translation
  units then rebuilds finalImage/vmlinux/config. Previous stagedImage/gzip pre-MIPI;
  require distinct final marker/new exact-head build. No repeated generic QEMU.
- No DT/schema/device change, full32/26 contexts remain failed/PHY disabled. New
  source Image checks required before merge/matched binding; no runtime gate closed.


## 2026-10-29 — #27 accepted MIPI source build and matched metadata

- PR430 merged9c3f4a81c8fb791ee76b1266f0365177223ceb82 after six exact-head
  checks atb5e12688ced84a917657d928365dec969eb66a1c, actual run40859970271/
  job123400424086. All three real PHY units/builtin dependencies/finalImage pass.
  Final Image3efbebf6bd60705a981f350129b3ad57ee2748414f94ea41c8563f2df20f0d94,
 28645888bytes; source outputs match lock. Normalized full receipt public, raw
  log private. Prior stagedImage/gzip excluded/W1objects pre-finalImage only.
- Actual source-matched schema adds exact MIPI compatible/required reset/forbidden
  overrides with olderSoC policy restored structurally.35 controls retain implicit
  full-validator type policy, not just selected PHY schema; valid drive[4000]
  distinguishes policy rejection from scalar-type failure.52 relevant selectors/
 54 closed schemas reproduce the full pipeline for all frozen instances.
- Fresh-DTB guard resolves actual APMIXED@1000c000/ID13/refclk26m, INFRACFG reset10,
 4KiB/source0x6c extent and disabled DSI PHY/PLL lineage.21 graph mutations reject;
  no claim actual reset/clock/PLL/controller function. Both fresh DTBs pass.
- Full registered5186-YAML contexts32→31(19unmatched/12validation),26→25(16/9),
  only MIPI unmatched removed/no additions. Gunyah warning/disabled AFE unmatched/
  exit1/passedfalse retained; DTBs/source/disabled states unchanged. New exact-head
  metadata checks required before merge; no redundant kernel build for schema.
- Next existing independent #27 source is disabled MT8163 DSI controller actual
  variant/IRQ/clock/power/probe/resource ownership. No guessed compatibility or
  device action. Thermal/physical PHY/clock/recovery/beta gates remain unqualified.


## 2026-10-29 — #27 finite actual DSI source contract

- PR431 merged3bb81d6b atd503ce8 after five exact-head checks/471 CI tests/35
  metadata+type controls/two fresh graphs. Exact normalized receipt now public
  evidence/mipi-binding/ci-result.json; prior new-CI-required text historical.
- Pinned donor35854B plus cachedACK34699B, protocolheaders26478B and bounded DRM
  master/Kconfig/Makefile38023B source in evidence/dsi-source; legacy DSIC/header
  already cached/tracked. Actual descriptor cmdq200/VM130/bypass/noVM flags found,
  no MT8173 alias. Legacybypasshelper commented, VM_DONE enableuncommented; no
  IRQabsence/hardwarebehavior claim. ACKmaster lacks MT8163 MMSYS/component data.
- Actual selected C RAM ASan/UBSan witnesses retained invalidformat reference,
  false later success/caller enable, ignored PHY powererror, bind resetfailure
  afterencoderinit, attach fieldcommit/lookup/bridge ownership andnine probeerrors.
  IRQfailure unregistershost; component add ishostattach, notprobe. Kernel caller/
  devres/clock/power/bridge/reset frameworks mocked, no physical failure observed.
- Actual cmdq writers on12 syntheticbuilder cases showdonor globalHSTXchange and
  layoutbounds: legacy128words ->508B payload;509 reachesnextword;1020 wraps u8
  countzero. No measuredhardwaredepth/corruption or panel commands. New source
  intent must boundinputs/widths andscope flags/initialcmdmode toMT8163.
- NEXT actualkernelimplementation, not anothermodel: scopedvariant/lifecycle/
  fault/cleanup/host/bind/queue handling+oldSoC controls/atomicapply/explicitbuiltin
  DSI/master/PHY/config/Image. Sourcecontroller integration isnot fullMMSYSpipeline
  orpanel support. AllDTs/disabledstates/31/25failedcontexts/runtimegates unchanged.


## 2026-10-29 — #27 actual isolated DSI implementation

Implemented a three-target locked ACK patch, MT8163-only descriptor/checked
power/ref/cache/cleanup/host/probe/packet backend, and component identification
without MMSYS pipeline data. Existing SoC bodies/descriptors remain unchanged.
All-output shadow preflight handles absent new header and rejects input/output
or revision drift before target writes. Separate builtin DRM/DSI build wrapper
preserves prior build scripts and requires real mtk_dsi.o/mtk_drm_drv.o probes
and final distinct Image marker; no aggregate object target or QEMU claim.

Actual RAM test found ACK CMDQ_SIZE0x3f narrower than the legacy128-word layout:
508B truncates count. Scoped cap248B fits63 words;249/508 rejected. Native actual
patched helper/caller C with ASan/UBSan passes power/reference/cleanup failures,
bridge/DDP callbacks, bind/attach/probe/IRQ and bounded packet/read/error paths.
478 host tests pass locally. Commands: python3 scripts/audit_dsi_port.py;
python3 -m unittest discover -s tests; python3 scripts/ci.py repository --base
 d0eb1046bdd39b76094cebf0fed234974934c5eb. Prior432 final473-test CI receipt now
public in evidence/dsi-source/ci-result.json. Current implementation is NOT kernel
build accepted yet: exact-head dsi-provider object/config/final Image and PR
checks next. No DT/schema/device/PHY/panel/reset/security action. Full31/25
contexts/disabled states and all physical/loading/failed-return/log gates remain.

PR433 opened at b818202bc31cce3877af2370386060a066290da9. Initial Linux
repository gate found a GCC unused-but-set value in the RAM poll mock (Clang
accepted it); fixed the mock to evaluate the actual condition, without warning
suppression or kernel source change. Superseded build40871144375 cancelled;
replacement exact-head dsi-provider build required after the fix. Private binding
controls also expose missing candidate panel graph: full dt-validate suppresses
disabled-node validation errors, so unmatched removal is not graph acceptance.
No binding publication or DT change.


## 2026-10-29 — #27 accepted DSI source and matched disabled metadata

PR433 merged6f670e0346a278857eff946e5ab6bc82d6b168f1 after five head2109781
checks/478 tests and required Linux40871693672/job123440089189 passed. Actual
DSI/DRM object probes, builtin dependencies and final29374976B Image SHA
37d881065af7ece2b6ad707b8a26fba66348214482220275a632a8f7ee68d1aa accepted.
Three source hashes match lock; public build receipt separates pre-DSI Images
and pre-Image W1 object hashes. No runtime, panel or physical rollback proof.

Published source-matched DSI proposal/closed56-schema pipeline/40 actual frozen
controls/older policy preservation and fresh dependency guard. Source-DTB guards
pin IRQ195/MM domain0/MMSYS clocks34/35/reset23/MIPI PHY+HS ownership; actual panel
graph remains absent and selected-schema controls reject it. Do not invent graph
data or relax graph requirements. Full wrapper5186-YAML contexts canonical31→30
(18/12),isolated25→24(15/9) remove only DSI unmatched; disabled required-property
suppression hides missing graph in full wrapper, not acceptance. Both wrappers
still exit1/passedfalse; Gunyah warning/AFE unmatched retained. Fresh DTB hashes
b837e6cb/4480f085 unchanged. Commands and processing receipts in dsi-binding;
new exact metadata PR CI required. No new kernel build/device/DT/security action.


## 2026-10-29 — #27 finite actual display-PWM source/core prerequisites

Locked ACK/donor8532B drivers (identical), exact legacy PWM/header/register/clock
helper, and two capped official PWM core/API reads (67893+19649B). Actual selected
core+driver+legacy C ASan/UBSan RAM witnesses cover framework-valid disabled-change
output enable/cache divergence, raw period readback missing+1 over4096 values,
u64 period narrowing wrap before divider guard, zero-rate helper calls (mock
records zero denominator, no actual division), two clock failures/five probe
stages.65536 low-word states each: period operations16384equal(mask0xc00 differs),
commit2equal(legacy fullword1->0 vs modern bit0). Divider mask is10bits in both,
not11 from comment; subset masks are not hardware width proof. Legacy three-clock
API order/discarded negative injected returns recorded, no observed device error.

Actual accepted DTB PWM status is okay, correcting queued disabled lead; no DT
change, source Image/PWM builtin/variant/binding/runtime acceptance. Prior resolved
PWM_MTK_DISP=m only. Next actual scoped safety/lifecycle/field policy implementation
requires patched-C/oldSoC controls/preflight/new exact builtin object/config/Image.
No another source microtrace for settled callback errors. Full30/24 remains
failed, all physical loading/failed-return/log/thermal/panel gates open.434 final
CI receipt now public evidence/dsi-binding/ci-result.json. Reproduce audit script
and test_disp_pwm_source; native helper callbacks never touch devices.


## 2026-10-29 — #27 actual scoped PWM implementation

Added explicit MT8163 callback boundary/descriptor; old descriptors/ops/bodies
preserved. Scoped disabled handling ignores irrelevant parameters and never
enables; checked64-bit arithmetic/rate/range precedes narrowing/MMIO/cache.
Conservative source policy uses legacy-written10bit divider/period/13bit duty,
fullword commit1→0; rejects existing wider-period bits rather than inventing
hardware width. Encoded+1/overflow-safe readback, owned main/MM refs/mutex, resource/
override probe checks and idempotent ordered devm cleanup/fault cover publication
failure/removal without claiming physical shutdown. No DT/state changes or
hardware action; PWM source statusokay is preserved.

Actual shadow-patched C/core/native ASan/UBSan controls pass source reproducers,
64bit limits/26MHz quantization, errors/output preservation, MMIO/cache order,
65536 preservation states, six probe stages/publication failure/cleanup and all
older descriptors. Atomic input/all-output preflight negatives preserve targets.
Separate pwm-provider stages unchanged prior wrappers then builtin PWM object/
config/final Image with distinct marker; NEW exact-head Image required before
merge/binding. Prior435 final483-test CI receipt published with this actual code.
Full30/24 diagnostic contexts and all loading/failed-return/log/physical gates
remain open. No source-build or runtime success is claimed before actual CI.

Local full host suite488 tests passed; repository checks at base32979e5a passed.

## 2026-10-29 — owner-requested ordered roadmap and issue-to-PR control (#438)

Owner said practical progress was unchanged and requested a systematic board and
Valethon-style issue→PR sequence. Created dedicated hardware tasks#441–#447 and
split original combined#334/#335/#336 scopes; retained#22/#329/#330/#331 for the
four foundation groups. All14 now have staged source/build/device criteria. Added
entry decision#439 under operational recovery#344 and bounded source exception
#440 for existingPR436. Historical#106 is at GitHub's100-sub-issue limit, so preserve
it and place operational work under#344 instead of moving/deleting old evidence.

PR436 now correctly Fixes#440 and source-mergedc2de79d47b6d6b6dc5a026a68d0db331c37302a0
after all six exact-head checks at8ff8731 and actual488 tests/PWM object/config/final
29374976B Image SHAa8b730da8bcf53cb332bfe84e1d8a4a8eef6c665b36ead367b69ca380a326d42.
Its normalized receipt is published with this administrative change; no further
PWM binding scope starts, and no hardware/DT gate closes from this source result.

Project4 receives Execution order, Depends on, Acceptance gate and Primary PR,
matching status/delivery fields, native hierarchy, explicit task contracts and
manual row order. Default view remains unfiltered with completed scopes visible.
Stable ordered-roadmap.json and checker negatives enforce hierarchy,14 unique
hardware groups, backward acyclic dependencies, one primary task per PR, one active
implementation task, and explicit GO before physical entry. NO-GO completion is
not runtime admission. Replaced the operational queue and archived its old source
history. First real next task is#439 after roadmap#438 acceptance; no unrelated
peripheral bypass when blocked. Full30/24 and all physical/boot/log/beta gates remain
open. Raw board/API/build captures stay ignored under out/.

## 2026-10-29 — #439 first recoverable boot NO-GO decision

Used retained exact installed-route evidence; no repeated microtrace/stock capture,
new kernel build or device action. Decision explains why no cached route admits
PL7/LK3/TEE262 loading; specifies smallest diagnostic bundle and missing CPU/RAM/
transport/post-fixup DT/independent return/log/supply/thermal/abort contracts.
Historical separate Image/initramfs proofs are not an integrated candidate;
all seven ACM gates stay zero. Signed stock material/normal return/320KiB export
do not qualify experimental failure recovery or logs. Input hashes pinned in
evidence/first-boot-decision/decision.json.

Single next action: prepare existing345 exact-board mechanical inspection and
independent recovery/logging proposal within authorized planning. Request owner
approval only after a concrete physical procedure is ready for review; no opening/
electrical/firmware execution or peripheral bypass. NO-GO may complete439 decision acceptance but never admits347 or closes
346/348. Replaced obsolete watchdog-next/percentage section in current route
admission. Issue-linked PR and exact-head checks required before acceptance.

## 2026-10-29 — #439 direct working-project documentation correction

Read original k4y0z Douglas unlock guide (expanded newer-firmware warning), recent
page47 reports, Rortiz2 LineageOS17.1 and newly linked18.1 author threads in browser
after web502. Opening is explicitly not a normal installation prerequisite; it
is a possible failure fallback. Cached external brick9820 script directs minimal
BootROM whereas author's warning requires full for external brick scripts. Recent
reports describe this wrong pairing and failures, not controlled causation;5.7.1.0
question on reviewed page has no answer. Existing branch maxima are not whole-
route exclusion.18.1 maintainer requires prior unlock/TWRP and points to amazon-oss.

Pinned cached BoardConfig and recovery fix sources show packaging and modified-
layout dependencies. No source script executed, security relaxed, tablet opened,
ROM downloaded or device queried. Reopened439 software-first;345conditionalBlocked.
Followup stays same primary issue. Next exact software-branch proposal must resolve
package pairing/installed applicability/independent failure exit; no hardware-first
assumption, unrelated scope or new synthetic wrapper. Runtime347/346/348 stay open.

## 2026-10-29 — #439 concrete software-unlock proposal

Prepared one reviewable original external-brick/full-BootROM/TWRP proposal, not a
new helper or source microtrace. Offline preflight reverified three retained whole
archives and12 script inputs. Header reads establish bundled fastboot64 ELF x86-64
and fastboot32 ELF x86; current Darwin/arm64 cannot run them natively. No Linux
image, VM, executable replacement or ROM downloaded/executed.

Proposal specifies brick9820 as first destructive boundary, full v1.2 BootROM
only, no minimal/step2 mixup, remapped TWRP stage and stop at recovery. Lists actual
GPT/preloader/LK/TEE/RPMB mutations, uncertain5.7.1.0 applicability, existing helper
size/selector weaknesses, and lack of guaranteed software-only return on initial
failure. Exact stock material and later rooted/modified recovery return are not
claimed as independent rescue before successful unlock. No device action occurred.

Owner decision is explicit risk approval/rejection for this attended persistent
software attempt on prepared Linux x86-64. No case opening/electrical action
included. HOLD pending that decision/host; no unrelated peripheral work. Required
exact-head PR checks before accepting proposal; physical gates remain open.

## 2026-10-29 — owner-approved lab entry347 and urgent app QA

Owner approved software attempt and free use of destructive lab Linux/device,
with immediate reporting if broken.439decisioncompleted;347onlyActiveTask. Recovered
existing strict-key SSH connection from this thread's history after mistakenly
checking desktop VM inventory; dedicated lab is Linux/x86-64 with adb/fastboot/
PySerial. One expected DouglasAPI22,PL7/LK3/TEE262,bootcompleted,USBpower/100%
battery26C observed for pre-destructive identity/supply check. No mode or tablet
write. Three pinned original archives staged/unpacked separately; exact current
9299968B recovery and907705758B authenticated OTA transferred and hashes verified
on lab. Seven Python host files compile, bundled Linux fastboot version probe
passes. No existing ttyACM before entry.

Host ModemManager active; SSH account lacks sudo/noninteractive admin. Owner
explicitly wants admin rights; prepared one-time grant requested. Cannot grant
root from unprivileged account. No firmware mutation until serial/service setup
can be applied. Current private SSH args/workspace/receipts under ignored out;
never publish selectors/hostnames. Parallels inventory query stopped after hang;
no VMs changed and no VM provisioning needed.

Immediate owner priority is full Connect and passkey QA on these onlylab devices.
Known working ROM path precedes maintained-kernel completion. Source checks show
Connect minSdk24/current CI aarch64; Googlepasskeys needAndroid9/API28+, and current
Lineage18.1 source isARM32. Match APK/ROM ABI and test actual credentialprovider/
userverification/browser/PKCE/deeplink, not merely boot. No ROM/GApps downloaded
or account configured. Existing14 maintained-kernel hardware gates remain open.

## 2026-10-29 — #347 actual case-closed custom-recovery entry

Owner granted sudo; stopped ModemManager reversibly, installed temporary /run
USB/tty plugdev rules and preserved prior state. Stockfastboot identifiedDOUGLAS
with same serial. Once-only original brick9820 sentOKAY5.194s; owner's privatephoto
showedAllgood/unplug/poweroff/fullbootrom. Hoststatusreadfailed after deliberate
ownerUSBdisconnect, not a reason to retry. Owner poweredoff/reconnected; single
original FULL script handshook. Exact conditional no-short prompt ackedoneEnter;
no short or caseopening. Helper reportedGPT/RPMB/preloader/TEE/LK/payload/header
stages, exited0 at16:31:27UTC. This is not independent all-partition readback.

PostfullfastbootDOUGLAS observed. Partition size1100000 was unprefixedhex,
corroborated against actual GPT sectors51200..86015 =17MiB, notdecimal1.1MB;
initial conservativefitparser held until resolved. Original TWRPstage hash618590
ranonce: recovery_x13,512,704B send/writeOKAY, authorizeduserdataerase/MISCwrite/
rebootOKAY, exit0 at16:34:13UTC. ActualADB recovery transport/douglas/TWRP3.3.1-0
and kernel3.18.19-g51c2c8d5bfb observed. Retrieved22,493B recoverylog and130,931B
currentkernellog privately; exact hashes/publiclimits in runtime-result.json.

Legacycustomrecovery isPermissive; securegetvaryes and unlockedgetvarempty are
recorded, not relabeledunlockedflagpassed. Maintainedkernel/Android11/Connect/
passkeyQA have not booted/passed. Independent failed-load stockreturn and retained
failurelog gates stayopen. No observeddamage, no caseopening/electricalaction.
All actual scripts/receipts stay in same347/PR452, not a newmicro-issue/PR.

## 2026-10-29 — #347 actual Android11 ROM and Google-services installation

Owner confirmed TWRP startup swipe. USB initially absent; later Linux enumerated
recovery again without another unlock/reflash. Verified staged ROM SHA8dacd21b
and boot remapping to physical p5/system p14. One new install accepted after the
previous unaccepted CLI request: actual system block writes, script succeeded,
updater RC0, 59s and menu return. Read-only installed system confirms Android11,
API30, ARMv7. Android first boot was not requested until Google services completed.

Original ARM11 GApps uses recovery uname, which reports aarch64; recovery ABI
property reports arm64-v8a while installed Android ABI is armeabi-v7a. Exact
package ARM toybox executed with explicit shell RC0 (uname armv8l). Local installer
correction checks helper executability and installed-system ABI separately,
retaining original SDK guard. 35 actual shell ABI cases and three helper-exit
cases pass; source-hash rejection precedes output creation. All29 payload members
unchanged, stale archive signature metadata removed explicitly; no publisher
signature claim. Initial archive verifier reused mutated ZipInfo offsets and
failed before any install; copying ZipInfo fixed validation. Only verified v2
archive installed. Actual GApps copied files, cleaned/unmounted, Done/updaterRC0
and menu return. Exact receipts in approved-lab-entry/qa-install-result.json.

497 current host tests pass. First Android boot requested once at22:31:15UTC;
completion/provider/browser/Connect/passkey QA still pending. No maintained-kernel,
failed-load stock return or retained-failure-log admission inferred. Preserve
rollback assets until no longer needed and delete temporary installers afterward.

## 2026-10-30 — #347 Android home screen and authorized runtime

Owner completed setup using their own Google account and confirmed home screen;
reported device-policy enrollment failed because device cannot be encrypted.
Authorized ADB now reports device transport, sys.boot_completed=1, setup_complete=1
and provisioned=1. Android11/API30/ARMv7 Lineage18.1-20261026 confirmed.
Runtime ro.crypto.state=unsupported, crypto.type empty, SELinux Permissive,
security patch2024-02-05, ro.secure1/ro.debuggable1. These are actual donor-ROM
limits, not policy bypasses or maintained-kernel qualification. No account data,
PIN, credentials or user content read.

Allowlisted package versions: GMS20.45.16, PlayStore53.8.11 updated package plus
20.4.33 system baseline, GSF11, AOSPWebView146.0.7680.153, Jelly11 defaultbrowser;
Chrome absent. Browser/provider/passkey ceremonies and matchingARMv7 ConnectAPK
remain unmeasured. Official Android CredentialManager documentation confirms
API28+ minimum for passkeys; API30 alone is not actual provider acceptance.
Public sanitized receipt android-runtime-result.json. Owner physical steps must
be batched to avoid repeated trips between rooms.

## 2026-10-30 — owner roadmap correction: platform release, branding, then app QA

Owner does not want Connect/features QA until stable fully updated release.
Installed LineageOS18.1 remains interim lab baseline, not finished public OS.
Project-branded boot/setup/wallpaper/launcher/About identity is a release requirement
under existing#333, retaining attribution/license notices and truthful Android and
security-patch fields. #333 now explicitly selects supported upstream/patch/component
versions and update path and validates stability/security. #354 reviews exact notices
and public artifact obligations; #340 packages branded stable updated release; #341
admits app QA afterward. No new micro-issue/parallel active implementation created.
#347 remains current entry acceptance; #346/#348 next in order. Existing donor-ROM
encryption/Permissive/2024patch facts remain limitations, never renamed as passes.
Project overview/current-delivery sections and visible board fields updated/read back.

## 2026-10-30 — owner-approved ValethonOS project/repository identity

Owner selected ValethonOS for Android and explicitly approved repository rename.
GitHub repository is now TOVSWORLD/ValethonOS-Android; local origin updated.
Project4/epic/current issues, repository description, current README/roadmaps,
contribution/security links, issue-form display choices and release-category name
use ValethonOS identity. Historical evidence/source locks, build paths, scope labels
and CI check identifiers retain stable engineering IDs; no runtime asset rebrand
is claimed. Actual OS branding implementation remains ordered#333 release work.
Old project overview was stale pre-boot text; replaced with measured milestone,
interim-vs-public distinction, current/next issues and instructions to follow fields.
Large board mutation hit transient502; same requested values replayed in bounded
batches and verified by readback. No gate/status/order/primaryPR was silently changed.

## 2026-10-30 — phase progress made visible; stale fallback/log scope corrected

Owner said Phase gates did not show where we are or current work. Audited all30
ordered task states plus native phase children. Inspection345 still had obsolete
approval/Linux-host blockers despite completed case-closed entry; closed NOT_PLANNED
and labeled as unneeded route, not hardware tested.348 now distinguishes completed
normal recovery/current-kernel log capture from untested failed-boot retention.
346 was already CLOSED/COMPLETED and boardStatusDone while DeliverystateBlocked;
preserved closed state, aligned presentation and kept remaining failed-load gate
explicit under phase344/release acceptance. No unsupported runtime pass inferred.

Added visible Current work field and replaced10 generic phase summaries with
achieved/current/next/blocker/concrete-exit information. Queued/history/complete
phases explicitly say no implementation runs. Phase view places progress fields
ahead of child-count widgets; exact Execution order/PrimaryPR/hierarchy retained.
All-gates view retains completed/dropped scopes. Current physical operation: none.

## 2026-10-30 — #347 actual entry acceptance reviewed

Reviewed original GO/owner authorization, exact starting generation/package pairing,
FULL/hacked-fastboot/TWRP endpoints, actual current logs, recovery restart and later
Android11 home/setup/authorizedADB observations against issue347's bounded-entry
acceptance. Accepted only the selected persistent software route/interim endpoint;
no maintained-kernel, security, public-release or failed-load return/log gate inferred.
ENTRY-ACCEPTANCE.md links exact observation-time receipts and accounts for deliberate
disconnect, unaccepted CLI request, stop/retry limits and known security limitations.
Next phase344 handoff is a concrete independent return/log proposal using retained
assets; no device action or repeat installation is implied. Phase344 stays open.

## 2026-10-30 — #346 one-visit recovery preparation

Owner clarified that chat desk and server room are separate: no chat reply is
possible beside the tablet. Added explicit-arm Linux supervisor with10-minute
travel/disconnection wait followed by one90-second reconnection/helper bound.
It pins original helper/common/logger sources, rejects wrong/ambiguous MediaTek
ports, never auto-discovers/opens unrelated serial nodes and kills the helper
process group on timeout. Exclusive private attempt receipt prevents silent reuse.
Default preflight opens no serial interface and does not change tablet mode.
Eight negative/lifecycle tests plus full505 host tests passed. Dedicated Linux
staging returned PREFLIGHT_OK; NOT_ARMED with matching source identities and current
Android USB port. No listener/helper/device action started; actual TWRP entry and
failed-load return/log retention remain unmeasured. Draft PR453 stays on existing346.

## 2026-10-31 — #346 attempt1 exposed host timing error

Owner authorized one attempt and performed the one-visit batch. Supervisor timed
out before helper log creation. Owner home screen and ADB device/boot_completed1/
Android11 verified. Retained host kernel timestamps show preloader enumerated
111.33seconds after disconnection, beyond the original90second combined reconnect/
helper window. The FACTORYM helper never launched; protocol compatibility remains
untested. Corrected host design to separate600s travel,300s manual shutdown/reconnect
and90s actual helper bounds; one launch/no retry preserved. Eight lifecycle/negative
tests and repository check pass. Sanitized attempt receipt recorded; raw USB journal
private. No rearming, reboot, flash, wipe or new physical request performed.

## 2026-10-31 — #346 actual Android-independent recovery entry

Owner performed the corrected one-visit batch; original FACTORYM helper exited0.
Owner special-menu observation corroborated by ADB recovery/TWRP3.3.1-0/douglas/
3.18.19-g51c2c8d5bfb. StageA existing recovery-entry path is now observed independent
of Android for the transition. No failed-load injected, no flashing/wipe/reinstall/
menu action/automatic reboot, no personal-data read. Tablet left in TWRP. Exact
sanitized attempt2 receipt recorded;346 failed-load return and348 failure retention
remain unqualified. Next work is concrete StageB artifact/transport/endpoint/log review.

## 2026-10-31 — #346 concrete StageB logging prerequisite

Read-only TWRP diagnostic-interface metadata shows last_kmsg/pstore/config.gz absent,
live /dev/kmsg available; no user data read. Historical diagnostic Image config
uses PSTORE_RAM=m with no modules in its isolated initramfs, so it cannot supply
that retention backend. Recorded prerequisite in346 before code; current policy
now requires built-in pstore RAM and console, disables block logging and rejects
the historical config as current-ready. Historical CI audit is explicitly labeled
and uses its original recorded policy; it does not replace a fresh resolved build.
Exact pinned ACK pstore Kconfig retained with provenance. No physical RAM address
selected, no reset/readout ownership inferred and no device action performed.

## 2026-10-31 — #346 built-in RAM logging kernel compile passed

Exact sourceb18254b/run41250510504 compiled successfully22:58:42–23:22:35UTC.
Completed log verifies PSTORE/PSTORE_RAM/PSTORE_CONSOLE=y and block backendn,
plus config/vmlinux/Image/Image.gz hashes. Sanitized diagnostic-build-result.json
records exact evidence. Workflow prints hashes but does not retain compiled files;
a later reviewed package build must explicitly export its artifacts. No boot image
packed/loaded, RAM region selected or retention/failure-return qualification inferred.
Tablet remains in existing TWRP; next is bounded load/readout contract, not another
blind compile or owner trip.
