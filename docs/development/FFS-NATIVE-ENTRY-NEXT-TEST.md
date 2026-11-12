# Next milestone: positively observe accepted native kexec entry

November 12, 2026. Built, linked and checked offline. Read-only tablet preflight
passed. This new Image, FunctionFS hold and jump have not run on the tablet.

The last capture proved Android init received the exact target and entered
shutdown. It did not establish entry into kernel_kexec. Original boot/config,
recovery and normal ADB were verified after the owner's hard-boot return.

## The discriminating change

Exact FunctionFS source unregisters the entire configfs gadget on its last ADB
descriptor close, removing sibling ACM too. The live mount is named `adb` and
has no no_disconnect option. No USB-specific shutdown action was found in the
limited init-file search; that does not exclude every teardown path.

The new kernel adds a **default-off, root-only, current-boot hold**. On MT8163,
for the ADB function only, an explicit enable plus a fresh 32-hex nonce selects
the driver's existing no_disconnect branch on last close. It emits a
nonce-bound priority-zero checkpoint. It does not skip explicit gadget unbind,
negative-open-count recovery, controller shutdown or device/DMA shutdown.
The host reader and USB descriptor identities are unchanged.

The actual console C functions reproduced an early-completion race: completion
could clear req_busy before the sender overwrote it as busy again. Ownership
is now set before queue submission; success does not overwrite completion.
Both completion schedules and queue rejection pass. The 8 KB buffer is unchanged.
The controller instead saves the four printk values and temporarily selects
console level 1, favoring priority-zero checkpoints over teardown noise.

Inside kernel_kexec, **after acquiring its mutex and accepting a loaded image**,
the MT8163/PID-1/default-image path emits:

`KXHANDOFF native_entry=1 image_present=1`

It then requests a one-second sleep before kernel_restart_prepare and device
shutdown, providing USB a drain opportunity. The existing namespaced dispatcher,
CPU-off gates, cache/MMU/exception-level transition and relocation are unchanged.
This does not guarantee real-time delivery or independent recovery.

## One owner-attended approval covers both stages

1. Use the exact prepared source boot candidate once. Verify the new source
   boot and **restore/read back the original full boot on flash before moving
   on**. Recovery is never written. The hold remains off by default during boot.
2. Read fresh source DT/RAM, build the exact target bundle with a fresh nonce and
   fixed Image/original initrd, check all memory reservations, and bind the
   resulting manifest/client hashes under the same approval. Do not load the
   offline preview; the runner refuses it.
3. Arm the nonce-bound FunctionFS hold only in its default unowned state, save
   printk settings and set level 1. Arm source capture and require a fresh
   kernel-only USB marker **before loading**. If a check fails, stop without
   jumping; the helper restores ADB-only and the controller disables/clears
   its hold and restores printk before unrooting. Do not overwrite foreign state.
4. Arm target capture, load once, verify loaded state and original flash/recovery
   again, acknowledge helper handoff intent, and request the exact orderly jump
   once. The helper itself issues no reboot. Preserve both captures privately,
   synced and hash-verified. No post-request tablet command or automatic retry.
5. If needed, return by unplugging USB, holding only Power for 40 seconds,
   releasing, waiting 5 seconds and reconnecting the same cable/port. Original
   boot is already on flash before the jump. Verify original boot/config/recovery
   and normal ADB after return. Do not change a recovery menu.

The host target window remains five minutes. One approval covers the one source
boot/restore and at most one jump; there is no second per-stage approval when
checks pass. A source-boot failure stops before any jump and uses the existing
bounded rollback path. Owner assistance may still be required; automatic return
is unqualified. All older trial approvals remain consumed.

## Pass/fail meaning

- Fresh source USB challenge: confirms source kernel-console capture before load.
- Fresh `KXUSB_FFS ... adb_last_close=retained`: confirms the guarded last-close
  branch actually ran. Absence does not establish which teardown path occurred.
- **Fresh native-entry checkpoint after the source challenge: the next milestone
  passes.** Native kexec accepted an image under its mutex. It does not prove
  CPU shutdown, relocation or target entry.
- Fresh target nonce on its own console: separately proves target kernel entry.
  A complete Android boot remains a further qualification.

If native entry is observed but the target remains absent, proceed to the
device-shutdown/CPU-off/relocation interval. Do not return to the live logging
baseline. If it is not observed, retain the actual positive checkpoints and
choose a different discriminating follow-up rather than repeating blindly.

[Prepared artifacts and checks](../../evidence/independent-recovery/ffs-native-entry-preparation-result.json).
[Exact single-use approval policy](../../evidence/independent-recovery/ffs-console-two-stage-authorization-template.json).
[Default-read-only two-stage driver](../../scripts/run_source_usb_trial.py).
