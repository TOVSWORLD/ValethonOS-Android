# First combined Douglas kernel draft

This is a complete first bring-up kernel/ramdisk/DT package, not the finished
Android OS or a claim that every board peripheral works. It integrates the pinned
ACK base and existing MT8163 clock, pinctrl, power, IOMMU, USB, SYM827, MIPI, DSI and
PWM ports in one final Image. eMMC and retained logging are built in. SELinux stays
enforcing. The normal PM/suspend callback core is included to satisfy the pinned
tracing exports; the ramdisk does not request suspend or CPU hotplug. No new recovery automation, observer or entry delay is included.

The matched own-source DT preserves measured memory/reservations and enables the
supported USB0 peripheral and conservative eMMC route. Secondary CPUs, display,
touch, audio and wireless remain runtime-unqualified; compiling their providers
does not justify enabling unsupported hardware paths. Primary-only boot follows
the unresolved vendor mt-boot/PSCI contract. This draft is for useful boot results,
not Android app QA.

Logging has two independent consumers: nonce-bound /dev/kmsg over configfs ACM and
kernel-owned boot-tail VLOG0001 snapshots, retrievable with the existing read-only
collector in recovery. A 1MiB timestamped printk ring plus initcall tracing records
probe order/errors; panic timeout0 avoids requesting an automatic reboot. The
retained writer cannot cover failures before eMMC/its late-init worker. USB cannot
cover failures before USB initializes. No positive hardware log is claimed.

Build: dispatch kernel-baseline.yml mode=first-draft, entry_checkpoint=none.
The run retains Image/Image.gz/config/System.map, integrated provider objects,
enforcing PID1/ramdisk/policy hashes and the bounded VM result. Package with
scripts/finish_first_draft.py using that exact run's files. Installation and arming
remain separate and blocked until a complete reviewed physical procedure.
