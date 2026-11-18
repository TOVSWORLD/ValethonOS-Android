import copy
import sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from display_dtb_profile import COMPONENTS,plan
import test_ack_storage_contract as storage


def fixture():
    tree=storage.fixture()
    for kind,(compatible,address) in COMPONENTS.items():
        node='/soc/'+kind+'@'+format(address,'x')
        if kind=='gpio':node='/soc/pinctrl@1000b000'
        tree[node]={'compatible':storage.raw(compatible.encode()+b'\0'),'reg':storage.cells(0,address,0,0x1000)}
        if kind=='gpio':tree[node].update({'gpio-controller':'','#gpio-cells':storage.cells(2)})
        if kind=='mmsys':tree[node]['mboxes']=storage.cells(99)
    tree['/soc/pwrap@1000d000/pmic/regulators/ldo_vgp3']={'regulator-name':storage.raw(b'vgp3\0')}
    tree['/chosen']['bootargs']=storage.raw(b'console=ttyS0 earlycon=uart8250,mmio32,0x444bf000 keep_bootcon initcall_debug valethon.native_trial=old loglevel=7\0')
    return tree


class DisplayProfile(unittest.TestCase):
    def test_source_backed_pins_regulator_and_command_queue_closure(self):
        tree=fixture();original=copy.deepcopy(tree)
        resources,changes=plan(tree,'# CONFIG_MTK_CMDQ is not set\n')
        self.assertEqual(tree,original)
        pins=[v for kind,node,prop,v in changes if prop=='pinmux']
        self.assertIn([43<<8,83<<8],pins)
        self.assertIn([(75<<8)|1,(76<<8)|1],pins)
        self.assertTrue(any(kind=='delete' and prop=='mboxes' for kind,node,prop,v in changes))
        self.assertTrue(any(prop=='dev-ctrl' and v==[0x47] for kind,node,prop,v in changes))
        self.assertFalse(any(prop in ['rom-addr','rom-val','eeprom_data','epprom_data'] for kind,node,prop,v in changes))
        bootargs=next(v for kind,node,prop,v in changes if prop=='bootargs')
        self.assertIn('console=tty0',bootargs)
        self.assertNotIn('earlycon',bootargs)
        self.assertNotIn('valethon.native_trial',bootargs)
        self.assertTrue(any(prop=='valethon,offline-display-preview' for kind,node,prop,v in changes))

    def test_missing_ambiguous_resource_and_cmdq_rejected_before_edits(self):
        tree=fixture()
        with self.assertRaises(ValueError):plan(tree,'CONFIG_MTK_CMDQ=y\n')
        missing=copy.deepcopy(tree);del missing['/soc/gamma@1400f000']
        with self.assertRaises(ValueError):plan(missing,'# CONFIG_MTK_CMDQ is not set')
        duplicate=copy.deepcopy(tree);duplicate['/soc/duplicate-gamma']=copy.deepcopy(duplicate['/soc/gamma@1400f000'])
        with self.assertRaises(ValueError):plan(duplicate,'# CONFIG_MTK_CMDQ is not set')

    def test_consumed_preview_or_disk_logger_opt_in_rejected(self):
        for key in ['valethon,offline-display-preview','valethon,trial-nonce']:
            tree=fixture();tree['/chosen'][key]=''
            with self.assertRaises(ValueError):plan(tree,'# CONFIG_MTK_CMDQ is not set')
