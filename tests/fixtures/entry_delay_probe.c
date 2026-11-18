/* Bare-metal emulator RAM only. Never a physical device helper. */
typedef unsigned long u64;
extern int invoke_entry_delay(void);
extern volatile u64 valethon_entry_delay_seconds;
static u64 el(void){u64 v;__asm__ volatile("mrs %0,CurrentEL":"=r"(v));return v;}
static u64 counter(void){u64 v;__asm__ volatile("isb; mrs %0,cntpct_el0":"=r"(v));return v;}
static u64 frequency(void){u64 v;__asm__ volatile("mrs %0,cntfrq_el0":"=r"(v));return v;}
static void set_frequency(u64 v){__asm__ volatile("msr cntfrq_el0,%0;isb"::"r"(v):"memory");}
static u64 control(void){u64 v;if(el()==4)__asm__ volatile("mrs %0,sctlr_el1":"=r"(v));else if(el()==8)__asm__ volatile("mrs %0,sctlr_el2":"=r"(v));else __asm__ volatile("mrs %0,sctlr_el3":"=r"(v));return v;}
static void set_control(u64 v){if(el()==4)__asm__ volatile("msr sctlr_el1,%0;isb"::"r"(v):"memory");else if(el()==8)__asm__ volatile("msr sctlr_el2,%0;isb"::"r"(v):"memory");else __asm__ volatile("msr sctlr_el3,%0;isb"::"r"(v):"memory");}
static void message(const char *p){register u64 x0 __asm__("x0")=4;register const char *x1 __asm__("x1")=p;__asm__ volatile("hlt #0xf000":"+r"(x0):"r"(x1):"memory");}
int main(void){
 volatile u64 *start=(volatile u64 *)0x98600000UL,*end=(volatile u64 *)0x991b8000UL;
 u64 mode=el(),freq=frequency(),saved=control();
 if((mode!=4&&mode!=8&&mode!=12)||!freq||(saved&5))goto fail;
 start[-1]=0x12345678;end[0]=0xabcdef;
 valethon_entry_delay_seconds=0;
 if(invoke_entry_delay())goto fail;
 u64 color=mode==4?0xffffffffUL:mode==8?0xff00ff00UL:0xffff00ffUL;color|=color<<32;
 for(volatile u64 *p=start;p<end;p++)if(*p!=(((u64)p&0x10000)?0xff000000ff000000UL:color))goto fail;
 /* Cache-enabled path must paint and clean the same exact owned span. */
 for(volatile u64 *p=start;p<end;p++)*p=0x22222222;
 set_control(saved|4);if(invoke_entry_delay())goto fail;set_control(saved);
 for(volatile u64 *p=start;p<end;p++)if(*p!=(((u64)p&0x10000)?0xff000000ff000000UL:color))goto fail;
 /* Invalid frequency and out-of-range request skip the dwell. */
 valethon_entry_delay_seconds=8;set_frequency(0);if(invoke_entry_delay())goto fail;
 set_frequency(200000000);if(invoke_entry_delay())goto fail;set_frequency(freq);
 valethon_entry_delay_seconds=9;if(invoke_entry_delay())goto fail;
 valethon_entry_delay_seconds=8;u64 before=counter();if(invoke_entry_delay())goto fail;
 if(counter()-before<freq*8)goto fail;
 if(start[-1]!=0x12345678||end[0]!=0xabcdef)goto fail;
 if(mode==4)message("ENTRY_DELAY_EL1_SPAN_GATES_REGISTERS_8S_PASS\n");
 else if(mode==8)message("ENTRY_DELAY_EL2_SPAN_GATES_REGISTERS_8S_PASS\n");
 else message("ENTRY_DELAY_EL3_SPAN_GATES_REGISTERS_8S_PASS\n");
 return 0;
fail:message("ENTRY_DELAY_FAIL\n");return 1;
}
