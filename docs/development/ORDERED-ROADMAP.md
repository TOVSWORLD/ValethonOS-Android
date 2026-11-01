# Ordered ValethonOS delivery roadmap

Owner correction,29 October2026. The objective is a recoverable diagnostic boot
with useful logs, followed by a coherent Android beta. Source/PR/test counts are
not a completion percentage. [Project4](https://github.com/users/TOVSWORLD/projects/4)
and its issue bodies carry live delivery truth; [ordered-roadmap.json](ordered-roadmap.json)
defines stable ordering, dependencies and acceptance contracts.

## Current delivery and owner release requirements — 30 October2026

- **Completed milestone:** the approved case-closed software route reached TWRP;
  Android11 LineageOS18.1 and Google services were installed. Owner home screen,
  completed setup and authorized ADB boot_completed=1 are measured under #347/PR452.
- **Current execution:** #347 entry accepted / PR452 merged. #346 demonstrated
  Android-independent existing TWRP entry. Diagnostic kernel compilation passed,
  but exact nonpersistent loading and compatible retained-log readout remain
  unresolved under draft PR453. #348 failed-boot retention follows; no device
  trial or build is running.
- **Interim versus public OS:** the installed upstream LineageOS build is a lab
  baseline. It is not the finished project-branded OS or a stable/current release
  acceptance. Its patch level is2024-02-05, encryption reports unsupported and
  SELinux is Permissive; device-policy enrollment failed. None is hidden by branding.
- **Public platform target, #333:** select supported Android/upstream maintenance,
  actual security/component versions and update path; integrate and test stability,
  security and project OS identity. Own boot animation, setup, wallpaper, launcher
  defaults and About/build information must retain accurate upstream attribution,
  licenses, Android version and security-patch details.
- **Release and QA, #340 → #341:** package the stable updated branded OS and its
  recovery/update/source handoff, then admit Connect/passkey/feature QA. App QA and
  app installation for QA are deferred until those platform gates pass.

This adds release acceptance requirements to existing ordered issues, not parallel
branding or peripheral tasks. One active implementation Task is #346. Existing
PWM exception#440/PR436 is source-complete, without hardware admission or new scope.

## Follow phase progress without opening every child task

Open [Phase gates — progress and next steps](https://github.com/users/TOVSWORLD/projects/4/views/2).
Each row shows achieved milestones, **Current work**, the specific next handoff,
remaining blocker and the concrete phase exit. Queued phases explicitly say no
implementation is running. Child-issue counts are not the progress measure.

Current phase1 has working interim Android11/recovery/ADB. Entry acceptance passed
under#347/merged PR452. Conditional board inspection#345 is closed **not planned**;
no opening was needed. Ordinary/current-boot log capture is complete; remaining
#348 is explicitly failed-boot retention/retrieval. Issue#346 is reopened for remaining failed-load qualification;
its ordinary stock-return evidence is retained, while phase/release acceptance must
not infer a demonstrated failed-load return from the issue's closed state.

The all-gates view retains completed/dropped history. Future phase summaries identify
what source groundwork exists, what remains untested and the exact predecessor.

## How work proceeds

1. Select the earliest open task whose predecessor and explicit outcome gates
   pass. Mark that task Active on both Status and Delivery state before work.
   Parent Feature/Phase rollups do not count as parallel implementation tasks.
2. Work one implementation task at a time. Each PR has exactly one primary Task
   issue, and each task records its primary PR. Use `codex/issue-N-short-name` and
   `Updates #N`; use `Fixes #N` only when the issue's actual acceptance passes.
   Necessary follow-up PRs stay on the same issue; do not invent a micro-issue for
   each source fragment or test. Merge to development only after all required
   exact-head checks pass. Main receives development-to-main releases only.
3. Follow source contract → bounded implementation → exact candidate build →
   approved device qualification → sanitized acceptance evidence. Source/build
   success does not close runtime hardware issues. Keep the issue open until its
   actual acceptance is met, including required follow-up testing.
4. If blocked, record the exact blocker. Work only within that task or on a
   documented prerequisite inserted ahead of it. Update order/dependencies before
   coding. Do not jump to an unrelated peripheral. Material scope/risk decisions
   needing owner approval remain explicit; approval is never inferred from delay.
5. Keep Status=Delivery state and synchronize result/next/blocker/order/dependencies/
   gate/primary PR at selection, PR updates, merge and acceptance. Read back native
   parents, labels and board state. The default view keeps completed scopes visible.

A closed NO-GO decision is not permission for a physical trial. The entry task
requires an explicit GO and the reviewed package/recovery/log/safety conditions.
Pretrial provisions are reviewed before entry; independent failure-return and log
retention issues remain open until their actual observations pass. This avoids a
circular requirement to declare failure recovery tested before its approved trial.

## Phase 1 — Entry, independent return and useful logs

Operational phase#344 under feature#327 owns this work:

- **010 — #439:** decide exact-build route, smallest diagnostic package, CPU/memory/
  transport contract, pretrial recovery/log/power/thermal provisions, stop criteria
  and one concrete next action/owner decision. No repeated LK microtraces, stock
  captures or synthetic readiness wrappers as progress substitutes.
- **020 — #347:** execute only the reviewed admitted entry/bounded trial. No cached
  route currently qualifies. A NO-GO#439 does not unblock it.
- **030 — #346:** demonstrate stock return independently of the failed experiment.
  Already demonstrated ordinary stock return is not the missing test.
- **040 — #348:** prove attributable experimental boot/failure logs, retrieval and
  retention coverage. The known320KiB stock export is not that proof.

Issue#345 is a conditional exact-board inspection proposal, selected only if it
is a necessary route prerequisite. Historical phase#106 already has100 native
sub-issues; retain its evidence and open runtime exit, and add no more source
micro-scopes there. All operational entry/return/log work follows#344.

Standing authorization covers scoped low-risk lab diagnostics. High-brick-risk
unlock/downgrade/bootloader/security writes/electrical actions still require an
explicit reviewed procedure and approval. No security weakening merely for logs.

## Phases 2–5 — Boot foundation and usable Android

- **Phase 2,#21:** **050 — #22**, diagnostic memory/UART and internal-storage
  qualification after useful logs and return evidence.
- **Phase 3,#328:** **060 — #18** clock/reset, **070 — #19** pinctrl/EINT,
  **080 — #20** PMIC/domain qualification. Reuse completed source work; resolve
  only the active blocker and measure required behavior. A necessary first-boot
  source prerequisite must be explicitly inserted through#439, not used as a
  reason to restart broad provider/peripheral cleanup.
- **Phase 4,#23:** **100 — #329** display/backlight, **110 — #330** touch,
  **120 — #331** GPU/graphics composition, in that order.
- **Phase 5,#24:** **200 — #333**, one reproducible integrated Android candidate
  through setup/home UI, matching ABI/Binder/config/HAL inputs and SELinux enforcing.

## Phase 6 — Dedicated peripheral tasks

Each group has its own source/implementation/build/device-test plan and measurable
acceptance. Execute in this order after the preceding gate:

- **300 — #334:** Wi-Fi identity/firmware/HAL, integrity transfer and reconnect.
- **310 — #442:** audio AFE/codec/routes/HAL, playback and recording.
- **320 — #335:** battery/charging/model-qualified thermal behavior and safe limits.
- **330 — #443:** suspend/wake sources and ten controlled cycles.
- **340 — #336:** declared USB roles, actual receipt/integrity and reconnect/cleanup.
- **350 — #444:** SD integrity, clean unmount and controlled hotplug.
- **360 — #446:** declared video codecs, playback/seek/sync and actual acceleration.
- **370 — #441:** Bluetooth pairing, declared profiles and reconnect/wake.
- **380 — #445:** identified sensors, orientation/range/events/wake.
- **390 — #447:** identified front/rear sensors, ISP/HAL and camera modes/capture.

Together with internal storage, display/backlight, touch and GPU, these are14
broad hardware groups. This is a qualification inventory, not14 untouched drivers
or a percentage. None has experimental-kernel device qualification yet.

An unsupported item stays unqualified. If a beta scope exclusion is needed, stop
for an explicit recorded owner decision and amend dependencies/order before
continuing; do not mark an untested hardware gate Done or silently hop past it.
Pretrial supply/thermal safety remains mandatory even before full functional
charging/thermal qualification; no generic invented thresholds are permitted.

## Phase 7 — Complete candidate and admit QA

- **400 — #27:** final candidate-wide DT/dependency validation. Component binding
  work belongs to its ordered subsystem issue, not a separate pre-boot cleanup loop.
- **410 — #353** and **420 — #354:** owner first-party license decision and exact
  artifact redistribution/source obligations. Unresolved rights are not assumed.
- **500 — #340:** exact reproducible beta package, known limits and recovery/log handoff.
- **510 — #341:** measured A01–A07 admission review; no critical recovery/data-loss/
  thermal/security failure and no claim of passing an untested runtime gate.

Existing completed scopes#29,#339,#342,#343 remain visible as history. They do not
stand in for physical gates. The current next outcome is#346 independent recovery qualification, followed by#348,
not app QA or an unrelated peripheral PR.

## Validation of the roadmap

`python3 scripts/check_ordered_roadmap.py` verifies the14 unique hardware groups,
Epic→Feature→Phase→Task hierarchy, ordered acyclic dependencies, explicit GO gate,
primary-issue PR contract and single bounded pre-existing exception. Unit negatives
reject duplicate groups, forward/cyclic dependencies, wrong parent levels, missing
PR contract and an omitted NO-GO safeguard. This validates the plan; live readiness
still comes from current GitHub evidence, never from this static file alone.
