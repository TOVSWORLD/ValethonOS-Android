/* SPDX-License-Identifier: GPL-2.0 */
#ifndef KXSTAGE_UAPI_H
#define KXSTAGE_UAPI_H
#include <linux/types.h>
#include <linux/ioctl.h>
#define KXSTAGE_MAX_SEGMENTS 3
#define KXSTAGE_MAX_BYTES (32ULL * 1024 * 1024)
struct kxstage_request { __u64 entry, nr_segments, segments, flags; };
struct kxstage_status {
 __u64 attempted, prepared, segments, owned_pages, execute_disabled;
 __u64 mem_bytes[KXSTAGE_MAX_SEGMENTS];
 __u32 crc32[KXSTAGE_MAX_SEGMENTS];
 __u32 reserved;
};
#define KXSTAGE_PREPARE _IOW('K', 0x31, struct kxstage_request)
#define KXSTAGE_STATUS _IOR('K', 0x32, struct kxstage_status)
#define KXSTAGE_DISCARD _IO('K', 0x33)
/* Deliberately no execute operation. Unknown ioctls return EOPNOTSUPP. */
#endif
