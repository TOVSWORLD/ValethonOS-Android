#!/usr/bin/env python3
"""Exact own-source eMMC mailbox prerequisite DT; compile only, no device action."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import build_lab_log_dtb as base
from compare_pmic_dtb import snapshot
from build_douglas_dtb import inspect_header
ROOT=Path(__file__).resolve().parents[1]


def build(output,nonce):
    if output.exists() or output.is_symlink() or len(nonce)!=32 or not any(nonce):
        raise ValueError('Fresh output/fresh32-byte nonce required')
    output.mkdir(mode=0o700)
    baseline=base.build(output/'baseline')
    extra='''
/* Minimal persistent log prerequisite; no HS200/high-speed/reset trial. */
&pio { status = "okay"; };
&pwrap { status = "okay"; };
&mmc0 {
 status = "okay";
 max-frequency = <26000000>;
 /delete-property/ mmc-hs200-1_8v;
 /delete-property/ cap-mmc-highspeed;
 /delete-property/ cap-mmc-hw-reset;
};
/ { chosen { valethon,trial-nonce = [NONCE]; }; };
'''.replace('NONCE',' '.join(f'{v:02x}' for v in nonce))
    source=output/'retained.dts';source.write_bytes((output/'baseline/lab.dts').read_bytes()+extra.encode())
    dtc=ROOT/'work/dtb-tool/build/dtc';get=ROOT/'work/dtb-tool/build/fdtget';target=output/'retained.dtb'
    r=subprocess.run([str(dtc),'-a','4','-I','dts','-O','dtb','-o',str(target),str(source)],capture_output=True,text=True,check=True)
    if r.stderr:raise ValueError('Retained DT diagnostics require correction')
    before=snapshot(get,output/'baseline/lab.dtb');after=snapshot(get,target)
    expected=json.loads(json.dumps(before))
    for path in ['/soc/pinctrl@1000b000','/soc/pwrap@1000d000','/soc/mmc@11230000']:
        expected[path]['status']=base.string('okay')
    mmc=expected['/soc/mmc@11230000'];mmc['max-frequency']=base.encoded((26000000).to_bytes(4,'big'))
    for name in ['mmc-hs200-1_8v','cap-mmc-highspeed','cap-mmc-hw-reset']:mmc.pop(name)
    expected['/chosen']['valethon,trial-nonce']=base.encoded(nonce)
    if expected!=after:raise ValueError('Unexpected retained DT delta')
    report={'scope':'Own-source minimal eMMC logging prerequisite, no physical acceptance','artifact':inspect_header(target.read_bytes()),'baseline':baseline,'nonce_sha256':hashlib.sha256(nonce).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'exact_delta_only':True,'max_frequency':26000000,'hs200_highspeed_hwreset_removed':True,'firmware_reservations_unchanged':True,'device_written':False}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--nonce-file',type=Path,required=True);a=p.parse_args()
    print(json.dumps(build(a.output,a.nonce_file.read_bytes()),indent=2))
