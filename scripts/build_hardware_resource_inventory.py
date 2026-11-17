import sys,json,hashlib,re,argparse
from pathlib import Path
sys.path.insert(0,'scripts')
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw
fixed={'compatible','reg','status','#address-cells','#size-cells','ranges','dma-ranges','interrupts','interrupts-extended','interrupt-parent','interrupt-controller','#interrupt-cells','phandle','linux,phandle','clocks','clock-names','#clock-cells','clock-frequency','clock-div','assigned-clocks','assigned-clock-parents','assigned-clock-rates','resets','reset-names','#reset-cells','power-domains','#power-domain-cells','dmas','dma-names','#dma-cells','iommus','#iommu-cells','phys','phy-names','#phy-cells','gpio-controller','#gpio-cells','gpio-ranges','pinctrl-names','memory-region','no-map','reusable','size','alignment','alloc-ranges','device_type','enable-method','method','cpu_on','cpu_off','cpu_suspend','affinity_info','bus-width','max-frequency','mmc-hs200-1_8v','non-removable','cap-sd-highspeed','dr_mode','maximum-speed','regulator-name','regulator-min-microvolt','regulator-max-microvolt','regulator-always-on','regulator-boot-on','regulator-ramp-delay','pinmux','bias-disable','bias-pull-up','bias-pull-down','drive-strength','input-enable','output-high','output-low','slew-rate','interrupt-names','reg-names'}
def allowed(k):return k in fixed or re.fullmatch(r'pinctrl-\d+',k) or k.endswith(('-supply','-gpios','_gpios'))
def export(t):
 out={};ph={v['phandle']:n for n,v in t.items() if 'phandle' in v}
 for n,p in sorted(t.items()):
  if n.startswith(('/chosen','/idme','/firmware/android','/aliases')):continue
  props={k:v for k,v in sorted(p.items()) if allowed(k)}
  if not props:continue
  refs={}
  for k,v in props.items():
   if k.endswith('-supply') or k=='interrupt-parent':
    if v in ph:refs[k]=[ph[v]]
   elif re.fullmatch(r'pinctrl-\d+',k):
    b=raw(v);refs[k]=[ph.get(' '.join(format(x,'x') for x in b[i:i+4]),'UNRESOLVED') for i in range(0,len(b),4)]
  out[n]={'properties_hex_bytes':props}
  if refs:out[n]['resolved_direct_providers']=refs
 return out

def build(root, fdtget, output):
 result={'date':'2026-11-17','scope':'Kernel-facing hardware resources from archived working-source and consumed ACK device trees; no new device acquisition','format':'Properties are exact raw big-endian hex bytes; interpret reg/interrupt/clock cells using parent/provider bindings. Direct scalar supply/IRQ-parent/pinctrl links are resolved; multi-cell clock/DMA/IRQ references remain encoded, not guessed.','excluded':'chosen bootargs/nonce/seed, idme identity, aliases and all properties outside explicit hardware allowlist','hardware_support_qualified':False,'trees':{}}
 for key,file in [('working_source_4_9','source-private.dtb'),('tested_ack_6_18','target-private.dtb')]:
  p=root/file;t=snapshot(fdtget,p);result['trees'][key]={'dtb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nodes':export(t)}
 # Verify no identity/argument channels or unintended properties escaped selection.
 for tree in result['trees'].values():
  for n,p in tree['nodes'].items():
   assert not n.startswith(('/chosen','/idme','/firmware/android','/aliases'))
   assert all(allowed(k) for k in p['properties_hex_bytes'])
 output.write_text(json.dumps(result,indent=2)+'\n')
 return result

if __name__ == '__main__':
 p=argparse.ArgumentParser(description='Export allowlisted kernel-facing resources; no device acquisition')
 p.add_argument('--bundle',type=Path,required=True)
 p.add_argument('--fdtget',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 a=p.parse_args()
 if a.output.exists():p.error('Fresh output required')
 result=build(a.bundle,a.fdtget,a.output)
 print(json.dumps({'nodes':{k:len(v['nodes']) for k,v in result['trees'].items()},'allowlist_checked':True,'bytes':a.output.stat().st_size}))
