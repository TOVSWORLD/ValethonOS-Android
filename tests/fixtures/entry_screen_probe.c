/* Emulator RAM only: no device framebuffer or physical RAM access. */
typedef unsigned long u64;typedef unsigned int u32;
extern int invoke_marker(u64);
static void message(const char *p){register u64 x0 __asm__("x0")=4;register const char *x1 __asm__("x1")=p;__asm__ volatile("hlt #0xf000":"+r"(x0):"r"(x1):"memory");}
int main(void){volatile u64 *start=(volatile u64 *)0x98600000UL,*end=(volatile u64 *)0x991b8000UL;volatile u32 *dt=(volatile u32 *)0x48000000UL;start[-1]=0x12345678;end[0]=0xabcdef;
 for(u64 *p=(u64 *)start;p<(u64 *)end;p++)*p=0;
 for(int test=0;test<9;test++){
  for(int i=0;i<32;i++)dt[i]=0;
  dt[0]=0xedfe0dd0;dt[1]=0x6f000000;dt[2]=0x38000000;dt[3]=0x64000000;dt[4]=0x28000000;dt[5]=0x11000000;dt[6]=0x10000000;dt[8]=0x0b000000;dt[9]=0x2c000000;
  dt[14]=0x01000000;dt[16]=0x03000000;dt[17]=0x10000000;dt[23]=0x02000000;dt[24]=0x09000000;
  const char *value="mediatek,mt8163";const char *name="compatible";
  for(int i=0;i<16;i++)((volatile char *)dt)[76+i]=value[i];
  for(int i=0;i<11;i++)((volatile char *)dt)[100+i]=name[i];
  if(test==1)dt[0]=0;
  if(test==2)dt[1]=0x27000000;
  if(test==3)dt[1]=0x01001000;
  if(test==4)((volatile char *)dt)[76]='x';
  if(test==5)((volatile char *)dt)[100]='X';
  if(test==6)dt[18]=0xffffffff;
  if(test==7)dt[9]=0x04000000;
  if(invoke_marker(test==0?0:0x48000000UL))goto fail;
  if(test<8){for(volatile u64 *p=start;p<end;p++)if(*p)goto fail;}
 }
 for(volatile u64 *p=start;p<end;p++)if(*p!=(((u64)p&0x10000)?0UL:~0UL))goto fail;
 if(start[-1]!=0x12345678||end[0]!=0xabcdef)goto fail;
 message("ENTRY_SCREEN_EMULATED_SPAN_GATES_REGISTERS_PASS\n");return 0;
fail:message("ENTRY_SCREEN_EMULATED_FAIL\n");return 1;}
