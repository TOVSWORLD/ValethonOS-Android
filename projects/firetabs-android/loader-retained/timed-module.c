#include "timed-module.h"
static int lft_command(void *context,struct lf_command *cmd){return ld_command(context,cmd);}
static unsigned lft_clock(void *context){return lt_now(context);}
unsigned long lft_state_bytes(void){return sizeof(struct lft_state);}
int lft_start(struct lft_state *s,const struct lc_config *config,const struct lp_plan *plan,const struct lp_ops *ops,const struct lh_service *hash,const struct lft_plan *services){
 if(!s)return -1;s->writer.module.log.stopped=1;
 if(s->started){s->command.stopped=1;return -1;}s->started=1;
 if(!services||!services->cache_size_kib||services->cache_enabled>1||ld_init(&s->command,&services->command))return -1;
 struct lf_adapter card={&s->command,lft_command,lft_clock,services->command.rca,services->cache_size_kib,services->cache_enabled,services->command.verified,services->command.verified,0};
 return lfw_start(&s->writer,config,plan,ops,hash,&card);
}
int lft_emit(struct lft_state *s,const struct lc_point *point){
 if(!s||!s->started||s->command.stopped||s->command.clock.failed)return -1;
 return lfw_emit(&s->writer,point);
}

/* This entry checks selected cached identity before any timer/controller/storage
 * callbacks. Getter/pointer provenance still belongs to the reviewed frontend. */
int lft_start_bound(struct lft_state *s,const struct lc_config *config,const struct lp_plan *plan,const struct lp_ops *ops,const struct lh_service *hash,const struct lft_plan *services,const struct li_plan *identity,const struct li_reader *reader){
 if(!s)return -1;
 if(s->started){s->writer.module.log.stopped=1;s->command.stopped=1;return -1;}
 struct li_binding b;
 if(!plan||!services||li_capture(&b,identity,reader)||(unsigned long)plan->device!=b.device||services->command.rca!=b.rca||services->cache_size_kib!=b.cache_size_kib||services->cache_enabled!=b.cache_enabled){
  s->started=1;s->writer.module.log.stopped=1;s->command.stopped=1;return -1;
 }
 return lft_start(s,config,plan,ops,hash,services);
}
