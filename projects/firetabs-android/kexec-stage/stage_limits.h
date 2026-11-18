/* SPDX-License-Identifier: GPL-2.0 */
#ifndef KXSTAGE_LIMITS_H
#define KXSTAGE_LIMITS_H
/* Shared, side-effect-free validation runs on the kernel's copied segment list. */
static inline int kxstage_layout_ok(unsigned long long entry, unsigned long nr,
 const struct kexec_segment *s)
{
 unsigned long i, j;
 unsigned long long total = 0;
 if (!nr || nr > 3 || (entry & 3)) return 0;
 for (i = 0; i < nr; i++) {
  unsigned long long end = (unsigned long long)s[i].mem + s[i].memsz;
  if (!s[i].memsz || s[i].memsz > 32ULL*1024*1024 ||
      end < s[i].mem || (s[i].mem & 4095) || (end & 4095) ||
      s[i].bufsz > s[i].memsz || (s[i].bufsz && !s[i].buf)) return 0;
  total += s[i].memsz;
  if (total > 32ULL*1024*1024) return 0;
  for (j = 0; j < i; j++)
   if (s[i].mem < s[j].mem + s[j].memsz && s[j].mem < end) return 0;
 }
 return s[0].bufsz && entry >= s[0].mem && entry - s[0].mem < s[0].bufsz;
}
#endif
