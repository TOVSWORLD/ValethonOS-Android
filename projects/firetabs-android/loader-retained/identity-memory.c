#include "identity.h"
/* Analysis frontend: descriptor ownership must be established before use. Exact
 * selected field reads only, no lazy getter, CID, user data or MMIO access. */
int li_memory_read(void *context,unsigned address,unsigned char *out,unsigned n){
 const struct li_plan *p=context;
 if(!p||!out||!p->device||!p->block_device||(p->device|p->block_device)&3||p->card!=0x4bd7e280u||p->host!=0x4bd7edf0u)return -1;
 if(p->device>0xfffffff3u)return -1;
 int allowed=(address==0x4bd7e038u&&n==4)||((address==p->device+4||address==p->device+8)&&n==4)||(address==p->host+0x28&&n==4);
 static const unsigned offsets[]={0,0x18,0x1c,0x10c,0x6d,0x145};
 for(unsigned i=0;i<6;i++)if(address==p->card+offsets[i]&&n==((i==3||i==4)?1u:4u))allowed=1;
 if(!allowed)return -1;
 const volatile unsigned char *input=(const volatile unsigned char *)(unsigned long)address;
 for(unsigned i=0;i<n;i++)out[i]=input[i];return 0;
}
