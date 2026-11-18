import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from generate_douglas_tpv_sequence import SOURCE,OUTPUT,function,translate,render


class TPVPanel(unittest.TestCase):
    def test_generated_sequence_reproduces_source(self):
        steps=translate(function(SOURCE.read_text()))
        self.assertEqual(OUTPUT.read_text(),render(steps))
        self.assertEqual(len(steps),174)
        self.assertEqual(sum(not kind for kind,_,_ in steps),2)

    def test_unreviewed_source_and_queue_inputs_rejected(self):
        for body in ['unsigned int data_array[64]; unknown_call();',
                     'unsigned int data_array[64]; dsi_set_cmdq(data_array,1,1);',
                     'unsigned int data_array[64]; data_array[64]=0;',
                     'unsigned int data_array[64]; MDELAY(100000);',
                     'unsigned int data_array[64]; data_array[0]=0x00103902; dsi_set_cmdq(data_array,1,1);']:
            with self.assertRaises(ValueError):translate(body)

    def test_actual_legacy_c_emits_identical_packets(self):
        body=function(SOURCE.read_text())
        harness='''#include <stdio.h>
static void MDELAY(unsigned int n){printf("D %u\\n",n);}
static void dsi_set_cmdq(unsigned int *w,unsigned int n,unsigned int force){
 if(!force||!n||n>63)return;
 unsigned int type=(w[0]>>8)&255,size=type==0x39?w[0]>>16:type==0x15?2:1;
 printf("W %u",type);
 for(unsigned int i=0;i<size;i++){
  unsigned int word=type==0x39?w[1+i/4]:w[0];unsigned int shift=type==0x39?(i%4)*8:16+i*8;
  printf(" %u",(word>>shift)&255);
 }
 printf("\\n");
}
static void original(void){'''+body+'''\n}
int main(void){original();return 0;}
'''
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'trace.c';source.write_text(harness);binary=Path(directory)/'trace'
            cc=shutil.which('clang') or shutil.which('cc');self.assertIsNotNone(cc)
            subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],check=True,capture_output=True)
            actual=subprocess.check_output([str(binary)],text=True).splitlines()
        expected=['D '+str(delay) if not kind else 'W '+str(kind)+' '+ ' '.join(str(v) for v in data) for kind,delay,data in translate(body)]
        self.assertEqual(actual,expected)

    def test_actual_power_and_command_error_matrix(self):
        harness=r'''
#include <string.h>
#include "douglas_tpv_core.h"
struct fake {int failed_write,short_write,enable_error,disable_error,writes,enables,disables,reset,power,events;};
static int supply(void *opaque,int on){struct fake *f=opaque;f->events++;if(on){f->enables++;return f->enable_error;}f->disables++;return f->disable_error;}
static void power(void *opaque,int on){struct fake *f=opaque;f->events++;f->power=on;}
static void reset(void *opaque,int on){struct fake *f=opaque;f->events++;f->reset=on;}
static void delay(void *opaque,unsigned int ms){struct fake *f=opaque;f->events++;if(ms>500)__builtin_trap();}
static long write_packet(void *opaque,const unsigned char *data,unsigned int n){
 struct fake *f=opaque;int index=f->writes++;f->events++;(void)data;
 if(index==f->failed_write)return f->short_write?(long)n-1:-110;
 return (long)n;
}
int main(void){
 unsigned int total=0;
 for(unsigned int i=0;i<sizeof(douglas_tpv_sequence)/sizeof(douglas_tpv_sequence[0]);i++)if(douglas_tpv_sequence[i].type)total++;
 for(int short_write=0;short_write<2;short_write++)for(int index=-1;index<(int)total;index++){
  struct fake f={0};f.failed_write=index;f.short_write=short_write;struct douglas_tpv_state s={0};
  struct douglas_tpv_io io={supply,power,reset,delay,write_packet,&f};
  int ret=douglas_tpv_prepare(&s,&io);
  if(index>=0){
   if(ret!=(short_write?-5:-110)||s.active||s.rail_owned||f.power||!f.reset||f.disables!=1||f.writes!=index+1)return 1;
  }else{
   if(ret||!s.active||!s.rail_owned||f.writes!=(int)total)return 2;
   int before=f.events;if(douglas_tpv_prepare(&s,&io)||f.events!=before)return 3;
   douglas_tpv_disable(&s,&io);if(s.active||!f.reset)return 4;
   before=f.events;douglas_tpv_disable(&s,&io);if(f.events!=before)return 5;
   if(douglas_tpv_unprepare(&s,&io)||s.rail_owned||f.power)return 6;
   before=f.events;if(douglas_tpv_unprepare(&s,&io)||f.events!=before)return 7;
  }
 }
 {struct fake f={0};f.enable_error=-517;struct douglas_tpv_state s={0};struct douglas_tpv_io io={supply,power,reset,delay,write_packet,&f};
  if(douglas_tpv_prepare(&s,&io)!=-517||s.rail_owned||f.events!=1||f.writes)return 8;}
 {struct fake f={0};f.failed_write=0;f.disable_error=-16;struct douglas_tpv_state s={0};struct douglas_tpv_io io={supply,power,reset,delay,write_packet,&f};
  if(douglas_tpv_prepare(&s,&io)!=-110||!s.fault||!s.rail_owned)return 9;
  int before=f.events;if(douglas_tpv_prepare(&s,&io)!=-5||f.events!=before)return 10;}
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'probe.c';source.write_text(harness);binary=Path(directory)/'probe'
            cc=shutil.which('clang') or shutil.which('cc');self.assertIsNotNone(cc)
            subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                            '-I',str(OUTPUT.parent),str(source),'-o',str(binary)],check=True,capture_output=True)
            subprocess.run([str(binary)],check=True,capture_output=True)

class PanelInstallation(unittest.TestCase):
    def test_build_input_failure_does_not_install_any_panel_file(self):
        from install_douglas_tpv_panel import install,PORT
        lock=json.loads((PORT/'panel-inputs.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);parent=root/'drivers/gpu/drm/panel';parent.mkdir(parents=True)
            (parent/'Kconfig').write_bytes((ROOT/'evidence/display-pipeline-source/ack-panel-Kconfig').read_bytes())
            (parent/'Makefile').write_text('wrong final build input')
            before={p.name:p.read_bytes() for p in parent.iterdir()}
            with self.assertRaises(ValueError):install(root,lock['ack_commit'])
            self.assertEqual(before,{p.name:p.read_bytes() for p in parent.iterdir()})

    def test_install_and_explicit_build_scope(self):
        from install_douglas_tpv_panel import install,PORT
        from select_kernel_build_scope import choose
        lock=json.loads((PORT/'panel-inputs.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);parent=root/'drivers/gpu/drm/panel';parent.mkdir(parents=True)
            for name in ['Kconfig','Makefile']:(parent/name).write_bytes((ROOT/('evidence/display-pipeline-source/ack-panel-'+name)).read_bytes())
            report=install(root,lock['ack_commit']);self.assertFalse(report['hardware_execution'])
            self.assertIn('CONFIG_DRM_PANEL_AMAZON_DOUGLAS_TPV',(parent/'Makefile').read_text())
            with self.assertRaises(ValueError):install(root,lock['ack_commit'])
        self.assertEqual(choose('workflow_dispatch',mode='display-provider')['mode'],'display-provider')
        self.assertEqual(choose('pull_request',changed=['projects/firetabs-android/kernel/display-port/panel/panel-amazon-douglas-tpv.c'])['mode'],'display-provider')
        with self.assertRaises(ValueError):choose('workflow_dispatch',mode='display-provider',argument_profile='generic-force')
