#!/usr/bin/env python3
"""Compile an isolated own-source log-bringup DT; never use a stock DTB or device."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from build_douglas_dtb import verify_inputs, compile_tree, inspect_header
from compare_pmic_dtb import snapshot

ROOT = Path(__file__).resolve().parents[1]
APPEND = ROOT / 'projects/firetabs-android/kernel/lab-log/append.dts'
METADATA = ROOT / 'evidence/independent-recovery/trial-placement-metadata.json'
ARGS = 'nr_cpus=1 maxcpus=0 clk_ignore_unused regulator_ignore_unused rdinit=/init'
DISABLED = [
    '/psci', '/pmu', '/cpus/cpu@1', '/cpus/cpu@2', '/cpus/cpu@3',
    '/soc/t-phy@11210000/usb-phy@11210900', '/soc/usb@11270000',
    '/soc/gpu@13040000', '/soc/i2c@11008000', '/soc/mmc@11230000',
    '/soc/pwm@14014000', '/soc/serial@11002000', '/soc/pinctrl@1000b000',
    '/soc/syscon@10005000', '/soc/pwrap@1000d000', '/soc/syscon@10006000',
    '/soc/timer@10008000', '/display-backlight', '/regulator-vgpu',
    '/soc/clock-controller@11220000', '/soc/clock-controller@13000000',
    '/soc/syscon@14000000', '/soc/clock-controller@15000000',
    '/soc/clock-controller@16000000', '/soc/clock-controller@17000000',
    '/reserved-memory/audio-dma-pool', '/soc/iommu@10205000',
    '/soc/smi@14017000', '/soc/larb@14016000', '/soc/larb@16010000',
    '/soc/larb@15001000', '/soc/larb@17001000', '/soc/mailbox@10212000',
]


def encoded(raw):
    return ' '.join(format(byte, 'x') for byte in raw)


def string(value):
    return encoded(value.encode('ascii') + b'\0')


def compare(before, after, metadata):
    expected = copy.deepcopy(before)
    for path in DISABLED:
        if path not in expected:
            raise ValueError('Expected source node absent: ' + path)
        expected[path]['status'] = string('disabled')
    expected['/']['version'] = string(metadata['root_version'])
    expected['/chosen'].pop('stdout-path')
    expected['/chosen']['bootargs'] = string(ARGS)
    ranges = metadata['memory'][0]['reg']
    expected['/memory@40000000']['reg'] = encoded(b''.join(
        struct.pack('>QQ', int(item['address'], 16), item['bytes']) for item in ranges))
    expected['/soc/usb@11200000'].update(status=string('okay'), dr_mode=string('peripheral'))
    expected['/soc/t-phy@11210000']['status'] = string('okay')
    del expected['/reserved-memory/secmon@43000000']
    for item in metadata['reserved']:
        name = item['node'] + ('@98600000' if item['node'] == 'fb-reserved-memory' else '')
        expected['/reserved-memory/' + name] = {
            'reg': encoded(b''.join(struct.pack('>QQ', int(row['address'], 16), row['bytes'])
                                    for row in item['reg'])), 'no-map': ''}
    if expected != after:
        changed = sorted(path for path in expected.keys() | after.keys() if expected.get(path) != after.get(path))
        raise ValueError('Unexpected DT node/property delta: ' + ', '.join(changed))
    return {'source_nodes_compared': len(after), 'unrelated_properties_preserved': True,
            'source_of_mmio_and_clocks': 'Unchanged locked own-source base',
            'source_of_memory_and_reservations': 'Scoped recovery metadata',
            'stock_dtb_substituted': False, 'runtime_qualified': False}


def build(output):
    if output.exists() or output.is_symlink():
        raise ValueError('Fresh output directory required')
    dtc = ROOT / 'work/dtb-tool/build/dtc'
    get = ROOT / 'work/dtb-tool/build/fdtget'
    if subprocess.check_output([str(dtc), '--version'], text=True).strip() != 'Version: DTC 1.8.1':
        raise ValueError('Pinned DTC required')
    index, experiment = verify_inputs('usb-frequency-resource')
    output.mkdir(parents=True)
    base = output / 'base'
    base.mkdir()
    compile_tree(index, experiment, base, dtc, get)
    source = output / 'lab.dts'
    source.write_bytes((base / 'douglas.pp.dts').read_bytes() + b'\n' + APPEND.read_bytes())
    target = output / 'lab.dtb'
    result = subprocess.run([str(dtc), '-a', '4', '-I', 'dts', '-O', 'dtb', '-o', str(target), str(source)],
                            capture_output=True, text=True, check=True)
    if result.stderr:
        raise ValueError('DTC diagnostics require correction: ' + result.stderr)
    facts = compare(snapshot(get, base / 'douglas.dtb'), snapshot(get, target), json.loads(METADATA.read_text()))
    artifact = inspect_header(target.read_bytes())
    if artifact['bytes'] % 4:
        raise ValueError('Legacy loader suffix arithmetic requires aligned DT size')
    report = {'scope': 'Own-source lab DT compile/semantic comparison only; no boot test',
              'artifact': artifact, 'facts': facts,
              'append_sha256': hashlib.sha256(APPEND.read_bytes()).hexdigest(),
              'metadata_sha256': hashlib.sha256(METADATA.read_bytes()).hexdigest(),
              'base_dtb_sha256': experiment['expected_artifact']['sha256'],
              'kernel_commandline': ARGS, 'physical_execution_admitted': False}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))


if __name__ == '__main__':
    main()
