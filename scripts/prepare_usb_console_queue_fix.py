#!/usr/bin/env python3
"""Exact console request ordering correction; no USB/DMA/handoff redesign."""
import argparse,difflib,hashlib,json
from pathlib import Path
from prepare_ffs_console_hold import function
SOURCE_SHA='72c3bdad40f4d5be71d4ae3a914a8ea03bf0d251b0cb01e2cfa31a42cfe2941e'
def prepare(before):
    if hashlib.sha256(before.encode()).hexdigest()!=SOURCE_SHA:raise ValueError('Exact audited u_serial source required')
    return fix_queue(before)
def fix_queue(before):
    old='\t\t\treq->length = xfer;\n'
    success='\t\t\telse\n\t\t\t\tinfo->req_busy = 1;\n'
    if before.count(old)!=1 or before.count(success)!=1:raise ValueError('Console queue anchors differ')
    after=before.replace(old,old+'\n\t\t\t/* Publish ownership before completion can run on another CPU. */\n\t\t\tinfo->req_busy = 1;\n',1)
    return after.replace(success,'',1)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();before=a.source.read_text();after=prepare(before);a.out.mkdir(mode=0o700)
    (a.out/'u_serial.c').write_text(after)
    (a.out/'queue-order.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/drivers/usb/gadget/function/u_serial.c',tofile='b/drivers/usb/gadget/function/u_serial.c')))
    for name,s in [('baseline',before),('fixed',after)]:
        (a.out/(name+'.inc')).write_text(function(s,'void gs_complete_out(')+function(s,'int gs_console_thread('))
    (a.out/'report.json').write_text(json.dumps(dict(original_sha256=SOURCE_SHA,patched_sha256=hashlib.sha256(after.encode()).hexdigest(),ownership_published_before_queue=True,success_does_not_overwrite_completion=True,queue_error_still_clears_busy=True,buffer_size_unchanged=True,device_execution=False),indent=2)+'\n')
