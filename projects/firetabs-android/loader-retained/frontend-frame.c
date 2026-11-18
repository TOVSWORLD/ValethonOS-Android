#include "frontend.h"
/* Hook frame: APSR, checkpoint kind, r0..r12, return LR; native SP is frame+64. */
int lfo_frame_dispatch(struct lfo_state *state,const struct lfo_descriptor *desc,const unsigned *frame){
 struct lfo_event event={0};event.point.mode=*(volatile unsigned *)0x4bd7c3a0;
 if(event.point.mode)return 1;
 unsigned kind=frame[1];
 if(kind==LC_READ){
  unsigned long long request=(unsigned long long)frame[6]|((unsigned long long)frame[7]<<32);
  unsigned long long logical=desc->config.logical_boot_first_sector*512;
  if(request!=logical&&request!=logical+2048)return 1;
  if(frame[11]!=8)return 1;
  event.point.stage=LC_READ;event.point.kind=request==logical?1:2;
  event.point.read_bytes=frame[10];event.point.destination=frame[9];
  event.point.requested_offset=request;
  const unsigned *native=frame+16;
  event.point.selected_offset=(unsigned long long)native[4]|((unsigned long long)native[5]<<32);
  event.point.selected_first_sector=desc->config.target_first_sector;
  event.device=frame[8];
 }else if(kind==LC_HANDOFF){event.point.stage=LC_HANDOFF;event.point.entry=frame[2];event.point.dt=frame[3];}
 else if(kind==LC_PRE_SHUTDOWN){event.point.stage=LC_PRE_SHUTDOWN;event.point.entry=frame[13];event.point.dt=frame[18];event.device=*(volatile unsigned *)0x4bd7e038;}
 else return 1;
 return lfo_dispatch(state,desc,&event);
}
