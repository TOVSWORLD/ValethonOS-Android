#!/usr/bin/env python3
"""Package built Android init through the observed graphics LK/RAM path; offline only."""
import argparse,hashlib,json,lzma,os,re,stat,struct,subprocess,zlib
from pathlib import Path
from pack_graphics_boot import assemble,INITRD_ADDRESS
from pack_lab_log_boot import METADATA
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw
from audit_trial_loader_contract import audit

ROOT=Path(__file__).resolve().parents[1]
IMAGE_SHA='c83baf995268af14e0a4ba3faac683ee2ee4d6d1c4717a675d7eaccea20337b6'
MAX_CPIO=8*1024*1024
def sha(data):return hashlib.sha256(data).hexdigest()

def ramdisk(data):
    decoder=zlib.decompressobj(31);archive=decoder.decompress(data,MAX_CPIO+1)
    if len(archive)>MAX_CPIO or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:raise ValueError('One bounded complete Android gzip archive required')
    at=0;entries={};duplicates=[]
    while at+110<=len(archive):
        header=archive[at:at+110]
        if header[:6]!=b'070701':raise ValueError('Android newc header required')
        fields=[int(header[6+i*8:14+i*8],16) for i in range(13)]
        size,namesize=fields[6],fields[11]
        if not 1<=namesize<=256 or at+110+namesize>len(archive):raise ValueError('Invalid cpio name')
        namebytes=archive[at+110:at+110+namesize]
        if namebytes[-1:]!=b'\0' or b'\0' in namebytes[:-1]:raise ValueError('Invalid cpio name terminator')
        name=namebytes[:-1].decode('ascii')
        begin=(at+110+namesize+3)&~3;end=begin+size
        if end>len(archive):raise ValueError('Truncated Android cpio payload')
        at=(end+3)&~3
        if name=='TRAILER!!!':
            if size or any(archive[at:]):raise ValueError('Unexpected cpio trailer data')
            break
        if name.startswith('/') or '..' in name.split('/') or not name:raise ValueError('Unsafe Android cpio path')
        row={'mode':fields[1],'uid':fields[2],'gid':fields[3],'bytes':size,'sha256':sha(archive[begin:end])}
        if name in entries:
            if not stat.S_ISDIR(fields[1]) or entries[name]!=row:raise ValueError('Conflicting duplicate cpio entry')
            duplicates.append(name)
        entries[name]=row
        if name=='init':init=archive[begin:end]
        if name=='fstab.douglas':fstab=archive[begin:end]
    else:raise ValueError('Android cpio trailer missing')
    if 'init' not in entries or not stat.S_ISREG(entries['init']['mode']) or not entries['init']['mode']&0o111:raise ValueError('Executable first-stage init required')
    if len(init)<52 or init[:6]!=b'\x7fELF\x01\x01' or struct.unpack_from('<H',init,18)[0]!=40:raise ValueError('ARM32 first-stage init required')
    phoff=struct.unpack_from('<I',init,28)[0];entsize,count=struct.unpack_from('<HH',init,42)
    if entsize!=32 or not 1<=count<=128 or phoff+count*entsize>len(init):raise ValueError('Invalid init ELF program headers')
    if any(struct.unpack_from('<I',init,phoff+i*entsize)[0]==3 for i in range(count)):raise ValueError('First-stage init must not require a dynamic interpreter')
    expected=(ROOT/'projects/firetabs-android/android-integration/device/init/fstab.douglas').read_bytes()
    if 'fstab.douglas' not in entries or fstab!=expected:raise ValueError('Exact system-only first-stage fstab required')
    return archive,{'compressed_sha256':sha(data),'unpacked_bytes':len(archive),'unpacked_sha256':sha(archive),'entries':entries,'identical_directory_duplicates':duplicates,'first_stage_init_arm32_static':True,'exact_system_only_fstab':True}

def prepare(kernel,template,android_ramdisk,installed_lk,package_lk,output,fdtget,fdtput):
    if output.exists():raise ValueError('Fresh output directory required')
    runtime=json.loads((ROOT/'evidence/graphics-source/graphics-interaction-runtime-result.json').read_text())
    previous=json.loads((template/'report.json').read_text());source=template/'dt/graphics-preview-private.dtb'
    if sha((template/'boot-full.img').read_bytes())!=runtime['candidate_sha256'] or runtime.get('interaction_qualified') is not True or runtime.get('return_to_twrp_verified') is not True:raise ValueError('Observed graphics/return template required')
    if sha(source.read_bytes())!=previous['dt_sha256']:raise ValueError('Observed DT hash mismatch')
    image=(kernel/'Image').read_bytes();compressed=(kernel/'Image.gz').read_bytes()
    if sha(image)!=IMAGE_SHA:raise ValueError('Completed Android-support Image required')
    rd_bytes=android_ramdisk.read_bytes()
    expected=json.loads((ROOT/'evidence/android-integration-source/first-image-build-result.json').read_text())
    if sha(rd_bytes)!=expected['artifacts']['ramdisk.img']['sha256']:raise ValueError('Exact compiled/audited Android ramdisk required')
    archive,rd_report=ramdisk(rd_bytes)
    rd=lzma.compress(archive,format=lzma.FORMAT_XZ,check=lzma.CHECK_CRC32,filters=[{'id':lzma.FILTER_LZMA2,'dict_size':8*1024*1024,'preset':6}])
    if lzma.decompress(rd)!=archive:raise ValueError('Lossless Android ramdisk re-encoding failed')
    nonce=os.urandom(32);output.mkdir(mode=0o700);dt=output/'android-private.dtb';dt.write_bytes(source.read_bytes())
    before=snapshot(fdtget,source);old=raw(before['/chosen']['valethon,direct-trial']).rstrip(b'\0').decode()
    args=raw(before['/chosen']['bootargs']).rstrip(b'\0').decode().split()
    if sum(x=='valethon.direct_trial='+old for x in args)!=1:raise ValueError('Exact prior trial identity required')
    args=[x for x in args if not x.startswith(('valethon.direct_trial=','loglevel='))]
    if any(x.startswith(('androidboot.hardware=','androidboot.selinux=','androidboot.valethon_trial=')) for x in args):raise ValueError('Unexpected prior Android boot arguments')
    args+=['loglevel=3','androidboot.hardware=douglas','androidboot.selinux=enforcing','androidboot.valethon_trial='+nonce.hex()]
    cmdline=' '.join(args)
    if len(cmdline.encode())>=512:raise ValueError('Original header command-line field exceeded')
    for key,value in [('linux,initrd-start',INITRD_ADDRESS),('linux,initrd-end',INITRD_ADDRESS+len(rd))]:
        subprocess.run([str(fdtput),'-t','x',str(dt),'/chosen',key,'0',format(value,'x')],check=True,capture_output=True)
    for key,value in [('bootargs',cmdline),('valethon,direct-trial',nonce.hex())]:
        subprocess.run([str(fdtput),'-t','s',str(dt),'/chosen',key,value],check=True,capture_output=True)
    data=bytearray(dt.read_bytes());data.extend(bytes((-len(data))%4));struct.pack_into('>I',data,4,len(data));dt.write_bytes(data)
    after=snapshot(fdtget,dt)
    if {k:v for k,v in before.items() if k!='/chosen'}!={k:v for k,v in after.items() if k!='/chosen'}:raise ValueError('Hardware/resource/firmware DT changed')
    if set(before['/chosen'])!=set(after['/chosen']):raise ValueError('Unexpected chosen property set')
    candidate,report=assemble(image,compressed,bytes(data),rd,json.loads(METADATA.read_text()))
    candidate=bytearray(candidate);candidate[64:576]=cmdline.encode()+bytes(512-len(cmdline.encode()));candidate=bytes(candidate)
    loader=audit(installed_lk.read_bytes(),package_lk.read_bytes(),candidate,expected_candidate_sha=sha(candidate))
    loader['next_decision']='Static loader/container checks only; use the grouped Android T1 session for physical acceptance. No new instrumentation gate.'
    if loader['candidate']['decoded_sha256']!=IMAGE_SHA or loader['candidate']['dt_sha256']!=sha(data):raise ValueError('Independent original-loader roundtrip failed')
    report.update(scope='Offline integrated Android direct boot package; not physical authorization',partition_sha256=sha(candidate),source_sha256=sha(Path(__file__).read_bytes()),original_pack_source_sha256=sha((ROOT/'scripts/pack_graphics_boot.py').read_bytes()),observed_graphics_template_sha256=runtime['candidate_sha256'],hardware_dt_nodes_unchanged=True,android_ramdisk=rd_report,ramdisk_bytes=len(rd),ramdisk_sha256=sha(rd),dt_sha256=sha(data),nonce_sha256=sha(nonce),loader_static_audit=loader,androidboot_hardware='douglas',androidboot_selinux='enforcing',system_partition_bytes=1692925952,system_backup_required=True,physical_execution_admitted=False,recovery_writes_allowed=False,userdata_writes_allowed=False)
    for name,blob in [('boot-full.img',candidate),('initramfs.cpio.xz',rd),('trial-nonce-private.bin',nonce),('report.json',(json.dumps(report,indent=2)+'\n').encode())]:
        p=output/name;p.write_bytes(blob);p.chmod(0o600)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['kernel','template','android-ramdisk','installed-lk','package-lk','output','fdtget','fdtput']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();r=prepare(**vars(a));print(json.dumps({'offline_package_sha256':r['partition_sha256'],'payload_bytes':r['payload_bytes'],'ramdisk_unpacked_bytes':r['android_ramdisk']['unpacked_bytes'],'hardware_dt_nodes_unchanged':True,'physical_execution_admitted':False}))
