#!/usr/bin/env python3
"""Stage one reviewed private candidate from TWRP. Default read-only; never reboot."""
import argparse
import json
from pathlib import Path
import subprocess
from logging_test_gate import require_logging_control
from restore_diagnostic_boot import Adb, BOOT_BYTES, preflight, restore, sha, validate_backup


def candidate_manifest(candidate, report, original, rollback):
    validate_backup(original, rollback)
    if (len(candidate) != BOOT_BYTES or candidate[:8] != b'ANDROID!'
            or sha(candidate) != report.get('partition_sha256')
            or report.get('partition_bytes') != BOOT_BYTES
            or report.get('scope') != 'Offline first normal log-bringup candidate; review still required'
            or report.get('physical_execution_admitted') is not False
            or report.get('failed_load_qualified') is not False
            or report.get('recovery_partition_written') is not False):
        raise ValueError('Exact offline first-trial candidate/report required')
    if sha(candidate) == sha(original):
        raise ValueError('Candidate must differ from rollback')
    return {'boot': {'bytes': BOOT_BYTES, 'sha256': sha(candidate)}, 'recovery': rollback['recovery']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['selector-file', 'candidate', 'candidate-report', 'original-boot', 'rollback-manifest']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--write-candidate', action='store_true')
    p.add_argument('--receipt', type=Path)
    a = p.parse_args()
    try:
        if a.write_candidate:
            require_logging_control()
        # Exact full-size regular inputs; do not follow binary asset symlinks.
        for path in [a.candidate, a.original_boot]:
            if path.is_symlink() or not path.is_file() or path.stat().st_size != BOOT_BYTES:
                raise ValueError('Full-size regular boot files required')
        candidate = a.candidate.read_bytes()
        original = a.original_boot.read_bytes()
        rollback = json.loads(a.rollback_manifest.read_text())
        manifest = candidate_manifest(candidate, json.loads(a.candidate_report.read_text()), original, rollback)
        selector = json.loads(a.selector_file.read_text())['selector']
        if not isinstance(selector, str) or not selector or selector.startswith('-'):
            raise ValueError('Explicit authorized ADB selector required')
        adb = Adb('adb', selector)
        if a.write_candidate:
            if a.receipt is None:
                raise ValueError('Exclusive private operation receipt required')
            result = restore(adb, candidate, manifest, sha(original), a.receipt,
                             operation='install reviewed first normal logging candidate')
        else:
            preflight(adb, candidate, manifest, sha(original))
            result = {'preflight': 'passed', 'write_started': False, 'rebooted': False}
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, OSError, subprocess.SubprocessError):
        p.exit(2, 'Candidate staging stopped; no retry or reboot. Inspect private receipt if created.\n')


if __name__ == '__main__':
    main()
