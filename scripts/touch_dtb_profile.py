#!/usr/bin/env python3
"""Offline source-backed touch/boot-watchdog DT preview over observed display DT."""
import argparse,json,struct,subprocess,hashlib
from pathlib import Path
from compare_pmic_dtb import snapshot
from display_dtb_profile import cells
from prepare_native_jump_bundle import raw
from prepare_ack_native_bundle import reservation_map


def plan(tree,config):
    for key in ['TOUCHSCREEN_GOODIX','INPUT_EVDEV','I2C_MT65XX','MEDIATEK_WATCHDOG','WATCHDOG_HANDLE_BOOT_ENABLED']:
        if 'CONFIG_'+key+'=y\n' not in config+'\n':raise ValueError('Builtin touch/watchdog support required: '+key)
    if 'CONFIG_WATCHDOG_OPEN_TIMEOUT=0\n' not in config+'\n':raise ValueError('Existing boot-enabled heartbeat contract required')
    def unique(compatible):
        found=[n for n,p in tree.items() if compatible.encode() in raw(p.get('compatible','')).split(b'\0')]
        if len(found)!=1:raise ValueError('Unique touch resource required: '+compatible)
        return found[0]
    gpio=unique('mediatek,mt8163-pinctrl');wdt=unique('mediatek,mt8163-wdt')
    buses=[n for n,p in tree.items() if 'mediatek,mt8163-i2c'.encode() in raw(p.get('compatible','')).split(b'\0') and cells(p.get('reg',''))[:2]==[0,0x11007000]]
    if len(buses)!=1:raise ValueError('Exact I2C0 bus required')
    bus=buses[0]
    if cells(tree[gpio].get('#gpio-cells',''))!=[2] or cells(tree[gpio].get('#interrupt-cells',''))!=[2]:raise ValueError('GPIO/EINT cell contract differs')
    if cells(tree[wdt].get('reg',''))!=[0,0x10007000,0,0x1000]:raise ValueError('Watchdog resource differs')
    if cells(tree[wdt].get('interrupts',''))!=[0,128,8]:raise ValueError('Watchdog IRQ contract differs')
    providers={}
    for name in ['vgp2','vio18']:
        found=[n for n,p in tree.items() if raw(p.get('regulator-name',''))==name.encode()+b'\0']
        if len(found)!=1:raise ValueError('Exact touch regulator required: '+name)
        providers[name]=found[0]
    edits=[];next_phandle=max(cells(p['phandle'])[0] for p in tree.values() if 'phandle' in p)+1
    def phandle(node):
        nonlocal next_phandle
        if 'phandle' in tree.get(node,{}):return cells(tree[node]['phandle'])[0]
        value=next_phandle;next_phandle+=1;edits.append(('x',node,'phandle',[value]));return value
    gp=phandle(gpio);avdd=phandle(providers['vgp2']);io=phandle(providers['vio18'])
    pinbus=gpio+'/valethon-touch-i2c';pinirq=gpio+'/valethon-touch-irq';pinreset=gpio+'/valethon-touch-reset'
    for node in [pinbus,pinirq,pinreset]:
        if node in tree:raise ValueError('Fresh touch pinctrl groups required')
        edits.append(('create',node,None,None))
    pb,pi,pr=[phandle(n) for n in [pinbus,pinirq,pinreset]]
    for node,pins in [(pinbus,[(75<<8)|1,(76<<8)|1]),(pinirq,[35<<8]),(pinreset,[46<<8])]:
        edits.extend([('create',node+'/pins',None,None),('x',node+'/pins','pinmux',pins),('flag',node+'/pins','bias-disable',None)])
    # GPIO35 is EINT46 in the pinned SoC table. Direction switching is owned by
    # the Goodix reset/address-selection sequence; no unsupported slew alias.
    edits.append(('flag',pinirq+'/pins','input-enable',None))
    node=bus+'/touchscreen@5d'
    if node in tree:raise ValueError('Fresh touch node required')
    edits.extend([('create',node,None,None),('s',node,'compatible',['goodix,gt9xx']),('x',node,'reg',[0x5d]),
        ('x',node,'interrupt-parent',[gp]),('x',node,'interrupts',[46,2]),
        ('x',node,'irq-gpios',[gp,35,0]),('x',node,'reset-gpios',[gp,46,0]),
        ('s',node,'pinctrl-names',['default']),('x',node,'pinctrl-0',[pi,pr]),
        ('x',node,'AVDD28-supply',[avdd]),('x',node,'VDDIO-supply',[io]),
        ('s',node,'goodix,config-name',['douglas-gt9xx.cfg']),
        ('x',node,'touchscreen-size-x',[800]),('x',node,'touchscreen-size-y',[1280]),
        ('s',node,'status',['okay']),('s',bus,'pinctrl-names',['default']),('x',bus,'pinctrl-0',[pb]),
        ('s',bus,'status',['okay']),('s',wdt,'status',['okay']),
        ('x',providers['vgp2'],'regulator-min-microvolt',[3000000]),
        ('x',providers['vgp2'],'regulator-max-microvolt',[3000000])])
    if cells(tree[providers['vio18']].get('regulator-min-microvolt',''))!=[1800000] or cells(tree[providers['vio18']].get('regulator-max-microvolt',''))!=[1800000]:raise ValueError('Existing IO1.8V supply required')
    for child in tree:
        if child.startswith(bus+'/') and child.count('/')==bus.count('/')+1:
            edits.append(('s',child,'status',['disabled']))
    for resource in [gpio,wdt,bus,*providers.values()]:
        parent=resource.rsplit('/',1)[0]
        while parent:
            if raw(tree.get(parent,{}).get('status',''))==b'disabled\0':raise ValueError('Disabled touch supplier ancestor: '+parent)
            parent=parent.rsplit('/',1)[0]
    return {'i2c':bus,'gpio':gpio,'watchdog':wdt,'touch':node,**providers},edits


def preview(source,config,output,fdtget,fdtput):
    before=snapshot(fdtget,source);resources,edits=plan(before,config)
    output.mkdir(mode=0o700);dt=output/'touch-preview-private.dtb';dt.write_bytes(source.read_bytes())
    for kind,node,prop,value in edits:
        if kind=='create':args=['-c',str(dt),node]
        elif kind=='flag':args=[str(dt),node,prop]
        else:args=['-t',kind,str(dt),node,prop,*[hex(v)[2:] if kind=='x' else v for v in value]]
        subprocess.run([str(fdtput),*args],check=True,capture_output=True)
    after=snapshot(fdtget,dt)
    for node,p in before.items():
        if node.startswith(('/memory','/reserved-memory')) and after[node]!=p:raise ValueError('RAM/reservation changed')
    if reservation_map(source.read_bytes())[2]!=reservation_map(dt.read_bytes())[2]:raise ValueError('FDT reserve map changed')
    result={'scope':'Offline touch/watchdog DT preview only','offline_preview':True,'physical_execution_admitted':False,
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'dtb_sha256':hashlib.sha256(dt.read_bytes()).hexdigest(),
            'resources':resources,'memory_reservations_preserved':True,'watchdog_driver_enabled':True,
            'watchdog_reset_cause_claimed':False,'irq_gpio':35,'irq_eint_line':46,'analog_microvolts':3000000,'edits':len(edits)}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['source','config','output','fdtget','fdtput']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();print(json.dumps(preview(a.source,a.config.read_text(),a.output,a.fdtget,a.fdtput)))
