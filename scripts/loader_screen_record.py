#!/usr/bin/env python3
"""Decode WRC1 records from normalized framebuffer/photo samples, never writes device."""
import argparse,json,struct
from pathlib import Path
BASE=0x98600000
SURFACE=4096000
CHECK=0xc35a963c
PHASES={1:'resident_hook_install',2:'pre_shutdown_arrival',3:'non_normal_mode',4:'incoming_irq_mask',5:'invalid_device',6:'bridge_result',7:'recorder_result',8:'attempt_consumed'}
def decode_words(words,token,expected_phase=None):
 if len(words)!=4:raise ValueError('Four words required')
 header,value,status,check=words;phase=(header>>16)&255
 if header>>24!=0x57 or header&65535!=token or phase not in PHASES or (expected_phase and phase!=expected_phase):raise ValueError('Magic/token/phase mismatch')
 if check!=header^value^status^CHECK:raise ValueError('Screen checksum mismatch')
 return {'phase':phase,'stage':PHASES[phase],'value':value,'signed_value':value-(1<<32) if value>>31 else value,'cpsr':hex(status),'irq_masked':bool(status&128),'screen_token':f'{token:04x}','kernel_entry_proved':False}
def decode_pixels(sample,token,phase):
 # Sample centers and four nearby points, never border pixels.
 values=[]
 for row in range(4):
  values.append([sum(sample(bit*8+dx,(phase-1)*40+row*8+dy) for dx,dy in [(3,3),(4,3),(3,4),(4,4),(2,2)])/5 for bit in range(32)])
 header=0x57000000|(phase<<16)|token
 black=[v for bit,v in enumerate(values[0]) if not(header&(1<<(31-bit)))];white=[v for bit,v in enumerate(values[0]) if header&(1<<(31-bit))]
 lo=sum(black)/len(black);hi=sum(white)/len(white)
 if hi-lo<64:raise ValueError('Insufficient black/white contrast')
 threshold=(lo+hi)/2;words=[]
 for row in values:
  if any(abs(v-threshold)<(hi-lo)*0.12 for v in row):raise ValueError('Ambiguous pixel cell')
  n=0
  for v in row:n=(n<<1)|int(v>threshold)
  words.append(n)
 return decode_words(words,token,phase)
def decode_surface(raw,token):
 if len(raw)!=SURFACE:raise ValueError('Exact800x1280x4 surface required')
 def sample(x,y):return sum(raw[(y*800+x)*4:(y*800+x)*4+3])/3
 out=[]
 for phase in PHASES:
  try:out.append(decode_pixels(sample,token,phase))
  except ValueError:pass
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--surface',type=Path,required=True);p.add_argument('--token',required=True);a=p.parse_args();r=decode_surface(a.surface.read_bytes(),int(a.token,16));print(json.dumps({'records':r,'positive_capture':bool(r),'kernel_entry_proved':False},indent=2))
