/* SPDX-License-Identifier: GPL-2.0 */
/* Bounded staging test. The module must refuse legacy execution requests. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include "stage_uapi.h"
struct user_segment { uint64_t buffer, bufsz, destination, memsz; };
_Static_assert(sizeof(void *) == 8, "Native 64-bit client required");
_Static_assert(sizeof(struct user_segment) == 32, "Segment ABI mismatch");
_Static_assert(sizeof(struct kxstage_request) == 32, "Request ABI mismatch");
_Static_assert(sizeof(struct kxstage_status) == 80, "Status ABI mismatch");

#include "stage_crc.h"

static int rejects_execution(int fd)
{
 errno = 0;
 int rejected = ioctl(fd, 0x45584543UL, NULL) == -1 && errno == EOPNOTSUPP;
 if (rejected) errno = 0;
 return rejected;
}
int main(int argc, char **argv)
{
 struct kxstage_request req = {0};
 struct kxstage_status before = {0}, staged = {0}, after = {0};
 struct user_segment segments[3] = {
  {0, 5123, 0x40080000, 8192}, {0, 1149, 0x48000000, 4096}, {0, 3999, 0x43480000, 4096},
 };
 unsigned char *buffers[3] = {0};
 uint32_t expected[3] = {0};
 unsigned i;
 size_t j;
 int fd = -1, ok = 0, attempted = 0, failure_errno = 0;
 const char *phase = "arguments";
 struct stat node;
 if (argc != 2 || strcmp(argv[1], "--selftest")) {
  fprintf(stderr, "Usage: kxstage-client --selftest (staging only; never executes)\n"); return 2;
 }
 alarm(15);
 phase = "open";
 fd = open("/dev/kxstage", O_RDWR | O_CLOEXEC | O_NOFOLLOW);
 if (fd < 0) goto out;
 phase = "node_identity";
 if (fstat(fd, &node) || !S_ISCHR(node.st_mode) || node.st_uid || (node.st_mode & 0777) != 0600) goto out;
 phase = "initial_status_and_execution_refusal";
 if (ioctl(fd, KXSTAGE_STATUS, &before) || before.attempted || before.prepared ||
     before.owned_pages || before.execute_disabled != 1 || !rejects_execution(fd)) goto out;
 phase = "allocate_client_buffers";
 for (i = 0; i < 3; i++) {
  buffers[i] = calloc(1, segments[i].memsz);
  if (!buffers[i]) goto out;
  for (j = 0; j < segments[i].bufsz; j++) buffers[i][j] = (unsigned char)((j*17 + i*71 + 3) & 255);
  segments[i].buffer = (uintptr_t)buffers[i];
  expected[i] = kxstage_crc32(buffers[i], segments[i].memsz);
 }
 req.entry = segments[0].destination;
 req.nr_segments = 3;
 req.segments = (uintptr_t)segments;
 phase = "prepare";
 attempted = 1;
 if (ioctl(fd, KXSTAGE_PREPARE, &req)) goto out;
 phase = "prepared_status";
 if (ioctl(fd, KXSTAGE_STATUS, &staged) || !staged.prepared || !staged.attempted ||
     staged.segments != 3 || !staged.owned_pages || staged.owned_pages > 24592 ||
     staged.execute_disabled != 1 || !rejects_execution(fd)) goto out;
 phase = "copied_crc_and_zero_padding";
 for (i = 0; i < 3; i++)
  if (staged.mem_bytes[i] != segments[i].memsz || staged.crc32[i] != expected[i]) goto out;
 phase = "discard";
 if (ioctl(fd, KXSTAGE_DISCARD) || ioctl(fd, KXSTAGE_STATUS, &after) ||
     after.prepared || after.owned_pages || !after.attempted || after.execute_disabled != 1) goto out;
 /* A second prepare is forbidden even after successful discard. */
 phase = "duplicate_prepare_refusal";
 errno = 0;
 if (ioctl(fd, KXSTAGE_PREPARE, &req) != -1 || errno != EALREADY) goto out;
 ok = 1;
 phase = "complete";
out:
 failure_errno = ok ? 0 : errno;
 if (fd >= 0) {
  /* Idempotent cleanup also covers every failure after the first open. */
  if (ioctl(fd, KXSTAGE_DISCARD)) {
   if (ok) { phase = "cleanup_discard"; failure_errno = errno; } ok = 0;
  }
  if (ioctl(fd, KXSTAGE_STATUS, &after) || after.owned_pages || after.prepared) {
   if (ok) { phase = "cleanup_status"; failure_errno = errno; } ok = 0;
  }
  if (close(fd)) {
   if (ok) { phase = "close"; failure_errno = errno; } ok = 0;
  }
 }
 for (i = 0; i < 3; i++) free(buffers[i]);
 alarm(0);
 printf("{\"complete\":%s,\"prepare_attempted\":%s,\"segments\":%llu,"
        "\"requested_bytes\":16384,\"staged_bytes\":%llu,\"owned_pages_prepared\":%llu,\"owned_pages_after\":%llu,"
        "\"crc32\":[\"%08x\",\"%08x\",\"%08x\"],\"execute_disabled\":%s,\"handoff_attempted\":false,\"phase\":\"%s\",\"errno\":%d}\n",
        ok ? "true" : "false", attempted ? "true" : "false",
        (unsigned long long)staged.segments, (unsigned long long)(staged.mem_bytes[0]+staged.mem_bytes[1]+staged.mem_bytes[2]), (unsigned long long)staged.owned_pages,
        (unsigned long long)after.owned_pages, staged.crc32[0], staged.crc32[1], staged.crc32[2],
        before.execute_disabled == 1 && after.execute_disabled == 1 ? "true" : "false", phase, failure_errno);
 return ok ? 0 : 1;
}
