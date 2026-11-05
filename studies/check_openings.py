from pathlib import Path
from playwright.sync_api import sync_playwright
import json,argparse
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8732');parser.add_argument('--screenshots',type=Path,default=Path('/tmp/loganchal-opening-qa'));args=parser.parse_args()
repo=Path(__file__).resolve().parent.parent;out=args.screenshots;out.mkdir(parents=True,exist_ok=True)
ids=['prism-eclipse','porcelain-earth','woven-earth','night-gradient'];checks=[];errors=[]
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
 for i in range(18):
  page.goto(args.url+'/');page.wait_for_selector('.stage[data-ready=true]');sequence.append(page.locator('.stage').get_attribute('data-scene'))
 assert all(a!=b for a,b in zip(sequence,sequence[1:]))
 assert all(len(set(sequence[i:i+6]))==6 for i in (0,6,12))
 assert not set(sequence)&{'eclipse-arc','common-arc','earth-glaze'}
 page.close()
 for id in ids:
  page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
  page.goto(f'{args.url}/?study={id}');page.wait_for_selector('.stage[data-ready=true]');assert page.locator('#top').evaluate("e=>e.classList.contains('opened')");page.close()
 page=browser.new_page();page.goto(args.url+'/studies/');assert page.locator('main article').count()==6;page.close();browser.close()
assert not errors,errors
result={'layouts':checks,'opening_sequence':sequence,'reduced_motion':'passed','comparison_scene_count':6,'browser_errors':errors}
(repo/'studies/qa/editorial-browser-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(f'Passed {len(checks)} responsive layouts, 18 shuffled visits, reduced motion and scene comparison.')
