#include "clock.h"
/* Pinned LK's bounded three-read GPT4 sampler. Its microsecond delay helper
 * multiplies by13; this profile pins13MHz, without configuring the timer. */
unsigned lt_pinned_ticks(void *unused){(void)unused;unsigned (*read)(void)=(void*)0x4bd25dfd;return read();}
int lt_init(struct lt_clock *c,unsigned (*reader)(void *),void *context,unsigned verified){
 if(!c)return -1;c->failed=1;c->initialized=0;
 if(!reader||!verified)return -1;
 unsigned first=reader(context),next=first;
 for(unsigned i=0;i<32&&next==first;i++)next=reader(context);
 if(next==first||next-first>=0x80000000U)return -1;
 c->ticks=reader;c->context=context;c->last=next;c->remainder=0;c->milliseconds=0;c->initialized=1;c->failed=0;return 0;
}
unsigned lt_now(void *opaque){
 struct lt_clock *c=opaque;if(!c||!c->initialized||c->failed)return c?c->milliseconds:0;
 unsigned next=c->ticks(c->context),delta=next-c->last;
 if(delta>=0x80000000U){c->failed=1;return c->milliseconds;}
 c->last=next;c->milliseconds+=delta/13000U;
 unsigned remainder=c->remainder+delta%13000U;
 c->milliseconds+=remainder/13000U;c->remainder=remainder%13000U;return c->milliseconds;
}
