from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import retained_log_mailbox as m

class ActualKernelBlockIO(unittest.TestCase):
    def test_actual_bio_frontend_and_codec_against_disk_and_independent_reader(self):
        source=(ROOT/'projects/firetabs-android/kernel/lab-retained/mailbox.c').read_text()
        code=source[source.index('static int mailbox_block'):source.index('static int mailbox_prefix')]
        harness=r'''
#define _XOPEN_SOURCE 700
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include "retained_mailbox.h"
typedef unsigned char u8;
#define GFP_KERNEL 0
#define REQ_OP_READ 0
#define REQ_OP_WRITE 1
#define ALIGN(x,a) (((x)+(a)-1)&~((a)-1))
#define min_t(t,a,b) ((t)(a)<(t)(b)?(t)(a):(t)(b))
struct block_device {int fd;};struct file {struct block_device b;};struct page {unsigned char bytes[4096];};
struct bio {struct {unsigned long bi_sector;}bi_iter;struct block_device *b;struct page *page;int op;};
struct mailbox_context {struct file *file;u8 *hash_buffer;struct page *page;};
static struct block_device *file_bdev(struct file *f){return &f->b;}
static void *page_address(struct page *p){return p->bytes;}
static struct bio *bio_alloc(struct block_device *b,int n,int op,int flags){(void)flags;assert(n==1);struct bio *p=calloc(1,sizeof(*p));assert(p);p->b=b;p->op=op;return p;}
static int bio_add_page(struct bio *b,struct page *p,unsigned n,unsigned off){assert(n==4096&&!off);b->page=p;return (int)n;}
static int submit_bio_wait(struct bio *b){unsigned long off=b->bi_iter.bi_sector*512;assert(!(off%4096)&&off+4096<=VM_PARTITION);ssize_t got;if(b->op){assert(off>=VM_SLOT_BASE&&off+4096<=VM_PARTITION-VM_HEADER);got=pwrite(b->b->fd,b->page->bytes,4096,(off_t)off);}else got=pread(b->b->fd,b->page->bytes,4096,(off_t)off);return got==4096?0:-EIO;}
static void bio_put(struct bio *b){free(b);}
static int blkdev_issue_flush(struct block_device *b){return fsync(b->fd);}
'''+code+r'''
static int prefix(void *v,const unsigned char *sha){(void)sha;struct mailbox_context *c=v;unsigned char p[4096];for(unsigned long at=0;at<VM_BASE;at+=4096){assert(!mailbox_read(c,at,p,4096));for(unsigned i=0;i<4096;i++)if(p[i]!=(unsigned char)((at+i)%251))return -1;}return 0;}
int main(int argc,char **argv){assert(argc==2);struct file f={{open(argv[1],O_RDWR)}};assert(f.b.fd>=0);struct page p;struct mailbox_context c={&f,NULL,&p};struct vm_io io={&c,mailbox_read,mailbox_write,mailbox_flush,prefix};unsigned char nonce[32],scratch[4096],payload[8193];for(unsigned i=0;i<32;i++)nonce[i]=(unsigned char)i;for(unsigned i=0;i<sizeof(payload);i++)payload[i]=(unsigned char)(i%239);struct vm_record record;
assert(mailbox_write(&c,VM_BASE,payload,4096)==-EINVAL);
assert(mailbox_write(&c,VM_PARTITION-VM_HEADER,payload,1)==-EINVAL);
assert(mailbox_write(&c,VM_SLOT_BASE+1,payload,1)==-EINVAL);
assert(!vm_commit(&io,nonce,payload,sizeof(payload),scratch,&record));assert(record.sequence==2);
close(f.b.fd);return 0;}
'''
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);(p/'probe.c').write_text(harness)
            subprocess.run([shutil.which('cc'),'-std=c11','-Wall','-Wextra','-Werror','-O2','-I'+str(ROOT/'projects/firetabs-android/diagnostic-usb'),str(p/'probe.c'),'-o',str(p/'probe')],check=True)
            prefix=bytes(range(251))*(m.BASE//251)+bytes(range(m.BASE%251))
            before,sha=m.prepare(prefix+bytes(m.PARTITION-m.BASE),bytes(range(32)),b'VALETHON HOST CONTROL v1\nnot kernel\n')
            disk=p/'disk';disk.write_bytes(before)
            subprocess.run([str(p/'probe'),str(disk)],check=True)
            after=disk.read_bytes();r=m.inspect(after,bytes(range(32)),sha)['latest']
            self.assertEqual(r['payload'],bytes(i%239 for i in range(8193)))
            self.assertEqual(after[:m.SLOT_BASE],before[:m.SLOT_BASE]);self.assertEqual(after[-4096:],bytes(4096))
            # Sector padding belongs exclusively to this record slot.
            self.assertEqual(after[m.SLOT_BASE+m.SLOT+m.HEADER+8193:m.SLOT_BASE+m.SLOT+m.HEADER+12288],bytes(4095))
