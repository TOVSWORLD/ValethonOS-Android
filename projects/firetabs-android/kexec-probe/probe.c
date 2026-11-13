/* SPDX-License-Identifier: GPL-2.0 */
/* Compatibility probe only. No image loading, device shutdown or handoff code. */
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kallsyms.h>
#include <linux/smp.h>
#include <linux/utsname.h>
#include <asm/page.h>

static int __init kxprobe_init(void)
{
	static const char * const names[] = {
		"machine_shutdown", "migrate_to_reboot_cpu", "kernel_restart_prepare",
		"cpu_hotplug_enable", "cpu_do_switch_mm", "__flush_dcache_area",
		"__hyp_set_vectors", "set_cpu_boot_mode_flag",
	};
	unsigned long current_el;
	unsigned int i;

	asm volatile("mrs %0, CurrentEL" : "=r" (current_el));
	pr_info("KXPROBE v1 release=%s page_shift=%u current_el=%lu online_cpus=%u\n",
		init_utsname()->release, (unsigned int)PAGE_SHIFT,
		(current_el >> 2) & 3, num_online_cpus());
	for (i = 0; i < ARRAY_SIZE(names); ++i)
		pr_info("KXPROBE symbol=%s present=%u\n", names[i],
			kallsyms_lookup_name(names[i]) != 0);
	pr_info("KXPROBE complete handoff_attempted=0\n");
	return 0;
}

static void __exit kxprobe_exit(void)
{
	pr_info("KXPROBE unloaded handoff_attempted=0\n");
}
module_init(kxprobe_init);
module_exit(kxprobe_exit);
MODULE_LICENSE("GPL v2");
MODULE_DESCRIPTION("Read-only ARM64 Linux-to-Linux compatibility probe; no handoff");
MODULE_VERSION("1");
