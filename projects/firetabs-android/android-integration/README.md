# Maintained Android integration inputs

`platform-locked.xml` pins all 1,087 platform projects to the gitlinks in Android superproject `d6985d7ea38e602e9b1c94e2ebcbafacd7cc9892`, whose `.supermanifest` identifies manifest `29ace668ae756c7b8917c57abb440f6518844b0c`. The manifest and superproject project sets match exactly. Remote checkout URLs are explicit; no project revision is a moving branch. This is the June 17, 2026 source snapshot already selected by the Android 17 audit, not a current security-patch qualification.

The source capture, immutable URLs, hashes and missing-file results are in `evidence/android-integration-source/`. `scripts/lock_android_manifest.py` reproduces the resolved manifest from captured gitlinks and rejects missing/extra projects, moving revisions or unflattened includes. Four regression checks validate the actual project closure and reject incomplete lock inputs. No platform checkout, Android compilation or tablet Android boot is inferred from metadata capture.

## Kernel and ABI contract

Carry forward the observed arm64 ACK6.18 kernel, 4 KiB pages, correct 2 MiB RAM exclusion and the qualified display/touch/GPU configuration. Required native panel APKs are ARM32. The pinned `build/make/target/product/aosp_arm.mk` explicitly describes ARM32 userspace with the 64-bit Binder interface; its generic BoardConfig selects ARMv7-A NEON. This is evidence that an ARM32 product path exists, not a completed Douglas product or proof that all HALs/apps compile.

`kernel.fragment` enables BinderFS and built-in FUSE/FunctionFS. Pinned Android init mounts BinderFS and exposes binder/hwbinder/vndbinder; FunctionFS supplies authenticated adbd endpoints rather than the standalone ACM console. `kernel-apex.fragment` adds built-in loop/device-mapper/dm-verity and EROFS/FS-verity, derived from captured pinned apexd/APEX source. `scripts/build_android_provider.sh` preserves the existing graphics provider and checks resolved changes with `check_android_kernel_delta.py`. The source-only kernel compile is active; no resulting image has executed on the tablet. No standalone Binder/logging test is required.

## Graphics source findings

Pinned minigbm defines `android.hardware.graphics.allocator-service.minigbm` (AIDL allocator V3), `mapper.minigbm` (stable-C mapper), `libminigbm_gralloc` and gralloc4 helpers. Generic minigbm includes the MediaTek dumb-buffer backend, which selects the DRM driver named `mediatek`; it does not provide a Panfrost backend. Do not allocate scanout on the Panfrost render node. The display KMS and GPU render nodes must retain their distinct roles with compatible dma-buf import, formats and modifiers.

Pinned drm_hwcomposer defines `android.hardware.composer.hwc3-service.drm`, composer3 V5, init/VINTF fragments, and mapper4 metadata support. Its composer service runs as system with graphics/drmrpc groups. Actual mapper compatibility, buffer metadata, fencing and enforcing domains still need integrated qualification; listing modules is not acceptance.

## Compiled Bionic graphics path

The pinned AOSP Mesa tree lacks EGL/GBM/Panfrost Soong modules; its meson2hermetic route needs an unmerged converter/configuration. Instead, `scripts/build_bionic_graphics.py` implements Mesa's documented NDK/Meson integration using the **same Mesa 26.2.7/libdrm 2.4.133 sources as the working hardware demo**, rebuilt for Android. All configure/compile/install steps completed with official NDK r30 and `armv7a-linux-androideabi34`. This is actual ARM32 Bionic compilation, not reuse of glibc libraries or an Android image build. Hashes and failed source-build attempts are preserved in `evidence/android-integration-source/bionic-graphics-build-result.json`.

`scripts/package_bionic_graphics.py` validates real ARM ELF32 shared libraries, Android ABI notes, dependencies, SONAMEs and host-path/glibc exclusion. It emits four strict `cc_prebuilt_library_shared` modules and retains source notices; examples are in `graphics-package/`. Link-time-only Android ABI stand-ins are excluded from installed runtimes. EGL/GLES live under vendor/lib/egl; their Gallium dependency lives in vendor/lib. No Vulkan or GBM runtime is included; pinned Android minigbm supplies allocation. Release license audit and runtime compatibility remain open.

Pinned SkiaGLRenderEngine explicitly falls back to GLES2, and SurfaceFlinger recognizes `skiaglthreaded` as threaded GL/Ganesh. The product selects this path plus HWUI `skiagl` and advertises GLES2 only. Captured source/hashes are in `renderengine-source-inputs.json` and `framework-backend-inputs.json`. This source selection does not prove every Skia extension or rendering workload on T720; integrated qualification remains required. Do not advertise GLES3.1, Vulkan, CDD or GMS compliance.

## Douglas product candidate and full-build admission

`device/` contains source-controlled ARM32/Binder64 BoardConfig, product, init, readonly-system fstab, device manifest and labels. `scripts/stage_android_product.py` verifies compiled graphics and metadata hashes, keeps Soong ELF checks enabled, refuses conflicting checkout files and stages both source/package trees. Actual staging passed in an isolated control directory; **no complete Android checkout, product graph pass or full image compile has occurred**.

Existing p14 capacity is 1,692,925,952 bytes, with 16 MiB reserved. Vendor/product/system_ext co-locate in system; boot/recovery/vendor_boot/init_boot/userdata/cache images are disabled. First-home `/data` is volatile 256-MiB tmpfs; no original userdata/cache/metadata mount, format or migration is configured. This is an engineering profile, not persistent installation acceptance. Full build must resolve boot-required HAL/VINTF/policy and image fit; runtime must qualify memory, allocation/composition, enforcing SELinux and authenticated ADB. No bypass or generic GSI flash is authorized. A later system write needs verified original-system backup and concrete rollback/owner approval.

Next is kernel compile completion, full product graph validation and one complete system/ramdisk candidate, followed by grouped T1. Current snapshot is not security-patch or release qualification. Infrastructure resources, credentials, costs, caches, runner lifecycle, provider tickets and build tracking belong in private GitLab. Product source/hardware acceptance remains here under #331/#333.
