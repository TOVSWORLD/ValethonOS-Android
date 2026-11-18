# Next milestone execution plan

November17,2026. **Reached on Douglas:** maintained Linux initialization,
controlled enforcing PID1 and its exact fresh USB identity header.
[Runtime evidence](../../evidence/independent-recovery/ack-usb-end-to-end-runtime-result.json).
Original Android boot/config/recovery and normal ADB verified after return.
Latest owner Power confirmation is pending in the receipt.

## Next product milestone: read-only internal storage on the maintained kernel

Continue the existing Phase2 boot-foundation work under #22. Carry forward the
working RAM exclusion correction and USB/PID1 path. Trace the working4.9 eMMC
clocks, regulators, pinctrl, interrupts and MT8163 host implementation into the
pinned maintained tree using the [hardware contract](DOUGLAS-HARDWARE-CONTRACT.md).
Prepare a RAM-boot profile that enables the internal eMMC controller only and
keeps user-space block writes forbidden. Do not mount or modify personal data.

The concrete next acceptance is discovery of the internal storage plus a
read-only verification of the already-known original boot artifact, reported
through the existing USB path. This advances the Android boot foundation;
maintained Android userspace/init/adbd integration follows. It does not claim
that a maintained Android build, Android UI or general hardware qualification
already exists. Use existing build resources and prepare/validate the exact
candidate before requesting another owner-attended hardware attempt.

## Transfer follow-up, not a prerequisite

The40-byte VLOG0002+fresh nonce is verified. Zero complete records/no terminal
means the optional kernel-record stream stopped after identity; it does not
erase the kernel/PID1/USB milestone or block storage/userspace work. A host
termios.error cleanup escape was fixed offline so the actual capture result
survives disconnect. Primary post-header stream cause remains open under #348.
Do not launch a logging-only device test to re-prove working stages. Owner
explicitly requested this. Use a functional storage/status response in the next
integrated test rather than making complete kernel-log retrieval an entry gate.

Scope5 and earlier approvals are consumed. One protected source boot/restore and
RAM jump per new owner-attended trial, original boot restored/read back before
jump, recovery untouched and bounded read-only return. No wrapper replay or
automatic retry. Preserve historical failures in the existing issues.
