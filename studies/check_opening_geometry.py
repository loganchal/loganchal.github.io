from source_cache import resolve_source
import json,math,argparse
from pathlib import Path
import numpy as np
from PIL import Image
parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);args=parser.parse_args()
repo=Path(__file__).resolve().parent.parent;scenes=json.loads((repo/'studies/scenes.json').read_text());rows=[]
Image.MAX_IMAGE_PIXELS=None
for s in scenes:
 for pr,W,H in [('wide',1600,960),('portrait',768,1280)]:
  R=s.get('portraitRadius',s['radius']) if pr=='portrait' else s['radius'];t=math.radians(s['angle']);C=np.array([W/2+R*math.sin(t),H*s.get('horizon',.53)+R*math.cos(t)]);d=s.get('portrait_density',s.get('render_density',2.4)) if pr=='portrait' else s.get('render_density',2.4)
  for slot,g in enumerate(s['source_geometry']):
   im=Image.open(resolve_source(args.cache,g['source_file']));cx,cy,r=g['circle'];contact=([208,800,1392] if pr=='wide' else [96,384,672])[slot]
   a=math.atan2(-math.sqrt(R*R-(contact-C[0])**2),contact-C[0])-(g.get('portrait_source_angle',g['source_angle']) if pr=='portrait' else g['source_angle']);inv=np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]])*r/R;o=np.array([cx,cy])-inv@C
   assert R*d/r<=1+1e-8
   # Check every corner of each visible side panel. Affine extrema lie at corners.
   edge=W*(.26 if pr=='wide' else .25);x0,x1=(0,edge) if slot==0 else ((W-edge,W) if slot==2 else (W*s['finalInset']/100,W*(1-s['finalInset']/100)))
   points=np.array([[x,y] for x in [x0,x1] for y in [0,H]])@inv.T+o
   clearance=float(min(points[:,0].min(),points[:,1].min(),im.width-points[:,0].max(),im.height-points[:,1].max()))
   if clearance<0 and g.get('allow_black_extension'):
    # Only empty photographed black field may meet the black stage.
    borders=[]
    for x in [0,im.width-1]:borders.append(np.column_stack([np.full(im.height,x),np.arange(im.height)]))
    for y in [0,im.height-1]:borders.append(np.column_stack([np.arange(im.width),np.full(im.width,y)]))
    border=np.concatenate(borders);q=(border-o)@np.linalg.inv(inv).T
    visible=(q[:,0]>=x0)&(q[:,0]<=x1)&(q[:,1]>=0)&(q[:,1]<=H)
    a=np.array(im.convert('RGB'));pixels=a[border[visible,1],border[visible,0]].astype(float)
    adjusted=np.maximum(0,np.round((pixels-g['black_point'])*255/(255-g['black_point'])))
    maximum=float(adjusted.max()) if len(adjusted) else 0
    assert maximum<=8,(s['id'],pr,slot,'Nonblack source edge would be cut',maximum)
   elif slot!=1 or s.get('fresh_family'):assert clearance>=0,(s['id'],pr,slot,clearance)
   for density in (1,d):
    asset=repo/f'studies/scenes/{s["id"]}/{slot}-{pr}-{round(W*density)}.webp'
    with Image.open(asset) as rendered:assert rendered.size==(round(W*density),round(H*density))
   row=dict(scene=s['id'],profile=pr,slot=slot,source=g['source_file'],source_pixels=list(im.size),native_pixels_per_output_pixel=r/R/d,visible_source_clearance_px=clearance)
   feature={"glass":"glass","red":"porcelain","basket":"basket","lahire":"lahire"}.get(s['slots'][slot])
   if feature:
    measure=json.loads((repo/f'studies/qa/editorial-contours/{feature}.json').read_text());p=np.array(measure['points']);res=(np.linalg.norm(p-[cx,cy],axis=1)-r)*R/r
    row.update(contour_rms_artboard_px=float(np.sqrt(np.mean(res**2))),contour_max_artboard_px=float(abs(res).max()))
   rows.append(row)
(repo/'studies/qa/editorial-geometry-checks.json').write_text(json.dumps(rows,indent=2)+'\n');print('Verified',len(rows),'source registrations; no side panel leaves its native photograph; no image upsampling.')
