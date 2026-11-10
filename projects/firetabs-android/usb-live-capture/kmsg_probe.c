/* SPDX-License-Identifier: GPL-2.0-only */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
static long long ms(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return -1;return (long long)t.tv_sec*1000+t.tv_nsec/1000000;}
int main(int argc,char**argv){
 char expected[160],b[8192];int fd;long long end;
 if(argc!=2||strlen(argv[1])!=32||strspn(argv[1],"0123456789abcdef")!=32)return 2;
 snprintf(expected,sizeof(expected),"KXUSB trial=%s usb_capture_probe=1\n",argv[1]);
 fd=open("/dev/kmsg",O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
 if(fd<0||lseek(fd,0,SEEK_END)<0)return 3;
 printf("KXUSB_READY %s\n",argv[1]);fflush(stdout);end=ms()+20000;
 for(unsigned attempts=0;attempts<65536&&ms()<end;attempts++){
  ssize_t n=read(fd,b,sizeof(b)-1);
  if(n<0){if(errno==EINTR||errno==EPIPE)continue;if(errno==EAGAIN){struct pollfd p={fd,POLLIN,0};if(poll(&p,1,100)<0&&errno!=EINTR)break;continue;}break;}
  if(n<=0)break;
  b[n]=0;
  char*message=strchr(b,';');
  if(message&&!strcmp(message+1,expected)){
   if(fwrite(b,1,n,stdout)!=(size_t)n||fflush(stdout)){close(fd);return 5;}close(fd);return 0;
  }
 }
 close(fd);return 4;
}
