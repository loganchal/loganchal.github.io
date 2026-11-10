from pathlib import Path
import sys,json,math,copy
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter1d
Image.MAX_IMAGE_PIXELS=None
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'studies'));from source_cache import resolve_source
bank=Path('/Users/loganchalmers/.codex/visualizations/2026/11/03/01a1a0dc-31b8-7f81-a879-a80620ec2736/opening-image-library');path=root/'studies/scenes.json';scenes=json.load(open(path));reference=next(s for s in scenes if s['id']=='gold-earth')['source_geometry'][1];proof=[]
for sid in ['bode-artemis-rivals','bode-earth-mirror-clock']:
 s=next(x for x in scenes if x['id']==sid);g=s['source_geometry'][0];photo=s['source_geometry'][1]
 if sid=='bode-earth-mirror-clock':
  for k in ['circle','fit_points','fit_rms_native_px','fit_max_native_px','contour_kind']:photo[k]=copy.deepcopy(reference[k])
  photo['native_pixels_per_artboard_pixel']=photo['circle'][2]/s['radius'];photo['native_pixels_per_portrait_artboard_pixel']=photo['circle'][2]/s['portraitRadius']
 cx,cy,r=g['circle'];box=(int(cx+r-750),int(cy-2100),int(cx+r+750),int(cy+2800));raw=Image.open(resolve_source(bank,g['source_file']));im=np.array(raw.crop(box));chroma=im[:,:,0].astype(np.float32)-im[:,:,2].astype(np.float32);red=np.array(Image.open(resolve_source(bank,photo['source_file'])).getchannel('R'),dtype=np.float32)
 for profile,W,H in [('wide',1600,960),('portrait',768,1280)]:
  R=s['radius']if profile=='wide'else s['portraitRadius'];t=math.radians(s['angle']if profile=='wide'else s.get('portrait_angle',s['angle']));h=s.get('horizon',.53)if profile=='wide'else s.get('portrait_horizon',s.get('horizon',.53));C=np.array([W/2+R*math.sin(t),H*h+R*math.cos(t)]);key='source_angle'if profile=='wide'else'portrait_source_angle';old=g.get(key,g['source_angle']);contact=g.get('target_x',208)if profile=='wide'else g.get('portrait_target_x',96);q=math.atan2(-math.sqrt(R*R-(contact-C[0])**2),contact-C[0]);pcx,pcy,pr=photo['circle'];px=photo.get('target_x',800)if profile=='wide'else photo.get('portrait_target_x',384);pa=math.atan2(-math.sqrt(R*R-(px-C[0])**2),px-C[0])-photo.get(key,photo['source_angle']);PM=np.array([[math.cos(pa),math.sin(pa)],[-math.sin(pa),math.cos(pa)]])*pr/R;po=np.array([pcx,pcy])-PM@C
  dy=np.arange(-6,6,.1);seams=[];opening=s['openingInset']if profile=='wide'else s['portrait_openingInset']
  for inset in [opening,s['finalInset']]:
   x=W*inset/100;y=C[1]-math.sqrt(R*R-(x-C[0])**2);p=np.column_stack([np.full(len(dy),x),y+dy])@PM.T+po;z=map_coordinates(red,[p[:,1],p[:,0]],order=1,mode='constant');grad=np.gradient(gaussian_filter1d(z,2));valid=np.flatnonzero(abs(dy)<4);k=valid[np.argmax(grad[valid])];seams.append((x,y,float(dy[k])))
  options=[]
  for phase in np.linspace(old-.08,old+.08,641):
   a=q-phase;M=np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]])*r/R;o=np.array([cx,cy])-M@C;corn=np.array([[x,y]for x in [0,W*opening/100]for y in [0,H]])@M.T+o
   if min(corn[:,0].min(),corn[:,1].min(),raw.width-corn[:,0].max(),raw.height-corn[:,1].max())<0:continue
   diffs=[]
   for x,y,body in seams:
    nativephase=math.atan2(-math.sqrt(R*R-(x-C[0])**2),x-C[0])-a;nativephase=(nativephase+math.pi)%(2*math.pi)-math.pi
    if not(g['valid_source_phase_interval_radians'][0]<=nativephase<=g['valid_source_phase_interval_radians'][1]):break
    pts=np.column_stack([np.full(len(dy),x),y+dy])@M.T+o;z=map_coordinates(chroma,[pts[:,1]-box[1],pts[:,0]-box[0]],order=1);z=gaussian_filter1d(z,1);pick=np.flatnonzero(z>90)
    if not len(pick):break
    diffs.append(float(dy[pick[0]]-body))
   if len(diffs)==2:options.append((max(abs(v)for v in diffs)+abs(phase-old)*.05,float(phase),diffs))
  assert options,(sid,profile,'no supported registration');best=min(options);g[key]=best[1];proof.append({'scene':sid,'profile':profile,'old_phase':old,'new_phase':best[1],'native_predicted_differences_artboard_px':best[2]});print(proof[-1],flush=True)
path.write_text(json.dumps(scenes,indent=2,ensure_ascii=False)+'\n');(root/'studies/qa/bode-rigid-framing.json').write_text(json.dumps(proof,indent=2)+'\n')
