import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from apply_display_port import apply,PORT


class DisplayPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.source=Path(self.tmp.name)
        self.lock=json.loads((PORT/'inputs.json').read_text())
        for part in self.lock['files']:
            dest=self.source/part['target'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/part['source'],dest)

    def test_all_outputs_and_reapplication_rejected(self):
        report=apply(self.source,self.lock['ack_commit']);self.assertTrue(report['all_outputs_preflighted'])
        for part in self.lock['files']:
            self.assertEqual(hashlib.sha256((self.source/part['target']).read_bytes()).hexdigest(),part['patched_sha256'])
        with self.assertRaises(ValueError):apply(self.source,self.lock['ack_commit'])

    def test_bad_last_input_leaves_every_file_unchanged(self):
        part=self.lock['files'][-1];(self.source/part['target']).write_text('wrong mutex source')
        before={part['target']:(self.source/part['target']).read_bytes() for part in self.lock['files']}
        with self.assertRaises(ValueError):apply(self.source,self.lock['ack_commit'])
        self.assertEqual(before,{part['target']:(self.source/part['target']).read_bytes() for part in self.lock['files']})

    def test_existing_function_bodies_unchanged(self):
        apply(self.source,self.lock['ack_commit'])
        def bodies(text):
            result={}
            for match in re.finditer(r'^[\w *]+\b(\w+)\([^;{}]*\)\s*\n\{',text,re.M):
                end=text.index('\n}',match.end())+2
                result[match[1]]=text[match.start():end]
            return result
        for part in self.lock['files']:
            before=bodies((ROOT/part['source']).read_text());after=bodies((self.source/part['target']).read_text())
            self.assertGreater(len(before),5)
            self.assertEqual(before,{name:after[name] for name in before})
            self.assertTrue(set(after)-set(before)<= {'mtk_dsi_mt8163_prepare_lanes','mtk_dsi_mt8163_unprepare_lanes'})

    def test_actual_mutex_descriptor_and_pipeline_data(self):
        apply(self.source,self.lock['ack_commit'])
        text=(self.source/'drivers/soc/mediatek/mtk-mutex.c').read_text()
        defs='\n'.join(line for line in text.splitlines() if line.startswith('#define MT8163_MUTEX_MOD_'))
        module=re.search(r'static const u8 mt8163_mutex_mod\[DDP_COMPONENT_ID_MAX\] = \{.*?\n\};',text,re.S)[0]
        names=[name for name in re.findall(r'\[(DDP_COMPONENT_\w+)\]',module) if name!='DDP_COMPONENT_ID_MAX']
        # Real added C data is compiled; only framework enum indexing is synthetic.
        prefix='#include <stdbool.h>\ntypedef unsigned char u8;\nenum {'+','.join(names)+',DDP_COMPONENT_ID_MAX};\n'
        body=prefix+defs+'\n'+module+'''\nint main(void){
 if(mt8163_mutex_mod[DDP_COMPONENT_OVL0]!=6||mt8163_mutex_mod[DDP_COMPONENT_RDMA0]!=8)return 1;
 if(mt8163_mutex_mod[DDP_COMPONENT_COLOR0]!=11||mt8163_mutex_mod[DDP_COMPONENT_CCORR]!=12)return 2;
 if(mt8163_mutex_mod[DDP_COMPONENT_AAL0]!=13||mt8163_mutex_mod[DDP_COMPONENT_GAMMA]!=14)return 3;
 if(mt8163_mutex_mod[DDP_COMPONENT_DITHER0]!=15||mt8163_mutex_mod[DDP_COMPONENT_UFOE]!=16)return 4;
 if(mt8163_mutex_mod[DDP_COMPONENT_PWM0]!=17)return 5;
 return 0;}\n'''
        c=self.source/'test.c';c.write_text(body);binary=self.source/'test'
        cc=shutil.which('clang') or shutil.which('cc');self.assertIsNotNone(cc)
        subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror',str(c),'-o',str(binary)],check=True,capture_output=True)
        subprocess.run([str(binary)],check=True,capture_output=True)
        master=(self.source/'drivers/gpu/drm/mediatek/mtk_drm_drv.c').read_text()
        path=re.search(r'static unsigned int mt8163_mtk_ddp_main\[\] = \{(.*?)\n\};',master,re.S)[1]
        self.assertEqual(re.findall(r'DDP_COMPONENT_\w+',path),['DDP_COMPONENT_OVL0','DDP_COMPONENT_COLOR0','DDP_COMPONENT_CCORR','DDP_COMPONENT_AAL0','DDP_COMPONENT_GAMMA','DDP_COMPONENT_DITHER0','DDP_COMPONENT_RDMA0','DDP_COMPONENT_UFOE','DDP_COMPONENT_DSI0','DDP_COMPONENT_PWM0'])

    def test_actual_panel_lane_bridge_guards_and_cleanup(self):
        apply(self.source,self.lock['ack_commit'])
        text=(self.source/'drivers/gpu/drm/mediatek/mtk_dsi.c').read_text()
        def function(name):
            at=text.index('int '+name+'(struct mipi_dsi_device *device)\n{')
            return text[at:text.index('\n}',at)+2]
        helpers=function('mtk_dsi_mt8163_prepare_lanes')+'\n'+function('mtk_dsi_mt8163_unprepare_lanes')
        harness=r'''
#include <stdbool.h>
#include <stddef.h>
#define EOPNOTSUPP 95
#define EPIPE 32
#define DSI_TXRX_CTRL 0
struct mipi_dsi_host_ops {int id;};
static const struct mipi_dsi_host_ops mtk_dsi_ops={1},other_ops={2};
struct mipi_dsi_host {const struct mipi_dsi_host_ops *ops;};
struct mipi_dsi_device {struct mipi_dsi_host *host;};
struct mtk_dsi {int strict_lock,refcount;bool is_mt8163,strict_fault,strict_active,strict_attached,strict_phy_owned,strict_engine_owned,strict_digital_owned,lanes_ready;unsigned char *regs;};
static struct mtk_dsi context;static int locks,operations;
static struct mtk_dsi *host_to_dsi(struct mipi_dsi_host *host){(void)host;return &context;}
static bool mtk_dsi_mt8163(struct mtk_dsi *dsi){return dsi->is_mt8163;}
static void mutex_lock(int *lock){(void)lock;if(locks++)__builtin_trap();}
static void mutex_unlock(int *lock){(void)lock;if(--locks)__builtin_trap();}
static void mtk_dsi_lane_ready(struct mtk_dsi *dsi){operations++;dsi->lanes_ready=true;}
static void mtk_dsi_stop(struct mtk_dsi *dsi){(void)dsi;operations++;}
static void mtk_dsi_set_cmd_mode(struct mtk_dsi *dsi){(void)dsi;operations++;}
static void mtk_dsi_lane0_ulp_mode_enter(struct mtk_dsi *dsi){(void)dsi;operations++;}
static void mtk_dsi_clk_ulp_mode_enter(struct mtk_dsi *dsi){(void)dsi;operations++;}
static void writel(unsigned value,unsigned char *reg){if(value||reg!=context.regs)__builtin_trap();operations++;}
'''+helpers+r'''
static void valid(void){static unsigned char reg;context=(struct mtk_dsi){0};context.is_mt8163=true;context.strict_active=true;context.strict_attached=true;context.strict_phy_owned=true;context.strict_engine_owned=true;context.strict_digital_owned=true;context.refcount=1;context.regs=&reg;operations=0;}
int main(void){
 struct mipi_dsi_host host={&mtk_dsi_ops};struct mipi_dsi_device device={&host};
 valid();if(mtk_dsi_mt8163_prepare_lanes(NULL)!=-95||mtk_dsi_mt8163_unprepare_lanes(NULL)!=-95||operations)return 1;
 host.ops=&other_ops;if(mtk_dsi_mt8163_prepare_lanes(&device)!=-95||operations)return 2;host.ops=&mtk_dsi_ops;
 for(int mode=0;mode<8;mode++){
  valid();
  switch(mode){case 0:context.is_mt8163=false;break;case 1:context.strict_fault=true;break;case 2:context.strict_active=false;break;case 3:context.refcount=0;break;case 4:context.strict_attached=false;break;case 5:context.strict_phy_owned=false;break;case 6:context.strict_engine_owned=false;break;case 7:context.strict_digital_owned=false;break;}
  if(mtk_dsi_mt8163_prepare_lanes(&device)!=(mode?-32:-95)||operations||locks)return 3;
 }
 valid();if(mtk_dsi_mt8163_prepare_lanes(&device)||!context.lanes_ready||operations!=1||context.refcount!=1||locks)return 4;
 context.strict_fault=true; /* A failed command must not prohibit safe lane cleanup. */
 if(mtk_dsi_mt8163_unprepare_lanes(&device)||context.lanes_ready||operations!=6||context.refcount!=1||locks)return 5;
 int before=operations;if(mtk_dsi_mt8163_unprepare_lanes(&device)||operations!=before)return 6;
 valid();context.lanes_ready=true;context.strict_engine_owned=false;
 if(mtk_dsi_mt8163_unprepare_lanes(&device)!=-32||operations||!context.lanes_ready||locks)return 7;
 return 0;
}
'''
        c=self.source/'lanes.c';c.write_text(harness);binary=self.source/'lanes'
        cc=shutil.which('clang') or shutil.which('cc');self.assertIsNotNone(cc)
        subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(c),'-o',str(binary)],check=True,capture_output=True)
        subprocess.run([str(binary)],check=True,capture_output=True)
