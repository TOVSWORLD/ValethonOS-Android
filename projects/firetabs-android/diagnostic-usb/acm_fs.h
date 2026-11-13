/* Linux/AArch64 callback adapters; host tests execute only RAM-backed fake syscalls. */
#ifndef FIRETABS_ACM_FS_H
#define FIRETABS_ACM_FS_H
#if !defined(__aarch64__) && !defined(FT_ACM_HOST_TEST)
#error "Linux AArch64 ABI or explicit RAM-only test required"
#endif
#if !defined(__BYTE_ORDER__) || __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "Little-endian dirent ABI required"
#endif
_Static_assert(sizeof(long)==8 && sizeof(void *)==8,"64-bit syscall argument ABI required");
#include "acm_setup.h"
#define FT_NR_MKDIRAT 34
#define FT_NR_UNLINKAT 35
#define FT_NR_SYMLINKAT 36
#define FT_NR_OPENAT 56
#define FT_NR_CLOSE 57
#define FT_NR_GETDENTS64 61
#define FT_NR_READ 63
#define FT_NR_WRITE 64
#define FT_AT_FDCWD -100
#define FT_AT_REMOVEDIR 0x200
/* ARM64 fcntl overrides are pinned and checked before generic fallbacks. */
#define FT_O_WRONLY 1
#define FT_O_DIRECTORY 0040000
#define FT_O_NOFOLLOW 0100000
#define FT_O_CLOEXEC 02000000
struct ft_acm_io {long (*call)(void *,long,long,long,long,long,long,long);void *ctx;};
static int ft_same(const char *a,const char *b) {
 unsigned long i=0;while(a[i]&&b[i]&&a[i]==b[i])i++;return a[i]==b[i];
}
static long ft_call(struct ft_acm_io *io,long nr,long a,long b,long c,long d,long e,long f) {
 return io->call(io->ctx,nr,a,b,c,d,e,f);
}
static long ft_retry(struct ft_acm_io *io,long nr,long a,long b,long c) {
 long r=-4;for(int tries=0;tries<8&&r==-4;tries++)r=ft_call(io,nr,a,b,c,0,0,0);return r;
}
static int ft_resource(const char *path) {
 static const char * const names[]={FT_ACM_ROOT,FT_ACM_ROOT "/strings/0x409",FT_ACM_ROOT "/configs/c.1",FT_ACM_ROOT "/configs/c.1/strings/0x409",FT_ACM_ROOT "/functions/acm.usb0",FT_ACM_ROOT "/configs/c.1/acm.usb0"};
 for(int i=0;i<6;i++)if(ft_same(path,names[i]))return i;
 return -1;
}
static int ft_write_path(const char *path) {
 static const char * const names[]={FT_ACM_ROOT "/idVendor",FT_ACM_ROOT "/idProduct",FT_ACM_ROOT "/strings/0x409/manufacturer",FT_ACM_ROOT "/strings/0x409/product",FT_ACM_ROOT "/configs/c.1/strings/0x409/configuration",FT_ACM_ROOT "/UDC"};
 for(int i=0;i<6;i++)if(ft_same(path,names[i]))return 1;
 return 0;
}
static int ft_fs_mkdir(void *ctx,const char *path) {
 struct ft_acm_io *io=ctx;int i=ft_resource(path);if(i<0||i>4)return -22;
 return (int)ft_call(io,FT_NR_MKDIRAT,FT_AT_FDCWD,(long)path,0700,0,0,0);
}
static int ft_fs_unlink(void *ctx,const char *path) {
 struct ft_acm_io *io=ctx;if(ft_resource(path)!=5)return -22;
 return (int)ft_call(io,FT_NR_UNLINKAT,FT_AT_FDCWD,(long)path,0,0,0,0);
}
static int ft_fs_rmdir(void *ctx,const char *path) {
 struct ft_acm_io *io=ctx;int i=ft_resource(path);if(i<0||i>4)return -22;
 return (int)ft_call(io,FT_NR_UNLINKAT,FT_AT_FDCWD,(long)path,FT_AT_REMOVEDIR,0,0,0);
}
static int ft_fs_link(void *ctx,const char *target,const char *path) {
 struct ft_acm_io *io=ctx;if(ft_resource(target)!=4||ft_resource(path)!=5)return -22;
 return (int)ft_call(io,FT_NR_SYMLINKAT,(long)target,FT_AT_FDCWD,(long)path,0,0,0);
}
static long ft_read_file(struct ft_acm_io *io,const char *path,char *buf,unsigned long cap) {
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)path,FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd<0)return fd;
 unsigned long used=0;long result=0;
 while(used<cap) {
  long n=ft_retry(io,FT_NR_READ,fd,(long)(buf+used),cap-used);
  if(n<0){result=n;break;}
  if((unsigned long)n>cap-used){result=-5;break;}
  if(!n){result=(long)used;break;}
  used+=(unsigned long)n;result=(long)used;
 }
 if(result>=0&&used==cap) {
  char extra;long n=ft_retry(io,FT_NR_READ,fd,(long)&extra,1);
  if(n)result=n<0?n:-75;
 }
 long closed=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);
 return result<0?result:closed<0?closed:result;
}
static int ft_fs_write(void *ctx,const char *path,const char *data,unsigned long n) {
 struct ft_acm_io *io=ctx;
 if(!ft_write_path(path)||!n||n>64)return -22;
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)path,FT_O_WRONLY|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd<0)return (int)fd;
 long wrote=ft_retry(io,FT_NR_WRITE,fd,(long)data,n);
 long closed=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0); /* Never retry close after EINTR. */
 if(wrote==-19&&closed>=0&&ft_same(path,FT_ACM_ROOT "/UDC")&&n==1&&data[0]=='\n') {
  char current[96];long got=ft_read_file(io,path,current,sizeof(current));
  if(got==0||(got==1&&current[0]=='\n'))return 0; /* Already unbound, confirmed by readback. */
 }
 if(wrote<0)return (int)wrote;
 if((unsigned long)wrote!=n)return -5; /* Do not split configfs attribute stores. */
 return closed<0?(int)closed:0;
}
static const struct ft_acm_ops ft_acm_filesystem_ops={ft_fs_mkdir,ft_fs_write,ft_fs_link,ft_fs_unlink,ft_fs_rmdir};
static int ft_udc_path(char *out,unsigned long cap,const char *name,const char *suffix) {
 const char *parts[]={"/sys/class/udc/",name,suffix};unsigned long used=0;
 for(int p=0;p<3;p++)for(unsigned long i=0;parts[p][i];i++) {
  if(used+1>=cap)return -75;
  out[used++]=parts[p][i];
 }
 out[used]=0;return 0;
}
static int ft_bytes(const char *a,const char *b,unsigned long n) {
 for(unsigned long i=0;i<n;i++)if(a[i]!=b[i])return 0;
 return 1;
}
static int ft_expected_udc(struct ft_acm_io *io,const char *name) {
 char path[160],buf[96];long n;
 static const char compatible[]="mediatek,mt8163-musb\0mediatek,mtk-musb";
 static const unsigned char reg[]={0,0,0,0,0x11,0x20,0,0,0,0,0,0,0,0,0x10,0};
 if(ft_udc_path(path,sizeof(path),name,"/device/of_node/compatible"))return -75;
 n=ft_read_file(io,path,buf,sizeof(buf));if(n<0)return (int)n;
 if((unsigned long)n!=sizeof(compatible)||!ft_bytes(buf,compatible,sizeof(compatible)))return -19;
 if(ft_udc_path(path,sizeof(path),name,"/device/of_node/reg"))return -75;
 n=ft_read_file(io,path,buf,sizeof(buf));if(n<0)return (int)n;
 if((unsigned long)n!=sizeof(reg)||!ft_bytes(buf,(const char *)reg,sizeof(reg)))return -19;
 if(ft_udc_path(path,sizeof(path),name,"/device/of_node/dr_mode"))return -75;
 n=ft_read_file(io,path,buf,sizeof(buf));if(n<0)return (int)n;
 if(n!=(long)sizeof("peripheral")||!ft_bytes(buf,"peripheral",sizeof("peripheral")))return -19;
 return 0;
}
static int ft_discover_udc(struct ft_acm_io *io,char *out,unsigned long cap) {
 if(!io||!io->call||!out||cap<64)return -22;
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/sys/class/udc",FT_O_DIRECTORY|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd<0)return (int)fd;
 char selected[64]={0};int found=0,result=-75,ended=0;
 for(int chunk=0;chunk<8;chunk++) {
  unsigned char buf[2048];long n=ft_retry(io,FT_NR_GETDENTS64,fd,(long)buf,sizeof(buf));
  if(n<0){result=(int)n;break;}
  if(n>(long)sizeof(buf)){result=-5;break;}
  if(!n){ended=1;result=found==1?0:-19;break;}
  unsigned long pos=0;result=0;
  while(pos<(unsigned long)n) {
   if((unsigned long)n-pos<20){result=-22;break;}
   unsigned int record=buf[pos+16]|((unsigned int)buf[pos+17]<<8);
   if(record<24||record%8||record>(unsigned long)n-pos){result=-22;break;}
   unsigned long len=0;
   while(len<record-19&&buf[pos+19+len])len++;
   if(len==record-19||len>63){result=-22;break;}
   char name[64];for(unsigned long i=0;i<len;i++)name[i]=(char)buf[pos+19+i];name[len]=0;
   if(!ft_same(name,".")&&!ft_same(name,"..")) {
    if(!ft_acm_udc(name)){result=-22;break;}
    if(found++){result=-7;break;}
    for(unsigned long i=0;i<=len;i++)selected[i]=name[i];
   }
   pos+=record;
  }
  if(result)break;
 }
 long closed=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);
 if(result)return result;
 if(!ended)return -75;
 if(closed<0)return (int)closed;
 result=ft_expected_udc(io,selected);if(result)return result;
 for(unsigned long i=0;i<64;i++)out[i]=selected[i];
 return 0;
}
#endif
