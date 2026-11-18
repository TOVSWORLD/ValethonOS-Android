#!/usr/bin/env python3
"""Offline UART0 configuration preview. Does not produce or admit a jump bundle."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw
from prepare_ack_native_bundle import IMAGE_SHA, CONFIG_SHA

NODE = '/soc/serial@11002000'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def prepare(bundle, kernel, output, fdtget, fdtput):
    manifest = json.loads((bundle / 'report.json').read_text())
    data = (bundle / 'target-private.dtb').read_bytes()
    if sha(data) != manifest['target_dtb_sha256']:
        raise ValueError('Exact consumed DT required')
    if sha((kernel / 'Image').read_bytes()) != IMAGE_SHA or sha((kernel / 'resolved.config').read_bytes()) != CONFIG_SHA:
        raise ValueError('Exact tested ACK kernel/config required')
    config = (kernel / 'resolved.config').read_text().splitlines()
    required = ['SERIAL_EARLYCON', 'SERIAL_8250_CONSOLE', 'SERIAL_8250_MT6577']
    if not all('CONFIG_' + x + '=y' in config for x in required):
        raise ValueError('Built-in UART driver and console required')
    tree = snapshot(fdtget, bundle / 'target-private.dtb')
    if raw(tree[NODE]['status']) != b'disabled\0' or raw(tree[NODE]['reg']) != bytes.fromhex('00000000110020000000000000000400'):
        raise ValueError('Expected disabled UART0 at exact register range')
    phandle = tree[NODE]['pinctrl-0']
    pins = [n for n, p in tree.items() if p.get('phandle') == phandle]
    if len(pins) != 1 or raw(tree[pins[0] + '/pins']['pinmux']) != bytes.fromhex('00004f0100005001'):
        raise ValueError('Exact GPIO79/80 function-one UART routing required')
    args = raw(tree['/chosen']['bootargs'])[:-1].decode()
    if any(x.startswith(('console=', 'earlycon', 'keep_bootcon', 'ignore_loglevel')) for x in args.split()):
        raise ValueError('UART arguments already present; reviewed delta required')
    output.mkdir(mode=0o700)
    target = output / 'uart-preview-private.dtb'
    target.write_bytes(data)
    target.chmod(0o600)
    changes = [(NODE, 'status', 'okay'),
               ('/chosen', 'stdout-path', NODE + ':921600n8'),
               ('/chosen', 'bootargs', args + ' earlycon console=ttyS0,921600n8 keep_bootcon ignore_loglevel')]
    expected = {n: dict(p) for n, p in tree.items()}
    for node, prop, value in changes:
        subprocess.run([str(fdtput), '-t', 's', str(target), node, prop, value], check=True)
        expected[node][prop] = ' '.join(format(x, 'x') for x in value.encode() + b'\0')
    if snapshot(fdtget, target) != expected:
        raise ValueError('Unexpected UART preview delta')
    result = dict(scope='Offline UART configuration preview; physical wiring and new trial package pending',
                  loadable=False, hardware_execution=False, original_dtb_sha256=sha(data),
                  preview_dtb_sha256=sha(target.read_bytes()), target_image_sha256=IMAGE_SHA,
                  target_image_rebuilt=False, uart0_enabled=True, explicit_earlycon=True,
                  explicit_uart_console=True, baud=921600, framing='8N1',
                  gpio_rx=79, gpio_tx=80, gpio_function=1,
                  pcb_tx_pad_known=False, logic_voltage_known=False,
                  earlycon_programs_baud=False, earlycon_requires_existing_uart_initialization=True,
                  inherited_baud_unqualified=True, uart_qualified=False,
                  previous_trial_authorization_reusable=False,
                  changes=[dict(node=n, property=p) for n, p, _ in changes])
    (output / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    (output / 'report.json').chmod(0o600)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['bundle', 'kernel', 'output', 'fdtget', 'fdtput']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.bundle, a.kernel, a.output, a.fdtget, a.fdtput), indent=2))
