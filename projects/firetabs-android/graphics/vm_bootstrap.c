/* SPDX-License-Identifier: GPL-2.0-only
 * Execute the actual labels/domain/graphics exec in a generic VM, without USB.
 */
#define _start unused_graphics_start
#include "bootstrap.c"
#undef _start
__attribute__((noreturn))void _start(void){
 struct ft_acm_io io={lab_call,0};struct vp_io vp={lab_call,0};struct vp_state state={0};
 int r=vp_bootstrap(&vp,lab_policy_blob,sizeof(lab_policy_blob),&state);
 if(!r)r=graphics_labels(&io);if(!r)r=ll_enter_init(&io);
 if(!r){struct ll_context ctx={&io,-1,-1,0,0};graphics_exec(&ctx);}
 for(;;){const long wait[2]={1,0};ft_call(&io,FT_SERIAL_NANOSLEEP,(long)wait,0,0,0,0,0);}
}
