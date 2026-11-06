/* Actual nonblocking Linux/AArch64 fd adapters for the separate lab candidate.
 * Caller must own an opened duplex ACM port after policy/role/identity checks.
 * No gadget activation, filesystem mount, failure injection or reboot here. */
#ifndef VALETHON_LAB_LOG_IO_H
#define VALETHON_LAB_LOG_IO_H
#include "acm_serial.h"
#include "kernel_log_stream.h"
#define LL_NR_LSEEK 62
#define LL_NR_CLOCK_GETTIME 113
struct ll_context {
 struct ft_acm_io *io;long serial_fd,kmsg_fd;
 unsigned long deadline_ms,stop_ms;
};
static inline unsigned long ll_now(struct ll_context *ctx) {
 long ts[2]={0,0};
 if(ft_call(ctx->io,LL_NR_CLOCK_GETTIME,1,(long)ts,0,0,0,0)<0||ts[0]<0||ts[1]<0||ts[1]>=1000000000)return 0;
 if((unsigned long)ts[0]>(~0UL-1000)/1000)return 0;
 return (unsigned long)ts[0]*1000+(unsigned long)ts[1]/1000000;
}
static inline int ll_deadline(void *opaque) {
 struct ll_context *ctx=opaque;unsigned long now=ll_now(ctx);
 return now&&now<ctx->deadline_ms;
}
static inline int ll_pause(struct ll_context *ctx) {
 const long ts[2]={0,10000000};long r=ft_call(ctx->io,FT_SERIAL_NANOSLEEP,(long)ts,0,0,0,0,0);
 return r<0&&r!=-4?(int)r:0;
}
static inline int ll_transfer(struct ll_context *ctx,unsigned char *data,unsigned long n,int writing,unsigned long limit) {
 unsigned long used=0;
 if(!n||n>VL_MAX_RECORD)return -22;
 for(unsigned long tries=0;tries<16384&&used<n;tries++) {
  unsigned long now=ll_now(ctx);if(!now||now>=ctx->deadline_ms||now>=limit)return -110;
  long r=ft_call(ctx->io,writing?FT_NR_WRITE:FT_NR_READ,ctx->serial_fd,(long)(data+used),n-used,0,0,0);
  now=ll_now(ctx);if(!now||now>=ctx->deadline_ms||now>=limit)return -110;
  if(r==-4)continue;
  if(r==-11){int paused=ll_pause(ctx);if(paused)return paused;continue;}
  if(r<=0)return r<0?(int)r:-5;
  if((unsigned long)r>n-used)return -5;
  used+=(unsigned long)r;
 }
 return used==n?0:-110;
}
static inline int ll_send(void *opaque,const unsigned char *data,unsigned long n) {
 struct ll_context *ctx=opaque;
 return ll_transfer(ctx,(unsigned char *)data,n,1,ctx->deadline_ms);
}
static inline int ll_ack(void *opaque,unsigned char *data,unsigned long n) {
 struct ll_context *ctx=opaque;unsigned long now=ll_now(ctx);
 if(!now||now>~0UL-10000)return -110;
 int r=ll_transfer(ctx,data,n,0,now+10000);
 if(!r){now=ll_now(ctx);if(!now||now>~0UL-10000)return -110;ctx->stop_ms=now+10000;}
 return r;
}
static inline long ll_read_log(void *opaque,unsigned char *data,unsigned long cap) {
 struct ll_context *ctx=opaque;
 if(!ctx->stop_ms||!cap||cap>VL_MAX_RECORD)return -22;
 for(unsigned long tries=0;tries<65536;tries++) {
  unsigned long now=ll_now(ctx);
  if(!now||now>=ctx->deadline_ms)return -110;
  if(now>=ctx->stop_ms)return 0; /* Explicit clean ten-second capture end. */
  long r=ft_call(ctx->io,FT_NR_READ,ctx->kmsg_fd,(long)data,cap,0,0,0);
  if(!ll_deadline(ctx))return -110;
  if(r==-4)continue;
  if(r==-11){int paused=ll_pause(ctx);if(paused)return paused;continue;}
  if(r==0)return -5; /* Unexpected EOF, never a fabricated clean end. */
  return r; /* Includes EPIPE: ring loss invalidates complete capture. */
 }
 return -110;
}
static inline long ll_open_kmsg(struct ft_acm_io *io) {
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/kmsg",FT_SERIAL_NONBLOCK|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd<0)return fd;
 unsigned long long aligned[32]={0};unsigned char *st=(unsigned char *)aligned;
 long r=ft_call(io,FT_SERIAL_STATX,fd,(long)"",FT_SERIAL_AT_EMPTY_PATH,FT_SERIAL_STATX_TYPE,(long)st,0);
 unsigned int mode=(unsigned int)st[28]|((unsigned int)st[29]<<8);
 if(r>=0&&(!(ft_serial_u32(st)&FT_SERIAL_STATX_TYPE)||(mode&FT_SERIAL_IFMT)!=FT_SERIAL_IFCHR||
    ft_serial_u32(st+128)!=1||ft_serial_u32(st+132)!=11))r=-19;
 if(r>=0){r=ft_call(io,LL_NR_LSEEK,fd,0,0,0,0,0);if(r>0)r=-5;} /* Oldest record. */
 if(r<0){ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);return r;}
 return fd;
}
#endif
