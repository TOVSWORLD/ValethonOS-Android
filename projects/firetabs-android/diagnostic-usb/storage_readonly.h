/* Private Douglas storage probe: fixed p5, O_RDONLY, no block ioctl or mount.
 * Hardware reset remains the backstop for an uninterruptible driver read.
 * The digest field contains the expected digest ONLY after verification.
 */
#ifndef FIRETABS_STORAGE_READONLY_H
#define FIRETABS_STORAGE_READONLY_H
#include "lab_log_io.h"
#define FS_BOOT_BYTES (16UL*1024*1024)
#define FS_PACKET_BYTES 120
struct fs_result { unsigned int stage,flags;int error;unsigned long bytes; };
int combined_verify(const unsigned char *,unsigned long,const unsigned char[32]);
static const unsigned char fs_boot_hash[32]={
 0x08,0xfc,0xf3,0x45,0x5d,0x66,0x94,0x36,0x32,0xd0,0xfc,0x91,0x34,0x8d,0x4a,0xb7,
 0xd4,0x1b,0x80,0xc4,0x0d,0x88,0xe6,0x12,0x72,0x00,0x0a,0x1d,0x69,0x7f,0xaa,0x1e};
static inline int fs_metadata(struct ft_acm_io *io) {
 static const char *const paths[]={"/sys/class/block/mmcblk0p5/dev","/sys/class/block/mmcblk0p5/partition","/sys/class/block/mmcblk0p5/size","/sys/class/block/mmcblk0/device/type"};
 static const char *const values[]={"179:5\n","5\n","32768\n","MMC\n"};
 for(unsigned i=0;i<4;i++){
  char b[32]={0};long n=ft_read_file(io,paths[i],b,sizeof(b)-1);
  if(n<0)return (int)n;
  unsigned long wanted=0;while(values[i][wanted])wanted++;
  if(n!=(long)wanted||!ft_same(b,values[i]))return -19;
 }
 return 0;
}
static inline int fs_node(struct ft_acm_io *io,long fd) {
 unsigned long long aligned[32]={0};unsigned char *st=(unsigned char *)aligned;
 long r=ft_call(io,FT_SERIAL_STATX,fd,(long)"",FT_SERIAL_AT_EMPTY_PATH,FT_SERIAL_STATX_TYPE,(long)st,0);
 if(r<0)return (int)r;
 unsigned mode=(unsigned)st[28]|((unsigned)st[29]<<8);
 return (!(ft_serial_u32(st)&FT_SERIAL_STATX_TYPE)||(mode&FT_SERIAL_IFMT)!=0060000||ft_serial_u32(st+128)!=179||ft_serial_u32(st+132)!=5)?-19:0;
}
static inline int fs_probe(struct ll_context *ctx,struct fs_result *out) {
 struct ft_acm_io *io=ctx->io;long fd=-1,memory=-1;int r=-110;
 out->stage=1;out->flags=1;out->bytes=0; /* Caller has verified enforcing policy. */
 for(unsigned i=0;i<800&&ll_deadline(ctx);i++){
  r=fs_metadata(io);if(r!=-2)break;
  r=ll_pause(ctx);if(r)break;
  r=-110;
 }
 if(r)goto done;
 out->flags|=2;out->stage=2;
 fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/firetabs-boot",FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd<0){r=(int)fd;goto done;}
 r=fs_node(io,fd);if(r)goto done;
 out->flags|=4;out->stage=3;
 memory=ft_call(io,222,0,FS_BOOT_BYTES,3,0x22,-1,0); /* private anonymous RW RAM */
 if(memory<0&&memory>=-4095){r=(int)memory;memory=-1;goto done;}
 for(unsigned tries=0;out->bytes<FS_BOOT_BYTES&&tries<8192;tries++){
  if(!ll_deadline(ctx)){r=-110;goto done;}
  unsigned long n=FS_BOOT_BYTES-out->bytes;if(n>65536)n=65536;
  long got=ft_retry(io,FT_NR_READ,fd,memory+(long)out->bytes,n);
  if(got<=0||got>(long)n){r=got<0?(int)got:-5;goto done;}
  out->bytes+=(unsigned long)got;
 }
 if(out->bytes!=FS_BOOT_BYTES){r=-75;goto done;}
 {unsigned char extra;long got=ft_retry(io,FT_NR_READ,fd,(long)&extra,1);if(got){r=got<0?(int)got:-27;goto done;}}
 out->flags|=8;out->stage=4;
 if(!ll_deadline(ctx)){r=-110;goto done;}
 r=combined_verify((const unsigned char *)memory,FS_BOOT_BYTES,fs_boot_hash)?-74:0;
 if(!ll_deadline(ctx))r=-110;
 if(!r){out->flags|=16;out->stage=5;}
done:
 if(memory!=-1){long z=ft_call(io,215,memory,FS_BOOT_BYTES,0,0,0,0);if(!r&&z)r=(int)z;}
 if(fd>=0){long z=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);if(!r&&z)r=(int)z;}
 out->error=r;return r;
}
static inline void fs_le(unsigned char *p,unsigned long v,unsigned n){for(unsigned i=0;i<n;i++)p[i]=(unsigned char)(v>>(8*i));}
static inline void fs_packet(unsigned char packet[FS_PACKET_BYTES],const unsigned char nonce[32],const struct fs_result *r){
 for(unsigned i=0;i<FS_PACKET_BYTES;i++)packet[i]=0;
 const char magic[]="VSTORE01";for(unsigned i=0;i<8;i++)packet[i]=(unsigned char)magic[i];
 for(unsigned i=0;i<32;i++)packet[8+i]=nonce[i];
 fs_le(packet+40,1,4);fs_le(packet+44,r->stage,4);fs_le(packet+48,(unsigned int)r->error,4);fs_le(packet+52,r->flags,4);
 fs_le(packet+56,r->bytes,8);fs_le(packet+64,FS_BOOT_BYTES,8);
 /* Reserved card-capacity field deliberately zero; no CID/serial collected. */
 fs_le(packet+80,179,4);fs_le(packet+84,5,4);
 if(r->flags&16)for(unsigned i=0;i<32;i++)packet[88+i]=fs_boot_hash[i];
}
#endif
