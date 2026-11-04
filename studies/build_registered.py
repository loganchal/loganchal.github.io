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
W,H=cfg['artboard'];R=cfg['radius'];center=np.array(cfg['center'])
assert np.allclose(center,[W/2,R+.53*H])
args.output.mkdir(parents=True,exist_ok=True)
for source in cfg['sources']:
 path=args.sources/source['file']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==source['source_sha256'], f"Source changed: {path}"
 image=Image.open(path).convert('RGB')
 black=source['black_point']
 if black:
  image=image.point([max(0,round((v-black)*255/(255-black))) for v in range(256)]*3)
 cx,cy,r=source['circle'];scale=R/r
 target_angle=math.atan2(-math.sqrt(R*R-(source['target_x']-center[0])**2),source['target_x']-center[0])
 theta=target_angle-source['source_angle']
 inverse=np.array([[math.cos(theta),math.sin(theta)],[-math.sin(theta),math.cos(theta)]])/scale
 offset=np.array([cx,cy])-inverse@center
 for width in (1600,3840):
  density=width/W
  assert scale*density<=1, f"Crop would upscale native image: {source['name']}"
  coeff=(inverse[0,0]/density,inverse[0,1]/density,offset[0],inverse[1,0]/density,inverse[1,1]/density,offset[1])
  # Rectangular frame only; never warp or replace the photographed silhouette.
  result=image.transform((width,round(H*density)),Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC,fillcolor=(0,0,0))
  result.save(args.output/(source['name']+'-'+str(width)+'.webp'),quality=95,method=5)
 print(source['name'], 'native pixels per artboard pixel:',round(1/scale,3))
