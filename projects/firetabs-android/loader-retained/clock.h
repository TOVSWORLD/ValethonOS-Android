#ifndef VALETHON_LOADER_CLOCK_H
#define VALETHON_LOADER_CLOCK_H
struct lt_clock {unsigned (*ticks)(void *);void *context;unsigned last,remainder,milliseconds,initialized,failed;};
int lt_init(struct lt_clock *,unsigned (*)(void *),void *,unsigned);
unsigned lt_now(void *);
unsigned lt_pinned_ticks(void *);
#endif
