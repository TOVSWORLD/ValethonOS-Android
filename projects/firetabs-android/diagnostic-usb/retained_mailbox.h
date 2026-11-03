/* Bounded private trial boot-tail record format. No device discovery or admission.
 * Caller must hold exclusive target access, verify prefix SHA256 and exact size,
 * and supply synchronous read/write/flush callbacks. No original/recovery writes.
 */
#ifndef VALETHON_RETAINED_MAILBOX_H
#define VALETHON_RETAINED_MAILBOX_H
#define VM_BASE (15UL*1024*1024)
#define VM_HEADER 4096UL
#define VM_SLOT (127UL*4096)
#define VM_SLOT_BASE (VM_BASE+VM_HEADER)
#define VM_PARTITION (16UL*1024*1024)
#define VM_CAPACITY (VM_SLOT-VM_HEADER)
struct vm_io {
 void *context;
 int (*read)(void *,unsigned long,void *,unsigned long);
 int (*write)(void *,unsigned long,const void *,unsigned long);
 int (*flush)(void *);
 int (*prefix_sha256)(void *,const unsigned char *);
};
struct vm_record {unsigned long long sequence;unsigned used,index;};
static unsigned vm_u32(const unsigned char *p){return (unsigned)p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static unsigned long long vm_u64(const unsigned char *p){return (unsigned long long)vm_u32(p)|((unsigned long long)vm_u32(p+4)<<32);}
static void vm_put32(unsigned char *p,unsigned x){for(unsigned i=0;i<4;i++)p[i]=(unsigned char)(x>>(8*i));}
static void vm_put64(unsigned char *p,unsigned long long x){vm_put32(p,(unsigned)x);vm_put32(p+4,(unsigned)(x>>32));}
static int vm_equal(const unsigned char *a,const unsigned char *b,unsigned long n){for(unsigned long i=0;i<n;i++)if(a[i]!=b[i])return 0;return 1;}
static int vm_zero(const unsigned char *a,unsigned long n){for(unsigned long i=0;i<n;i++)if(a[i])return 0;return 1;}
static unsigned vm_crc_update(unsigned crc,const unsigned char *p,unsigned long n){
 for(unsigned long i=0;i<n;i++){crc^=p[i];for(unsigned j=0;j<8;j++)crc=(crc>>1)^(0xedb88320U&(0U-(crc&1)));}return crc;
}
static unsigned vm_crc(const unsigned char *p,unsigned long n){return ~vm_crc_update(~0U,p,n);}
static int vm_read_record(struct vm_io *io,unsigned index,const unsigned char *nonce,struct vm_record *r,unsigned char *scratch){
 unsigned long start=VM_SLOT_BASE+index*VM_SLOT;
 if(io->read(io->context,start,scratch,VM_HEADER))return -1;
 if(vm_zero(scratch,VM_HEADER))return 0;
 if(!vm_equal(scratch,(const unsigned char *)"VLOG0001",8)||vm_u32(scratch+8)!=1||vm_u32(scratch+12)!=VM_HEADER||!vm_u64(scratch+16)||!vm_equal(scratch+24,nonce,32)||!vm_zero(scratch+68,VM_HEADER-68))return 0;
 unsigned wanted=vm_u32(scratch+64);vm_put32(scratch+64,0);if(vm_crc(scratch,VM_HEADER)!=wanted)return 0;
 r->sequence=vm_u64(scratch+16);r->used=vm_u32(scratch+56);r->index=index;
 if(!r->used||r->used>VM_CAPACITY)return 0;
 wanted=vm_u32(scratch+60);unsigned crc=~0U;
 for(unsigned long at=0;at<r->used;){unsigned long n=r->used-at;if(n>VM_HEADER)n=VM_HEADER;if(io->read(io->context,start+VM_HEADER+at,scratch,n))return -1;crc=vm_crc_update(crc,scratch,n);at+=n;}
 return (~crc==wanted)?1:0;
}
static int vm_commit(struct vm_io *io,const unsigned char *nonce,const unsigned char *payload,unsigned used,unsigned char *scratch,struct vm_record *committed){
 if(!io||!io->read||!io->write||!io->flush||!io->prefix_sha256||!nonce||vm_zero(nonce,32)||!payload||!used||used>VM_CAPACITY)return -1;
 if(io->read(io->context,VM_BASE,scratch,VM_HEADER))return -2;
 if(!vm_equal(scratch,(const unsigned char *)"VSEED001",8)||!vm_equal(scratch+8,nonce,32)||!vm_zero(scratch+76,VM_HEADER-76))return -3;
 unsigned seed_crc=vm_u32(scratch+72);vm_put32(scratch+72,0);if(vm_crc(scratch,VM_HEADER)!=seed_crc||io->prefix_sha256(io->context,scratch+40))return -3;
 if(io->read(io->context,VM_PARTITION-VM_HEADER,scratch,VM_HEADER)||!vm_zero(scratch,VM_HEADER))return -3;
 struct vm_record a={0},b={0};int va=vm_read_record(io,0,nonce,&a,scratch),vb=vm_read_record(io,1,nonce,&b,scratch);
 if(va<0||vb<0||(va&&vb&&a.sequence==b.sequence))return -4;
 struct vm_record latest={0};if(va)latest=a;if(vb&&b.sequence>latest.sequence)latest=b;
 if(!latest.sequence){
  for(unsigned long at=VM_SLOT_BASE;at<VM_PARTITION-VM_HEADER;at+=VM_HEADER){if(io->read(io->context,at,scratch,VM_HEADER)||!vm_zero(scratch,VM_HEADER))return -4;}
 }
 if(latest.sequence==~0ULL)return -4;
 unsigned index=latest.sequence?1-latest.index:0;unsigned long start=VM_SLOT_BASE+index*VM_SLOT;
 for(unsigned long i=0;i<VM_HEADER;i++)scratch[i]=0;
 if(io->write(io->context,start,scratch,VM_HEADER)||io->flush(io->context))return -5;
 if(io->write(io->context,start+VM_HEADER,payload,used)||io->flush(io->context))return -5;
 for(unsigned long i=0;i<VM_HEADER;i++)scratch[i]=0;
 for(unsigned i=0;i<8;i++)scratch[i]=((const unsigned char *)"VLOG0001")[i];
 vm_put32(scratch+8,1);vm_put32(scratch+12,VM_HEADER);vm_put64(scratch+16,latest.sequence+1);
 for(unsigned i=0;i<32;i++)scratch[24+i]=nonce[i];
 vm_put32(scratch+56,used);vm_put32(scratch+60,vm_crc(payload,used));vm_put32(scratch+64,vm_crc(scratch,VM_HEADER));
 if(io->write(io->context,start,scratch,VM_HEADER)||io->flush(io->context))return -5;
 int result=vm_read_record(io,index,nonce,committed,scratch);
 if(result!=1||committed->sequence!=latest.sequence+1||committed->used!=used)return -6;
 return 0;
}
#endif
