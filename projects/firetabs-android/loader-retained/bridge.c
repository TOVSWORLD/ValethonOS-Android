#include "bridge.h"
#define LB_PREFIX (15ULL*1024*1024)
static int lb_nonzero(const unsigned char *p){unsigned n=0;for(unsigned i=0;i<32;i++)n|=p[i];return n!=0;}
int lb_load(struct lb_result *out,const struct lb_plan *plan,const struct lb_io *io){
 if(!out)return -1;
 if(out->attempted){out->loaded=0;out->start=0;out->emit=0;return -1;}
 out->attempted=1;out->loaded=0;out->code=0;out->state=0;out->stack_top=0;out->start=0;out->emit=0;out->allocation_bytes=0;
 if(!plan||!io||!io->read||!io->allocate||!io->sha256_equal||!io->cache_sync)return -2;
 /* Copy immutable inputs before allocating or reading. These flags require
  * separately proved bindings, never discovery or admission by this bridge. */
 struct lb_plan p=*plan;struct lb_io cb=*io;
 if(!p.bindings_verified||p.code_bytes<512||p.code_bytes>16384||(p.code_bytes&511)||
    !p.state_bytes||p.state_bytes>12288||p.stack_bytes!=4096||
    !(p.start_offset&1)||!(p.emit_offset&1)||p.start_offset>=p.code_bytes||p.emit_offset>=p.code_bytes||
    !lb_nonzero(p.sha256)||!p.target_first_sector||p.target_first_sector>(~0ULL-16*1024*1024)/512||
    (p.blob_offset&4095)||p.blob_offset<4096||p.blob_offset>LB_PREFIX-p.code_bytes)return -3;
 unsigned state_capacity=(p.state_bytes+15)&~15U;
 unsigned total=p.code_bytes+state_capacity+p.stack_bytes;
 unsigned char *base=cb.allocate(16,total);
 if(!base)return -4;
 unsigned long address=(unsigned long)base;
 if((address&15)||address>~0UL-total)return -5;
 /* Allocated RAM may be written, never the source partition. No retry/free of
  * an uncertain allocation. Publish callable entries only after hash+cache. */
 if(cb.read(cb.context,p.target_first_sector*512+p.blob_offset,base,p.code_bytes))return -6;
 if(cb.sha256_equal(cb.context,base,p.code_bytes,p.sha256))return -7;
 volatile unsigned char *zero=base+p.code_bytes;
 for(unsigned i=0;i<state_capacity+p.stack_bytes;i++)zero[i]=0;
 if(cb.cache_sync(cb.context,base,p.code_bytes))return -8;
 out->code=base;out->state=base+p.code_bytes;out->stack_top=base+total;
 out->start=base+p.start_offset;out->emit=base+p.emit_offset;
 out->allocation_bytes=total;out->loaded=1;return 0;
}
