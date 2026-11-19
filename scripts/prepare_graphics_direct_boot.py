#!/usr/bin/env python3
"""Prepare one qualified GPU rendering package offline; no tablet interface."""
import argparse, hashlib, json, lzma, struct, subprocess
from pathlib import Path
from audit_trial_loader_contract import audit
from compare_pmic_dtb import snapshot
from graphics_dtb_profile import preview
from graphics_kernel_contract import verify, sha, ROOT
from pack_graphics_boot import assemble, INITRD_ADDRESS
from pack_lab_log_boot import METADATA
from prepare_native_jump_bundle import raw


def prepare(kernel,touch,display,template,component,policy,vm_off,vm_on,installed_lk,package_lk,output,fdtget,fdtput):
    checked=verify(kernel,touch,display);receipt=json.loads((ROOT/'evidence/touch-input-source/touch-runtime-result.json').read_text())
    if sha((template/'boot-full.img').read_bytes())!=receipt['candidate_sha256']: raise ValueError('Exact physically observed touch package required')
    previous=json.loads((template/'report.json').read_text());source=template/'dt/touch-preview-private.dtb'
    if sha(source.read_bytes())!=previous['dt_sha256']: raise ValueError('Observed touch DT differs')
    report=json.loads((component/'report.json').read_text());policy_report=json.loads((policy/'report.json').read_text())
    nonce=(component/'trial-nonce-private.bin').read_bytes();rd=(component/'initramfs.cpio.xz').read_bytes();policy_bytes=(policy/'policy.33').read_bytes()
    if (report.get('graphics_render_profile') is not True or len(nonce)!=32 or sha(nonce)!=report['nonce_sha256']
            or report['builder_sha256']!=sha((ROOT/'scripts/build_graphics_initramfs.py').read_bytes())
            or report['policy_sha256']!=sha(policy_bytes) or report['policy_report_sha256']!=sha((policy/'report.json').read_bytes())
            or policy_report.get('graphics_render_profile') is not True
            or len(policy_report['forbidden_privilege_mutations_rejected'])!=20 or not all(policy_report['forbidden_privilege_mutations_rejected'].values())
            or report['pid1_fork_allowed'] is not False or report['gallium_threading_enabled'] is not False or report['disk_shader_cache_enabled'] is not False):
        raise ValueError('Exact enforcing graphics component and controls required')
    for name,want in report['sources_sha256'].items():
        if '..' in Path(name).parts or Path(name).is_absolute() or sha((ROOT/name).read_bytes())!=want: raise ValueError('Graphics runtime source drift')
    for name,want in policy_report['source_sha256'].items():
        if Path(name).name!=name or sha((ROOT/'projects/firetabs-android/diagnostic-usb/policy'/name).read_bytes())!=want: raise ValueError('Graphics policy drift')
    facts=report['artifacts']['initramfs.cpio.xz'];unpacked=lzma.decompress(rd)
    if len(rd)!=facts['bytes'] or sha(rd)!=facts['sha256'] or len(unpacked)!=facts['unpacked_bytes'] or sha(unpacked)!=facts['unpacked_sha256']:
        raise ValueError('Graphics archive differs')
    for path,mode in [(vm_off,'off'),(vm_on,'on')]:
        vm=json.loads(path.read_text())
        if (vm.get('passed') is not True or vm.get('vm_only') is not True or vm.get('virtualization')!=mode
                or vm.get('kernel_sha256')!=checked['image_sha256'] or vm.get('policy_sha256')!=sha(policy_bytes)
                or vm.get('component_report_sha256')!=sha((component/'report.json').read_bytes())
                or vm.get('vm_archive_sha256')!=report['artifacts']['vm-only-initramfs.cpio.xz']['sha256']):
            raise ValueError('Both exact-kernel/component VM controls required')
    output.mkdir(mode=0o700)
    dt_report=preview(source,(kernel/'resolved.config').read_text(),output/'dt',fdtget,fdtput);dt=output/'dt/graphics-preview-private.dtb'
    chosen=snapshot(fdtget,source)['/chosen'];old=raw(chosen['valethon,direct-trial']).rstrip(b'\0').decode()
    if old==nonce.hex(): raise ValueError('Fresh graphics identity required')
    args=raw(chosen['bootargs']).rstrip(b'\0').decode();token='valethon.direct_trial='+old
    if args.count(token)!=1: raise ValueError('Exact retained touch identity required')
    args=args.replace(token,'valethon.direct_trial='+nonce.hex())
    for name,value in [('linux,initrd-start',INITRD_ADDRESS),('linux,initrd-end',INITRD_ADDRESS+len(rd))]:
        subprocess.run([str(fdtput),'-t','x',str(dt),'/chosen',name,'0',hex(value)[2:]],capture_output=True,check=True)
    for name,value in [('bootargs',args),('valethon,direct-trial',nonce.hex())]:
        subprocess.run([str(fdtput),'-t','s',str(dt),'/chosen',name,value],capture_output=True,check=True)
    data=bytearray(dt.read_bytes());data.extend(bytes((-len(data))%4));struct.pack_into('>I',data,4,len(data));dt.write_bytes(data)
    image=(kernel/'Image').read_bytes();compressed=(kernel/'Image.gz').read_bytes()
    candidate,final=assemble(image,compressed,bytes(data),rd,json.loads(METADATA.read_text()))
    loader=audit(installed_lk.read_bytes(),package_lk.read_bytes(),candidate,expected_candidate_sha=sha(candidate))
    if loader['candidate']['decoded_sha256']!=checked['image_sha256'] or loader['candidate']['dt_sha256']!=sha(data): raise ValueError('Original loader roundtrip differs')
    final.update(scope='Offline direct graphics candidate only',authorization_scope='graphics-direct-1',kernel=checked,
        nonce_sha256=sha(nonce),policy_sha256=sha(policy_bytes),initramfs_sha256=sha(rd),dt_sha256=sha(data),
        dt_preview=dt_report,loader_static_audit=loader,expected_current_boot_sha256=receipt['candidate_sha256'],
        original_rollback_ready=True,recovery_written=False,automatic_trial_retry=False,
        owner_selected_stay_in_twrp=True,physical_graphics_verified=False,
        acceptance='Actual colored cube rotates with touch movement; non-T720/software renderer is rejected',
        source_sha256=sha(Path(__file__).read_bytes()),pack_source_sha256=sha((ROOT/'scripts/pack_graphics_boot.py').read_bytes()))
    for name,b in [('boot-full.img',candidate),('trial-nonce-private.bin',nonce),('report.json',(json.dumps(final,indent=2)+'\n').encode())]:
        p=output/name;p.write_bytes(b);p.chmod(0o600)
    return final


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['kernel','touch','display','template','component','policy','vm-off','vm-on','installed-lk','package-lk','output','fdtget','fdtput']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();prepare(**vars(a));print('Offline direct graphics candidate prepared; no device action.')
