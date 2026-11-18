#define _XOPEN_SOURCE 700
#include <assert.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>
#define current get_current() /* Real kernel macro collision regression. */
#include "retained_mailbox.h"
struct context {int fd,fail,operation,writes;};
static int rd(void *c,unsigned long offset,void *out,unsigned long count){return pread(((struct context *)c)->fd,out,count,(off_t)offset)==(ssize_t)count?0:-1;}
static int wr(void *c,unsigned long offset,const void *data,unsigned long count){struct context *x=c;assert(offset>=VM_SLOT_BASE&&offset+count<=VM_PARTITION-VM_HEADER);x->writes++;if(++x->operation==x->fail)return -1;return pwrite(x->fd,data,count,(off_t)offset)==(ssize_t)count?0:-1;}
static int flush(void *c){struct context *x=c;if(++x->operation==x->fail)return -1;return fsync(x->fd);}
/* Fixture identity: every immutable byte has independently known content. The
 * real kernel backend must implement SHA256, not this fixture-only predicate. */
static int prefix(void *c,const unsigned char *digest){(void)digest;unsigned char b[4096];for(unsigned long at=0;at<VM_BASE;at+=sizeof(b)){if(rd(c,at,b,sizeof(b)))return -1;for(unsigned i=0;i<sizeof(b);i++)if(b[i]!=(unsigned char)((at+i)%251))return -1;}return 0;}
int main(int argc,char **argv){assert(argc==3);struct context c={.fd=open(argv[1],O_RDWR),.fail=atoi(argv[2])};assert(c.fd>=0);struct stat st;assert(!fstat(c.fd,&st)&&S_ISREG(st.st_mode)&&st.st_size==VM_PARTITION);unsigned char nonce[32],scratch[VM_HEADER];for(unsigned i=0;i<32;i++)nonce[i]=(unsigned char)i;struct vm_io io={&c,rd,wr,flush,prefix};struct vm_record r={0};const unsigned char payload[]="C writer persisted before USB\n";int result=vm_commit(&io,nonce,payload,sizeof(payload)-1,scratch,&r);printf("%d %d\n",result,c.writes);close(c.fd);return 0;}
