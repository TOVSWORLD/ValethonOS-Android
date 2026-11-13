/* Actual extracted last-close functions, with RAM adapters for kernel APIs. */
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define ENTER() ((void)0)
#define READ_ONCE(x) (x)
enum { FFS_DEACTIVATED=1, FFS_CLOSING=2, FFS_SETUP_PENDING=3 };
struct ffs_data {int opened,no_disconnect,state,eps_count,setup_state;void*epfiles;const char*dev_name;};
static bool ft_hold_adb;
static char ft_hold_trial[33];
static int board=1,resets,destroys,stalls,puts_count,markers;
static int atomic_dec_and_test(int*p){return --*p==0;}
static int atomic_read(int*p){return *p;}
static bool of_machine_is_compatible(const char*s){return board&&!strcmp(s,"mediatek,mt8163");}
static void ffs_data_reset(struct ffs_data*f){(void)f;resets++;}
static void ffs_data_put(struct ffs_data*f){(void)f;puts_count++;}
static void ffs_epfiles_destroy(void*p,int n){if(!p||n!=3)abort();destroys++;}
static void __ffs_ep0_stall(struct ffs_data*f){(void)f;stalls++;}
#define pr_emerg(...) (++markers)
#include "actual-last-close.inc"
int main(int argc,char**argv){
 if(argc!=2)return 2;
 int n=atoi(argv[1]);struct ffs_data f={.opened=1,.eps_count=3,.epfiles=(void*)1,.dev_name="adb"};
 strcpy(ft_hold_trial,"11111111111111111111111111111111");ft_hold_adb=true;
 switch(n){
 case 0:ft_hold_adb=false;break;
 case 1:break;
 case 2:ft_hold_trial[0]=0;break;
 case 3:ft_hold_trial[10]='g';break;
 case 4:f.dev_name="mtp";break;
 case 5:board=0;break;
 case 6:f.no_disconnect=1;ft_hold_adb=false;break;
 case 7:f.opened=2;break;
 case 8:f.opened=0;break;
 case 9:f.setup_state=FFS_SETUP_PENDING;break;
 case 10:f.epfiles=NULL;break;
 case 11:f.dev_name=NULL;break;
 default:return 3;
 }
 ffs_data_closed(&f);
 bool retained=n==1||n==6||n==9||n==10;
 if(puts_count!=1)return 4;
 if(n==7){if(resets||destroys||markers||f.opened!=1)return 5;}
 else if(retained){
  if(resets||f.state!=FFS_DEACTIVATED||f.epfiles)return 6;
  if(destroys!=(n==10?0:1)||stalls!=(n==9)||markers!=(n==6?0:1))return 7;
 }else if(resets!=1||destroys||markers||f.state!=FFS_CLOSING)return 8;
 puts("ffs_last_close_control=passed");return 0;
}
