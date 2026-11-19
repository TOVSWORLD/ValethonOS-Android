#!/usr/bin/env python3
"""Offline direct-loader comparison; no flashing, reboot or recovery interface."""
import gzip
import json
import struct
import subprocess
from pathlib import Path
from audit_trial_loader_contract import audit
from compare_pmic_dtb import snapshot
from display_kernel_contract import verify as verify_kernel, sha
from pack_lab_log_boot import assemble, CONTRACT, METADATA
from prepare_native_jump_bundle import raw
from verify_display_bundle import verify as verify_ram, component
from loader_fb_reservation import preserve


def prepare(kernel, baseline, template, old_component, fresh_component, installed_lk,
            package_lk, output, fdtget, fdtput):
    old_nonce=(old_component/'trial-nonce-private.bin').read_bytes()
    nonce=(fresh_component/'trial-nonce-private.bin').read_bytes()
    if old_nonce==nonce:raise ValueError('Fresh direct-boot nonce required')
    verify_ram(template/'report.json',kernel,baseline,old_component,fdtget,nonce=old_nonce)
    component(fresh_component,nonce)
    checked=verify_kernel(kernel)
    output.mkdir(mode=0o700)
    dt=output/'target-private.dtb';dt.write_bytes((template/'target-private.dtb').read_bytes())
    before=snapshot(fdtget,dt);contract=json.loads(CONTRACT.read_text())
    rd=(fresh_component/'initramfs.cpio.gz').read_bytes()
    for key,value in [('linux,initrd-start',contract['initramfs_address']),
                      ('linux,initrd-end',contract['initramfs_address']+len(rd))]:
        subprocess.run([str(fdtput),'-t','x',str(dt),'/chosen',key,'0',hex(value)[2:]],check=True)
    subprocess.run([str(fdtput),'-d',str(dt),'/chosen','valethon,native-trial'],check=True)
    subprocess.run([str(fdtput),'-t','s',str(dt),'/chosen','valethon,direct-trial',nonce.hex()],check=True)
    args=raw(before['/chosen']['bootargs']).rstrip(b'\0').decode()
    token='valethon.native_trial='+old_nonce.hex()
    if args.count(token)!=1:raise ValueError('Exact native identity token required')
    args=args.replace(token,'valethon.direct_trial='+nonce.hex())
    subprocess.run([str(fdtput),'-t','s',str(dt),'/chosen','bootargs',args],check=True)
    data=bytearray(dt.read_bytes());data.extend(bytes((-len(data))%4));struct.pack_into('>I',data,4,len(data))
    fixed,fb_change=preserve(bytes(data));dt.write_bytes(fixed)
    after=snapshot(fdtget,dt)
    expected={k:v for k,v in before.items() if k!='/chosen'}
    expected[fb_change['new_path']]=expected.pop(fb_change['old_path'])
    if expected!={k:v for k,v in after.items() if k!='/chosen'}:
        raise ValueError('Direct package changed board resources')
    chosen=after['/chosen']
    if set(chosen)!={'bootargs','linux,initrd-start','linux,initrd-end','valethon,direct-trial'}:
        raise ValueError('Unreviewed chosen properties')
    image=(kernel/'Image').read_bytes();compressed=bytearray(gzip.compress(image,mtime=0));compressed[9]=255
    candidate,report=assemble(image,bytes(compressed),dt.read_bytes(),rd,contract,json.loads(METADATA.read_text()))
    loader=audit(installed_lk.read_bytes(),package_lk.read_bytes(),candidate,expected_candidate_sha=sha(candidate))
    if (loader['candidate']['decoded_sha256']!=checked['image_sha256'] or
            loader['candidate']['dt_sha256']!=sha(dt.read_bytes())):raise ValueError('Loader round trip differs')
    report.update(scope='Direct display boot comparison; offline preparation',
        kernel_image_sha256=checked['image_sha256'],kernel_config_sha256=checked['config_sha256'],
        nonce_sha256=sha(nonce),initramfs_sha256=sha(rd),policy_sha256='bb81388f3817c91e1f0590c67a208d83224c2d3a20f7cc00f4401553f8a0bacd',
        board_resources_unchanged=True,native_trampoline_used=False,native_31s_deadline_available=False,
        automatic_android_return_qualified=False,original_boot_restore_required=True,
        authorization_scope='display-direct-fbfix-2',loader_fb_name_adjustment=fb_change,
        physical_execution_admitted=False,recovery_written=False,loader_static_audit=loader,
        source_sha256={str(Path(__file__).relative_to(Path(__file__).resolve().parents[1])):sha(Path(__file__).read_bytes()),
                       'scripts/audit_trial_loader_contract.py':sha(Path('scripts/audit_trial_loader_contract.py').read_bytes()),
                       'scripts/loader_fb_reservation.py':sha(Path('scripts/loader_fb_reservation.py').read_bytes())})
    for name,data in [('boot-full.img',candidate),('trial-nonce-private.bin',nonce),('report.json',(json.dumps(report,indent=2)+'\n').encode())]:
        p=output/name;p.write_bytes(data);p.chmod(0o600)
    return report
