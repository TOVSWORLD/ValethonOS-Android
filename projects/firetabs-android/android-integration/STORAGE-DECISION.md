# First candidate storage decision

Decision November 19, 2026: retain explicitly volatile /data for the first
integrated engineering boot. Do not auto-adopt existing Android userdata or add
formatting, migration or encryption changes. This does not satisfy persistent
installation acceptance. Apps/settings/ADB authorizations stored under /data can
be lost on every reboot; test instructions must account for fresh authorization.

## Why a persistent switch is not ready

- The maintained kernel physically verified original boot-partition reads.
  Writable filesystem integrity, crash consistency and Android /data have not
  been qualified by that result.
- Captured parent kernel configuration has ext4 and security labels built in,
  but FS_ENCRYPTION and DM_CRYPT disabled. The bounded integrated Android delta
  adds loop/APEX support, not the missing encryption stack.
- The product has no qualified KeyMint/secure-storage integration, fstab data
  encryption profile, key provisioning or recovery design for a new data volume.
  Silently choosing unencrypted persistent data is not an acceptable shortcut.
- The original userdata belongs to the retained installation; adoption could
  modify it even without an explicit format. No verified separate scratch
  partition or approved removable-media fixture is available in this design.

## Intended persistent profile and reusable work

Use a separately identified, backed-up data target only after capacity and
ownership are verified. Define fstab/filesystem, encryption/key management,
SELinux labels, vold/init behavior, corruption handling, explicit format and
rollback together. Preserve an independently selectable volatile profile for
recovery/bring-up. Never select an arbitrary block path from a name-only alias.

External SD is a possible later target, not a ready fixture: its maintained host
and hotplug/write path also require source integration and qualification. A loop
file on original userdata still writes the original installation and does not
avoid its encryption/mount/backup issues.

Keep standard Android storage services and the compiled kernel artifacts/source
workspace. The eventual filesystem/crypto kernel delta and init/fstab/policy
changes can be rebuilt incrementally; a second clean AOSP build is not inherently
required. Do not include a boot-time selector that falls back to formatting or
silently mounts the original installation.

The first candidate's 256-MiB tmpfs is an unmeasured engineering allocation. Check
actual /data usage, low-memory behavior and package/provider startup in T1. If it
is insufficient, adjust from evidence without consuming unbounded RAM. Preinstalled
WebView/readiness assets in read-only system avoid reinstalling them after every
reset, but do not make their settings persistent.

## First-home security-service dependency correction — November 20, 2026

The actual Android VM revealed that keystore2 aborts without a default
KeyMint/Keymaster instance. The first image did not install one. Add the pinned
AIDL nonsecure KeyMint reference service and AIDL Rust nonsecure Gatekeeper APEX
for the volatile-data engineering profile. They are software implementations,
not evidence of hardware-backed key isolation, CDD compliance, persistent
credential protection or release security qualification. Original userdata and
recovery remain excluded. Do not suppress keystore's critical-service failure or
weaken SELinux to manufacture first-home success. Qualify the actual services in
the real Android VM before the next grouped tablet session.
