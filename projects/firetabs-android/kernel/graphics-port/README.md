# Douglas graphics/userspace integration

Primary issue: #331; implementation/evidence PR #456. The maintained 6.18
kernel now renders a GPU cube that the owner observed moving and responding
to taps and dragging. Exact candidate `628a1641...` rejects non-T720/software
renderers and validates rendered pixels before scanout. USB stayed connected.
The start prompt was not seen; that UX observation does not invalidate the
actual interaction or justify another cube-only test.

[Physical result](../../../../evidence/graphics-source/graphics-interaction-runtime-result.json)
records observation and recovery separately. This is standalone functional
GPU rendering, not Android composer, full API conformance, broad stability or
maintained Android setup/home acceptance. Broader touch qualification remains
open under #330. Original recovery stays unchanged and exact rollback remains
available.

## Source-backed hardware and runtime

Mali-T720 uses registers at 0x13040000, job/MMU/GPU IRQs 227/226/225,
MFG clock gating, fixed 1.15V supply and the source-listed 416MHz parent.
Both MFG_ASYNC domain6 and nested MFG domain7 must be enabled. The first
candidate left them disabled; the power driver skipped parent6 and never
registered GPU domain7. Enabling exactly those two domains preserved the
observed display MM0, Goodix touch, watchdog and memory configuration.
[Correction evidence](../../../../evidence/graphics-source/power-domain-correction.json).

The pinned runtime is Mesa26.2.7/libdrm2.4.133 with Panfrost, EGL/GLES2,
GBM and MediaTek DRM/KMS. The enforcing policy retains storage/input write,
PID1 fork and executable-memory denials. The first-tap program draws one
waiting frame, permits up to15minutes arrival, then starts five minutes of
animation/input on first valid touch. Hardware interaction was observed with
USB connected; portable disconnected operation is not claimed as tested.

## Next outcome: Android graphics/userspace

Carry this working kernel/display/touch/GPU into the existing Android
integration outcome, toward issue333's maintained Android setup/home milestone:

1. Pin Android source/device configuration, ABI/Binder, firmware/HAL and update
   inputs against the existing maintained-kernel/source audit.
2. Integrate allocator/composer/EGL with this DRM/Panfrost display path, plus
   Android init/adbd and enforcing SELinux. Resolve the documented T720 GLES2
   limitation against the actual Android render path and declared API scope.
3. Build reproducible integrated artifacts and a concrete storage/rollback plan,
   then qualify one attended setup/home candidate.

Do not count this standalone demo as Android compatibility, substitute an old
Lineage baseline for the maintained platform, or add another logging/cube proof
gate for observed foundations. Full conformance, release stability, security
and updates remain explicit requirements.

References: [Mesa Panfrost](https://docs.mesa3d.org/drivers/panfrost.html),
[Mesa Android build](https://docs.mesa3d.org/android.html), and the central
[hardware contract](../../../../docs/development/DOUGLAS-HARDWARE-CONTRACT.md).
