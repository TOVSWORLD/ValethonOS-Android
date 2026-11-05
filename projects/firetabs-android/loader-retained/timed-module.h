#ifndef VALETHON_LOADER_TIMED_MODULE_H
#define VALETHON_LOADER_TIMED_MODULE_H
#include "firmware-module.h"
#include "command.h"
#include "identity.h"
struct lft_plan {struct ld_plan command;unsigned cache_size_kib,cache_enabled;};
struct lft_state {struct lfw_state writer;struct ld_context command;unsigned started;};
unsigned long lft_state_bytes(void);
int lft_start(struct lft_state *,const struct lc_config *,const struct lp_plan *,const struct lp_ops *,const struct lh_service *,const struct lft_plan *);
int lft_start_bound(struct lft_state *,const struct lc_config *,const struct lp_plan *,const struct lp_ops *,const struct lh_service *,const struct lft_plan *,const struct li_plan *,const struct li_reader *);
int lft_emit(struct lft_state *,const struct lc_point *);
#endif
