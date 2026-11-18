#ifndef VALETHON_LOADER_FRONTEND_H
#define VALETHON_LOADER_FRONTEND_H
#include "timed-module.h"
/* Diagnostic return codes only: no on-disk format, I/O or retry changes. */
enum lfo_error {
 LFO_INPUT=-101,LFO_DEVICE=-102,LFO_BLOCK=-103,LFO_REDIRECT=-104,
 LFO_HANDOFF_ARGUMENTS=-105,LFO_IDENTITY=-106,LFO_START=-107,
 LFO_MODE_COMMIT=-108,LFO_NOT_READY=-109,LFO_DEVICE_CHANGED=-110
};
struct lfo_descriptor {struct lc_config config;unsigned resident_read_entry;};
struct lfo_event {struct lc_point point;unsigned device;};
struct lfo_state {struct lft_state writer;unsigned attempted,ready,device,reads;};
unsigned long lfo_state_bytes(void);
int lfo_dispatch(struct lfo_state *,const struct lfo_descriptor *,const struct lfo_event *);
#endif
