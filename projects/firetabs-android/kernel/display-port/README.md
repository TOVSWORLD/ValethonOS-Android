# MT8163 Douglas display integration

Latest runtime correction: scope8 captured233 target kmsg records without loss
and returned original Android with Power untouched. LP8557 pre-init fails
ENXIO. Returned working OS ALSO leaves that node unbound: actual backlight is
leds-mt65xx with saved DT mode5, mapped in pinned source to DISP_PWM0. The
mandatory LP8557 panel dependency is wrong. Next correction is builtin PWM
backlight plus its DT path; the current Image has BACKLIGHT_PWM=m. Do not
requalify logging or claim a display pass. working-backlight-path-correction.json
records the active-path proof; earlier LP8557 assumptions below are historical.

Current runtime: full hosted build44253355044 passed. Scope7 booted the
maintained kernel/enforcing PID1 and returned original Android automatically,
but fb0 never appeared; owner saw no banner/bands and left Power untouched.
Its display-only program did not read kmsg, so no target probe-error capture
exists from that attempt. Working-OS animation is the known-good visual reference.

The corrected private display build uses --storage-readonly --display-functional
--display-errors. This selects VDISP002 status then VKMSG001: fresh nonce, byte
length, signed read error, flags and record count followed by raw kmsg bytes.
Flags:1 caught up,2 bounded cut,4 ring loss,8 deadline,16 read/open/close failure.
Limits:256KiB,4096 reads,2s collection,4s transfer. Existing validating nonblocking
kmsg-open/oldest-seek adapter is reused. No ACK, debugfs or block probe.
Truncated/missing tail preserves valid status; it never proves visible pixels.
Host raw data and inspect_display_errors.py output remain private under out/.
Fresh scope8 requires final qualification and new owner availability; scope7
is consumed. Kernel Image, display DT recipe and enforcing policy are unchanged.

Historical source preparation follows; older test/build counts are not current:

Updates #18 and #329. This implements source components for the agreed first
intermediate outcome: display and backlight. It is not another milestone between
storage and display. The next two outcomes remain touch/input and Android graphics/
userspace integration, followed by the major maintained-Android setup/home goal.

`mt8163-display-pipeline.patch` adds the source-backed MT8163 DRM master path,
component identification, gamma descriptor and mutex module map. It applies after
the existing DSI port. All original function bodies are preserved. The path is
OVL0/COLOR0/CCORR/AAL0/GAMMA/DITHER0/RDMA0/UFOE/DSI0/PWM0; the existing MMSYS
routing table already describes this route. Gamma has a512-entry10-bit LUT and
no integrated dither. Mutex data uses the donor's exact MT8163 module bits and
no separate mutex clock. No related-SoC master alias or fabricated route is used.

The existing saved working boot data identifies TPV/MP. Working4.9 board pinctrl
uses GPIO43 for panel power and GPIO83 for reset; GPIO110/65 comments in the
legacy wrapper are stale. VGP3 supplies panel I/O. The TPV-specific driver keeps
four RGB888 lanes, sync-event video, noncontinuous clock and the source porches.
The78000kHz mode preserves the working234MHz DDR PLL's468Mbps through the current
host's pixelclock*bpp/lanes calculation. It is not a claim of measured60Hz or
physical timing acceptance. The legacy `nt35521` wrapper serves several vendors;
its filename is not proof that the TPV glass has the same controller IC.

`generate_douglas_tpv_sequence.py` translates only the reviewed TPV function:
172 commands and two delays totaling140ms. It rejects unknown statements, queue
extents/types, uninitialized words and unbounded delays. A compiled execution of
the original function produces byte-for-byte identical packets/delays. Actual
ported C controls cover every command failure/short write, rail-enable failure,
uncertain rail-disable cleanup, no false active state and idempotent transitions.
The driver uses normal DRM panel/DSI, regulator and GPIO APIs; reset is active-low,
host-first prepare powers the host, then the panel settles its rails and calls
a scoped MT8163 lane-ready API before reset. Unprepare quiesces lanes before
dropping rails; failed lane cleanup retains power/ownership and a fault. The
API rejects foreign, inactive and unowned hosts and takes no new power reference.
Actual C controls cover guards and fault cleanup; electrical timing remains
unqualified until the functional test.

The working backlight driver is REGISTER_BASED LP8557 at I2C0x2c with config0x47,
not the generic donor PWM-backlight node. Use the existing maintained LP855X
backend built-in with a matching `ti,lp8557` node, no `pwms`, `dev-ctrl=0x47` and
initial brightness100. The working board spells `epprom_data` while its driver
reads `eeprom_data`, so that table is not loaded. Do not silently turn these
previously ignored ROM-setting writes into a new initialization sequence.
Actual bus/power ownership and brightness remain hardware qualification.

`build_display_provider.sh` builds the known first-draft source foundation,
preflights/applies the display additions, installs the locked TPV panel and
links a final Image with built-in LP855X/I2C and framebuffer console/logo.
The final gzip/size report is regenerated after these additions; earlier Images
from dependency stages are not the display build. The final manifest hashes
actual objects, Image, config, System.map and vmlinux. This is source compilation:
no DT activation, RAM packaging, firmware write or physical admission occurs.

Local validation: compiled panel, mutex and explicit host/panel lane controls
pass. All999 local regressions pass on the updated source, including the lane
API and DT recipe; the full hosted build remains separate.

`display_dtb_profile.py` previews the full pipeline, panel, I2C0 LP8557 and
required SMI/IOMMU suppliers over the proven RAM/storage DT. It preserves all
RAM/no-map/reserve-map data, uses working I2C0 pins75/76 and panel43/83, removes
unused CMDQ suppliers only with CMDQ explicitly disabled, and replaces the old
RAM-console hook arguments with tty0. Every edit is read back. The preview has
an explicit marker and no executable RAM metadata/authorization; it is not a
physical candidate or a reason to run another tablet test.
Actual hosted kernel compilation is the next check. After it passes, prepare
the complete display/panel/backlight DT dependency closure and a fresh RAM test
package carrying forward the proven memory, PID1, USB and return contract.
Do not replay consumed scope6, repeat a storage/logging-only test, or claim a
working screen from these source checks. Raw boot arguments remain private;
public source pins and the allowlisted variant are in
`evidence/display-pipeline-source/sources.json`.

The first hosted run44250389319 compiled the actual display objects and linked
Image, then failed because the final size-report writer refused to overwrite
the dependency report. A distinct display-image-size-report.json fixes that
packaging error. Its failed receipt is preserved; no artifact/runtime pass is
inferred. The lane API and DT preview additions require the next exact-head
full build. Previewing/validating DT data is not another tablet milestone.
