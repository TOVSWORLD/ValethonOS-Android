/* VM-only probe; actual filesystem operations, intercepted final UDC bind. */

#define _start unused_lab_start
#include "lab_init.c"
#undef _start
static void note(struct ft_acm_io *io,const char *p){unsigned long n=0;while(p[n])n++;lab_note(io,p,n);}
static void value(struct ft_acm_io *io,const char *name,long r){note(io,name);char out[]="+0000000000\n";out[0]=r<0?'-':'+';unsigned long v=r<0?0UL-(unsigned long)r:(unsigned long)r;for(int i=10;i>=1;i--){out[i]='0'+v%10;v/=10;}lab_note(io,out,sizeof(out)-1);}
static int vm_write(void *ctx,const char *path,const char *data,unsigned long n){
 if(ft_same(path,FT_ACM_ROOT "/UDC"))return 0; /* VM ONLY: never bind any UDC. */
 return ft_fs_write(ctx,path,data,n);
}
__attribute__((noreturn))void _start(void){
 struct ft_acm_io io={lab_call,0};struct vp_io vp={lab_call,0};struct vp_state state={0};
 int r=vp_bootstrap(&vp,lab_policy_blob,sizeof(lab_policy_blob),&state);if(r)goto idle;
 r=ll_label_archive(&io);if(r)goto idle;
 value(&io,"VM_LABELS=",r);
 value(&io,"VM_PROC=",ft_call(&io,40,(long)"proc",(long)"/proc",(long)"proc",15,0,0));
 value(&io,"VM_SYS=",ft_call(&io,40,(long)"sysfs",(long)"/sys",(long)"sysfs",15,0,0));
 value(&io,"VM_DOMAIN=",ll_enter_init(&io));
 long fd=ll_open_kmsg(&io);value(&io,"VM_KMSG_OPEN=",fd);if(fd>=0){char b[8192];long n=ft_call(&io,63,fd,(long)b,sizeof(b),0,0,0);value(&io,"VM_KMSG_READ=",n);ft_call(&io,57,fd,0,0,0,0,0);}
 long oldfd=ft_retry(&io,56,-100,(long)"/sys/class/udc",00200000|00400000);
 value(&io,"VM_GENERIC_FLAGS_OPEN=",oldfd);if(oldfd>=0)ft_call(&io,57,oldfd,0,0,0,0,0);
 fd=ft_retry(&io,56,-100,(long)"/sys/class/udc",FT_O_DIRECTORY|FT_O_NOFOLLOW|FT_O_CLOEXEC);value(&io,"VM_UDC_DIR=",fd);
 if(fd>=0){unsigned char b[2048];long n=ft_call(&io,61,fd,(long)b,sizeof(b),0,0,0);value(&io,"VM_UDC_DENTS_BYTES=",n);
  for(long p=0;p+20<n;){unsigned size=b[p+16]|((unsigned)b[p+17]<<8);value(&io,"VM_DENT_SIZE=",size);if(!size||p+size>n)break;char name[64];int i=0;while(i<63&&19+i<(int)size&&b[p+19+i]){name[i]=b[p+19+i];i++;}name[i]=0;note(&io,"VM_UDC_NAME=");note(&io,name);note(&io,"\n");p+=size;}
  ft_call(&io,57,fd,0,0,0,0,0);}
 value(&io,"VM_CONFIGFS=",ft_call(&io,40,(long)"configfs",(long)"/config",(long)"configfs",14,0,0));
 value(&io,"VM_NAMESPACE_BEFORE=",ll_usb_namespace(&io));
 {struct ft_acm_state gadget={0};struct ft_acm_ops ops={ft_fs_mkdir,vm_write,ft_fs_link,ft_fs_unlink,ft_fs_rmdir};
 r=ft_acm_setup(&ops,&io,&gadget,"vm-probe-only","0x1209","0x0001",1);value(&io,"VM_REAL_CONFIGFS_SETUP_WITHOUT_BIND=",r);
 value(&io,"VM_REAL_CONFIGFS_CLEANUP=",ft_acm_cleanup(&ops,&io,&gadget));}
 value(&io,"VM_NAMESPACE_AFTER=",ll_usb_namespace(&io));note(&io,"VM_FILESYSTEM_PROBE_DONE\n");
 idle:for(;;){long ts[2]={60,0};ft_call(&io,101,(long)ts,0,0,0,0,0);}
}
