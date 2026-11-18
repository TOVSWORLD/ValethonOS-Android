/* WRC1 binary screen record; no LCD driver, timer, heap or storage calls.
 * Writes only mirrored small bands within the independently corroborated
 * 12,288,000-byte framebuffer allocation. Pixel visibility is not assumed.
 */
#include "frontend.h"
extern const struct lfo_descriptor lbo_frontend;
extern int lb_cache_sync(void *,void *,unsigned);
int lw_screen(unsigned phase,unsigned value,unsigned status){
 if(phase<1||phase>8)return -1;
 /* This fixed device-only allocation is bound by the delivery guard to the
  * archived FBIOGET metadata and independent firmware videolfb tag. No mutable
  * console pointer, allocation, driver or timer is needed to report a gate.
  * Black/white words are invariant under the observed RGB/BGR byte ordering. */
 unsigned header=0x57000000|(phase<<16)|lbo_frontend.config.nonce[0]|(lbo_frontend.config.nonce[1]<<8);
 for(unsigned page=0;page<3;page++){
  unsigned at=0x98600000+page*4096000+(phase-1)*128000;
  for(unsigned line=0;line<4;line++){
   unsigned bits=line==0?header:line==1?value:line==2?status:header^value^status^0xc35a963cu;
   for(unsigned y=0;y<8;y++){
    volatile unsigned *out=(void *)(unsigned long)(at+(line*8+y)*3200);
    for(unsigned x=0;x<256;x++)out[x]=(bits&(1u<<(31-(x>>3))))?0xffffffffu:0xff000000u;
   }
  }
  for(unsigned off=0;off<128000;off+=16000)
   if(lb_cache_sync(0,(void *)(unsigned long)(at+off),16000))return -1;
 }
 return 0;
}
