#include "physical.h"
#include "../diagnostic-usb/retained_mailbox.h"
unsigned long lp_context_bytes(void){return sizeof(struct lp_context);}
void lp_pinned_ops(struct lp_ops *ops){
 if(ops){ops->read=(void*)0x4bd358e9;ops->write=(void*)0x4bd35a89;}
}
int lp_init(struct lp_context *c,const struct lp_plan *p,const struct lp_ops *ops,const struct lh_service *hash,void *buffer,unsigned capacity){
 if(!c)return -1;c->stopped=1;
 if(c->initialized)return -1;c->initialized=1;
 if(!p||!ops||!hash||!p->device||!p->bindings_verified||!p->buffer_owned||!p->first_sector||
    p->first_sector>(~0ULL-VM_PARTITION)/512||p->first_sector>0x100000000ULL-VM_PARTITION/512||p->bytes!=VM_PARTITION||p->gpt_partition!=5||p->mmc_partition!=8||
    !ops->read||!ops->write||!hash->compress||!hash->verified||!buffer||((unsigned long)buffer&3)||capacity!=VM_HEADER||
    (unsigned long)buffer>~0UL-VM_HEADER)return -1;
 c->plan=*p;c->ops=*ops;c->hash=*hash;c->buffer=buffer;c->stopped=0;return 0;
}
int lp_read(void *opaque,unsigned long offset,void *out,unsigned long n){
 struct lp_context *c=opaque;if(!c||c->stopped)return -1;
 if(!out||!n||n>8192||(offset&511)||offset>VM_PARTITION-n)goto fail;
 unsigned count=(unsigned)((n+511)&~511UL);
 void *destination=out;
 if((n&511)||((unsigned long)out&3)){
  if(count>VM_HEADER||offset>VM_PARTITION-count)goto fail;
  destination=c->buffer;
 }
 /* Always invoke the pinned wrapper's aligned path. Its global unaligned
  * bounce buffer is neither borrowed nor assumed initialized. */
 unsigned got=c->ops.read(c->plan.device,c->plan.first_sector*512+offset,destination,count,8);
 if(got!=count)goto fail;
 if(destination!=out){volatile unsigned char *d=out;for(unsigned i=0;i<n;i++)d[i]=c->buffer[i];}
 return 0;
 fail:c->stopped=1;return -2;
}
int lp_read_absolute(void *opaque,unsigned long long offset,void *out,unsigned n){
 struct lp_context *c=opaque;if(!c||c->stopped)return -1;
 unsigned long long first=c->plan.first_sector*512;
 if(offset<first||offset-first>VM_BASE||!n||n>VM_BASE||offset-first>VM_BASE-n){c->stopped=1;return -2;}
 return lp_read(c,(unsigned long)(offset-first),out,n);
}
int lp_write(void *opaque,unsigned long offset,const void *input,unsigned long n){
 struct lp_context *c=opaque;if(!c||c->stopped)return -1;
 if(!input||n!=VM_HEADER||(offset&(VM_HEADER-1))||offset<VM_SLOT_BASE||offset>VM_PARTITION-2*VM_HEADER)goto fail;
 unsigned got=c->ops.write(c->plan.device,input,c->plan.first_sector*512+offset,(unsigned)n,8);
 if(got!=n)goto fail;return 0;
 fail:c->stopped=1;return -2;
}
int lp_prefix(void *opaque,const unsigned char *expected){
 struct lp_context *c=opaque;if(!c||c->stopped)return -1;
 unsigned long at=(unsigned long)expected,buffer=(unsigned long)c->buffer;
 struct lhs_state state={0};if(!expected||at>~0UL-32||(at<buffer+VM_HEADER&&at+32>buffer)||lhs_init(&state,&c->hash))goto fail;
 for(unsigned offset=0;offset<VM_BASE;offset+=VM_HEADER){
  if(lp_read(c,offset,c->buffer,VM_HEADER)||lhs_add(&state,c->buffer,VM_HEADER))goto fail;
 }
 if(lhs_finish(&state,expected))goto fail;return 0;
 fail:c->stopped=1;return -2;
}
