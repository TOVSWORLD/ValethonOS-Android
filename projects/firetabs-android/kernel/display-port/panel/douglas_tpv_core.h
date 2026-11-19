/* SPDX-License-Identifier: GPL-2.0-only */
/* Source-backed TPV prepare/disable sequencing; callbacks own all kernel I/O. */
#ifndef DOUGLAS_TPV_CORE_H
#define DOUGLAS_TPV_CORE_H
#include "douglas_tpv_sequence.h"
struct douglas_tpv_io {
 int (*supply)(void *,int);
 void (*power)(void *,int);
 void (*reset)(void *,int); /* Logical assertion: true drives physical reset low. */
 void (*delay)(void *,unsigned int);
 int (*lanes_ready)(void *);
 int (*lanes_down)(void *);
 long (*write)(void *,const unsigned char *,unsigned int);
 void *ctx;
};
struct douglas_tpv_state { int rail_owned,lanes_owned,active,fault; };
static inline int douglas_tpv_unprepare(struct douglas_tpv_state *s,const struct douglas_tpv_io *io)
{
 int ret;
 if (!s->rail_owned)
  return 0;
 io->reset(io->ctx,1);
 if(s->lanes_owned) {
  ret=io->lanes_down(io->ctx);
  if(ret) { s->fault=1;s->active=0;return ret; }
  s->lanes_owned=0;
 }
 io->delay(io->ctx,15);
 io->power(io->ctx,0);
 io->delay(io->ctx,5);
 ret=io->supply(io->ctx,0);
 io->delay(io->ctx,10);
 s->active=0;
 if(ret) { s->fault=1;return ret; }
 s->rail_owned=0;
 return 0;
}
static inline void douglas_tpv_disable(struct douglas_tpv_state *s,const struct douglas_tpv_io *io)
{
 if (!s->active)
  return;
 /* Working TPV suspend asserts reset instead of sending display-off/sleep-in. */
 io->reset(io->ctx,1);
 io->delay(io->ctx,120);
 s->active=0;
}
static inline int douglas_tpv_prepare(struct douglas_tpv_state *s,const struct douglas_tpv_io *io)
{
 unsigned long i;int ret;
 if(s->fault)return -5;
 if(s->active)return 0;
 if(s->rail_owned)return -16;
 ret=io->supply(io->ctx,1);
 if(ret)return ret;
 s->rail_owned=1;
 io->delay(io->ctx,6);
 io->power(io->ctx,1);
 io->delay(io->ctx,30);
 ret=io->lanes_ready(io->ctx);
 if(ret)goto failed;
 s->lanes_owned=1;
 io->delay(io->ctx,10);
 io->reset(io->ctx,0);
 io->delay(io->ctx,10);
 io->reset(io->ctx,1);
 io->delay(io->ctx,10);
 io->reset(io->ctx,0);
 io->delay(io->ctx,20);
 for(i=0;i<sizeof(douglas_tpv_sequence)/sizeof(douglas_tpv_sequence[0]);i++) {
  const struct douglas_tpv_command *step=&douglas_tpv_sequence[i];long written;
  if(!step->type) { io->delay(io->ctx,step->delay_ms);continue; }
  if((step->type==0x05&&step->length!=1)||(step->type==0x15&&step->length!=2)||
     (step->type==0x39&&step->length<=2)||!step->length||step->length>sizeof(step->data)) {
   ret=-22;goto failed;
  }
  written=io->write(io->ctx,step->data,step->length);
  if(written!=(long)step->length) { ret=written<0?(int)written:-5;goto failed; }
 }
 s->active=1;
 return 0;
failed:
 /* Preserve primary command error; uncertain regulator cleanup latches fault. */
 (void)douglas_tpv_unprepare(s,io);
 return ret;
}
#endif
