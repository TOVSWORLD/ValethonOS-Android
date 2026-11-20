/* SPDX-License-Identifier: GPL-2.0-only
 * Bounded pre-Android capture. No block-device, reset, policy or gadget writes.
 * Builtin g_serial owns USB until Android's early-init releases it explicitly.
 */
#define _GNU_SOURCE
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
static long long now_ms(void) {
 struct timespec t; if(clock_gettime(CLOCK_MONOTONIC,&t))return -1;
 return (long long)t.tv_sec*1000+t.tv_nsec/1000000;
}
static void marker(int fd,const char *s) { if(fd>=0)(void)write(fd,s,strlen(s)); }
static void bounded_file(int serial,const char *path,long long deadline) {
 int fd=open(path,O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);if(fd<0)return;
 char b[4096];size_t total=0;
 while(serial>=0 && total<65536 && now_ms()<deadline) {
  ssize_t n=read(fd,b,sizeof(b));if(n<=0)break;total+=(size_t)n;
  for(ssize_t at=0;at<n && now_ms()<deadline;) {
   ssize_t w=write(serial,b+at,(size_t)(n-at));
   if(w>0)at+=w;
   else if(errno==EAGAIN || errno==EINTR) { struct timespec t={0,2000000};nanosleep(&t,NULL); }
   else { close(fd);return; }
  }
 } close(fd);
}
int main(int argc,char **argv,char **envp) {
 (void)argc;(void)argv;
 int proc=mount("proc","/proc","proc",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL)==0;
 int sys=mount("sysfs","/sys","sysfs",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL)==0;
 int made=mknod("/dev/kmsg",S_IFCHR|0600,makedev(1,11))==0;
 int log=open("/dev/kmsg",O_WRONLY|O_CLOEXEC|O_NOFOLLOW);
 marker(log,"<6>VALETHON PREINIT: entered before Android /init\n");
 int readfd=open("/dev/kmsg",O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
 int serial=open("/dev/ttyGS0",O_WRONLY|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
 /* devtmpfs is deliberately not mounted: Android first-stage owns /dev setup. */
 int made_serial=0;
 if(serial<0 && sys) {
  FILE *f=fopen("/sys/class/tty/ttyGS0/dev","r");unsigned major,minor;
  if(f) { if(fscanf(f,"%u:%u",&major,&minor)==2 && major>0 && major<4096 && minor<4096) {
   made_serial=mknod("/dev/ttyGS0",S_IFCHR|0600,makedev(major,minor))==0;
   serial=open("/dev/ttyGS0",O_WRONLY|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
  } fclose(f); }
 }
 /* Pstore contains PREVIOUS boot records, never evidence of this boot by itself.
  * A later collection-only boot can send these without executing Android again.
  */
 int readout=0;FILE *cmd=fopen("/proc/cmdline","r");
 if(cmd) { char line[4096];if(fgets(line,sizeof(line),cmd) && strstr(line," valethon.capture_readout=1"))readout=1;fclose(cmd); }
 int ps=sys && mount("pstore","/sys/fs/pstore","pstore",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL)==0;
 long long retained_start=now_ms();
 if(ps && retained_start>=0 && serial>=0) {
  marker(log,"<6>VALETHON PREINIT: previous-boot pstore follows; require previous trial identity\n");
  bounded_file(serial,"/sys/fs/pstore/console-ramoops-0",retained_start+8000);
  for(int i=0;i<13 && now_ms()<retained_start+8000;i++) {
   char path[96];snprintf(path,sizeof(path),"/sys/fs/pstore/dmesg-ramoops-%d",i);
   bounded_file(serial,path,retained_start+8000);
  }
 }
 if(ps)umount("/sys/fs/pstore");
 if(readout) { marker(log,"<6>VALETHON PREINIT: collection-only mode; Android /init not executed\n");for(;;)pause(); }
 /* Best effort only. USB absence cannot prevent Android init from running. */
 long long start=now_ms();size_t total=0;char buf[8192];
 while(start>=0 && now_ms()>=start && now_ms()-start<8000 && total<1048576) {
  ssize_t n=readfd>=0?read(readfd,buf,sizeof(buf)):-1;
  if(n>0) {
   total+=(size_t)n;
   if(serial>=0) { ssize_t at=0;while(at<n) { ssize_t w=write(serial,buf+at,(size_t)(n-at));if(w<=0)break;at+=w; } }
  } else if(n<0 && errno==EPIPE) { /* ring overrun: preserve progress, never claim completeness */
   marker(log,"<4>VALETHON PREINIT: kmsg ring overrun\n");
  } else { struct timespec pause={0,20000000};nanosleep(&pause,NULL); }
 }
 marker(log,"<6>VALETHON PREINIT: executing original Android /init; USB console remains until early-init\n");
 if(serial>=0)close(serial);if(readfd>=0)close(readfd);if(log>=0)close(log);
 if(made_serial)unlink("/dev/ttyGS0");if(made)unlink("/dev/kmsg");
 if(sys)umount("/sys");if(proc)umount("/proc");
 char *args[]={"/init",NULL};execve(args[0],args,envp);
 /* PID1 must not exit; kernel console/pstore retain the exact exec errno. */
 int error=errno;dprintf(2,"VALETHON PREINIT: exec /init failed errno=%d\n",error);
 for(;;)pause();
}
