# Third-party notices and evidence provenance

This is a provenance index, not a blanket license or a complete distribution-compliance
claim. The project does not distribute a firmware image or vendor application binary.
Each future distributable needs its own complete component and license inventory.

- `evidence/sources.lock.json` pins mt8163-dev, amazon-oss, amonet and CrestronKeeper
  research checkouts. Restore sources separately; preserve their licenses and notices.
- `evidence/kernel*`, `evidence/NetBpfLoad*` and `evidence/los24-armv7.mk` are upstream
  reference source files. Keep their original headers. Android kernel work must follow
  the licenses of the files being modified, including applicable GPL obligations.
- `patches/` contains historical adaptations against upstream Android/device code.
  A patch does not relicense the underlying source. Record origin and author when
  importing or modifying a patch.
- `evidence/crestron/` records publicly retrieved package metadata, static manifest
  inspection and download hashes. APKs, native libraries and firmware are excluded.
  Crestron names and marks belong to their owners; no endorsement is claimed.
- Other `evidence/` files include upstream release pages, API responses, source extracts
  and research outputs. Consult the cited origin and retained headers for terms.
- Amazon, Fire, Android, LineageOS, Google and Crestron marks identify compatibility
  targets and upstream projects; this independent project is not their official port.

Report a missing attribution or provenance concern privately through SECURITY.md if it
contains sensitive material, otherwise open a documentation issue with the exact path.
Do not introduce an unsupported SPDX label on third-party or vendor-derived content.

`evidence/kernel-audit/` preserves pinned upstream ACK, MediaTek community, legacy,
LibreEcho and AOSP source/listing references with original headers and a SHA256 index.
These sources retain their file-level terms; source excerpts are not relicensed as
first-party documentation. Research integration proposals do not establish runtime or
redistribution approval for any separately obtained vendor firmware.

`evidence/independent-recovery/watchdog-source/` retains pinned ACK watchdog
source/Kconfig (GPL-2.0+ driver header preserved) and the existing MT8163 legacy
register header. sources.json records exact upstream revisions and hashes; the
base-watchdog match adaptation does not relicense those sources.

The private early-entry display checkpoint patch targets Android Common Kernel
`arch/arm64/kernel/head.S` at d9318bdb4c34e8b2d997b4f67ced56b120b22b87.
The retained source fixture preserves its upstream SPDX license notice; see
https://android.googlesource.com/kernel/common/+/d9318bdb4c34e8b2d997b4f67ced56b120b22b87/arch/arm64/kernel/head.S.
Framebuffer metadata interpretation was checked against the retained MT8163 source
at e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74; this is provenance, not device acceptance.

The private retained-log worker uses the pinned Android Common Kernel block/BIO,
printk snapshot and SHA256 APIs under its GPL-2.0-only kernel source notice. The
exact upstream drivers/misc/Makefile fixture retains its upstream notice; provenance
is in projects/firetabs-android/kernel/lab-retained/inputs.json. The dual-slot record
codec and host reader are project implementations, not the legacy MTK RAM format.

The private earliest-entry probe patches the same pinned ACK head.S listed above;
its boot-contract reference is that revision's Documentation/arch/arm64/booting.rst.
No upstream boot/reset/security behavior is claimed qualified by emulator controls.

The prepare-only kexec staging recipe derives four generic kernel files from
fabianishere/kexec-mod at4ba956fd60b29d2fea324515596b392afdcfa2c5, retaining its
GPLv2 headers and the original Linux/Eric Biederman notices. The generated source
and adaptation patch stay in ignored build output; source-manifest.json records
all inputs/changes. The exact working4.9 kernel source donor is amazon-oss at
72940eb733af8df948cc216cb977cd8be9cba5a9. Kernel-facing wrapper files retain their
file-level notices; none changes the repository-wide license policy.

The bounded secondary-off candidate follows the CPU1–3 MTCMOS ordering/definitions
in amazon-oss72940eb733af8df948cc216cb977cd8be9cba5a9,
`drivers/misc/mediatek/base/power/mt8163/mtcmos.[ch]` and `mt_psci.c`.
Generated vendor files/patches preserve original MediaTek GPL notices in ignored
build output. Kernel-facing candidate files carry GPL-2.0 notices; exact source
hashes are recorded in kexec-cpu-shutdown-audit.json and kexec-cpu-off-build-result.json.

The legacy affinity patch generator targets `drivers/firmware/psci.c` from the
same amazon-oss72940eb733af source. Generated patched source preserves the original
ARM GPL notices in ignored output. The query module/policy are GPL-2.0 kernel-facing
sources; no source-kernel binding is installed by the query test.

The isolated full source-kernel recipe also applies pinned compiler-compatibility
corrections to seven existing amazon-oss files (audio, CPU frequency, boot getters,
sensor batching, USB and display declarations) at the same72940eb733af revision.
Generated files and the private combined patch preserve their original MediaTek
GPL notices. The recipe does not change repository-wide licensing.
