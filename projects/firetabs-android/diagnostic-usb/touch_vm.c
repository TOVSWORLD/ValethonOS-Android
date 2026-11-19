/* VM-only policy checks. No real input device or tablet pass is claimed. */
#define _start unused_touch_start
#include "touch_init.c"
#undef _start
static void note(struct ft_acm_io *io,const char *p){unsigned long n=0;while(p[n])n++;lab_note(io,p,n);}
static void value(struct ft_acm_io *io,const char *name,long r){
 note(io,name);char out[]="+0000000000\n";out[0]=r<0?'-':'+';unsigned long v=r<0?0UL-(unsigned long)r:(unsigned long)r;
 for(int i=10;i>=1;i--){out[i]=(char)('0'+v%10);v/=10;}lab_note(io,out,sizeof(out)-1);
}
__attribute__((noreturn))void _start(void){
 struct ft_acm_io io={lab_call,0};struct vp_io vp={lab_call,0};struct vp_state state={0};
 long r=vp_bootstrap(&vp,lab_policy_blob,sizeof(lab_policy_blob),&state);
 if(r)goto idle;
 value(&io,"VM_TOUCH_LABELS=",touch_label_archive(&io));
 value(&io,"VM_TOUCH_DOMAIN=",ll_enter_init(&io));
 value(&io,"VM_TOUCH_ENFORCE=",vp_enforcing(&vp));
 /* virt exposes a virtual input device. Check a real read-only evdev fd,
  * without claiming a Goodix device or injecting input events. */
 r=ft_retry(&io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/input/event0",FT_SERIAL_NONBLOCK|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 value(&io,"VM_TOUCH_READ_OPEN=",r);
 if(r>=0){long fd=r;struct tp_event event;
  value(&io,"VM_TOUCH_READ_IDLE=",ft_call(&io,FT_NR_READ,fd,(long)&event,sizeof(event),0,0,0));
  unsigned int version=0;
  value(&io,"VM_TOUCH_IOCTL_DENIED=",ft_call(&io,29,fd,0x80044501,(long)&version,0,0,0));
  ft_call(&io,FT_NR_CLOSE,fd,0,0,0,0,0);
 }
 r=ft_retry(&io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/input/event0",FT_O_WRONLY|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 value(&io,"VM_TOUCH_WRITE_DENIED=",r);
 if(r>=0)ft_call(&io,FT_NR_CLOSE,r,0,0,0,0,0);
 {const char label[]="system_u:object_r:input_dev_t";
  value(&io,"VM_TOUCH_RELABEL_DENIED=",ft_call(&io,LL_NR_LSETXATTR,(long)"/dev/input/event0",(long)"security.selinux",(long)label,sizeof(label),0,0));}
 note(&io,"VM_TOUCH_PROBE_DONE\n");
idle:
 for(;;){const long ts[2]={1,0};ft_call(&io,FT_SERIAL_NANOSLEEP,(long)ts,0,0,0,0,0);}
}
