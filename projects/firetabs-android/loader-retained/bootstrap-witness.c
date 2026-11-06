/* Analysis-only late observer with an independent LK screen witness.
 * No installer selects this profile. Display/stack/runtime safety still need
 * qualification; a modeled print is not physical logging evidence.
 */
#include "bridge.h"
#include "frontend.h"
extern const struct lb_plan lbo_load_plan;
extern const struct lfo_descriptor lbo_frontend;
extern int lh_equal(void *,const void *,unsigned,const unsigned char *);
extern int lb_cache_sync(void *,void *,unsigned);
extern int lbo_call(void *,void *,const void *,const unsigned *,void *);
struct witness_context {int (*compress)(unsigned *,const void *,unsigned);unsigned verified,device;};
static struct lb_result loaded;
static struct witness_context context={lh_block,1,0};
__attribute__((noinline)) static void witness(unsigned phase,unsigned value){
 unsigned status;__asm__ volatile("mrs %0,cpsr":"=r"(status));
 /* Fixed format: no reclaimed original format pointers and no arbitrary string.
  * Phase1 resident before app; 2 hook arrival; 3 non-normal mode;
  * 4 masked; 5 invalid device; 6 bridge result; 7 dispatcher result;
  * 8 already consumed (value is loaded flag).
  * The final word is CPSR, including the original I bit. */
 ((int (*)(const char *,...))0x4bd44b3d)("VREC %u %08x %08x\n",phase,value,status);
}
void lbo_arrival(void){witness(1,*(volatile unsigned *)0x4bd7c3a0);}
static int read_blob(void *opaque,unsigned long long address,void *out,unsigned count){
 struct witness_context *c=opaque;
 unsigned (*read)(void *,unsigned long long,void *,unsigned,unsigned)=(void *)0x4bd358e9;
 return read((void *)(unsigned long)c->device,address,out,count,8)==count?0:-1;
}
static const struct lb_io services={&context,read_blob,(void *)0x4bd45bb9,lh_equal,lb_cache_sync};
void lbo_observe(const unsigned *frame){
 unsigned status;__asm__ volatile("mrs %0,cpsr":"=r"(status));
 witness(2,frame[1]);
 unsigned mode=*(volatile unsigned *)0x4bd7c3a0;
 if(mode){witness(3,mode);return;}
 if(status&0x80){witness(4,status);return;}
 if(loaded.attempted){witness(8,loaded.loaded);return;}
 context.device=*(volatile unsigned *)0x4bd7e038;
 if(!context.device||(context.device&3)||context.device>0xffffffe7u){loaded.attempted=1;witness(5,context.device);return;}
 int result=lb_load(&loaded,&lbo_load_plan,&services);
 witness(6,(unsigned)result);
 if(result)return;
 result=lbo_call(loaded.start,loaded.state,&lbo_frontend,frame,loaded.stack_top);
 witness(7,(unsigned)result);
}
