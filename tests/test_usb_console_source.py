import json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_usb_console_source import prepare
class Tests(unittest.TestCase):
 def test_wrong_source_refused(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'serial.c').write_text('wrong')
   with self.assertRaises(ValueError):prepare(p/'serial.c',p/'out')
 def test_actual_generated_init_and_cleanup(self):
  source=Path(__file__).resolve().parents[1]/'evidence/independent-recovery/usb-console-source/serial.c'
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);prepare(source,p/'patch');s=(p/'patch/serial.c').read_text();init=s[s.index('static int __init init(void)'):s.index('module_init(init);')];cleanup=s[s.index('static void __exit cleanup(void)'):s.index('module_exit(cleanup);')]
   header='''#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#define __init
#define __exit
#define pr_info(...) ((void)0)
#define cpu_to_le16(x) (x)
#define USB_CLASS_COMM 2
#define USB_CLASS_VENDOR_SPEC 255
#define GS_CDC_PRODUCT_ID 1
#define GS_CDC_OBEX_PRODUCT_ID 2
#define GS_PRODUCT_ID 3
#define STRING_DESCRIPTION_IDX 0
static bool ft_bind,ft_registered,use_acm=true,use_obex;
static char ft_trial[33];
static int probes,unregisters,probe_error;
static struct {const char*label;int bConfigurationValue;} serial_config_driver;
static struct {int bDeviceClass,idProduct;} device_desc;
static struct {const char*s;} strings_dev[1];
static int gserial_driver;
static int usb_composite_probe(int*p){(void)p;probes++;return probe_error;}
static void usb_composite_unregister(int*p){(void)p;unregisters++;}
'''
   main='''int main(void){
assert(init()==0 && probes==0 && !ft_registered);cleanup();assert(!unregisters);
ft_bind=true;assert(init()==-EINVAL && !probes);strcpy(ft_trial,"gggggggggggggggggggggggggggggggg");assert(init()==-EINVAL && !probes);
strcpy(ft_trial,"0123456789abcdef0123456789abcdef");probe_error=-ENODEV;assert(init()==-ENODEV && probes==1 && !ft_registered);cleanup();assert(!unregisters);
probe_error=0;assert(init()==0 && probes==2 && ft_registered && device_desc.idProduct==GS_CDC_PRODUCT_ID);cleanup();assert(unregisters==1);
ft_registered=false;use_acm=false;use_obex=true;assert(init()==0 && device_desc.idProduct==GS_CDC_OBEX_PRODUCT_ID);
ft_registered=false;use_obex=false;assert(init()==0 && device_desc.idProduct==GS_PRODUCT_ID && device_desc.bDeviceClass==USB_CLASS_VENDOR_SPEC);
return 0;}
'''
   (p/'control.c').write_text(header+init+cleanup+main)
   subprocess.run([shutil.which('cc'),'-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'control.c'),'-o',str(p/'control')],check=True)
   subprocess.run([str(p/'control')],check=True)
