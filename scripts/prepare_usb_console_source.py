#!/usr/bin/env python3
"""Pinned legacy USB console source: opt-in deferred bind preserves source ADB."""
import argparse,difflib,hashlib,json
from pathlib import Path
SOURCE_SHA='663f141cb6386de685d615b174a8cd6532cd27783b6d379748bc1bb960905465'
def once(s,old,new):
 if s.count(old)!=1:raise ValueError('Pinned USB serial anchor differs')
 return s.replace(old,new)
def prepare(source,out):
 before=source.read_text()
 if hashlib.sha256(before.encode()).hexdigest()!=SOURCE_SHA:raise ValueError('Exact original g_serial source required')
 after=once(before,'static int __init init(void)\n{','''/* Private diagnostic kernel leaves Android ADB ownership unchanged by default.
 * The diagnostic target explicitly enables its builtin console gadget and nonce.
 */
static bool ft_bind;
static bool ft_registered;
static char ft_trial[33];
module_param(ft_bind, bool, 0444);
module_param_string(ft_trial, ft_trial, sizeof(ft_trial), 0444);
MODULE_PARM_DESC(ft_bind, "Opt in to private diagnostic serial binding");
MODULE_PARM_DESC(ft_trial, "Exact private diagnostic target trial ID");

static int __init init(void)
{
 int status;
 if (!ft_bind) return 0;
 if (strlen(ft_trial) != 32 || strspn(ft_trial, "0123456789abcdef") != 32)
  return -EINVAL;
 pr_info("KXUSB target_trial=%s console_bind=requested\\n", ft_trial);
''')
 after=once(after,'\treturn usb_composite_probe(&gserial_driver);','\tstatus = usb_composite_probe(&gserial_driver);\n\tif (!status) ft_registered = true;\n\treturn status;')
 after=once(after,'\tusb_composite_unregister(&gserial_driver);','\tif (ft_registered) usb_composite_unregister(&gserial_driver);')
 out.mkdir(mode=0o700);(out/'serial.c').write_text(after)
 (out/'usb-console.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/drivers/usb/gadget/legacy/serial.c',tofile='b/drivers/usb/gadget/legacy/serial.c')))
 r={'scope':'USB kernel console integration; not built/boot-tested by preparation','original_sha256':SOURCE_SHA,'patched_sha256':hashlib.sha256(after.encode()).hexdigest(),'target_only_parameters':['g_serial.ft_bind=1','g_serial.ft_trial=<32hex>','console=ttyGS0'],'default_bind_behavior':'deferred; preserves Android ADB ownership','explicit_target_bind_behavior':'original descriptor setup/probe after nonce validation','required_config':{'CONFIG_USB_G_SERIAL':'y','CONFIG_U_SERIAL_CONSOLE':'y'},'other_source_gadget_functions_unchanged':True,'watchdog_changes':False,'security_changes':False,'device_execution':False}
 (out/'source-report.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.source,a.out),indent=2))
