/* Private functional display probe. Kernel fbdev console draws the test banner.
 * Read-only sysfs metadata is not proof that physical pixels are visible.
 */
#ifndef FIRETABS_DISPLAY_STATUS_H
#define FIRETABS_DISPLAY_STATUS_H
#include "lab_log_io.h"
#define FD_PACKET_BYTES 120
struct fd_result {unsigned int stage,flags,width,height,bpp,stride,name_length;int error,banner_error;char name[32];};
static inline int fd_number(const char *text,unsigned long n,unsigned long *at,unsigned int *value){
 unsigned long start=*at;unsigned long number=0;
 while(*at<n&&text[*at]>='0'&&text[*at]<='9'){
  number=number*10+(unsigned int)(text[(*at)++]-'0');if(number>16777216)return -22;
 }
 if(*at==start)return -22;*value=(unsigned int)number;return 0;
}
static inline int fd_integer(struct ft_acm_io *io,const char *path,unsigned int *value){
 char b[32];unsigned long at=0;long n=ft_read_file(io,path,b,sizeof(b));if(n<0)return (int)n;
 int r=fd_number(b,(unsigned long)n,&at,value);return r?r:at+1==(unsigned long)n&&b[at]=='\n'?0:-22;
}
static inline int fd_metadata(struct ft_acm_io *io,struct fd_result *r){
 char size[32];long n=ft_read_file(io,"/sys/class/graphics/fb0/virtual_size",size,sizeof(size));unsigned long at=0;
 if(n<0)return (int)n;
 if(fd_number(size,(unsigned long)n,&at,&r->width)||at>=(unsigned long)n||size[at++]!=','||
    fd_number(size,(unsigned long)n,&at,&r->height)||at+1!=(unsigned long)n||size[at]!='\n')return -22;
 int result=fd_integer(io,"/sys/class/graphics/fb0/bits_per_pixel",&r->bpp);if(result)return result;
 result=fd_integer(io,"/sys/class/graphics/fb0/stride",&r->stride);if(result)return result;
 n=ft_read_file(io,"/sys/class/graphics/fb0/name",r->name,sizeof(r->name));if(n<0)return (int)n;
 if(n<2||n>32||r->name[n-1]!='\n')return -22;
 r->name_length=(unsigned int)n-1;r->name[n-1]=0;
 for(unsigned int i=0;i<r->name_length;i++)if(r->name[i]<' '||r->name[i]>'~')return -22;
 if(r->width!=800||r->height!=1280||(r->bpp!=16&&r->bpp!=24&&r->bpp!=32)||r->stride<(800*r->bpp+7)/8||r->stride>8192)return -19;
 if(!ft_same(r->name,"mediatekdrmfb"))return -19;
 return 0;
}
static inline int fd_banner(struct ft_acm_io *io){
 static const char banner[]="\033[2J\033[H\033[0mVALETHON DISPLAY TEST\nMaintained Linux - Douglas TPV\n\n\033[41m        RED        \033[0m\n\033[42m       GREEN       \033[0m\n\033[44m        BLUE       \033[0m\n\nUSB status follows; automatic return is bounded.\n";
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/console",FT_O_WRONLY|FT_SERIAL_NONBLOCK|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd<0)return (int)fd;
 long n=ft_retry(io,FT_NR_WRITE,fd,(long)banner,sizeof(banner)-1);
 long close=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);
 return n!=(long)sizeof(banner)-1?(n<0?(int)n:-5):close<0?(int)close:0;
}
static inline int fd_probe(struct ll_context *ctx,struct fd_result *r){
 int result=-110;r->stage=1;r->flags=1;
 for(unsigned int i=0;i<800&&ll_deadline(ctx);i++){
  result=fd_metadata(ctx->io,r);if(result!=-2)break;
  result=ll_pause(ctx);if(result)break;result=-110;
 }
 if(!result){r->stage=2;r->flags|=2;r->banner_error=fd_banner(ctx->io);result=r->banner_error;
  if(!result){r->stage=3;r->flags|=4;}}
 r->error=result;return result;
}
static inline void fd_le(unsigned char *p,unsigned long v,unsigned int n){for(unsigned int i=0;i<n;i++)p[i]=(unsigned char)(v>>(8*i));}
static inline void fd_packet(unsigned char packet[FD_PACKET_BYTES],const unsigned char nonce[32],const struct fd_result *r){
 for(unsigned int i=0;i<FD_PACKET_BYTES;i++)packet[i]=0;
 const char magic[]="VDISP001";for(unsigned int i=0;i<8;i++)packet[i]=(unsigned char)magic[i];
 for(unsigned int i=0;i<32;i++)packet[8+i]=nonce[i];
 fd_le(packet+40,1,4);fd_le(packet+44,r->stage,4);fd_le(packet+48,(unsigned int)r->error,4);fd_le(packet+52,r->flags,4);
 fd_le(packet+56,r->width,4);fd_le(packet+60,r->height,4);fd_le(packet+64,r->bpp,4);fd_le(packet+68,r->stride,4);
 fd_le(packet+72,(unsigned long)r->height*r->stride,8);fd_le(packet+80,r->name_length,4);fd_le(packet+84,(unsigned int)r->banner_error,4);
 for(unsigned int i=0;i<r->name_length&&i<32;i++)packet[88+i]=(unsigned char)r->name[i];
}
#endif
