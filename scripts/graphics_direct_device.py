#!/usr/bin/env python3
"""One reviewed GPU candidate replacement from existing original TWRP only."""
import argparse,json,re
from pathlib import Path
from restore_diagnostic_boot import Adb,BOOT_BYTES,BOOT,RECOVERY,RECOVERY_BYTES,PartitionReadError,sha,validate_backup,preflight,restore
from display_direct_device import ORIGINAL,RECOVERY as RECOVERY_SHA
ROOT=Path(__file__).resolve().parents[1]
TOUCH_SHA=json.loads((ROOT/'evidence/touch-input-source/touch-runtime-result.json').read_text())['candidate_sha256']
LOCK=ROOT/'evidence/graphics-source/direct-preparation-result.json'


class ExactReadAdb(Adb):
    def read(self,node,size):
        expected={BOOT:BOOT_BYTES,RECOVERY:RECOVERY_BYTES}
        if node not in expected or size!=expected[node]: raise ValueError('Only exact boot/recovery reads admitted')
        sectors=self.run(['exec-out','cat','/sys/class/block/'+Path(node).name+'/size']).strip()
        if not re.fullmatch(rb'[0-9]+',sectors) or int(sectors)*512!=size: raise ValueError('Full partition geometry differs')
        data=self.run(['exec-out','head','-c',str(size),node])
        if len(data)!=size: raise PartitionReadError(size,data)
        return data


def inputs(case):
    report=json.loads((case/'report.json').read_text());lock=json.loads(LOCK.read_text());auth=json.loads((case/'owner-authorization-private.json').read_text())
    candidate=(case/'boot-full.img').read_bytes();original=(case/'original-boot.img').read_bytes();nonce=(case/'trial-nonce-private.bin').read_bytes()
    manifest={'boot':{'bytes':BOOT_BYTES,'sha256':ORIGINAL},'recovery':{'bytes':RECOVERY_BYTES,'sha256':RECOVERY_SHA}};validate_backup(original,manifest)
    expected={'scope':'graphics-direct-1','candidate_sha256':sha(candidate),'nonce_sha256':sha(nonce),
              'expected_current_boot_sha256':TOUCH_SHA,'runner_sha256':sha(Path(__file__).read_bytes()),'owner_approved':True,
              'maximum_candidate_writes':1,'recovery_writes_allowed':False,'automatic_trial_retry':False}
    if any(type(auth.get(k)) is not type(v) or auth.get(k)!=v for k,v in expected.items()): raise ValueError('Exact fresh graphics authorization required')
    if (len(candidate)!=BOOT_BYTES or len(nonce)!=32 or sha(candidate)!=report['partition_sha256']
            or lock.get('ready_for_attended_test') is not True or lock.get('candidate_sha256')!=sha(candidate)
            or report.get('scope')!='Offline direct graphics candidate only' or report.get('authorization_scope')!='graphics-direct-1'
            or report['nonce_sha256']!=sha(nonce) or report.get('expected_current_boot_sha256')!=TOUCH_SHA
            or report.get('owner_selected_stay_in_twrp') is not True or report.get('automatic_trial_retry') is not False
            or report.get('kernel',{}).get('image_sha256')!='c8fd42b8cad42b75246a5d757b3de80b151076fa4a6a344fcc278fe0912880f5'
            or report.get('source_sha256')!=sha((Path(__file__).parent/'prepare_graphics_direct_boot.py').read_bytes())
            or report.get('pack_source_sha256')!=sha((Path(__file__).parent/'pack_graphics_boot.py').read_bytes())):
        raise ValueError('Exact qualified graphics package required')
    return candidate,original,manifest


def run(case,adb,action):
    candidate,original,manifest=inputs(case)
    if action=='preflight':preflight(adb,original,manifest,TOUCH_SHA);return {'preflight':'passed','written':False}
    if action!='install': raise ValueError('Only preflight and one candidate install admitted; stay in TWRP afterward')
    m={'boot':{'bytes':BOOT_BYTES,'sha256':sha(candidate)},'recovery':manifest['recovery']}
    return restore(adb,candidate,m,TOUCH_SHA,case/'install-receipt.json',operation='owner-requested next graphics test; one replacement of exact touch p5')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=Path,required=True);p.add_argument('--selector-file',type=Path,required=True);p.add_argument('action',choices=['preflight','install'])
    a=p.parse_args();selector=json.loads(a.selector_file.read_text())['selector']
    if not isinstance(selector,str) or not selector or selector.startswith('-'): raise ValueError('Explicit selected tablet required')
    print(json.dumps(run(a.case,ExactReadAdb('adb',selector),a.action)))
