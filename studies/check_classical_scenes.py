"""Check delivered physical joins and the complete classical-scene entrance."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent.parent
scene=next(s for s in json.loads((root/'studies/scenes.json').read_text())if s['id']=='gold-earth')
delivery=json.loads((root/'studies/delivery.json').read_text())[scene['id']]
rows=[]
for profile,W,H in [('wide',1600,960),('portrait',768,1280)]:
 R=scene.get('portraitRadius',scene['radius'])if profile=='portrait'else scene['radius']
 tilt=math.radians(scene.get('portrait_angle',scene['angle'])if profile=='portrait'else scene['angle'])
 h=scene.get('portrait_horizon',scene.get('horizon',.53))if profile=='portrait'else scene.get('horizon',.53)
 C=np.array([W/2+R*math.sin(tilt),H*h+R*math.cos(tilt)])
 level=delivery[profile]['levels'][-1];D=level['density'];width=round(W*D)
 images=[np.asarray(Image.open(root/url.split('?')[0])).astype(float)for url in level['urls']]
 starts=[0,int(width*scene['finalInset']/100),width-images[2].shape[1]]
 for state,inset in [('opening',scene.get('portrait_openingInset',25)if profile=='portrait'else scene.get('openingInset',26)),('settled',scene['finalInset'])]:
  for slot,side in [(0,'left'),(2,'right')]:
   x=W*inset/100 if slot==0 else W*(1-inset/100)
   expected=C[1]-math.sqrt(R*R-(x-C[0])**2)
   ys=np.arange(round((expected-12)*D),round((expected+12)*D))
   body_x=min(images[1].shape[1]-1,max(0,round(x*D)-starts[1]))
   material_x=min(images[slot].shape[1]-1,max(0,round(x*D)-starts[slot]))
   photo=images[1][ys,body_x,0]
   body=ys[int(np.argmax(np.gradient(gaussian_filter1d(photo,1.5))))]/D
   pixels=images[slot][ys,material_x]
   if slot==0:
    gold=gaussian_filter1d(pixels[:,0]-pixels[:,2],1.5)
    edge=ys[np.flatnonzero(gold>90)[0]]/D
   else:
    stone=gaussian_filter1d(pixels[:,:2].mean(axis=1),1.5)
    edge=ys[int(np.argmin(np.gradient(stone)))]/D
   body_world_x=(body_x+starts[1])/D
   material_world_x=(material_x+starts[slot])/D
   body_expected=C[1]-math.sqrt(R*R-(body_world_x-C[0])**2)
   material_expected=C[1]-math.sqrt(R*R-(material_world_x-C[0])**2)
   error=abs((edge-material_expected)-(body-body_expected))
   assert error<=1.1,(profile,state,side,error)
   rows.append(dict(profile=profile,state=state,join=side,body_edge=body,material_edge=edge,difference_artboard_px=error))
errors=[];layouts=[]
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome')
 for W,H in [(1512,982),(390,844),(320,740),(844,390)]:
  context=browser.new_context(viewport={'width':W,'height':H},device_scale_factor=2)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8735/classical-scenes/view.html?study=gold-earth');page.wait_for_selector('.stage[data-ready=true]')
  assert page.evaluate('scene.id')=='gold-earth'
  assert page.locator('.arc-study > i').count()==3
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  runway=page.evaluate('document.querySelector("#top").offsetHeight-innerHeight')
  page.evaluate('(r)=>scrollTo(0,r)',runway);page.wait_for_selector('#top.opened');page.evaluate('scrollTo(0,0)')
  assert page.evaluate('document.querySelector("#top").offsetHeight===innerHeight')
  layouts.append(dict(width=W,height=H,one_way_scroll=True,three_layers=True,no_overflow=True))
  context.close()
 browser.close()
assert not errors,errors
report={'delivered_physical_joins':rows,'maximum_difference_artboard_px':max(r['difference_artboard_px']for r in rows),'layouts':layouts,'page_errors':errors,'fan_studies_excluded_from_rotation':True}
(root/'studies/qa/classical-scene-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('Passed8deliveredphysicaljoins<=1.1artboardpx,4viewportlayouts,one-wayentrance,zeroJSerrors')
