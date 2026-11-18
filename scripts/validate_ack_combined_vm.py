#!/usr/bin/env python3
"""Generic Cortex-A53 VM regression for an instrumented ACK Image, never a tablet test."""
import argparse,hashlib,json,os,re,selectors,socket,struct,subprocess,time,tempfile
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()

def reserve(data):
 h=list(struct.unpack_from('>10I',data));at=h[4];end=at
 while end+16<=len(data):
  a,n=struct.unpack_from('>QQ',data,end);end+=16
  if not a and not n:break
 else:raise ValueError('Unterminated VM reserve map')
 old=data[at:end-16]
 new=old+struct.pack('>QQQQQQ',0x42000000,0x28000,0x444bf000,65536,0,0)
 delta=len(new)-(end-at);out=bytearray(data[:at]+new+data[end:]);h[1]+=delta
 for i in [2,3]:
  if h[i]>=end:h[i]+=delta
 # QEMU dumpdtb leaves a large capacity tail; external-DTB loading grows
 # that again. Trim unused capacity before the ARM64 2MiB FDT size check.
 used=max(h[2]+h[9],h[3]+h[8],at+len(new));h[1]=used
 struct.pack_into('>10I',out,0,*h)
 return bytes(out[:used])

def mon(path,command):
 # QMP replies acknowledge completed commands; HMP prompts can be stale/partial.
 import shlex
 with socket.socket(socket.AF_UNIX) as sock:
  sock.settimeout(8);sock.connect(str(path));stream=sock.makefile('rwb',buffering=0)
  json.loads(stream.readline())
  def execute(name,args=None):
   request={'execute':name,'id':'request'}
   if args is not None:request['arguments']=args
   stream.write(json.dumps(request).encode()+b'\n')
   while True:
    reply=json.loads(stream.readline())
    if reply.get('id')=='request':
     if 'error' in reply:raise ValueError('VM QMP command failed')
     return reply.get('return')
  execute('qmp_capabilities')
  if command=='stop':execute('stop');return b''
  if command=='info registers':return execute('human-monitor-command',{'command-line':command}).encode()
  words=shlex.split(command)
  if len(words)!=4 or words[0]!='pmemsave':raise ValueError('Unexpected monitor request')
  execute('pmemsave',{'val':int(words[1],0),'size':int(words[2],0),'filename':words[3]})
  return b''

def run(kernel,initrd,plan,output,virtualization):
 output.mkdir(mode=0o700)
 if sha(kernel.read_bytes())!=plan['image_sha256'] or sha(initrd.read_bytes())!=plan['initramfs_sha256']:
  raise ValueError('Exact VM inputs required')
 token=plan['trial_id']
 if not re.fullmatch('[0-9a-f]{32}',token):raise ValueError('Exact kernel hook token required')
 dt=output/'virt-private.dtb'
 common=['qemu-system-aarch64','-machine','virt,gic-version=2,virtualization='+virtualization,'-cpu','cortex-a53','-smp','1','-m','512','-accel','tcg','-nodefaults','-display','none','-nic','none']
 dump=common[:];dump[dump.index('virt,gic-version=2,virtualization='+virtualization)]+=',dumpdtb='+str(dt)
 dump += ['-serial','stdio','-kernel',str(kernel),'-initrd',str(initrd),'-append','console=ttyAMA0,115200 earlycon=pl011,0x9000000 rdinit=/init nr_cpus=1 maxcpus=0 loglevel=8 ignore_loglevel panic=-1']
 subprocess.run(dump,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=15,check=True)
 dt.write_bytes(reserve(dt.read_bytes()))
 monitor_dir=tempfile.TemporaryDirectory(prefix='ft-vm-');monitor=Path(monitor_dir.name)/'monitor.sock';ring=output/'console-private.bin'
 cmd=common+['-serial','stdio','-monitor','none','-qmp','unix:'+str(monitor)+',server=on,wait=off','-no-reboot','-kernel',str(kernel),'-initrd',str(initrd),'-dtb',str(dt),'-device','loader,addr=0x444bf000,data=0x43474244,data-len=4','-append','console=ttyAMA0,115200 earlycon=pl011,0x9000000 rdinit=/init nr_cpus=1 maxcpus=0 loglevel=8 ignore_loglevel panic=-1']
 proc=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 data=bytearray();reached=False;began=time.monotonic()
 try:
  with selectors.DefaultSelector() as s:
   s.register(proc.stdout,selectors.EVENT_READ)
   while time.monotonic()-began<60 and len(data)<2*1024*1024:
    for key,_ in s.select(.1):
     b=os.read(key.fd,65536)
     if not b:break
     data+=b
    if b'VM_FILESYSTEM_PROBE_DONE' in data:reached=True;break
    if proc.poll() is not None:break
  if proc.poll() is None:
   mon(monitor,'stop')
   (output/'registers-private.txt').write_bytes(mon(monitor,'info registers'))
   mon(monitor,'pmemsave 0x444bf000 0x10000 '+json.dumps(str(ring)))
   mon(monitor,'pmemsave 0x48200000 0x200000 '+json.dumps(str(output/'loaded-fdt-private.bin')))
 finally:
  if proc.poll() is None:proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
  monitor_dir.cleanup()
 (output/'boot-private.log').write_bytes(data)
 text=bytes(data).replace(b'\r\n',b'\n')
 vals={k.decode():int(v) for k,v in re.findall(rb'^(VM_[A-Z_]+)=([+-][0-9]{10})$',text,re.M)}
 zero=['VM_LABELS','VM_PROC','VM_SYS','VM_DOMAIN','VM_CONFIGFS','VM_NAMESPACE_BEFORE','VM_REAL_CONFIGFS_SETUP_WITHOUT_BIND','VM_REAL_CONFIGFS_CLEANUP','VM_NAMESPACE_AFTER']
 policy_ok=reached and all(vals.get(k)==0 for k in zero) and vals.get('VM_KMSG_READ',0)>0 and vals.get('VM_KMSG_OPEN',-1)>=0 and vals.get('VM_GENERIC_FLAGS_OPEN')==-22 and vals.get('VM_UDC_DIR',-1)>=0
 payload=b''
 if ring.exists():
  raw=ring.read_bytes();sig,start,size=struct.unpack_from('<III',raw)
  if sig==0x43474244 and start<65524 and size<=65524:
   payload=(raw[12+start:]+raw[12:12+start]) if size==65524 else raw[12:12+size]
 stages=['linux_entry','before_mmu','after_mmu','virtual_entry','start_kernel'];positions={}
 for stage in stages:
  mark=('FIRETABS_ACK_COMBINED_V2 nonce='+token+' stage='+stage+'\n').encode()
  if payload.count(mark)==1:positions[stage]=payload.index(mark)
 all_stages=list(positions)==stages and list(positions.values())==sorted(positions.values())
 passed=policy_ok and all_stages and b'Linux version 6.18.34-valethon-draft1+' in text and not any(x in text for x in [b'Kernel panic',b'Internal error: Oops',b'avc:  denied'])
 result=dict(scope='Exact instrumented Image generic Cortex-A53 VM; no tablet or physical USB qualification',passed=passed,image_sha256=plan['image_sha256'],vm_initramfs_sha256=plan['initramfs_sha256'],virtualization=virtualization,stages={s:s in positions for s in stages},stages_in_order=all_stages,enforcing_pid1_filesystem_probe=policy_ok,metadata_integrity_stub_executed=False,hardware_execution=False,disk_attached=False,network_attached=False,tablet_commands=False,raw_log_sha256=sha(data),elapsed_seconds=round(time.monotonic()-began,3))
 (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['kernel','initrd','plan','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--virtualization',choices=['on','off'],required=True);a=p.parse_args()
 r=run(a.kernel,a.initrd,json.loads(a.plan.read_text()),a.output,a.virtualization);print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)
