#!/usr/bin/env python3
"""Independent exact first-draft byte checks; no physical operations."""
import argparse
from pathlib import Path
import json,hashlib,struct,zlib,gzip,subprocess,sys
import retained_log_mailbox as mailbox
from inspect_boot_image import inspect
from measure_arm64_image import measure

def verify(p):
    r=json.loads((p/'report.json').read_text());image=(p/'boot-full.img').read_bytes();nonce=(p/'nonce-private.bin').read_bytes()
    sha=lambda data:hashlib.sha256(data).hexdigest()
    for name,facts in r['artifacts'].items():
     data=(p/name).read_bytes();assert facts=={'bytes':len(data),'sha256':sha(data)}
    assert len(image)==16777216 and sha(image)==r['partition_sha256']
    layout=inspect(image,16777216)
    k,entry,rd,rdaddr,second,secondaddr,tags,page,version,osversion=struct.unpack_from('<10I',image,8)
    assert page==2048 and version==0 and second==0 and tags==0x48000000 and rdaddr==0x43480000
    kernel=image[page:page+k];d=zlib.decompressobj(31);raw=d.decompress(kernel,64*1024*1024);assert d.eof and raw==(p/'Image').read_bytes()
    used=len(kernel)-len(d.unused_data);assert kernel[used:(used+3)&~3]==bytes((-used)%4)
    assert kernel[(used+3)&~3:]==(p/'draft.dtb').read_bytes()
    assert kernel[:used]==(p/'Image.gz').read_bytes()
    ramdisk_at=page+((k+page-1)//page)*page;ramdisk=image[ramdisk_at:ramdisk_at+rd]
    assert ramdisk==(p/'initramfs.cpio.gz').read_bytes()
    archive=gzip.decompress(ramdisk);assert archive.count(nonce)==1
    identifier=hashlib.sha1()
    for data in [kernel,ramdisk,b'']:identifier.update(data);identifier.update(struct.pack('<I',len(data)))
    assert image[576:596]==identifier.digest()
    assert image[64:576].split(b'\0')[0].decode()==r['bootargs']
    assert entry==0x40000000+struct.unpack_from('<Q',raw,8)[0]
    size=measure(raw,kernel[:used]);assert size['decoded_file_fits_lk_capacity']
    assert 0x40000000+size['image_size']<0x42000000
    fdt=Path(__file__).resolve().parents[1]/'work/dtb-tool/build/fdtget'
    def get(node,prop,kind='s'):
     return subprocess.check_output([str(fdt),'-t'+kind,str(p/'draft.dtb'),node,prop],text=True).strip()
    assert get('/chosen','bootargs')==r['bootargs']
    assert bytes(int(v,16) for v in get('/chosen','valethon,trial-nonce','bx').split())==nonce
    assert get('/soc/usb@11200000','status')=='okay' and get('/soc/usb@11200000','dr_mode')=='peripheral'
    assert get('/soc/t-phy@11210000','status')=='okay'
    assert get('/soc/mmc@11230000','status')=='okay' and int(get('/soc/mmc@11230000','max-frequency','u'))==26000000
    mailbox.validate_seed(image,nonce,r['prefix_sha256']);state=mailbox.inspect(image,nonce,r['prefix_sha256'])
    assert state['latest']['sequence']==1 and state['latest']['payload'].startswith(b'VALETHON HOST CONTROL v1\n') and not state['invalid_slots']
    symbols=(p/'System.map').read_text();assert 'mailbox_init' in symbols and 'mt8163_dsi_driver_data' in symbols and 'mt8163_mipitx_data' in symbols
    assert 'valethon_lab_entry_screen' not in symbols and 'valethon_entry_delay' not in symbols
    result={'scope':'Independent final-byte checks, not physical acceptance','passed':True,'partition_sha256':sha(image),'files_verified':len(r['artifacts']),'android_component_ID_valid':True,'exact_Image_DT_ramdisk_nonce_binding':True,'USB0_peripheral_and_emmc_enabled':True,'runtime_fits_below_inflate_stack':True,'initial_mailbox_host_control_only':True,'old_entry_instrumentation_absent':True,'physical_access':False}
    (p/'independent-verification.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--folder',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(verify(args.folder),indent=2))
