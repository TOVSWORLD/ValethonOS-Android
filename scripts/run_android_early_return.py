#!/usr/bin/env python3
"""One original FACTORYM return, armed only after the early-capture observation window."""
import argparse,json,os,re,sys,time
from pathlib import Path
from android_early_capture_device import inputs,authorization
from bounded_recovery_entry import verify_sources,choose_port,scan_ports,launch_helper
from restore_diagnostic_boot import update_receipt

def arm(case):
    m=inputs(case);authorization(case,m)
    boot=json.loads((case/'boot-request-private.json').read_text())
    if boot.get('candidate_boot_sha256')!=m['files']['boot']['sha256'] or time.time()<boot['at']+300:raise ValueError('Exact boot and completed five-minute observation required')
    cfg=json.loads((case/'return-config-private.json').read_text());modules=Path(cfg['modules']);verify_sources(modules)
    if not re.fullmatch(r'[0-9]+-[0-9]+(?:\.[0-9]+)*',cfg['physical_usb_path']):raise ValueError('Pinned physical USB path required')
    p=case/'return-helper-receipt-private.json';state={'armed':True,'helper_launches':0,'maximum_helper_launches':1,'recovery_written':False,'kernel_written':False}
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:json.dump(state,f);f.flush();os.fsync(f.fileno())
    print('RETURN_HELPER_ARMED; one call maximum; awaiting instructed manual restart',flush=True)
    end=time.monotonic()+900
    try:
        while time.monotonic()<end:
            port=choose_port(scan_ports(),cfg['physical_usb_path'])
            if port is not None:
                state.update(helper_launches=1,helper_started=True);update_receipt(p,state)
                rc=launch_helper(modules,port,90,case/'return-helper-private.log')
                state.update(helper_returncode=rc,complete=rc==0,armed=False);update_receipt(p,state)
                if rc:raise RuntimeError('Recovery helper failed; no retry')
                return state
            time.sleep(.1)
        raise TimeoutError('Return window expired; no retry')
    except BaseException as error:
        state.update(armed=False,failure_kind=type(error).__name__);update_receipt(p,state);raise
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=Path,required=True);p.add_argument('--arm-once',action='store_true');a=p.parse_args()
    if not a.arm_once:raise SystemExit('NOT_ARMED; explicit arm required after observation')
    print(json.dumps(arm(a.case)))
