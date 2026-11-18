/* Explicit labels for the three immutable archive objects only. Enforcing policy
 * remains active; no forced contexts, arbitrary paths, or MAC_ADMIN capability. */
#ifndef VALETHON_LAB_LABELS_H
#define VALETHON_LAB_LABELS_H
#include "acm_serial.h"
#define LL_NR_LSETXATTR 6
#define LL_NR_LGETXATTR 9
#define LL_O_PATH 010000000
static inline int ll_context_equal(const unsigned char *raw,long n,const char *context) {
 unsigned long size=0;while(context[size])size++;
 if(n!=(long)size&&n!=(long)(size+1))return 0;
 if(n==(long)(size+1)&&raw[size])return 0;
 for(unsigned long i=0;i<size;i++)if(raw[i]!=(unsigned char)context[i])return 0;
 return 1;
}
static inline int ll_label_archive(struct ft_acm_io *io) {
 static const char * const paths[]={"/dev","/dev/console","/dev/kmsg"};
 static const char * const contexts[]={"system_u:object_r:dev_dir_t","system_u:object_r:console_t","system_u:object_r:kmsg_t"};
 for(int i=0;i<3;i++) {
  long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)paths[i],LL_O_PATH|FT_O_NOFOLLOW|FT_O_CLOEXEC);
  if(fd<0)return (int)fd;
  unsigned long long aligned[32]={0};unsigned char *st=(unsigned char *)aligned;
  long r=ft_call(io,FT_SERIAL_STATX,fd,(long)"",FT_SERIAL_AT_EMPTY_PATH,FT_SERIAL_STATX_TYPE,(long)st,0);
  unsigned int mode=(unsigned int)st[28]|((unsigned int)st[29]<<8);
  if(r>=0&&(!(ft_serial_u32(st)&FT_SERIAL_STATX_TYPE)||
      (mode&FT_SERIAL_IFMT)!=(i?FT_SERIAL_IFCHR:0040000)||
      (i&&(ft_serial_u32(st+128)!=(i==1?5U:1U)||ft_serial_u32(st+132)!=(i==1?1U:11U)))))r=-19;
  long closed=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);
  if(r<0)return (int)r;
  if(closed<0)return (int)closed;
  unsigned char value[128]={0};
  r=ft_call(io,LL_NR_LGETXATTR,(long)paths[i],(long)"security.selinux",(long)value,sizeof(value),0,0);
  if(r<0)return (int)r;
  if(!ll_context_equal(value,r,contexts[i])) {
   unsigned long size=0;while(contexts[i][size])size++;
   r=ft_call(io,LL_NR_LSETXATTR,(long)paths[i],(long)"security.selinux",(long)contexts[i],size+1,0,0);
   if(r)return (int)r;
   r=ft_call(io,LL_NR_LGETXATTR,(long)paths[i],(long)"security.selinux",(long)value,sizeof(value),0,0);
   if(r<0)return (int)r;
   if(!ll_context_equal(value,r,contexts[i]))return -13;
  }
 }
 return 0;
}
/* Configfs has a uniform filesystem label in the pinned kernel. Only the USB
 * subsystem may exist, and no preexisting gadget may be adopted. No mutation. */
static inline int ll_exact_children(struct ft_acm_io *io,const char *path,const char *only) {
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)path,FT_O_DIRECTORY|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd<0)return (int)fd;
 int seen=0,result=-75,ended=0;
 for(int chunk=0;chunk<8;chunk++) {
  unsigned char b[2048];long n=ft_retry(io,FT_NR_GETDENTS64,fd,(long)b,sizeof(b));
  if(n<0){result=(int)n;break;}
  if(n>(long)sizeof(b)){result=-5;break;}
  if(!n){ended=1;result=(only&&seen!=1)?-19:0;break;}
  unsigned long p=0;result=0;
  while(p<(unsigned long)n) {
   if((unsigned long)n-p<20){result=-22;break;}
   unsigned int size=b[p+16]|((unsigned int)b[p+17]<<8);
   if(size<24||size%8||size>(unsigned long)n-p){result=-22;break;}
   unsigned long len=0;while(len<size-19&&b[p+19+len])len++;
   if(len==size-19||len>63){result=-22;break;}
   char name[64];for(unsigned long j=0;j<len;j++)name[j]=(char)b[p+19+j];name[len]=0;
   if(!ft_same(name,".")&&!ft_same(name,"..")) {
    if(!only||!ft_same(name,only)||seen++){result=-17;break;}
   }
   p+=size;
  }
  if(result)break;
 }
 long closed=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);
 return result?result:!ended?-75:closed<0?(int)closed:0;
}
static inline int ll_usb_namespace(struct ft_acm_io *io) {
 int r=ll_exact_children(io,"/config","usb_gadget");
 return r?r:ll_exact_children(io,"/config/usb_gadget",0);
}
#endif
