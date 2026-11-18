#!/usr/bin/env python3
"""Photo-analysis tests from exact emulated pixels; no real camera evidence."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageFilter
from decode_loader_screen_photo import decode,project

def validate(image,manifest):
 meta=json.loads(manifest.read_text());token=int(meta['screen_token'],16);source=Image.open(image).convert('RGB');cases=[]
 def positive(name,picture,quad=None):
  r=decode(picture,token,quad);assert [x['phase'] for x in r['records']]==list(range(1,9)),(name,r);cases.append(name)
 positive('exact_emitted_pixels',source)
 positive('two_times_scale',source.resize((1600,2560)))
 positive('moderate_blur',source.filter(ImageFilter.GaussianBlur(0.7)))
 positive('exposure_offset_and_reduced_contrast',source.point(lambda x:40+round(x*0.65)))
 quad=[40,30,440,50,460,710,20,730]
 inverse=project([0,0,800,0,800,1280,0,1280],list(zip(quad[::2],quad[1::2])))
 photo=source.transform((500,800),Image.Transform.PERSPECTIVE,inverse.coefficients,resample=Image.Resampling.BILINEAR)
 positive('perspective_lcd_quad',photo,quad)
 rotated=source.transpose(Image.Transpose.ROTATE_90)
 positive('portrait_record_in_landscape_photo',rotated,[0,800,0,0,1280,0,1280,800])
 assert not decode(source,token^1)['positive_capture'];cases.append('wrong_capture_token_rejected')
 assert not decode(Image.new('RGB',(800,1280),'gray'),token)['positive_capture'];cases.append('blank_low_contrast_rejected')
 assert not decode(source,token,[300,500,700,500,700,1200,300,1200])['positive_capture'];cases.append('wrong_lcd_region_rejected')
 try:project([0,0,0,0,0,0,0,0])
 except ValueError:cases.append('degenerate_quad_rejected')
 else:raise AssertionError('Degenerate photo geometry accepted')
 return {'scope':'Independent Pillow photo decoder against exact emitted local ARM pixels with synthetic scale/blur/exposure/perspective/rotation; not actual tablet visibility or camera qualification.',
 'candidate_sha256':meta['candidate_sha256'],'observer_sha256':meta['observer_sha256'],'case_count':len(cases),'cases':cases,'kernel_entry_proved':False,'actual_camera_capture':False,'device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for key in ['image','manifest','output']:p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();r=validate(a.image,a.manifest);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Independent photo-decoder controls passed:',r['case_count'])
