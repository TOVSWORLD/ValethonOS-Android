/* SPDX-License-Identifier: GPL-2.0-only
 * Existing enforcing USB/display bootstrap, then immutable graphics ELF exec.
 */
#define VALETHON_DISPLAY_TEST 1
#define VALETHON_DISPLAY_ERRORS 1
#include "touch_probe.h"
#include "display_errors.h"
static int graphics_label_node(struct ft_acm_io *io,const char *path,unsigned int major,unsigned int minor,const char *context){
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)path,LL_O_PATH|FT_O_NOFOLLOW|FT_O_CLOEXEC);if(fd<0)return (int)fd;
 unsigned long long aligned[32]={0};unsigned char *st=(unsigned char *)aligned;
 long r=ft_call(io,FT_SERIAL_STATX,fd,(long)"",FT_SERIAL_AT_EMPTY_PATH,FT_SERIAL_STATX_TYPE,(long)st,0);
 unsigned int mode=(unsigned int)st[28]|((unsigned int)st[29]<<8);
 if(r>=0&&(!(ft_serial_u32(st)&FT_SERIAL_STATX_TYPE)||(mode&FT_SERIAL_IFMT)!=FT_SERIAL_IFCHR||ft_serial_u32(st+128)!=major||ft_serial_u32(st+132)!=minor))r=-19;
 long closed=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);if(r<0||closed<0)return r<0?(int)r:(int)closed;
 unsigned long n=0;while(context[n])n++;
 r=ft_call(io,LL_NR_LSETXATTR,(long)path,(long)"security.selinux",(long)context,n+1,0,0);if(r)return (int)r;
 unsigned char actual[128]={0};r=ft_call(io,LL_NR_LGETXATTR,(long)path,(long)"security.selinux",(long)actual,sizeof(actual),0,0);
 return r<0?(int)r:ll_context_equal(actual,r,context)?0:-13;
}
static int graphics_labels(struct ft_acm_io *io){
 int r=ll_label_archive(io);if(!r)r=tp_label(io);if(r)return r;
 for(unsigned int i=0;i<4;i++){
  char path[80];tp_path(path,"/dev/dri/card",i,"");r=graphics_label_node(io,path,226,i,"system_u:object_r:drm_display_t");if(r)return r;
  /* The render suffix is128..131, so construct it without tp_path's0..15 API. */
  char render[]="/dev/dri/renderD128";unsigned int value=128+i;render[17]=(char)('0'+value/10%10);render[18]=(char)('0'+value%10);
  r=graphics_label_node(io,render,226,value,"system_u:object_r:drm_render_t");if(r)return r;
 }
 r=graphics_label_node(io,"/dev/null",1,3,"system_u:object_r:graphics_null_t");if(r)return r;
 return graphics_label_node(io,"/dev/urandom",1,9,"system_u:object_r:graphics_random_t");
}
__attribute__((noreturn))static void graphics_exec(struct ll_context *ctx){
 struct ft_acm_io *io=ctx->io;
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/console",FT_O_WRONLY|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd>=0){
  long r=ft_call(io,25,fd,2,0,0,0,0); /* fcntl F_SETFD: console survives exec. */
  if(!r)for(int i=0;i<3;i++)if(fd!=i){r=ft_call(io,24,fd,i,0,0,0,0);if(r<0)break;}
  if(r>=0){
   const char *const argv[]={"/graphics",0};
   const char *const env[]={"LD_LIBRARY_PATH=/lib","LIBGL_DRIVERS_PATH=/lib/dri","GBM_BACKENDS_PATH=/lib/gbm","GALLIUM_THREAD=0","mesa_glthread=false","MESA_SHADER_CACHE_DISABLE=1","LC_ALL=C",0};
   (void)ft_call(io,221,(long)argv[0],(long)argv,(long)env,0,0,0);
  }
 }
 const char text[]="\033[41m\033[2J\033[HVALETHON GRAPHICS EXEC STOPPED\nLeave Power untouched.\033[0m\n";
 if(fd>=0)(void)tp_write(io,fd,text,sizeof(text)-1);
 for(;;){const long wait[2]={1,0};ft_call(io,FT_SERIAL_NANOSLEEP,(long)wait,0,0,0,0,0);}
}
static int graphics_send(void *opaque,const unsigned char *data,unsigned long n){
 (void)ll_send(opaque,data,n);graphics_exec(opaque);
}
#define ll_label_archive graphics_labels
#define ll_send graphics_send
#include "storage_init.c"
