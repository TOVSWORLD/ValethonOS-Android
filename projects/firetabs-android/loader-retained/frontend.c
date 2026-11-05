#include "frontend.h"
static int lfo_read(void *context,unsigned at,unsigned char *out,unsigned n){return li_memory_read(context,at,out,n);}
static int lfo_hash(unsigned *state,const void *input,unsigned blocks){return lh_block(state,input,blocks);}
static unsigned lfo_word(unsigned at){return *(volatile unsigned *)(unsigned long)at;}
unsigned long lfo_state_bytes(void){return sizeof(struct lfo_state);}
int lfo_dispatch(struct lfo_state *s,const struct lfo_descriptor *d,const struct lfo_event *e){
 if(!s||!d||!e)return -1;
 const struct lc_point *p=&e->point;
 if(p->mode)return 1;
 if(p->stage!=LC_READ&&p->stage!=LC_HANDOFF)return 1;
 if(!s->attempted){
  /* Initialize only from an actual redirected normal read. Recovery/fastboot
   * never allocate through this module or issue record/cache commands. */
  if(p->stage!=LC_READ)return 1;
  s->attempted=1;
  if(!e->device||(e->device&3)||e->device>0xffffffe7u||d->resident_read_entry!=0x4bcff009u||
     lfo_word(0x4bd7e038)!=e->device||lfo_word(e->device+16)!=d->resident_read_entry||lfo_word(e->device+20)!=0x4bd35a89u)return -1;
  unsigned block=lfo_word(e->device+8);
  if(!block||(block&3)||block>0xffffffebu||lfo_word(block+4)!=512)return -1;
  if(p->selected_first_sector!=d->config.target_first_sector||
     (p->requested_offset!=d->config.logical_boot_first_sector*512&&p->requested_offset!=d->config.logical_boot_first_sector*512+2048)||
     p->selected_offset!=d->config.target_first_sector*512+(p->requested_offset-d->config.logical_boot_first_sector*512))return -1;
  struct li_plan identity={e->device,0x4bd7e280,0x4bd7edf0,block};
  struct li_reader reader={&identity,lfo_read};struct li_binding binding;
  if(li_discover(&binding,e->device,block,&reader))return -1;
  struct lp_plan target={(void *)(unsigned long)e->device,d->config.target_first_sector,16*1024*1024,5,8,1,1};
  struct lp_ops ops;lp_pinned_ops(&ops);struct lh_service hash;hash.compress=lfo_hash;__asm__ volatile("" : "+r"(hash.compress));hash.verified=1;
  struct lft_plan timing={0};ld_pinned_services(&timing.command);timing.command.rca=binding.rca;timing.command.block_bytes=512;timing.command.verified=1;timing.cache_size_kib=binding.cache_size_kib;timing.cache_enabled=binding.cache_enabled;
  if(lft_start_bound(&s->writer,&d->config,&target,&ops,&hash,&timing,&identity,&reader))return -1;
  struct lc_point mode={0};mode.stage=LC_MODE;
  /* MODE means observed normal mode at first redirected read, not proof that
   * an earlier mode-hook executed or the kernel entered. */
  if(lft_emit(&s->writer,&mode))return -1;
  s->device=e->device;s->ready=1;
 }
 if(!s->ready)return -1;
 if(p->stage==LC_READ){
  if(e->device!=s->device){s->ready=0;return -1;}
  unsigned bit=p->kind==1?1:p->kind==2?2:0;
  if(!bit||(s->reads&bit))return 1;
  s->reads|=bit;
 }
 int rc=lft_emit(&s->writer,p);if(rc<0)s->ready=0;return rc;
}
