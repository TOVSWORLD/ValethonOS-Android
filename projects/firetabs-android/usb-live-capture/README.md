# Live USB logging capture — current hardware path

The owner selected USB logging/capture as the priority on November 10, 2026.
Use the working 4.9 kernel's existing USB stack; failed-retention and watchdog
work remain documented but do not block this path.

## Observed hardware result

A RAM-only reader captured one exact fresh kernel marker over physical USB ADB.
The serial test then exposed existing `acm.gs0` alongside the existing ADB
configuration. Its first host open failed with PermissionError. The tablet's
helper still restored ADB-only and normal adbd. The corrected receiver opens only
the selected physical device's CDC ACM character node, using a narrow privileged
fd transfer if needed. The receiver stays unprivileged; no host group, ACL, udev
or persistent device property changes are made.

The second test captured 390 bytes containing the exact marker read from
`/dev/kmsg`, saved/synced on the Linux host and hash-checked on the controller.
ADB-only and normal UID2000 adbd were restored automatically. No boot/recovery
write or reboot occurred in either test. This qualifies a kernel-marker→ACM→host
path on the working kernel, not full logging across a failed handoff.

[Actual results, failed attempt and controls](../../../evidence/independent-recovery/live-usb-capture-result.json).

## Tools and limits

`kmsg_probe.c` reads only one unique matching kernel marker for the ADB transport
probe. `acm_trial.c` captures a fresh matching kernel marker before USB changes,
adds only the ACM function link, transmits that kernel-record body for a 30-second
window, and attempts original-mode restoration locally without host commands.
It changes no descriptors or properties and exposes no storage or command shell.
It refuses a foreign existing function and deletes only its owned link after
unbind. The original ADB function remains. Configfs/driver operations can block;
this is not a hardware-guaranteed wall-clock deadline. Physical recovery may be
needed if a driver stalls, although both observed tests restored normally.

`run_live_acm_probe.py` defaults to read-only preflight. Execution consumes an
exact artifact-bound authorization. `capture_live_acm_probe.py` selects one CDC
ACM interface by physical port, VID/PID and character-device identity, opens once,
requires the exact trial frame and syncs private raw bytes. Its privileged helper
opens only the selected node and passes the fd through a private socket; root
peer and opened-node identities are checked. Root does not run the receiver or
write capture files. No arbitrary USB device is selected and no open is retried.

Thirteen actual C restoration/refusal controls passed on Linux; six Python
physical-endpoint controls and a real pseudo-terminal fd-transfer control passed.
The source-only compile/control checks do not establish kernel boot acceptance.

## Next: kernel console before Android

The exact 4.9 source already implements CONFIG_U_SERIAL_CONSOLE and a builtin
CDC ACM serial gadget. `prepare_usb_console_source.py` keeps binding disabled by
default so the native source boot retains ADB. The diagnostic target alone opts
in with `g_serial.ft_bind=1`, an exact `g_serial.ft_trial=<32hex>` and
`console=ttyGS0`. It keeps the original driver descriptor/probe path after this
explicit guard. Console support can replay kernel messages without waiting for
Android init to start a logging daemon. It cannot emit before USB hardware/driver
initialization, and host receipt still requires a hardware test.

The isolated USB-console native kernel build is in progress. Required config
changes are USB_G_SERIAL, U_SERIAL_CONSOLE, and selected USB_F_OBEX only. Existing
native CPU gates/orderly route and security configuration are preserved. No new
watchdog/timer change is part of this build. No console-enabled Image has booted.

```sh
python3 -m unittest discover -s tests -p 'test_live_acm_capture.py'
python3 -m unittest discover -s tests -p 'test_usb_console_source.py'
# Linux host controls against the actual temporary helper:
cc -std=c11 -O2 -Wall -Wextra -Werror \
  -Iprojects/firetabs-android/usb-live-capture \
  tests/usb_acm_restore_harness.c -o /tmp/usb-acm-restore-controls
```
