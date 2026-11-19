# Douglas hardware and kernel implementation contract

## Touch candidate built; exact-kernel VM checks passed — November 18, 2026

The maintained Goodix kernel build succeeded in GitHub run 44438104081.
Source 1525308e981f48a6abd4a8122093f478053382a0 and workflow merge commit
ccb8f413cb657d31e2110d0296736982ee25d03f have the same tree. The downloaded
artifact digest and all 14 manifest files verified. Goodix is the only kernel
configuration change from the observed display baseline: module to builtin.
The source-backed DT uses GPIO35/EINT46, reset46, I2C0 pads75/76 and VGP2 at
3.0V with VIO18 at1.8V. RAM reservations and the corrected loader framebuffer
node survive. Enable the existing watchdog driver for inherited heartbeat;
this does not establish the prior reset cause or stable hardware operation.

The enforcing touch component compiled in the approved isolated lab directory.
All 1,041 repository tests pass in the final source regression run.
All16 forbidden-privilege compiler controls passed. On the exact new kernel,
both virtualization modes pass real virtual-evdev read-only open/idle-read,
denied ioctl, denied relabel and denied write-open checks. The first VM fixture
incorrectly assumed no virtual input device; its failed result is retained.
These results are VM policy checks, not physical Goodix qualification.

A fresh direct touch package is prepared offline. Static original-loader audit
and disposable authorization-fixture checks pass; missing approval and the
historical display scope are rejected. No real owner authorization file was
created and no tablet command was run. Original Android remains restored.
The visible acceptance is all nine large blue panels turning green as the owner
touches them. USB display status is sent before the touch window, its send result
does not gate the grid, and it cannot prove touch. No raw events are stored.
Next: publish the exact preparation, obtain fresh attendance/staging/test
approval, run one direct test, then restore and verify original Android.
No new logging proof gate. Receipts: evidence/touch-input-source/
kernel-build-result.json and touch-preparation-result.json.

## Touch/input source integration started — November18,2026

Work moved to codex/issue-330-touch-input, stacked on observed display foundation.
Read-only restored-OS metadata confirms Goodix-TS at I2C0x5d/goodix,gt9xx and
input goodix-ts; capability axes800/1280, direct multitouch. Cached186-byte
configuration exactly matches pinned public hvt groups0-3. Sensor/chip ID is not
claimed from the all-zero live-read section; it is unusable evidence.
Pinned working driver/DTS and maintained Goodix source retained. GPIO35 maps to
EINT46 (not IRQ35); resetGPIO46, falling edge from profile. Working driver sets
VGP2 analog3.0V; IO1.8V. Preserve source profile, not guessed coordinates/config.
Minimal maintained driver change adds legacy goodix,gt9xx compatible alias; its
runtime chip-ID selection remains. Dedicated touch-provider build keeps observed
display setup and makes GOODIX builtin, retaining Goodix/watchdog object evidence.
Public configuration generator reproduces the known cached186-byte profile and
rejects changes. All1035 tests pass; no new Image build or touch hardware pass yet.
Next run exact touch kernel build while preparing DT/supplies/EINT, enforcing
read-only evdev access and large visual3x3 feedback. Handle inherited watchdog
alongside this test; no new logging proof gate or physical test authorized.
Original Android remains restored; raw working-OS metadata private in out/touch-input-1.
Source contract: projects/firetabs-android/kernel/touch-port/contract.json.

## Visible display/backlight achieved; touch/input next — November18,2026

Corrected direct scope2 ran once after explicit staging/test approval. Owner
confirmed VALETHON DISPLAY TEST and labelled red/green/blue bands physically
visible. Maintained kernel/PID1 reached the actual display test. Carry this
foundation forward; do not demand another screen or logging proof before touch.
Some small error text was reported but unreadable; do not invent its contents.
Target USB endpoint appeared five times about65.6–65.8s apart. Captured120 bytes
fail the display-status header; no valid USB status or kernel snapshot. Physical
visual evidence is affirmative; the packet is NOT a valid nonce-bound proof.
Repeated boot resets, their cause, stable operation, brightness endpoints and
suspend/resume remain unqualified; full#329 acceptance is not closed.
One candidate p5 write/readback and one direct boot request; full300s observation.
Afterward original helper ran once, original TWRP returned, original p5 restored
once/full readback, p6 unchanged. Original Android boot/config/recovery, fresh
completed boot and normal ADB verified. Current installation is original Android.
No recovery/bootstrap/bootloader write, test replay or active capture/helper.
Receipt direct-fbfix-runtime-result.json; private checkpoint out/display-direct-fbfix-2.
Next agreed implementation is#330 Goodix touch/input: working source declares
I2C0x5d, reset46, IRQ35. Check active controller/config/orientation before porting;
current maintained GOODIX is modular, INPUT_EVDEV/I2C_MT65XX builtin. Prepare
visual touch feedback on the achieved display, then one fresh qualified test.
Alongside that, inspect inherited watchdog handling for repeated resets. Current
Image has MEDIATEK_WATCHDOG builtin and boot-enabled handoff support, but the RAM
bootstrap-derived DT disables watchdog@10007000. Historical watchdog candidate3
predated observed kernel entry; reuse its source/VM findings, not its old test.
Watchdog reset cause is not established and no watchdog-only/logging trial is
selected. Keep invalid USB packet tracked separately; do not reopen logging gate.

## Concrete direct-loader framebuffer-node collision fixed — November18,2026

The direct input DT already contains fb-reserved-memory@98600000, imported from
the live OS reservation map. Exact original LK callback25c54 unconditionally
adds fb-reserved-memory. Its libfdt name lookup also matches unit-address suffixes;
add returns-2/EXISTS, callback returns1, caller3dfe4 branches to failure return,
and wrapper3ec20 loops before kernel handoff. This is a deterministic violated
contract on that selected path, not proof it was the sole physical reset cause.
Exact pinned LK callback AND libfdt instruction emulation reproduce failure on
the tested DT. Renaming the preserved node to fw-reserved-memory@98600000 passes
(return0); reg/no-map/compatible survive the callback unchanged. Removal is only
a negative/control fixture, never the candidate fix. Runtime globals are modeled,
not measured firmware state; receipt direct-loader-fb-collision-audit.json.
Implemented a one-byte input node-name change in direct packaging. No reservation,
RAM exclusion, phandle, panel setting, kernel, policy or capture is removed/changed.
Builder verifies every other board property. Fresh unchanged enforcing PID1 built;
1031 regression tests pass and all three exact-code callback controls pass.
Fresh corrected package and exact-LK static loader audit passed; offline device
guard accepts exact inputs under a disposable test authorization fixture, rejects
unapproved templates and consumed scope1. Scope display-direct-fbfix-2 is ready
locally for fresh owner attendance/approval, not staged to the lab. No new tablet
action or test approval. Original Android remains verified restored.
Receipt direct-fbfix-preparation.json; private checkpoint out/display-direct-fbfix-2.
Consumed first direct test and unknown owner visual result stay historical.

Current consolidation: November 17, 2026. Target: Amazon Fire HD 8 (2017),
douglas/KFDOWI, MT8163; maintained-kernel candidate is the pinned ACK 6.18.34
Image. This is the central hardware reference for implementation and test
selection. It brings the existing source audits together. Maintained-kernel/PID1/USB and
read-only eMMC are now observed on this tablet; display remains unqualified.
The current OS loading animation is a working display/backlight/graphics
reference. Use its pinned board/driver setup when comparing the maintained path.

## Pin configuration compatibility — November18,2026

Scope10 reached DRM component matching/IOMMU attachment, then failed group43
pin configuration. The working4.9 driver uses PIN_CONFIG_SLEW_RATE as a GPIO
output-direction alias via mtk_pconf_set_direction; it does not program a
pad-slew register. output-low/high already select output direction. Maintained
ACK maps those properties to PIN_CONFIG_LEVEL, which is supported, but rejects
SLEW_RATE. Actual working dispatcher/helper and ACK dispatcher C tests prove
removing the redundant alias preserves final output level/direction on43/83.
Keep the known-working behavior; do not invent a new slew setting or port a
register write the working handler never made. Same Image/PWM/MM0/policy/capture.

## Active multimedia-domain ancestry correction — November18,2026

Scope9's actual DT still disabled /soc/syscon@10006000, inherited from the
bootstrap DISABLED list. Its power-controller child supplies domain0/MM to
display. Corrected recipe enables the parent/controller and MM0 only, disables
the other seven domains, validates MM_SEL51 and checks selected-resource
ancestors. Pinned provider probes only available domain children. Kernel Image,
policy and capture are unchanged; scope10 tests/seven controls/final offline
validation pass. Corrected physical display remains pending.

## Active backlight correction — November18,2026

Runtime/saved-DT/source comparison disproves the earlier assumption that the
LP8557 node must drive this board. Returned working Android leaves0-002c unbound
and uses lcd-backlight/leds-mt65xx; actual working DT led_mode5 maps to
CUST_BLS_PWM/disp_bls_set_backlight/DISP_PWM0. The declared LP8557 DT node is not
evidence of an active driver. Candidate's mandatory LP8557 backlight phandle
therefore blocks panel registration unnecessarily. Correct to the working PWM
path, retaining panel power ownership and source-backed timing. Maintained
The previous Image had BACKLIGHT_PWM modular; new source616de189/run44273014513
builds it builtin. Corrected DT connects PWM0, pin59 function1, period39385ns
(1024 clocks at the declared26MHz main clock, divider0). Panel owns GPIO43.
Compiled-image VM and offline DT checks pass; physical display is still pending.
[Source and read-only binding proof](../../evidence/display-pipeline-source/working-backlight-path-correction.json).

## How to use this reference

Start with the relevant subsystem below, then inspect its exact working-source
implementation, current target resources and linked port notes. Before changing
code or asking for a test, identify which contract is wrong or unimplemented.
Preserve working board values unless a cited source establishes a required change.
Distinguish hardware present, source support, compiled support and physical
acceptance. A peripheral disabled for a bootstrap is not absent hardware.

The [resource inventory](../../evidence/independent-recovery/douglas-hardware-resources.json)
records 430 resource-bearing nodes from the archived working-source DT and 152
from the consumed ACK trial DT. It includes allowlisted MMIO/bus addresses,
interrupts, clock/reset/DMA/PHY references, pinctrl, supplies, regulator limits,
CPU firmware calls and reservations. Values are exact big-endian hex bytes;
interpret them with parent/provider cell counts and matching bindings. Direct
supply/interrupt-parent/pinctrl phandles are resolved to node paths. Multi-cell
clock/DMA/IRQ references remain encoded rather than guessed.

This inventory excludes boot arguments, nonce/seed and identity channels; it is
not a raw device dump. It is also not every vendor tuning property. The full
pinned DTS, driver tables, binding definitions and subsystem notes remain the
source for vendor command sequences and opaque configuration payloads.

## Source hierarchy and current evidence

- Legacy source donor: [3.18 tree, e0a3a2b](https://github.com/mt8163-dev/android_kernel_amazon_mt8163/tree/e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74).
- Exact working-kernel source revision: [4.9 tree, 72940eb](https://github.com/amazon-oss/android_kernel_amazon_mt8163/tree/72940eb733af8df948cc216cb977cd8be9cba5a9).
- Working board description: [4.9 Douglas DTS](https://github.com/amazon-oss/android_kernel_amazon_mt8163/blob/72940eb733af8df948cc216cb977cd8be9cba5a9/arch/arm64/boot/dts/mediatek/douglas.dts)
  and [SoC DTSI](https://github.com/amazon-oss/android_kernel_amazon_mt8163/blob/72940eb733af8df948cc216cb977cd8be9cba5a9/arch/arm64/boot/dts/mediatek/mt8163.dtsi).
- Maintained implementation: [ACK d9318bd](https://android.googlesource.com/kernel/common/+/d9318bdb4c34e8b2d997b4f67ced56b120b22b87/).
- Existing component/source anchors: [historical support matrix](../../projects/firetabs-android/kernel/support-matrix.json).
  Its October 25 statements such as “uncompiled” are historical, not current build status.
- Compiled complete draft identity and object hashes:
  [first-kernel-draft receipt](../../evidence/independent-recovery/first-kernel-draft-result.json).
- Latest tablet outcome: [fresh PID1 USB identity](../../evidence/independent-recovery/ack-usb-end-to-end-runtime-result.json).
  Exact fresh40-byte header received after the controlled PID1 policy gates.
  Kernel/PID1/USB-identity milestone reached; following record stream incomplete.
  Earlier [RAM-corrected kernel/PID1 result](../../evidence/independent-recovery/ack-ramfix-runtime-result.json):
  Kernel initialization and /init execution, SELinux policy load and USB
  enumeration/CDC ACM observed. Fresh USB protocol witness remains open.
  Earlier [C-init panic](../../evidence/independent-recovery/ack-cinit-runtime-result.json):
  Retained output identifies a panic and an omitted live RAM exclusion; fix
  success remains unproven. Prior [combined result](../../evidence/independent-recovery/ack-combined-runtime-result.json):
  Full padded Image integrity, actual entry/MMU/virtual transition and start_kernel
  passed on Douglas. Complete kernel initialization and enforcing PID1/USB remain
  unproven. Earlier [unattributed ACK trial](../../evidence/independent-recovery/ack-native-runtime-result.json)
  is preserved as history, not current execution status.
- [Full-image offline audit](../../evidence/independent-recovery/ack-full-image-offline-audit.json)
  checks relocation and the exact pre-MMU instruction path. It is not hardware acceptance.

An archived live DT is authoritative for what was handed to that boot, not proof
that every declared optional component exists or was probed. Source declarations
are implementation evidence, not a substitute for the physical board's identity.
Use [project memory](PROJECT-MEMORY.md) for consumed trials and owner constraints.

## 1. CPU, exception levels, MMU and firmware

Hardware family: four Cortex-A53 cores, ARM64 kernel with 32-bit Android baseline.
The legacy CPU power path uses vendor mt-boot/MTCMOS operations; the maintained
kernel expects supported firmware CPU operations. The live source PSCI contract
is `arm,psci`, SMC with explicit cpu_suspend/off/on/affinity IDs 0x84000001–04.
The native target was changed to match that binding, rather than assume PSCI0.2.
This establishes a DT contract, not a claim that the firmware implements only0.1.

The source native handoff physically verifies secondary off state before device
shutdown and retains a final gate. The maintained target bootstrap limits CPUs
to one; target SMP and suspend/resume are unqualified. The full target Image has
text_offset zero and therefore uses a 2MiB-aligned base at0x40000000, x0=FDT and
x1–x3=0. Full Image extent is28,049,408 bytes. Preserve architecture entry/cache/
exception-level requirements rather than copying old vendor entry assumptions.

Required implementation: valid entry ABI, correct CPU firmware methods and power
sequence, exact page-table capabilities and later SMP/hotplug. Offline A53 entry
selected48-bit VA/40-bit PA despite a52-bit-capable config; that capability alone
is not a diagnosed boot fault. See [boot contract](DOUGLAS-BOOT-CONTRACT.md),
[ACK RAM contract](ACK-LINUX-RAM-BOOT.md) and the receipts above.

## 2. DRAM, reservations and bootloader fixups

The tablet class has1.5GB RAM; a donor512MiB memory declaration is not the working
map. Use the archived working DT memory banks and FDT reserve map for the actual
trial, and preserve firmware/secure/display/log reservations. Fixed source
reservations include ATF0x43000000/0x30000, RAM-console region0x44400000/0x200000,
log region reg0x44600000/0x20000 and mdump0x4bd00000/0x300000. The log node's unit
address says46600000 while reg says44600000: reg is the resource declaration;
do not silently “correct” it from the name. Dynamic CONSYS placement, framebuffer
allocation and bootloader-reserved regions need their own source/runtime context.

Required implementation: correct usable banks, no overlap among Image/DT/initrd/
firmware regions, preserved no-map semantics, correctly scoped reserved consumers.
The current native builder imports live firmware reservations. That does not
qualify generic donor reservations for every loader route.
See [reservation inventory](../../evidence/reservation-inventory/result.json),
[LK memory fixups](../../projects/firetabs-android/kernel/LK-MEMORY-FIXUPS.md)
and the generated resource inventory.

### Live RAM exclusions discovered November17

The C-init [hardware receipt](../../evidence/independent-recovery/ack-cinit-runtime-result.json)
records source System RAM excluding98400000–98600000. Earlier target DT imports
did not cover this gap with no-map. A fault VA in show_pte corresponds to a
physical page in the gap under the A53 runtime linear map; causality remains
unproven. [Correction](ACK-LIVE-RAM-FIX.md): derive allocator exclusions from fresh
working /proc/iomem in addition to DT, bind its hash, and verify every gap is
unallocatable. Do not infer this gap's owner or free old reservations from a
static resource inventory. This is a software-observed working-kernel contract.

## 3. Interrupts, timer and watchdog/reset

Preserve GIC topology, interrupt-parent chains, SPI numbers, polarity/sysirq
selection and architecture timer firmware requirements. A numeric vendor IRQ
cannot be inserted into a different parent binding unchanged. Source UART0,
for example, declares separate UART and DMA interrupts; those do not become a
single modern UART binding by deleting fields.

Watchdog register block is0x10007000. The entry stub programs a31-second reset-only
deadline after shutdown. Owner confirmed automatic return in the consumed ACK
attempt, but the exact reset cause/expiration behavior is not established. The
target watchdog driver was disabled for that experiment, not absent from the SoC.
Required implementation: correct IRQ parent/type, timer access, watchdog match and
reset ownership, with explicit firmware interaction. See [sysirq](DOUGLAS-SYSIRQ-DT.md),
[watchdog](WATCHDOG-BINDING.md), [larb IRQ contract](../../evidence/larb-irq-contract/)
and [watchdog port](../../projects/firetabs-android/kernel/lab-watchdog/).

## 4. Clocks and resets

The SoC needs oscillator inputs plus topckgen, infracfg, apmixedsys and peripheral
clock providers, including audio/display/GPU/video gates. Exact provider IDs,
parents, rate selection, reset relationships and sequencing are part of the
contract. Do not replace missing providers with fixed clocks merely to compile.
The donor clock port has been compiled in later builds; the October source matrix
is not the current compile result. Required implementation: dependency closure,
correct mux/gate API adaptation and per-consumer clock ownership through shutdown.
See [clock port](../../projects/firetabs-android/kernel/clock-port/),
[TOPCKGEN](TOPCKGEN-BINDING.md), [INFRACFG](INFRACFG-BINDING.md),
[APMIXEDSYS](APMIXEDSYS-BINDING.md) and the resource inventory for consumer references.

## 5. GPIO, pinctrl and external interrupt wiring

Preserve MT8163 pin descriptors, function numbers, pull/input/Schmitt/drive settings,
EINT mapping and state transitions. A SoC GPIO index is not a PCB test-pad number.
Required implementation: matching pinctrl driver plus board-specific default,
sleep and transition states; supplying only pin names is insufficient.
See [pinctrl port](../../projects/firetabs-android/kernel/pinctrl-port/),
[pinctrl binding](../../projects/firetabs-android/kernel/dtb/PINCTRL-BINDING.md)
and the working DTS pinctrl groups. Physical pad/net correspondence is a separate
claim to trace through board documentation, not assumed to require measurement.

## 6. PMIC, regulators, voltage domains and power sequencing

Legacy board declarations include MT6323 over the PMIC wrapper and an external
SYM827 core regulator at I2C address0x60. Preserve rail names, voltage constraints,
always-on/boot-on requirements, supply consumers, interrupt delivery and startup/
suspend ordering. ACK MT6323 regulator support alone does not implement the MT8163
wrapper host or all power domains. The SYM827 adaptation uses the FAN53555 family
implementation; compatible/register behavior must follow the port evidence.

Required implementation: pwrap host, PMIC child bindings, regulators, clocks,
SCPSYS/MTCMOS domains and bus protection. A VIO18 rail used by camera or eMMC is
not by itself evidence that the UART bank uses that rail.
See [PMIC DT](DOUGLAS-PMIC-DT.md), [pwrap](../../projects/firetabs-android/kernel/dtb/PWRAP-BINDING.md),
[SCPSYS](../../projects/firetabs-android/kernel/dtb/SCPSYS-BINDING.md),
[power port](../../projects/firetabs-android/kernel/power-port/),
[SYM827](../../projects/firetabs-android/kernel/dtb/SYM827-BINDING.md).

## 7. UART and early console

Working DT: UART0 at0x11002000,26MHz input, RX GPIO79/function1 and TX
GPIO80/function1. Vendor driver has separate pin-set/clear states and power-state
remux. The exact working config enables MTK_SERIAL and MTK_SERIAL_CONSOLE;
console/baud/probe functions are linked, and live DT contains the matching
`mediatek,mtk-uart` fallback. Console setup defaults to115200; supplied options
request921600. These are software facts, not guessed baud/route requirements.

The maintained driver uses mt6577 fallback, MEM32/regshift2 and different clock/
DMA/binding expectations. Its earlycon callback inherits baud initialization.
The consumed ACK DT disabled UART0 and had no UART console arguments. A UART DT
preview corrects those three properties without rebuilding the Image. The source
boot also suppresses UART printk; silence alone cannot diagnose hardware.

Required implementation: exact early/normal console initialization, clock/pin
continuity and suppression policy. Physical PCB TX contact and bank supply remain
unresolved in the project; documentation has not been exhausted. Existing board
image is a recovery reference, not yet a UART map. USB-PHY UART switching is
present in source but disabled in tested config. MSDC2 alternate UART pins are
not the removable MSDC1 card slot.
See [source trace](../../evidence/independent-recovery/legacy-uart-source-trace.json),
[UART binding](DOUGLAS-UART-BINDING.md), [prepared tools](UART-FIRST-CAPTURE.md).

## 8. I2C, SPI and board identification

Bus/controller clocks, pinmux, parent interrupts and child addresses are kernel
contracts. Legacy Douglas declares backlight at0x2c, camera children at0x3c/0x21,
Goodix at0x5d, SYM827 at0x60, charger at0x6b, sensor candidates at0x18/0x44/
0x6a/0x6c and thermal sensors0x70–72. These addresses are on their declared I2C
buses, not one shared address space. Optional/variant declarations must not all
be labeled physically fitted or probed. Use node status and driver/board evidence.
Required implementation: bus timing, DMA/PIO support, supplies/reset and variant
selection. The pinned board DTS and generated inventory preserve the hierarchy.

## 9. eMMC, removable SD and partition/recovery contract

Legacy eMMC uses an8-bit non-removable interface and requests1.8V HS200; removable
SD is4-bit and uses the MSDC1 pin group. The donor uses the mt2701 MMC fallback;
compatibility does not establish electrical timing. Preserve supplies, pinctrl,
drive strength, reset and host quirks. Conservative initial timing does not license
arbitrary changes to voltage or board wiring.

The experimental Linux target disabled all three MMC controllers and removed the
disk-log opt-in; this is a RAM-only bootstrap policy. Actual boot/recovery partition
identity and aliases are separately verified before any authorized write. Never
write a name-only alias or treat an eMMC address as a RAM physical address.
Required implementation: first read-only host/card identification, then explicit
integrity/return testing when selected. See [console/storage](DOUGLAS-CONSOLE-STORAGE.md),
[MMC source](../../evidence/offline-emmc-geometry/) and the ACK RAM receipt.

The November18 storage candidate preserves the actual maintained DT's26MHz
maximum and enables only MMC0 at11230000, not the historical200MHz/HS200 request.
It checks source/hclk/bus clock IDs31/58/28, assigned parent21, SDR/UHS pin groups,
8-bit non-removable wiring and existing VEMC3V3/VIO18 providers. IRQ0/79/8 is
behind MediaTek sysirq10200620; changing it to direct-GIC polarity is incorrect.
The working kernel uses CONFIG_MMC_MTK and generic mtk-sd.o; ComboA/PRO is not its
active host. Its mt8163 and mt2701 compatibility entries have identical divisor,
pad tune, FIFO/data tune and64-bit DMA quirks, corroborating the maintained
mt2701 fallback. Pinned working source:
[mtk-sd.c](https://github.com/amazon-oss/android_kernel_amazon_mt8163/blob/72940eb733af8df948cc216cb977cd8be9cba5a9/drivers/mmc/host/mtk-sd.c),
[host Makefile](https://github.com/amazon-oss/android_kernel_amazon_mt8163/blob/72940eb733af8df948cc216cb977cd8be9cba5a9/drivers/mmc/host/Makefile).
[Candidate checks](../../evidence/independent-recovery/ack-storage-readonly-preparation.json)
are offline preparation. The [actual storage test](../../evidence/independent-recovery/ack-storage-readonly-runtime-result.json)
subsequently read/verified original p5 exactly16MiB under the maintained kernel,
sent fresh functional USB success and returned to verified original Android.
This establishes known-p5 read-only integrity, not general/writable filesystems.

## 10. USB controller, PHY, DMA and gadget

USB0 at0x11200000 needs the MT8163 MUSB glue, USB2 PHY, analog resources, clocks,
power/supplies, interrupt routing and role selection. Preserve PHY/controller
binding resources and distinguish host, peripheral and OTG behavior. Target
bootstrap selects peripheral; source USB-console capture is physically proven,
and fresh target PID1 USB identity plus functional storage status are now
observed. This does not qualify all USB roles, PHY timings or peripherals.

Required implementation: provider dependency closure, proper PHY register ranges,
DMA ownership/quiescence, gadget/configfs and correct host capture. No new UART
mode may silently replace the working USB control path.
See [USB prerequisites](../../projects/firetabs-android/kernel/USB-PREREQUISITES.md),
[USB resources](../../projects/firetabs-android/kernel/dtb/USB-RESOURCE-BINDINGS.md),
[analog PHY](../../projects/firetabs-android/kernel/dtb/USB-ANALOG-BINDING.md),
[gadget prerequisites](../../projects/firetabs-android/kernel/USB-GADGET-PREREQUISITES.md).

## 11. IOMMU, SMI, DMA and power-domain dependencies

MT8163 multimedia paths depend on the matching IOMMU, SMI common/larb nodes,
port identifiers, clocks, power domains and bus protection. Driver data from a
related MediaTek SoC cannot be assumed to share ports or IRQ semantics.
Required implementation: matching provider/consumer IDs, DMA address limits,
reserved buffers and shutdown ordering. These remain relevant to kexec even when
an eventual target peripheral is disabled: the source must quiesce its DMA.
See [IOMMU/SMI](../../projects/firetabs-android/kernel/dtb/IOMMU-SMI-BINDINGS.md),
[IOMMU port](../../projects/firetabs-android/kernel/iommu-port/) and larb IRQ evidence.

## 12. Display panel, DSI and backlight

Legacy panel driver is NT35521 Douglas,800×1280, four DSI lanes, RGB888. It contains
vendor-ID-dependent timing and command tables. Its GPIO110/65 comments are
stale: pinned working4.9 board pinctrl and saved live DT use GPIO43 for panel
power and GPIO83 for reset. This tablet's already captured panel variant is
TPV/MP; preserve that specific sequence and VGP3 I/O supply. Do not flatten its variants into one timing or assume a
framebuffer address implements the panel. The working board declares LP8557
backlight at I2C0x2c; its active driver uses REGISTER_BASED brightness with config
0x47. A PWM driver compile is not proof of that backlight path. The working DTS
epprom_data spelling does not match its driver's eeprom_data lookup, so the ROM
table is not loaded. Do not silently activate these settings during the port.
[Exact public source pins](../../evidence/display-pipeline-source/sources.json).

Required implementation: panel identification, regulator/reset/delay/DSI commands,
MIPI PHY, DSI host, MMSYS route, DRM graph, backlight and scanout. Preserve source
initialization arrays by reference with their license/provenance, rather than
invent a generic panel definition. Target bootstrap disabled the display path;
its absence on screen cannot locate early kernel failure.
See [panel source](https://github.com/mt8163-dev/android_kernel_amazon_mt8163/blob/e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74/drivers/misc/mediatek/lcm/nt35521_wxga_dsi_vdo_douglas/nt35521_wxga_dsi_vdo_douglas.c),
[DSI](../../projects/firetabs-android/kernel/DSI-SOURCE-PREREQUISITES.md),
[MIPI](../../projects/firetabs-android/kernel/MIPI-SOURCE-PREREQUISITES.md),
[MMSYS](../../projects/firetabs-android/kernel/dtb/MMSYS-BINDING.md),
[display PWM](../../projects/firetabs-android/kernel/DISP-PWM-SOURCE-PREREQUISITES.md).

## 13. Touch, keys and cover detection

Legacy declares Goodix gt9xx at I2C0x5d, reset GPIO46 and IRQ GPIO35 with multiple
configuration groups. Modern Goodix family support is not automatically the
correct variant/configuration. Board also declares a ROHM hall BU520 and PMIC/
GPIO keys. Required implementation: matched controller variant, IRQ/reset/power,
configuration blob semantics, input orientation and suspend/wake behavior.
See pinned Douglas DTS, [pinctrl binding](../../projects/firetabs-android/kernel/dtb/PINCTRL-BINDING.md)
and the historical support matrix's touch anchors.

## 14. GPU and Android graphics

Hardware family is Mali-T720. ACK Panfrost recognition is source support, not a
working Android EGL/gralloc/composer stack. Required implementation: correct GPU
clocks, regulators, reset/power domains, IOMMU/SMI dependencies, DRM buffers and
userspace integration. Target bootstrap disabled GPU probes. Hardware rendering,
compositor, display synchronization and application compatibility remain separate
acceptance results. See historical GPU source anchors and MMSYS/IOMMU contracts.

## 15. Wi-Fi and Bluetooth

Legacy uses the MT8163 CONSYS vendor combo stack with dedicated Wi-Fi/BT supplies
and a dynamic reserved-memory consumer. Do not infer a supported radio from an
mt76 source directory or silently equate a vendor chip label with a modern driver.
Required implementation: exact radio/bus/firmware/NVRAM interface, power/reset/
clock sequence, regulatory/calibration data and Bluetooth transport. Firmware and
calibration licensing/identity handling must remain separate from public source.
Exact reusable modern transport/firmware integration is unresolved; this is not
missing physical hardware. Use pinned DTS supplies/reservations and legacy config
anchors in the support matrix.

## 16. Audio, microphone and jack

The board requires MediaTek AFE routing, clocks/DMA/interrupts, PMIC codec and
board amplifier/jack/microphone paths. The pinned board source and PMIC child
bindings are the starting contract, not proof that a generic MT6323 codec binds
correctly. Required implementation: ASoC graph/machine routing, pinctrl, supplies,
DAI formats/rates and controls. Target bootstrap disables AFE. Playback, recording,
jack events and power behavior remain unqualified on the maintained kernel.
See [AUDSYS](../../projects/firetabs-android/kernel/dtb/AUDSYS-BINDING.md),
PMIC DTS and generated resource dependencies.

## 17. Charging, battery, thermal and DVFS

Legacy declares BQ24297 charger at I2C0x6b, MT6323 power/fuel-gauge paths, external
CPU regulator, CPU/GPU operating points, thermal sensors and cooling policy.
Board source includes TMP103 nodes0x70–72 and virtual thermistor nodes; a source
node is not evidence every sensor is fitted on this unit. Required implementation:
correct battery/charger limits, thermistor interpretation, thermal calibration,
OPP voltage/frequency transitions and cooling ties. The bootstrap removes CPU OPP
references to avoid unqualified DVFS, not to declare DVFS complete.
See [thermal prerequisites](../../projects/firetabs-android/kernel/THERMAL-SOURCE-PREREQUISITES.md),
[thermal source](../../evidence/thermal-source/), regulator contract and pinned DTS.

## 18. Motion/light sensors, cameras and media blocks

Source declares BMA253/LSM6DS3-related motion variants, ambient-light/proximity
entries and camera children. Some are optional/alternative board declarations;
model specifications, enabled DT and actual working-driver evidence must resolve
presence. Required implementation: per-variant driver, bus address, IRQ/power/
orientation/calibration; camera additionally needs sensor identification, MIPI RX,
clock/regulator/reset sequence and ISP/userspace integration. Media decode/encode
requires its power/clock/IOMMU/firmware contract. These are later peripherals,
not prerequisites for the RAM-only PID1 milestone. Do not list them as supported
because nodes or related drivers compile.

## 19. Retained logs and reset observability

Existing vendor retained backend uses DBGC header and a64KiB console zone at
0x444bf000 inside a larger reserved region. The target maps the existing zone via
console-only ramoops parameters. Entry-stub marker recovery is proven; a modern
Linux record is not. Record identity, generation, bounds, cache publication and
reset-retention semantics are part of this contract; an old record cannot prove
the new kernel executed. Keep full Image integrity, actual Linux checkpoints and
USB PID1 evidence distinct. See ACK RAM contract and runtime receipt.

## 20. Android ABI, security and userspace contract

An ARM64 kernel does not imply64-bit Android apps on the interim32-bit system.
Maintained Android integration needs resolved COMPAT/page size, Binder, cgroups,
BPF/networking, filesystems, device nodes, initramfs/init and enforcing SELinux,
plus matching HALs and firmware interfaces. The controlled PID1 preserves a tested
enforcing policy, but generic VM success is not device policy acceptance. The
working Android11 baseline is not current maintained ValethonOS. Follow the
ordered roadmap after Linux startup; do not jump to app feature work.

## Known gaps and implementation order

The component categories above provide a complete coverage index; source-derived
values remain bounded by their evidence. This is not a claim that every unknown
has been filled. Current critical path:

1. Finish source-derived early execution/console contract, including vendor-to-ACK
   initialization differences and documentary UART bank/board-net mapping.
2. Identify a concrete violated or missing contract; prepare one test that
   distinguishes actual relocated-image integrity and Linux entry/MMU/PID1 stages.
3. Establish maintained-kernel startup on the tablet with preserved return path.
4. Enable storage and other board providers against this reference, then
   display/input/graphics, networking/power and the remaining Android hardware.

Do not require every peripheral or physical UART measurement before Linux boot.
Do not propose another broad “minimal kernel/normal bootloader/early logs” reset
of the plan: those approaches and their failures are already recorded. Use this
contract to identify what the next change actually tests.

## Reproduction and maintenance

Generate the resource inventory from the archived private trial inputs:

```sh
python3 scripts/build_hardware_resource_inventory.py \
  --bundle out/recovery-linux-pivot/ack-native-trial-runtime-1/target-private \
  --fdtget work/dtb-tool/build/fdtget \
  --output out/douglas-hardware-resources-review.json
```

The exporter uses an explicit hardware-property allowlist, excludes identity/
chosen channels and resolves only references it can interpret. Three controls
cover excluded private channels, direct providers and explicit unresolved pins.
The inventory's two DT hashes bind its source snapshots. This command reads only
local artifacts and does not access the tablet.

For each new result, update the relevant contract section and exact source/
artifact reference, the current issue, project memory and active work queue.
Retain dated earlier audits as history; do not treat their old status as the live
implementation state. Open unknowns need a precise missing fact and source lead,
not a blanket request for more equipment or another round of black-screen tests.

[Validation receipt](../../evidence/independent-recovery/douglas-hardware-contract-validation.json):
three export controls, exact reproduction, new-Python checks, local links and
Android evidence checks pass. The repository-wide integrity command stops at an
unchanged pre-existing no-op test helper in `test_source_usb_shutdown.py:201`;
it is not reported as passing. No tablet acquisition or firmware test ran.
