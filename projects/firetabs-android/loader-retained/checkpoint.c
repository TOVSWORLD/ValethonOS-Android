#include "checkpoint.h"
static void lc_copy(unsigned char *d,const unsigned char *s,unsigned long n){for(unsigned long i=0;i<n;i++)d[i]=s[i];}
static int lc_read(void *opaque,unsigned long at,void *out,unsigned long n){
 struct lc_context *c=opaque;
 if((at&(VM_HEADER-1))||!n||n>VM_HEADER||at>VM_PARTITION-n)return -1;
 return c->underlying.read(c->underlying.context,at,out,n);
}
static int lc_write(void *opaque,unsigned long at,const void *input,unsigned long n){
 struct lc_context *c=opaque;
 if((at&(VM_HEADER-1))||!n||n>VM_HEADER||at<VM_SLOT_BASE||at>VM_PARTITION-2*VM_HEADER)return -1;
 for(unsigned i=0;i<VM_HEADER;i++)c->block[i]=0;
 lc_copy(c->block,input,n);
 return c->underlying.write(c->underlying.context,at,c->block,VM_HEADER);
}
static int lc_flush(void *opaque){struct lc_context *c=opaque;return c->underlying.flush(c->underlying.context);}
static int lc_prefix(void *opaque,const unsigned char *expected){
 struct lc_context *c=opaque;
 if(!vm_equal(expected,c->config.prefix,32))return -1;
 /* First commit hashes the full prefix. Subsequent commits only write the tail;
  * adapter target/exclusivity must remain immutable throughout this boot. */
 if(!c->prefix_verified){if(c->underlying.prefix_sha256(c->underlying.context,expected))return -1;c->prefix_verified=1;}
 return 0;
}
unsigned long lc_context_bytes(void){return sizeof(struct lc_context);}
unsigned lc_payload_bytes(void){return LC_BYTES;}
int lc_init(struct lc_context *c,const struct lc_config *config,const struct vm_io *io){
 if(!c||!config||!io)return -1;
 for(unsigned long i=0;i<sizeof(*c);i++)((unsigned char*)c)[i]=0;
 c->stopped=1;
 if(!io->read||!io->write||!io->flush||!io->prefix_sha256||!config->durability_verified||!config->exclusive_target_verified||
    config->partition_bytes!=VM_PARTITION||config->gpt_partition!=5||config->mmc_partition!=8||
    !config->target_first_sector||config->target_first_sector>(~0ULL-VM_PARTITION)/512||
    !config->logical_boot_first_sector||config->logical_boot_first_sector>(~0ULL-VM_PARTITION)/512||
    vm_zero(config->nonce,32)||vm_zero(config->prefix,32))return -1;
 c->config=*config;c->underlying=*io;
 c->guarded=(struct vm_io){c,lc_read,lc_write,lc_flush,lc_prefix};c->stopped=0;return 0;
}
static int lc_fresh(struct lc_context *c){
 static const unsigned char control[]="VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n";
 struct vm_record r={0};int valid=vm_read_record(&c->guarded,0,c->config.nonce,&r,c->scratch);
 if(valid!=1||r.sequence!=1||r.used!=sizeof(control)-1||!vm_equal(c->scratch,control,sizeof(control)-1))return -1;
 for(unsigned long at=VM_SLOT_BASE+VM_HEADER;at<VM_PARTITION-VM_HEADER;at+=VM_HEADER){
  if(lc_read(c,at,c->scratch,VM_HEADER))return -1;
  unsigned start=0;
  if(at==VM_SLOT_BASE+VM_HEADER){if(!vm_equal(c->scratch,control,sizeof(control)-1))return -1;start=sizeof(control)-1;}
  if(!vm_zero(c->scratch+start,VM_HEADER-start))return -1;
 }
 return 0;
}
static int lc_previous(struct lc_context *c){
 struct vm_record a={0},b={0};
 int va=vm_read_record(&c->guarded,0,c->config.nonce,&a,c->scratch);
 int vb=vm_read_record(&c->guarded,1,c->config.nonce,&b,c->scratch);
 if(va<0||vb<0||(va&&vb&&a.sequence==b.sequence))return -1;
 struct vm_record latest={0};if(va)latest=a;if(vb&&b.sequence>latest.sequence)latest=b;
 if(latest.sequence!=c->commits+1||latest.index!=(c->commits&1)||latest.used!=LC_BYTES)return -1;
 if(vm_read_record(&c->guarded,latest.index,c->config.nonce,&latest,c->scratch)!=1||
    !vm_equal(c->scratch,c->payload,LC_BYTES))return -1;
 return 0;
}
int lc_emit(struct lc_context *c,const struct lc_point *p){
 if(!c||!p)return -1;
 if(c->stopped)return -1;
 if(c->finished||p->mode!=0)return 1; /* recovery/fastboot: no new I/O */
 if(p->stage==LC_READ){
  unsigned long long logical=c->config.logical_boot_first_sector*512;
  if(!((p->kind==1&&p->requested_offset==logical)||(p->kind==2&&p->requested_offset==logical+2048)))return 1;
 }
 if(p->stage<LC_MODE||p->stage>LC_PRE_SHUTDOWN||(!c->commits&&p->stage!=LC_MODE)||
    (c->commits&&p->stage==LC_MODE)||c->commits>=LC_MAX_COMMITS){c->stopped=1;return -2;}
 if((!c->commits&&lc_fresh(c))||(c->commits&&lc_previous(c))){c->stopped=1;return -3;}
 unsigned char *out=c->payload;unsigned tag=sizeof(LC_TAG)-1;
 lc_copy(out,(const unsigned char*)LC_TAG,tag);out+=tag;
 unsigned fields[]={p->stage,p->mode,p->stage==LC_READ?p->kind:0,5,8,
                    p->stage==LC_READ?p->read_bytes:0,p->stage==LC_READ?p->destination:0,
                    (p->stage==LC_HANDOFF||p->stage==LC_PRE_SHUTDOWN)?p->entry:0,(p->stage==LC_HANDOFF||p->stage==LC_PRE_SHUTDOWN)?p->dt:0};
 for(unsigned i=0;i<9;i++){vm_put32(out,fields[i]);out+=4;}
 vm_put64(out,c->config.target_first_sector);out+=8;
 vm_put64(out,p->stage==LC_READ?p->selected_first_sector:0);out+=8;
 vm_put64(out,p->stage==LC_READ?p->requested_offset:0);out+=8;
 vm_put64(out,p->stage==LC_READ?p->selected_offset:0);out+=8;
 lc_copy(out,c->config.prefix,32);out+=32;lc_copy(out,c->config.nonce,32);
 struct vm_record committed={0};
 int ret=vm_commit(&c->guarded,c->config.nonce,c->payload,LC_BYTES,c->scratch,&committed);
 if(ret||committed.sequence!=c->commits+2){c->stopped=1;return ret?ret:-4;}
 c->commits++;c->last_stage=p->stage;
 if(p->stage==LC_HANDOFF||p->stage==LC_PRE_SHUTDOWN)c->finished=1;
 return 0;
}
