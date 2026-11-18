/* Separate private read-only storage PID1. Never an admitted/public OS image.
 * Fixed original boot-partition read only; no userdata, reboot or block write.
 * Test PID1209:0001 is nonunique, in-house only; never redistribute/manufacture:
 * https://pid.codes/1209/0001/
 */
#include "lab_log_io.h"
#include "lab_policy_load.h"
#include "lab_labels.h"
#include "lab_domain.h"
#include "storage_readonly.h"
#include "lab_inputs.h" /* Builder-generated immutable policy blob and fresh nonce. */
static long lab_call(void *ctx,long nr,long a,long b,long c,long d,long e,long f) {
 (void)ctx;
 register long x0 __asm__("x0")=a;register long x1 __asm__("x1")=b;
 register long x2 __asm__("x2")=c;register long x3 __asm__("x3")=d;
 register long x4 __asm__("x4")=e;register long x5 __asm__("x5")=f;
 register long x8 __asm__("x8")=nr;
 __asm__ volatile("svc #0":"+r"(x0):"r"(x1),"r"(x2),"r"(x3),"r"(x4),"r"(x5),"r"(x8):"memory","cc");
 return x0;
}
static void lab_note(struct ft_acm_io *io,const char *text,unsigned long n) {
 long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/console",FT_O_WRONLY|FT_SERIAL_NONBLOCK|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd<0)return;
 ft_call(io,FT_NR_WRITE,fd,(long)text,n,0,0,0);
 ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);
}
static int lab_run(struct ft_acm_io *io,int *stage) {
 *stage=1;
 struct vp_io policy_io={io->call,io->ctx};struct vp_state policy={0};
 int result=vp_bootstrap(&policy_io,lab_policy_blob,sizeof(lab_policy_blob),&policy);
 if(result||!policy.loaded||!policy.readonly)return result?result:-1;
 *stage=2;
 result=ll_label_archive(io);if(result)return result;
 {long fd=ft_retry(io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/firetabs-boot",LL_O_PATH|FT_O_NOFOLLOW|FT_O_CLOEXEC);
  if(fd<0)return (int)fd;
  int checked=fs_node(io,fd);long closed=ft_call(io,FT_NR_CLOSE,fd,0,0,0,0,0);
  if(checked||closed<0)return checked?checked:(int)closed;
  const char context[]="system_u:object_r:boot_block_t";unsigned char value[128]={0};
  long r=ft_call(io,LL_NR_LSETXATTR,(long)"/dev/firetabs-boot",(long)"security.selinux",(long)context,sizeof(context),0,0);
  if(r)return (int)r;
  r=ft_call(io,LL_NR_LGETXATTR,(long)"/dev/firetabs-boot",(long)"security.selinux",(long)value,sizeof(value),0,0);
  if(r<0||!ll_context_equal(value,r,context))return r<0?(int)r:-13;
 }
 /* Existing qualified-output program/gates remain unchanged. This separate
  * candidate performs first-trial provisions/checks rather than claiming that
  * the as-yet-unobserved logging/failed-return milestones have already passed. */
 unsigned int mounts=0;char udc[64];
 struct ft_acm_state gadget={0};
 struct ft_serial_state serial={-1,0,0,0,0,0,{0,0,0,0,0,{0}}};
 long kmsg=-1;
 const char *fs[3]={"proc","sysfs","configfs"};
 const char *paths[3]={"/proc","/sys","/config"};
 *stage=3;
 for(int i=0;i<2;i++) {
  long r=ft_call(io,VP_NR_MOUNT,(long)fs[i],(long)paths[i],(long)fs[i],15,0,0);
  if(r){result=(int)r;goto finish;}mounts|=1U<<i;
 }
 *stage=4;
 result=ll_enter_init(io);if(result)goto finish;
 for(int i=0;i<2;i++) {
  char cpus[4];const char *path=i?"/sys/devices/system/cpu/possible":"/sys/devices/system/cpu/online";
  long n=ft_read_file(io,path,cpus,sizeof(cpus));
  if(n!=2||cpus[0]!='0'||cpus[1]!='\n'){result=-1;goto finish;}
 }
 *stage=5;
 result=ft_discover_udc(io,udc,sizeof(udc));if(result)goto finish;
 *stage=6;
 {long r=ft_call(io,VP_NR_MOUNT,(long)fs[2],(long)paths[2],(long)fs[2],14,0,0);
  if(r){result=(int)r;goto finish;}mounts|=4;
 }
 *stage=7;
 result=ll_usb_namespace(io);if(result)goto finish;
 *stage=8;
 result=ft_acm_setup(&ft_acm_filesystem_ops,io,&gadget,udc,"0x1209","0x0001",1);
 if(result)goto finish;
 *stage=9;
 result=ft_serial_open_duplex_owned(io,1,gadget.bound,&serial);if(result)goto finish;
 *stage=10;
 {
  struct ll_context context={io,serial.fd,-1,0,0};unsigned long now=ll_now(&context);
  if(!now||now>~0UL-20000){result=-110;goto finish;}
  context.deadline_ms=now+15000;
  struct fs_result status={0};(void)fs_probe(&context,&status);
  unsigned char packet[FS_PACKET_BYTES];fs_packet(packet,lab_trial_nonce,&status);
  now=ll_now(&context);if(!now||now>~0UL-4000){result=-110;goto finish;}
  context.deadline_ms=now+4000;
  *stage=11;result=ll_send(&context,packet,sizeof(packet));
  /* Keep the owned endpoint alive until reset; no transfer ACK dependency. */
  if(!result)for(;;){const long ts[2]={1,0};ft_call(io,FT_SERIAL_NANOSLEEP,(long)ts,0,0,0,0,0);}
 }

finish:
 if(kmsg>=0){long r=ft_call(io,FT_NR_CLOSE,kmsg,0,0,0,0,0);if(!result&&r<0)result=(int)r;}
 if(serial.fd>=0||serial.node_owned){int r=ft_serial_close(io,&serial);if(r)return result?result:r;}
 /* Preserve virtual mounts on unresolved gadget cleanup, just as legacy flow. */
 if(gadget.cleanup_error)return result?result:gadget.cleanup_error;
 {int r=ft_acm_cleanup(&ft_acm_filesystem_ops,io,&gadget);if(r)return result?result:r;}
 for(int i=2;i>=0;i--)if(mounts&(1U<<i)) {
  long r=ft_call(io,39,(long)paths[i],0,0,0,0,0);if(r)return result?result:(int)r;
 }
 return result;
}
__attribute__((noreturn)) void _start(void) {
 struct ft_acm_io io={lab_call,0};
 (void)&ft_serial_output; /* Preserve existing fixed-frame API without selecting it. */
 int stage=0;
 int result=lab_run(&io,&stage);
 char report[]="VALETHON_LAB_STAGE=00 RESULT=+0000000000\n";
 unsigned int position=sizeof("VALETHON_LAB_STAGE=")-1;
 report[position]=(char)('0'+stage/10);report[position+1]=(char)('0'+stage%10);
 position=sizeof("VALETHON_LAB_STAGE=00 RESULT=")-1;
 report[position]=result<0?'-':'+';
 unsigned int value=result<0?0U-(unsigned int)result:(unsigned int)result;
 for(int i=0;i<10;i++){report[position+10-i]=(char)('0'+value%10);value/=10;}
 lab_note(&io,report,sizeof(report)-1);
 if(result)lab_note(&io,"VALETHON_LAB_LOG_FAILED\n",sizeof("VALETHON_LAB_LOG_FAILED\n")-1);
 else lab_note(&io,"VALETHON_LAB_LOG_SOURCE_DONE\n",sizeof("VALETHON_LAB_LOG_SOURCE_DONE\n")-1);
 for(;;){const long ts[2]={60,0};ft_call(&io,FT_SERIAL_NANOSLEEP,(long)ts,0,0,0,0,0);}
}
