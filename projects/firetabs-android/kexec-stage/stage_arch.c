/* SPDX-License-Identifier: GPL-2.0 */
#include <linux/errno.h>
#include "kexec.h"
/* Allocation bookkeeping only: no page-table creation or CPU state changes. */
int machine_kexec_prepare(struct kimage *image) { return 0; }
void machine_kexec_cleanup(struct kimage *image) { }
/* Defense in depth. No ioctl reaches this symbol; no arch restart code linked. */
int kernel_kexec(void) { return -EOPNOTSUPP; }
