import copy
from pathlib import Path
import struct
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from ack_storage_contract import MMC0, verify_tree


def raw(value):
    return ' '.join(format(x, 'x') for x in value)


def cells(*values):
    return raw(struct.pack('>'+'I'*len(values), *values))


def fixture():
    nodes = ['/soc/clock-controller@10001000', '/soc/clock-controller@10000000',
             '/soc/pinctrl@1000b000/emmc-sdr-pins', '/soc/pinctrl@1000b000/emmc-uhs-pins',
             '/soc/pwrap@1000d000/pmic/regulators/ldo_vemc3v3',
             '/soc/pwrap@1000d000/pmic/regulators/ldo_vio18', '/soc/interrupt-controller@10200620']
    tree = {path: {'phandle': cells(i)} for i, path in enumerate(nodes, 1)}
    tree.update({'/': {'interrupt-parent': cells(7)}, '/soc': {}, '/chosen': {},
                 '/soc/mmc@11240000': {'status': raw(b'disabled\0')},
                 '/soc/mmc@11250000': {'status': raw(b'disabled\0')}})
    tree[MMC0] = {'compatible': raw(b'mediatek,mt8163-mmc\0mediatek,mt2701-mmc\0'),
                  'status': raw(b'okay\0'), 'clock-names': raw(b'source\0hclk\0bus_clk\0'),
                  'pinctrl-names': raw(b'default\0state_uhs\0'),
                  'reg': cells(0,0x11230000,0,0x1000), 'interrupts': cells(0,79,8),
                  'bus-width': cells(8), 'max-frequency': cells(26000000), 'non-removable': '',
                  'clocks': cells(1,31,2,58,1,28), 'assigned-clocks': cells(2,58),
                  'assigned-clock-parents': cells(2,21), 'pinctrl-0': cells(3), 'pinctrl-1': cells(4),
                  'vmmc-supply': cells(5), 'vqmmc-supply': cells(6)}
    return tree


class StorageDT(unittest.TestCase):
    def test_exact_contract(self):
        self.assertTrue(verify_tree(fixture()))

    def test_wrong_clock_supply_pins_irq_and_highspeed_rejected(self):
        for key, value in [('clocks', cells(1,31,2,59,1,28)), ('vqmmc-supply', cells(5)),
                           ('pinctrl-0', cells(4)), ('interrupts', cells(0,79,4)),
                           ('max-frequency', cells(200000000)), ('cap-mmc-highspeed', '')]:
            tree=fixture();tree[MMC0][key]=value
            with self.subTest(key=key), self.assertRaises(ValueError):verify_tree(tree)

    def test_external_storage_and_logger_rejected(self):
        tree=fixture();tree['/soc/mmc@11240000']['status']=raw(b'okay\0')
        with self.assertRaises(ValueError):verify_tree(tree)
        tree=fixture();tree['/chosen']['valethon,trial-nonce']=cells(1)
        with self.assertRaises(ValueError):verify_tree(tree)
