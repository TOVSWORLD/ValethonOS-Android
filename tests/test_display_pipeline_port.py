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
            self.assertEqual(before,after)

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
