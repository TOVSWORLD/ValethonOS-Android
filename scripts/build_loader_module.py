#!/usr/bin/env python3
"""Build an analysis-only PIC module locally; never package/install a boot image."""
import argparse,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build(compiler,output):
 output.mkdir(parents=True,exist_ok=True,mode=0o700)
 env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str((output/'zig-cache').resolve()),ZIG_LOCAL_CACHE_DIR=str((output/'zig-local-cache').resolve()))
 flags=['-target','thumb-freestanding-eabi','-mcpu=cortex_a9','-Oz','-g','-fPIC','-fvisibility=hidden','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables'];objects=[]
 for name in ['checkpoint','mmc_flush','module','freestanding']:
  obj=output/(name+'.o');objects.append(str(obj));subprocess.run([compiler,'cc',*flags,'-c',str(ROOT/'projects/firetabs-android/loader-retained'/(name+'.c')),'-o',str(obj)],env=env,check=True)
 subprocess.run([compiler,'cc',*flags,'-nostdlib','-Wl,--build-id=none','-Wl,-T,'+str(ROOT/'projects/firetabs-android/loader-retained/analysis.ld'),'-Wl,-e,lm_start',*objects,'-o',str(output/'module.elf')],env=env,check=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zig',default='zig');p.add_argument('--out',type=Path,default=ROOT/'out/loader-module');a=p.parse_args();build(a.zig,a.out)
