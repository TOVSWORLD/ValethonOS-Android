# Active work queue — ordered delivery

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
  Diagnostic kernel compilation passed. Exact original-loader RAM handoff and an
  owned compatible retained-log writer/reader remain unresolved in draft PR453;
  no build or device operation is running. Ordinary return remains complete;
  #348 failure retention remains unqualified.
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
