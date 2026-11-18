/* SPDX-License-Identifier: GPL-2.0 */
/* Prepare-only kexec staging. No firmware, CPU shutdown or MMU operations. */
#include <linux/module.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/capability.h>
#include <linux/uaccess.h>
#include <linux/mutex.h>
#include "kexec.h"
#include "kexec_internal.h"
#include "stage_uapi.h"

extern unsigned long kxstage_owned_pages;
static DEFINE_MUTEX(request_lock);
static bool attempted;
static atomic_t opened = ATOMIC_INIT(0);

static void discard_locked(void)
{
 mutex_lock(&kexec_mutex);
 kimage_free(xchg(&kexec_image, NULL));
 mutex_unlock(&kexec_mutex);
}
static int stage_open(struct inode *inode, struct file *file)
{
 if (!capable(CAP_SYS_BOOT)) return -EPERM;
 return atomic_cmpxchg(&opened, 0, 1) ? -EBUSY : 0;
}
static long stage_ioctl(struct file *file, unsigned int command, unsigned long arg)
{
 struct kxstage_request req;
 struct kxstage_status status = { .execute_disabled = 1 };
 unsigned int i;
 int ret = 0;
 if (!capable(CAP_SYS_BOOT)) return -EPERM;
 mutex_lock(&request_lock);
 switch (command) {
 case KXSTAGE_STATUS:
  status.attempted = attempted;
  status.prepared = !!kexec_image;
  status.owned_pages = kxstage_owned_pages;
  if (kexec_image) {
   status.segments = kexec_image->nr_segments;
   for (i = 0; i < status.segments; i++) {
    status.mem_bytes[i] = kexec_image->segment[i].memsz;
    status.crc32[i] = kexec_image->stage_crc[i] ^ ~0U;
   }
  }
  ret = copy_to_user((void __user *)arg, &status, sizeof(status)) ? -EFAULT : 0;
  break;
 case KXSTAGE_PREPARE:
  if (attempted) { ret = -EALREADY; break; }
  if (copy_from_user(&req, (void __user *)arg, sizeof(req))) { ret = -EFAULT; break; }
  if (req.flags || !req.nr_segments || req.nr_segments > KXSTAGE_MAX_SEGMENTS) {
   ret = -EINVAL; break;
  }
  attempted = true;
  ret = sys_kexec_load(req.entry, req.nr_segments,
       (struct kexec_segment __user *)(unsigned long)req.segments, KEXEC_ARCH_AARCH64);
  pr_info("KXSTAGE prepare result=%d segments=%llu owned_pages=%lu execute_disabled=1\n",
          ret, (unsigned long long)req.nr_segments, kxstage_owned_pages);
  break;
 case KXSTAGE_DISCARD:
  discard_locked();
  pr_info("KXSTAGE discard owned_pages=%lu execute_disabled=1\n", kxstage_owned_pages);
  if (kxstage_owned_pages) ret = -EUCLEAN;
  break;
 default:
  ret = -EOPNOTSUPP;
 }
 mutex_unlock(&request_lock);
 return ret;
}
static int stage_release(struct inode *inode, struct file *file)
{
 mutex_lock(&request_lock);
 discard_locked();
 atomic_set(&opened, 0);
 mutex_unlock(&request_lock);
 return 0;
}
static const struct file_operations stage_fops = {
 .owner = THIS_MODULE, .open = stage_open, .release = stage_release,
 .unlocked_ioctl = stage_ioctl,
};
static struct miscdevice stage_device = {
 .minor = MISC_DYNAMIC_MINOR, .name = "kxstage", .fops = &stage_fops, .mode = 0600,
};
static int __init stage_init(void)
{
 int ret = misc_register(&stage_device);
 if (!ret) pr_info("KXSTAGE v1 prepare_only=1 max_bytes=33554432\n");
 return ret;
}
static void __exit stage_exit(void)
{
 misc_deregister(&stage_device);
 discard_locked();
 if (kxstage_owned_pages) pr_err("KXSTAGE accounting failure: retained pages=%lu\n", kxstage_owned_pages);
 pr_info("KXSTAGE unloaded owned_pages=%lu execute_disabled=1\n", kxstage_owned_pages);
}
module_init(stage_init);
module_exit(stage_exit);
MODULE_LICENSE("GPL v2");
MODULE_DESCRIPTION("Bounded prepare-only ARM64 kexec staging; no handoff implementation");
MODULE_VERSION("1");
