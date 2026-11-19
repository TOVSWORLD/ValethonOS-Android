# First integrated candidate: broad useful contents, bounded boot risk

Owner direction, November 19, 2026: include known later components wherever
they will not make the build, boot or existing diagnostics unproductive. Group
qualification on one candidate. This is a scope plan, not proof of inclusion,
successful compilation or hardware operation.

## Include and verify before freezing the candidate

- Existing ARM32/Binder64 runtime, maintained kernel, GLES2 graphics integration,
  enforcing SELinux, authenticated ADB and independent recovery path.
- Launcher, Settings, software keyboard, package installer, file browser,
  downloads, certificate management and standard network configuration UI.
  Resolve inherited packages in the actual product graph; avoid duplicate or
  obsolete module names. Source presence does not prove installation.
- An actual ARM32 WebView provider and its framework/provider configuration,
  subject to provenance, licensing, API/graphics compatibility and image fit.
  The captured handheld product only conditionally includes chromium.mk;
  WebViewBootstrap alone is not evidence of a usable browser engine.
- A small app/browser test payload or separately installable companion package
  to exercise WebView, ordinary app installation, touch and graphics together.
  Keep optional tests manually launched, without privileged boot services.
- Lightweight Valethon identity, wallpaper, launcher defaults and boot artwork
  where existing assets are ready. Preserve accurate upstream/security fields.
- Existing Android debugging tools and useful passive diagnostics. Do not add
  another standalone logging qualification or a second USB gadget owner.
- Source-ready standard connectivity/media components for grouped T2 checks.
  Declare hardware feature XML and start hardware services only for integrated
  implementations; do not advertise unsupported radios, cameras or sensors.

## Optional components must not become boot dependencies

Ordinary applications and an eventual panel-mode manager should be installable
and manually selectable. Do not replace the known launcher, enable kiosk/device
owner mode, add privileged permissions or auto-start experimental services for
first home. Proprietary Crestron APKs and missing native panel services are not
approved redistributable system components. ARM32 support is already selected;
app-specific compatibility still requires testing.

Wi-Fi/BT transport/firmware and audio routing are unresolved in the hardware
contract. Include implementations only after source integration is concrete;
framework packages or a successful compile do not establish working hardware.

## Persistence is an explicit storage design, not a package addition

Current /data is 256-MiB volatile tmpfs. Before freezing, assess a separately
backed, opt-in persistent-data profile and required filesystem/encryption/policy
support. Do not auto-mount, format or migrate original userdata, silently remove
encryption or substitute an unreviewed file-backed image. Preserve the temporary
profile as the explicit first-home fallback. Any persistent storage test needs
its concrete backup/write/restore plan; document unresolved blockers honestly.

## Freeze and grouped acceptance

Produce a resolved installed-package/provider inventory, feature/service list,
storage profile, licenses and measured system/RAM/boot-container fit. Existing
p14 is 1,692,925,952 bytes with 16 MiB reserved; no repartitioning or check bypass.
If optional contents do not fit, retain separately installable artifacts rather
than enlarge the image or impair boot. Freeze exact hashes after these checks.

Run T1 setup/home, graphics/touch, enforcing SELinux, authenticated ADB and final
recovery, plus source-ready T2 suites on that same candidate. Optional app
failures must leave launcher, ADB and diagnostic access usable. Preserve the
incremental build workspace; later app installation need not rebuild Android,
while framework/HAL/policy changes can require new images and affected tests.

No full-build resource launch or new device write is authorized by this plan.
