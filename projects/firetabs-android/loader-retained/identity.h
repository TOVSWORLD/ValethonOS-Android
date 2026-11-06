#ifndef VALETHON_LOADER_IDENTITY_H
#define VALETHON_LOADER_IDENTITY_H
/* Reads only selected non-identifying fields, never CID/CSD or user data. */
struct li_reader {void *context;int (*read)(void *,unsigned,unsigned char *,unsigned);};
struct li_plan {unsigned device,card,host,block_device;};
struct li_binding {unsigned device,card,host,block_device,rca,cache_size_kib,cache_enabled;};
int li_capture(struct li_binding *,const struct li_plan *,const struct li_reader *);
int li_discover(struct li_binding *,unsigned,unsigned,const struct li_reader *);
int li_memory_read(void *,unsigned,unsigned char *,unsigned);
#endif
