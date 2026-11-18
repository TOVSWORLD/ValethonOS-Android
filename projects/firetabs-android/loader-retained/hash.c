#include "hash.h"
/* SHA-256 framing around the pinned generic ARM compression implementation.
 * No CPU feature selection, device I/O, allocation, global writes or firmware
 * capability-register changes. This helper is bounded to16MiB RAM input. */
int lh_equal(void *opaque,const void *input,unsigned n,const unsigned char *expected){
 struct lh_service *service=opaque;
 if(!service||!service->verified||!service->compress||!expected||(!input&&n)||n>16U*1024*1024)return -1;
 const unsigned char *in=input;
 unsigned state[8]={0x6a09e667U,0xbb67ae85U,0x3c6ef372U,0xa54ff53aU,0x510e527fU,0x9b05688cU,0x1f83d9abU,0x5be0cd19U};
 if(n>=64&&service->compress(state,in,n/64))return -2;
 unsigned remainder=n&63U,blocks=remainder<56?1:2;
 unsigned char tail[128];volatile unsigned char *clear=tail;
 for(unsigned i=0;i<128;i++)clear[i]=0;
 for(unsigned i=0;i<remainder;i++)tail[i]=in[(n&~63U)+i];
 tail[remainder]=0x80;
 unsigned bits=n<<3,end=blocks*64;
 for(unsigned i=0;i<4;i++)tail[end-1-i]=(unsigned char)(bits>>(i*8));
 if(service->compress(state,tail,blocks))return -2;
 unsigned different=0;
 for(unsigned i=0;i<32;i++)different|=((state[i/4]>>(24-(i%4)*8))&255U)^expected[i];
 return different?-3:0;
}
