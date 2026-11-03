/* Read-only Linux/AArch64 framebuffer metadata: two GET ioctls, no pixels. */
typedef unsigned int u32;typedef unsigned short u16;
struct fix {char id[16];unsigned long smem_start;u32 smem_len,type,type_aux,visual;u16 xpanstep,ypanstep,ywrapstep;u32 line_length;unsigned long mmio_start;u32 mmio_len,accel;u16 capabilities,reserved[2];};
struct bits {u32 offset,length,msb_right;};
struct var {u32 xres,yres,xvirtual,yvirtual,xoffset,yoffset,bpp,grayscale;struct bits red,green,blue,transp;u32 nonstd,activate,height,width,accel,pixclock,left,right,upper,lower,hsync,vsync,sync,vmode,rotate,colorspace,reserved[4];};
_Static_assert(sizeof(struct fix)==80&&sizeof(struct var)==160,"Framebuffer metadata ABI");
_Static_assert(__builtin_offsetof(struct fix,line_length)==48,"Framebuffer line-length ABI");
static long call(long nr,long a,long b,long c,long d){register long x0 __asm__("x0")=a;register long x1 __asm__("x1")=b;register long x2 __asm__("x2")=c;register long x3 __asm__("x3")=d;register long x8 __asm__("x8")=nr;__asm__ volatile("svc #0":"+r"(x0):"r"(x1),"r"(x2),"r"(x3),"r"(x8):"memory","cc");return x0;}
__attribute__((noreturn))void _start(void){struct {char magic[8];struct fix f;struct var v;} p={{'F','B','M','E','T','A','0','1'},{0},{0}};long status=2;long fd=call(56,-100,(long)"/dev/graphics/fb0",0100000|02000000,0);if(fd>=0){if(call(29,fd,0x4602,(long)&p.f,0)==0&&call(29,fd,0x4600,(long)&p.v,0)==0){if(call(64,1,(long)&p,sizeof(p),0)==sizeof(p))status=0;}call(57,fd,0,0,0);}call(93,status,0,0,0);for(;;){}}
