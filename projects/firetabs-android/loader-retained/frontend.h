#ifndef VALETHON_LOADER_FRONTEND_H
#define VALETHON_LOADER_FRONTEND_H
#include "timed-module.h"
struct lfo_descriptor {struct lc_config config;unsigned resident_read_entry;};
struct lfo_event {struct lc_point point;unsigned device;};
struct lfo_state {struct lft_state writer;unsigned attempted,ready,device,reads;};
unsigned long lfo_state_bytes(void);
int lfo_dispatch(struct lfo_state *,const struct lfo_descriptor *,const struct lfo_event *);
#endif
