import sys, unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from graphics_dtb_profile import plan


def cells(*values):
    return ' '.join(f'{b:x}' for v in values for b in v.to_bytes(4, 'big'))


def string(value):
    return ' '.join(f'{b:x}' for b in value.encode()+b'\0')


def fixture():
    tree = {
        '/gpu': {'compatible': string('arm,mali-t720'), 'reg': cells(0, 0x13040000, 0, 0x4000),
                 'interrupts': cells(0, 227, 8, 0, 226, 8, 0, 225, 8), 'interrupt-names': string('job\0mmu\0gpu'),
                 'status': string('disabled'), 'clocks': cells(1, 0), 'assigned-clocks': cells(2, 54),
                 'power-domains': cells(3, 7), 'mali-supply': cells(4), 'operating-points-v2': cells(5)},
        '/mfg': {'compatible': string('mediatek,mt8163-mfgcfg'), 'phandle': cells(1), 'reg': cells(0, 0x13000000, 0, 0x1000)},
        '/top': {'compatible': string('mediatek,mt8163-topckgen'), 'phandle': cells(2)},
        '/spm': {'phandle': cells(3), 'compatible': string('mediatek,mt8163-power-controller')},
        '/spm/power-domain@6': {'reg':cells(6),'#power-domain-cells':cells(1),'status':string('disabled')},
        '/spm/power-domain@6/power-domain@7': {'reg':cells(7),'#power-domain-cells':cells(0),'status':string('disabled')},
        '/spm/power-domain@0': {'reg':cells(0),'status':string('okay')},
        '/supply': {'compatible': string('regulator-fixed'), 'phandle': cells(4),
                    'regulator-min-microvolt': cells(1150000), 'regulator-max-microvolt': cells(1150000)},
        '/opps': {'phandle': cells(5)}, '/opps/416': {'opp-hz': cells(0, 416000000), 'opp-microvolt': cells(1150000)},
    }
    config = ''.join('CONFIG_'+s+'=y\n' for s in ['DRM_PANFROST', 'DRM_MEDIATEK', 'DRM_SCHED', 'DRM_GEM_SHMEM_HELPER', 'TOUCHSCREEN_GOODIX', 'MEDIATEK_WATCHDOG'])
    return tree, config


class GraphicsDT(unittest.TestCase):
    def test_fixed_source_point_and_no_display_pll_rate_assignment(self):
        tree, config = fixture(); original = deepcopy(tree); resources, edits = plan(tree, config)
        self.assertEqual(tree, original)
        self.assertEqual(resources['gpu'], '/gpu')
        self.assertIn(('x', '/gpu', 'assigned-clock-parents', [2, 9]), edits)
        self.assertIn(('delete', '/gpu', 'operating-points-v2', []), edits)
        self.assertFalse(any(p == 'assigned-clock-rates' for _, _, p, _ in edits))

    def test_wrong_gpu_supply_interrupt_or_source_point_fails(self):
        for node, prop, value in [('/gpu', 'interrupts', cells(0, 227, 4)),
                                   ('/supply', 'regulator-max-microvolt', cells(1200000)),
                                   ('/opps/416', 'opp-hz', cells(0, 520000000)),
                                   ('/spm', 'status', string('disabled')),
                                   ('/gpu', 'assigned-clock-rates', cells(520000000))]:
            tree, config = fixture(); tree[node][prop] = value
            with self.assertRaises(ValueError): plan(tree, config)
        tree, config = fixture()
        with self.assertRaises(ValueError): plan(tree, config.replace('CONFIG_DRM_PANFROST=y', 'CONFIG_DRM_PANFROST=m'))

    def test_both_gpu_domains_enabled_and_display_domain_preserved(self):
        tree,config=fixture();before=deepcopy(tree);resources,edits=plan(tree,config)
        for key in ['power_domain_async','power_domain_mfg']:
            self.assertIn(('s',resources[key],'status',['okay']),edits)
        self.assertEqual([v for _,node,_,v in edits if node=='/spm/power-domain@0'],[])
        self.assertEqual(tree,before)
        for missing in ['/spm/power-domain@6','/spm/power-domain@6/power-domain@7']:
            broken=deepcopy(tree);del broken[missing]
            with self.assertRaises(ValueError):plan(broken,config)
        broken=deepcopy(tree);child=broken.pop('/spm/power-domain@6/power-domain@7');broken['/spm/power-domain@7']=child
        with self.assertRaises(ValueError):plan(broken,config)
