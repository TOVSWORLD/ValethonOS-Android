#!/usr/bin/env python3
"""Generic Cortex-A53 VM regression for an C-init ACK Image, never a tablet test."""
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

def geometry(data,plan):
 # Preserve virt controllers but transplant the target RAM banks/no-map ranges.
 h=list(struct.unpack_from('>10I',data));st=data[h[2]:h[2]+h[9]];strings=bytearray(data[h[3]:h[3]+h[8]])
 def nameoff(name):
  key=name.encode()+b'\0';at=bytes(strings).find(key)
  if at<0:at=len(strings);strings.extend(key)
  return at
 def prop(name,value):return struct.pack('>III',3,len(value),nameoff(name))+value+bytes((-len(value))%4)
 def begin(name):
  value=name.encode()+b'\0';return struct.pack('>I',1)+value+bytes((-len(value))%4)
 end=struct.pack('>I',2);block=begin('reserved-memory')+prop('#address-cells',struct.pack('>I',2))+prop('#size-cells',struct.pack('>I',2))+prop('ranges',b'')
 for i,(a,z) in enumerate(plan['nomap_ranges']):block+=begin('retained-gap@'+format(a,'x'))+prop('reg',struct.pack('>QQ',a,z-a))+prop('no-map',b'')+end
 block+=end;out=bytearray();stack=[];at=0;memories=0
 while at<len(st):
  start=at;tag=struct.unpack_from('>I',st,at)[0];at+=4
  if tag==1:
   stop=st.index(0,at);name=st[at:stop].decode();stack.append(name);at=(stop+4)&~3
   if len(stack)==2 and name=='reserved-memory':raise ValueError('Unexpected existing virt reserve nodes')
  elif tag==2:
   if len(stack)==1:out+=block
   stack.pop()
  elif tag==3:
   size,off=struct.unpack_from('>II',st,at);at+=8;value=st[at:at+size];at=(at+size+3)&~3
   name=bytes(strings[off:]).split(b'\0',1)[0].decode()
   if len(stack)==2 and stack[-1].startswith('memory@') and name=='reg':
    out+=prop('reg',b''.join(struct.pack('>QQ',a,z-a) for a,z in plan['memory_banks']));memories+=1;continue
  elif tag not in [4,9]:raise ValueError('Invalid FDT token')
  out+=st[start:at]
 if stack or memories!=1:raise ValueError('One virt RAM node required')
 result=bytearray(data[:h[2]]+out+strings);h[3]=h[2]+len(out);h[9]=len(out);h[8]=len(strings);h[1]=len(result);struct.pack_into('>10I',result,0,*h)
 return bytes(result)

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
 token=plan['nonce_hex']
 if not re.fullmatch('[0-9a-f]{64}',token):raise ValueError('Exact C-init identity required')
 dt=output/'virt-private.dtb'
 common=['qemu-system-aarch64','-machine','virt,gic-version=2,virtualization='+virtualization,'-cpu','cortex-a53','-smp','1','-m','1536','-accel','tcg','-nodefaults','-display','none','-nic','none']
 dump=common[:];dump[dump.index('virt,gic-version=2,virtualization='+virtualization)]+=',dumpdtb='+str(dt)
 dump += ['-serial','stdio','-kernel',str(kernel),'-initrd',str(initrd),'-append','console=ttyAMA0,115200 earlycon=uart8250,mmio32,0x444bf000 keep_bootcon initcall_debug rdinit=/init nr_cpus=1 maxcpus=0 loglevel=8 ignore_loglevel panic=-1']
 subprocess.run(dump,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=15,check=True)
 dt.write_bytes(geometry(reserve(dt.read_bytes()),plan))
 monitor_dir=tempfile.TemporaryDirectory(prefix='ft-vm-');monitor=Path(monitor_dir.name)/'monitor.sock';ring=output/'console-private.bin'
 cmd=common+['-serial','stdio','-monitor','none','-qmp','unix:'+str(monitor)+',server=on,wait=off','-no-reboot','-kernel',str(kernel),'-initrd',str(initrd),'-dtb',str(dt),'-device','loader,addr=0x444bf000,data=0x43474244,data-len=4','-append','console=ttyAMA0,115200 earlycon=uart8250,mmio32,0x444bf000 keep_bootcon initcall_debug rdinit=/init nr_cpus=1 maxcpus=0 loglevel=8 ignore_loglevel panic=-1']
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
  if sig==0x43474244 and start<4084 and start<=size<=4084:
   payload=(raw[12+start:12+4084]+raw[12:12+start]) if size==4084 else raw[12:12+size]
 identity=('FIRETABS_CINIT_V3 nonce='+token+'\n').encode()
 fresh=identity in payload
 run_init=fresh and b'Run /init as init process' in payload
 passed=policy_ok and fresh and run_init and not any(x in text for x in [b'Kernel panic',b'Internal error: Oops',b'avc:  denied'])
 result=dict(scope='Exact RAM-fix Image Cortex-A53 VM with target RAM/no-map geometry; no tablet/physical USB qualification',board_memory_geometry=True,nomap_ranges=len(plan['nomap_ranges']),passed=passed,image_sha256=plan['image_sha256'],vm_initramfs_sha256=plan['initramfs_sha256'],virtualization=virtualization,fresh_console_identity=fresh,run_init_seen=run_init,enforcing_pid1_filesystem_probe=policy_ok,permanent_callback_survived_init_memory_free=run_init,metadata_integrity_stub_executed=False,hardware_execution=False,disk_attached=False,network_attached=False,tablet_commands=False,raw_log_sha256=sha(data),elapsed_seconds=round(time.monotonic()-began,3))
 (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['kernel','initrd','plan','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--virtualization',choices=['on','off'],required=True);a=p.parse_args()
 r=run(a.kernel,a.initrd,json.loads(a.plan.read_text()),a.output,a.virtualization);print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)
