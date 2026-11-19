#!/usr/bin/env python3
"""Offline GPU enablement over the observed display/touch DT; never run devices."""
import argparse, hashlib, json, subprocess
from pathlib import Path
from compare_pmic_dtb import snapshot
from display_dtb_profile import cells
from prepare_native_jump_bundle import raw
from prepare_ack_native_bundle import reservation_map


def plan(tree, config):
    for symbol in ['DRM_PANFROST', 'DRM_MEDIATEK', 'DRM_SCHED', 'DRM_GEM_SHMEM_HELPER', 'TOUCHSCREEN_GOODIX', 'MEDIATEK_WATCHDOG']:
        if 'CONFIG_'+symbol+'=y\n' not in config+'\n':
            raise ValueError('Builtin graphics/touch dependency required: '+symbol)
    def unique(compatible):
        rows = [n for n, p in tree.items() if compatible.encode() in raw(p.get('compatible', '')).split(b'\0')]
        if len(rows) != 1: raise ValueError('Unique GPU supplier required: '+compatible)
        return rows[0]
    def provider(value):
        rows = [n for n, p in tree.items() if cells(p.get('phandle', '')) == [value]]
        if len(rows) != 1: raise ValueError('Unique referenced GPU supplier required')
        return rows[0]
    gpu = unique('arm,mali-t720'); p = tree[gpu]
    if cells(p.get('reg', '')) != [0, 0x13040000, 0, 0x4000]: raise ValueError('GPU register contract differs')
    if cells(p.get('interrupts', '')) != [0, 227, 8, 0, 226, 8, 0, 225, 8]: raise ValueError('GPU interrupts differ')
    if raw(p.get('interrupt-names', '')) != b'job\0mmu\0gpu\0': raise ValueError('GPU interrupt names differ')
    if raw(p.get('status', '')) != b'disabled\0': raise ValueError('Fresh disabled GPU required')
    clocks = cells(p.get('clocks', '')); assigned = cells(p.get('assigned-clocks', ''))
    power = cells(p.get('power-domains', '')); supply = cells(p.get('mali-supply', ''))
    if len(clocks) != 2 or clocks[1] != 0 or len(assigned) != 2 or assigned[1] != 54 or len(power) != 2 or power[1] != 7 or len(supply) != 1:
        raise ValueError('Source-backed GPU supplier selectors differ')
    gate, top, spm, regulator = map(provider, [clocks[0], assigned[0], power[0], supply[0]])
    if gate != unique('mediatek,mt8163-mfgcfg') or top != unique('mediatek,mt8163-topckgen'):
        raise ValueError('GPU clock provider differs')
    if cells(tree[gate].get('reg', '')) != [0, 0x13000000, 0, 0x1000]: raise ValueError('MFG clock range differs')
    rp = tree[regulator]
    if (raw(rp.get('compatible', '')) != b'regulator-fixed\0' or
            cells(rp.get('regulator-min-microvolt', '')) != [1150000] or
            cells(rp.get('regulator-max-microvolt', '')) != [1150000]):
        raise ValueError('Source-backed fixed GPU supply required')
    for resource in [top, spm]:
        if raw(tree[resource].get('status', '')) == b'disabled\0': raise ValueError('Existing GPU core supplier is disabled')
    opp = cells(p.get('operating-points-v2', ''))
    if len(opp) != 1: raise ValueError('Original donor OPP table required')
    table = provider(opp[0]); entries = [v for n, v in tree.items() if n.startswith(table+'/')]
    if not any(cells(v.get('opp-hz', '')) == [0, 416000000] and cells(v.get('opp-microvolt', '')) == [1150000] for v in entries):
        raise ValueError('Working source416MHz/1.15V point required')
    if 'assigned-clock-rates' in p: raise ValueError('Unexpected GPU PLL rate assignment')
    edits = [('s', gpu, 'status', ['okay']), ('s', gate, 'status', ['okay']),
             ('s', regulator, 'status', ['okay']), ('x', gpu, 'assigned-clock-parents', [assigned[0], 9]),
             ('delete', gpu, 'operating-points-v2', [])]
    return {'gpu': gpu, 'clock_gate': gate, 'topckgen': top, 'power_provider': spm, 'supply': regulator}, edits


def preview(source, config, output, fdtget, fdtput):
    before = snapshot(fdtget, source); resources, edits = plan(before, config)
    output.mkdir(mode=0o700); dt = output/'graphics-preview-private.dtb'; dt.write_bytes(source.read_bytes())
    for kind, node, prop, value in edits:
        args = ['-d', str(dt), node, prop] if kind == 'delete' else ['-t', kind, str(dt), node, prop, *[hex(v)[2:] if kind == 'x' else v for v in value]]
        subprocess.run([str(fdtput), *args], capture_output=True, check=True)
    after = snapshot(fdtget, dt); allowed = {(n, p) for _, n, p, _ in edits}
    if set(after) != set(before): raise ValueError('GPU preview changed board nodes')
    for node, props in before.items():
        for prop in props.keys() | after[node].keys():
            if props.get(prop) != after[node].get(prop) and (node, prop) not in allowed:
                raise ValueError('GPU preview changed another board resource')
    if reservation_map(source.read_bytes())[2] != reservation_map(dt.read_bytes())[2]: raise ValueError('GPU preview changed reserved RAM')
    report = {'scope': 'Offline fixed-clock GPU DT preview only', 'physical_execution_admitted': False,
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'dtb_sha256': hashlib.sha256(dt.read_bytes()).hexdigest(),
              'resources': resources, 'display_touch_memory_unchanged': True, 'gpu_dvfs_enabled': False,
              'gpu_clock_parent': 'CLK_TOP_UNIV_416M', 'source_rate_hz': 416000000,
              'hardware_rate_measured': False, 'gpu_supply_microvolts': 1150000}
    (output/'report.json').write_text(json.dumps(report, indent=2)+'\n'); return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['source', 'config', 'output', 'fdtget', 'fdtput']: p.add_argument('--'+n, type=Path, required=True)
    a = p.parse_args(); print(json.dumps(preview(a.source, a.config.read_text(), a.output, a.fdtget, a.fdtput)))
