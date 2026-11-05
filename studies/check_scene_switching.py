"""Check scene cycling, direct links, scroll continuity and loading failures."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse,json
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8732');parser.add_argument('--screenshots',type=Path,default=Path('/tmp/loganchal-scene-controls'));args=parser.parse_args()
repo=Path(__file__).resolve().parent.parent;text=(repo/'studies/catalogue.js').read_text();catalogue=json.loads(text[text.index('['):text.rindex(']')+1]);active=[s['id'] for s in catalogue if s.get('active',True)];count=len(active)
args.screenshots.mkdir(parents=True,exist_ok=True);results=[];errors=[]
def current(page):return page.locator('.stage').get_attribute('data-scene')
def change(page,keyboard=False):
 before=current(page);button=page.locator('.scene-switch')
 if keyboard:button.focus();button.press('Enter')
 else:button.click()
 page.wait_for_function('old=>document.querySelector(".stage").dataset.scene!==old',arg=before)
 page.wait_for_function('!document.querySelector(".scene-switch").disabled')
 assert current(page) in active
 assert not page.locator('.scene-switch').get_attribute('aria-busy')
 assert str(count) in page.locator('.scene-count').inner_text()
 return current(page)
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome')
 for W,H in [(1512,982),(390,844),(320,740),(844,390)]:
  context=browser.new_context(viewport={'width':W,'height':H},device_scale_factor=2);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(args.url+'/?study=lion-dawn&review=controls#top');page.wait_for_selector('.stage[data-ready=true]')
  assert current(page)=='lion-dawn'
  assert page.evaluate('!new URL(location.href).searchParams.has("study")')
  assert page.evaluate('new URL(location.href).searchParams.get("review")==="controls" && location.hash==="#top"')
  button=page.locator('.scene-switch');assert button.is_visible() and button.is_enabled()
  logo=page.locator('header a').bounding_box();box=button.bounding_box()
  assert box['height']>=44
  assert box['x']>=logo['x']+logo['width'] or box['y']>=logo['y']+logo['height'],(W,logo,box)
  assert page.evaluate('document.documentElement.scrollWidth===innerWidth')
  change(page,keyboard=True)
  # A mid-introduction change must preserve the consumed scroll and progress.
  runway=page.evaluate('document.querySelector("#top").offsetHeight-innerHeight');page.evaluate('(n)=>scrollTo(0,n*.5)',runway);page.wait_for_function('parseFloat(getComputedStyle(document.querySelector(".stage")).getPropertyValue("--show"))>=0')
  page.wait_for_timeout(100);progress=page.evaluate('openingProgress');scroll=page.evaluate('scrollY');change(page)
  assert abs(page.evaluate('scrollY')-scroll)<1
  assert page.evaluate('openingProgress')>=progress
  assert not page.locator('#top').evaluate('e=>e.classList.contains("opened")')
  page.evaluate('scrollTo(0,0)');page.wait_for_timeout(100);assert page.evaluate('openingProgress')>=progress
  # Finish once; changing the image must not recreate the captive runway.
  page.evaluate('(n)=>scrollTo(0,n)',runway);page.wait_for_function('document.querySelector("#top").classList.contains("opened")');page.evaluate('scrollTo(0,0)');change(page)
  assert page.locator('#top').evaluate('e=>e.classList.contains("opened")')
  assert page.evaluate('document.querySelector("#top").offsetHeight')==H
  assert abs(page.evaluate('scrollY'))<1
  page.screenshot(path=str(args.screenshots/f'controls-{W}.png'))
  shown=current(page);page.reload();page.wait_for_selector('.stage[data-ready=true]');assert current(page)!=shown
  results.append({'viewport':[W,H],'button_and_logo_do_not_overlap':True,'keyboard':'passed','partial_and_completed_scroll_preserved':True,'review_link_released':True,'refresh_advanced':True});context.close()
 # Exhaust two complete decks through the button, without repeating within either.
 context=browser.new_context();page=context.new_page();page.goto(args.url+'/?study=lion-dawn');page.wait_for_selector('.stage[data-ready=true]');sequence=[current(page)]
 for i in range(count*2-1):sequence.append(change(page))
 assert all(len(set(sequence[i:i+count]))==count for i in range(0,count*2,count)),sequence
 assert all(a!=b for a,b in zip(sequence,sequence[1:]))
 context.close()
 # Disabled browser storage must still permit a complete in-page shuffled deck.
 context=browser.new_context(reduced_motion='reduce');context.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage unavailable')}})");page=context.new_page();page.goto(args.url+'/');page.wait_for_selector('.stage[data-ready=true]');assert page.locator('#top').evaluate('e=>e.classList.contains("opened")');no_storage=[current(page)]
 for i in range(count-1):no_storage.append(change(page))
 assert len(set(no_storage))==count
 context.close()
 # A failed destination keeps the current complete scene and restores the button.
 context=browser.new_context();page=context.new_page();page.goto(args.url+'/');page.wait_for_selector('.stage[data-ready=true]');before=current(page);page.route('**/studies/scenes/**',lambda route:route.abort());page.locator('.scene-switch').click();page.wait_for_function('document.querySelector("#scene-status").textContent.includes("could not load")');assert current(page)==before;assert page.locator('.scene-switch').is_enabled();context.close();browser.close()
# Initial-load recovery: a broken requested scene advances to a complete alternative.
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome');page=browser.new_page()
 page.route('**/studies/scenes/lion-dawn/**',lambda route:route.abort())
 page.goto(args.url+'/?study=lion-dawn');page.wait_for_selector('.stage[data-ready=true]')
 assert current(page)!='lion-dawn' and page.locator('.scene-switch').is_enabled()
 browser.close()
assert not errors,errors
report={'active_scene_count':count,'responsive_controls':results,'two_button_decks':sequence,'storage_blocked_deck':no_storage,'load_failure_preserves_current_scene':True,'initial_load_recovers_to_another_scene':True,'browser_errors':errors}
(repo/'studies/qa/scene-switching-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(f'Passed responsive controls, preserved scroll, refresh, {count*2} manual frames, storage failure and image-load failure.')
