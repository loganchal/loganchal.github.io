from source_cache import resolve_source
"""Rebuild grouped opening scenes from untouched originals in a source cache."""
from pathlib import Path
from PIL import Image
import argparse,json,math,numpy as np
Image.MAX_IMAGE_PIXELS=None
parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);parser.add_argument('--output',type=Path,default=Path(__file__).parent/'scenes');parser.add_argument('--scene',action='append',help='Build only these scene IDs (repeatable)');parser.add_argument('--slot',type=int,action='append',choices=range(3),help='Build only these slots (repeatable)');args=parser.parse_args()
scenes=json.loads((Path(__file__).parent/'scenes.json').read_text())
if args.scene:
 unknown=set(args.scene)-{scene['id'] for scene in scenes}
 if unknown:parser.error('Unknown scene: '+', '.join(sorted(unknown)))
 scenes=[scene for scene in scenes if scene['id'] in args.scene]
for scene in scenes:
 folder=args.output/scene['id'];folder.mkdir(parents=True,exist_ok=True)
 images=[]
 for source in scene['source_geometry']:
  image=Image.open(resolve_source(args.cache,source['source_file'])).convert('RGB');black=source['black_point']
  if black:image=image.point([max(0,round((v-black)*255/(255-black))) for v in range(256)]*3)
  images.append(image)
 for profile,W,H in [('wide',1600,960),('portrait',768,1280)]:
  R=scene.get('portraitRadius',scene['radius']) if profile=='portrait' else scene['radius'];tilt=math.radians(scene['angle']);center=np.array([W/2+R*math.sin(tilt),H*scene.get('horizon',.53)+R*math.cos(tilt)])
  for slot,(name,source,image) in enumerate(zip(scene['slots'],scene['source_geometry'],images)):
   if args.slot and slot not in args.slot:continue
   cx,cy,r=source['circle'];angle=source.get('portrait_source_angle',source['source_angle']) if profile=='portrait' else source['source_angle'];contact=([208,800,1392] if profile=='wide' else [96,384,672])[slot]
   if name=='saturn' and (profile=='portrait' or slot==0):angle=math.atan2(-math.sqrt(r*r-(3800-cx)**2),3800-cx)
   theta=math.atan2(-math.sqrt(R*R-(contact-center[0])**2),contact-center[0])-angle
   inverse=np.array([[math.cos(theta),math.sin(theta)],[-math.sin(theta),math.cos(theta)]])*r/R;offset=np.array([cx,cy])-inverse@center
   for density in (1,scene.get('portrait_density',scene.get('render_density',2.4)) if profile=='portrait' else scene.get('render_density',2.4)):
    assert R*density/r<=1+1e-8,'Would enlarge native source pixels'
    coeff=(inverse[0,0]/density,inverse[0,1]/density,offset[0],inverse[1,0]/density,inverse[1,1]/density,offset[1]);result=image.transform((round(W*density),round(H*density)),Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC,fillcolor=(0,0,0));result.save(folder/f'{slot}-{profile}-{round(W*density)}.webp',quality=95,method=5)
 print(scene['id'],'rebuilt')
