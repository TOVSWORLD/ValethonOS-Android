#ifndef VALETHON_LOADER_PHYSICAL_H
#define VALETHON_LOADER_PHYSICAL_H
#include "hash-stream.h"
struct lp_plan {void *device;unsigned long long first_sector;unsigned bytes,gpt_partition,mmc_partition,bindings_verified,buffer_owned;};
struct lp_ops {
 unsigned (*read)(void *,unsigned long long,void *,unsigned,unsigned);
 unsigned (*write)(void *,const void *,unsigned long long,unsigned,unsigned);
};
struct lp_context {unsigned initialized,stopped;struct lp_plan plan;struct lp_ops ops;struct lh_service hash;unsigned char *buffer;};
unsigned long lp_context_bytes(void);
int lp_init(struct lp_context *,const struct lp_plan *,const struct lp_ops *,const struct lh_service *,void *,unsigned);
int lp_read(void *,unsigned long,void *,unsigned long);
int lp_read_absolute(void *,unsigned long long,void *,unsigned);
int lp_write(void *,unsigned long,const void *,unsigned long);
int lp_prefix(void *,const unsigned char *);
void lp_pinned_ops(struct lp_ops *);
#endif
