from pathlib import Path
from playwright.sync_api import sync_playwright
import json,argparse
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8732');parser.add_argument('--screenshots',type=Path,default=Path('/tmp/loganchal-opening-qa'));parser.add_argument('--scene',action='append',help='Limit layout checks to these scene IDs');parser.add_argument('--report',type=Path,help='Write a separate QA receipt');args=parser.parse_args()
repo=Path(__file__).resolve().parent.parent;out=args.screenshots;out.mkdir(parents=True,exist_ok=True)
catalogue=(repo/'studies/catalogue.js').read_text();catalogue=json.loads(catalogue[catalogue.index('['):catalogue.rindex(']')+1]);active=[s['id'] for s in catalogue if s.get('active',True)];inactive={s['id'] for s in catalogue if not s.get('active',True)};count=len(active)
ids=args.scene or active;checks=[];errors=[]
if set(ids)-set(active):parser.error('Layout checks require active scene IDs')
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome')
 for id in ids:
  for W,H in [(1512,982),(1728,1117),(390,844),(844,390)]:
   page=browser.new_page(viewport={'width':W,'height':H},device_scale_factor=2)
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('response',lambda r:errors.append(f'{r.status} {r.url}') if r.status>=400 and not r.url.endswith('/favicon.ico') else None)
   page.goto(f'{args.url}/?study={id}')
   page.wait_for_selector('.stage[data-ready=true]');page.wait_for_timeout(250)
   assert page.locator('.stage').get_attribute('data-scene')==id
   assert page.evaluate('document.documentElement.scrollWidth===innerWidth')
   get=lambda:page.evaluate("parseFloat(getComputedStyle(document.querySelector('.stage')).getPropertyValue('--inset'))")
   before=get();runway=page.evaluate("document.querySelector('#top').offsetHeight-innerHeight")
   if W in [1512,390]:page.screenshot(path=str(out/f'{id}-{W}-initial.png'))
   page.evaluate('(n)=>scrollTo(0,n)',runway*.5);page.wait_for_function("value=>parseFloat(getComputedStyle(document.querySelector('.stage')).getPropertyValue('--inset'))<value",arg=before);partial=get();assert partial<before
   page.evaluate('scrollTo(0,0)');page.wait_for_timeout(100);assert abs(get()-partial)<.01,'Transition rewound'
   page.evaluate('(n)=>scrollTo(0,n)',runway);page.wait_for_function("document.querySelector('#top').classList.contains('opened')")
   assert page.locator('#top').evaluate("e=>e.classList.contains('opened')")
   final=get();page.evaluate('scrollTo(0,innerHeight)');page.wait_for_timeout(100);page.evaluate('scrollTo(0,0)');page.wait_for_timeout(100);assert get()==final
   if W in [1512,390]:page.screenshot(path=str(out/f'{id}-{W}-opened.png'))
   checks.append({'scene':id,'viewport':[W,H],'dpr':2,'initial_inset':before,'settled_inset':final,'no_horizontal_overflow':True,'one_way_scroll':'passed'})
   page.close()
 page=browser.new_page();page.goto(args.url+'/');page.evaluate('localStorage.clear()');sequence=[]
 for i in range(count*3):
  page.goto(args.url+'/');page.wait_for_selector('.stage[data-ready=true]');sequence.append(page.locator('.stage').get_attribute('data-scene'))
 assert all(a!=b for a,b in zip(sequence,sequence[1:]))
 assert all(len(set(sequence[i:i+count]))==count for i in range(0,count*3,count))
 assert not set(sequence)&inactive
 page.close()
 for id in ids:
  page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
  page.goto(f'{args.url}/?study={id}');page.wait_for_selector('.stage[data-ready=true]');assert page.locator('#top').evaluate("e=>e.classList.contains('opened')");page.close()
 page=browser.new_page();page.goto(args.url+'/studies/');assert page.locator('main article').count()==count;page.close();browser.close()
assert not errors,errors
result={'layouts':checks,'opening_sequence':sequence,'reduced_motion':'passed','comparison_scene_count':count,'browser_errors':errors}
(args.report or repo/'studies/qa/editorial-browser-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(f'Passed {len(checks)} responsive layouts, {count*3} shuffled visits, reduced motion and scene comparison.')
