#include "command.h"
#define LD_LIMIT 65536U
#define INT 0x0cU
#define CMD 0x34U
#define ARG 0x38U
#define STS 0x3cU
#define RESP 0x40U
#define COMMAND_EVENTS 0x700U
#define INTEN 0x10U
#define DMA_CFG 0x98U
static unsigned ld_read_pinned(void *unused,unsigned off){
 (void)unused;if(off!=INT&&off!=STS&&off!=RESP&&off!=INTEN&&off!=DMA_CFG)return ~0U;
 unsigned value=*(volatile unsigned *)(0x11230000UL+off);
 #if defined(__arm__)
 __asm__ volatile("dmb sy" ::: "memory");
 #endif
 return value;
}
static void ld_write_pinned(void *unused,unsigned off,unsigned value){
 (void)unused;if(off!=ARG&&off!=CMD&&off!=INT)return;
 if(off==INT&&(value&~COMMAND_EVENTS))return;
 *(volatile unsigned *)(0x11230000UL+off)=value;
 #if defined(__arm__)
 __asm__ volatile("dsb sy" ::: "memory");
 #endif
}
static unsigned ld_ticks_pinned(void *p){return lt_pinned_ticks(p);}
void ld_pinned_services(struct ld_plan *p){if(p){p->read=ld_read_pinned;p->write=ld_write_pinned;p->io=0;p->ticks=ld_ticks_pinned;p->timer=0;}}
unsigned long ld_context_bytes(void){return sizeof(struct ld_context);}
int ld_init(struct ld_context *c,const struct ld_plan *p){
 if(!c)return -1;c->stopped=1;if(c->initialized)return -1;c->initialized=1;
 if(!p||!p->read||!p->write||!p->ticks||!p->verified||!p->rca||p->rca>0xffffU||p->block_bytes!=512)return -1;
 c->plan=*p;
 if((p->read(p->io,INTEN)&COMMAND_EVENTS)||(p->read(p->io,DMA_CFG)&1U))return -1;
 if(lt_init(&c->clock,p->ticks,p->timer,p->verified))return -1;
 c->stopped=0;return 0;
}
static int ld_expired(struct ld_context *c,unsigned start,unsigned timeout){unsigned now=lt_now(c);return c->clock.failed||now-start>=timeout;}
int ld_command(void *opaque,struct lf_command *request){
 struct ld_context *c=opaque;if(!c||!c->initialized||c->stopped)return -1;
 if(!request||request->retries||!request->timeout_ms||request->timeout_ms>50)goto fail;
 if(!((request->opcode==6&&request->argument==0x03200101U&&request->response_type==8)||
      (request->opcode==13&&request->argument==c->plan.rca<<16&&request->response_type==1)))goto fail;
 if((c->plan.read(c->plan.io,INTEN)&COMMAND_EVENTS)||(c->plan.read(c->plan.io,DMA_CFG)&1U))goto fail;
 unsigned start=lt_now(c),ready=0,mask=request->opcode==13?2:1;
 if(c->clock.failed)goto fail;
 for(unsigned i=0;i<LD_LIMIT;i++){
  if(ld_expired(c,start,request->timeout_ms))goto fail;
  if(!(c->plan.read(c->plan.io,STS)&mask)){ready=1;break;}
 }
 if(!ready)goto fail;
 unsigned events=c->plan.read(c->plan.io,INT);
 /* No unrelated interrupt is acknowledged or hidden. Stale command errors
  * indicate an uncertain previous operation and stop before issuing anything. */
 if(events&~COMMAND_EVENTS||events&0x600U)goto fail;
 if(events)c->plan.write(c->plan.io,INT,events);
 if(c->plan.read(c->plan.io,INT)&COMMAND_EVENTS)goto fail;
 c->plan.write(c->plan.io,ARG,request->argument);
 /* Send R1 for CMD6 and poll completion with CMD13 in lf_flush. This avoids
  * pinned LK's unbounded R1b DAT0 loop; Linux MMC also has an R1 fallback. */
 c->plan.write(c->plan.io,CMD,(c->plan.block_bytes<<16)|0x80U|request->opcode);
 for(unsigned i=0;i<LD_LIMIT;i++){
  if(ld_expired(c,start,request->timeout_ms))goto fail;
  events=c->plan.read(c->plan.io,INT);
  if(events&~COMMAND_EVENTS)goto fail;
  if(events&COMMAND_EVENTS){
   c->plan.write(c->plan.io,INT,events&COMMAND_EVENTS);
   if(events&0x600U)goto fail;
   request->response[0]=c->plan.read(c->plan.io,RESP);
   if(ld_expired(c,start,request->timeout_ms))goto fail;
   if(request->opcode==13&&((request->response[0]>>9)&15U)==7U){
    unsigned pace=lt_now(c),progress=0;
    for(unsigned j=0;j<LD_LIMIT;j++){
     unsigned now=lt_now(c);
     if(c->clock.failed||now-start>=request->timeout_ms)goto fail;
     if(now-pace>=1U){progress=1;break;}
    }
    if(!progress)goto fail;
   }
   return 0;
  }
 }
 fail:c->stopped=1;return -2;
}
