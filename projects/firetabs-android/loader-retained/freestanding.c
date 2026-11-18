/* ARM EABI structure-copy helper for the analysis-only freestanding build. */
void __aeabi_memcpy8(void *destination,const void *source,unsigned count){
 volatile unsigned char *out=destination;const unsigned char *in=source;
 while(count--)*out++=*in++;
}
