#!/usr/bin/env python3
"""Prepare one offline direct touch candidate; no device or flashing interface."""
import argparse, gzip, json, struct, subprocess
from pathlib import Path
from audit_trial_loader_contract import audit
from build_diagnostic_initramfs import inspect_elf
from build_touch_initramfs import entries, check_archive
from compare_pmic_dtb import snapshot
from generate_goodix_config import configuration, SOURCE as BOARD
from pack_lab_log_boot import assemble, CONTRACT, METADATA
from prepare_native_jump_bundle import raw
from touch_dtb_profile import preview
from touch_kernel_contract import verify, sha, ROOT


def prepare(kernel, baseline, template, component, policy, installed_lk, package_lk, output, fdtget, fdtput):
    checked = verify(kernel, baseline)
    if sha((template/'boot-full.img').read_bytes()) != 'c0fc6394d3bae58e2d4fb3318c6fdfbca508f95887b29fedd52de061fe1c5e40':
        raise ValueError('Exact physically observed display package required')
    source_dt = template/'target-private.dtb'
    if sha(source_dt.read_bytes()) != 'a94338de1003c96e9fce04b8969aac08aab1de5eaf0e496564285042cc6d800a':
        raise ValueError('Exact observed display DT required')
    report = json.loads((component/'report.json').read_text())
    policy_report = json.loads((policy/'report.json').read_text())
    nonce = (component/'trial-nonce-private.bin').read_bytes()
    elf = (component/'init').read_bytes(); inspect_elf(elf)
    rd = (component/'initramfs.cpio.gz').read_bytes(); blob = (policy/'policy.33').read_bytes()
    if (report.get('touch_input_profile') is not True or len(nonce) != 32 or sha(nonce) != report['nonce_sha256']
            or nonce not in elf or elf.count(blob) != 1 or sha(blob) != report['policy_sha256']
            or sha((policy/'report.json').read_bytes()) != report['policy_report_sha256']
            or policy_report.get('touch_input_profile') is not True
            or len(policy_report['forbidden_privilege_mutations_rejected']) != 16
            or not all(policy_report['forbidden_privilege_mutations_rejected'].values())
            or report['builder_sha256'] != sha((ROOT/'scripts/build_touch_initramfs.py').read_bytes())):
        raise ValueError('Exact enforcing touch component required')
    for name, want in report['sources_sha256'].items():
        if Path(name).name != name or sha((ROOT/'projects/firetabs-android/diagnostic-usb'/name).read_bytes()) != want:
            raise ValueError('Touch runtime source drift')
    for name, want in policy_report['source_sha256'].items():
        if Path(name).name != name or sha((ROOT/'projects/firetabs-android/diagnostic-usb/policy'/name).read_bytes()) != want:
            raise ValueError('Touch policy source drift')
    for name, data in [('init', elf), ('initramfs.cpio.gz', rd)]:
        if report['artifacts'][name] != {'bytes': len(data), 'sha256': sha(data)}: raise ValueError('Component artifact differs')
    check_archive(gzip.decompress(rd), entries(elf, configuration(BOARD.read_text())))
    old = snapshot(fdtget, source_dt)['/chosen']
    old_nonce = raw(old['valethon,direct-trial']).rstrip(b'\0').decode()
    if nonce.hex() == old_nonce: raise ValueError('Fresh touch identity required')
    output.mkdir(mode=0o700)
    dt_report = preview(source_dt, (kernel/'resolved.config').read_text(), output/'dt', fdtget, fdtput)
    dt = output/'dt/touch-preview-private.dtb'; contract = json.loads(CONTRACT.read_text())
    args = raw(old['bootargs']).rstrip(b'\0').decode(); token = 'valethon.direct_trial='+old_nonce
    if args.count(token) != 1: raise ValueError('Exact previous direct identity required')
    args = args.replace(token, 'valethon.direct_trial='+nonce.hex())
    for name, value in [('linux,initrd-start', contract['initramfs_address']), ('linux,initrd-end', contract['initramfs_address']+len(rd))]:
        subprocess.run([str(fdtput), '-t', 'x', str(dt), '/chosen', name, '0', hex(value)[2:]], check=True, capture_output=True)
    for name, value in [('bootargs', args), ('valethon,direct-trial', nonce.hex())]:
        subprocess.run([str(fdtput), '-t', 's', str(dt), '/chosen', name, value], check=True, capture_output=True)
    data = bytearray(dt.read_bytes()); data.extend(bytes((-len(data)) % 4)); struct.pack_into('>I', data, 4, len(data)); dt.write_bytes(data)
    image = (kernel/'Image').read_bytes(); compressed = bytearray(gzip.compress(image, mtime=0)); compressed[9] = 255
    candidate, final = assemble(image, bytes(compressed), bytes(data), rd, contract, json.loads(METADATA.read_text()))
    loader = audit(installed_lk.read_bytes(), package_lk.read_bytes(), candidate, expected_candidate_sha=sha(candidate))
    if loader['candidate']['decoded_sha256'] != checked['image_sha256'] or loader['candidate']['dt_sha256'] != sha(data):
        raise ValueError('Loader component round trip differs')
    final.update(scope='Offline direct touch candidate only', authorization_scope='touch-direct-1',
                 kernel=checked, nonce_sha256=sha(nonce), policy_sha256=sha(blob), initramfs_sha256=sha(rd),
                 dt_sha256=sha(data), dt_preview=dt_report, loader_static_audit=loader,
                 physical_execution_admitted=False, physical_touch_verified=False,
                 original_boot_restore_required=True, automatic_android_return_qualified=False,
                 recovery_written=False, native_trampoline_used=False,
                 touch_acceptance='Owner sees all nine targets turn green while touching them',
                 usb_status_is_touch_proof=False, source_sha256=sha(Path(__file__).read_bytes()))
    for name, content in [('boot-full.img', candidate), ('trial-nonce-private.bin', nonce), ('report.json', (json.dumps(final, indent=2)+'\n').encode())]:
        p = output/name; p.write_bytes(content); p.chmod(0o600)
    return final


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['kernel', 'baseline', 'template', 'component', 'policy', 'installed-lk', 'package-lk', 'output', 'fdtget', 'fdtput']:
        p.add_argument('--'+n, type=Path, required=True)
    a = p.parse_args(); prepare(**vars(a)); print('Offline direct touch candidate prepared; no device admission.')
