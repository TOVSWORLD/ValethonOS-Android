#!/usr/bin/env python3
"""Host metadata observation only. Never opens a TTY or calls a return helper."""
import argparse
import json
import os
from pathlib import Path
import time
from known_boot_capture_device import inputs, approval, CANDIDATE
from observe_selected_usb import observe
from restore_diagnostic_boot import update_receipt


def host_boot_id():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def private_json(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        os.fchmod(stream.fileno(), 0o600)
        json.dump(value, stream, indent=2); stream.flush(); os.fsync(stream.fileno())


def watch(case):
    private, *_ = inputs(case)
    approval(private)
    receipt = json.loads((private / 'install-receipt.json').read_text())
    if receipt.get('verified') is not True or receipt.get('rollback_sha256') != CANDIDATE:
        raise ValueError('Verified exact control installation required')
    config = json.loads((private / 'host-config-private.json').read_text())
    port = config['physical_usb_path']
    # Validate and read only the explicit selected port before creating an arm receipt.
    from observe_selected_usb import snapshot
    initial = snapshot(port)
    expected = config['initial_usb_identity']
    if (not initial.get('present') or not initial.get('vendor') or not initial.get('product')
            or (initial['vendor'], initial['product']) != (expected['vendor'], expected['product'])):
        raise ValueError('Selected recovery USB identity must match the prepared host receipt')
    initial_ids = (initial.get('vendor'), initial.get('product'))
    path = private / 'observation-receipt.json'
    result = {'armed': True, 'candidate_sha256': CANDIDATE, 'minimum_seconds': 300,
              'automatic_return': False, 'automatic_restore': False, 'helper_launches': 0,
              'host_boot_id_private': host_boot_id()}
    private_json(path, result)
    try:
        end = time.monotonic() + 600
        while time.monotonic() < end:
            current = snapshot(port)
            if not current.get('present') or (current.get('vendor'), current.get('product')) != initial_ids:
                break
            time.sleep(.1)
        else:
            raise TimeoutError('Owner travel window expired; no return action')
        started = time.monotonic()
        result.update(boot_departure_monotonic=started, minimum_observation_end_monotonic=started+300)
        update_receipt(path, result)
        result['metadata'] = observe(port, private / 'selected-usb-events-private.jsonl', 330)
        result['minimum_observation_elapsed'] = time.monotonic() >= started + 300
    except BaseException as error:
        result.update(failure_kind=type(error).__name__, armed=False)
        update_receipt(path, result)
        raise
    result.update(armed=False, complete=True)
    update_receipt(path, result)
    return {'complete': True, 'automatic_return': False, 'device_written': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', type=Path, required=True)
    print(json.dumps(watch(p.parse_args().case), indent=2))
