#ifndef VALETHON_LOADER_HASH_H
#define VALETHON_LOADER_HASH_H
struct lh_service {int (*compress)(unsigned *,const void *,unsigned);unsigned verified;};
int lh_equal(void *,const void *,unsigned,const unsigned char *);
int lh_block(unsigned *,const void *,unsigned);
#endif
