# Douglas graphics/userspace integration

Primary issue: #331. Carries the physically observed display and nine-target
touch foundations from #329/#330. The owner selected staying in original TWRP
with the exact current candidate on p5 rather than returning to Android between
tests. Original rollback remains ready; recovery must remain unchanged.

The next candidate will exercise GPU rendering and visible DRM composition
with touch interaction. A repeated console banner/grid or driver probe alone
does not qualify this outcome. It is a preparation toward maintained Android
graphics/userspace, not an Android setup/home pass.

Use the pinned ACK6.18 Panfrost driver and existing MT8163 display pipeline.
The source identifies Mali-T720 at0x13040000 with job/MMU/GPU IRQ227/226/225,
MFG clock gate, MFG power domain and a fixed1.15V supply. Validate the actual
prepared DT and source relationships before enabling them. Preserve known
display, Goodix, watchdog and RAM reservations.

The official Mesa Panfrost documentation currently lists T720 OpenGL ES2.0
and OpenGL2.1, with no Vulkan. These are userspace-driver limits, not proof of
tablet support. Pin a maintained Mesa release and compile a coherent Panfrost,
EGL/GLES2, GBM/libdrm display path. Never count software rendering as hardware
acceleration. Android EGL/gralloc/composer and platform API compatibility
remain explicit integration requirements after the rendering path works.

Preparation order:

1. Build Panfrost and required DRM dependencies into the tested kernel.
2. Match GPU DT, clock, power, regulator and OPP contracts to pinned sources.
3. Build the renderer/runtime and enforcing policy; verify dynamic dependencies,
   required threading, device access and package memory/size limits.
4. Qualify the exact candidate offline and in VMs. Existing TWRP installation
   must expect the exact retained graphics predecessor, not assume original p5 is installed.
5. Load one qualified candidate and show actual animated GPU rendering with
   touch response. Keep an exact original-image rollback available.

The first physical graphics attempt displayed GBM failure digit2. The exact
failed DT left MFG_ASYNC6 and its MFG7 child disabled, preventing registration
of the referenced domain7. Enable both domains while preserving active MM0;
see `evidence/graphics-source/power-domain-correction.json`. The corrected
candidate is not yet hardware-qualified.
No new logging proof gate, userdata access, recovery write or automatic trial
retry is selected.

References: [Mesa Panfrost](https://docs.mesa3d.org/drivers/panfrost.html),
[Mesa Android build](https://docs.mesa3d.org/android.html),
`evidence/touch-input-source/touch-runtime-result.json`, and the central
`docs/development/DOUGLAS-HARDWARE-CONTRACT.md`.
