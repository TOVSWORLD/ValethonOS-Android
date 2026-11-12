#!/usr/bin/env python3
"""Read-only by default; one approved source-console boot and captured jump."""
import argparse,hashlib,json,os,shlex,subprocess,tarfile
from pathlib import Path
from run_pstore_warm_reboot import LabADB
from run_native_source_boot import facts,BOOT_SHA
from run_usb_console_source_boot import run as source_boot
from run_usb_console_jump import run as jump
from prepare_native_jump_bundle import prepare
from build_native_load_client import build

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/'evidence/independent-recovery/ffs-console-two-stage-authorization-template.json'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def read(f):return json.loads(f.read_text())
def private(f,value):
    with os.fdopen(os.open(f,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as h:
        json.dump(value,h,indent=2)

def validate(policy,package,linked,image,capture,helper,authorization):
    if not all(sha(ROOT/f)==digest for f,digest in policy['code_sha256'].items()):
        raise ValueError('Reviewed trial code differs')
    for f,key in [(package/'report.json','source_package_report_sha256'),(package/'boot-full.img','source_boot_candidate_sha256'),(package/'original-boot.img','original_boot_sha256'),(linked,'linked_report_sha256'),(image,'target_image_sha256'),(capture,'capture_report_sha256'),(helper,'source_helper_sha256')]:
        if sha(f)!=policy[key]:raise ValueError('Reviewed trial asset differs: '+key)
    if read(capture)['helper_sha256']!=sha(helper) or read(capture)['receiver_sha256']!=sha(ROOT/'scripts/capture_source_usb_console.py'):
        raise ValueError('Capture report does not bind actual helper/receiver')
    if read(capture).get('functionfs_hold') is True:
        profile=read(linked)
        if profile.get('ffs_console_hold_linked') is not True or profile.get('console_queue_ownership_before_submit') is not True or profile.get('diagnostic_route_console_dwell_ms')!=1000 or profile.get('native_entry_checkpoint_linked') is not True:
            raise ValueError('FunctionFS hold requires its exact linked kernel profile')
    if authorization:
        expected={**policy,'owner_approved':True,'owner_available':True}
        if read(authorization)!=expected:raise ValueError('Exact two-stage approval and owner availability required')

def run(a):
    policy=read(getattr(a,'policy',None) or POLICY)
    validate(policy,a.source_package,a.linked_report,a.image,a.capture_report,a.helper,a.authorization)
    a.output.mkdir(mode=0o700)
    if a.authorization:
        fd=os.open(str(a.authorization)+'.consumed',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
    d=LabADB(read(a.ssh_args));linked=read(a.linked_report);report=read(a.source_package/'report.json')
    child=None
    if a.authorization:
        child=a.output/'source-authorization-private.json'
        private(child,dict(scope='usb-console-native-source-boot-1',runner_sha256=sha(ROOT/'scripts/run_native_source_boot.py'),profile_runner_sha256=sha(ROOT/'scripts/run_usb_console_source_boot.py'),native_config_sha256=policy['native_config_sha256'],candidate_sha256=policy['source_boot_candidate_sha256'],original_boot_sha256=BOOT_SHA,owner_approved=True,owner_available=True,maximum_candidate_writes=1,maximum_restore_writes=1,maximum_reboots=1,recovery_writes_allowed=False,experimental_jump_allowed=False))
    first=source_boot(d,a.lab_package,report,linked,a.output/'source-boot',child)
    if not a.authorization:return {'read_only_preflight':first}
    private(a.output/'source-stage-summary.json',first)
    if not all(first.get(k) is True for k in ['complete','native_kernel_running','original_boot_restored','normal_shell_restored']):
        return {'source_boot':first,'jump_executed':False}
    inputs=a.output/'source-inputs-private';inputs.mkdir(mode=0o700)
    try:
        d.adb('root');d.adb('wait-for-device');f=facts(d)
        if f['boot']!=BOOT_SHA or f['config']!=policy['native_config_sha256'] or d.shell('cat /sys/kernel/kexec_loaded').strip()!=b'0':
            raise ValueError('Fresh source/flash/load-state differs')
        for name,cmd in [('live.dtb','cat /sys/firmware/fdt'),('iomem.txt','cat /proc/iomem')]:
            q=inputs/name;q.write_bytes(d.shell(cmd));q.chmod(0o600)
    finally:
        d.adb('unroot');d.adb('wait-for-device')
        if b'uid=2000(' not in d.shell('id'):raise ValueError('Normal ADB not restored')
    bundle=a.output/'target-private';client=a.output/'client-private'
    m=prepare((a.source_package/'original-boot.img').read_bytes(),(inputs/'live.dtb').read_bytes(),(inputs/'iomem.txt').read_text(),bundle,a.fdtget,a.fdtput,target_image=a.image.read_bytes(),usb_linked=linked)
    c=build(ROOT/'projects/firetabs-android/native-kexec/load_client.c',bundle/'report.json',client)
    files={name:bundle/name for name in ['image.bin','metadata.bin','initrd.bin']}
    files.update({'native-load':client/'native-load','source-acm-hold':a.helper})
    for name in ['capture_live_acm_probe.py','capture_usb_kernel_console.py','capture_source_usb_console.py']:
        files[name]=ROOT/'scripts'/name
    archive=a.output/'target-package-private.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        for name,q in files.items():t.add(q,arcname=name,recursive=False)
    dest=a.lab_package+'/target-'+m['trial_id']
    code='import pathlib,tarfile,sys,json,hashlib\np=pathlib.Path('+repr(dest)+');p.mkdir(mode=0o700)\nwith tarfile.open(fileobj=sys.stdin.buffer,mode="r|gz") as t:t.extractall(p,filter="data")\nprint(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir()}))'
    with archive.open('rb') as h:
        r=subprocess.run(d.args+['python3 -c '+shlex.quote(code)],stdin=h,capture_output=True,timeout=120,check=True)
    if json.loads(r.stdout)!={n:sha(q) for n,q in files.items()}:raise ValueError('Fresh lab assets differ')
    capture=read(a.capture_report)
    pre=jump(d,dest,bundle/'report.json',client/'build-result.json',linked,a.output/'jump-preflight',source_report=capture)
    if pre.get('complete') is not True:raise ValueError('Jump preflight failed')
    auth=a.output/'jump-authorization-private.json'
    private(auth,dict(scope='native-usb-source-target-console-jump-1',runner_sha256=sha(ROOT/'scripts/run_usb_console_jump.py'),manifest_sha256=sha(bundle/'report.json'),client_sha256=c['client_sha256'],target_image_sha256=policy['target_image_sha256'],native_config_sha256=policy['native_config_sha256'],receiver_sha256=sha(ROOT/'scripts/capture_usb_kernel_console.py'),shared_receiver_sha256=sha(ROOT/'scripts/capture_live_acm_probe.py'),owner_approved=True,owner_available=True,maximum_loads=1,maximum_jump_requests=1,boot_writes_allowed=False,automatic_reboot_allowed=False,source_capture_report_sha256=hashlib.sha256(json.dumps(capture,sort_keys=True).encode()).hexdigest(),source_capture_manager_sha256=sha(ROOT/'scripts/source_usb_console_trial.py')))
    return {'source_boot':first,'jump':jump(d,dest,bundle/'report.json',client/'build-result.json',linked,a.output/'jump',auth,capture)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['ssh-args','source-package','linked-report','image','capture-report','helper','output','fdtget','fdtput']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--lab-package',required=True);p.add_argument('--authorization',type=Path);p.add_argument('--policy',type=Path)
    a=p.parse_args()
    try:
        result=run(a);print(json.dumps(result,indent=2))
        success=result.get('read_only_preflight',{}).get('complete') is True or result.get('jump',{}).get('complete') is True
        raise SystemExit(0 if success else 1)
    except Exception as e:print(json.dumps({'failure_kind':type(e).__name__,'automatic_retry':False}));raise SystemExit(1)
