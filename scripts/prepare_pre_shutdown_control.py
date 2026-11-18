#!/usr/bin/env python3
"""Prepare a private exact pre-shutdown control bundle locally; never deploy or arm."""
import argparse
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
SCOPE = 'known-boot-pre-shutdown-control-2'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def profile_guard(template, manifest, scope=None):
    scope = SCOPE if scope is None else scope
    if manifest.get('snapshot_stage') != 'pre_shutdown' or manifest.get('checkpoint_site') != '0x4bd3e3e8':
        raise ValueError('Exact pre-shutdown profile required')
    bindings = {'CANDIDATE': manifest['observer_sha256'], 'KERNEL_CANDIDATE': manifest['candidate_sha256'],
                'CONTROL_PREFIX': manifest['prefix_sha256'], 'CONTROL_SEED': manifest['seed_sha256']}
    lines = template.splitlines()
    found = set()
    for node in ast.parse(template).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in bindings:
                value = bindings[name]
                if len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
                    raise ValueError('Exact SHA256 bindings required')
                lines[node.lineno-1:node.end_lineno] = [name+'='+repr(value)]; found.add(name)
    if found != set(bindings) or template.count("'known-boot-capture-control-1'") != 1:
        raise ValueError('Unexpected guard template')
    result = '\n'.join(lines)+'\n'
    result = result.replace("'known-boot-capture-control-1'", repr(scope))
    checked = {n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(result).body
               if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)
               and n.targets[0].id in bindings}
    if checked != bindings:
        raise ValueError('Generated guard does not match all artifact bindings')
    return result


def prepare(folder, output, additional_files=None, scope=None):
    scope = SCOPE if scope is None else scope
    manifest = json.loads((folder/'manifest.json').read_text())
    image = (folder/'boot-full.img').read_bytes(); observer = (folder/'observer-payload-sectors-private.bin').read_bytes()
    nonce = (folder/'nonce.bin').read_bytes()
    if (len(image)!=16777216 or digest(image)!=manifest['candidate_sha256']
            or digest(observer)!=manifest['observer_sha256']
            or digest(image[:15728640])!=manifest['prefix_sha256']
            or digest(image[15728640:15732736])!=manifest['seed_sha256']
            or len(nonce)!=32 or digest(nonce)!=manifest['nonce_sha256']):
        raise ValueError('Exact immutable control package required')
    sources = ['known_boot_capture_device.py','guard_known_boot_capture.py','known_boot_control_watch.py',
               'known_boot_control_return.py','assess_known_boot_control.py','restore_diagnostic_boot.py',
               'pull_retained_mailbox.py','retained_log_mailbox.py','loader_checkpoint_record.py',
               'observe_selected_usb.py','bounded_recovery_entry.py']
    files = {'scripts/'+name:(ROOT/'scripts'/name).read_bytes() for name in sources}
    files['scripts/guard_known_boot_capture.py'] = profile_guard(files['scripts/guard_known_boot_capture.py'].decode(),manifest,scope).encode()
    assessor = files['scripts/assess_known_boot_control.py'].decode()
    if assessor.count("record['stage'] == 'pre_handoff'")!=1 or assessor.count("latest['sequence'] >= 4")!=1:
        raise ValueError('Unexpected assessor template')
    assessor = assessor.replace("record['stage'] == 'pre_handoff'", "record['stage'] == 'pre_shutdown'")
    assessor = assessor.replace("latest['sequence'] >= 4", "latest['sequence'] >= 3")
    files['scripts/assess_known_boot_control.py'] = assessor.replace('pre-handoff record retrieved','pre-shutdown record retrieved').encode()
    for name in sources:
        compile(files['scripts/'+name],name,'exec')
    for name,path in {'boot-full.img':folder/'boot-full.img','candidate-manifest.json':folder/'manifest.json',
                      'observer-sectors.bin':folder/'observer-payload-sectors-private.bin','nonce.bin':folder/'nonce.bin',
                      'original-boot.img':ROOT/'out/diagnostic-trial-rollback/boot-full.img',
                      'rollback-manifest.json':ROOT/'out/diagnostic-trial-rollback/manifest.json',
                      'original-sectors.bin':ROOT/'out/loader-observer-device-original-private/boot_amonet-payload-sectors.bin',
                      'original-ranges.json':ROOT/'out/loader-observer-device-original-private/receipt.json'}.items():
        files['private/'+name] = path.read_bytes()
    if digest(files['private/original-boot.img'])!='08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e' or image[:7796736]!=files['private/original-boot.img'][:7796736]:
        raise ValueError('Original declared boot stack must remain identical')
    if additional_files:
        files.update(additional_files)
    auth={'scope':scope,'candidate_sha256':manifest['candidate_sha256'],'observer_sha256':manifest['observer_sha256'],
          'owner_approved':False,'owner_available':False,'minimum_seconds':300,'automatic_return':False}
    files['private/owner-authorization.template.json'] = (json.dumps(auth,indent=2)+'\n').encode()
    deployed = {name:{'bytes':len(data),'sha256':digest(data)} for name,data in files.items()}
    files['private/deployment-manifest.json'] = (json.dumps(deployed,indent=2)+'\n').encode()
    output.mkdir(mode=0o700)
    for name,data in files.items():
        path=output/name;path.parent.mkdir(mode=0o700,exist_ok=True)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as stream:stream.write(data)
    archive=output/'private/deployment-private.tar.gz'
    with archive.open('xb') as stream:
        os.fchmod(stream.fileno(),0o600)
        with tarfile.open(fileobj=stream,mode='w:gz') as tar:
            for name,data in files.items():
                info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o600;info.mtime=0
                tar.addfile(info,io.BytesIO(data))
    return {'files':len(deployed),'archive_bytes':archive.stat().st_size,'archive_sha256':digest(archive.read_bytes()),
            'guard_all_four_artifact_hashes_verified':True,'owner_approved':False,'owner_available':False,
            'source_exported':False,'device_accessed':False,'armed':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(prepare(a.folder,a.out),indent=2))
