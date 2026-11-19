# Douglas engineering product inputs

Staged at `device/valethon/douglas`; paired with the hash-verified generated graphics package at `vendor/valethon/graphics`. Target: `valethon_douglas-trunk_staging-userdebug`. This is a source candidate, not a build graph pass, flashed image or Android runtime qualification.

Uses one ARM32 app ABI and Binder64 with the observed arm64 ACK kernel. System/vendor/product/system_ext are co-located in the existing p14 system image, as permitted by the pinned build rules; no vendor/super partition is invented. Image size is bounded by captured p14 capacity (1,692,925,952 bytes). The normal build must reject an oversized image; do not trim checks or repartition to force it through.

Builds system and ramdisk inputs only. Boot/recovery/vendor_boot/init_boot/userdata/cache images are disabled. The direct-boot container must use the existing qualified loader path and integrated BinderFS/FUSE/FunctionFS kernel delta, not an emulator boot image. The kernel bootargs must identify `androidboot.hardware=douglas`; final boot image/initrd size, RAM placement and policy checks remain required.

The first-home profile mounts a 256-MiB volatile tmpfs for `/data`. It has no userdata/cache/metadata fstab entry, encryption setup, formatting or migration path. This keeps the first Android framework attempt separate from adopting the existing installation's data. The RAM allowance is unmeasured and may need tuning with the actual low-RAM Android boot. It is not a persistent installation or storage acceptance result.

SELinux stays enforcing. Library labels use the existing same-process HAL type; no permissive domain, privileged blanket allow rule or version check bypass is included. Actual policy compilation, mapper/composer/graphics ABI pairing, missing boot-required HALs, memory footprint, image fit and first-stage mount behavior must be qualified by the complete build and integrated test. No hardware-backed keystore or release/security compatibility is claimed.

A device VINTF base manifest is included; installed graphics modules provide the captured allocator/mapper/composer fragments. Actual framework/vendor compatibility must pass the full build.

The platform configfs/adbd flow uses the MediaTek MUSB UDC name `musb-hdrc.0.auto`; its actual Android bind/auth behavior must be qualified. FunctionFS is enabled in the integrated kernel fragment because the achieved ACM console does not supply an ADB FunctionFS endpoint. ADB authentication is retained; no private host key is embedded.

No tablet operation is implemented here. A later p14/system write would require a concrete reviewable test plan, verified complete original-system backup, matching rollback artifacts and explicit owner approval. Existing TWRP and original userdata remain outside this source build's write scope.
