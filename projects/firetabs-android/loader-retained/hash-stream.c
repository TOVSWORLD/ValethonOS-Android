#include "hash-stream.h"
int lhs_init(struct lhs_state *s,const struct lh_service *service){
 if(!s)return -1;s->active=0;s->failed=1;
 if(!service||!service->verified||!service->compress)return -1;
 const unsigned initial[8]={0x6a09e667U,0xbb67ae85U,0x3c6ef372U,0xa54ff53aU,0x510e527fU,0x9b05688cU,0x1f83d9abU,0x5be0cd19U};
 for(unsigned i=0;i<8;i++)s->words[i]=initial[i];
 s->bytes=0;s->compress=service->compress;s->active=1;s->failed=0;return 0;
}
int lhs_add(struct lhs_state *s,const void *input,unsigned n){
 if(!s||!s->active||s->failed)return -1;
 if((!input&&n)||(n&63)||n>8192||s->bytes>16U*1024*1024-n){s->failed=1;return -1;}
 if(n&&s->compress(s->words,input,n/64)){s->failed=1;return -2;}
 s->bytes+=n;return 0;
}
int lhs_finish(struct lhs_state *s,const unsigned char *expected){
 if(!s||!s->active||s->failed)return -1;
 s->active=0;
 if(!expected){s->failed=1;return -1;}
 unsigned char tail[64];volatile unsigned char *clear=tail;for(unsigned i=0;i<64;i++)clear[i]=0;
 tail[0]=0x80;unsigned bits=s->bytes<<3;for(unsigned i=0;i<4;i++)tail[63-i]=(unsigned char)(bits>>(8*i));
 if(s->compress(s->words,tail,1)){s->failed=1;return -2;}
 unsigned different=0;for(unsigned i=0;i<32;i++)different|=((s->words[i/4]>>(24-(i%4)*8))&255U)^expected[i];
 if(different){s->failed=1;return -3;}return 0;
}
