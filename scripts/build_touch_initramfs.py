#!/usr/bin/env python3
"""Build a separate enforcing, read-only evdev visual test component; never boot it."""
import argparse,gzip,hashlib,json,re,secrets,shutil,subprocess
from pathlib import Path
from build_diagnostic_initramfs import archive,inspect_elf
from generate_goodix_config import configuration,SOURCE as BOARD
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'projects/firetabs-android/diagnostic-usb'
sha=lambda b:hashlib.sha256(b).hexdigest()


def check_archive(raw,entries):
    expected=entries+[('TRAILER!!!',0,b'',(0,0))];at=0
    for index,(name,mode,payload,device) in enumerate(expected,1):
        if raw[at:at+6]!=b'070701':raise ValueError('Invalid touch archive header')
        fields=[int(raw[at+6+i*8:at+14+i*8],16) for i in range(13)]
        encoded=name.encode()+b'\0';start=at+110
        if fields!=[index,mode,0,0,1,0,len(payload),0,0,*device,len(encoded),0] or raw[start:start+len(encoded)]!=encoded:raise ValueError('Touch archive ownership/node differs')
        end=start+len(encoded);start=(end+3)&~3
        if any(raw[end:start]) or raw[start:start+len(payload)]!=payload:raise ValueError('Touch archive contents differ')
        end=start+len(payload);at=(end+3)&~3
        if any(raw[end:at]):raise ValueError('Nonzero touch archive padding')
    if any(raw[at:]):raise ValueError('Unexpected touch archive tail')


def entries(elf,config):
    result=[(n,0o040755,b'',(0,0)) for n in ['dev','proc','sys','security','config','lib','lib/firmware','lib/firmware/goodix']]
    result += [('dev/input',0o040555,b'',(0,0)),('dev/console',0o020600,b'',(5,1)),('dev/kmsg',0o020400,b'',(1,11)),('dev/firetabs-boot',0o060400,b'',(179,5))]
    result += [('dev/input/event'+str(i),0o020400,b'',(13,64+i)) for i in range(16)]
    result += [('lib/firmware/goodix/douglas-gt9xx.cfg',0o100400,config,(0,0)),('init',0o100500,elf,(0,0))]
    return result


def build(policy,policy_report,output):
    report=json.loads(policy_report.read_text());blob=policy.read_bytes()
    controls={'enforcement_toggle','policy_reload','block_read','reboot_capability','pid1_fork','pid1_domain_escape','block_write','block_ioctl','block_create','block_relabel','other_block_open','input_write','input_ioctl','input_create','input_relabel','input_block_open'}
    if (report.get('touch_input_profile') is not True or report.get('storage_readonly_profile') is not True or report.get('policy_version')!=33 or report.get('policy_sha256')!=sha(blob) or len(blob)!=report['policy_bytes'] or report.get('permissive_domains') is not False or report.get('unknown_permissions')!='deny' or set(report['forbidden_privilege_mutations_rejected'])!=controls or not all(report['forbidden_privilege_mutations_rejected'].values())):raise ValueError('Exact enforcing touch policy and negative controls required')
    if set(report['source_sha256'])!={'ack-abi.cil','storage-readonly.cil','touch-input.cil'}:raise ValueError('Policy source closure differs')
    for name,want in report['source_sha256'].items():
        if sha((SOURCE/'policy'/name).read_bytes())!=want:raise ValueError('Touch policy source drift')
    output.mkdir(mode=0o700,parents=True);nonce=secrets.token_bytes(32)
    def array(name,b):return 'static const unsigned char '+name+'[]={\n'+',\n'.join(','.join('0x%02x'%v for v in b[i:i+16]) for i in range(0,len(b),16))+'\n};\n'
    (output/'lab_inputs.h').write_text(array('lab_policy_blob',blob)+array('lab_trial_nonce',nonce));(output/'trial-nonce-private.bin').write_bytes(nonce)
    linker=shutil.which('ld.lld-18')
    if not linker:raise ValueError('Pinned LLVM18 linker required')
    cmd=['clang-18','--target=aarch64-linux-gnu','--ld-path='+linker,'-nostdlib','-static','-Os','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-stack-protector','-mgeneral-regs-only','-Wl,--build-id=none,-e,_start','-I',str(output),'-o',str(output/'init'),str(SOURCE/'touch_init.c'),str(SOURCE/'memory.c'),str(ROOT/'projects/firetabs-android/native-kexec/combined_sha256.c')]
    result=subprocess.run(cmd,capture_output=True,timeout=90);(output/'compile-private.log').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Touch component compile failed; inspect private log')
    elf=(output/'init').read_bytes();inspection=inspect_elf(elf);config=configuration(BOARD.read_text());items=entries(elf,config);raw=archive(items);check_archive(raw,items)
    packed=bytearray(gzip.compress(raw,mtime=0));packed[9]=255;packed=bytes(packed)
    if gzip.decompress(packed)!=raw or elf.count(blob)!=1 or nonce not in elf or b'VALETHON TOUCH TEST' not in elf:raise ValueError('Touch component identity/policy differs')
    (output/'initramfs.cpio.gz').write_bytes(packed)
    final={'scope':'Standalone visual touch component only; no device admission','touch_input_profile':True,'display_functional_profile':True,'display_errors_profile':True,'storage_readonly_profile':True,'storage_probe_enabled':False,'policy_sha256':sha(blob),'policy_report_sha256':sha(policy_report.read_bytes()),'nonce_sha256':sha(nonce),'elf':inspection,'archive_entries':[n for n,*_ in items],'touch_config_sha256':sha(config),'touch_nodes':{'major':13,'first_minor':64,'count':16,'read_only':True},'builder_sha256':sha(Path(__file__).read_bytes()),'archive_builder_sha256':sha((ROOT/'scripts/build_diagnostic_initramfs.py').read_bytes()),'sources_sha256':{p.name:sha(p.read_bytes()) for p in SOURCE.iterdir() if p.suffix in ['.c','.h']},'artifacts':{n:{'bytes':len(b),'sha256':sha(b)} for n,b in [('init',elf),('initramfs.cpio.gz',packed)]},'physical_execution_admitted':False,'reboot_interface':False,'raw_input_events_stored':False}
    (output/'report.json').write_text(json.dumps(final,indent=2)+'\n')
    for p in output.iterdir():
        if p.is_file():p.chmod(0o600)
    return final


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['policy','policy-report','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();build(a.policy,a.policy_report,a.output);print('Enforcing visual touch component built; no hardware execution.')
