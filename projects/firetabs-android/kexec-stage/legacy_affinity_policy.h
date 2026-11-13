/* SPDX-License-Identifier: GPL-2.0 */
#ifndef KX_LEGACY_AFFINITY_POLICY_H
#define KX_LEGACY_AFFINITY_POLICY_H
#define KXAFF_FID 0x84000004U
/* Narrow observed legacy board/conduit/DT contract; not a firmware capability claim. */
static inline int kxaff_legacy_allowed(int mt8163, int legacy, int smc,
 unsigned fid)
{
 return mt8163 == 1 && legacy == 1 && smc == 1 && fid == KXAFF_FID;
}
static inline int kxaff_query_args(unsigned long target, unsigned long level)
{
 return target <= 3 && level == 0;
}
#endif
