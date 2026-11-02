#!/usr/bin/env python3
"""Pack a private conditional p5 candidate offline; never flash or reboot."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
from measure_arm64_image import measure, bounded_file, MAX_IMAGE
import lab_log_config

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'projects/firetabs-android/kernel/lab-log/package-contract.json'
METADATA = ROOT / 'evidence/independent-recovery/trial-placement-metadata.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def overlap(a, b):
    return a[0] < b[0] + b[1] and b[0] < a[0] + a[1]


def assemble(image, compressed, dtb, initramfs, contract, metadata):
    measured = measure(image, compressed)
    if not measured['decoded_file_fits_lk_capacity'] or len(image) > contract['decoded_image_limit_bytes']:
        raise ValueError('Decoded Image exceeds selected original loader capacity')
    base = contract['ram_base']
    entry = base + measured['text_offset']
    if base % 0x200000 or entry % 0x80000 or measured['flags'] & 1:
        raise ValueError('Unsupported base/entry alignment or big-endian Image')
    kernel = (entry, measured['image_size'])
    if entry + len(image) > contract['inflate_stack']:
        raise ValueError('Decoded Image overlaps selected loader inflate stack')
    if len(dtb) < 40 or len(dtb) % 4 or len(dtb) > contract['dtb_limit_bytes']:
        raise ValueError('Aligned bounded DT required')
    if struct.unpack_from('>II', dtb) != (0xd00dfeed, len(dtb)):
        raise ValueError('DT header/extent differs')
    if not initramfs or len(initramfs) > 1024 * 1024:
        raise ValueError('Bounded initramfs required')
    # Limit decompression to prevent an unreviewed archive from exhausting memory.
    import zlib
    d = zlib.decompressobj(31)
    archive = d.decompress(initramfs, 1024 * 1024 + 1)
    if len(archive) > 1024 * 1024 or not d.eof or d.unused_data or d.unconsumed_tail:
        raise ValueError('One bounded complete initramfs gzip member required')
    regions = [kernel, (contract['initramfs_address'], len(archive)),
               (contract['tags_address'], contract['dtb_limit_bytes']),
               (contract['staging_address'], len(dtb))]
    banks = [(int(row['address'], 16), row['bytes']) for node in metadata['memory'] for row in node['reg']]
    reserved = [(int(row['address'], 16), row['bytes']) for node in metadata['reserved'] for row in node['reg']]
    for index, region in enumerate(regions):
        if not any(region[0] >= start and region[0] + region[1] <= start + size for start, size in banks):
            raise ValueError('Runtime region outside observed RAM')
        if any(overlap(region, other) for other in reserved + regions[:index]):
            raise ValueError('Runtime region overlaps reservation or another component')
    # Original path rounds the DT suffix to four bytes. Align both boundaries.
    packed_kernel = compressed + bytes((-len(compressed)) % 4) + dtb
    page = contract['page_bytes']
    if page != 2048 or contract['header_version'] != 0 or contract['mtk_kernel_wrapper']:
        raise ValueError('Unreviewed image format')
    header = bytearray(page)
    header[:8] = b'ANDROID!'
    struct.pack_into('<10I', header, 8, len(packed_kernel), entry, len(initramfs),
                     contract['initramfs_address'], 0, 0, contract['tags_address'], page, 0, 0)
    header[48:48 + len(b'ValethonLab')] = b'ValethonLab'
    commandline = b'nr_cpus=1 maxcpus=0 clk_ignore_unused regulator_ignore_unused rdinit=/init'
    header[64:64 + len(commandline)] = commandline
    # v0 ID includes kernel, ramdisk and the zero-length second component.
    digest = hashlib.sha1()
    for data in [packed_kernel, initramfs, b'']:
        digest.update(data)
        digest.update(struct.pack('<I', len(data)))
    header[576:596] = digest.digest()
    payload = bytes(header)
    for data in [packed_kernel, initramfs]:
        payload += data + bytes((-len(data)) % page)
    if len(payload) > contract['partition_bytes']:
        raise ValueError('Candidate exceeds full p5 partition')
    full = payload + bytes(contract['partition_bytes'] - len(payload))
    return full, {'measurement': measured, 'entry': entry,
                  'runtime_regions': regions, 'kernel_component_bytes': len(packed_kernel),
                  'component_sha1': digest.hexdigest(), 'payload_bytes': len(payload),
                  'partition_bytes': len(full), 'partition_sha256': sha(full)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['image', 'gzip', 'config', 'dtb', 'dt-report', 'initramfs', 'initramfs-report', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    if a.output.exists() or a.output.is_symlink():
        p.error('Fresh private output directory required')
    image = bounded_file(a.image, MAX_IMAGE)
    compressed = bounded_file(a.gzip, MAX_IMAGE)
    dtb = bounded_file(a.dtb, 1024 * 1024)
    initramfs = bounded_file(a.initramfs, 1024 * 1024)
    config = bounded_file(a.config, 1024 * 1024).decode()
    lab_log_config.diagnostic_config.check(config, lab_log_config.requirements())
    lab_log_config.usb_acm_config.check(config)
    dt = json.loads(a.dt_report.read_text())
    component = json.loads(a.initramfs_report.read_text())
    if dt['artifact']['sha256'] != sha(dtb) or dt['artifact']['bytes'] != len(dtb):
        raise ValueError('Exact DT report required')
    for path, field in [('projects/firetabs-android/kernel/lab-log/append.dts', 'append_sha256'),
                        ('evidence/independent-recovery/trial-placement-metadata.json', 'metadata_sha256')]:
        if sha((ROOT / path).read_bytes()) != dt[field]:
            raise ValueError('DT inputs changed after build')
    if component['artifacts']['initramfs.cpio.gz'] != {'bytes': len(initramfs), 'sha256': sha(initramfs)}:
        raise ValueError('Exact private initramfs report required')
    for field, path in [('builder_sha256', 'scripts/build_lab_log_initramfs.py'),
                        ('archive_builder_sha256', 'scripts/build_diagnostic_initramfs.py')]:
        if sha((ROOT / path).read_bytes()) != component[field]:
            raise ValueError('Component builder changed after build')
    for name, expected in component['sources_sha256'].items():
        path = ROOT / 'projects/firetabs-android/diagnostic-usb' / name
        if path.name != name or sha(path.read_bytes()) != expected:
            raise ValueError('PID1 source drift')
    full, report = assemble(image, compressed, dtb, initramfs,
                            json.loads(CONTRACT.read_text()), json.loads(METADATA.read_text()))
    report.update(scope='Offline first normal log-bringup candidate; review still required',
                  contract_sha256=sha(CONTRACT.read_bytes()), config_sha256=sha(config.encode()),
                  nonce_sha256=component['nonce_sha256'], policy_sha256=component['policy_sha256'],
                  physical_execution_admitted=False, failed_load_qualified=False,
                  original_partition_tail_replaced=True, recovery_partition_written=False)
    a.output.mkdir(mode=0o700, parents=True)
    for name, data in [('boot-full.img', full), ('report.json', (json.dumps(report, indent=2) + '\n').encode())]:
        target = a.output / name
        with target.open('xb') as f:
            f.write(data)
        target.chmod(0o600)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
