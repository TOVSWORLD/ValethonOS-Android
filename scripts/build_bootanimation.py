#!/usr/bin/env python3
"""Deterministic Android animation of the owner-selected intercom artwork."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import zipfile
import zlib

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'projects/firetabs-android/android-integration/branding'
WIDTH,HEIGHT,FPS=300,512,24
INTRO,LOOP=36,24

def chunk(kind,data):
 return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)

def png(pixels):
 raw=b''.join(b'\0'+pixels[y*WIDTH*3:(y+1)*WIDTH*3] for y in range(HEIGHT))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',WIDTH,HEIGHT,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')

def smooth(x):
 x=max(0,min(1,x));return x*x*(3-2*x)

def frame(source,index,intro=False):
 pixels=bytearray(source)
 if intro:
  t=index/(INTRO-1)
  for y in range(HEIGHT):
   # Circuit field rises first; the exact logo/name then fade into place.
   if 160<=y<=269:alpha=smooth((t-.48)/.42)
   else:alpha=smooth((t*1.35-(1-y/HEIGHT))/.22)
   for x in range(WIDTH):
    at=(y*WIDTH+x)*3
    for c,bg in enumerate((0,9,30)):
     pixels[at+c]=round(bg+(source[at+c]-bg)*alpha)
 else:
  # Small activity accents occupy the original blank header; artwork unchanged.
  for i in range(5):
   strength=(1+math.cos(2*math.pi*(index/LOOP-i/5)))/2
   color=tuple(round(v*(.20+.80*strength)) for v in (31,182,255))
   for y in range(108,113):
    for x in range(122+i*14,127+i*14):
     if (x-(124+i*14))**2+(y-110)**2<=4:
      at=(y*WIDTH+x)*3;pixels[at:at+3]=bytes(color)
 return png(pixels)

def build_bytes():
 source=zlib.decompress((ART/'intercom-300x512.rgb.zlib').read_bytes())
 if len(source)!=WIDTH*HEIGHT*3:raise ValueError('Incorrect source raster size')
 manifest=json.loads((ART/'artwork-source.json').read_text())
 if hashlib.sha256(source).hexdigest()!=manifest['raster_sha256']:raise ValueError('Artwork raster hash mismatch')
 if hashlib.sha256((ART/'intercom-background.png').read_bytes()).hexdigest()!=manifest['source_sha256']:raise ValueError('Original artwork hash mismatch')
 output=io.BytesIO()
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_STORED) as archive:
  entries=[('desc.txt',f'{WIDTH} {HEIGHT} {FPS}\np 1 0 intro\np 0 0 loop\n'.encode())]
  entries.extend((f'intro/{i:04d}.png',frame(source,i,True)) for i in range(INTRO))
  entries.extend((f'loop/{i:04d}.png',frame(source,i)) for i in range(LOOP))
  for name,data in entries:
   info=zipfile.ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_STORED
   info.external_attr=0o100644<<16;archive.writestr(info,data)
 return output.getvalue()

def build(destination,preview=None):
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_bytes(build_bytes())
 source=zlib.decompress((ART/'intercom-300x512.rgb.zlib').read_bytes())
 if preview:preview.write_bytes(frame(source,5))
 return hashlib.sha256(destination.read_bytes()).hexdigest()

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,required=True)
 parser.add_argument('--preview',type=Path)
 args=parser.parse_args();digest=build(args.output,args.preview)
 print(f'{args.output.stat().st_size} bytes; SHA256 {digest}')
