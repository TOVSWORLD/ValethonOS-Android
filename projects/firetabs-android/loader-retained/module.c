#include "module.h"
static int lm_read(void *p,unsigned long at,void *out,unsigned long n){struct lm_state *s=p;return s->physical.read(s->physical.context,at,out,n);}
static int lm_write(void *p,unsigned long at,const void *in,unsigned long n){struct lm_state *s=p;return s->physical.write(s->physical.context,at,in,n);}
static int lm_prefix(void *p,const unsigned char *expected){struct lm_state *s=p;return s->physical.prefix_sha256(s->physical.context,expected);}
static int lm_flush(void *p){struct lm_state *s=p;return lf_flush(&s->persistence);}
unsigned long lm_state_bytes(void){return sizeof(struct lm_state);}
int lm_start(struct lm_state *s,const struct lc_config *c,const struct vm_io *physical,const struct lf_adapter *adapter){
 if(!s)return -1;
 s->log.stopped=1;
 if(s->initialized)return -1;
 s->initialized=1;
 if(!c||!physical||!adapter)return -1;
 /* Caller provides a fresh zeroed exclusively owned state once per boot, never retries
  * initialization after a failed checkpoint. No device operation during setup. */
 if(!physical->read||!physical->write||!physical->prefix_sha256||adapter->stopped||
    !adapter->command||!adapter->now_ms||!adapter->bindings_verified||!adapter->clock_verified||
    !adapter->rca||adapter->rca>0xffffU||!adapter->cache_size_kib||adapter->cache_enabled!=1)return -1;
 s->physical=*physical;s->persistence=*adapter;
 struct vm_io guarded={s,lm_read,lm_write,lm_flush,lm_prefix};
 return lc_init(&s->log,c,&guarded);
}
int lm_emit(struct lm_state *s,const struct lc_point *p){return s&&s->initialized?lc_emit(&s->log,p):-1;}
