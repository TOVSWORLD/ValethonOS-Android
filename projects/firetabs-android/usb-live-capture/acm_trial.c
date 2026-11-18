/* SPDX-License-Identifier: GPL-2.0-only
 * One temporary ACM+ADB configuration; restore ADB-only without host commands.
 * No USB descriptors, properties, boot images or storage endpoints are changed.
 */
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
#define G "/config/usb_gadget/g1"
static int receipt=-1;
static void note(const char*s,int error){dprintf(receipt,"%s errno=%d\n",s,error);fsync(receipt);}
static int read_text(const char*p,char*b,size_t n){int f=open(p,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(f<0)return -1;ssize_t r=read(f,b,n-1);int err=errno;close(f);errno=err;if(r<=0||(size_t)r>=n-1)return -1;b[r]=0;while(r&&b[r-1]=='\n')b[--r]=0;return 0;}
static int store(const char*p,const char*s){int f=open(p,O_WRONLY|O_CLOEXEC|O_NOFOLLOW);if(f<0)return -1;size_t n=strlen(s);ssize_t r=write(f,s,n);int err=errno;int c=close(f);if(r!=(ssize_t)n||c){errno=r<0?err:EIO;return -1;}return 0;}
static int resolves(const char*p,const char*expected){char b[PATH_MAX];return realpath(p,b)&&!strcmp(b,expected);}
static int original(void){char b[64];struct stat s;
 if(read_text(G "/UDC",b,sizeof(b))||strcmp(b,"musb-hdrc"))return 0;
 if(!resolves(G "/configs/b.1/f1",G "/functions/ffs.adb"))return 0;
 if(lstat(G "/configs/b.1/f2",&s)==0||errno!=ENOENT)return 0;
 return !read_text(G "/functions/acm.gs0/port_num",b,sizeof(b))&&!strcmp(b,"0");
}
static int restore(int owned){char b[64];
 if(read_text(G "/UDC",b,sizeof(b))||(*b&&strcmp(b,"musb-hdrc")))return -1;
 if(!resolves(G "/configs/b.1/f1",G "/functions/ffs.adb"))return -1;
 if(owned){
  if(!resolves(G "/configs/b.1/f2",G "/functions/acm.gs0"))return -1;
  if(*b&&store(G "/UDC","\n"))return -1;
  if(unlink(G "/configs/b.1/f2"))return -1;
 }else{struct stat s;if(lstat(G "/configs/b.1/f2",&s)==0||errno!=ENOENT)return -1;}
 if(read_text(G "/UDC",b,sizeof(b)))return -1;
 if(!*b&&store(G "/UDC","musb-hdrc\n"))return -1;
 return original()?0:-1;
}
static long long milliseconds(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return -1;return (long long)t.tv_sec*1000+t.tv_nsec/1000000;}
static int kernel_frame(const char*nonce,char*line,size_t capacity){
 char expected[128],payload[140],record[8192];int reader=-1,writer=-1,result=-1;
 snprintf(expected,sizeof(expected),"KXUSB_ACM trial=%s capture_probe=1\n",nonce);
 snprintf(payload,sizeof(payload),"<6>%s",expected);
 reader=open("/dev/kmsg",O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
 if(reader<0||lseek(reader,0,SEEK_END)<0)goto done;
 writer=open("/dev/kmsg",O_WRONLY|O_CLOEXEC|O_NOFOLLOW);
 if(writer<0)goto done;
 note("kernel_marker_write_intent",0);
 if(write(writer,payload,strlen(payload))!=(ssize_t)strlen(payload))goto done;
 close(writer);writer=-1;
 long long end=milliseconds()+2000;
 for(unsigned attempts=0;attempts<4096&&milliseconds()<end;attempts++){
  ssize_t n=read(reader,record,sizeof(record)-1);
  if(n<0){if(errno==EINTR||errno==EPIPE)continue;if(errno==EAGAIN){struct timespec pause={0,1000000};nanosleep(&pause,NULL);continue;}break;}
  if(n<=0)break;
  record[n]=0;char*message=strchr(record,';');
  if(message&&!strcmp(message+1,expected)&&strlen(message+1)<capacity){memcpy(line,message+1,strlen(message+1)+1);result=0;break;}
 }
 done:if(reader>=0)close(reader);if(writer>=0)close(writer);return result;
}
static void trial(const char*nonce){int owned=0,tty=-1,changed=0;char line[128],dev[64];struct stat st;unsigned maj,min;struct termios saved,t;int settings=0;
 struct timespec settle={2,0};nanosleep(&settle,NULL);
 if(!original()){note("source_changed_refuse",0);goto done;}
 note("source_verified",0);
 if(kernel_frame(nonce,line,sizeof(line))){note("kernel_capture_failed",errno);goto done;}
 note("kernel_record_captured",0);changed=1;note("unbind_intent",0);
 if(store(G "/UDC","\n")){note("unbind_failed",errno);goto cleanup;}
 note("unbind_complete",0);
 if(symlink(G "/functions/acm.gs0",G "/configs/b.1/f2")){note("link_failed",errno);goto cleanup;}owned=1;
 if(store(G "/UDC","musb-hdrc\n")){note("bind_failed",errno);goto cleanup;}
 note("acm_adb_bound",0);
 tty=open("/dev/ttyGS0",O_RDWR|O_NONBLOCK|O_NOCTTY|O_NOFOLLOW|O_CLOEXEC);
 if(tty<0){note("tty_open_failed",errno);goto cleanup;}
 if(read_text("/sys/class/tty/ttyGS0/dev",dev,sizeof(dev))||sscanf(dev,"%u:%u",&maj,&min)!=2||fstat(tty,&st)||!S_ISCHR(st.st_mode)||st.st_rdev!=makedev(maj,min)){note("tty_identity_failed",0);goto cleanup;}
 if(tcgetattr(tty,&saved)){note("tty_getattr_failed",errno);goto cleanup;}
 t=saved;cfmakeraw(&t);t.c_cflag|=CREAD|CLOCAL;t.c_cflag&=~(HUPCL|CRTSCTS);cfsetispeed(&t,B9600);cfsetospeed(&t,B9600);settings=1;
 if(tcsetattr(tty,TCSANOW,&t)){note("tty_settings_failed",errno);goto cleanup;}
 long long end=milliseconds()+30000;unsigned accepted=0;size_t offset=0,len=strlen(line);
 for(unsigned attempts=0;attempts<300&&milliseconds()<end;attempts++){
  ssize_t n=write(tty,line+offset,len-offset);
  if(n>0){offset+=(size_t)n;if(offset==len){accepted++;offset=0;}}
  else if(n<0&&errno!=EAGAIN&&errno!=EINTR){note("serial_write_failed",errno);break;}
  struct timespec pause={0,100000000};nanosleep(&pause,NULL);
 }
 note("frames_accepted_not_host_proof",(int)accepted);
 cleanup:
 if(changed){note("restore_intent",0);int status=restore(owned);note(status?"restore_failed":"restore_verified",status?errno:0);}
 if(tty>=0){if(settings&&tcsetattr(tty,TCSANOW,&saved))note("tty_restore_failed",errno);if(close(tty))note("tty_close_failed",errno);}
 done:note("finished",0);close(receipt);_exit(0);
}
int main(int argc,char**argv){char path[160];
 if(argc!=2||strlen(argv[1])!=32||strspn(argv[1],"0123456789abcdef")!=32||geteuid())return 2;
 if(!original())return 3;
 snprintf(path,sizeof(path),"/dev/kxusb-acm-%s/receipt",argv[1]);receipt=open(path,O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0600);if(receipt<0)return 4;
 note("prepared",0);pid_t child=fork();if(child<0)return 5;
 if(child){printf("USB_ACM_STARTED\n");close(receipt);return 0;}
 if(setsid()<0)_exit(6);
 child=fork();if(child<0)_exit(7);if(child)_exit(0);
 close(0);close(1);close(2);trial(argv[1]);return 0;
}
