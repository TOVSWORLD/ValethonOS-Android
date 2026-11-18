#!/usr/bin/env python3
"""Prepare exact changed review bundle locally. Approval/availability stay false."""
import argparse,hashlib,json
from pathlib import Path
import prepare_pre_shutdown_control as parent
ROOT=Path(__file__).resolve().parents[1]
SCOPE='known-boot-copy-control-3'
def prepare(folder,output,execution,pixels,photo,independent):
 manifest=json.loads((folder/'manifest.json').read_text());e=json.loads(execution.read_text());p=json.loads(pixels.read_text());c=json.loads(photo.read_text());i=json.loads(independent.read_text())
 for r in [e,p,c,i]:
  if r['candidate_sha256']!=manifest['candidate_sha256']:raise ValueError('Different candidate evidence')
 for r in [e,c,i]:
  if r['observer_sha256']!=manifest['observer_sha256']:raise ValueError('Different observer evidence')
 if not(e['late_hook_installed_by_executed_resident_code'] and e['no_synthetic_late_hook_installation'] and e['case_count']>=10 and
        p['no_timer_heap_storage_or_lcd_driver_calls'] and p['all_unselected_pixels_canaries_preserved'] and p['phase_count']==8 and
        c['case_count']>=10 and i['all_executable_bytes_within_proven_copy_and_cache_span'] and
        manifest['embedded_lk_tail_unchanged']):raise ValueError('Incomplete copy/pixel/capture evidence')
 if e['bootstrap_sha256']!=manifest['bootstrap_sha256'] or p['bootstrap_sha256']!=manifest['bootstrap_sha256']:raise ValueError('Different linked bootstrap')
 extras={'controller/'+n:(ROOT/'scripts'/n).read_bytes() for n in ['loader_screen_record.py','decode_loader_screen_photo.py']}
 for name,r in [('execution.json',e),('pixels.json',p),('photo.json',c),('independent.json',i)]:extras['controller/'+name]=(json.dumps(r,indent=2)+'\n').encode()
 r=parent.prepare(folder,output,extras,scope=SCOPE)
 r.update(scope=SCOPE,screen_token=manifest['screen_token'],candidate_sha256=manifest['candidate_sha256'],observer_sha256=manifest['observer_sha256'],copy_boundary_evidence_bound=True,physical_execution_admitted=False)
 return r
if __name__=='__main__':
 a=argparse.ArgumentParser()
 for key in ['folder','out','execution','pixels','photo','independent']:a.add_argument('--'+key,type=Path,required=True)
 x=a.parse_args();print(json.dumps(prepare(x.folder,x.out,x.execution,x.pixels,x.photo,x.independent),indent=2))
