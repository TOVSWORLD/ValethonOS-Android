/* SPDX-License-Identifier: GPL-2.0 */
#ifndef KXSTAGE_CRC_H
#define KXSTAGE_CRC_H
#include <stdint.h>
#include <stddef.h>
static inline uint32_t kxstage_crc32(const unsigned char *p, size_t n)
{
 uint32_t crc = ~0U;
 size_t i;
 unsigned bit;
 for (i = 0; i < n; i++) {
  crc ^= p[i];
  for (bit = 0; bit < 8; bit++) crc = (crc >> 1) ^ (0xedb88320U & (0U - (crc & 1)));
 }
 return crc ^ ~0U;
}
#endif
