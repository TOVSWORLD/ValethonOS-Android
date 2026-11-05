#ifndef VALETHON_LOADER_COMMAND_H
#define VALETHON_LOADER_COMMAND_H
#include "clock.h"
#include "mmc_flush.h"
struct ld_plan {unsigned (*read)(void *,unsigned);void (*write)(void *,unsigned,unsigned);void *io;unsigned (*ticks)(void *);void *timer;unsigned rca,block_bytes,verified;};
/* clock first: lt_now and ld_command share the same immutable adapter context. */
struct ld_context {struct lt_clock clock;struct ld_plan plan;unsigned initialized,stopped;};
unsigned long ld_context_bytes(void);
int ld_init(struct ld_context *,const struct ld_plan *);
int ld_command(void *,struct lf_command *);
void ld_pinned_services(struct ld_plan *);
#endif
