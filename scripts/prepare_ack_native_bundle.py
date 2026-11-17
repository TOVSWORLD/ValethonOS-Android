#!/usr/bin/env python3
"""Prepare a pinned full ACK Linux Image/initramfs for the native RAM path."""
import hashlib
import json
import re
import secrets
import struct
import subprocess
from pathlib import Path

from build_ack_trampoline import build as build_entry
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw, cells, ranges_ok

IMAGE, META, ENTRY, INITRD = 0x40000000, 0x42000000, 0x42018000, 0x69244000
IMAGE_SHA = '0f43c1f91d9c158659f4f4522d44390cdd934074fb57135344e9d20142235930'
CONFIG_SHA = '733284da97440ff9251b4a91b97f99475cd2c9a527d05e557237e1751bf6517e'
DRAFT_DT_SHA = '55dfd1402eae194bf3e4ffe3a4c92e3ad6d24b8c4993488525473a28de65c6cb'
RELEASE = '6.18.34-valethon-draft1+'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def reservation_map(data):
    at = struct.unpack_from('>I', data, 16)[0]
    start = at
    result = []
    while at + 16 <= len(data):
        address, size = struct.unpack_from('>QQ', data, at); at += 16
        if not address and not size:
            return start, at, result
        if not size or address + size >= 1 << 64:
            raise ValueError('Invalid FDT reservation')
        result.append((address, address + size))
    raise ValueError('Unterminated FDT reservation map')


def reserve_union(data, ranges):
    start, end, old = reservation_map(data)
    merged = []
    for low, high in sorted(set(old + list(ranges))):
        if low < 0 or high <= low or high >= 1 << 64:
            raise ValueError('Invalid firmware reservation extent')
        if merged and low <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(high, merged[-1][1]))
        else:
            merged.append((low, high))
    encoded = b''.join(struct.pack('>QQ', low, high - low) for low, high in merged) + bytes(16)
    delta = len(encoded) - (end - start)
    out = bytearray(data[:start] + encoded + data[end:])
    header = list(struct.unpack_from('>10I', out))
    for i in [2, 3]:
        if start <= header[i] < end:
            raise ValueError('Reservation map overlaps FDT data')
        if header[i] >= end:
            header[i] += delta
    header[1] += delta
    struct.pack_into('>10I', out, 0, *header)
    if header[1] != len(out):
        raise ValueError('FDT extent changed inconsistently')
    return bytes(out), merged


def reserved_nodes(tree):
    result = []
    for node, props in tree.items():
        if node.startswith('/reserved-memory/') and 'reg' in props:
            numbers = cells(props['reg'])
            if len(numbers) % 2:
                raise ValueError('Unreviewed reserved-memory cells')
            result += [(a, a + n) for a, n in zip(numbers[::2], numbers[1::2]) if n]
    return result


def bootargs(target_nonce):
    if not re.fullmatch('[0-9a-f]{64}', target_nonce):
        raise ValueError('Exact fresh PID1 nonce required')
    return ('nr_cpus=1 maxcpus=0 cpuidle.off=1 clk_ignore_unused regulator_ignore_unused '
            'rdinit=/init panic=0 loglevel=7 printk.time=1 '
            'ramoops.mem_address=0x444bf000 ramoops.mem_size=0x10000 '
            'ramoops.record_size=0 ramoops.console_size=0x10000 '
            'ramoops.ftrace_size=0 ramoops.pmsg_size=0 ramoops.ecc=0 '
            'valethon.native_trial=' + target_nonce)


def prepare(source_dtb, iomem, draft_dtb, image, config, initramfs, init_report,
            target_nonce, source_linked, out, fdtget, fdtput):
    if sha(image) != IMAGE_SHA or sha(config) != CONFIG_SHA or sha(draft_dtb) != DRAFT_DT_SHA:
        raise ValueError('Exact complete first ACK draft artifacts required')
    if (len(target_nonce) != 32 or not any(target_nonce) or sha(target_nonce) != init_report['nonce_sha256'] or
            sha(initramfs) != init_report['artifacts']['initramfs.cpio.gz']['sha256']):
        raise ValueError('Fresh enforcing PID1/initramfs/nonce binding required')
    if init_report.get('policy_sha256') != '5b4f85ffa6c0d9a812fbbd004b307a4f932e93a720cb830eab582aeae21cf1e8':
        raise ValueError('Exact previously VM-tested enforcing policy required')
    if source_linked.get('early_cpu_shutdown_before_devices') is not True:
        raise ValueError('Hardware-tested source handoff profile required')
    offset, extent, flags = struct.unpack_from('<QQQ', image, 8)
    if image[56:60] != b'ARMd' or offset != 0 or flags != 10 or not len(image) <= extent < META - IMAGE:
        raise ValueError('ACK zero-offset Image must fit at its aligned RAM base')
    if not 0 < len(initramfs) <= 1024 * 1024:
        raise ValueError('Bounded RAM-only initramfs required')
    out.mkdir(mode=0o700)
    source_file = out / 'source-private.dtb'; source_file.write_bytes(source_dtb)
    target = out / 'target-private.dtb'; target.write_bytes(draft_dtb)
    live, original = snapshot(fdtget, source_file), snapshot(fdtget, target)
    for tree in [live, original]:
        if b'mediatek,mt8163\0' not in raw(tree['/']['compatible']):
            raise ValueError('MT8163 source/target required')
        for name in ['#address-cells', '#size-cells']:
            if tree['/'].get(name) != '0 0 0 2' or tree['/reserved-memory'].get(name) != '0 0 0 2':
                raise ValueError('Exact 64-bit board DT cells required')
    memories = [p for n, p in live.items() if n.startswith('/memory') and p.get('device_type') == '6d 65 6d 6f 72 79 0']
    target_memories = [n for n, p in original.items() if n.startswith('/memory') and p.get('device_type') == '6d 65 6d 6f 72 79 0']
    if not memories or len(target_memories) != 1:
        raise ValueError('Reviewed memory-node structure required')
    memory_reg = b''.join(raw(p['reg']) for p in memories)
    changes = []

    def put(node, prop, kind, values):
        subprocess.run([str(fdtput), '-t', kind, str(target), node, prop, *values], check=True)
        changes.append((node, prop))

    def delete(node, prop):
        subprocess.run([str(fdtput), '-d', str(target), node, prop], check=True)
        changes.append((node, prop))

    put(target_memories[0], 'reg', 'x', [format(x, 'x') for x in struct.unpack('>' + 'I' * (len(memory_reg) // 4), memory_reg)])
    # The observed firmware uses the legacy explicit-ID contract, not the
    # version-discovery contract assumed by the historical draft DT.
    psci = live.get('/psci', {})
    expected_psci = {'compatible': b'arm,psci\0', 'method': b'smc\0',
                     'cpu_suspend': bytes.fromhex('84000001'), 'cpu_off': bytes.fromhex('84000002'),
                     'cpu_on': bytes.fromhex('84000003'), 'affinity_info': bytes.fromhex('84000004')}
    if set(psci) != set(expected_psci) or any(raw(psci[k]) != v for k, v in expected_psci.items()):
        raise ValueError('Exact observed legacy firmware contract required')
    for prop, value in expected_psci.items():
        if prop in ['compatible', 'method']:
            put('/psci', prop, 's', [value[:-1].decode()])
        else:
            put('/psci', prop, 'x', [format(struct.unpack('>I', value)[0], 'x')])
    if 'valethon,trial-nonce' not in original['/chosen']:
        raise ValueError('Known draft disk-log opt-in property expected for explicit removal')
    delete('/chosen', 'valethon,trial-nonce')
    disabled = []
    disabled_tokens = [b'wdt', b'mt8163-mmc', b'mt8163-mali', b'mt8163-dsi', b'mt8163-mipi-tx',
                       b'mt8163-disp-', b'mt8163-mmsys', b'mt8163-smi-', b'mt8163-afe-pcm', b'pwm-backlight']
    for node, props in original.items():
        compatible = raw(props.get('compatible', ''))
        if any(t in compatible for t in disabled_tokens):
            put(node, 'status', 's', ['disabled']); disabled.append(node)
        if node.startswith('/cpus/cpu@') and 'operating-points-v2' in props:
            delete(node, 'operating-points-v2')
    if '/soc/watchdog@10007000' not in disabled or not all('/soc/mmc@' + a in disabled for a in ['11230000', '11240000', '11250000']):
        raise ValueError('Watchdog and all board storage controllers must be disabled')
    if original['/soc/watchdog@10007000'].get('phandle'):
        raise ValueError('Watchdog reset-provider dependencies need separate review')
    args = bootargs(target_nonce.hex())
    put('/chosen', 'bootargs', 's', [args])
    put('/chosen', 'linux,initrd-start', 'x', ['0', format(INITRD, 'x')])
    put('/chosen', 'linux,initrd-end', 'x', ['0', format(INITRD + len(initramfs), 'x')])
    put('/chosen', 'valethon,native-trial', 's', [target_nonce.hex()])
    before_reservations = snapshot(fdtget, target)
    expected = {n: dict(p) for n, p in original.items()}
    for node, prop in changes:
        if prop in before_reservations[node]:
            expected[node][prop] = before_reservations[node][prop]
        else:
            expected[node].pop(prop, None)
    if before_reservations != expected:
        raise ValueError('Unexpected target DT property change')
    firmware = reservation_map(source_dtb)[2] + reserved_nodes(live)
    updated, combined = reserve_union(target.read_bytes(), firmware)
    target.write_bytes(updated)
    final = snapshot(fdtget, target)
    if final != before_reservations or 'valethon,trial-nonce' in final['/chosen']:
        raise ValueError('Disk logger must remain unarmed; reservation insertion must not change properties')
    if (raw(final['/chosen']['bootargs']) != args.encode() + b'\0' or
            cells(final['/chosen']['linux,initrd-start']) != [INITRD] or
            cells(final['/chosen']['linux,initrd-end']) != [INITRD + len(initramfs)] or
            raw(final[target_memories[0]]['reg']) != memory_reg or
            any(raw(final[n]['status']) != b'disabled\0' for n in disabled)):
        raise ValueError('Final RAM boot profile readback differs')
    if raw(final['/soc/usb@11200000']['dr_mode']) != b'peripheral\0' or raw(final['/soc/usb@11200000']['status']) == b'disabled\0':
        raise ValueError('USB0 peripheral must remain enabled')
    safety_reserved = combined + reserved_nodes(final)
    ram = [(int(a, 16), int(z, 16) + 1) for a, z in re.findall(r'^([0-9a-f]+)-([0-9a-f]+) : System RAM$', iomem, re.M)]
    token = secrets.token_hex(16)
    entry, entry_report = build_entry(out / 'entry-private', token)
    if len(updated) > ENTRY - META:
        raise ValueError('DT exceeds metadata staging space')
    metadata = updated + bytes(ENTRY - META - len(updated)) + entry
    segments = [('image.bin', image, IMAGE, (extent + 4095) & -4096),
                ('metadata.bin', metadata, META, (len(metadata) + 4095) & -4096),
                ('initrd.bin', initramfs, INITRD, (len(initramfs) + 4095) & -4096)]
    ranges_ok([(a, a + n) for _, _, a, n in segments], ram, safety_reserved)
    report = dict(scope='Full pinned ACK Linux RAM boot; unexecuted', target_kind='ack-linux-v1',
                  trial_id=token, target_nonce_sha256=sha(target_nonce), target_release=RELEASE,
                  target_image_sha256=sha(image), target_config_sha256=sha(config),
                  source_config_sha256=source_linked['artifacts']['.config']['sha256'],
                  source_kernel_image_sha256=source_linked['artifacts']['arch/arm64/boot/Image']['sha256'],
                  source_dtb_sha256=sha(source_dtb), target_dtb_sha256=sha(updated),
                  target_initramfs_sha256=sha(initramfs), entry=ENTRY, image_entry=IMAGE,
                  image_memory_bytes=extent, original_boot_sha256='08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e',
                  disk_logger_dt_opt_in_removed=True, all_storage_controllers_disabled=True,
                  target_watchdog_driver_disabled=True, bootstrap_disabled_nodes=disabled,
                  live_firmware_reservations_preserved=True, source_cpu_shutdown_before_devices=True,
                  legacy_psci_contract_copied_from_live=True,
                  target_cpu_limit=1, deadline=entry_report, segments=[],
                  target_kernel_boot_proven=False, target_pid1_proven=False)
    for name, data, address, memory in segments:
        p = out / name; p.write_bytes(data); p.chmod(0o600)
        report['segments'].append(dict(file=name, sha256=sha(data), bytes=len(data), address=address, memory_bytes=memory))
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    for p in [source_file, target, out / 'report.json']:
        p.chmod(0o600)
    return report
