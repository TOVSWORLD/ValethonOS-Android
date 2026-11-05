#!/usr/bin/env python3
"""Capture only: travel window, then full300-second endpoint wait after departure.

No recovery helper, ADB command, reset or restore interface exists here.
"""
import argparse
import json
import os
from pathlib import Path
import time
import threading
from observe_selected_usb import observe
from capture_lab_kernel_log import capture,private_bytes,validate


def wait_departure(present,clock=time.monotonic,sleep=time.sleep):
    if not present():raise ValueError('Exact initial recovery USB identity required')
    end=clock()+600
    while present():
        if clock()>=end:raise TimeoutError('Owner travel window expired; no device action')
        sleep(.1)
    return clock()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=Path,required=True);a=p.parse_args();base=a.case/'private'
    plan=json.loads(private_bytes(base/'capture-plan-private.json',4096));report=json.loads(private_bytes(base/'candidate-report.json',65536));nonce=private_bytes(base/'nonce-private.bin',32)
    validate(plan,report,nonce)
    if (plan['wait_seconds']!=300 or plan.get('minimum_no_intervention_seconds')!=300
            or any(plan.get(k) is not False for k in ['automatic_return_helper','automatic_restore','automatic_reboot'])):
        raise ValueError('Exact five-minute capture-only plan required')
    installed=json.loads(private_bytes(base/'install-receipt.json',65536))
    if installed.get('verified') is not True or installed.get('rollback_sha256')!=report['partition_sha256']:raise ValueError('Verified exact installation required')
    initial=json.loads(private_bytes(base/'initial-usb-identity.json',4096));device=Path('/sys/bus/usb/devices')/plan['physical_usb_path']
    def present():
        try:return (device/'idVendor').read_text().strip()==initial['vendor'] and (device/'idProduct').read_text().strip()==initial['product']
        except FileNotFoundError:return False
    receipt={'armed':True,'automatic_return':False,'automatic_restore':False,'minimum_seconds':300,'candidate_sha256':report['partition_sha256'],'waiting_for_owner_boot':True}
    fd=os.open(base/'capture-arm-receipt.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream:json.dump(receipt,stream);stream.flush();os.fsync(stream.fileno())
    from restore_diagnostic_boot import update_receipt
    try:
        started=wait_departure(present)
        receipt.update(waiting_for_owner_boot=False,boot_departure_monotonic=started,minimum_observation_end_monotonic=started+300)
        update_receipt(base/'capture-arm-receipt.json',receipt)
        metadata={}
        def watch_metadata():
            try:metadata.update(observe(plan['physical_usb_path'],base/'selected-usb-events-private.jsonl',330))
            except Exception as error:metadata.update(failure_kind=type(error).__name__)
        watcher=threading.Thread(target=watch_metadata,daemon=True)
        watcher.start()
        result=capture(plan,nonce,base/'usb-capture')
        watcher.join(timeout=335)
        if watcher.is_alive():metadata.update(failure_kind='MetadataObserverDeadlineExceeded')
        receipt['usb_metadata_observer']=metadata
    except BaseException as error:
        receipt.update(armed=False,capture_finished=True,capture_complete=False,failure_kind=type(error).__name__)
        update_receipt(base/'capture-arm-receipt.json',receipt)
        raise
    receipt.update(armed=False,capture_finished=True,capture_complete=result['complete'])
    update_receipt(base/'capture-arm-receipt.json',receipt)
    print(json.dumps({'capture_complete':result['complete'],'automatic_return':False,'automatic_restore':False}))

if __name__=='__main__':main()
