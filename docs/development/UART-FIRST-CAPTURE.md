# Douglas UART: prepared capture tools and conditional bench procedure

> November 17 correction: [NEXT-MILESTONE-PLAN.md](NEXT-MILESTONE-PLAN.md)
> supersedes the bench-first selection below. Trace the older working kernels and
> exact-board documentation first. Physical measurement has not been demonstrated
> necessary; no technician, purchase or opening is selected. The recorder/DT
> preparation remains usable, while physical wiring is unqualified.

Historical November 16 selection: receive-only capture from the
known-working tablet, after a board-level operator identifies TX and its electrical
level. No experimental Linux jump is selected. Software preparation is complete;
physical pin identification and voltage measurement are still required. The owner
confirmed no multimeter, scope/logic analyzer or UART adapter is available. Do not
repeat the equipment question or select a purchase from an assumed voltage.

## Findings that change the test

The consumed ACK DT disables `/soc/serial@11002000` and has no UART earlycon or
console argument. The exact ACK config already builds SERIAL_EARLYCON,
SERIAL_8250_CONSOLE and SERIAL_8250_MT6577. The new offline DT preview enables
only UART0, selects its stdout path at 921600n8, and adds `earlycon`,
`console=ttyS0,921600n8`, `keep_bootcon` and `ignore_loglevel`. Every other DT
property, including firmware/storage/watchdog settings, is compared unchanged.
This is a configuration preview, not an executable jump bundle; the consumed
trial cannot load it without a separately prepared package.

The cached, pinned ACK driver sets MEM32 access with register shift 2 in its
earlycon callback. It **does not initialize the UART baud generator**. Therefore
921600 is a source-backed starting setting, not a measured guarantee. The
normal console driver can configure baud later; early output depends on inherited
UART/clock/pin state. No assumption of bootloader UART initialization is made.
The archived source boot also includes `printk.disable_uart=1`, so silence from
a normal boot cannot alone reject wiring or establish a failed kernel entry.
Any calibration setting change must first be matched to the running kernel.

Vendor MT8163 pin definitions map GPIO79/function1 to RX0 and
GPIO80/function1 to TX0. Those are SoC pin indices, not PCB pad numbers. The
consumed target's pinctrl resolves to exactly those functions. UART0's alternate
GPIO87/88 functions are MSDC2; this board's removable-card pinctrl uses MSDC1
GPIO121–126. A microSD UART breakout is therefore not established by that alternate
function. Do not buy or wire one on that assumption.

The source contains USB-PHY UART-switch code, but the hardware-tested source
config has MTK_UART_USB_SWITCH disabled. That code does not establish a working
USB serial console, a cable pinout or voltage on this tablet. No USB-PHY switch
is selected: it would change the existing USB control path without a qualified
replacement.

## Recovered earlier board documentation

The October 27 original-route review already found the maintainer's
[annotated Douglas board fallback](https://xdaforums.com/posts/90488396/), recorded
in `CURRENT-STOCK-ENTRY-RETURN.md` and
`evidence/douglas-original-route/report.json`. The old chat was checked again in
this session: it selected USB-first recovery plus this hardware fallback after
reaching the original XDA thread. This is the board reference the owner recalled;
it must be reused rather than presented as undiscovered.

That record qualifies the existence of a recovery/BootROM contact reference,
**not a UART TX/RX/voltage map**. The live post could not be retrieved by this
session's text browser, so no new claims are made about its image. Match it to
the actual board as a layout reference, and keep any BootROM contact distinct
from a UART candidate. No pad shorting or replay of the already-completed
original recovery procedure is part of this test.

The hardware route is therefore a bench task, not an immediate owner wiring
exercise. With no instruments available, a board-level operator who already owns
the tools can establish the electrical facts and baseline in one session. A new
adapter purchase is premature until a usable signal and its level are established.
No appointment or third-party contact has been made.

## Exact physical evidence still needed

The owner's earlier answer says no internal photos or PCB revision record exists;
that question is resolved. A competent board-level operator must now inspect the
actual unit and provide the following in one bench session:

1. Confirm the actual board marking/revision and accessible pad locations against
   the 2017 KFDOWI/SX034QT mechanical references. Record an oriented board image
   and pad labels; hide serial numbers/barcodes before any public use.
2. Establish a suitable ground reference and identify a candidate TX waveform
   using high-impedance instrumentation during an ordinary working boot. Measure
   idle-high/low levels and bit timing before choosing a receiver. Do not infer
   UART voltage from the battery or assume that a pad beside ground is TX.
3. Select an input whose documented thresholds/ratings match the measured signal.
   Connect only the verified board TX to receiver RX and the qualified common
   ground. Leave adapter TX, VCC, RTS and DTR physically disconnected. Ordinary
   USB adapters can drive those outputs when opened even if software never writes.
4. Record raw waveform plus decoded bytes across a known-working boot. Begin with
   measured timing, using 921600/8N1 as the source-backed candidate; preserve raw
   data if the bootloader and kernel use different baud settings. A scope/logic
   analyzer is preferable to blind baud changes. Determine whether any silence
   is console suppression before considering an experimental Linux boot.

The **first acceptance result** is attributable, readable bootloader or working
kernel output with measured electrical levels and a repeatable capture. Receiving
noise, seeing an idle-high pad, an empty file, or a printed host marker does not
qualify UART. Stop after this baseline and review actual output. Do not combine
pad discovery with flashing, pad shorting, BootROM entry or an experimental jump.

Opening/connector handling must be assessed for the actual unit by the operator.
The same-generation cover-only account shows a clip-fit enclosure but does not
establish our board's battery connector technique or electrical isolation. No
heating, motherboard removal or generic connector motion is prescribed here.
A power-off alone does not disconnect the battery. If safe access needs an
unverified mechanical action, resolve that with the operator before proceeding.

## Capture tool ready for the bench

`scripts/capture_uart_receive_only.py` uses the Python standard library on POSIX.
Run it on the host connected to the qualified receiver. Linux provides the native
921600 termios setting; a host without it is rejected before opening the port.
Use the receiver's stable device path, not an automatically selected USB port:

```sh
python3 scripts/capture_uart_receive_only.py \
  --port /dev/serial/by-id/REPLACE_WITH_VERIFIED_RECEIVER \
  --baud 921600 --seconds 120 \
  --output out/uart-working-boot-1
```

After `UART_CAPTURE_READY`, the operator performs the agreed ordinary boot. The
tool sends no serial bytes, flushes no pending input and issues no modem-line
ioctls. It captures at most 16 MiB/120 seconds, fsyncs received chunks, records
SHA256/byte count, and restores/verifies terminal settings on exit (ignoring the
driver-maintained PENDIN input flag). Raw bytes and reports are private. It has no
ADB, reboot, flashing or kernel acceptance behavior. Disconnected physical output
wires remain necessary; software read-only access is not electrical isolation.

Five PTY controls passed: exact binary bytes including control characters,
no port write calls, settings restoration, private file permissions, empty-data
interpretation, bounded prefix, invalid limits and non-character-device refusal.
These are host tests; no real adapter or tablet UART has been tested.

Reproduce the UART DT preview from the consumed trial's private DT/config:

```sh
python3 scripts/prepare_ack_uart_preview.py \
  --bundle out/recovery-linux-pivot/ack-native-trial-runtime-1/target-private \
  --kernel out/valethon-first-draft-1 \
  --output out/recovery-linux-pivot/ack-uart-preview-NEW \
  --fdtget work/dtb-tool/build/fdtget --fdtput work/dtb-tool/build/fdtput
```

The result binds the exact consumed DT and kernel hashes, verifies GPIO79/80
pinmux, and rejects any unrelated DT delta. Its report is explicit `loadable:false`.
No new kernel build, boot/restore, load or jump was performed in this preparation.

## Sources and access outcomes

- [Amazon model specifications](https://developer.amazon.com/docs/device-specs/ft-device-specifications-firehd-models.html): 2017 KFDOWI/MT8163 identity; no UART pinout.
- [Firsthand 2017 cover-only account](https://sakue.com/archives/821): explicitly KFDOWI/SX034QT; cover geometry only. It does not label UART pads or establish voltage.
- [FCC filing index](https://fccid.io/2AIP4-4639): internal-photo exhibit 3376398 is listed. Retrieval from the FCC and both mirrors returned HTTP403 in this session. Internal photos were **not inspected**; listing an exhibit is not board evidence.
- [iFixit SX034QT firsthand question](https://www.ifixit.com/Answers/View/550468/%28SX034QT%29%2BHow%2Bthe%2Bheck%2Bdoes%2Bthe%2Bmotherboard%2Bcome%2Bout%2Bof%2Bthis%2Bthing): title names SX034QT but site category identifies a different generation. Excluded as an exact-unit connector/removal procedure.
- [FTDI cable specification](https://ftdichip.com/wp-content/uploads/2023/07/DS_TTL-232RG_CABLES.pdf): adapter variants have specific I/O levels and can exceed 921600 baud. Does not establish tablet voltage; no adapter purchase selected.
- [Saleae input thresholds](https://www.saleae.com/support/specifications-hardware/electrical-characteristics/supported-voltages): some analyzers cannot resolve 1.8V logic. Select against measured signal, not a generic product label.
- Cached exact source/pinmux hashes: `evidence/uart-log-contract/report.json`
  and `pin-source-hashes.json`; the relevant tested config/DT hashes are bound by
  the UART preparation receipt. The postmarketOS wiki was access-denied;
  no pad/voltage claim is inferred from it.

The decisive missing input is actual board/electrical evidence, not another
literature-search loop. If the owner lacks suitable tools, use a board-level
repair/debug operator for the scoped receive-only baseline. No booking or message
to anyone else has been made.
