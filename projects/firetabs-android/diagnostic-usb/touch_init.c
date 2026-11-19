/* Separate standalone touch PID1. Existing display/storage runtime is unchanged. */
#define VALETHON_DISPLAY_TEST 1
#define VALETHON_DISPLAY_ERRORS 1
#include "touch_probe.h"
#include "display_errors.h"
static int touch_label_archive(struct ft_acm_io *io){
 int r=ll_label_archive(io);return r?r:tp_label(io);
}
static int touch_send(void *opaque,const unsigned char *data,unsigned long n){
 /* Send the existing display packet before the attended touch window. Its
  * result never gates the visual grid and never attests a touch pass. */
 int r=ll_send(opaque,data,n);(void)tp_run(opaque);return r;
}
#define ll_label_archive touch_label_archive
#define ll_send touch_send
#include "storage_init.c"
