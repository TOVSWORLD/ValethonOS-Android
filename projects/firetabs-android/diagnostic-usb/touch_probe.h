/* Standalone visual touch grid. Read-only evdev; no ioctl, event injection,
 * storage, network, privilege transition or reset operation. */
#ifndef FIRETABS_TOUCH_PROBE_H
#define FIRETABS_TOUCH_PROBE_H
#include "display_status.h"
#include "lab_labels.h"
#define TP_SLOTS 16
struct tp_slot {int x,y;unsigned int active,valid;};
struct tp_state {struct tp_slot slots[TP_SLOTS];unsigned int slot,visited,frames;int failed;};
struct tp_event {long seconds,microseconds;unsigned short type,code;int value;};
_Static_assert(sizeof(struct tp_event)==24,"AArch64 evdev ABI required");
static inline void tp_feed(struct tp_state *s,const struct tp_event *e){
 if(s->failed)return;
 if(e->type==0&&e->code==3){s->failed=-75;return;} /* SYN_DROPPED: no fabricated resync. */
 if(e->type==3){
  if(e->code==0x2f){if(e->value<0||e->value>=TP_SLOTS){s->failed=-22;return;}s->slot=(unsigned int)e->value;return;}
  struct tp_slot *p=&s->slots[s->slot];
  if(e->code==0x39){p->active=e->value>=0;p->valid=0;return;}
  if(e->code==0x35||e->code==0x36){
   int limit=e->code==0x35?800:1280;
   if(e->value<0||e->value>limit){s->failed=-34;return;}
   if(e->code==0x35){p->x=e->value==800?799:e->value;p->valid|=1;}
   else {p->y=e->value==1280?1279:e->value;p->valid|=2;}
  }
 }
 if(e->type==0&&e->code==0){
  for(unsigned int i=0;i<TP_SLOTS;i++)if(s->slots[i].active&&s->slots[i].valid==3){
   unsigned int cell=(unsigned int)(s->slots[i].y*3/1280)*3+(unsigned int)(s->slots[i].x*3/800);
   s->visited|=1U<<cell;
  }
  s->frames++;
 }
}
static inline void tp_path(char out[80],const char *prefix,unsigned int n,const char *suffix){
 unsigned int at=0;while(*prefix)out[at++]=*prefix++;
 if(n>=10)out[at++]='1';out[at++]=(char)('0'+n%10);
 while(*suffix)out[at++]=*suffix++;out[at]=0;
}
static inline int tp_label(struct ft_acm_io *io){
 const char context[]="system_u:object_r:input_dev_t";
 for(unsigned int i=0;i<TP_SLOTS;i++){
  char path[80];tp_path(path,"/dev/input/event",i,"");
  long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)path,LL_O_PATH|FT_O_NOFOLLOW|FT_O_CLOEXEC);
  if(fd<0)return (int)fd;
  unsigned long long aligned[32]={0};unsigned char *st=(unsigned char *)aligned;
  long r=ft_call(io,FT_SERIAL_STATX,fd,(long)"",FT_SERIAL_AT_EMPTY_PATH,FT_SERIAL_STATX_TYPE,(long)st,0);
  unsigned int mode=(unsigned int)st[28]|((unsigned int)st[29]<<8);
  if(r>=0&&(!(ft_serial_u32(st)&FT_SERIAL_STATX_TYPE)||(mode&FT_SERIAL_IFMT)!=FT_SERIAL_IFCHR||ft_serial_u32(st+128)!=13||ft_serial_u32(st+132)!=64+i))r=-19;
  long closed=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);if(r<0||closed<0)return r<0?(int)r:(int)closed;
  r=ft_call(io,LL_NR_LSETXATTR,(long)path,(long)"security.selinux",(long)context,sizeof(context),0,0);if(r)return (int)r;
  unsigned char actual[128]={0};r=ft_call(io,LL_NR_LGETXATTR,(long)path,(long)"security.selinux",(long)actual,sizeof(actual),0,0);
  if(r<0||!ll_context_equal(actual,r,context))return r<0?(int)r:-13;
 }
 return 0;
}
static inline int tp_write(struct ft_acm_io *io,long fd,const char *text,unsigned long n){
 unsigned long at=0;
 for(unsigned int tries=0;tries<256&&at<n;tries++){long r=ft_call(io,FT_NR_WRITE,fd,(long)(text+at),n-at,0,0,0);if(r==-4)continue;if(r<=0||r>(long)(n-at))return r<0?(int)r:-5;at+=(unsigned long)r;}
 return at==n?0:-110;
}
static inline int tp_draw(struct ft_acm_io *io,unsigned int visited,int error){
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/console",FT_O_WRONLY|FT_SERIAL_NONBLOCK|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd<0)return (int)fd;
 const char title[]="\033[2J\033[HVALETHON TOUCH TEST\nTap each large BLUE panel. A touched panel turns GREEN.\n";
 int result=tp_write(io,fd,title,sizeof(title)-1);
 for(unsigned int cell=0;!result&&cell<9;cell++)for(unsigned int row=0;!result&&row<20;row++){
  char line[64];unsigned int at=0,r=8+(cell/3)*24+row,c=5+(cell%3)*33;
  line[at++]='\033';line[at++]='[';line[at++]=(char)('0'+r/10);line[at++]=(char)('0'+r%10);line[at++]=';';line[at++]=(char)('0'+c/10);line[at++]=(char)('0'+c%10);line[at++]='H';
  const char *color=error?"\033[41m":visited&(1U<<cell)?"\033[42m":"\033[44m";
  while(*color)line[at++]=*color++;
  for(unsigned int x=0;x<28;x++)line[at++]=' ';
  line[at++]='\033';line[at++]='[';line[at++]='0';line[at++]='m';result=tp_write(io,fd,line,at);
 }
 if(!result){const char *message=error?"\033[3;1HINPUT UNAVAILABLE OR INVALID - TEST NOT PASSED":visited==511?"\033[3;1HALL NINE TARGETS REACHED":"\033[3;1HWaiting for touch; keep Power untouched";unsigned long n=0;while(message[n])n++;result=tp_write(io,fd,message,n);}
 long closed=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);return result?result:closed<0?(int)closed:0;
}
static inline int tp_run(struct ll_context *ctx){
 unsigned long now=ll_now(ctx);if(!now||now>~0UL-80000)return -110;ctx->deadline_ms=now+80000;
 long input=-1;
 for(unsigned int retry=0;retry<500&&ll_deadline(ctx)&&input<0;retry++){
  for(unsigned int i=0;i<TP_SLOTS;i++){
   char path[80],name[80];tp_path(path,"/sys/class/input/event",i,"/device/name");
   long n=ft_read_file(ctx->io,path,name,sizeof(name)-1);
   if(n<=0||n>=(long)sizeof(name))continue;name[n]=0;
   if(!ft_same(name,"Goodix Capacitive TouchScreen\n"))continue;
   tp_path(path,"/dev/input/event",i,"");input=ft_retry(ctx->io,FT_NR_OPENAT,FT_AT_FDCWD,(long)path,FT_SERIAL_NONBLOCK|FT_O_NOFOLLOW|FT_O_CLOEXEC);break;
  }
  if(input<0){int pause=ll_pause(ctx);if(pause)return pause;}
 }
 if(input<0){(void)tp_draw(ctx->io,0,-19);return -19;}
 struct tp_state state={0};int result=tp_draw(ctx->io,0,0);
 for(unsigned int tries=0;!result&&tries<16000&&ll_deadline(ctx);tries++){
  struct tp_event events[32];long n=ft_call(ctx->io,FT_NR_READ,input,(long)events,sizeof(events),0,0,0);
  if(n==-4)continue;
  if(n==-11){result=ll_pause(ctx);continue;}
  if(n<=0||n>(long)sizeof(events)||n%(long)sizeof(events[0])){result=n<0?(int)n:-5;break;}
  unsigned int old=state.visited;
  for(unsigned int i=0;i<(unsigned long)n/sizeof(events[0]);i++)tp_feed(&state,&events[i]);
  if(state.failed){result=state.failed;break;}
  if(old!=state.visited)result=tp_draw(ctx->io,state.visited,0);
 }
 if(result)(void)tp_draw(ctx->io,state.visited,result);
 long closed=ft_call(ctx->io,FT_NR_CLOSE,input,0,0,0,0,0);return result?result:closed<0?(int)closed:0;
}
#endif
