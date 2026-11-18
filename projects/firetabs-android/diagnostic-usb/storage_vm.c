/* VM ONLY. Synthetic virtio disk; never admitted by the physical bundle.
 * Replaces archive block nodes BEFORE policy load. Production PID1 is separate.
 */
#define _start unused_storage_start
#include "storage_init.c"
#undef _start
static void note(struct ft_acm_io *io,const char *p){unsigned long n=0;while(p[n])n++;lab_note(io,p,n);}
static void value(struct ft_acm_io *io,const char *name,long r){
 note(io,name);char out[]="+0000000000\n";out[0]=r<0?'-':'+';unsigned long v=r<0?0UL-(unsigned long)r:(unsigned long)r;
 for(int i=10;i>=1;i--){out[i]=(char)('0'+v%10);v/=10;}lab_note(io,out,sizeof(out)-1);
}
static int vm_dev(struct ft_acm_io *io,unsigned *major,unsigned *minor){
 char b[32]={0};long n=ft_read_file(io,"/sys/class/block/vda/dev",b,31);if(n<0)return (int)n;
 unsigned a=0,z=0;long at=0;
 while(at<n&&b[at]>='0'&&b[at]<='9'){a=a*10+(unsigned)(b[at++]-'0');if(a>4095)return -22;}
 if(at==0||at>=n||b[at++]!=':')return -22;
 long first=at;
 while(at<n&&b[at]>='0'&&b[at]<='9'){z=z*10+(unsigned)(b[at++]-'0');if(z>1048575)return -22;}
 if(at==first||at+1!=n||b[at]!='\n')return -22;
 *major=a;*minor=z;return 0;
}
__attribute__((noreturn))void _start(void){
 struct ft_acm_io io={lab_call,0};long fd=-1;unsigned major=0,minor=0;
 /* Kernel virtual files only; no policy/enforcement toggle. */
 long r=ft_call(&io,VP_NR_MOUNT,(long)"sysfs",(long)"/sys",(long)"sysfs",15,0,0);
 if(r)goto idle;
 for(int i=0;i<500;i++){
  r=vm_dev(&io,&major,&minor);if(r!=-2)break;
  const long ts[2]={0,10000000};ft_call(&io,FT_SERIAL_NANOSLEEP,(long)ts,0,0,0,0,0);
 }
 if(r)goto idle;
 {unsigned long dev=(minor&255U)|((unsigned long)major<<8)|((unsigned long)(minor&~255U)<<12);
  /* This archive contains no block nodes; create exactly two synthetic aliases. */
  r=ft_call(&io,FT_SERIAL_MKNODAT,FT_AT_FDCWD,(long)"/dev/firetabs-boot",0060400,dev,0,0);if(r)goto idle;
  r=ft_call(&io,FT_SERIAL_MKNODAT,FT_AT_FDCWD,(long)"/dev/other-block",0060400,dev,0,0);if(r)goto idle;
 }
 {struct vp_io vp={lab_call,0};struct vp_state state={0};r=vp_bootstrap(&vp,lab_policy_blob,sizeof(lab_policy_blob),&state);if(r)goto idle;}
 r=ll_label_archive(&io);if(r)goto idle;
 {const char context[]="system_u:object_r:boot_block_t";unsigned char b[128]={0};
  r=ft_call(&io,LL_NR_LSETXATTR,(long)"/dev/firetabs-boot",(long)"security.selinux",(long)context,sizeof(context),0,0);if(r)goto idle;
  r=ft_call(&io,LL_NR_LGETXATTR,(long)"/dev/firetabs-boot",(long)"security.selinux",(long)b,sizeof(b),0,0);
  if(r<0||!ll_context_equal(b,r,context))goto idle;
 }
 value(&io,"VM_STORAGE_DOMAIN=",ll_enter_init(&io));
 value(&io,"VM_STORAGE_ENFORCE=",ft_read_file(&io,"/security/enforce",(char[4]){0},4));
 fd=ft_retry(&io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/firetabs-boot",FT_O_NOFOLLOW|FT_O_CLOEXEC);
 value(&io,"VM_STORAGE_READ_OPEN=",fd);if(fd<0)goto idle;
 {long memory=ft_call(&io,222,0,FS_BOOT_BYTES,3,0x22,-1,0);if(memory<0)goto idle;
  unsigned long used=0;int failed=0;
  for(int i=0;i<4096&&used<FS_BOOT_BYTES;i++){
   unsigned long want=FS_BOOT_BYTES-used;if(want>65536)want=65536;
   long n=ft_retry(&io,FT_NR_READ,fd,memory+(long)used,want);
   if(n<=0||n>(long)want){failed=1;break;}used+=(unsigned long)n;
  }
  value(&io,"VM_STORAGE_READ_BYTES=",(long)used);
  unsigned char extra;value(&io,"VM_STORAGE_EOF=",ft_retry(&io,FT_NR_READ,fd,(long)&extra,1));
  if(failed||used!=FS_BOOT_BYTES)goto idle;
  /* VM-only deterministic all-0x5a fixture expected hash. */
  static const unsigned char hash[32]=VM_STORAGE_EXPECTED_HASH;
  value(&io,"VM_STORAGE_HASH=",combined_verify((unsigned char *)memory,used,hash));
  ((unsigned char *)memory)[0]^=1;
  value(&io,"VM_STORAGE_BAD_HASH=",combined_verify((unsigned char *)memory,used,hash));
  value(&io,"VM_STORAGE_IOCTL_DENIED=",ft_call(&io,FT_SERIAL_IOCTL,fd,0x80081272,(long)&used,0,0,0));
  value(&io,"VM_STORAGE_READ_FD_WRITE_DENIED=",ft_call(&io,FT_NR_WRITE,fd,memory,1,0,0,0));
  ft_call(&io,215,memory,FS_BOOT_BYTES,0,0,0,0);
 }
 ft_call(&io,FT_NR_CLOSE,fd,0,0,0,0,0);fd=-1;
 value(&io,"VM_STORAGE_WRITE_OPEN_DENIED=",ft_retry(&io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/firetabs-boot",FT_O_WRONLY|FT_O_NOFOLLOW|FT_O_CLOEXEC));
 value(&io,"VM_STORAGE_OTHER_READ_DENIED=",ft_retry(&io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/other-block",FT_O_NOFOLLOW|FT_O_CLOEXEC));
 value(&io,"VM_STORAGE_MKNOD_DENIED=",ft_call(&io,FT_SERIAL_MKNODAT,FT_AT_FDCWD,(long)"/dev/unapproved-block",0060400,0,0,0));
 note(&io,"VM_STORAGE_PROBE_DONE\n");
idle:
 if(fd>=0)ft_call(&io,FT_NR_CLOSE,fd,0,0,0,0,0);
 for(;;){const long ts[2]={60,0};ft_call(&io,FT_SERIAL_NANOSLEEP,(long)ts,0,0,0,0,0);}
}
