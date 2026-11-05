import json,math,argparse
from pathlib import Path
import numpy as np
from PIL import Image
parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);args=parser.parse_args()
repo=Path(__file__).resolve().parent.parent;scenes=json.loads((repo/'studies/scenes.json').read_text());rows=[]
Image.MAX_IMAGE_PIXELS=None
for s in scenes:
 if s['id'] not in ['prism-eclipse','porcelain-earth','woven-earth','night-gradient']:continue
 for pr,W,H in [('wide',1600,960),('portrait',768,1280)]:
  R=s['radius'];t=math.radians(s['angle']);C=np.array([W/2+R*math.sin(t),H*.53+R*math.cos(t)]);d=s.get('render_density',2.4)
  for slot,g in enumerate(s['source_geometry']):
   im=Image.open(args.cache/g['source_file']);cx,cy,r=g['circle'];contact=([208,800,1392] if pr=='wide' else [96,384,672])[slot]
   a=math.atan2(-math.sqrt(R*R-(contact-C[0])**2),contact-C[0])-g['source_angle'];inv=np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]])*r/R;o=np.array([cx,cy])-inv@C
   assert R*d/r<=1+1e-8
   # Check every corner of each visible side panel. Affine extrema lie at corners.
   edge=W*(.26 if pr=='wide' else .25);x0,x1=(0,edge) if slot==0 else ((W-edge,W) if slot==2 else (W*s['finalInset']/100,W*(1-s['finalInset']/100)))
   points=np.array([[x,y] for x in [x0,x1] for y in [0,H]])@inv.T+o
   clearance=float(min(points[:,0].min(),points[:,1].min(),im.width-points[:,0].max(),im.height-points[:,1].max()))
   if slot!=1:assert clearance>=0,(s['id'],pr,slot,clearance)
   for density in (1,d):
    asset=repo/f'studies/scenes/{s["id"]}/{slot}-{pr}-{round(W*density)}.webp'
    with Image.open(asset) as rendered:assert rendered.size==(round(W*density),round(H*density))
   row=dict(scene=s['id'],profile=pr,slot=slot,source=g['source_file'],source_pixels=list(im.size),native_pixels_per_output_pixel=r/R/d,visible_source_clearance_px=clearance)
   feature={"glass":"glass","red":"porcelain","basket":"basket"}.get(s['slots'][slot])
   if feature:
    measure=json.loads((repo/f'studies/qa/editorial-contours/{feature}.json').read_text());p=np.array(measure['points']);res=(np.linalg.norm(p-[cx,cy],axis=1)-r)*R/r
    row.update(contour_rms_artboard_px=float(np.sqrt(np.mean(res**2))),contour_max_artboard_px=float(abs(res).max()))
   rows.append(row)
(repo/'studies/qa/editorial-geometry-checks.json').write_text(json.dumps(rows,indent=2)+'\n');print('Verified',len(rows),'source registrations; no side panel leaves its native photograph; no image upsampling.')
