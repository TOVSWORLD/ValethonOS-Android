#!/usr/bin/env python3
"""Build analysis-only bridge with pinned generic hash/cache bindings locally."""
import argparse,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build(compiler,output):
 output.mkdir(parents=True,exist_ok=True,mode=0o700)
 env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str((output/'zig-cache').resolve()),ZIG_LOCAL_CACHE_DIR=str((output/'zig-local-cache').resolve()))
 flags=['-target','thumb-freestanding-eabi','-mcpu=cortex_a9','-Oz','-g','-fPIC','-fvisibility=hidden','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-nostdlib','-Wl,--build-id=none','-Wl,-u,lh_equal','-Wl,-u,lh_block','-Wl,-u,lb_cache_sync','-Wl,-T,'+str(ROOT/'projects/firetabs-android/loader-retained/analysis.ld'),'-Wl,-e,lb_load']
 sources=[str(ROOT/'projects/firetabs-android/loader-retained'/name) for name in ['bridge.c','hash.c','hash-block.S','cache.S','freestanding.c']]
 subprocess.run([compiler,'cc',*flags,*sources,'-o',str(output/'bridge.elf')],env=env,check=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zig',default='zig');p.add_argument('--out',type=Path,default=ROOT/'out/loader-bridge');a=p.parse_args();build(a.zig,a.out)
