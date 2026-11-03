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
