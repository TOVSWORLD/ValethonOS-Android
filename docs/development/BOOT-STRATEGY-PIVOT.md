# Bolder fallback: remove kexec from the boot path

The owner requested this pivot if the single minimal reset-payload test fails
or remains inconclusive. Preparation is authorized; a new hardware procedure
must be concrete and have a reviewed restoration path before it runs.

The failed experiments all depend on carrying a running vendor kernel through
device shutdown, relocation and a warm entry into another kernel. Ordinary
bootloader entry has already booted the diagnostic Linux Image successfully.
The fallback uses that proven cold-boot path to reach a minimal non-Android Linux
environment, removing the warm handoff from the critical path.

## Work and acceptance gates

1. Inventory the device's already established bootloader/recovery capabilities.
   Determine whether a supported RAM-boot method exists. Its existence is
   currently unproven. Prefer it if verified; otherwise evaluate the existing
   protected boot-partition install/readback/restore mechanism.
2. Build a minimal initramfs around the hardware-booted vendor Image. The first
   milestone is a non-Android `/init` executing and accepting a host command over
   USB, with a fresh boot identity. This isolates the boot chain and userspace
   before changing kernel generations or adding the complete desktop stack.
3. Design original-image restoration before optional bring-up work. Evaluate
   embedding the compressed exact original image and an early bounded restorer;
   measure the complete package against the actual boot-partition capacity.
   Fit, successful restoration, and fallback behavior are not yet established.
   A qualified independent return path is required before this image is tested.
4. Validate the initramfs entry/restorer and failure paths offline, preserve the
   original recovery partition, bind exact artifact hashes and permit one
   attended boot test. Do not reuse consumed kexec trial authorizations.
5. After the minimal environment runs through the normal boot chain, advance
   kernel/driver bring-up along that path. Keep kexec as an optional later
   capability rather than a prerequisite for the operating-system milestone.

This is a boot-strategy change, not a claim that fastboot RAM boot, the new
initramfs, or the proposed embedded restoration already works. Preserve the
successful USB capture and hardware evidence for later diagnosis, but stop
spending repeated tablet jumps on the same unobserved warm-transition interval.
