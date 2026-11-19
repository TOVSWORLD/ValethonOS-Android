# Maintained Android integration inputs

`platform-locked.xml` pins all 1,087 platform projects to the gitlinks in Android superproject `d6985d7ea38e602e9b1c94e2ebcbafacd7cc9892`, whose `.supermanifest` identifies manifest `29ace668ae756c7b8917c57abb440f6518844b0c`. The manifest and superproject project sets match exactly. Remote checkout URLs are explicit; no project revision is a moving branch. This is the June 17, 2026 source snapshot already selected by the Android 17 audit, not a current security-patch qualification.

The source capture, immutable URLs, hashes and missing-file results are in `evidence/android-integration-source/`. `scripts/lock_android_manifest.py` reproduces the resolved manifest from captured gitlinks and rejects missing/extra projects, moving revisions or unflattened includes. Four regression checks validate the actual project closure and reject incomplete lock inputs. No platform checkout, Android compilation or tablet Android boot is inferred from metadata capture.

## Kernel and ABI contract

Carry forward the observed arm64 ACK6.18 kernel, 4 KiB pages, correct 2 MiB RAM exclusion and the qualified display/touch/GPU configuration. Required native panel APKs are ARM32. The pinned `build/make/target/product/aosp_arm.mk` explicitly describes ARM32 userspace with the 64-bit Binder interface; its generic BoardConfig selects ARMv7-A NEON. This is evidence that an ARM32 product path exists, not a completed Douglas product or proof that all HALs/apps compile.

`kernel.fragment` records two concrete integrated-kernel changes: enable BinderFS, which pinned Android init mounts and links as `/dev/binder`, `/dev/hwbinder`, `/dev/vndbinder`; and make FUSE built-in rather than depending on an unshipped module for Android emulated storage. Existing resolved kernel has Binder IPC/COMPAT/SELinux but BinderFS disabled and FUSE modular. Merge into the integrated kernel build and inspect resolved config before packaging. No standalone Binder/tablet/logging test is required.

## Graphics source findings

Pinned minigbm defines `android.hardware.graphics.allocator-service.minigbm` (AIDL allocator V3), `mapper.minigbm` (stable-C mapper), `libminigbm_gralloc` and gralloc4 helpers. Generic minigbm includes the MediaTek dumb-buffer backend, which selects the DRM driver named `mediatek`; it does not provide a Panfrost backend. Do not allocate scanout on the Panfrost render node. The display KMS and GPU render nodes must retain their distinct roles with compatible dma-buf import, formats and modifiers.

Pinned drm_hwcomposer defines `android.hardware.composer.hwc3-service.drm`, composer3 V5, init/VINTF fragments, and mapper4 metadata support. Its composer service runs as system with graphics/drmrpc groups. Actual mapper compatibility, buffer metadata, fencing and enforcing domains still need integrated qualification; listing modules is not acceptance.

Important build blocker found before paying for a full build: the pinned AOSP Mesa tree contains generated Soong files but no `Android.bp` for EGL, GBM or the Panfrost Gallium driver. Existing generated driver files cover llvmpipe/zink and virtualization paths. Do not invent `libEGL_mesa`/Panfrost product packages and assume those modules exist. The pinned `README.aosp.md` describes meson2hermetic generation; the referenced converter is an unmerged upstream change, and the expected `hermetic/android` project configuration is absent from this Mesa tree. The direct GitHub connector verified converter commit `c5855fbe801e315b1e0429c43d7eee0a0c5b2d3e` and upstream PR15462 remains open. Neither converter execution nor generated driver qualification is claimed.

The already-qualified Linux/glibc Mesa demo cannot be copied into Android/Bionic. The next implementation work is the source-controlled Bionic EGL/Panfrost build integration and complete Douglas product/device configuration, followed by build graph validation. Preserve the functioning kernel and hardware choices. T720 GLES2/no-Vulkan constraints remain in the hardware audit; do not advertise GLES3.1, Vulkan, CDD or GMS compliance.

## Full-build admission

Not ready for a paid full build: complete Douglas product/BoardConfig, boot/root/init/fstab layout, graphics build generation, allocator/composer pairing, device SELinux/VINTF, adbd and exact artifact/storage/rollback packaging still need closure. No generic GSI is authorized for flashing. Revision closure solves reproducibility of source inputs; it does not replace those implementation requirements.

Infrastructure resources, credentials, operational costs, caches, runner lifecycle, provider tickets and build run tracking belong in the separate private GitLab project, not public issues. Product source and hardware acceptance remain here under #331/#333 and the grouped T0/T1 test plan.
