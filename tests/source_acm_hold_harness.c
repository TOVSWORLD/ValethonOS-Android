/* Executes the generated helper's actual hold/restore flow against RAM adapters. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>
#include <setjmp.h>
static int scenario,bound=1,linked,unbinds,binds,deletes;
static long long fake_ms;
static jmp_buf done;
static const char nonce[]="11111111111111111111111111111111";
static int ram_open(const char*p,int flags,...){
 (void)flags;
 if(strstr(p,"handoff-intent")){if(scenario==1){errno=ENOENT;return -1;}return 12;}
 if(strstr(p,"/UDC"))return 10;
 if(strstr(p,"port_num"))return 11;
 abort();
}
static ssize_t ram_read(int f,void*b,size_t n){
 const char*s=f==12?(scenario==2?"22222222222222222222222222222222":nonce):f==11?"0\n":bound?"musb-hdrc\n":"\n";
 size_t len=strlen(s);if(len>n)abort();memcpy(b,s,len);return len;
}
static ssize_t ram_write(int f,const void*b,size_t n){
 if(f!=10)abort();
 if(n==1&&!memcmp(b,"\n",1)){bound=0;unbinds++;}
 else if(n==10&&!memcmp(b,"musb-hdrc\n",10)){bound=1;binds++;}
 else abort();
 return n;
}
static int ram_close(int f){(void)f;return 0;}
static int ram_lstat(const char*p,struct stat*s){(void)p;if(linked){memset(s,0,sizeof(*s));s->st_mode=S_IFLNK;return 0;}errno=ENOENT;return -1;}
static char*ram_realpath(const char*p,char*b){
 const char*r=strstr(p,"/f1")?(scenario==3?"/foreign":"/config/usb_gadget/g1/functions/ffs.adb"):linked?"/config/usb_gadget/g1/functions/acm.gs0":NULL;
 if(!r)return NULL;
 strcpy(b,r);return b;
}
static int ram_link(const char*a,const char*b){(void)a;(void)b;if(bound||linked)abort();linked=1;return 0;}
static int ram_unlink(const char*p){(void)p;if(bound||!linked)abort();linked=0;deletes++;return 0;}
static int ram_clock(clockid_t c,struct timespec*t){(void)c;t->tv_sec=fake_ms/1000;t->tv_nsec=(fake_ms%1000)*1000000;return 0;}
static int ram_sleep(const struct timespec*t,struct timespec*r){(void)r;fake_ms+=t->tv_sec*1000+t->tv_nsec/1000000;return 0;}
static void ram_exit(int status){if(status)abort();longjmp(done,1);}
#define open ram_open
#define read ram_read
#define write ram_write
#define close ram_close
#define lstat ram_lstat
#define realpath ram_realpath
#define symlink ram_link
#define unlink ram_unlink
#define clock_gettime ram_clock
#define nanosleep ram_sleep
#define _exit ram_exit
#define main helper_main
#include "source-acm-hold.c"
#undef main
int main(int argc,char**argv){
 if(argc!=2)return 2;
 scenario=atoi(argv[1]);
 if(!setjmp(done))trial(nonce);
 if(scenario==0){if(unbinds!=1||binds!=1||deletes||!linked||!bound)return 3;}
 else if(scenario==1||scenario==2){if(unbinds!=2||binds!=2||deletes!=1||linked||!bound)return 4;}
 else if(scenario==3){if(unbinds||binds||deletes||linked)return 5;}
 else return 6;
 puts("hold_control=passed");return 0;
}
