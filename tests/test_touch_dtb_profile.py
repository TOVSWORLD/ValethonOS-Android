import json,re,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from touch_dtb_profile import plan
ROOT=Path(__file__).resolve().parents[1]
def s(v):return (v.encode()+b'\0').hex(' ')
def x(*v):return struct.pack('>'+'I'*len(v),*v).hex(' ')
CONFIG=''.join('CONFIG_'+n+'=y\n' for n in ['TOUCHSCREEN_GOODIX','INPUT_EVDEV','I2C_MT65XX','MEDIATEK_WATCHDOG','WATCHDOG_HANDLE_BOOT_ENABLED'])+'CONFIG_WATCHDOG_OPEN_TIMEOUT=0\n'
def tree():
    wdt=json.loads((ROOT/'evidence/watchdog-binding/captured-node.json').read_text())
    return {'/':{},'/soc':{},'/soc/gpio':{'compatible':s('mediatek,mt8163-pinctrl'),'#gpio-cells':x(2),'#interrupt-cells':x(2),'phandle':x(1)},'/soc/i2c':{'compatible':s('mediatek,mt8163-i2c'),'reg':x(0,0x11007000,0,0x70)},'/soc/watchdog':{'compatible':s('mediatek,mt8163-wdt'),'reg':x(*wdt['reg'][0]),'interrupts':x(*wdt['interrupts'][0])},'/soc/vgp2':{'regulator-name':s('vgp2')},'/soc/vio18':{'regulator-name':s('vio18'),'regulator-min-microvolt':x(1800000),'regulator-max-microvolt':x(1800000)},'/soc/i2c/unused@2c':{'status':s('okay')}}


class TouchDT(unittest.TestCase):
    def test_gpio35_is_source_eint46_and_other_i2c_devices_remain_off(self):
        table=(ROOT/'projects/firetabs-android/kernel/pinctrl-port/overlay/drivers/pinctrl/mediatek/pinctrl-mtk-mt8163.h').read_text()
        self.assertRegex(table,r'PINCTRL_PIN\(35, "KPROW2"\),\s*NULL, "mt8163",\s*MTK_EINT_FUNCTION\(0, 46\)')
        r,edits=plan(tree(),CONFIG)
        self.assertIn(('x',r['touch'],'interrupts',[46,2]),edits)
        self.assertIn(('s','/soc/i2c/unused@2c','status',['disabled']),edits)
        self.assertIn(('x',r['vgp2'],'regulator-min-microvolt',[3000000]),edits)
        self.assertFalse(any(e[2]=='slew-rate' for e in edits))

    def test_missing_builtin_or_wrong_provider_is_rejected(self):
        with self.assertRaises(ValueError):plan(tree(),CONFIG.replace('CONFIG_TOUCHSCREEN_GOODIX=y','CONFIG_TOUCHSCREEN_GOODIX=m'))
        for node,prop,value in [('/soc','status',s('disabled')),('/soc/watchdog','reg',x(0,0x10007004,0,0x100)),('/soc/vio18','regulator-min-microvolt',x(3300000))]:
            t=tree();t[node][prop]=value
            with self.assertRaises(ValueError):plan(t,CONFIG)
