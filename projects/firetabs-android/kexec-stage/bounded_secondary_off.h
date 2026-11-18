/* SPDX-License-Identifier: GPL-2.0 */
/* Candidate MT8163 secondary shutdown core. No native I/O in this file.
 * Exact ordering/offsets: Amazon source 72940eb733af, mt8163/mtcmos.[ch].
 * Adapter callbacks must finish independently: budgets cannot interrupt a
 * stuck firmware call, regmap access, clock read, or bus transaction.
 */
#ifndef KX_BOUNDED_SECONDARY_OFF_H
#define KX_BOUNDED_SECONDARY_OFF_H
#ifdef __KERNEL__
#include <linux/errno.h>
#else
#include <errno.h>
#endif

enum kxoff_phase {
 KXOFF_VALIDATE, KXOFF_FIRMWARE, KXOFF_WFI, KXOFF_LOCK,
 KXOFF_RECHECK, KXOFF_ISOLATE, KXOFF_SRAM, KXOFF_POWER, KXOFF_DONE
};
struct kxoff_result {
 unsigned phase, steps, writes, locked, off_confirmed;
 int error;
};
struct kxoff_ops {
 void *context;
 unsigned long long (*now)(void *);
 /* 0=explicit firmware OFF, 1=ON/ON_PENDING, negative=error. */
 int (*firmware_off)(void *, unsigned);
 int (*read)(void *, unsigned, unsigned *);
 int (*write)(void *, unsigned, unsigned);
 int (*try_lock)(void *); /* 1=owned, 0=busy, negative=error */
 void (*unlock)(void *);
 void (*relax)(void *);
};
struct kxoff_budget {
 const struct kxoff_ops *ops;
 struct kxoff_result *result;
 unsigned limit;
 unsigned long long start, duration;
};

static inline int kxoff_tick(struct kxoff_budget *b)
{
 unsigned long long now;
 if (b->result->steps >= b->limit) return -ETIMEDOUT;
 b->result->steps++;
 now = b->ops->now(b->ops->context);
 if (now < b->start || now - b->start >= b->duration) return -ETIMEDOUT;
 return 0;
}

static inline int kxoff_read(struct kxoff_budget *b, unsigned reg, unsigned *v)
{
 int ret = kxoff_tick(b);
 return ret ? ret : b->ops->read(b->ops->context, reg, v);
}

static inline int kxoff_write(struct kxoff_budget *b, unsigned reg, unsigned v)
{
 int ret = kxoff_tick(b);
 if (ret) return ret;
 b->result->writes++; /* Attempts, including a failed write. */
 return b->ops->write(b->ops->context, reg, v);
}

static inline int kxoff_update(struct kxoff_budget *b, unsigned reg,
 unsigned clear, unsigned set)
{
 unsigned v;
 int ret = kxoff_read(b, reg, &v);
 return ret ? ret : kxoff_write(b, reg, (v & ~clear) | set);
}

static inline int kxoff_poll(struct kxoff_budget *b, unsigned reg,
 unsigned mask, unsigned expected)
{
 unsigned v;
 int ret;
 for (;;) {
  ret = kxoff_read(b, reg, &v);
  if (ret) return ret;
  if ((v & mask) == expected) return 0;
  b->ops->relax(b->ops->context);
 }
}

/* CPU0/cluster/power-on are deliberately outside this candidate's scope.
 * Caller must already have requested secondary exit using the matched OS path.
 * No retry/rollback is attempted after partial power-down.
 */
static inline int kxoff_secondary(const struct kxoff_ops *ops, unsigned cpu,
 unsigned max_steps, unsigned long long timeout_ns, struct kxoff_result *out)
{
 static const unsigned control[] = {0, 0x218, 0x21c, 0x220};
 static const unsigned l1[] = {0, 0x264, 0x26c, 0x274};
 struct kxoff_budget b;
 unsigned mask, wfi, first, second;
 int ret;
 if (!out) return -EINVAL;
 out->phase = KXOFF_VALIDATE; out->steps = 0; out->writes = 0;
 out->locked = 0; out->off_confirmed = 0; out->error = -EINVAL;
 if (!ops || !ops->now || !ops->firmware_off || !ops->read ||
     !ops->write || !ops->try_lock || !ops->unlock || !ops->relax ||
     cpu < 1 || cpu > 3 || !max_steps || !timeout_ns) return -EINVAL;
 b.ops = ops; b.result = out; b.limit = max_steps;
 b.start = ops->now(ops->context); b.duration = timeout_ns;
 mask = 1U << (cpu + 9); wfi = 1U << (cpu + 16);
 out->phase = KXOFF_FIRMWARE;
 for (;;) {
  ret = kxoff_tick(&b);
  if (ret) goto done;
  ret = ops->firmware_off(ops->context, cpu);
  if (ret < 0) goto done;
  if (!ret) break;
  if (ret != 1) { ret = -EIO; goto done; }
  ops->relax(ops->context);
 }
 out->phase = KXOFF_WFI;
 ret = kxoff_poll(&b, 0x720, wfi, wfi);
 if (ret) goto done;
 out->phase = KXOFF_LOCK;
 for (;;) {
  ret = kxoff_tick(&b);
  if (ret) goto done;
  ret = ops->try_lock(ops->context);
  if (ret < 0) goto done;
  if (ret == 1) { out->locked = 1; break; }
  if (ret != 0) { ret = -EIO; goto done; }
  ops->relax(ops->context);
 }
 /* Recheck WFI under the same lock used by the original MTCMOS code. */
 out->phase = KXOFF_RECHECK;
 ret = kxoff_read(&b, 0x720, &first);
 if (ret) goto done;
 if (!(first & wfi)) { ret = -EBUSY; goto done; }
 out->phase = KXOFF_ISOLATE;
 ret = kxoff_write(&b, 0x000, (0xb16U << 16) | 1U);
 if (ret) goto done;
 ret = kxoff_update(&b, control[cpu], 0, 1U << 1); /* PWR_ISO */
 if (ret) goto done;
 ret = kxoff_update(&b, control[cpu], 0, 1U << 5); /* SRAM_CKISO */
 if (ret) goto done;
 ret = kxoff_update(&b, control[cpu], 1U << 6, 0); /* SRAM_ISOINT_B */
 if (ret) goto done;
 out->phase = KXOFF_SRAM;
 ret = kxoff_update(&b, l1[cpu], 0, 1U); /* L1_PDN */
 if (ret) goto done;
 ret = kxoff_poll(&b, l1[cpu], 1U << 8, 1U << 8); /* ACK */
 if (ret) goto done;
 out->phase = KXOFF_POWER;
 ret = kxoff_update(&b, control[cpu], 1U, 0); /* reset */
 if (ret) goto done;
 ret = kxoff_update(&b, control[cpu], 0, 1U << 4); /* clock */
 if (ret) goto done;
 ret = kxoff_update(&b, control[cpu], 1U << 2, 0); /* PWR_ON */
 if (ret) goto done;
 ret = kxoff_update(&b, control[cpu], 1U << 3, 0); /* PWR_ON_2ND */
 if (ret) goto done;
 for (;;) {
  ret = kxoff_read(&b, 0x60c, &first);
  if (ret) goto done;
  ret = kxoff_read(&b, 0x610, &second);
  if (ret) goto done;
  if (!(first & mask) && !(second & mask)) break;
  ops->relax(ops->context);
 }
 /* A callback that exhausts wall time on the final read cannot yield PASS. */
 ret = kxoff_tick(&b);
 if (ret) goto done;
 out->phase = KXOFF_DONE; out->off_confirmed = 1;
done:
 if (out->locked) { ops->unlock(ops->context); out->locked = 0; }
 out->error = ret;
 return ret;
}

/* Read-only final certificate for a CPU0-survivor handoff. Caller must keep
 * hotplug serialized from shutdown through relocation; snapshots cannot prove
 * absence of an intervening power-on. Sticky failures cannot be cleared here.
 */
static inline int kxoff_verify_all(const struct kxoff_ops *ops,
 unsigned possible_mask, unsigned online_mask, unsigned long failures,
 unsigned max_steps, unsigned long long timeout_ns, struct kxoff_result *out)
{
 struct kxoff_budget b;
 unsigned cpu, first, second;
 int ret;
 if (!out) return -EINVAL;
 out->phase = KXOFF_VALIDATE; out->steps = 0; out->writes = 0;
 out->locked = 0; out->off_confirmed = 0; out->error = -EINVAL;
 if (!ops || !ops->now || !ops->firmware_off || !ops->read ||
     !ops->try_lock || !ops->unlock || !ops->relax ||
     !max_steps || !timeout_ns || possible_mask != 15 || online_mask != 1)
  return -EINVAL;
 if (failures) { out->error = -EIO; return -EIO; }
 b.ops = ops; b.result = out; b.limit = max_steps;
 b.start = ops->now(ops->context); b.duration = timeout_ns;
 out->phase = KXOFF_FIRMWARE;
 for (cpu = 1; cpu <= 3; cpu++) {
  for (;;) {
   ret = kxoff_tick(&b);
   if (ret) goto done;
   ret = ops->firmware_off(ops->context, cpu);
   if (ret < 0) goto done;
   if (!ret) break;
   if (ret != 1) { ret = -EIO; goto done; }
   ops->relax(ops->context);
  }
 }
 out->phase = KXOFF_LOCK;
 for (;;) {
  ret = kxoff_tick(&b);
  if (ret) goto done;
  ret = ops->try_lock(ops->context);
  if (ret < 0) goto done;
  if (ret == 1) { out->locked = 1; break; }
  if (ret != 0) { ret = -EIO; goto done; }
  ops->relax(ops->context);
 }
 out->phase = KXOFF_POWER;
 ret = kxoff_read(&b, 0x60c, &first);
 if (ret) goto done;
 ret = kxoff_read(&b, 0x610, &second);
 if (ret) goto done;
 if ((first | second) & (7U << 10)) { ret = -EBUSY; goto done; }
 ret = kxoff_tick(&b);
 if (ret) goto done;
 out->phase = KXOFF_DONE; out->off_confirmed = 1;
done:
 if (out->locked) { ops->unlock(ops->context); out->locked = 0; }
 out->error = ret;
 return ret;
}
#endif
