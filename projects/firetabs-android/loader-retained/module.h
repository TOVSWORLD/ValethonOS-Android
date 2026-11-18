#ifndef VALETHON_LOADER_MODULE_H
#define VALETHON_LOADER_MODULE_H
#include "checkpoint.h"
#include "mmc_flush.h"
struct lm_state {unsigned initialized;struct lc_context log;struct lf_adapter persistence;struct vm_io physical;};
unsigned long lm_state_bytes(void);
int lm_start(struct lm_state *,const struct lc_config *,const struct vm_io *,const struct lf_adapter *);
int lm_emit(struct lm_state *,const struct lc_point *);
#endif
