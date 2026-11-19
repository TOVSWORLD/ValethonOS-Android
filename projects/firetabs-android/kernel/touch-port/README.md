# Douglas touch/input integration

Successor to the visually observed display/backlight foundation, issue #330.
Working Android binds Goodix-TS at I2C0x5d and exposes goodix-ts. Capability
metadata gives800/1280 coordinate maxima; the cached186-byte configuration
exactly matches public hvt groups0-3. The live-read section is all zero and
is not evidence of chip ID, sensor ID or active controller contents.

Preserve GPIO46 reset/GPIO35 interrupt, with GPIO35 mapping to EINT46,
falling edge. Working driver sets VGP2 to3.0V and optional IO rail to1.8V.
Use the existing maintained Goodix driver with a vendor-compatible alias;
it retains runtime chip-ID selection. Ship the source-derived matching
configuration through its existing firmware-config mechanism. No controller
flash updater is enabled. No touch device has been enabled/tested yet.

Next finish source-backed DT, enforcing read-only input access and a large
visual touch grid. Handle inherited watchdog state alongside this work;
repeated-reset cause is not yet established. Keep invalid USB status separate
and carry the achieved physical screen forward without another display proof.
