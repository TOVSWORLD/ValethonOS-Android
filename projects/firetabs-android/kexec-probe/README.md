# Linux-to-Linux compatibility probe

This is the first bounded runtime step of the kexec investigation. It is a
logging-only module with **no kernel loader, image copying, CPU offlining, device
shutdown, MMU change, hypervisor call or handoff implementation**. It reports
CurrentEL, online CPU count, page size and symbol-name availability through the
working Linux kernel's printk/dmesg channel. Symbol addresses are never called or
printed. Loading/unloading a kernel module remains privileged code execution.

## Exact target and artifact

Target the installed LineageOS kernel, **not TWRP**:

- Kernel: `4.9.337-g72940eb733af`.
- Public source: [amazon-oss 72940eb733af8df948cc216cb977cd8be9cba5a9](https://github.com/amazon-oss/android_kernel_amazon_mt8163/tree/72940eb733af8df948cc216cb977cd8be9cba5a9).
- Extracted actual configuration SHA256: `b087199622287207923f9449eedd820ee1940ee82157e77648e36b4b959f3859`.
- Original boot SHA256: `08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e`.
- Probe SHA256: `371fe33c9b98515cac131f4c03a4208486aada660146b8b66ac41d44e7c3e889` (6144 bytes).
- Probe scope: `kexec-compatibility-probe-1`.

The existing TWRP is a different 3.18 kernel with no recovered configuration.
Its symbol-name report must not be treated as the LineageOS ABI. A stale cached
3.18 vendor config also must not replace the actual 4.9 boot-image configuration.

The probe was compiled on Linux with GCC 13.3.0. The installed kernel banner names
GCC 6.3.1. Source/config/release/import checks pass, but runtime ABI acceptance is
not claimed. The kernel's normal module-version checks must remain enabled, and a
rejection must stop the attempt. Never use force-load options or patch CRC checks.

## Reproduce without a tablet

`scripts/build_kexec_probe.py` uses the pinned source directory and exact extracted
configuration. It runs olddefconfig and refuses any changed option. It builds only
six provider objects and extracts their absolute exported CRCs; the resulting
`probe-provider.symvers` is a **limited table for this probe**, not a full kernel's
Module.symvers. No completed kernel image is needed or produced by this recipe.

```sh
python3 scripts/build_kexec_probe.py \
  --source /path/android_kernel_amazon_mt8163-72940eb733af8df948cc216cb977cd8be9cba5a9 \
  --config /path/extracted-working.config --out /path/probe-build \
  --probe projects/firetabs-android/kexec-probe
python3 scripts/verify_kexec_probe.py \
  --module /path/probe-build/probe/kxprobe.ko \
  --symvers /path/probe-build/probe-provider.symvers --output /path/probe-verified.json
python3 -m unittest discover -s tests -p 'test_kexec_probe*.py'
```

The verifier checks ELF architecture/type, a narrow imported-symbol allowlist,
release and ABI flags, and CRCs for every import plus module_layout. These checks
are necessary artifact checks, not proof of hardware execution or a complete code
safety proof. Source and compiler provenance remain part of review.

## Proposed single compatibility test

The first approved runtime test completed on November 8, 2026; see the actual
result below. This source file does not authorize another execution. Obtain exact approval
and current owner availability before changing the tablet's boot state or loading
the module. No new boot image or bootstrap is flashed. Boot the installed LineageOS
normally once; the source runner itself never reboots. Use the installed rooted-debugging capability and a root ADB session. If it is
disabled, stop and ask the owner to enable it; do not install root or change settings
automatically.

`scripts/run_kexec_probe.py` defaults to preflight only. It requires normal Android,
the exact kernel release, exact live /proc/config.gz configuration and exact full
normal boot hash. It rejects an already-loaded module, stale KXPROBE records and a
non-RAM /dev. Execute mode requires a separate private authorization bound to the
exact module/boot hashes, scope and current owner approval/availability, with
`handoff_allowed` false. It stages the module only in /dev tmpfs, checks readback,
performs one ordinary insmod, collects the full fresh ten-record report, unloads
once, verifies module absence, deletes RAM staging and preserves private logs.
No retry, force-loading, account interaction, security-policy change or reboot.
If insertion is rejected, preserve dmesg and stop. If ADB is lost, preserve the
uncertain-state receipt and use the already reviewed recovery return; do not repeat.

Success means a complete fresh compatibility report plus verified unload/cleanup.
It does not qualify kexec or target-kernel logging. CurrentEL does not by itself
identify the original cold-boot exception level. Symbol presence does not establish
call signatures, CPU-parking completion, DMA shutdown or firmware compatibility.
The next kexec port still needs those contracts, correct 64-bit register handling,
and an independently observable handoff to an already-working target kernel.

## Actual runtime result — November 8, 2026

The exact approved probe was inserted once, accepted by the live kernel's ABI
checks, and produced all ten fresh printk records through ADB. It reported EL1,
4KB pages, three online CPUs at that instant, and all eight queried symbols
present, including set_cpu_boot_mode_flag. It unloaded successfully and module
absence/RAM staging cleanup were verified. No kernel handoff, flash or additional
reboot occurred in the runner. Full private evidence archives match on lab/controller.

Before insertion, one preflight stopped because rooted debugging was disabled; the
owner enabled it. Two exec-out stream upload attempts then timed out, each with
zero module insertions and verified cleanup. Switching to standard adb push into
verified RAM-backed /dev fixed the transfer; the module bytes never changed.
The runner now requires root adbd and uses that transfer protocol. No force-load,
module rejection or repeated module execution occurred.

This proves the probe's module ABI and live printk/ADB capture on this working
kernel. It does not prove any kexec handoff, CPU shutdown, highest firmware EL,
new-kernel entry or target-kernel logging. The next source work can use the matched
4.9 ABI and live reports; no new physical test is selected by this result.
