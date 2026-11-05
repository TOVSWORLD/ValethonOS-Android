#include "mmc_flush.h"
#define LF_BUDGET_MS 1000U
#define LF_COMMAND_MS 50U
#define LF_POLLS 8U
/* Conservative: all upper status bits, SWITCH_ERROR and EXCEPTION_EVENT.
 * R1 bit meanings: pinned kernel include/linux/mmc/mmc.h. */
#define LF_BAD_STATUS 0xffffe0c0U
static int lf_issue(struct lf_adapter *a,unsigned start,unsigned op,unsigned arg,unsigned response,unsigned *status){
 if(a->now_ms(a->context)-start>=LF_BUDGET_MS)return -2;
 struct lf_command cmd={0};cmd.opcode=op;cmd.argument=arg;
 cmd.response_type=response;cmd.timeout_ms=LF_COMMAND_MS;cmd.retries=0;
 int rc=a->command(a->context,&cmd);
 if(rc||a->now_ms(a->context)-start>=LF_BUDGET_MS)return -3;
 *status=cmd.response[0];if(*status&LF_BAD_STATUS)return -4;
 return 0;
}
static int lf_ready(unsigned status){return (status&0x100U)&&((status>>9)&15U)==4U;}
int lf_flush(void *opaque){
 struct lf_adapter *a=opaque;unsigned status=0;
 if(!a||a->stopped)return -1;
 if(!a->command||!a->now_ms||!a->bindings_verified||!a->clock_verified||
    !a->cache_size_kib||a->cache_enabled!=1||!a->rca||a->rca>0xffffU){a->stopped=1;return -1;}
 unsigned start=a->now_ms(a->context);
 /* Refuse to issue a write-class command unless the card is already selected,
  * ready and clean. This status is never reused as post-flush completion. */
 if(lf_issue(a,start,13,a->rca<<16,1,&status)||!lf_ready(status))goto fail;
 /* WRITE_BYTE, EXT_CSD_FLUSH_CACHE=32, value=1, command set=1. One CMD6 only. */
 if(lf_issue(a,start,6,0x03200101U,8,&status))goto fail;
 for(unsigned i=0;i<LF_POLLS;i++){
  if(lf_issue(a,start,13,a->rca<<16,1,&status))goto fail;
  if(lf_ready(status))return 0;
  /* Only the programming state may remain busy. Unexpected states fail closed. */
  if(((status>>9)&15U)!=7U)goto fail;
 }
 fail:a->stopped=1;return -5;
}
