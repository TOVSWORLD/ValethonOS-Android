# MT8163 Douglas display integration

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
host-first panel prepare is requested, and local power/reset ordering follows
working resume/suspend. Complete host/rail/LP11/reset ordering still requires
DSI integration review before hardware admission; this source build does not
claim that cross-driver ordering is established.

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

Local validation:995 tests pass, including compiled panel and mutex controls.
Actual hosted kernel compilation is the next check. After it passes, prepare
the complete display/panel/backlight DT dependency closure and a fresh RAM test
package carrying forward the proven memory, PID1, USB and return contract.
Do not replay consumed scope6, repeat a storage/logging-only test, or claim a
working screen from these source checks. Raw boot arguments remain private;
public source pins and the allowlisted variant are in
`evidence/display-pipeline-source/sources.json`.
