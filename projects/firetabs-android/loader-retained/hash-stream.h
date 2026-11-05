#ifndef VALETHON_LOADER_HASH_STREAM_H
#define VALETHON_LOADER_HASH_STREAM_H
#include "hash.h"
struct lhs_state {unsigned words[8],bytes,active,failed;int (*compress)(unsigned *,const void *,unsigned);};
int lhs_init(struct lhs_state *,const struct lh_service *);
int lhs_add(struct lhs_state *,const void *,unsigned);
int lhs_finish(struct lhs_state *,const unsigned char *);
#endif
