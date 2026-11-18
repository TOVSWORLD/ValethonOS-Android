#include "firmware-module.h"
static int lfw_read(void *c,unsigned long at,void *out,unsigned long n){return lp_read(c,at,out,n);}
static int lfw_write(void *c,unsigned long at,const void *in,unsigned long n){return lp_write(c,at,in,n);}
static int lfw_prefix(void *c,const unsigned char *expected){return lp_prefix(c,expected);}
unsigned long lfw_state_bytes(void){return sizeof(struct lfw_state);}
int lfw_start(struct lfw_state *s,const struct lc_config *config,const struct lp_plan *plan,const struct lp_ops *ops,const struct lh_service *hash,const struct lf_adapter *card){
 if(!s)return -1;
 s->module.log.stopped=1;
 if(!config||!plan||config->target_first_sector!=plan->first_sector||config->partition_bytes!=plan->bytes||
    config->gpt_partition!=plan->gpt_partition||config->mmc_partition!=plan->mmc_partition){s->storage.stopped=1;return -1;}
 /* Reuse only the writer's padded output block for prefix/short-read scratch.
  * Codec headers and the seed's expected digest live in its separate scratch. */
 if(lp_init(&s->storage,plan,ops,hash,s->module.log.block,4096))return -1;
 struct vm_io physical={&s->storage,lfw_read,lfw_write,0,lfw_prefix};
 return lm_start(&s->module,config,&physical,card);
}
int lfw_emit(struct lfw_state *s,const struct lc_point *point){
 if(!s||!s->module.initialized||s->storage.stopped)return -1;
 return lm_emit(&s->module,point);
}
