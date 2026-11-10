/* SPDX-License-Identifier: GPL-2.0-only
 * Native ARM64 load/unload only. No reboot/execute syscall or command exists.
 * bundle.h is generated from the exact privately retained bundle manifest.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include "bundle.h"
#ifndef __aarch64__
#error AArch64 target required
#endif
_Static_assert(sizeof(unsigned long)==8,"64-bit ABI required");
_Static_assert(__NR_kexec_load==104,"Reviewed syscall number required");
struct segment {void *buf; size_t bufsz; unsigned long mem; size_t memsz;};
static int loaded(void) {
 char b[3]={0};int f=open("/sys/kernel/kexec_loaded",O_RDONLY|O_CLOEXEC);
 if(f<0)return -1;
 ssize_t n=read(f,b,2);close(f);
 if(n!=2||b[1]!='\n'||(b[0]!='0'&&b[0]!='1'))return -1;
 return b[0]-'0';
}
int main(int argc,char **argv) {
 struct segment s[3]={{0}};cpu_set_t mask;int dir=-1,rc=1,err=0;
 if(argc!=3 || (strcmp(argv[1],"--load")&&strcmp(argv[1],"--unload"))) {
  fputs("usage: native-load --load|--unload BUNDLE_DIRECTORY\n",stderr);return 2;
 }
 if(geteuid()!=0){fputs("root required\n",stderr);return 2;}
 CPU_ZERO(&mask);CPU_SET(0,&mask);
 if(sched_setaffinity(0,sizeof(mask),&mask)){perror("CPU0 affinity");return 2;}
 if(!strcmp(argv[1],"--unload")) {
  if(loaded()!=1){fputs("expected loaded state\n",stderr);return 2;}
  rc=syscall(__NR_kexec_load,0UL,0UL,NULL,0xb70000UL);err=errno;
  if(rc||loaded()!=0){fprintf(stderr,"unload failed errno=%d\n",err);return 1;}
  puts("native_unload=complete");return 0;
 }
 if(loaded()!=0){fputs("refuse pre-existing or unknown load\n",stderr);return 2;}
 dir=open(argv[2],O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
 if(dir<0){perror("bundle directory");return 2;}
 for(unsigned i=0;i<3;i++) {
  struct stat st;int f=openat(dir,bundle[i].name,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
  if(f<0){perror("bundle open");goto done;}
  if(fstat(f,&st)||!S_ISREG(st.st_mode)||st.st_size!=(off_t)bundle[i].bytes){close(f);fputs("bundle size/type differs\n",stderr);goto done;}
  s[i].buf=malloc(bundle[i].bytes);s[i].bufsz=bundle[i].bytes;s[i].mem=bundle[i].address;s[i].memsz=bundle[i].memory_bytes;
  if(!s[i].buf){close(f);goto done;}
  size_t at=0;
  while(at<s[i].bufsz){ssize_t n=read(f,(char*)s[i].buf+at,s[i].bufsz-at);if(n<0&&errno==EINTR)continue;if(n<=0){close(f);goto done;}at+=(size_t)n;}
  char extra;ssize_t n=read(f,&extra,1);close(f);if(n!=0)goto done;
 }
 rc=syscall(__NR_kexec_load,(unsigned long)BUNDLE_ENTRY,3UL,s,0xb70000UL);err=errno;
 if(rc||loaded()!=1){fprintf(stderr,"native_load=failed errno=%d\n",err);rc=1;}else{puts("native_load=complete segments=3 execute=disabled");rc=0;}
 done:
 for(unsigned i=0;i<3;i++)free(s[i].buf);
 close(dir);return rc;
}
