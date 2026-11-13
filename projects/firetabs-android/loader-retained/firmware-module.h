#ifndef VALETHON_LOADER_FIRMWARE_MODULE_H
#define VALETHON_LOADER_FIRMWARE_MODULE_H
#include "module.h"
#include "physical.h"
struct lfw_state {struct lm_state module;struct lp_context storage;};
unsigned long lfw_state_bytes(void);
int lfw_start(struct lfw_state *,const struct lc_config *,const struct lp_plan *,const struct lp_ops *,const struct lh_service *,const struct lf_adapter *);
int lfw_emit(struct lfw_state *,const struct lc_point *);
#endif
