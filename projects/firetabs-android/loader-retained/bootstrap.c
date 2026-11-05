#include "bridge.h"
#include "frontend.h"
extern const struct lb_plan lbo_load_plan;
extern const struct lfo_descriptor lbo_frontend;
extern int lh_equal(void *,const void *,unsigned,const unsigned char *);
extern int lb_cache_sync(void *,void *,unsigned);
extern int lbo_call(void *,void *,const void *,const unsigned *,void *);
struct lbo_context {int (*compress)(unsigned *,const void *,unsigned);unsigned verified,device;};
static struct lb_result loaded;
static struct lbo_context context={lh_block,1,0};
static int read_blob(void *opaque,unsigned long long address,void *out,unsigned count){
 struct lbo_context *c=opaque;
 unsigned (*read)(void *,unsigned long long,void *,unsigned,unsigned)=(void *)0x4bd358e9;
 return read((void *)(unsigned long)c->device,address,out,count,8)==count?0:-1;
}
static const struct lb_io services={&context,read_blob,(void *)0x4bd45bb9,lh_equal,lb_cache_sync};
void lbo_observe(const unsigned *frame){
 if(*(volatile unsigned *)0x4bd7c3a0)return;
 unsigned status;__asm__ volatile("mrs %0,cpsr":"=r"(status));
 if(status&0x80){loaded.attempted=1;return;}
 if(!loaded.attempted){
  if(frame[1]!=LC_READ||frame[11]!=8)return;
  unsigned long long request=(unsigned long long)frame[6]|((unsigned long long)frame[7]<<32),boot=lbo_frontend.config.logical_boot_first_sector*512;
  if(request!=boot&&request!=boot+2048)return;
  context.device=frame[8];
  if(lb_load(&loaded,&lbo_load_plan,&services))return;
 }
 if(loaded.loaded)lbo_call(loaded.start,loaded.state,&lbo_frontend,frame,loaded.stack_top);
}
