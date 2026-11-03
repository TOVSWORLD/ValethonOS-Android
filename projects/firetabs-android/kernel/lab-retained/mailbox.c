// SPDX-License-Identifier: GPL-2.0-only
/* Private bounded log experiment: no filesystem, userspace write API or reset.
 * An exact DT nonce + seeded experimental p5 tail + full prefix SHA256 are
 * mandatory. This is not permission to execute on a physical device.
 */
#include <linux/blkdev.h>
#include <linux/bio.h>
#include <linux/mm.h>
#include <linux/delay.h>
#include <linux/fs.h>
#include <linux/file.h>
#include <linux/init.h>
#include <linux/kdev_t.h>
#include <linux/kmsg_dump.h>
#include <linux/kthread.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/slab.h>
#include <linux/utsname.h>
#include <linux/vmalloc.h>
#include <crypto/sha2.h>
#include "retained_mailbox.h"

struct mailbox_context { struct file *file; u8 *hash_buffer; struct page *page; };
static u8 mailbox_nonce[32];
static int mailbox_holder;
static int mailbox_block(struct mailbox_context *c, unsigned long offset, bool write)
{
 struct bio *bio; int ret;
 if ((offset & (VM_HEADER-1)) || offset > VM_PARTITION-VM_HEADER) return -EINVAL;
 if (write && (offset < VM_SLOT_BASE || offset >= VM_PARTITION-VM_HEADER)) return -EINVAL;
 bio=bio_alloc(file_bdev(c->file),1,write?REQ_OP_WRITE:REQ_OP_READ,GFP_KERNEL);
 if(!bio)return -ENOMEM;
 bio->bi_iter.bi_sector=offset>>9;
 if(bio_add_page(bio,c->page,VM_HEADER,0)!=VM_HEADER){bio_put(bio);return -EIO;}
 ret=submit_bio_wait(bio);bio_put(bio);return ret;
}
static int mailbox_read(void *opaque, unsigned long offset, void *buffer, unsigned long count)
{
 struct mailbox_context *c=opaque;
 if ((offset & (VM_HEADER-1)) || !count || count>VM_HEADER) return -EINVAL;
 if(mailbox_block(c,offset,false))return -EIO;
 memcpy(buffer,page_address(c->page),count);return 0;
}
static int mailbox_write(void *opaque, unsigned long offset, const void *buffer, unsigned long count)
{
 struct mailbox_context *c=opaque;const u8 *input=buffer;
 if ((offset & (VM_HEADER-1)) || offset<VM_SLOT_BASE || offset>VM_PARTITION-VM_HEADER || !count || ALIGN(count,VM_HEADER)>VM_PARTITION-VM_HEADER-offset) return -EINVAL;
 for(unsigned long at=0;at<count;at+=VM_HEADER){
  unsigned long n=min_t(unsigned long,count-at,VM_HEADER);
  memset(page_address(c->page),0,VM_HEADER);memcpy(page_address(c->page),input+at,n);
  if(mailbox_block(c,offset+at,true))return -EIO;
 }
 return 0;
}
static int mailbox_flush(void *opaque)
{
 return blkdev_issue_flush(file_bdev(((struct mailbox_context *)opaque)->file));
}
static int mailbox_prefix(void *opaque, const unsigned char *expected)
{
 struct mailbox_context *c = opaque; struct sha256_ctx hash; u8 result[32], want[32];
 memcpy(want, expected, sizeof(want)); sha256_init(&hash);
 for (unsigned long at=0; at<VM_BASE; at+=VM_HEADER) {
  if (mailbox_read(c, at, c->hash_buffer, VM_HEADER)) return -EIO;
  sha256_update(&hash, c->hash_buffer, VM_HEADER);
 }
 sha256_final(&hash, result);
 return memcmp(result, want, sizeof(want)) ? -EINVAL : 0;
}
static int mailbox_thread(void *unused)
{
 struct mailbox_context c={0}; struct block_device *bdev;
 struct vm_io io={&c,mailbox_read,mailbox_write,mailbox_flush,mailbox_prefix};
 u8 *scratch=NULL; char *payload=NULL; int ret=-ENODEV;
 /* Bounded discovery only. No data write until all guards below and vm_commit. */
 for (unsigned attempt=0;attempt<30;attempt++) {
  c.file=bdev_file_open_by_dev(MKDEV(179,5),BLK_OPEN_READ|BLK_OPEN_WRITE|BLK_OPEN_EXCL,&mailbox_holder,NULL);
  if (!IS_ERR(c.file)) break;
  c.file=NULL; msleep(1000);
 }
 if (!c.file) goto out;
 bdev=file_bdev(c.file);
 if (!bdev_is_partition(bdev)||bdev_partno(bdev)!=5||strcmp(bdev->bd_disk->disk_name,"mmcblk0")||bdev_nr_bytes(bdev)!=VM_PARTITION||bdev_read_only(bdev)) goto out;
 c.page=alloc_page(GFP_KERNEL);c.hash_buffer=kmalloc(VM_HEADER,GFP_KERNEL);scratch=kmalloc(VM_HEADER,GFP_KERNEL);payload=vmalloc(VM_CAPACITY);
 if (!c.page||!c.hash_buffer||!scratch||!payload) {ret=-ENOMEM;goto out;}
 for (unsigned commit=0;commit<12;commit++) {
  struct kmsg_dump_iter iter;struct vm_record record;size_t used=0;
  int lead=scnprintf(payload,VM_CAPACITY,"VALETHON RETAINED KERNEL LOG v1 release=%s snapshot=%u\n",init_utsname()->release,commit+1);
  kmsg_dump_rewind(&iter);
  kmsg_dump_get_buffer(&iter,true,payload+lead,VM_CAPACITY-lead,&used);
  ret=vm_commit(&io,mailbox_nonce,(const u8 *)payload,lead+used,scratch,&record);
  if (ret) break; /* Never retry a failed/partial write. Earlier slot remains. */
  pr_info("valethon-mailbox: verified sequence %llu bytes %u\n",record.sequence,record.used);
  if(commit!=11)msleep(5000);
 }
 out:
 if(c.file)fput(c.file);
 if(c.page)__free_page(c.page);
 kfree(c.hash_buffer);kfree(scratch);vfree(payload);
 pr_info("valethon-mailbox: stopped result %d; no retry\n",ret);
 return 0;
}
static int __init mailbox_init(void)
{
 struct device_node *chosen;const u8 *nonce;int size;
 if(!of_machine_is_compatible("mediatek,mt8163"))return 0;
 chosen=of_find_node_by_path("/chosen");if(!chosen)return 0;
 nonce=of_get_property(chosen,"valethon,trial-nonce",&size);
 if(nonce&&size==32)memcpy(mailbox_nonce,nonce,sizeof(mailbox_nonce));
 of_node_put(chosen);
 if(vm_zero(mailbox_nonce,sizeof(mailbox_nonce)))return 0;
 return PTR_ERR_OR_ZERO(kthread_run(mailbox_thread,NULL,"valethon-log"));
}
late_initcall(mailbox_init);
MODULE_LICENSE("GPL");
