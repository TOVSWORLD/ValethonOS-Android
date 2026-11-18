#!/usr/bin/env python3
"""Exact-source, default-off ADB last-close diagnostic hold; offline only."""
import argparse,difflib,hashlib,json,re
from pathlib import Path

SOURCE_SHA='d9659aaad3fd36bbde3936717b0d585fd0cdbc47a039e840a61364689a066823'
HELPER=r'''
/* Current-boot diagnostic scope only; ordinary FunctionFS behavior is default.
 * Reuse the existing no_disconnect branch for ADB's last descriptor close.
 * The runner arms a fresh nonce only after original boot is restored on flash.
 */
static bool ft_hold_adb;
static char ft_hold_trial[33];
module_param(ft_hold_adb, bool, 0600);
module_param_string(ft_hold_trial, ft_hold_trial, sizeof(ft_hold_trial), 0600);
MODULE_PARM_DESC(ft_hold_adb, "Private source-console ADB last-close hold");
MODULE_PARM_DESC(ft_hold_trial, "Exact source-console diagnostic nonce");

static bool ft_keep_adb_console(struct ffs_data *ffs)
{
 if (!READ_ONCE(ft_hold_adb) || !ffs->dev_name ||
     strcmp(ffs->dev_name, "adb") ||
     !of_machine_is_compatible("mediatek,mt8163") ||
     strlen(ft_hold_trial) != 32 ||
     strspn(ft_hold_trial, "0123456789abcdef") != 32)
  return false;
 pr_emerg("KXUSB_FFS trial=%s adb_last_close=retained\n", ft_hold_trial);
 return true;
}

'''

def prepare(before):
    if hashlib.sha256(before.encode()).hexdigest()!=SOURCE_SHA:
        raise ValueError('Exact audited FunctionFS source required')
    anchor='static void ffs_data_closed(struct ffs_data *ffs)\n{'
    if before.count(anchor)!=1 or before.count('if (ffs->no_disconnect) {')!=1:
        raise ValueError('FunctionFS last-close anchors differ')
    after=before.replace('#include <linux/module.h>','#include <linux/module.h>\n#include <linux/of.h>',1)
    after=after.replace(anchor,HELPER+anchor,1)
    after=after.replace('if (ffs->no_disconnect) {','if (ffs->no_disconnect || ft_keep_adb_console(ffs)) {',1)
    return after

def function(source,name):
    match=re.search(r'static '+re.escape(name)+r'[^;{]*\{',source)
    if match is None:raise ValueError('Actual function definition missing: '+name)
    at=match.start();brace=match.end()-1;depth=1;end=brace+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[at:end]+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();before=a.source.read_text();after=prepare(before);a.out.mkdir(mode=0o700)
    (a.out/'f_fs.c').write_text(after)
    (a.out/'ffs-console-hold.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/drivers/usb/gadget/function/f_fs.c',tofile='b/drivers/usb/gadget/function/f_fs.c')))
    (a.out/'actual-last-close.inc').write_text(function(after,'bool ft_keep_adb_console(')+function(after,'void ffs_data_closed('))
    (a.out/'report.json').write_text(json.dumps(dict(original_sha256=SOURCE_SHA,patched_sha256=hashlib.sha256(after.encode()).hexdigest(),default_enabled=False,root_only_parameters=True,requires_exact_nonce=True,board='mediatek,mt8163',function='adb',uses_existing_no_disconnect_branch=True,normal_config_and_negative_open_count_path_unchanged=True,device_execution=False),indent=2)+'\n')
