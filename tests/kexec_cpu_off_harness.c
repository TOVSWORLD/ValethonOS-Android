/* SPDX-License-Identifier: GPL-2.0 */
#include <string.h>
#include "bounded_secondary_off.h"

struct fake {
 unsigned regs[0x800 / 4];
 unsigned cpu, mode, reads, writes, fw, locks, unlocks, held, access, fail_at;
 unsigned log_reg[32], log_value[32];
 unsigned long long clock;
};
struct result {
 int error;
 unsigned phase, steps, writes, off, reads, fw, locks, unlocks, held;
 unsigned log_reg[32], log_value[32];
};
static unsigned long long now(void *p)
{
 struct fake *f = p;
 if (f->mode == 7) return ++f->clock * 1000;
 if (f->mode == 8) return f->clock++ ? 99 : 100;
 return 0; /* Frozen clock must still terminate through the shared step cap. */
}
static int firmware(void *p, unsigned cpu)
{
 struct fake *f = p; f->fw++;
 if (f->mode == 1) return 1;
 if (f->mode == 2) return -EOPNOTSUPP;
 if (f->mode == 12) return -EIO;
 if (f->mode == 14 && cpu == 2) return 1;
 return 0;
}
static int read_reg(void *p, unsigned reg, unsigned *v)
{
 struct fake *f = p; f->reads++; f->access++;
 if (f->fail_at && f->access == f->fail_at) return -EIO;
 if (reg >= 0x800 || reg % 4) return -EINVAL;
 *v = f->regs[reg/4];
 if (f->mode == 3 && reg == 0x720) *v = 0;
 if (f->mode == 9 && reg == 0x720 && f->held) *v = 0;
 if ((reg == 0x264 || reg == 0x26c || reg == 0x274) &&
     (*v & 1) && f->mode != 5) *v |= 256;
 if (reg == 0x60c || reg == 0x610) {
  if (f->writes >= 9) *v = 0;
  if (f->mode == 6 && reg == 0x60c) *v |= 1U << (f->cpu + 9);
  if (f->mode == 10 && reg == 0x610) *v |= 1U << (f->cpu + 9);
  if (f->mode == 11) *v |= 1U << 9; /* Unrelated CPU0 must not prevent success. */
 }
 return 0;
}
static int write_reg(void *p, unsigned reg, unsigned value)
{
 struct fake *f = p; unsigned n = f->writes++;
 f->access++;
 if (n < 32) { f->log_reg[n] = reg; f->log_value[n] = value; }
 if (f->fail_at && f->access == f->fail_at) return -EIO;
 if (!f->held || reg >= 0x800 || reg % 4) return -EINVAL;
 f->regs[reg/4] = value;
 return 0;
}
static int try_lock(void *p)
{
 struct fake *f = p; f->locks++;
 if (f->mode == 4) return 0;
 f->held = 1; return 1;
}
static void unlock(void *p)
{
 struct fake *f = p; f->unlocks++; f->held = 0;
}
static void relax(void *p) { (void)p; }

void run(unsigned cpu, unsigned mode, unsigned fail_at, unsigned limit,
         unsigned long long timeout, struct result *r)
{
 struct fake f;
 struct kxoff_result status;
 struct kxoff_ops ops = { &f, now, firmware, read_reg, write_reg, try_lock, unlock, relax };
 memset(&f, 0, sizeof(f)); memset(r, 0, sizeof(*r));
 f.cpu = cpu; f.mode = mode; f.fail_at = fail_at;
 f.regs[0x720/4] = 0xfU << 16;
 f.regs[0x218/4] = f.regs[0x21c/4] = f.regs[0x220/4] = 0x8000004d;
 f.regs[0x60c/4] = f.regs[0x610/4] = 0xfU << 9;
 if (mode == 13) ops.firmware_off = 0;
 r->error = kxoff_secondary(&ops, cpu, limit, timeout, &status);
 r->phase = status.phase; r->steps = status.steps;
 r->writes = status.writes; r->off = status.off_confirmed;
 r->reads = f.reads; r->fw = f.fw; r->locks = f.locks;
 r->unlocks = f.unlocks; r->held = f.held;
 memcpy(r->log_reg, f.log_reg, sizeof(f.log_reg));
 memcpy(r->log_value, f.log_value, sizeof(f.log_value));
}

void gate(unsigned mode, unsigned possible, unsigned online, unsigned failures,
          unsigned fail_at, struct result *r)
{
 struct fake f;
 struct kxoff_result status;
 /* NULL writer makes any accidental power-sequencing path fail immediately. */
 struct kxoff_ops ops = { &f, now, firmware, read_reg, 0, try_lock, unlock, relax };
 memset(&f, 0, sizeof(f)); memset(r, 0, sizeof(*r));
 f.cpu = 1; f.mode = mode; f.fail_at = fail_at;
 r->error = kxoff_verify_all(&ops, possible, online, failures, 32, 100000, &status);
 r->phase = status.phase; r->steps = status.steps;
 r->writes = status.writes; r->off = status.off_confirmed;
 r->reads = f.reads; r->fw = f.fw; r->locks = f.locks;
 r->unlocks = f.unlocks; r->held = f.held;
}
