/* Loader-produced VLOG0001 records. No device discovery or physical admission.
 * Adapter must independently prove exact target, synchronous I/O and durability.
 */
#ifndef VALETHON_LOADER_CHECKPOINT_H
#define VALETHON_LOADER_CHECKPOINT_H
#include "../diagnostic-usb/retained_mailbox.h"
#define LC_TAG "VALETHON LOADER CHECKPOINT v1\n"
#define LC_BYTES ((unsigned)(sizeof(LC_TAG)-1+132))
#define LC_MAX_COMMITS 8
#define LC_MODE 1
#define LC_READ 2
#define LC_HANDOFF 3
#define LC_PRE_SHUTDOWN 4
struct lc_config {
 unsigned char nonce[32],prefix[32];
 unsigned long long target_first_sector,logical_boot_first_sector;
 unsigned partition_bytes,gpt_partition,mmc_partition,durability_verified,exclusive_target_verified;
};
struct lc_point {
 unsigned stage,mode,kind,read_bytes,destination,entry,dt;
 unsigned long long selected_first_sector,requested_offset,selected_offset;
};
struct lc_context {
 struct lc_config config;
 struct vm_io underlying,guarded;
 unsigned commits,last_stage,prefix_verified,stopped,finished;
 unsigned char scratch[VM_HEADER],block[VM_HEADER],payload[LC_BYTES];
};
int lc_init(struct lc_context *,const struct lc_config *,const struct vm_io *);
int lc_emit(struct lc_context *,const struct lc_point *);
unsigned long lc_context_bytes(void);
unsigned lc_payload_bytes(void);
#endif
