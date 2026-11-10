"""Measure visible outer-gold and photographed body edges in delivery crops."""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
root=Path(__file__).resolve().parent.parent
scenes={s['id']:s for s in json.loads((root/'studies/scenes.json').read_text())}
delivery=json.loads((root/'studies/delivery.json').read_text())
rows=[]
for sid in ['bode-artemis-rivals','bode-earth-mirror-clock']:
 s=scenes[sid]
 for profile,W,H in [('wide',1600,960),('portrait',768,1280)]:
  R=s.get('portraitRadius',s['radius'])if profile=='portrait'else s['radius']
  t=math.radians(s.get('portrait_angle',s['angle'])if profile=='portrait'else s['angle'])
  h=s.get('portrait_horizon',s.get('horizon',.53))if profile=='portrait'else s.get('horizon',.53)
  C=np.array([W/2+R*math.sin(t),H*h+R*math.cos(t)])
  level=delivery[sid][profile]['levels'][-1];D=level['density'];width=round(W*D)
  imgs=[np.array(Image.open(root/u.split('?')[0])).astype(float)for u in level['urls'][:2]];offset=int(width*s['finalInset']/100)
  for state,inset in [('opening',s.get('portrait_openingInset',25)if profile=='portrait'else s.get('openingInset',26)),('settled',s['finalInset'])]:
   x=W*inset/100;y=C[1]-math.sqrt(R*R-(x-C[0])**2)
   ys=np.arange(round((y-25)*D),round((y+25)*D));ix=min(imgs[0].shape[1]-1,round(x*D));jx=min(imgs[1].shape[1]-1,max(0,round(x*D)-offset))
   rgb=imgs[0][ys,ix];chroma=gaussian_filter1d(rgb[:,0]-rgb[:,2],1.5)
   picks=np.flatnonzero(chroma>90);assert len(picks),(sid,profile,state,'gold boundary absent')
   gold=ys[picks[0]]/D
   red=gaussian_filter1d(imgs[1][ys,jx,0],1.5);body=ys[int(np.argmax(np.gradient(red)))]/D
   gx=ix/D;bx=(jx+offset)/D
   gy=C[1]-math.sqrt(R*R-(gx-C[0])**2);by=C[1]-math.sqrt(R*R-(bx-C[0])**2)
   diff=(gold-gy)-(body-by)
   assert abs(diff)<=2,(sid,profile,state,'visible boundary mismatch',diff)
   rows.append(dict(scene=sid,profile=profile,state=state,gold_edge=gold,body_edge=body,edge_difference_artboard_px=diff))
   print(sid,profile,state,round(diff,3),flush=True)
(root/'studies/qa/bode-delivered-joins.json').write_text(json.dumps(rows,indent=2)+'\n')
