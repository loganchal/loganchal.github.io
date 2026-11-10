from pathlib import Path
import json,sys,math
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter1d
from scipy.optimize import least_squares
Image.MAX_IMAGE_PIXELS=None
site=Path(__file__).resolve().parents[3];sys.path.insert(0,str(site/'studies'));from source_cache import resolve_source
bank=Path('/Users/loganchalmers/.codex/visualizations/2026/11/03/01a1a0dc-31b8-7f81-a879-a80620ec2736/opening-image-library');p=site/'studies/scenes.json';scenes=json.load(open(p));proof=[]
for sid,span in [('bode-artemis-rivals',(.045,.54)),('bode-earth-mirror-clock',(-.30,.32))]:
 s=next(x for x in scenes if x['id']==sid);g=s['source_geometry'][0];old=np.array([4204.349245882502,4652.971002348036,4064.8142569076354] if sid=='bode-artemis-rivals' else [4236.613887370342,4652.935913203665,4033.3326469969793]);raw=Image.open(resolve_source(bank,g['source_file']));
 # Only the measured right-hand rim is required; avoid allocating full-size float channels.
 box=(int(old[0]+old[2]-650),int(old[1]-1800),int(old[0]+old[2]+650),int(old[1]+2600));im=np.array(raw.crop(box));chroma=im[:,:,0].astype(np.float32)-im[:,:,2].astype(np.float32)
 points=[];traces=[];radii=np.arange(old[2]+45,old[2]+350,.5)
 for angle in np.linspace(*span,121):
  xs=old[0]+radii*np.cos(angle);ys=old[1]+radii*np.sin(angle)
  z=map_coordinates(chroma,[ys-box[1],xs-box[0]],order=1);z=gaussian_filter1d(z,2);grad=np.gradient(z,radii);gold=np.flatnonzero(z>90);assert len(gold)>0,(sid,angle,'No gold band');last=int(gold[-1]);lo=max(0,last-10);hi=min(len(grad),last+10);k=lo+int(np.argmin(grad[lo:hi]));rr=radii[k];points.append([old[0]+rr*np.cos(angle),old[1]+rr*np.sin(angle)]);traces.append({'angle':angle,'radius':rr,'drop':float(grad[k])})
  assert 2<k<len(radii)-3,(sid,angle,k)
 points=np.array(points);training=points[np.arange(len(points))%5!=0];hold=points[np.arange(len(points))%5==0]
 initial=old.copy();initial[2]+=150
 fit=least_squares(lambda q:np.linalg.norm(training-q[:2],axis=1)-q[2],initial,loss='soft_l1',f_scale=1.5)
 residual=np.linalg.norm(points-fit.x[:2],axis=1)-fit.x[2];inliers=abs(residual)<8;fit=least_squares(lambda q:np.linalg.norm(training[np.abs(np.linalg.norm(training-fit.x[:2],axis=1)-fit.x[2])<8]-q[:2],axis=1)-q[2],fit.x,loss='soft_l1',f_scale=1.0);residual=np.linalg.norm(points-fit.x[:2],axis=1)-fit.x[2];holdres=np.linalg.norm(hold-fit.x[:2],axis=1)-fit.x[2]
 g['circle']=fit.x.tolist();g['fit_points']=points.tolist();g['contour_kind']='Visible outside gold-band boundary against paper; native negative radial chromatic transition. Registered to outside silhouette, replacing the former inner blue/gold boundary.';g['fit_rms_native_px']=float(np.sqrt(np.mean(residual**2)));g['fit_max_native_px']=float(abs(residual).max());g['valid_source_phase_interval_radians']=list(span);g['native_pixels_per_artboard_pixel']=float(fit.x[2]/s['radius']);g['native_pixels_per_portrait_artboard_pixel']=float(fit.x[2]/s.get('portraitRadius',s['radius']));g['confirmation_method']='121 untouched native radial R-B profiles; 25 held out from robust circle fit; only measured source interval is supported.'
 proof.append({'scene':sid,'old_inner_circle':old.tolist(),'outer_gold_circle':fit.x.tolist(),'native_interval':list(span),'rms_native_px':float(np.sqrt(np.mean(residual**2))),'max_native_px':float(abs(residual).max()),'holdout_rms_native_px':float(np.sqrt(np.mean(holdres**2))),'holdout_max_native_px':float(abs(holdres).max()),'inlier_rms_native_px':float(np.sqrt(np.mean(residual[inliers]**2))),'rejected_pick_indices':np.flatnonzero(~inliers).tolist(),'traces':traces,'native_points':points.tolist()})
 print(sid,'old',old,'new',fit.x,'rms',proof[-1]['rms_native_px'],'max',proof[-1]['max_native_px'],flush=True)
 del im
p.write_text(json.dumps(scenes,indent=2,ensure_ascii=False)+'\n');(site/'studies/qa/bode-outer-boundary-fit.json').write_text(json.dumps(proof,indent=2)+'\n')
