#!/usr/bin/env python3
"""Link analysis bootstrap exclusively into console-reclaimed resident spans."""
import argparse,os,subprocess,struct,json
from pathlib import Path
from validate_loader_console_reclaim import SPANS
ROOT=Path(__file__).resolve().parents[1]
def sections(path):
 b=path.read_bytes();at=struct.unpack_from('<I',b,32)[0];size,count,names=struct.unpack_from('<HHH',b,46);ss=[struct.unpack_from('<10I',b,at+i*size) for i in range(count)];t=ss[names];strings=b[t[4]:t[4]+t[5]];out=[]
 for s in ss:
  name=strings[s[0]:].split(b'\0')[0].decode()
  if s[2]&2 and s[5] and s[1] in [1,8]:out.append((name,s[5],s[8] or 1,s[1]))
 return out
def build(compiler,output,pre_shutdown=False,screen_witness=False):
 output.mkdir(parents=True,exist_ok=True,mode=0o700);env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(output.resolve()/'zig-cache'),ZIG_LOCAL_CACHE_DIR=str(output.resolve()/'zig-local-cache'))
 flags=['-target','thumb-freestanding-eabi','-mcpu=cortex_a9','-Oz','-g','-fvisibility=hidden','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables'];objects=[];items=[]
 if screen_witness and not pre_shutdown:raise ValueError('Screen witness requires late-only pre-shutdown profile')
 if pre_shutdown:flags+=['-DLBO_PRE_SHUTDOWN=1']
 if screen_witness:flags+=['-DLBO_SCREEN_WITNESS=1']
 for name in [('bootstrap-witness.c' if screen_witness else 'bootstrap.c'),'bootstrap-hooks.S','bridge.c','hash.c','hash-block.S','cache.S','freestanding.c']:
  obj=output/(name.rsplit('.',1)[0]+'.o');subprocess.run([compiler,'cc',*flags,'-c',str(ROOT/'projects/firetabs-android/loader-retained'/name),'-o',str(obj)],env=env,check=True);objects.append(obj)
  items += [(obj,sec,n,align,kind) for sec,n,align,kind in sections(obj) if not sec.startswith('.ARM.exidx')]
 # Deterministic bounded bin assignment, backtrack to accommodate section alignment.
 items.sort(key=lambda x:-x[2]);bins=list(SPANS);placement=[]
 def fit(i):
  if i==len(items):return True
  obj,sec,n,align,kind=items[i]
  for k,(lo,hi) in enumerate(bins):
   at=(lo+align-1)&~(align-1)
   if at+n>hi:continue
   bins[k]=(at+n,hi);placement.append((obj,sec,n,at,kind))
   if fit(i+1):return True
   placement.pop();bins[k]=(lo,hi)
  return False
 if not fit(0):raise ValueError('Owned spans cannot contain bootstrap sections: '+repr([(s,n) for _,s,n,_,_ in items]))
 entry='lbo_arrival' if screen_witness else 'lbo_read'
 lines=['ENTRY('+entry+')','lbo_original_handoff = 0x4bd3de69;','SECTIONS {']
 for i,(obj,sec,n,at,kind) in enumerate(placement):lines.append(f'.owned{i} 0x{0x4bcff000+at:x} : {{ *({sec}) }}')
 lines+=['/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }','}'];script=output/'bootstrap.ld';script.write_text('\n'.join(lines)+'\n')
 subprocess.run([compiler,'cc',*flags,'-nostdlib','-Wl,-e,'+entry,'-Wl,-u,'+('lbo_pre_shutdown' if pre_shutdown else 'lbo_handoff'),'-Wl,--build-id=none','-Wl,-T,'+str(script),*[str(x) for x in objects],'-o',str(output/'bootstrap.elf')],env=env,check=True)
 r={'scope':'analysis bootstrap link in owned console spans only','bytes':sum(x[2] for x in placement),'sections':[{'object':o.name,'section':s,'bytes':n,'resident_offset':hex(at),'zero':kind==8} for o,s,n,at,kind in placement],'physical_candidate':False,'screen_witness':screen_witness,'read_observer':not screen_witness};(output/'placement.json').write_text(json.dumps(r,indent=2)+'\n');print('Owned bootstrap bytes:',r['bytes'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zig',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--pre-shutdown',action='store_true');p.add_argument('--screen-witness',action='store_true');a=p.parse_args();build(a.zig,a.out,a.pre_shutdown,a.screen_witness)
