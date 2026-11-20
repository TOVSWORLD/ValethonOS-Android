# First integrated Android candidate contents

November 19, 2026. These are verified source selections, not a resolved AOSP
graph, built image inventory or tablet runtime pass.

## Explicit selections

The Douglas product now selects `webview`, `Browser2`, `LatinIME`, `Settings`,
`DocumentsUI`, `DownloadProvider`, `DownloadProviderUi`, `PackageInstaller`,
`CertInstaller` and `ValethonReadiness`, alongside launcher, Provision and the inherited `com.android.adbd` device APEX.
The standalone `adbd` module is host-only in this product graph; do not add it
to PRODUCT_PACKAGES or accept its host binary as the device ADB output.
Most tools are inherited already; explicitly selecting them makes the required
scope visible. Make package lists tolerate repeated module names. Provider loader
and platform-support libraries are required by the pinned webview module itself.

Source captures and their immutable revisions/hashes are retained under
evidence/android-integration-source/product-contents. In particular:

- generic_no_telephony inherits handheld system/product/system_ext/vendor.
- handheld_product selects Browser2/LatinIME; handheld_system_ext selects
  Settings/launcher/Provision/SystemUI. Existing base/handheld system captures
  select installation, download, certificate and file tools.
- handheld_system conditionally includes frameworks/webview/chromium/chromium.mk,
  but there is no frameworks/webview project in this locked manifest. Explicit
  `webview` selection instead uses external/chromium-webview/Android.bp.
- That module supplies an ARM APK selected by RELEASE_PACKAGE_WEBVIEW_VERSION;
  captured framework config selects com.android.webview. The pinned source tree
  contains several versions, not a guarantee that a particular version is selected.
  Captured build/release trunk_staging selects 145.0.7632.218, and its ARM
  directory contains webview.apk (Git blob 35c7ea359566544997dffe1daf58afcccf8ecb1f).
  Verify the effective graph flag and actual built APK before candidate freeze.
  Its old snapshot is not current WebView security qualification.

## Manually launched readiness app

Valethon Readiness runs an offline HTML/JavaScript page with nine touch tiles,
an animated CSS activity bar and a keyboard input. No permissions, network,
JavaScript-native bridge, boot receiver, service, privileged grant or kiosk role.
The app blocks network and content/file access. Native text reports provider
initialization failures where catchable; an app crash does not intentionally
control launcher/ADB or boot completion. Native provider crash isolation remains
a runtime property to test, not an absolute guarantee.

Launch from the app drawer or authorized ADB:

```
adb shell am start -n com.valethon.readiness/.ReadinessActivity
```

HTML/JS/touch/typing success is not proof of GPU hardware rendering, networking,
Crestron support, storage persistence or security compatibility. Ordinary apps
remain independently installable; proprietary Crestron panel services are excluded.

## Branding, storage and hardware

Canonical intercom-derived animation is included by product staging. Existing
product identity remains Valethon Douglas Engineering; preserve truthful Android
and security metadata. No replacement launcher/device-owner setup is introduced.

See STORAGE-DECISION.md: retain volatile /data for first boot and preserve original
userdata. Persistent encryption/key management/write qualification remains open.
No new radio/audio/camera HAL is claimed or auto-enabled by these package changes.
Hardware-specific feature declarations remain subject to actual implementation.

## Actual-build gate

Run product graph validation before compilation. Retain resolved release flags,
module-info.json, installed-files inventory, image sizes and logs with exact input
hashes. Build required system/ramdisk and the module-info target. Then run:

```
python3 scripts/check_android_product_contents.py \
  --aosp-root /work/android \
  --product-out /work/android/out/target/product/douglas \
  --module-info /work/android/out/target/product/douglas/module-info.json \
  --aapt2 /work/android/out/host/linux-x86/bin/aapt2 \
  --report /work/android/product-contents-result.json
```

The gate requires real installed outputs for every named module, checks the
provider APK package/version using aapt2, finds animation/system/ramdisk, and
measures expanded sparse-system size against p14 (not compressed file length).
The configured 16-MiB filesystem reserve still needs build/filesystem evidence;
an image size alone does not measure free blocks. This gate does not replace
VINTF/policy/ABI checks, final boot-container placement, RAM budget, provider
signature/load checks or the grouped tablet T1/T2 session.
