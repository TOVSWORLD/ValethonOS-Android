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
    tree['/soc/scpsys@10006000']['status']=storage.raw(b'disabled\0')
    controller='/soc/scpsys@10006000/power-controller'
    tree[controller]={'compatible':storage.raw(b'mediatek,mt8163-power-controller\0'),'#power-domain-cells':storage.cells(1),'phandle':storage.cells(102)}
    tree['/soc/topckgen@10000000']={'compatible':storage.raw(b'mediatek,mt8163-topckgen\0'),'phandle':storage.cells(101)}
    for index in range(8):
        node=controller+('/power-domain@6/power-domain@7' if index==7 else '/power-domain@'+str(index))
        tree[node]={'reg':storage.cells(index)}
        if index==0:tree[node].update({'clocks':storage.cells(101,51),'clock-names':storage.raw(b'mm\0')})
    tree['/soc/mmsys@14000000']['power-domains']=storage.cells(102,0)
    tree['/soc/mmsys@14000000']['phandle']=storage.cells(100)
    tree['/soc/pwm@14014000'].update({'#pwm-cells':storage.cells(2),'clock-names':storage.raw(b'main\0mm\0'),'clocks':storage.cells(100,33,100,32)})
    tree['/soc/pwrap@1000d000/pmic/regulators/ldo_vgp3']={'regulator-name':storage.raw(b'vgp3\0')}
    tree['/chosen']['bootargs']=storage.raw(b'console=ttyS0 earlycon=uart8250,mmio32,0x444bf000 keep_bootcon initcall_debug valethon.native_trial=old loglevel=7\0')
    return tree


class DisplayProfile(unittest.TestCase):
    def test_source_backed_pins_regulator_and_command_queue_closure(self):
        tree=fixture();original=copy.deepcopy(tree)
        resources,changes=plan(tree,'# CONFIG_MTK_CMDQ is not set\nCONFIG_BACKLIGHT_PWM=y\n')
        self.assertEqual(tree,original)
        pins=[v for kind,node,prop,v in changes if prop=='pinmux']
        self.assertIn([43<<8,83<<8],pins)
        self.assertIn([(59<<8)|1],pins)
        self.assertTrue(any(kind=='delete' and prop=='mboxes' for kind,node,prop,v in changes))
        self.assertFalse(any(prop=='dev-ctrl' for kind,node,prop,v in changes))
        self.assertTrue(any(prop=='pwms' and v[1:]==[0,39385] for kind,node,prop,v in changes))
        self.assertTrue(any(prop=='compatible' and v=='pwm-backlight' for kind,node,prop,v in changes))
        self.assertFalse(any(prop=='enable-gpios' for kind,node,prop,v in changes))
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
        with self.assertRaises(ValueError):plan(missing,'# CONFIG_MTK_CMDQ is not set\nCONFIG_BACKLIGHT_PWM=y\n')
        duplicate=copy.deepcopy(tree);duplicate['/soc/duplicate-gamma']=copy.deepcopy(duplicate['/soc/gamma@1400f000'])
        with self.assertRaises(ValueError):plan(duplicate,'# CONFIG_MTK_CMDQ is not set\nCONFIG_BACKLIGHT_PWM=y\n')

    def test_wrong_pwm_supplier_or_module_and_unused_lp8557_are_rejected_or_disabled(self):
        config='# CONFIG_MTK_CMDQ is not set\nCONFIG_BACKLIGHT_PWM=y\n'
        tree=fixture()
        with self.assertRaises(ValueError):plan(tree,config.replace('PWM=y','PWM=m'))
        bad=copy.deepcopy(tree);bad['/soc/pwm@14014000']['clocks']=storage.cells(100,32,100,33)
        with self.assertRaises(ValueError):plan(bad,config)
        tree['/soc/i2c@11007000/legacy-backlight@2c']={'compatible':storage.raw(b'ti,lp855x-led\0')}
        resources,changes=plan(tree,config)
        self.assertIn(('s','/soc/i2c@11007000/legacy-backlight@2c','status','disabled'),changes)
        self.assertNotIn(('s',resources['i2c'],'status','okay'),changes)

    def test_disabled_power_parent_is_enabled_with_only_mm_domain(self):
        config='# CONFIG_MTK_CMDQ is not set\nCONFIG_BACKLIGHT_PWM=y\n'
        tree=fixture();resources,changes=plan(tree,config)
        self.assertIn(('s',resources['scpsys'],'status','okay'),changes)
        self.assertIn(('s',resources['power'],'status','okay'),changes)
        self.assertIn(('s',resources['mm-domain'],'status','okay'),changes)
        disabled=[node for kind,node,prop,v in changes if prop=='status' and v=='disabled' and '/power-domain@' in node]
        self.assertEqual(len(disabled),7)
        bad=copy.deepcopy(tree);bad[resources['mm-domain']]['clocks']=storage.cells(101,50)
        with self.assertRaises(ValueError):plan(bad,config)

    def test_consumed_preview_or_disk_logger_opt_in_rejected(self):
        for key in ['valethon,offline-display-preview','valethon,trial-nonce']:
            tree=fixture();tree['/chosen'][key]=''
            with self.assertRaises(ValueError):plan(tree,'# CONFIG_MTK_CMDQ is not set\nCONFIG_BACKLIGHT_PWM=y\n')
