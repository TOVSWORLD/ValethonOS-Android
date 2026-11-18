/* Bounded log producer; caller owns admitted transport and nonblocking kmsg fd.
 * No USB activation, failure injection, storage write or reboot interface. */
#ifndef VALETHON_KERNEL_LOG_STREAM_H
#define VALETHON_KERNEL_LOG_STREAM_H
#define VL_MAX_RECORD 8192UL
#define VL_MAX_TOTAL (256UL*1024UL)
struct vl_io {
 long (*read_log)(void *,unsigned char *,unsigned long);
 int (*send_all)(void *,const unsigned char *,unsigned long);
 int (*receive_ack)(void *,unsigned char *,unsigned long);
 int (*within_deadline)(void *);
 void *ctx;
};
static inline void vl_u32(unsigned char *out,unsigned long n) {
 out[0]=(unsigned char)(n>>24);out[1]=(unsigned char)(n>>16);
 out[2]=(unsigned char)(n>>8);out[3]=(unsigned char)n;
}
static inline int vl_stream(struct vl_io *io,const unsigned char nonce[32]) {
 unsigned char header[40]={'V','L','O','G','0','0','0','2'},ack[40],buffer[VL_MAX_RECORD],frame[8];
 unsigned long total=0,seq=0;int nonzero=0;
 if(!io||!nonce||!io->read_log||!io->send_all||!io->receive_ack||!io->within_deadline)return -22;
 for(int i=0;i<32;i++){header[8+i]=nonce[i];nonzero|=nonce[i];}
 if(!nonzero)return -22;
 if(!io->within_deadline(io->ctx)||io->send_all(io->ctx,header,40))return -5;
 if(io->receive_ack(io->ctx,ack,40)||!io->within_deadline(io->ctx))return -5;
 const unsigned char prefix[8]={'V','A','C','K','0','0','0','2'};
 for(int i=0;i<40;i++)if(ack[i]!=(i<8?prefix[i]:nonce[i-8]))return -5;
 /* A zero read is a caller-selected clean snapshot end. EAGAIN/EPIPE are not
  * silently converted to success; live waiting/lost-record policy belongs to
  * the nonblocking kmsg adapter and its separately reviewed trial lifecycle. */
 for(unsigned long attempts=0;attempts<VL_MAX_TOTAL+16;attempts++) {
  if(!io->within_deadline(io->ctx))return -110;
  long n=io->read_log(io->ctx,buffer,VL_MAX_RECORD);
  if(!io->within_deadline(io->ctx))return -110;
  if(n==-4)continue;
  if(n<0)return (int)n;
  if((unsigned long)n>VL_MAX_RECORD||total+(unsigned long)n>VL_MAX_TOTAL)return -75;
  vl_u32(frame,seq);vl_u32(frame+4,(unsigned long)n);
  if(io->send_all(io->ctx,frame,8))return -5;
  if(n&&io->send_all(io->ctx,buffer,(unsigned long)n))return -5;
  if(!io->within_deadline(io->ctx))return -110;
  if(!n){
   /* Keep the gadget bound until the host has fsynced the terminal record. */
   if(io->receive_ack(io->ctx,ack,40)||!io->within_deadline(io->ctx))return -5;
   const unsigned char done[8]={'V','D','O','N','0','0','0','2'};
   for(int i=0;i<40;i++)if(ack[i]!=(i<8?done[i]:nonce[i-8]))return -5;
   return 0;
  }
  total+=(unsigned long)n;seq++;
 }
 return -110;
}
#endif
