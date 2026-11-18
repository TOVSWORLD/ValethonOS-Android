#!/usr/bin/env python3
"""Install the source-locked TPV panel in a disposable ACK tree; no DT activation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from generate_douglas_tpv_sequence import function,translate,render,SOURCE,OUTPUT
ROOT=Path(__file__).resolve().parents[1]
PORT=ROOT/'projects/firetabs-android/kernel/display-port'
KCONFIG='''
config DRM_PANEL_AMAZON_DOUGLAS_TPV
	tristate "Amazon Douglas TPV production panel"
	depends on OF && DRM_MIPI_DSI && GPIOLIB && REGULATOR
	depends on BACKLIGHT_CLASS_DEVICE
	help
	  Source-backed TPV variant for the Amazon Fire HD8 (2017).
	  Other panel vendors are not matched. Runtime qualification is separate.
'''
MAKEFILE='\nobj-$(CONFIG_DRM_PANEL_AMAZON_DOUGLAS_TPV) += panel-amazon-douglas-tpv.o\n'


def install(source,revision):
    lock=json.loads((PORT/'panel-inputs.json').read_text())
    if revision!=lock['ack_commit']:
        raise ValueError('Exact ACK revision required')
    if OUTPUT.read_text()!=render(translate(function(SOURCE.read_text()))):
        raise ValueError('TPV table differs from working source')
    for name,digest in lock['sources_sha256'].items():
        if hashlib.sha256((PORT/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Panel source changed after lock')
        dest=source/'drivers/gpu/drm/panel'/Path(name).name
        if dest.exists() or dest.is_symlink():
            raise ValueError('New panel target already exists')
    for name,digest in lock['targets'].items():
        path=source/name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Panel build input drift')
    for name in lock['sources_sha256']:
        (source/'drivers/gpu/drm/panel'/Path(name).name).write_bytes((PORT/name).read_bytes())
    for name,extra in [('Kconfig',KCONFIG),('Makefile',MAKEFILE)]:
        path=source/'drivers/gpu/drm/panel'/name;path.write_text(path.read_text()+extra)
    return {'scope':'TPV panel sources installed; no DT activation or device action',
            'sources':list(lock['sources_sha256']),'hardware_execution':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);args=parser.parse_args()
    revision=subprocess.check_output(['git','-C',str(args.source),'rev-parse','HEAD'],text=True).strip()
    print(json.dumps(install(args.source,revision),indent=2))
