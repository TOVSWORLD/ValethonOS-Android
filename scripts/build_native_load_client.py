#!/usr/bin/env python3
"""Build a static load-only client bound to one exact native jump manifest."""
import argparse,hashlib,json,subprocess
from pathlib import Path

def build(source,manifest,out,cc='aarch64-linux-musl-gcc'):
 r=json.loads(manifest.read_text());segments=r['segments']
 if len(segments)!=3 or [s['file'] for s in segments]!=['image.bin','metadata.bin','initrd.bin']:raise ValueError('Exact three-segment bundle required')
 if [s['address'] for s in segments]!=[0x40080000,0x42000000,0x69244000] or r['entry']!=0x42018000:raise ValueError('Reviewed physical layout required')
 for s in segments:
  if not 0<s['bytes']<=s['memory_bytes']<=32*1024*1024 or s['memory_bytes']%4096:raise ValueError('Bounded page-aligned capacity required')
 out.mkdir(mode=0o700)
 header='struct bundle_spec {const char *name; size_t bytes; unsigned long address; size_t memory_bytes;};\n#define BUNDLE_ENTRY 0x42018000UL\nstatic const struct bundle_spec bundle[3]={\n'
 for s in segments:header+='{"%s",%d,0x%xUL,%d},\n'%(s['file'],s['bytes'],s['address'],s['memory_bytes'])
 (out/'bundle.h').write_text(header+'};\n')
 subprocess.run([cc,'-std=c11','-O2','-Wall','-Wextra','-Werror','-static','-I'+str(out),str(source),'-o',str(out/'native-load')],check=True)
 b=(out/'native-load').read_bytes()
 if b[:6]!=b'\x7fELF\x02\x01' or b[18:20]!=b'\xb7\x00':raise ValueError('AArch64 ELF64 required')
 result={'scope':'Static native load/unload client; no execute command','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'client_sha256':hashlib.sha256(b).hexdigest(),'client_bytes':len(b),'execute_implemented':False,'loaded_on_tablet':False}
 (out/'build-result.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['source','manifest','out']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--cc',default='aarch64-linux-musl-gcc');a=p.parse_args();print(json.dumps(build(a.source,a.manifest,a.out,a.cc),indent=2))
