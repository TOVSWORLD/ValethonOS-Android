/* SPDX-License-Identifier: GPL-2.0-only
 * VM-only loader/memory/policy controls. Never a physical rendering pass.
 */
#define _GNU_SOURCE
#include <EGL/egl.h>
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <unistd.h>
static void value(const char *name,long result){printf("VM_GRAPHICS_%s=%+011ld\n",name,result);}
int main(void){
 setvbuf(stdout,NULL,_IONBF,0);setvbuf(stderr,NULL,_IONBF,0);
 char enforced[2]={0};int fd=open("/security/enforce",O_RDONLY|O_NOFOLLOW|O_CLOEXEC);ssize_t n=fd<0?-1:read(fd,enforced,2);if(fd>=0)close(fd);
 value("ENFORCE",n==1&&enforced[0]=='1'?0:-1);
 void *library=dlopen("/lib/libgallium-26.2.7.so",RTLD_NOW|RTLD_LOCAL);value("DRIVER_DLOPEN",library?0:-1);if(!library){const char *e=dlerror();if(e)printf("VM_GRAPHICS_LOAD_ERROR %s\n",e);}
 void *backend=dlopen("/lib/gbm/dri_gbm.so",RTLD_NOW|RTLD_LOCAL);value("GBM_DLOPEN",backend?0:-1);
 const char *extensions=eglQueryString(EGL_NO_DISPLAY,EGL_EXTENSIONS);value("EGL_CLIENT",extensions&&strstr(extensions,"EGL_EXT_platform_base")?0:-1);
 fd=memfd_create("graphics-vm",MFD_CLOEXEC);value("MEMFD",fd<0?-errno:0);
 void *memory=MAP_FAILED;
 if(fd>=0&&ftruncate(fd,4096)==0)memory=mmap(NULL,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
 if(memory!=MAP_FAILED){memcpy(memory,"GPU VM memory",14);value("MEMORY_RW",memcmp(memory,"GPU VM memory",14));errno=0;int r=mprotect(memory,4096,PROT_READ|PROT_EXEC);value("MEMORY_EXEC_DENIED",r<0?-errno:0);munmap(memory,4096);}
 else value("MEMORY_RW",-1);
 if(fd>=0)close(fd);
 errno=0;long child=syscall(SYS_clone,0,NULL,NULL,NULL,0);if(child==0)_exit(77);value("FORK_DENIED",child<0?-errno:0);
 fd=open("/dev/input/event0",O_WRONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC);value("INPUT_WRITE_DENIED",fd<0?-errno:0);if(fd>=0)close(fd);
 fd=open("/dev/firetabs-boot",O_WRONLY|O_NOFOLLOW|O_CLOEXEC);value("BLOCK_WRITE_DENIED",fd<0?-errno:0);if(fd>=0)close(fd);
 puts("VM_GRAPHICS_PROBE_DONE");for(;;)sleep(1);
}
