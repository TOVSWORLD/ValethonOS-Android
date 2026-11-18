#!/usr/bin/env python3
"""Exact console, metadata SHA and boot-to-PID1 controls; no tablet connection."""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
from qualify_ack_combined import machine,BASE,ENTRY,CONSOLE
from verify_ack_cinit_bundle import verify
from build_ack_cinit_console import prefix,CAPACITY
from build_ack_combined_entry import integrity_marker
from build_ack_trampoline import marker
from unicorn import arm64_const as r
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def qualify(bundle,kernel,nonce,vm_reports,out,ramfix=False):
 validator=verify
 if ramfix:
  from verify_ack_ramfix_bundle import verify as validator
 validator(bundle/'report.json',kernel,nonce=nonce)
 m=json.loads((bundle/'report.json').read_text());image=(bundle/'image.bin').read_bytes();padded=image+bytes(m['image_memory_bytes']-len(image));meta=(bundle/'metadata.bin').read_bytes();checks={}
 for name,corrupt in [('full_padded_integrity',None),('corrupt_first_page',123),('corrupt_final_padding',len(padded)-1)]:
  data=bytearray(padded)
  if corrupt is not None:data[corrupt]^=1
  c,state=machine(bytes(data),meta);c.emu_start(ENTRY,BASE,timeout=120000000,count=2_000_000_000);raw=bytes(c.mem_read(CONSOLE,65536))
  if corrupt is None:ok=c.reg_read(r.UC_ARM64_REG_PC)==BASE and not state['reset'] and integrity_marker(m['trial_id'],True) in raw and marker(m['trial_id']) in raw
  else:ok=state['reset'] and integrity_marker(m['trial_id'],False) in raw and marker(m['trial_id']) not in raw
  checks[name]=bool(ok)
 names=subprocess.check_output(['aarch64-linux-musl-nm','--defined-only',str(bundle/'console-private/console.elf')],text=True)
 symbols={v[2]:int(v[0],16) for l in names.splitlines() if len(v:=l.split())==3}
 # A synthetic console/device pair carries exactly the offsets independently
 # checked against both compiled setup and compiled UART callback instructions.
 stop,con,dev,text=0x42010000,0x42100000,0x42101000,0x42102000
 for label,header,message in [('small',(0x43474244,0,0),b'PID1 candidate\n'),('wrap',(0x43474244,4000,4000),b'z'*1900),('oversized',(0x43474244,0,0),b'x'*5000+b'TAIL'),('invalid_sig',(0,0,0),b'x'),('invalid_start',(0x43474244,4084,4084),b'x'),('invalid_size',(0x43474244,0,4085),b'x')]:
  c,state=machine(padded,meta,header);c.mem_write(con+104,struct.pack('<Q',dev));c.mem_write(dev+24,struct.pack('<Q',CONSOLE));c.mem_write(text,message)
  preserved=[getattr(r,'UC_ARM64_REG_X'+str(i)) for i in range(18,30)]
  want={reg:0x53000000+idx*16 for idx,reg in enumerate(preserved)}
  for reg,v in want.items():c.reg_write(reg,v)
  c.reg_write(r.UC_ARM64_REG_X0,con);c.reg_write(r.UC_ARM64_REG_X1,text);c.reg_write(r.UC_ARM64_REG_X2,len(message));c.reg_write(r.UC_ARM64_REG_X30,stop)
  before=bytes(c.mem_read(CONSOLE,65536));daif=c.reg_read(r.UC_ARM64_REG_PSTATE)&0x3c0
  c.emu_start(symbols['cinit_write'],stop,count=100000)
  raw=bytes(c.mem_read(CONSOLE,65536));start,size=struct.unpack_from('<II',raw,4)
  preserved_ok=all(c.reg_read(reg)==v for reg,v in want.items()) and c.reg_read(r.UC_ARM64_REG_X30)==stop and c.reg_read(r.UC_ARM64_REG_PSTATE)&0x3c0==daif
  if label.startswith('invalid'):ok=raw==before
  else:
   payload=raw[12+start:4096]+raw[12:12+start] if size==CAPACITY else raw[12:12+size]
   ok=prefix(nonce.hex()) in payload and message[-2048:] in payload and start<CAPACITY and size<=CAPACITY and raw[4096:]==before[4096:]
  checks['console_'+label]=bool(ok and preserved_ok and not state['reset'])
 # Setup is entered after the preserved PACIASP; A53 treats PAC as HINT.
 for label,valid in [('valid',True),('invalid_signature',False)]:
  c,state=machine(padded,meta,(0x43474244 if valid else 0,0,0));c.mem_write(dev,struct.pack('<Q',con));c.mem_write(dev+24,struct.pack('<Q',CONSOLE));c.mem_write(con+104,struct.pack('<Q',dev))
  c.reg_write(r.UC_ARM64_REG_X0,dev);c.reg_write(r.UC_ARM64_REG_X30,stop);c.reg_write(r.UC_ARM64_REG_SP,0x42200000)
  c.emu_start(symbols['cinit_setup'],stop,count=100000)
  result=c.reg_read(r.UC_ARM64_REG_X0)&0xffffffff;raw=bytes(c.mem_read(CONSOLE,4096));callback=struct.unpack('<Q',c.mem_read(con+16,8))[0]
  checks['setup_'+label]=result==(0 if valid else 0xffffffed) and (not valid or callback==symbols['cinit_write'] and b'retained_early_console_ready' in raw)
 vms=[json.loads(p.read_text()) for p in vm_reports]
 checks['exact_image_both_vm_modes_pid1_after_init_free']=len(vms)==2 and {v['virtualization'] for v in vms}=={'off','on'} and all(v['passed'] and v['image_sha256']==digest(bundle/'image.bin') and v['run_init_seen'] and v['enforcing_pid1_filesystem_probe'] and v['permanent_callback_survived_init_memory_free'] for v in vms)
 paths=['scripts/build_ack_cinit_console.py','scripts/prepare_ack_cinit_bundle.py','scripts/verify_ack_cinit_bundle.py','scripts/qualify_ack_cinit.py','scripts/validate_ack_cinit_vm.py','scripts/build_ack_combined_entry.py','scripts/qualify_ack_combined.py','projects/firetabs-android/native-kexec/combined_sha256.c']
 if ramfix:
  paths+=['scripts/prepare_ack_ramfix_bundle.py','scripts/verify_ack_ramfix_bundle.py','scripts/validate_ack_ramfix_vm.py']
  checks['target_memory_geometry_vm']=all(v.get('board_memory_geometry') is True for v in vms)
 result=dict(scope='Offline exact C-init Image/console/integrity qualification; no tablet commands',all_tests_passed=all(checks.values()),tests_skipped=0,checks=checks,image_sha256=digest(bundle/'image.bin'),metadata_sha256=digest(bundle/'metadata.bin'),source_sha256={p:digest(ROOT/p) for p in paths},vm_reports_sha256=[digest(p) for p in vm_reports],hardware_execution=False,target_pid1_proven=False)
 out.write_text(json.dumps(result,indent=2)+'\n')
 if not result['all_tests_passed']:raise ValueError('Qualification failed: '+','.join(k for k,v in checks.items() if not v))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['bundle','kernel','nonce-file','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--vm-report',type=Path,action='append',required=True);p.add_argument('--ramfix',action='store_true');a=p.parse_args();print(json.dumps(qualify(a.bundle,a.kernel,a.nonce_file.read_bytes(),a.vm_report,a.output,a.ramfix),indent=2))
