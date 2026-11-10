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
static int scenario,linked,bound,unbinds,binds,deletes;
static int mock_open(const char*,int,...);
static ssize_t mock_read(int,void*,size_t);
static ssize_t mock_write(int,const void*,size_t);
static int mock_close(int);
static int mock_lstat(const char*,struct stat*);
static char*mock_realpath(const char*,char*);
static int mock_unlink(const char*);
#define open mock_open
#define read mock_read
#define write mock_write
#define close mock_close
#define lstat mock_lstat
#define realpath mock_realpath
#define unlink mock_unlink
#define main acm_trial_main
#include "acm_trial.c"
#undef main
static int mock_open(const char*p,int flags,...){(void)flags;if(!strcmp(p,G "/UDC"))return 10;if(!strcmp(p,G "/functions/acm.gs0/port_num"))return 11;abort();}
static ssize_t mock_read(int f,void*b,size_t n){const char*s=f==11?(scenario==12?"1\n":"0\n"):(scenario==5?"foreign-udc\n":(bound?"musb-hdrc\n":"\n"));size_t l=strlen(s);if(l>n)abort();memcpy(b,s,l);return (ssize_t)l;}
static ssize_t mock_write(int f,const void*b,size_t n){if(f!=10)abort();if(n==1&&!memcmp(b,"\n",1)){unbinds++;if(scenario==7){errno=EIO;return -1;}bound=0;}else if(n==10&&!memcmp(b,"musb-hdrc\n",10)){binds++;if(scenario==8){errno=EIO;return -1;}bound=1;}else abort();return n;}
static int mock_close(int f){(void)f;return 0;}
static int mock_lstat(const char*p,struct stat*s){if(strcmp(p,G "/configs/b.1/f2"))abort();if(linked){memset(s,0,sizeof(*s));s->st_mode=S_IFLNK;return 0;}errno=ENOENT;return -1;}
static char*mock_realpath(const char*p,char*b){const char*r=NULL;if(!strcmp(p,G "/configs/b.1/f1"))r=scenario==4?"/foreign":G "/functions/ffs.adb";else if(!strcmp(p,G "/configs/b.1/f2")&&linked)r=scenario==3?"/foreign":G "/functions/acm.gs0";if(!r){errno=ENOENT;return NULL;}strcpy(b,r);return b;}
static int mock_unlink(const char*p){if(strcmp(p,G "/configs/b.1/f2")||!linked||bound)abort();deletes++;if(scenario==6){errno=EACCES;return -1;}linked=0;return 0;}
int main(int argc,char**argv){if(argc!=2)return 2;scenario=atoi(argv[1]);bound=!(scenario==2||scenario==10);linked=scenario!=0&&scenario!=10&&scenario!=12;int result;
 if(scenario==11||scenario==12){result=original();if(result)return 90;puts("control=passed");return 0;}
 int owned=scenario!=0&&scenario!=9&&scenario!=10;
 result=restore(owned);
 if(scenario==0){if(result||unbinds||binds||deletes)return 91;}
 else if(scenario==1){if(result||unbinds!=1||binds!=1||deletes!=1||linked||!bound)return 92;}
 else if(scenario==2){if(result||unbinds||binds!=1||deletes!=1)return 93;}
 else if(scenario==3||scenario==4||scenario==5||scenario==9){if(!result||unbinds||binds||deletes)return 94;}
 else if(scenario==6){if(!result||unbinds!=1||deletes!=1||binds||!linked)return 95;}
 else if(scenario==7){if(!result||unbinds!=1||deletes||binds)return 96;}
 else if(scenario==8){if(!result||unbinds!=1||deletes!=1||binds!=1||linked)return 97;}
 else if(scenario==10){if(result||unbinds||deletes||binds!=1)return 98;}
 else return 99;
 puts("control=passed");return 0;
}
