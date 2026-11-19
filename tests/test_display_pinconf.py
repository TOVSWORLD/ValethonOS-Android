from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_disp_pwm_source import function


class DisplayPinconf(unittest.TestCase):
    def test_working_slew_one_is_redundant_gpio_output_direction(self):
        source=(ROOT/'evidence/display-pipeline-source/working-pinctrl-mtk-common.c').read_text()
        actual_direction=function(source,'mtk_pmx_gpio_set_direction')
        self.assertIn('return mtk_pinctrl_set_gpio_direction(pctl, offset, !input);',actual_direction)
        generic=(ROOT/'evidence/display-pipeline-source/working-pinconf-generic.c').read_text()
        self.assertIn('{ "output-low", PIN_CONFIG_OUTPUT, 0, }',generic)
        self.assertIn('{ "slew-rate", PIN_CONFIG_SLEW_RATE, 0 }',generic)
        self.assertLess(generic.index('{ "output-low"'),generic.index('{ "slew-rate"'))
        code=r'''
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#define EINVAL 22
#define MTK_PUPD_SET_R1R0_00 0
enum pin_config_param {PIN_CONFIG_BIAS_DISABLE,PIN_CONFIG_BIAS_PULL_UP,
 PIN_CONFIG_BIAS_PULL_DOWN,PIN_CONFIG_INPUT_ENABLE,PIN_CONFIG_OUTPUT,
 PIN_CONFIG_INPUT_SCHMITT_ENABLE,PIN_CONFIG_DRIVE_STRENGTH,PIN_CONFIG_SLEW_RATE};
struct pinctrl_dev {int unused;};struct data {void *pin_dir_grps;};
struct mtk_pinctrl {void *chip;struct data *devdata;};
static struct data d;static struct mtk_pinctrl p={0,&d};static int level,direction;
static struct mtk_pinctrl *pinctrl_dev_get_drvdata(struct pinctrl_dev *x){return &p;}
static int mtk_pinctrl_set_gpio_direction(struct mtk_pinctrl *x,unsigned int pin,int output){
 if(pin!=43&&pin!=83)abort();direction=output;return 0;}
static int mtk_pconf_set_pull_select(struct mtk_pinctrl *a,unsigned int b,bool c,bool d,unsigned int e){return 0;}
static int mtk_pmx_gpio_set_direction(struct pinctrl_dev *a,void *b,unsigned int pin,bool input){direction=!input;return 0;}
static int mtk_pconf_set_ies_smt(struct mtk_pinctrl *a,unsigned int b,unsigned int c,unsigned int d){return 0;}
static int mtk_pconf_set_driving(struct mtk_pinctrl *a,unsigned int b,unsigned int c){return 0;}
static void mtk_gpio_set(void *a,unsigned int pin,int value){level=value;}
'''+function(source.replace('enum pin_config_param param)\n\n{','enum pin_config_param param)\n{'),'mtk_pconf_set_direction')+'\n'+function(source,'mtk_pconf_parse_conf')+r'''
int main(void){struct pinctrl_dev dev={0};
 for(int tables=0;tables<2;tables++)for(int pin=43;pin<=83;pin+=40)for(int value=0;value<2;value++){
  d.pin_dir_grps=tables?&d:NULL;level=-1;direction=-1;
  if(mtk_pconf_parse_conf(&dev,pin,PIN_CONFIG_OUTPUT,value)||level!=value||direction!=1)abort();
  if(mtk_pconf_parse_conf(&dev,pin,PIN_CONFIG_SLEW_RATE,1)||level!=value||direction!=1)abort();
 }
 return 0;}
'''
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);(p/'probe.c').write_text(code)
            subprocess.run([shutil.which('clang') or 'cc','-std=c11','-fsanitize=address,undefined',
                            str(p/'probe.c'),'-o',str(p/'probe')],check=True,capture_output=True)
            subprocess.run([str(p/'probe')],check=True,capture_output=True)

    def test_actual_dispatcher_rejects_slew_and_accepts_generic_output_mapping(self):
        generic=(ROOT/'evidence/display-pipeline-source/ack-pinconf-generic.c').read_text()
        self.assertIn('{ "output-low", PIN_CONFIG_LEVEL, 0, }',generic)
        self.assertIn('{ "output-high", PIN_CONFIG_LEVEL, 1, }',generic)
        self.assertIn('{ "slew-rate", PIN_CONFIG_SLEW_RATE, 0 }',generic)
        source=(ROOT/'evidence/pinctrl-port/ack/drivers/pinctrl/mediatek/pinctrl-mtk-common.c').read_text()
        body=function(source,'mtk_pconf_parse_conf')
        harness=r'''
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#define EINVAL 22
enum pin_config_param {PIN_CONFIG_BIAS_DISABLE,PIN_CONFIG_BIAS_PULL_UP,
 PIN_CONFIG_BIAS_PULL_DOWN,PIN_CONFIG_INPUT_ENABLE,PIN_CONFIG_LEVEL,
 PIN_CONFIG_INPUT_SCHMITT_ENABLE,PIN_CONFIG_DRIVE_STRENGTH,PIN_CONFIG_SLEW_RATE};
struct pinctrl_dev {int unused;};struct mtk_pinctrl {void *chip;};
static struct mtk_pinctrl p;static int level=-1,direction=-1,sets;
static struct mtk_pinctrl *pinctrl_dev_get_drvdata(struct pinctrl_dev *d){(void)d;return &p;}
static int mtk_pconf_set_pull_select(struct mtk_pinctrl *a,unsigned int b,bool c,bool d,unsigned int e){return 0;}
static int mtk_pmx_gpio_set_direction(struct pinctrl_dev *a,void *b,unsigned int pin,bool input){
 if(pin!=43&&pin!=83)abort();direction=input;return 0;}
static int mtk_pconf_set_ies_smt(struct mtk_pinctrl *a,unsigned int b,unsigned int c,unsigned int d){return 0;}
static int mtk_pconf_set_driving(struct mtk_pinctrl *a,unsigned int b,unsigned int c){return 0;}
static void mtk_gpio_set(void *a,unsigned int pin,int value){if(pin!=43&&pin!=83)abort();level=value;sets++;}
'''+body+r'''
int main(void){
 struct pinctrl_dev d={0};
 if(mtk_pconf_parse_conf(&d,43,PIN_CONFIG_SLEW_RATE,1)!=-EINVAL||sets)abort();
 if(mtk_pconf_parse_conf(&d,43,PIN_CONFIG_LEVEL,0)||level||direction||sets!=1)abort();
 if(mtk_pconf_parse_conf(&d,83,PIN_CONFIG_LEVEL,1)||level!=1||direction||sets!=2)abort();
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);(p/'probe.c').write_text(harness)
            subprocess.run([shutil.which('clang') or 'cc','-std=c11','-fsanitize=address,undefined',
                            str(p/'probe.c'),'-o',str(p/'probe')],check=True,capture_output=True)
            subprocess.run([str(p/'probe')],check=True,capture_output=True)
