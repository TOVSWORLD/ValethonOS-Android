#!/usr/bin/env python3
"""Linux host controls compile the actual client with mocked OS/syscall operations."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAMES=['load_success_and_segment_abi','refuse_preexisting_image','refuse_nonroot','refuse_affinity_failure','refuse_open_failure','refuse_file_size_change','refuse_short_read','report_load_failure','refuse_missing_loaded_state','unload_success','report_unload_failure','refuse_execute_argument']
def validate(header,out,cc='cc'):
 out.mkdir(mode=0o700);shutil.copyfile(header,out/'bundle.h')
 source=ROOT/'projects/firetabs-android/native-kexec/load_client.c';harness=ROOT/'tests/native_load_client_harness.c'
 subprocess.run([cc,'-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(source.parent),'-I'+str(out),str(harness),'-o',str(out/'controls')],check=True)
 cases=[]
 for i,name in enumerate(NAMES):
  r=subprocess.run([str((out/'controls').absolute()),str(i)],capture_output=True,timeout=10)
  if r.returncode or b'control=passed' not in r.stdout:raise ValueError('Actual client control failed: '+name)
  cases.append({'case':name,'passed':True})
 report={'scope':'Actual C client with mocked Linux files/syscalls; not tablet execution','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'harness_sha256':hashlib.sha256(harness.read_bytes()).hexdigest(),'cases':cases}
 (out/'control-result.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--header',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(validate(a.header,a.out),indent=2))
