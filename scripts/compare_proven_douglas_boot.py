#!/usr/bin/env python3
"""Read-only comparison of existing known-boot and diagnostic artifacts."""
import argparse,hashlib,json,struct,zlib
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def inspect(path):
 b=path.read_bytes();k,entry,ramdisk,rd,second,second_at,tags,page,dt,_=struct.unpack_from('<10I',b,8);assert b[:8]==b'ANDROID!' and page==2048
 dec=zlib.decompressobj(31);image=dec.decompress(b[page:page+k]);assert dec.eof and image[56:60]==b'ARMd'
 out={'partition_sha256':sha(b),'kernel_entry':hex(entry),'image_text_offset':hex(struct.unpack_from('<Q',image,8)[0]),'image_size':struct.unpack_from('<Q',image,16)[0],'page_bytes':page,'tags_address':hex(tags),'ramdisk_header_address':hex(rd),'decoded_kernel_sha256':sha(image),'cmdline':b[64:576].split(b'\0')[0].decode(),'appended_data_bytes':len(dec.unused_data)}
 pos=image.find(b'IKCFG_ST')
 if pos>=0:
  cfg=zlib.decompress(image[pos+8:],31).decode();keys=['CONFIG_ARM64','CONFIG_USB_G_ANDROID','CONFIG_USB_CONFIGFS','CONFIG_USB_CONFIGFS_ACM','CONFIG_USB_MTK_HDRC','CONFIG_MTK_RAM_CONSOLE','CONFIG_PSTORE','CONFIG_PSTORE_RAM','CONFIG_SECURITY_SELINUX'];values={}
  for line in cfg.splitlines():
   for key in keys:
    if line.startswith(key+'='):values[key]=line.split('=',1)[1]
    elif line=='# '+key+' is not set':values[key]='n'
  out['embedded_config_sha256']=sha(cfg.encode());out['embedded_config_selected']=values
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--known',type=Path,required=True);p.add_argument('--diagnostic',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();known=inspect(a.known);diag=inspect(a.diagnostic)
 r={'scope':'Offline existing artifact comparison, not a new device test','known_normal':known,'mainline_diagnostic':diag,'interpretation':['Known normal kernel is ARM64, not proof that all ARM64 kernels satisfy this firmware contract.','Different text offsets imply different valid entry addresses; copying the legacy address without changing Image placement would be wrong.','Header/cmdline differences are hypotheses, not proved causes.','Current diagnostic DT builder deliberately disables USB; absent USB does not establish absence of kernel entry.'],'recommended_control':'Preserve existing bootstrap; evaluate a self-contained diagnostic control using the already-booted kernel/DT and established USB logging before another mainline/custom-observer trial.','no_device_access':True,'trial8_selected_for_execution':False}
 a.output.write_text(json.dumps(r,indent=2)+'\n');print('Existing known ARM64 boot and diagnostic artifact comparison saved')
