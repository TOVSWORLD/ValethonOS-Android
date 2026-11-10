#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#undef __NR_kexec_load
#define __NR_kexec_load 104
#define __aarch64__ 1
static int scenario,state,calls;
static int fake_open(const char*,int,...);
static int fake_openat(int,const char*,int,...);
static int fake_fstat(int,struct stat*);
static ssize_t fake_read(int,void*,size_t);
static int fake_close(int);
static uid_t fake_geteuid(void);
static int fake_affinity(pid_t,size_t,const cpu_set_t*);
static long fake_syscall(long,...);
#define open fake_open
#define openat fake_openat
#define fstat fake_fstat
#define read fake_read
#define close fake_close
#define geteuid fake_geteuid
#define sched_setaffinity fake_affinity
#define syscall fake_syscall
#define main client_main
#include "load_client.c"
#undef main
static int fake_open(const char*p,int flags,...){(void)flags;return strstr(p,"kexec_loaded")?10:20;}
static int fake_openat(int d,const char*p,int flags,...){(void)d;(void)flags;if(scenario==4)return -1;for(int i=0;i<3;i++)if(!strcmp(p,bundle[i].name))return 21+i;return -1;}
static int fake_fstat(int f,struct stat*s){memset(s,0,sizeof(*s));s->st_mode=S_IFREG;s->st_size=bundle[f-21].bytes+(scenario==5);return 0;}
static ssize_t fake_read(int f,void*b,size_t n){static size_t at[3];if(f==10){memcpy(b,state?"1\n":"0\n",2);return 2;}int i=f-21;if(scenario==6)return 0;if(at[i]==bundle[i].bytes)return 0;memset(b,0,n);at[i]+=n;return n;}
static int fake_close(int f){(void)f;return 0;}
static uid_t fake_geteuid(void){return scenario==2?2000:0;}
static int fake_affinity(pid_t p,size_t n,const cpu_set_t*m){(void)p;if(n!=sizeof(*m)||!CPU_ISSET(0,m)||CPU_COUNT(m)!=1)abort();return scenario==3?-1:0;}
static long fake_syscall(long number,...){
 calls++;va_list ap;va_start(ap,number);unsigned long entry=va_arg(ap,unsigned long),nr=va_arg(ap,unsigned long);struct segment*s=va_arg(ap,struct segment*);unsigned long flags=va_arg(ap,unsigned long);va_end(ap);
 if(number!=104||flags!=0xb70000UL)abort();
 if(nr){if(nr!=3||entry!=BUNDLE_ENTRY)abort();for(int i=0;i<3;i++)if(s[i].mem!=bundle[i].address||s[i].bufsz!=bundle[i].bytes||s[i].memsz!=bundle[i].memory_bytes)abort();if(scenario==7){errno=5;return -1;}state=scenario==8?0:1;}
 else {if(entry||s)abort();if(scenario==10){errno=5;return -1;}state=0;}
 return 0;
}
int main(int argc,char**argv){if(argc!=2)return 99;scenario=atoi(argv[1]);state=(scenario==1||scenario==9||scenario==10);char*a[]={"native-load",scenario==9||scenario==10?"--unload":"--load","/bundle",NULL};if(scenario==11)a[1]="--execute";int v=client_main(3,a);int expected=(scenario==0||scenario==9)?0:((scenario==1||scenario==2||scenario==3||scenario==11)?2:1);int wantcalls=(scenario==0||scenario==7||scenario==8||scenario==9||scenario==10)?1:0;if(v!=expected||calls!=wantcalls)return 98;puts("control=passed");return 0;}
