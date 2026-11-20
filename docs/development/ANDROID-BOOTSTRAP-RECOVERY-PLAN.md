# Reach first Android home without another logging loop

Current hardware state: original TWRP, verified recovery/system, candidate left
installed, original backups retained. Both previous tablet cases are consumed.
No tablet action or new cloud/full-Android build is authorized by this document.

1. **Compare the actual failed candidates.** Preserve the first visible-console
   panic and combined diagnostic failure as separate results. The diagnostic
   added a kernel serial gadget, ramoops node and pre-init wrapper together; its
   silence cannot locate the failure. Use the original direct Android/framebuffer
   path for the next functional candidate. Complete USB streaming is not a gate.
2. **Exercise real Android offline.** Run the compiled ARM32 Android `/init` and
   completed system image together, with the original maintained kernel. Change
   only the VM storage path; keep system read-only, SELinux enforcing and no
   network. Prior small C-init probes did not exercise this dependency chain.
3. **Group confirmed startup repairs.** The real-image VM exposed missing
   `CPUSETS_V1`: SetupCgroups aborted before creating the process hierarchy, which
   prevented ueventd/APEX bootstrap and requested a reboot. Enabling this plus
   selected `PROC_PID_CPUSET` removes that failure with the original system image;
   all four bootstrap APEX packages activate and apexd-bootstrap exits zero.
   A later keystore critical-service abort remains. A VM-only early data-directory
   ordering experiment did not remove it and is excluded from the candidate.
   Existing Android logs identify the actual abort: no default KeyMint/Keymaster
   service is installed. Include the pinned AIDL Rust nonsecure KeyMint service
   and AIDL Rust nonsecure Gatekeeper APEX for the volatile-data engineering
   profile; do not claim hardware-backed protection. Add kernel PSI support:
   the shipped lmkd otherwise exits because its PSI monitor cannot initialize.
   Keep APEXes uncompressed on system: the first image's CAPEX payloads would use
   183,853,056 of the 268,435,456 volatile-data bytes; placing their originals on
   system adds 39,849,984 bytes before new native dependencies. Runtime ENOSPC was
   not observed, so this is a measured resource-risk reduction, not a panic cause. Do not send a known generic startup failure to the tablet.
   Record VM hardware limitations separately; a VM success is not tablet boot.
4. **Prepare one corrected hardware candidate.** Reuse the existing Android
   binaries, original RAM/DT/loader path and original Android init. Include only
   confirmed compatibility repairs. If a text init repair is required, validate
   the modified filesystem, labels, exact block delta and full resulting digest;
   New security-service binaries are required. Build that selected native/image
   update from the saved workspace rather than syncing/compiling Android afresh.
   Operational resource/budget/cache details remain in the private build project.
   No paid follow-up has started; its new resource allowance needs owner review.
   Keep original recovery/userdata excluded and original rollback available.
5. **Run one grouped attended test.** Check Android startup, Valethon animation,
   setup/home, touch/display and available authenticated USB/Enforcing evidence
   in one bounded session. Start existing capture before boot; absence of complete
   USB logs does not justify more standalone logging trials. Fresh exact case,
   watch cue, one boot request and one original-recovery return. No automatic
   retry. Save a photo of visible failures if possible.
6. **Use the actual result.** Preserve the first concrete fatal error and update
   issue #333 plus memory/current queue. No rebranding old experiments as new
   strategies, no unverified panic cause, no source/VM pass called tablet success.

Major milestone remains maintained Android setup/home with working display/touch,
SELinux enforcing and a verified return path. Logging is supporting evidence.
