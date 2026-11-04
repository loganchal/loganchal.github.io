"""Build the accepted photographic composition using only similarity transforms.
Usage: python3 studies/build_registered.py --sources /path/to/originals
The measured source contours and provenance are in registration.json and qa/.
"""
from pathlib import Path
from PIL import Image
import argparse, json, math, hashlib
import numpy as np
Image.MAX_IMAGE_PIXELS = None
parser=argparse.ArgumentParser()
parser.add_argument('--sources',type=Path,required=True)
parser.add_argument('--output',type=Path,default=Path(__file__).parent/'registered')
args=parser.parse_args()
cfg=json.loads((Path(__file__).parent/'registration.json').read_text())
args.output.mkdir(parents=True,exist_ok=True)
for source in cfg['sources']:
 path=args.sources/source['file']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==source['source_sha256'], f"Source changed: {path}"
 image=Image.open(path).convert('RGB')
 black=source['black_point']
 if black:
  image=image.point([max(0,round((v-black)*255/(255-black))) for v in range(256)]*3)
 cx,cy,r=source['circle']
 for profile in cfg['profiles']:
  W,H=profile['artboard'];R=profile['radius'];center=np.array(profile['center'])
  assert np.allclose(center,[W/2,R+.53*H])
  scale=R/r;source_angle=source['source_angle']
  override=profile.get('source_x_overrides',{}).get(source['name'])
  if override is not None:
   source_angle=math.atan2(-math.sqrt(r*r-(override-cx)**2),override-cx)
  contact=profile['side_contact_x'][source['name']]
  target_angle=math.atan2(-math.sqrt(R*R-(contact-center[0])**2),contact-center[0])
  theta=target_angle-source_angle
  inverse=np.array([[math.cos(theta),math.sin(theta)],[-math.sin(theta),math.cos(theta)]])/scale
  offset=np.array([cx,cy])-inverse@center
  for density in (1,2.4):
   assert scale*density<=1, f"Crop would upscale native image: {source['name']}"
   width=round(W*density)
   coeff=(inverse[0,0]/density,inverse[0,1]/density,offset[0],inverse[1,0]/density,inverse[1,1]/density,offset[1])
   result=image.transform((width,round(H*density)),Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC,fillcolor=(0,0,0))
   tag=source['name']+('-portrait' if profile['name']=='portrait' else '')
   result.save(args.output/(tag+'-'+str(width)+'.webp'),quality=95,method=5)
 print(source['name'], 'native pixels per artboard pixel:',round(r/cfg['radius'],3))
