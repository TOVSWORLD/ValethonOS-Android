/* Bounded nonblocking /dev/kmsg snapshot over the already-owned USB endpoint.
 * No ACK, mount, debugfs, privilege change, block I/O or reset operation.
 */
#ifndef FIRETABS_DISPLAY_ERRORS_H
#define FIRETABS_DISPLAY_ERRORS_H
#include "display_status.h"
#define DE_CAPACITY (256U*1024U)
#define DE_HEADER_BYTES 56
struct de_result {unsigned int bytes,records,flags;int error;};
static unsigned char de_buffer[DE_CAPACITY];
static inline void de_snapshot(struct ll_context *ctx,struct de_result *r){
 long fd=ll_open_kmsg(ctx->io);
 if(fd<0){r->error=(int)fd;r->flags=16;return;}
 unsigned char record[8192];
 for(unsigned int i=0;i<4096;i++){
  if(!ll_deadline(ctx)){r->error=-110;r->flags|=8;break;}
  long n=ft_call(ctx->io,FT_NR_READ,fd,(long)record,sizeof(record),0,0,0);
  if(n==-4)continue;
  if(n==-32){r->flags|=4;continue;}
  if(n==-11){r->flags|=1;break;}
  if(n<=0||n>(long)sizeof(record)){r->error=n<0?(int)n:-5;r->flags|=16;break;}
  if((unsigned long)n>DE_CAPACITY-r->bytes){r->flags|=2;break;}
  for(unsigned int j=0;j<(unsigned int)n;j++)de_buffer[r->bytes+j]=record[j];
  r->bytes+=(unsigned int)n;r->records++;
 }
 if(!(r->flags&27))r->flags|=2;
 long closed=ft_call(ctx->io,FT_NR_CLOSE,fd,0,0,0,0,0);
 if(closed<0&&!r->error){r->error=(int)closed;r->flags|=16;}
}
static inline int de_send(struct ll_context *ctx,const unsigned char nonce[32],const struct de_result *r){
 unsigned char header[DE_HEADER_BYTES]={0};const char magic[]="VKMSG001";
 for(unsigned int i=0;i<8;i++)header[i]=(unsigned char)magic[i];
 for(unsigned int i=0;i<32;i++)header[i+8]=nonce[i];
 fd_le(header+40,r->bytes,4);fd_le(header+44,(unsigned int)r->error,4);
 fd_le(header+48,r->flags,4);fd_le(header+52,r->records,4);
 int result=ll_send(ctx,header,sizeof(header));
 for(unsigned int at=0;!result&&at<r->bytes;){
  unsigned int n=r->bytes-at;if(n>4096)n=4096;
  result=ll_send(ctx,de_buffer+at,n);at+=n;
 }
 return result;
}
#endif
