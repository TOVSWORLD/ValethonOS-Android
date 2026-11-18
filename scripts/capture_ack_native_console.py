#!/usr/bin/env python3
"""One physical ACK PID1 capture using the existing nonce-bound wire receiver."""
import hashlib
import re
from pathlib import Path
from capture_lab_kernel_log import capture


def validate_profile(profile, nonce):
    if (profile.get('scope') not in ['ack-native-pid1-capture-1','ack-storage-readonly-capture-1','ack-display-functional-capture-1'] or len(nonce) != 32 or not any(nonce) or
            hashlib.sha256(nonce).hexdigest() != profile.get('nonce_sha256') or
            profile.get('usb_id') != '1209:0001' or profile.get('interface') != '00' or
            profile.get('wait_seconds') != 90 or
            profile.get('allow_privileged_open') is not True or
            not re.fullmatch(r'[0-9]{1,3}-[0-9]{1,3}(?:\.[0-9]{1,3}){0,6}', profile.get('physical_usb_path', ''))):
        raise ValueError('Exact bounded maintained-kernel capture profile required')
    return profile


def run(profile, nonce, output):
    validate_profile(profile, nonce)
    from ack_capture_supervisor import supervise
    return supervise(profile, nonce, output)
