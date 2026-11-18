#!/usr/bin/env python3
"""Derive a finite ACM hold from the exercised restoration helper; offline only."""
import argparse,hashlib
from pathlib import Path

def prepare(source):
    if hashlib.sha256(source.encode()).hexdigest()!='9339075982f1cc7bb90f7cb0b0832d256aeba967cdbab301807413781d74d22d':
        raise ValueError('Exact exercised ACM restoration source required')
    # Reuse the restoration code verbatim, not an independent USB switcher.
    start=source.index('static int kernel_frame(')
    end=source.index('int main(')
    hold=r'''static void trial(const char*nonce){
 int owned=0,changed=0;char path[160],b[64];
 struct timespec settle={2,0};nanosleep(&settle,NULL);
 if(!original()){note("source_changed_refuse",0);goto done;}
 changed=1;
 if(store(G "/UDC","\n"))goto cleanup;
 if(symlink(G "/functions/acm.gs0",G "/configs/b.1/f2"))goto cleanup;
 owned=1;
 if(store(G "/UDC","musb-hdrc\n"))goto cleanup;
 note("acm_adb_bound",0);
 snprintf(path,sizeof(path),"/dev/kxusb-acm-%s/handoff-intent",nonce);
 long long end=milliseconds()+180000;
 while(milliseconds()<end){
  if(!read_text(path,b,sizeof(b))&&!strcmp(b,nonce)){
   note("handoff_intent_no_further_usb_writes",0);goto done;
  }
  struct timespec pause={0,100000000};nanosleep(&pause,NULL);
 }
 cleanup:
 if(changed){int r=restore(owned);note(r?"restore_failed":"restore_verified",r?errno:0);}
 done:note("finished",0);close(receipt);_exit(0);
}
'''
    return source[:start]+hold+source[end:]

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();s=prepare(a.source.read_text());a.out.write_text(s)
    print(hashlib.sha256(s.encode()).hexdigest())
