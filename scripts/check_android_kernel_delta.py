#!/usr/bin/env python3
"""Reject unrelated kernel changes while admitting source-derived Android filesystem dependencies."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FRAGMENTS=[ROOT/'projects/firetabs-android/android-integration'/name for name in ['kernel.fragment','kernel-apex.fragment']]
# PNFS_BLOCK defaults to NFS_V4, capped by BLK_DEV_DM; making DM built-in
# promotes the existing m setting to y without changing the NFS configuration.
HELPERS={'CONFIG_PROC_PID_CPUSET','CONFIG_PNFS_BLOCK','CONFIG_BLK_DEV_LOOP_MIN_COUNT','CONFIG_LIBCRC32C','CONFIG_REED_SOLOMON','CONFIG_REED_SOLOMON_ENC8','CONFIG_REED_SOLOMON_DEC8','CONFIG_CRYPTO_HASH_INFO','CONFIG_CRYPTO_LIB_SHA256','CONFIG_LZ4_DECOMPRESS','CONFIG_ZSTD_DECOMPRESS','CONFIG_ZSTD_COMMON','CONFIG_XZ_DEC','CONFIG_XZ_DEC_ARM','CONFIG_XZ_DEC_ARMTHUMB','CONFIG_XZ_DEC_BCJ','CONFIG_CRYPTO_LZ4','CONFIG_CRYPTO_LZ4HC','CONFIG_CRYPTO_ZSTD','CONFIG_LZ4_COMPRESS','CONFIG_LZ4HC_COMPRESS','CONFIG_ZSTD_COMPRESS','CONFIG_ZLIB_INFLATE','CONFIG_CRYPTO_DEFLATE','CONFIG_ZLIB_DEFLATE'}
def config(path):
    return {k:v for line in Path(path).read_text().splitlines() if line.startswith('CONFIG_') for k,v in [line.split('=',1)]}
def check(parent,result):
    old=config(parent);new=config(result)
    required={k:v for fragment in FRAGMENTS for k,v in config(fragment).items()}
    changed={k:[old.get(k,'n'),new.get(k,'n')] for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
    for key,value in changed.items():
        if key=='CONFIG_PNFS_BLOCK' and value!=['m','y']:raise ValueError('Unexpected pNFS dependency transition')
        if key not in required and key not in HELPERS and not key.startswith('CONFIG_EROFS_FS_'):raise ValueError('Unrelated kernel change: '+key)
        if key not in required and value[1] not in ['y','m','8']:raise ValueError('Unexpected helper transition: '+key)
    for key,value in required.items():
        if new.get(key)!=value:raise ValueError('Required Android feature unresolved: '+key)
    for key in ['CONFIG_COMPAT','CONFIG_ARM64_4K_PAGES','CONFIG_DRM_PANFROST','CONFIG_TOUCHSCREEN_GOODIX','CONFIG_DRM_MEDIATEK','CONFIG_SECURITY_SELINUX']:
        if old.get(key)!='y' or new.get(key)!='y':raise ValueError('Working hardware/security requirement changed: '+key)
    return changed
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--result',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(check(a.parent,a.result),indent=2)+'\n');print('Only selected Android kernel features and bounded filesystem helpers changed.')
