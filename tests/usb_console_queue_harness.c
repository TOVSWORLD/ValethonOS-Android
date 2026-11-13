/* Exact extracted console callback/thread; deterministic completion schedules. */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
struct usb_ep {int maxpacket;const char*name;};
struct usb_request {char*buf;int length,status;};
struct gs_buf {int pending;};
struct usb_port {struct usb_ep*in;};
struct gs_port {struct usb_port*port_usb;};
struct gscons_info {struct gs_port*port;void*console_thread;struct usb_request*console_req;struct gs_buf con_buf;int req_busy,con_lock;};
static struct gscons_info gscons_info;
static int mode,queues,delivered,scheduled,pending_completion,rejected;
#define TASK_INTERRUPTIBLE 1
#define TASK_RUNNING 0
#define GFP_ATOMIC 0
#define pr_warn(...) ((void)ep)
#define pr_vdebug(...) ((void)ep)
#define spin_lock(x) ((void)(x))
#define spin_unlock(x) ((void)(x))
#define spin_lock_irq(x) ((void)(x))
static void gs_complete_out(struct usb_ep*,struct usb_request*);
static void unlock_irq(int*x){(void)x;if(pending_completion){pending_completion=0;gs_complete_out(gscons_info.port->port_usb->in,gscons_info.console_req);}}
#define spin_unlock_irq(x) unlock_irq(x)
static void set_current_state(int n){(void)n;}
static void wake_up_process(void*p){(void)p;}
static int gs_buf_data_avail(struct gs_buf*b){return b->pending;}
static int gs_buf_get(struct gs_buf*b,char*out,int n){b->pending-=n;memset(out,'x',n);return n;}
static int kthread_should_stop(void){return scheduled||gscons_info.con_buf.pending==0;}
static void schedule(void){scheduled++;}
static int usb_ep_queue(struct usb_ep*ep,struct usb_request*req,int flags){
 (void)flags;queues++;if(queues>8)abort();
 if(mode==2&&!rejected){rejected=1;return -ESHUTDOWN;}
 delivered+=req->length;req->status=0;
 if(mode==1)pending_completion=1;
 else gs_complete_out(ep,req); /* completion on another CPU before queue returns */
 return 0;
}
#include "console-under-test.inc"
int main(int argc,char**argv){
 if(argc!=3)return 2;
 mode=atoi(argv[1]);int fixed=atoi(argv[2]);
 struct usb_ep ep={64,"in"};struct usb_port usb={&ep};struct gs_port port={&usb};char bytes[64];struct usb_request req={bytes,0,0};
 gscons_info.port=&port;gscons_info.console_req=&req;gscons_info.con_buf.pending=192;
 gs_console_thread(NULL);
 if(mode==0&&!fixed){if(delivered!=64||gscons_info.con_buf.pending!=128||!gscons_info.req_busy)return 3;puts("baseline_lost_completion_reproduced");}
 else {if(gscons_info.con_buf.pending||gscons_info.req_busy||delivered!=(mode==2?128:192))return 4;puts("console_queue_control=passed");}
 return 0;
}
