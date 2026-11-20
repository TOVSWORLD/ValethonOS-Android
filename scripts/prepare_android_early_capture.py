#!/usr/bin/env python3
"""Offline combined diagnostic boot: original Android /init, builtin USB, RAM+boot-tail retention."""
import argparse,gzip,hashlib,json,lzma,os,struct,subprocess
from pathlib import Path
from prepare_android_direct_boot import ramdisk,sha
from build_diagnostic_initramfs import archive,inspect_elf
from pack_graphics_boot import assemble,INITRD_ADDRESS,CONTRACT
from pack_lab_log_boot import METADATA
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw
import retained_log_mailbox as mailbox
ROOT=Path(__file__).resolve().parents[1]

def config_values(data):
 values={}
 for line in data.decode().splitlines():
  if line.startswith('CONFIG_') and '=' in line:
   k,v=line.split('=',1);values[k]=v
  elif line.startswith('# CONFIG_') and line.endswith(' is not set'):values[line[2:-11]]='n'
 return values

def kernel_check(kernel,parent):
 report=json.loads((kernel/'result.json').read_text())
 for name,digest in report['artifacts'].items():
  if name not in ['arch/arm64/boot/Image','arch/arm64/boot/Image.gz','.config','System.map'] or sha((kernel/name).read_bytes())!=digest:raise ValueError('Kernel artifact mismatch')
 before=config_values(parent);after=config_values((kernel/'.config').read_bytes())
 delta={k:[before.get(k),after.get(k)] for k in set(before)|set(after) if before.get(k)!=after.get(k)}
 allowed={'CONFIG_U_SERIAL_CONSOLE','CONFIG_USB_G_SERIAL','CONFIG_USB_F_SERIAL','CONFIG_USB_F_OBEX'}
 if set(delta)-allowed or any(after.get(k)!='y' for k in ['CONFIG_U_SERIAL_CONSOLE','CONFIG_USB_G_SERIAL','CONFIG_PSTORE','CONFIG_PSTORE_RAM','CONFIG_PSTORE_CONSOLE']):raise ValueError('Unreviewed kernel configuration delta')
 if delta!=report['delta']:raise ValueError('Kernel delta receipt mismatch')
 if gzip.decompress((kernel/'arch/arm64/boot/Image.gz').read_bytes())!=(kernel/'arch/arm64/boot/Image').read_bytes():raise ValueError('Kernel compression mismatch')
 return delta

def augment(whole,wrapper):
 unpacked,report=ramdisk(whole);inspect_elf(wrapper)
 if 'valethon-preinit' in report['entries']:raise ValueError('Existing wrapper forbidden')
 # Preserve each original header/payload byte, cutting only the trailer and padding.
 at=0
 while True:
  header=unpacked[at:at+110];fields=[int(header[6+i*8:14+i*8],16) for i in range(13)]
  name=unpacked[at+110:at+110+fields[11]-1]
  if name==b'TRAILER!!!':break
  at=(((at+110+fields[11]+3)&~3)+fields[6]+3)&~3
 result=unpacked[:at]+archive([('valethon-preinit',0o100500,wrapper,(0,0))])
 if not result.startswith(unpacked[:at]):raise ValueError('Original ramdisk changed')
 return result,report

def prepare(kernel,parent_config,base,android_ramdisk,wrapper,output,get,put,readout=False):
 if output.exists():raise ValueError('Fresh output required')
 delta=kernel_check(kernel,parent_config.read_bytes())
 expected=json.loads((ROOT/'evidence/android-integration-source/first-image-build-result.json').read_text())
 if sha(android_ramdisk.read_bytes())!=expected['artifacts']['ramdisk.img']['sha256']:raise ValueError('Exact completed Android ramdisk required')
 source=base/'android-private.dtb';old=json.loads((base/'report.json').read_text())
 if sha(source.read_bytes())!=old['dt_sha256'] or sha((base/'boot-full.img').read_bytes())!=old['partition_sha256']:raise ValueError('Previous Android package mismatch')
 unpacked,rdreport=augment(android_ramdisk.read_bytes(),wrapper.read_bytes())
 rd=lzma.compress(unpacked,format=lzma.FORMAT_XZ,check=lzma.CHECK_CRC32,filters=[{'id':lzma.FILTER_LZMA2,'dict_size':8388608,'preset':6}])
 nonce=os.urandom(32);output.mkdir(mode=0o700);dt=output/'android-private.dtb';dt.write_bytes(source.read_bytes())
 before=snapshot(get,source)
 args=raw(before['/chosen']['bootargs']).rstrip(b'\0').decode().split()
 args=[v for v in args if not v.startswith(('console=ttyGS','loglevel=','rdinit=','androidboot.valethon_trial=','g_serial.'))]
 args+=['console=ttyGS0','loglevel=7','rdinit=/valethon-preinit','g_serial.enable=1','androidboot.valethon_trial='+nonce.hex()]
 if readout:args+=['valethon.capture_readout=1']
 cmdline=' '.join(args)
 if len(cmdline.encode())>=512:raise ValueError('Header command line exceeds limit')
 def setprop(path,key,*values,kind='x'):subprocess.run([str(put),'-t',kind,str(dt),path,key,*values],check=True,capture_output=True)
 setprop('/chosen','bootargs',cmdline,kind='s');setprop('/chosen','valethon,direct-trial',nonce.hex(),kind='s')
 setprop('/chosen','valethon,trial-nonce',*[f'{x:02x}' for x in nonce],kind='bx')
 setprop('/chosen','linux,initrd-start','0',f'{INITRD_ADDRESS:x}');setprop('/chosen','linux,initrd-end','0',f'{INITRD_ADDRESS+len(rd):x}')
 # Reuse only the documented pstore subrange inside the unchanged 2MiB reservation.
 # Root platform node avoids introducing overlapping reserved-memory children.
 subprocess.run([str(put),'-c',str(dt),'/ramoops@44410000'],check=True,capture_output=True)
 setprop('/ramoops@44410000','compatible','ramoops',kind='s')
 for name,values in [('reg',['0','44410000','0','e0000']),('record-size',['10000']),('console-size',['10000']),('max-reason',['2'])]:setprop('/ramoops@44410000',name,*values)
 after=snapshot(get,dt)
 if {k:v for k,v in before.items() if k!='/chosen'}!={k:v for k,v in after.items() if k not in ['/chosen','/ramoops@44410000']}:raise ValueError('Unexpected hardware DT delta')
 blob=bytearray(dt.read_bytes());blob.extend(bytes(-len(blob)%4));struct.pack_into('>I',blob,4,len(blob));dt.write_bytes(blob)
 full,report=assemble((kernel/'arch/arm64/boot/Image').read_bytes(),(kernel/'arch/arm64/boot/Image.gz').read_bytes(),bytes(blob),rd,json.loads(METADATA.read_text()))
 full=bytearray(full);full[64:576]=bytes(512);full[64:64+len(cmdline)]=cmdline.encode();full=bytes(full)
 if report['payload_bytes']>mailbox.BASE:raise ValueError('Payload overlaps reserved boot-tail slots')
 full,prefix=mailbox.prepare(full,nonce,b'VALETHON HOST CONTROL v1\nNot kernel output.\n');mailbox.inspect(full,nonce,prefix)
 report.update(scope='Combined early capture candidate; no device execution',partition_sha256=sha(full),dt_sha256=sha(bytes(blob)),kernel_config_delta=delta,original_android_init_unchanged=True,wrapper_sha256=sha(wrapper.read_bytes()),ramdisk_sha256=sha(rd),nonce_sha256=sha(nonce),retained_prefix_sha256=prefix,ramoops_region={'address':0x44410000,'bytes':0xe0000,'console_bytes':65536,'record_bytes':65536},retention_qualified=False,boot_tail_snapshot_interval_seconds=5,boot_tail_panic_guaranteed=False,kernel_usb_console_panic_delivery_guaranteed=False,android_adb_available=False,diagnostic_usb_owns_udc=True,collection_only=readout,system_rewrite_required=False,recovery_writes_allowed=False,userdata_writes_allowed=False)
 for name,data in [('boot-full.img',full),('initramfs.cpio.xz',rd),('trial-nonce-private.bin',nonce),('report.json',(json.dumps(report,indent=2)+'\n').encode())]:
  with (output/name).open('xb') as f:f.write(data)
 return report

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['kernel','parent-config','base','android-ramdisk','wrapper','output','get','put']:p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--readout',action='store_true')
 a=p.parse_args();r=prepare(a.kernel,a.parent_config,a.base,a.android_ramdisk,a.wrapper,a.output,a.get,a.put,a.readout);print(json.dumps({'prepared':True,'payload_bytes':r['payload_bytes'],'tablet_executed':False}))
