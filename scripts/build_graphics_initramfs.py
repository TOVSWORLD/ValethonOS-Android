#!/usr/bin/env python3
"""Build physical/VM graphics components; never package or operate a tablet."""
import argparse, hashlib, json, lzma, os, posixpath, re, secrets, shutil, struct, subprocess
from pathlib import Path
from build_diagnostic_initramfs import archive, inspect_elf
from build_touch_initramfs import entries as touch_entries, check_archive
from generate_goodix_config import configuration, SOURCE as BOARD
from build_graphics_userspace import MESA_SHA, DRM_SHA
ROOT = Path(__file__).resolve().parents[1]
DIAG = ROOT/'projects/firetabs-android/diagnostic-usb'
GRAPHICS = ROOT/'projects/firetabs-android/graphics'
sha = lambda b: hashlib.sha256(b).hexdigest()


def elf(data):
    if len(data)<64 or data[:7]!=b'\x7fELF\x02\x01\x01' or struct.unpack_from('<H',data,18)[0]!=183 or struct.unpack_from('<H',data,16)[0] not in [2,3]:
        raise ValueError('AArch64 ELF required')
    offset=struct.unpack_from('<Q',data,32)[0];size,count=struct.unpack_from('<HH',data,54)
    if size!=56 or not 0<count<128 or offset+size*count>len(data): raise ValueError('ELF headers differ')
    headers=[struct.unpack_from('<IIQQQQQQ',data,offset+i*size) for i in range(count)]
    for p in headers:
        if p[2]+p[5]>len(data) or p[5]>p[6] or p[6]>128*1024*1024: raise ValueError('Bounded ELF segment required')
    interp=None;needed=[]
    for p in headers:
        if p[0]==3:
            b=data[p[2]:p[2]+p[5]]
            if b!=b'/lib/ld-linux-aarch64.so.1\0': raise ValueError('Pinned AArch64 interpreter required')
            interp=b[:-1].decode()
        if p[0]!=2: continue
        tags=[]
        for at in range(p[2],p[2]+p[5],16):
            tag,value=struct.unpack_from('<qQ',data,at)
            if tag==0: break
            tags.append((tag,value))
        strings=[v for t,v in tags if t==5];lengths=[v for t,v in tags if t==10]
        if not strings and not any(t==1 for t,_ in tags): continue
        if len(strings)!=1 or len(lengths)!=1: raise ValueError('Dynamic string table differs')
        matches=[h[2]+strings[0]-h[3] for h in headers if h[0]==1 and h[3]<=strings[0]<h[3]+h[5]]
        if len(matches)!=1 or matches[0]+lengths[0]>len(data): raise ValueError('Dynamic string extent differs')
        table=data[matches[0]:matches[0]+lengths[0]]
        for tag,value in tags:
            if tag!=1: continue
            if value>=len(table) or b'\0' not in table[value:]: raise ValueError('Dynamic dependency is unterminated')
            name=table[value:].split(b'\0',1)[0].decode()
            if not re.fullmatch(r'[A-Za-z0-9_.+-]+',name): raise ValueError('Bounded dependency basename required')
            needed.append(name)
    return {'machine':'AArch64','interpreter':interp,'needed':needed}


def build(policy, policy_report, runtime, runtime_report, output):
    proof=json.loads(policy_report.read_text());binary=policy.read_bytes();runtime_proof=json.loads(runtime_report.read_text())
    if (proof.get('graphics_render_profile') is not True or proof.get('touch_input_profile') is not True
            or proof.get('policy_version')!=33 or proof.get('policy_sha256')!=sha(binary)
            or proof.get('permissive_domains') is not False or proof.get('unknown_permissions')!='deny'
            or len(proof['forbidden_privilege_mutations_rejected'])!=20
            or not all(proof['forbidden_privilege_mutations_rejected'].values())):
        raise ValueError('Exact enforcing graphics policy and20 controls required')
    if set(proof['source_sha256'])!={'ack-abi.cil','storage-readonly.cil','touch-input.cil','graphics-render.cil'}:
        raise ValueError('Graphics policy closure differs')
    for name,want in proof['source_sha256'].items():
        if sha((DIAG/'policy'/name).read_bytes())!=want: raise ValueError('Policy source drift')
    if (runtime_proof.get('compiled') is not True or runtime_proof.get('target')!='aarch64-linux-gnu'
            or runtime_proof.get('mesa_source_sha256')!=MESA_SHA or runtime_proof.get('libdrm_source_sha256')!=DRM_SHA):
        raise ValueError('Completed pinned runtime build required')
    output.mkdir(mode=0o700,parents=True);nonce=secrets.token_bytes(32)
    def array(name,b):return 'static const unsigned char '+name+'[]={\n'+',\n'.join(','.join('0x%02x'%v for v in b[i:i+16]) for i in range(0,len(b),16))+'\n};\n'
    (output/'lab_inputs.h').write_text(array('lab_policy_blob',binary)+array('lab_trial_nonce',nonce))
    (output/'trial-nonce-private.bin').write_bytes(nonce)
    def compile(name,args):
        r=subprocess.run([str(a) for a in args],capture_output=True,timeout=180);(output/(name+'-private.log')).write_bytes(r.stdout+r.stderr)
        if r.returncode: raise ValueError(name+' compile failed; inspect private log')
    linker=shutil.which('ld.lld-18')
    if not linker: raise ValueError('Pinned LLVM18 linker required')
    static=['clang-18','--target=aarch64-linux-gnu','--ld-path='+linker,'-nostdlib','-static','-Os','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-stack-protector','-mgeneral-regs-only','-Wl,--build-id=none,-e,_start','-I',output,'-I',DIAG]
    for target,source in [('init','bootstrap.c'),('vm-init','vm_bootstrap.c')]:
        compile(target,[*static,GRAPHICS/source,DIAG/'memory.c',ROOT/'projects/firetabs-android/native-kexec/combined_sha256.c','-o',output/target]);inspect_elf((output/target).read_bytes())
        content=(output/target).read_bytes()
        if content.count(binary)!=1 or nonce not in content: raise ValueError('Graphics bootstrap policy/identity differs')
    dynamic=['clang-18','--target=aarch64-linux-gnu','--gcc-toolchain=/usr','--ld-path='+linker,'-Os','-Wall','-Wextra','-Werror','-fPIE','-pie','-Wl,-z,relro,-z,now','-I',DIAG,'-I',runtime/'include','-I',runtime/'include/libdrm','-L',runtime/'lib','-Wl,-rpath-link,'+str(runtime/'lib')]
    for target,source in [('graphics','demo.c'),('graphics-vm','vm.c')]:
        compile(target,[*dynamic,GRAPHICS/source,'-lEGL','-lGLESv2','-lgbm','-ldrm','-lm','-ldl','-o',output/target])
        if elf((output/target).read_bytes())['interpreter']!='/lib/ld-linux-aarch64.so.1': raise ValueError('Dynamic graphics interpreter missing')
    files={};aliases={};closure={};pending=[]
    def locate(name):
        for p in [runtime/'lib'/name,runtime/'lib/dri'/name,Path('/usr/aarch64-linux-gnu/lib')/name]:
            if p.is_file(): return p
        p=Path(subprocess.check_output(['aarch64-linux-gnu-gcc','-print-file-name='+name],text=True).strip())
        if p.is_absolute() and p.is_file(): return p
        raise ValueError('Missing AArch64 runtime dependency: '+name)
    def library(path,alias):
        original=path.resolve();data=original.read_bytes();info=elf(data);name='lib/'+original.name
        if name in files:
            if closure[name]['source_sha256']!=sha(data): raise ValueError('Conflicting library basename')
        else:
            if original.is_relative_to(runtime.resolve()):
                relative=str(original.relative_to(runtime.resolve()));want=runtime_proof['runtime_files'].get(relative)
                if want!={'bytes':len(data),'sha256':sha(data)}: raise ValueError('Runtime build artifact drift')
            tmp=output/('stripped-'+original.name);tmp.write_bytes(data)
            subprocess.run(['aarch64-linux-gnu-strip','--strip-unneeded',str(tmp)],check=True,capture_output=True)
            stripped=tmp.read_bytes();elf(stripped);files[name]=stripped
            closure[name]={'source_sha256':sha(data),'sha256':sha(stripped),'bytes':len(stripped),**info}
            pending.extend(info['needed'])
        if alias!=name:
            target=posixpath.relpath(name,posixpath.dirname(alias));old=aliases.get(alias)
            if old and old!=target: raise ValueError('Conflicting library alias')
            aliases[alias]=target
    for program in ['graphics','graphics-vm']:pending.extend(elf((output/program).read_bytes())['needed'])
    library(runtime/'lib/libgallium-26.2.7.so','lib/libgallium-26.2.7.so')
    library(runtime/'lib/gbm/dri_gbm.so','lib/gbm/dri_gbm.so')
    library(locate('ld-linux-aarch64.so.1'),'lib/ld-linux-aarch64.so.1')
    visited=set()
    while pending:
        name=pending.pop()
        if name in visited:continue
        visited.add(name);library(locate(name),'lib/'+name)
    for name,target in aliases.items():
        if posixpath.normpath(posixpath.join(posixpath.dirname(name),target)) not in files: raise ValueError('Library symlink escapes closure')
    artifacts={}
    for variant,init,program in [('initramfs.cpio.xz','init','graphics'),('vm-only-initramfs.cpio.xz','vm-init','graphics-vm')]:
        items=touch_entries((output/init).read_bytes(),configuration(BOARD.read_text()))
        items += [('dev/dri',0o040555,b'',(0,0)),('dev/null',0o020600,b'',(1,3)),('dev/urandom',0o020400,b'',(1,9)),('lib/dri',0o040755,b'',(0,0)),('lib/gbm',0o040755,b'',(0,0))]
        items += [('dev/dri/card'+str(i),0o020600,b'',(226,i)) for i in range(4)]
        items += [('dev/dri/renderD'+str(128+i),0o020600,b'',(226,128+i)) for i in range(4)]
        items += [('graphics',0o100500,(output/program).read_bytes(),(0,0))]
        loader=posixpath.normpath(posixpath.join('lib',aliases.get('lib/ld-linux-aarch64.so.1','ld-linux-aarch64.so.1')))
        items += [(name,0o100500 if name==loader else 0o100400,data,(0,0)) for name,data in sorted(files.items())]
        items += [(name,0o120777,target.encode(),(0,0)) for name,target in sorted(aliases.items())]
        if len({name for name,*_ in items})!=len(items): raise ValueError('Duplicate graphics archive entry')
        raw=archive(items);check_archive(raw,items)
        packed=lzma.compress(raw,format=lzma.FORMAT_XZ,check=lzma.CHECK_CRC32,filters=[{'id':lzma.FILTER_LZMA2,'preset':6}])
        (output/(variant+'-size-private.json')).write_text(json.dumps({'raw_bytes':len(raw),'packed_bytes':len(packed)}))
        if len(raw)>30*1024*1024 or len(packed)>7*1024*1024 or lzma.decompress(packed)!=raw: raise ValueError('Graphics archive exceeds reviewed budget')
        (output/variant).write_bytes(packed);artifacts[variant]={'bytes':len(packed),'sha256':sha(packed),'unpacked_bytes':len(raw),'unpacked_sha256':sha(raw),'compression':'xz-lzma2-8m-crc32'}
    for name in ['init','vm-init','graphics','graphics-vm']:b=(output/name).read_bytes();artifacts[name]={'bytes':len(b),'sha256':sha(b)}
    final={'scope':'Physical/VM graphics components only; no device admission','graphics_render_profile':True,'policy_sha256':sha(binary),'policy_report_sha256':sha(policy_report.read_bytes()),'nonce_sha256':sha(nonce),'runtime_build_report_sha256':sha(runtime_report.read_bytes()),'artifacts':artifacts,'runtime_closure':closure,'library_aliases':aliases,'pid1_fork_allowed':False,'gallium_threading_enabled':False,'disk_shader_cache_enabled':False,'physical_graphics_verified':False,'builder_sha256':sha(Path(__file__).read_bytes()),'archive_builder_sha256':sha((ROOT/'scripts/build_diagnostic_initramfs.py').read_bytes()),'archive_checker_sha256':sha((ROOT/'scripts/build_touch_initramfs.py').read_bytes()),'sources_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [*GRAPHICS.glob('*.c'),*DIAG.glob('*.h'),DIAG/'storage_init.c',DIAG/'memory.c',ROOT/'projects/firetabs-android/native-kexec/combined_sha256.c']}}
    (output/'report.json').write_text(json.dumps(final,indent=2)+'\n')
    for p in output.iterdir():
        if p.is_file():p.chmod(0o600)
    return final


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['policy','policy-report','runtime','runtime-report','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();build(a.policy,a.policy_report,a.runtime,a.runtime_report,a.output);print('Graphics components built; no tablet operation.')
