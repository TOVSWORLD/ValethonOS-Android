#!/usr/bin/env python3
"""Assess an already-collected known-stack record; no device access or admission."""
import argparse
import json
from pathlib import Path
from known_boot_capture_device import inputs, returned_hash
import retained_log_mailbox as mailbox
from loader_checkpoint_record import decode
from restore_diagnostic_boot import sha


def assess_record(image, nonce, prefix):
    state = mailbox.inspect(image, nonce, prefix)
    latest = state['latest']
    record = decode(latest['payload'], nonce, prefix) if latest else None
    passed = bool(latest and latest['sequence'] >= 4 and not state['invalid_slots'] and record
                  and record['stage'] == 'pre_handoff'
                  and record['kernel_entry'] == 0x40080000 and record['dt_address'] == 0x48000000
                  and record['record_storage_first_sector'] == 18432)
    return {'loader_capture_criteria_passed': passed,
            'sequence': latest['sequence'] if latest else None,
            'loader_stage': record['stage'] if record else None,
            'invalid_slots': state['invalid_slots'],
            'kernel_entry_proved': False, 'kernel_logging_qualified': False,
            'modern_kernel_admitted': False,
            'meaning': 'Fresh known-stack pre-handoff record retrieved' if passed else
                       'Recorder control incomplete; do not infer modern-kernel failure'}


def assess(case):
    private, candidate, _, _, _, _, _, nonce, _ = inputs(case)
    returned_hash(private, candidate, nonce)
    image = (private / 'readout/boot-after-trial-private.img').read_bytes()
    result = assess_record(image, nonce, sha(candidate[:mailbox.BASE]))
    result['current_boot_sha256'] = sha(image)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', type=Path, required=True)
    print(json.dumps(assess(p.parse_args().case), indent=2))
