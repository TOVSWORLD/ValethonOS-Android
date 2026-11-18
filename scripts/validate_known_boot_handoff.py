import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('scripts').resolve()))
from validate_loader_complete import Complete,elf
import retained_log_mailbox as m
module=Path('out/loader-frontend-module/module.elf');seg,sym=elf(module,('lfo_frame_dispatch','lfo_state_bytes'))
# Complete needs all symbols used by Front.
from validate_loader_complete import raw_elf
_,sym=raw_elf(module)
f=Complete(seg,sym,Path('out/original-package-lk-private.bin').read_bytes(),Path('out/loader-complete-bootstrap/bootstrap.elf'),Path('out/trial6-loader-audit/boot.payload').read_bytes()[0xa00:0x1800],packed=Path('out/known-boot-capture-control-1'))
f.native_read();f.final(entry=0x40080000,dt=0x48000000)
assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==4
Path('out/known-boot-capture-control-handoff-result.json').write_text(json.dumps({'actual_original_entry':hex(0x40080000),'actual_original_dtb':hex(0x48000000),'arguments_preserved':True,'hardware_acceptance':False})+'\n')
print('Original-stack handoff argument replay passed')
