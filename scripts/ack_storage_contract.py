#!/usr/bin/env python3
"""Conservative internal eMMC DT contract; no SD/SDIO or disk logger opt-in."""
import struct
from prepare_native_jump_bundle import raw

KIND = 'ack-linux-storage-readonly-v6'
MMC0 = '/soc/mmc@11230000'


def cells(props, name):
    value = raw(props[name])
    if len(value) % 4:
        raise ValueError('Unaligned DT cells')
    return list(struct.unpack('>' + 'I' * (len(value) // 4), value))


def verify_tree(tree):
    node = tree[MMC0]
    expected = {
        'compatible': b'mediatek,mt8163-mmc\0mediatek,mt2701-mmc\0',
        'status': b'okay\0', 'clock-names': b'source\0hclk\0bus_clk\0',
        'pinctrl-names': b'default\0state_uhs\0',
    }
    for name, value in expected.items():
        if raw(node[name]) != value:
            raise ValueError('Wrong eMMC property: ' + name)
    for name, value in {'reg': [0, 0x11230000, 0, 0x1000], 'interrupts': [0, 79, 8],
                        'bus-width': [8], 'max-frequency': [26000000]}.items():
        if cells(node, name) != value:
            raise ValueError('Wrong eMMC cells: ' + name)
    if 'non-removable' not in node or raw(node['non-removable']):
        raise ValueError('Internal non-removable eMMC required')
    for forbidden in ['mmc-hs200-1_8v', 'mmc-hs200-1_2v', 'mmc-hs400-1_8v',
                      'mmc-hs400-1_2v', 'cap-mmc-highspeed', 'mmc-ddr-1_8v', 'mmc-ddr-1_2v']:
        if forbidden in node:
            raise ValueError('Unqualified high-speed mode: ' + forbidden)
    phandles = {}
    for path, props in tree.items():
        if 'phandle' in props:
            phandle = cells(props, 'phandle')
            if len(phandle) != 1 or phandle[0] in phandles:
                raise ValueError('Ambiguous phandle')
            phandles[phandle[0]] = path

    def references(name, paths, ids=None):
        values = cells(node, name)
        expected_count = len(paths) * (2 if ids is not None else 1)
        if len(values) != expected_count:
            raise ValueError('Wrong eMMC reference count: ' + name)
        for i, path in enumerate(paths):
            index = i * (2 if ids is not None else 1)
            if phandles.get(values[index]) != path or (ids is not None and values[index+1] != ids[i]):
                raise ValueError('Wrong eMMC reference: ' + name)
    references('clocks', ['/soc/clock-controller@10001000', '/soc/clock-controller@10000000', '/soc/clock-controller@10001000'], [31, 58, 28])
    references('assigned-clocks', ['/soc/clock-controller@10000000'], [58])
    references('assigned-clock-parents', ['/soc/clock-controller@10000000'], [21])
    references('pinctrl-0', ['/soc/pinctrl@1000b000/emmc-sdr-pins'])
    references('pinctrl-1', ['/soc/pinctrl@1000b000/emmc-uhs-pins'])
    references('vmmc-supply', ['/soc/pwrap@1000d000/pmic/regulators/ldo_vemc3v3'])
    references('vqmmc-supply', ['/soc/pwrap@1000d000/pmic/regulators/ldo_vio18'])
    # Low-level IRQ8 belongs behind the inherited MediaTek polarity controller.
    parent = node.get('interrupt-parent', tree['/soc'].get('interrupt-parent', tree['/'].get('interrupt-parent')))
    if parent is None or phandles.get(struct.unpack('>I', raw(parent))[0]) != '/soc/interrupt-controller@10200620':
        raise ValueError('Inherited MediaTek sysirq parent required')
    for address in ['11240000', '11250000']:
        if raw(tree['/soc/mmc@' + address]['status']) != b'disabled\0':
            raise ValueError('External storage controller enabled')
    if 'valethon,trial-nonce' in tree['/chosen']:
        raise ValueError('Disk logger opt-in forbidden')
    return True
