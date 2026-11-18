#!/usr/bin/env python3
"""Offline TPV display DT preview over the proven RAM/storage DT; no boot package."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw
from ack_storage_contract import verify_tree as verify_storage

COMPONENTS={
 'mmsys':('mediatek,mt8163-mmsys',0x14000000),
 'ovl':('mediatek,mt8163-disp-ovl',0x14007000),
 'rdma':('mediatek,mt8163-disp-rdma',0x14009000),
 'color':('mediatek,mt8163-disp-color',0x1400c000),
 'ccorr':('mediatek,mt8163-disp-ccorr',0x1400d000),
 'aal':('mediatek,mt8163-disp-aal',0x1400e000),
 'gamma':('mediatek,mt8163-disp-gamma',0x1400f000),
 'dither':('mediatek,mt8163-disp-dither',0x14010000),
 'ufoe':('mediatek,mt8163-disp-ufoe',0x14011000),
 'dsi':('mediatek,mt8163-dsi',0x14012000),
 'pwm':('mediatek,mt8163-disp-pwm',0x14014000),
 'mutex':('mediatek,mt8163-disp-mutex',0x14015000),
 'larb':('mediatek,mt8163-smi-larb',0x14016000),
 'smi':('mediatek,mt8163-smi-common',0x14017000),
 'phy':('mediatek,mt8163-mipi-tx',0x10215000),
 'iommu':('mediatek,mt8163-m4u',0x10205000),
 'i2c':('mediatek,mt8163-i2c',0x11007000),
 'gpio':('mediatek,mt8163-pinctrl',0x1000b000),
}


def cells(value):
    data=raw(value)
    if len(data)%4:raise ValueError('Unaligned cells')
    return list(struct.unpack('>'+'I'*(len(data)//4),data))


def resources(tree):
    result={}
    for kind,(compat,address) in COMPONENTS.items():
        found=[node for node,p in tree.items() if compat.encode() in raw(p.get('compatible','')).split(b'\0') and len(raw(p.get('reg','')))>=8 and int.from_bytes(raw(p['reg'])[:8],'big')==address]
        if len(found)!=1:raise ValueError('Unique source-backed resource required: '+kind)
        result[kind]=found[0]
    supplies=[node for node,p in tree.items() if raw(p.get('regulator-name',''))==b'vgp3\0']
    if len(supplies)!=1:raise ValueError('Unique working VGP3 supply required')
    result['vddio']=supplies[0]
    if 'gpio-controller' not in tree[result['gpio']] or cells(tree[result['gpio']]['#gpio-cells'])!=[2]:
        raise ValueError('Exact two-cell GPIO provider required')
    return result


def plan(tree,config):
    verify_storage(tree)
    if '# CONFIG_MTK_CMDQ is not set' not in config and 'CONFIG_MTK_CMDQ=n' not in config:
        raise ValueError('This profile uses the established CPU-driven CMDQ-disabled build')
    chosen=tree['/chosen']
    if 'valethon,offline-display-preview' in chosen:raise ValueError('Fresh non-preview input required')
    r=resources(tree);changes=[];phandles={}
    for node,p in tree.items():
        if 'phandle' in p:
            v=cells(p['phandle'])
            if len(v)!=1 or not v[0] or v[0] in phandles:raise ValueError('Ambiguous phandle')
            phandles[v[0]]=node
    next_handle=max(phandles,default=0)+1
    def handle(node):
        nonlocal next_handle
        if node in tree and 'phandle' in tree[node]:return cells(tree[node]['phandle'])[0]
        value=next_handle;next_handle+=1
        if value>=0xffffffff:raise ValueError('Phandle capacity exceeded')
        changes.append(('x',node,'phandle',[value]));return value
    for name,node in r.items():
        if name not in ['gpio','vddio']:changes.append(('s',node,'status','okay'))
        # No command-queue driver is built; do not leave missing mailbox suppliers.
        for prop in ['mboxes','mediatek,gce-client-reg','mediatek,gce-events']:
            if prop in tree[node]:changes.append(('delete',node,prop,None))
    changes.append(('x',r['iommu'],'mediatek,larbs',[handle(r['larb'])]))
    gpio=handle(r['gpio']);supply=handle(r['vddio'])
    pins=r['gpio']+'/douglas-panel-pins';settings=pins+'/pins'
    backlight=r['i2c']+'/backlight@2c';panel=r['dsi']+'/panel@0'
    port=r['dsi']+'/ports/port@1';host_ep=port+'/endpoint';panel_ep=panel+'/port/endpoint'
    i2c_pins=r['gpio']+'/douglas-backlight-i2c-pins';i2c_settings=i2c_pins+'/pins'
    for node in [pins,settings,i2c_pins,i2c_settings,backlight,panel,r['dsi']+'/ports',port,host_ep,panel+'/port',panel_ep]:
        if node in tree:raise ValueError('New display resource already exists: '+node)
        changes.append(('create',node,None,None))
    pins_h=handle(pins);bus_h=handle(i2c_pins);backlight_h=handle(backlight)
    host_h=handle(host_ep);panel_h=handle(panel_ep)
    changes += [('x',settings,'pinmux',[43<<8,83<<8]),('x',settings,'slew-rate',[1]),('flag',settings,'output-low',None),
                ('s',panel,'compatible','amazon,douglas-tpv-panel'),('x',panel,'reg',[0]),('x',panel,'vddio-supply',[supply]),
                ('x',panel,'power-gpios',[gpio,43,0]),('x',panel,'reset-gpios',[gpio,83,1]),
                ('s',panel,'pinctrl-names','default'),('x',panel,'pinctrl-0',[pins_h]),('x',panel,'backlight',[backlight_h]),
                ('s',backlight,'compatible','ti,lp8557'),('x',backlight,'reg',[0x2c]),
                ('s',backlight,'bl-name','douglas-backlight'),('bytes',backlight,'dev-ctrl',[0x47]),('bytes',backlight,'init-brt',[100]),
                ('x',r['dsi'],'#address-cells',[1]),('x',r['dsi'],'#size-cells',[0]),
                ('x',r['dsi']+'/ports','#address-cells',[1]),('x',r['dsi']+'/ports','#size-cells',[0]),('x',port,'reg',[1]),
                ('x',host_ep,'remote-endpoint',[panel_h]),('x',panel_ep,'remote-endpoint',[host_h])]
    # Working board i2c0 pin group is copied from its actual pinmux definition,
    # supplied in the source-backed profile below rather than inferred from labels.
    bus_pins=[(75<<8)|1,(76<<8)|1]
    changes += [('x',i2c_settings,'pinmux',bus_pins),('flag',i2c_settings,'bias-disable',None),
                ('s',r['i2c'],'pinctrl-names','default'),('x',r['i2c'],'pinctrl-0',[bus_h]),
                ('x',r['i2c'],'clock-frequency',[400000])]
    for node,p in tree.items():
        if b'pwm-backlight' in raw(p.get('compatible','')).split(b'\0'):
            changes.append(('s',node,'status','disabled'))
    args=raw(chosen['bootargs']).rstrip(b'\0').decode().split()
    args=[a for a in args if not a.startswith(('console=','earlycon','ramoops.','loglevel=','valethon.native_trial=')) and a not in ['keep_bootcon','initcall_debug','ignore_loglevel']]
    changes += [('s','/chosen','bootargs',' '.join(args+['console=tty0','loglevel=7'])),('flag','/chosen','valethon,offline-display-preview',None)]
    if 'valethon,native-trial' in chosen:changes.append(('delete','/chosen','valethon,native-trial',None))
    return r,changes


def preview(source,config,output,fdtget,fdtput):
    if output.exists() or output.is_symlink():raise ValueError('Fresh preview directory required')
    before=snapshot(fdtget,source);r,changes=plan(before,config)
    output.mkdir(mode=0o700,parents=True);dt=output/'display-preview-private.dtb';dt.write_bytes(source.read_bytes())
    for kind,node,prop,value in changes:
        if kind=='create':command=[str(fdtput),'-c',str(dt),node]
        elif kind=='delete':command=[str(fdtput),'-d',str(dt),node,prop]
        elif kind=='flag':command=[str(fdtput),str(dt),node,prop]
        else:
            datatype={'s':'s','x':'x','bytes':'bx'}[kind]
            values=[value] if kind=='s' else [format(v,'x') for v in value]
            command=[str(fdtput),'-t',datatype,str(dt),node,prop,*values]
        subprocess.run(command,check=True,capture_output=True)
    after=snapshot(fdtget,dt);verify_storage(after)
    for kind,node,prop,value in changes:
        if kind=='create':
            if node not in after:raise ValueError('Created node missing')
            continue
        if kind=='delete':
            if prop in after[node]:raise ValueError('Deleted property survived')
            continue
        expected=(value.encode()+b'\0' if kind=='s' else struct.pack('>'+'I'*len(value),*value) if kind=='x' else bytes(value) if kind=='bytes' else b'')
        if prop not in after[node] or raw(after[node][prop])!=expected:raise ValueError('Display DT edit readback differs')
    changed={(node,prop) for kind,node,prop,value in changes if kind!='create'}
    for node,props in before.items():
        for prop,value in props.items():
            if (node,prop) not in changed and after.get(node,{}).get(prop)!=value:raise ValueError('Unrelated DT property changed')
    from prepare_ack_native_bundle import reservation_map
    if reservation_map(source.read_bytes())[2]!=reservation_map(dt.read_bytes())[2]:raise ValueError('Firmware reserve map changed')
    if len(dt.read_bytes())>0x18000:raise ValueError('Preview DT exceeds metadata capacity')
    # Memory and every reservation remain byte-identical; preview is never a bundle.
    for node,p in before.items():
        if node.startswith(('/memory','/reserved-memory')) and after[node]!=p:raise ValueError('Memory/reservation changed')
    report={'scope':'Offline display DT preview only; no boot bundle or device action','offline_preview':True,
            'physical_execution_admitted':False,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'dtb_sha256':hashlib.sha256(dt.read_bytes()).hexdigest(),'resources':r,'edits':len(changes),
            'panel_variant':'TPV/MP','memory_reservations_preserved':True,'kernel_log_transfer_required':False}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['source','config','output','fdtget','fdtput']:parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();print(json.dumps(preview(args.source,args.config.read_text(),args.output,args.fdtget,args.fdtput),indent=2))
