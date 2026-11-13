#include "identity.h"
static int field(const struct li_reader *r,unsigned base,unsigned off,unsigned n,unsigned *value){
 unsigned char b[4];if(!base||base>0xffffffffu-off||base+off>0xffffffffu-(n-1)||r->read(r->context,base+off,b,n))return -1;
 *value=0;for(unsigned i=0;i<n;i++)*value|=(unsigned)b[i]<<(8*i);return 0;
}
static int snapshot(struct li_binding *out,const struct li_plan *p,const struct li_reader *r){
 unsigned id,block,host,base,flags,rca,revision,enabled,size;
 if(field(r,p->device,4,4,&id)||field(r,p->device,8,4,&block)||field(r,p->card,0,4,&host)||field(r,p->host,0x28,4,&base)||field(r,p->card,0x18,4,&rca)||field(r,p->card,0x1c,4,&flags)||field(r,p->card,0x10c,1,&revision)||field(r,p->card,0x6d,1,&enabled)||field(r,p->card,0x145,4,&size))return -1;
 if(id||block!=p->block_device||host!=p->host||base!=0x11230000u||!rca||rca>65535||!(flags&1)||revision<6||revision>8||enabled>1||!size||size>0x400000u)return -1;
 *out=(struct li_binding){p->device,p->card,p->host,block,rca,size,enabled};return 0;
}
int li_capture(struct li_binding *out,const struct li_plan *p,const struct li_reader *r){
 if(!out)return -1;*out=(struct li_binding){0};
 if(!p||!r||!r->read||!p->device||!p->card||!p->host||!p->block_device||(p->device|p->card|p->host|p->block_device)&3)return -1;
 struct li_binding a,b;if(snapshot(&a,p,r)||snapshot(&b,p,r))return -1;
 if(a.device!=b.device||a.card!=b.card||a.host!=b.host||a.block_device!=b.block_device||a.rca!=b.rca||a.cache_size_kib!=b.cache_size_kib||a.cache_enabled!=b.cache_enabled)return -1;
 *out=a;return 0;
}
/* Pinned archived get_device's global slot, without its lazy-init callback or
 * initialized-flag write. Host/card zero addresses derive from pure getters. */
int li_discover(struct li_binding *out,unsigned expected_device,unsigned expected_block,const struct li_reader *reader){
 if(!out)return -1;*out=(struct li_binding){0};
 if(!reader||!reader->read||!expected_device||!expected_block||(expected_device|expected_block)&3)return -1;
 unsigned device;if(field(reader,0x4bd7e038u,0,4,&device)||device!=expected_device)return -1;
 struct li_plan plan={device,0x4bd7e280u,0x4bd7edf0u,expected_block};
 return li_capture(out,&plan,reader);
}
