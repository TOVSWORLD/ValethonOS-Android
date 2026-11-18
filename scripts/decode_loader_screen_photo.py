#!/usr/bin/env python3
"""Read WRC1 from a private screen photo. No image/device writes or upload.

--quad is LCD corners TL TR BR BL in logical portrait orientation. Samples the
original pixels through a projective mapping; does not create an edited image.
Requires Pillow on the controller, not on the tablet/lab.
"""
import argparse,json
from pathlib import Path
from loader_screen_record import decode_pixels,PHASES

def project(quad,source=None):
 if len(quad)!=8:raise ValueError('Four LCD corners required')
 points=list(zip(quad[::2],quad[1::2]));matrix=[]
 for (u,v),(x,y) in zip(source or [(0,0),(800,0),(800,1280),(0,1280)],points):
  matrix.extend([[u,v,1,0,0,0,-x*u,-x*v,x],[0,0,0,u,v,1,-y*u,-y*v,y]])
 for col in range(8):
  pivot=max(range(col,8),key=lambda r:abs(matrix[r][col]))
  matrix[col],matrix[pivot]=matrix[pivot],matrix[col]
  n=matrix[col][col]
  if abs(n)<1e-10:raise ValueError('Degenerate LCD corner geometry')
  matrix[col]=[v/n for v in matrix[col]]
  for row in range(8):
   if row!=col:
    n=matrix[row][col];matrix[row]=[a-n*b for a,b in zip(matrix[row],matrix[col])]
 a,b,c,d,e,f,g,h=[row[8] for row in matrix]
 def locate(x,y):
  den=g*x+h*y+1
  if abs(den)<1e-10:raise ValueError('Invalid photo projection')
  return (a*x+b*y+c)/den,(d*x+e*y+f)/den
 locate.coefficients=(a,b,c,d,e,f,g,h)
 return locate

def decode(image,token,quad=None):
 image=image.convert('L');width,height=image.size
 locate=project(quad or [0,0,width,0,width,height,0,height])
 def sample(x,y):
  a,b=locate(x+0.5,y+0.5)
  if not(0<=a<width and 0<=b<height):raise ValueError('LCD sample outside photo')
  return image.getpixel((int(a),int(b)))
 records=[];rejected=[]
 for phase in PHASES:
  try:records.append(decode_pixels(sample,token,phase))
  except ValueError as e:rejected.append({'phase':phase,'reason':str(e)})
 return {'format':'WRC1','records':records,'positive_capture':bool(records),
         'rejected_rows':rejected,'kernel_entry_proved':False,
         'no_record_interpretation':'Unqualified/absent visual capture; does not locate a failed stage.'}
if __name__=='__main__':
 from PIL import Image
 p=argparse.ArgumentParser();p.add_argument('--image',type=Path,required=True);p.add_argument('--token',required=True);p.add_argument('--quad',nargs=8,type=float)
 a=p.parse_args()
 with Image.open(a.image) as image:result=decode(image,int(a.token,16),a.quad)
 print(json.dumps(result,indent=2));raise SystemExit(0 if result['positive_capture'] else 2)
