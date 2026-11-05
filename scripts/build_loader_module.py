#!/usr/bin/env python3
"""Build an analysis-only PIC module locally; never package/install a boot image."""
import argparse,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build(compiler,output,profile="core"):
 output.mkdir(parents=True,exist_ok=True,mode=0o700)
 env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str((output/'zig-cache').resolve()),ZIG_LOCAL_CACHE_DIR=str((output/'zig-local-cache').resolve()))
 flags=['-target','thumb-freestanding-eabi','-mcpu=cortex_a9','-Oz','-g','-fPIC','-fvisibility=hidden','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables'];objects=[]
 names=['checkpoint.c','mmc_flush.c','module.c','freestanding.c']
 if profile in ['firmware','timed']:names+=['physical.c','hash-stream.c','firmware-module.c','hash-block.S']
 if profile=='timed':names+=['clock.c','command.c','timed-module.c']
 for source in names:
  name=source.rsplit('.',1)[0]
  obj=output/(name+'.o');objects.append(str(obj));subprocess.run([compiler,'cc',*flags,'-c',str(ROOT/'projects/firetabs-android/loader-retained'/source),'-o',str(obj)],env=env,check=True)
 subprocess.run([compiler,'cc',*flags,'-nostdlib','-Wl,--build-id=none','-Wl,-T,'+str(ROOT/'projects/firetabs-android/loader-retained/analysis.ld'),'-Wl,-e,'+('lft_start' if profile=='timed' else 'lfw_start' if profile=='firmware' else 'lm_start'),*(['-Wl,-u,lh_block'] if profile in ['firmware','timed'] else []),*objects,'-o',str(output/'module.elf')],env=env,check=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zig',default='zig');p.add_argument('--out',type=Path,default=ROOT/'out/loader-module');p.add_argument('--profile',choices=['core','firmware','timed'],default='core');a=p.parse_args();build(a.zig,a.out,a.profile)
