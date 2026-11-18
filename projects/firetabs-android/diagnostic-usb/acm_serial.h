/* Fixed status frame only. All syscall access is injectable for RAM tests. */
#ifndef FIRETABS_ACM_SERIAL_H
#define FIRETABS_ACM_SERIAL_H
#include "acm_fs.h"
#define FT_SERIAL_IOCTL 29
#define FT_SERIAL_MKNODAT 33
#define FT_SERIAL_STATX 291
#define FT_SERIAL_NANOSLEEP 101
#define FT_SERIAL_NOCTTY 00000400
#define FT_SERIAL_NONBLOCK 00004000
#define FT_SERIAL_TCGETS 0x5401
#define FT_SERIAL_TCSETS 0x5402
#define FT_SERIAL_B9600 0x0000000d
#define FT_SERIAL_CS8 0x00000030
#define FT_SERIAL_CREAD 0x00000080
#define FT_SERIAL_CLOCAL 0x00000800
#define FT_SERIAL_AT_EMPTY_PATH 0x1000
#define FT_SERIAL_STATX_TYPE 0x00000001
#define FT_SERIAL_IFCHR 0020000
#define FT_SERIAL_IFMT 00170000
#define FT_SERIAL_VMIN 6
#define FT_SERIAL_VTIME 5
#define FT_SERIAL_NODE "/dev/firetabs-acm"
#define FT_SERIAL_PORT_PATH FT_ACM_ROOT "/functions/acm.usb0/port_num"
static const char ft_serial_frame[]="FIRETABS_ACM_STATUS_V1\nSOURCE_SETUP=complete\nHOST_RECEIPT=unverified\nEND\n";
struct ft_termios {unsigned int iflag,oflag,cflag,lflag;unsigned char line,cc[19];};
_Static_assert(sizeof(struct ft_termios)==36,"Pinned TCGETS/TCSETS layout");
struct ft_serial_state {long fd;int node_owned,restore_needed,primary,cleanup;unsigned long accepted;struct ft_termios original;};
static int ft_serial_number(const char *b,unsigned long n,unsigned long *pos,unsigned int max,unsigned int *out) {
 unsigned long i=*pos,start=i;unsigned int v=0;
 while(i<n&&b[i]>='0'&&b[i]<='9') {
  unsigned int d=(unsigned int)(b[i]-'0');if(d>max||v>(max-d)/10)return -22;
  v=v*10+d;i++;
 }
 if(i==start||(i-start>1&&b[start]=='0'))return -22;
 *pos=i;*out=v;return 0;
}
static int ft_serial_port(const char *b,unsigned long n,unsigned int *port) {
 unsigned long i=0;int r=ft_serial_number(b,n,&i,255,port);
 return r||i+1!=n||b[i]!='\n'?-22:0;
}
static int ft_serial_device(const char *b,unsigned long n,unsigned int *major,unsigned int *minor) {
 unsigned long i=0;int r=ft_serial_number(b,n,&i,4095,major);
 if(r||!*major||i>=n||b[i++]!=':')return -22;
 r=ft_serial_number(b,n,&i,1048575,minor);
 return r||i+1!=n||b[i]!='\n'?-22:0;
}
static int ft_serial_devpath(char *out,unsigned int port) {
 const char prefix[]="/sys/class/tty/ttyGS";unsigned long n=0;char digits[3];int count=0;
 if(port>255)return -22;
 for(;prefix[n];n++)out[n]=prefix[n];
 do{digits[count++]=(char)('0'+port%10);port/=10;}while(port);
 while(count)out[n++]=digits[--count];
 const char suffix[]="/dev";for(unsigned long i=0;i<sizeof(suffix);i++)out[n++]=suffix[i];
 return 0; /* Caller supplies at least32 bytes; max path length26 including NUL. */
}
static unsigned int ft_serial_u32(const unsigned char *p){return (unsigned int)p[0]|((unsigned int)p[1]<<8)|((unsigned int)p[2]<<16)|((unsigned int)p[3]<<24);}
static long ft_serial_ioctl(struct ft_acm_io *io,long fd,long request,void *arg) {
 long r=-4;for(int i=0;i<8&&r==-4;i++)r=ft_call(io,FT_SERIAL_IOCTL,fd,request,(long)arg,0,0,0);return r;
}
static int ft_serial_close(struct ft_acm_io *io,struct ft_serial_state *s) {
 int cleanup=0;
 if(s->fd>=0) {
  if(s->restore_needed) {
   long r=ft_serial_ioctl(io,s->fd,FT_SERIAL_TCSETS,&s->original);
   if(r<0)cleanup=(int)r;else s->restore_needed=0;
  }
  long r=ft_call(io,FT_NR_CLOSE,s->fd,0,0,0,0,0);s->fd=-1; /* Never retry Linux close. */
  if(r<0&&!cleanup)cleanup=(int)r;
 }
 if(s->node_owned) {
  long r=ft_call(io,FT_NR_UNLINKAT,FT_AT_FDCWD,(long)FT_SERIAL_NODE,0,0,0,0);
  if(r<0){if(!cleanup)cleanup=(int)r;}else s->node_owned=0;
 }
 s->cleanup=cleanup;return cleanup;
}
static int ft_serial_open_mode(struct ft_acm_io *io,int admitted,int owns_function,int duplex,struct ft_serial_state *s) {
 if(!io||!io->call||!s||(duplex!=0&&duplex!=1))return -22;
 if(admitted!=1||owns_function!=1)return -1;
 if(s->fd!=-1||s->node_owned||s->restore_needed||s->primary||s->cleanup||s->accepted)return -16;
 char buf[32],path[32];unsigned int port,major,minor;int ret=0;
 long n=ft_read_file(io,FT_SERIAL_PORT_PATH,buf,sizeof(buf));
 if(n<0)return (int)n;
 if(ft_serial_port(buf,(unsigned long)n,&port))return -22;
 ft_serial_devpath(path,port);
 n=ft_read_file(io,path,buf,sizeof(buf));if(n<0)return (int)n;
 if(ft_serial_device(buf,(unsigned long)n,&major,&minor))return -22;
 unsigned long encoded=(minor&0xffU)|((unsigned long)major<<8)|((unsigned long)(minor&~0xffU)<<12);
 long r=ft_call(io,FT_SERIAL_MKNODAT,FT_AT_FDCWD,(long)FT_SERIAL_NODE,FT_SERIAL_IFCHR|0600,(long)encoded,0,0);
 if(r<0)return (int)r; /* EEXIST is an error, never adopt an existing node. */
 s->node_owned=1;
 r=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)FT_SERIAL_NODE,(duplex?2:FT_O_WRONLY)|FT_SERIAL_NOCTTY|FT_SERIAL_NONBLOCK|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(r<0){ret=(int)r;goto finish;}s->fd=r;
 /* statx AT_EMPTY_PATH checks the opened fd, not a racy path lookup. */
 {unsigned long long aligned[32]={0};unsigned char *st=(unsigned char *)aligned;
  r=ft_call(io,FT_SERIAL_STATX,s->fd,(long)"",FT_SERIAL_AT_EMPTY_PATH,FT_SERIAL_STATX_TYPE,(long)st,0);
  if(r<0){ret=(int)r;goto finish;}
  unsigned int mode=(unsigned int)st[28]|((unsigned int)st[29]<<8);
  if(!(ft_serial_u32(st)&FT_SERIAL_STATX_TYPE)||(mode&FT_SERIAL_IFMT)!=FT_SERIAL_IFCHR||
   ft_serial_u32(st+128)!=major||ft_serial_u32(st+132)!=minor){ret=-19;goto finish;}
 }
 /* Recheck the owned function-to-port mapping before touching TTY settings. */
 {unsigned int check;
  n=ft_read_file(io,FT_SERIAL_PORT_PATH,buf,sizeof(buf));
  if(n<0){ret=(int)n;goto finish;}
  if(ft_serial_port(buf,(unsigned long)n,&check)||check!=port){ret=-19;goto finish;}
 }
 r=ft_serial_ioctl(io,s->fd,FT_SERIAL_TCGETS,&s->original);if(r<0){ret=(int)r;goto finish;}
 if(s->original.line!=0){ret=-19;goto finish;} /* Do not install/replace a line discipline. */
 {struct ft_termios raw={0,0,FT_SERIAL_B9600|FT_SERIAL_CS8|FT_SERIAL_CREAD|FT_SERIAL_CLOCAL,0,0,{0}};
  raw.cc[FT_SERIAL_VMIN]=1;raw.cc[FT_SERIAL_VTIME]=0;s->restore_needed=1;
  r=ft_serial_ioctl(io,s->fd,FT_SERIAL_TCSETS,&raw);if(r<0){ret=(int)r;goto finish;}
  struct ft_termios readback;
  r=ft_serial_ioctl(io,s->fd,FT_SERIAL_TCGETS,&readback);if(r<0){ret=(int)r;goto finish;}
  if(!ft_bytes((const char *)&raw,(const char *)&readback,sizeof(raw))){ret=-5;goto finish;}
 }
 return 0;
finish:
 s->primary=ret;
 {int cleanup=ft_serial_close(io,s);return ret?ret:cleanup;}
}
static inline int ft_serial_open_owned(struct ft_acm_io *io,int admitted,int owns_function,struct ft_serial_state *s) {
 return ft_serial_open_mode(io,admitted,owns_function,0,s);
}
static inline int ft_serial_open_duplex_owned(struct ft_acm_io *io,int admitted,int owns_function,struct ft_serial_state *s) {
 return ft_serial_open_mode(io,admitted,owns_function,1,s);
}
static int ft_serial_output(struct ft_acm_io *io,int admitted,int owns_function,struct ft_serial_state *s) {
 int ret=ft_serial_open_owned(io,admitted,owns_function,s);
 if(ret)return ret;
 long r=0;
 for(int attempts=0;attempts<128&&s->accepted<sizeof(ft_serial_frame)-1;attempts++) {
  unsigned long remaining=sizeof(ft_serial_frame)-1-s->accepted;
  r=ft_call(io,FT_NR_WRITE,s->fd,(long)(ft_serial_frame+s->accepted),remaining,0,0,0);
  if(r==-4)continue;
  if(r==-11) {
   const long delay[2]={0,10000000};long waited=ft_call(io,FT_SERIAL_NANOSLEEP,(long)delay,0,0,0,0,0);
   if(waited<0&&waited!=-4){ret=(int)waited;break;}continue;
  }
  if(r<=0){ret=r<0?(int)r:-5;break;}
  if((unsigned long)r>remaining){ret=-5;break;}s->accepted+=(unsigned long)r;
 }
 if(!ret&&s->accepted!=sizeof(ft_serial_frame)-1)ret=-110;
 s->primary=ret;
 {int cleanup=ft_serial_close(io,s);return ret?ret:cleanup;}
}
#endif
