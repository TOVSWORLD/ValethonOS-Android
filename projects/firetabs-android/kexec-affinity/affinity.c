/* SPDX-License-Identifier: GPL-2.0 */
/* Four one-shot AFFINITY_INFO queries only. No CPU_OFF/ON/SUSPEND or registers.
 * Firmware that never returns cannot be preempted by a host timeout.
 */
#include <linux/module.h>
#include <linux/init.h>
#include <linux/of.h>
#include <linux/cpu.h>
#include <linux/preempt.h>
#include <linux/arm-smccc.h>
#include <linux/string.h>
#include "legacy_affinity_policy.h"

static int __init affinity_init(void)
{
 struct device_node *psci, *cpus, *node;
 struct arm_smccc_res response;
 const char *method;
 u32 fid, cells, targets[4], value;
 unsigned cpu, current_cpu, online = 0, supported = 0;
 long result[4];
 int ret = -EINVAL;
 if (!of_machine_is_compatible("mediatek,mt8163")) return -ENODEV;
 psci = of_find_node_by_path("/psci");
 cpus = of_find_node_by_path("/cpus");
 if (!psci || !cpus) goto out_nodes;
 if (of_property_read_string(psci,"method",&method) ||
     of_property_read_u32(psci,"affinity_info",&fid) ||
     !kxaff_legacy_allowed(1,!!of_device_is_compatible(psci,"arm,psci"),
                           !strcmp(method,"smc"),fid) ||
     of_property_read_u32(cpus,"#address-cells",&cells) || cells != 1)
  goto out_nodes;
 for (cpu = 0; cpu < 4; cpu++) {
  node = of_get_cpu_node(cpu,NULL);
  if (!node) { ret = -EINVAL; goto out_nodes; }
  ret = of_property_read_u32(node,"reg",&value);
  of_node_put(node);
  if (ret || value != cpu) { ret = -EINVAL; goto out_nodes; }
  targets[cpu] = value;
 }
 ret = 0;
out_nodes:
 of_node_put(cpus); of_node_put(psci);
 if (ret) return ret;
 get_online_cpus();
 if (num_possible_cpus() != 4) { put_online_cpus(); return -EINVAL; }
 for (cpu=0; cpu<4; cpu++) {
  if (!cpu_possible(cpu)) { put_online_cpus(); return -EINVAL; }
  if (cpu_online(cpu)) online |= 1U << cpu;
 }
 current_cpu = get_cpu();
 pr_info("KXAFF v1 fid=84000004 conduit=smc queries=4 current_cpu=%u online_mask=%x\n",
         current_cpu,online);
 for (cpu=0; cpu<4; cpu++) {
  arm_smccc_smc(KXAFF_FID,targets[cpu],0,0,0,0,0,0,&response);
  result[cpu] = (long)(s32)response.a0; /* This DT selects SMC32. */
 }
 put_cpu();
 put_online_cpus();
 for (cpu=0; cpu<4; cpu++) {
  if (result[cpu] >= 0 && result[cpu] <= 2) supported++;
  pr_info("KXAFF cpu=%u target=%x result=%ld\n",cpu,targets[cpu],result[cpu]);
 }
 pr_info("KXAFF complete supported=%u current_on=%u state_changes=0 handoff=0\n",
         supported,current_cpu<4 && result[current_cpu]==0);
 return 0;
}
static void __exit affinity_exit(void)
{
 pr_info("KXAFF unloaded state_changes=0 handoff=0\n");
}
module_init(affinity_init);
module_exit(affinity_exit);
MODULE_LICENSE("GPL v2");
MODULE_DESCRIPTION("One-shot MT8163 legacy AFFINITY_INFO query; no state-changing calls");
MODULE_VERSION("1");
