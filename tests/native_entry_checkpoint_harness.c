/* Execute the actual native entry body with RAM adapters; never reboot. */
#include <stdbool.h>
#include <errno.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CONFIG_MACH_MT8163 1
#define KEXEC_TYPE_DEFAULT 0
#define current ((void*)0)
struct kimage {int type;};
static struct kimage image;
static struct kimage*kexec_image=&image;
static int kexec_mutex,locked,lock_busy,unlocks,tgid=1,board=1,native_marks,sleeps,shutdowns,starts;
static bool kexec_in_progress;
static jmp_buf jump;
static int mutex_trylock(int*p){(void)p;if(lock_busy)return 0;locked=1;return 1;}
static void mutex_unlock(int*p){(void)p;locked=0;unlocks++;}
static int task_tgid_nr(void*p){(void)p;return tgid;}
static bool of_machine_is_compatible(const char*s){return board&&!strcmp(s,"mediatek,mt8163");}
static void printk(const char*s){if(strstr(s,"native_entry=1"))native_marks++;else starts++;}
#define pr_emerg(...) printk(__VA_ARGS__)
static void msleep(unsigned n){if(n!=1000||!locked||!kexec_image||native_marks!=1||shutdowns)abort();sleeps++;}
static void kernel_restart_prepare(void*p){(void)p;shutdowns++;}
static void migrate_to_reboot_cpu(void){}
static void cpu_hotplug_enable(void){}
static void machine_shutdown(void){}
static void machine_kexec(struct kimage*p){if(p!=&image||!locked||shutdowns!=1||!kexec_in_progress)abort();longjmp(jump,1);}
#include "native-under-test.inc"
int main(int argc,char**argv){
 if(argc!=2)return 2;
 int n=atoi(argv[1]),event;
 if(n==1)kexec_image=NULL;
 if(n==2)lock_busy=1;
 if(n==3)image.type=1;
 if(n==4)board=0;
 if(n==5)tgid=99;
 event=setjmp(jump);
 if(!event){int ret=kernel_kexec();if(ret!=(n==1?-EINVAL:-EBUSY)||n<1||n>2)return 3;}
 else if(n==1||n==2)return 4;
 if(native_marks!=(n==0)||sleeps!=(n==0))return 5;
 if(n==1||n==2){if(shutdowns||starts||locked||unlocks!=(n==1))return 6;}
 else if(!event||shutdowns!=1||starts!=1)return 7;
 puts("native_entry_control=passed");return 0;
}
