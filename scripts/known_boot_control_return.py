#!/usr/bin/env python3
"""Explicit owner-requested return only; no capture, kernel write or automatic timer."""
import argparse
import json
from pathlib import Path
import time
from known_boot_capture_device import inputs, CANDIDATE
from known_boot_control_watch import private_json, host_boot_id
from restore_diagnostic_boot import update_receipt
from bounded_recovery_entry import verify_sources, scan_ports, choose_port, launch_helper


def return_once(case):
    private, *_ = inputs(case)
    authorization = json.loads((private / 'return-authorization.json').read_text())
    observation = json.loads((private / 'observation-receipt.json').read_text())
    started = observation.get('boot_departure_monotonic')
    if (authorization.get('owner_reported_at_desk') is not True
            or authorization.get('manual_return_requested') is not True
            or authorization.get('candidate_sha256') != CANDIDATE
            or observation.get('host_boot_id_private') != host_boot_id()
            or not isinstance(started, (int, float)) or time.monotonic() < started+300):
        raise ValueError('Owner desk report and full observation window required')
    config = json.loads((private / 'host-config-private.json').read_text())
    modules = Path(config['modules'])
    verify_sources(modules)
    path = private / 'manual-return-receipt.json'
    result = {'armed': True, 'helper_launches': 0, 'automatic_return': False,
              'owner_reported_at_desk': True, 'kernel_written': False}
    # Exclusive receipt, explicit fchmod and fsync before any helper may be selected.
    private_json(path, result)
    try:
        end = time.monotonic()+900
        while time.monotonic() < end:
            port = choose_port(scan_ports(), config['physical_usb_path'])
            if port is not None:
                result.update(helper_launches=1, helper_started=True)
                update_receipt(path, result)
                rc = launch_helper(modules, port, 90, private / 'original-return-helper-private.log')
                result.update(helper_returncode=rc, complete=True, armed=False)
                update_receipt(path, result)
                return {'helper_launches': 1, 'helper_returncode': rc, 'kernel_written': False}
            time.sleep(.1)
        raise TimeoutError('Manual return window expired; no retry')
    except BaseException as error:
        result.update(failure_kind=type(error).__name__, armed=False)
        update_receipt(path, result)
        raise


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', type=Path, required=True)
    print(json.dumps(return_once(p.parse_args().case), indent=2))
