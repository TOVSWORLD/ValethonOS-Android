/* Analysis-only persistence adapter; firmware bindings/placement not admitted. */
#ifndef VALETHON_LOADER_MMC_FLUSH_H
#define VALETHON_LOADER_MMC_FLUSH_H
struct lf_command { unsigned opcode,argument,response_type,response[4],timeout_ms,retries; };
/* Layout follows the pinned LK command constructor: response+0xc, timeout+0x1c,
 * retries+0x20. Command callback must make ONE bounded hardware attempt. */
struct lf_adapter {
 void *context;
 int (*command)(void *,struct lf_command *);
 unsigned (*now_ms)(void *);
 unsigned rca,cache_size_kib,cache_enabled,bindings_verified,clock_verified;
 unsigned stopped;
};
int lf_flush(void *);
#endif
