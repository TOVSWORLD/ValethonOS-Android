# Shared staged tests toward maintained Android

Updated November 19, 2026 at the owner's request. This plan groups issue
qualification into candidate sessions; it does not authorize device writes or
claim untested hardware. Machine mapping: [ordered-roadmap.json](ordered-roadmap.json).

## Current result and next major outcome

Standalone maintained-kernel display, touch and animated GPU/tap/drag operation
are observed. The latest exact graphics image and original recovery were verified
in original TWRP; no test/helper remains active. Do not repeat those standalone
proofs or make custom logging a new admission gate. #348 remains a non-blocking
follow-up; useful passive diagnostics can be retained inside the same session.

The next major outcome remains **maintained Android reaching usable setup/home,
with display/touch, enforcing SELinux, USB/ADB and verified recovery** (#333/#24).
It is reached through T0 and T1 below. Peripheral and release stages are later
acceptance, not extra prerequisites for first usable Android.

The three engineering packages remain: integrate one Android stack, build/qualify
one complete candidate, and test the integrated system. The stages below are
shared tests inside those packages, not additional owner milestones or a promise
of a fixed number of attempts.

## T0 — Offline integrated-candidate gate

No owner/tablet session. Issues #18/#19/#20 supply source-backed clock, pin and
power readiness; #329/#330/#331 supply the observed display/touch/GPU paths;
#333 owns the integrated Android package.

- Pin Android/device/ABI/Binder/firmware/HAL and kernel inputs. Resolve the
  documented T720 API limits against the actual Android graphics path.
- Integrate allocator/composer/EGL, Android init/adbd and enforcing SELinux.
  Keep existing working hardware unchanged unless a concrete dependency requires
  a change; collect all source-ready integration changes into one candidate.
- Build reproducible artifacts, perform candidate-required interface/policy/DT/
  memory/package checks, and retain precise hashes and results.
- Reuse #22 read-only-storage evidence. #27 contributes only candidate-required
  dependency/binding checks here; its full release corpus remains T3.
- Prepare exact storage/backup/install/rollback actions, owner instructions,
  candidate-specific time bounds, stop conditions and recovery method. Verify
  build-host capacity before bulk downloads. Obtain concrete resource/write
  approval where required; grouping itself grants no additional authorization.

Exit: one reviewable, reproducible integrated test package with mandatory T1
checkpoints ready. Do not require every peripheral issue to be ready.

## T1 — One integrated Android boot/UI session

One candidate installation and boot, shared across #329/#330/#331/#333. Check:

- Android init/compositor reaches actual setup/home on the maintained kernel.
- Display/backlight, basic brightness, tap/drag and ordinary UI navigation work.
- SELinux is enforcing; authorized USB/ADB is usable. This is the core USB
  checkpoint under #333/#336, not full USB-role/integrity acceptance.
- At session end, execute the approved return procedure once under #346 and verify the
  required exact partitions/configuration and independent recovery.

If ready and approved, continue directly into selected T2 checks on this same
running image before that final return. T2 depends on T1's functional UI entry,
not an intervening recovery/reinstall. The first-home milestone is recorded only
when its mandatory checks and the shared final return have passed.

Do not mark all of #329/#330/#331/#333/#336 done from a UI smoke pass: each keeps
its remaining brightness, touch, API/composer, transport, release and stability
acceptance. No separate display-only/touch-only/cube-only boot is planned.

## T2 — Functional suites on the same candidate

After T1 UI entry, run only source-ready, explicitly selected/approved checkpoints.
Unready hardware or absent fixtures are `not_run` or `blocked`; they do not
prevent other independent ready checks or the first-home milestone. Preserve all
issue acceptance rather than silently excluding a feature.

- **T2A connectivity/power:** Wi-Fi #334, Bluetooth #441, declared USB/data
  integrity #336, charging/battery/thermal #335. Capture reconnect/state checks
  together while the candidate is already running. Model-specific power limits
  and measurement requirements remain binding.
- **T2B media/input/storage:** audio #442, video #446, cameras #447, sensors #445,
  SD #444, display/touch follow-ups #329/#330. Use shared fixtures/session and
  capture the outcome for each issue. SD/hotplug runs only with the required card
  and approved procedure; unsupported modes never count as a pass.
- **T2C lifecycle:** suspend/wake #443 and related display/touch/#333 follow-ups.
  Requires actual #335 power/thermal readiness before these checks; do not infer
  it from an unrelated group pass. Retain the existing ten-cycle acceptance and
  recheck qualified input/network/audio/storage state. Repeated-boot/stability
  follow-ups stay distinct from first-home acceptance.

All selected stages share one final recovery. Failed prerequisites stop the
affected/dependent checks. A boot/return/storage/security/power-critical failure
stops the session and invokes the prepared return procedure; preserve completed
results. A later changed candidate repeats affected checks plus the common
boot/return guard, not every historical standalone proof.

## T3 — Release validation and handoff

After the required hardware scope is qualified, #27 full candidate-wide validation,
#333 full stability/security/update contract, #340 package/recovery handoff and
#341 admission review consume the shared evidence. Existing licensing #353/#354
and supported-client prerequisites remain explicit; no scope is waived by a
batch pass. This stage is beyond the next first-usable-Android milestone.

## Issue, dependency and evidence rules

- Keep one active implementation task and one primary issue per PR. Source and
  offline readiness remain serial/documented. Runtime acceptance may be earned
  together in the approved shared stage; do not require one physical trial per
  issue or wait for a predecessor runtime pass that the same candidate must prove.
- #331 Android composer/API work may hand off source/interface-ready inputs to
  #333 while both runtime acceptances await T1. Neither issue is falsely closed.
- Use one evidence pack per exact candidate/session, keyed by candidate hash,
  stage, checkpoint and issue. Each checkpoint records `pass`, `fail`, `not_run`
  or `blocked`, observations and limits, and the issue(s) it supports.
- Link that same evidence into every affected issue. Record one grouped owner
  procedure/approval and one prompt per stage or required action, not per issue.
- Retain historical failures and untouched acceptance text. A shared session is
  a work-time improvement, not a pass inferred from source, VM or queued bytes.
