#!/usr/bin/env python3
import re,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];folder=root/'evidence/independent-recovery/selinux-source'
s=json.loads((folder/'sources.json').read_text())
for r in s['records']:
 b=(folder/r['path'].split('/')[-1]).read_bytes();
 if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('Pinned SELinux ABI hash mismatch')
text=(folder/'classmap.h').read_text().replace('\\\n','')
text=re.sub(r'/\*.*?\*/','',text,flags=re.S)
macros=dict(re.findall(r'^#define\s+(COMMON_\w+)\s+([^\n]+)',text,re.M))
def perms(expr):
 toks=re.findall(r'"([a-z0-9_]+)"|(COMMON_\w+)|(NULL)',expr);result=[]
 leftover=re.sub(r'"[a-z0-9_]+"|COMMON_\w+|NULL|[\s,]','',expr)
 
 if leftover:raise ValueError('Unsupported ABI initializer expression')
 for name,macro,null in toks:
  if name:result.append(name)
  elif macro:result+=perms(macros[macro])
 
 if len(result)>32:raise ValueError('SELinux permission bitmap overflow')
 return result
classes=[(n,perms(p)) for n,p in re.findall(r'\{\s*"([a-z0-9_]+)"\s*,\s*\{(.*?)\}\s*\}',text,re.S)]

if len(classes)!=97 or len(dict(classes))!=len(classes):raise ValueError('Unexpected class table')
lines=['; Generated from exact ACK SELinux class/SID names; GPL-2.0 source headers retained.']
for n,p in classes:lines.append('(class '+n+' ('+' '.join(p)+'))')
lines.append('(classorder ('+' '.join(n for n,_ in classes)+'))')
body=(folder/'initial_sid_to_string.h').read_text().split('initial_sid_to_string[] = {',1)[1].split('};',1)[0]
sids=[]
for raw in body.splitlines():
 if not raw.strip():continue
 m=re.fullmatch(r'\s*(NULL|"[a-z0-9_]+"),\s*/\*\s*([a-z0-9_]+).*?\*/\s*',raw);
 if not m:raise ValueError('Unsupported SID declaration')
 if m[2]=='zero':continue
 n=m[1].strip('"') if m[1]!='NULL' else m[2];sids.append(n);lines.append('(sid '+n+')')

if len(sids)!=27:raise ValueError('Unexpected SID slots')
lines.append('(sidorder ('+' '.join(sids)+'))')
for n in sids:
 t={'kernel':'kernel_t','security':'security_t','unlabeled':'unlabeled_t','file':'rootfs_t','init':'init_t'}.get(n,'unlabeled_t');role='system_r' if t in ['kernel_t','init_t'] else 'object_r'
 lines.append('(sidcontext '+n+' (system_u '+role+' '+t+' ((s0) (s0))))')
import argparse
parser=argparse.ArgumentParser(description='Regenerate exact pinned ACK SELinux ABI declarations; no policy/device load')
parser.add_argument('--check',action='store_true');args=parser.parse_args()
output=root/'projects/firetabs-android/diagnostic-usb/policy/ack-abi.cil'
expected='\n'.join(lines)+'\n'
if args.check:
 if output.read_text()!=expected:raise ValueError('Generated SELinux ABI differs from pinned inputs')
else:output.write_text(expected)
print(str(len(classes))+' classes; '+str(len(sids))+' SID slots verified')
