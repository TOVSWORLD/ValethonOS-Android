/* Bounded RAM-only module load bridge. No boot image installation or arming. */
#ifndef VALETHON_LOADER_BRIDGE_H
#define VALETHON_LOADER_BRIDGE_H
struct lb_plan {
 unsigned code_bytes,state_bytes,stack_bytes,start_offset,emit_offset,bindings_verified;
 unsigned char sha256[32];
 unsigned long long target_first_sector,blob_offset;
};
struct lb_io {
 void *context;
 int (*read)(void *,unsigned long long,void *,unsigned);
 void *(*allocate)(unsigned,unsigned);
 int (*sha256_equal)(void *,const void *,unsigned,const unsigned char *);
 int (*cache_sync)(void *,void *,unsigned);
};
struct lb_result {unsigned attempted,loaded;void *code,*state,*stack_top,*start,*emit;unsigned allocation_bytes;};
int lb_load(struct lb_result *,const struct lb_plan *,const struct lb_io *);
#endif
