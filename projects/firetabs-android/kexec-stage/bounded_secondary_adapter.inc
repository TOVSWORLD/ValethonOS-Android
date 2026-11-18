/* SPDX-License-Identifier: GPL-2.0 */
/* Compile-only candidate included at end of matched MT8163 mtcmos.c.
 * Uses its actual regmap and shared lock, not arbitrary physical mappings.
 */
#include <linux/ktime.h>
#include <linux/cpu.h>
#include <linux/psci.h>
#include <uapi/linux/psci.h>
#include <asm/smp_plat.h>
#include "bounded_secondary_off.h"

struct kxoff_context { unsigned long flags; };
static unsigned long long kxoff_now(void *context)
{
 return ktime_get_ns();
}
static int kxoff_firmware(void *context, unsigned cpu)
{
 int ret;
 if (!psci_ops.affinity_info) return -EOPNOTSUPP;
 ret = psci_ops.affinity_info(cpu_logical_map(cpu), 0);
 if (ret < 0) return ret;
 if (ret == PSCI_0_2_AFFINITY_LEVEL_OFF) return 0;
 if (ret == PSCI_0_2_AFFINITY_LEVEL_ON ||
     ret == PSCI_0_2_AFFINITY_LEVEL_ON_PENDING) return 1;
 return -EIO;
}
static int kxoff_reg_read(void *context, unsigned reg, unsigned *value)
{
 return regmap_read(regmap_spm, reg, value);
}
static int kxoff_reg_write(void *context, unsigned reg, unsigned value)
{
 return regmap_write(regmap_spm, reg, value);
}
static int kxoff_try_lock(void *context)
{
 struct kxoff_context *c = context;
 return spin_trylock_irqsave(&spm_cpu_lock, c->flags) ? 1 : 0;
}
static void kxoff_unlock(void *context)
{
 struct kxoff_context *c = context;
 spin_unlock_irqrestore(&spm_cpu_lock, c->flags);
}
static void kxoff_relax(void *context) { cpu_relax(); }

int spm_mtcmos_secondary_off_bounded(unsigned cpu)
{
 struct kxoff_context context;
 struct kxoff_result result;
 const struct kxoff_ops ops = {
  .context = &context, .now = kxoff_now, .firmware_off = kxoff_firmware,
  .read = kxoff_reg_read, .write = kxoff_reg_write,
  .try_lock = kxoff_try_lock, .unlock = kxoff_unlock, .relax = kxoff_relax,
 };
 int ret;
 /* Bind symbolic header constants used by the host-tested core to vendor ABI. */
 BUILD_BUG_ON(SPM_POWERON_CONFIG_SET != 0 || SPM_PROJECT_CODE != 0xb16);
 BUILD_BUG_ON(SPM_SLEEP_TIMER_STA != 0x720);
 BUILD_BUG_ON(SPM_PWR_STATUS != 0x60c || SPM_PWR_STATUS_2ND != 0x610);
 BUILD_BUG_ON(SPM_CA7_CPU1_PWR_CON != 0x218 || SPM_CA7_CPU2_PWR_CON != 0x21c || SPM_CA7_CPU3_PWR_CON != 0x220);
 BUILD_BUG_ON(SPM_CA7_CPU1_L1_PDN != 0x264 || SPM_CA7_CPU2_L1_PDN != 0x26c || SPM_CA7_CPU3_L1_PDN != 0x274);
 BUILD_BUG_ON(CA7_CPU1 != (1U << 10) || CA7_CPU2 != (1U << 11) || CA7_CPU3 != (1U << 12));
 BUILD_BUG_ON(CA7_CPU1_STANDBYWFI != (1U << 17) || CA7_CPU2_STANDBYWFI != (1U << 18) || CA7_CPU3_STANDBYWFI != (1U << 19));
 BUILD_BUG_ON(PWR_RST_B != 1 || PWR_ISO != 2 || PWR_ON != 4 || PWR_ON_2ND != 8 || PWR_CLK_DIS != 16);
 BUILD_BUG_ON(SRAM_CKISO != 32 || SRAM_ISOINT_B != 64 || L1_PDN != 1 || L1_PDN_ACK != 256);
 if (cpu < 1 || cpu > 3 || cpu_online(cpu)) return -EINVAL;
 if (IS_ERR_OR_NULL(regmap_spm)) return -ENODEV;
 /* Candidate policy values, not hardware-qualified timing parameters. */
 ret = kxoff_secondary(&ops, cpu, 4096, 100000000ULL, &result);
 pr_info("KXOFF cpu=%u result=%d phase=%u steps=%u writes=%u off_confirmed=%u\n",
         cpu, ret, result.phase, result.steps, result.writes, result.off_confirmed);
 return ret;
}

int spm_mtcmos_secondary_off_check(unsigned long failures)
{
 struct kxoff_context context;
 struct kxoff_result result;
 const struct kxoff_ops ops = {
  .context = &context, .now = kxoff_now, .firmware_off = kxoff_firmware,
  .read = kxoff_reg_read, .write = NULL,
  .try_lock = kxoff_try_lock, .unlock = kxoff_unlock, .relax = kxoff_relax,
 };
 unsigned cpu, possible = 0, online = 0;
 int ret;
 if (IS_ERR_OR_NULL(regmap_spm)) return -ENODEV;
 if (num_possible_cpus() != 4) return -EINVAL;
 for (cpu = 0; cpu <= 3; cpu++) {
  if (cpu_possible(cpu)) possible |= 1U << cpu;
  if (cpu_online(cpu)) online |= 1U << cpu;
 }
 ret = kxoff_verify_all(&ops, possible, online, failures, 4096,
                        100000000ULL, &result);
 /* Caller must hold CPU hotplug serialization across this gate and jump. */
 if (num_online_cpus() != 1 || !cpu_online(0)) ret = -EBUSY;
 return ret;
}
