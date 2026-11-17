# MT8163 integration after the generic compiler baseline

> Historical source/integration snapshot. Use the [current hardware contract](../../../docs/development/DOUGLAS-HARDWARE-CONTRACT.md)
> for consolidated implementation status and later boot evidence. Statements below
> about routes/builds not yet established describe their original audit date.

This queue targets the pinned ACK in `support-matrix.json`. A successful generic
ARM64 defconfig build only verifies a compiler/source combination. It does not
advance the douglas `kernel_compile` gate in `../validation.json`.

1. **Clock and reset providers:** compare the donor's MT8163 clock drivers and
   binding IDs against ACK clock APIs and parent names. Bring bindings, Kconfig,
   Makefile and driver data together. Compile with warnings enabled, then check
   every DTS clock reference resolves to the intended provider/ID. Do not insert
   fixed-rate clocks to hide missing providers. See the clocks component in the
   support matrix for source anchors.
2. **Pinctrl and interrupts:** port donor MT8163 pin descriptors and EINT data;
   compile against ACK's MediaTek common pinctrl implementation. Check bank sizes,
   register offsets, interrupt mappings and GPIO consumers against the legacy
   board. Do not substitute another chip's pin table because it compiles.
3. **PMIC host and power domains:** ACK's MT6323 regulator support alone does not
   provide the MT8163 pwrap host. Reconcile donor pwrap/power-domain changes with
   ACK APIs, clock dependencies and required bus protection. Compile providers
   before enabling dependent MMC/display nodes.
4. **Board and CPU boot contract:** resolve stock mt-boot/MTCMOS versus donor PSCI
   with source review and later owner-supplied boot logs. Preserve this as an
   explicit prerequisite for multicore/suspend qualification. Do not silently
   change firmware expectations. Establish actual RAM/reserved-region handoff;
   the inherited DT's 512 MiB declaration is not the tablet's 1.5 GiB map.
5. **Storage and minimal console:** verify UART/MMC wiring, supplies, clocks and
   pinctrl. Only after the boot contract and recovery procedure are established
   should an owner-authorized diagnostic boot be proposed. No such test is
   authorized by this repository's current development work.
6. **Display/input and ordinary tablet operation:** port panel initialization,
   backlight and touch wiring, then DRM/IOMMU/SMI and GPU userspace integration.
   Follow with Wi-Fi, audio, suspend, charging/thermal and media. Compile and
   schema results are prerequisites, never substitutes for device measurements.

For each provider change, retain upstream/donor commit provenance and licenses,
record differences from ACK, build the affected objects and a complete Image,
and validate the matching DT against the complete binding corpus. An unresolved
binding must be recorded rather than converted into a suppressed warning.

The Android configuration stage follows the generic compiler diagnostic: resolve
GKI/Android requirements, 4 KiB pages and chosen userspace ABI, Binder, BPF,
SELinux and module/toolchain requirements. The stock boot partition size and
Image.gz-dtb envelope require a separate fit/loader investigation. No installable
image or release is produced by the generic experiment.
