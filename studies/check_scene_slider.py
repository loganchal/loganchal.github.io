"""Check that the angle slider selects whole scenes and ignores stale image decodes."""
import asyncio,json,argparse
from pathlib import Path
from playwright.async_api import async_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8732');args=parser.parse_args();out=Path('/tmp/loganchal-scene-slider');out.mkdir(exist_ok=True)
async def run():
 results=[];errors=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(channel='chrome')
  async def ready(page):await page.wait_for_selector('.stage[data-ready=true]')
  async def choose(page,index):
   expected=await page.evaluate('(i)=>sceneOrder[i].id',index)
   await page.locator('#scene-angle').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}));}',str(index))
   await page.wait_for_function('(id)=>document.querySelector(".stage").dataset.scene===id && !document.querySelector(".scene-switch").disabled',arg=expected)
   assert await page.locator('#scene-angle').get_attribute('aria-busy') is None
   assert await page.evaluate('new DOMMatrix(getComputedStyle(document.querySelector(".arc-study")).transform).b===0')
   return expected
  for W,H,dpr in [(1512,982,2),(390,844,2),(320,740,2),(844,390,1)]:
   context=await browser.new_context(viewport={'width':W,'height':H},device_scale_factor=dpr);page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   await page.goto(args.url+'/?study=station-aurora');await ready(page)
   n=await page.evaluate('sceneOrder.length');angles=await page.evaluate('sceneOrder.map(s=>s.angle)');assert angles==sorted(angles)
   slider=page.locator('#scene-angle');assert await slider.is_enabled()
   await slider.press('Home');first=await page.evaluate('sceneOrder[0].id');await page.wait_for_function('(id)=>document.querySelector(".stage").dataset.scene===id',arg=first)
   initial_path=await page.locator('#title-arc').get_attribute('d')
   await slider.press('End');last=await page.evaluate('sceneOrder[sceneOrder.length-1].id');await page.wait_for_function('(id)=>document.querySelector(".stage").dataset.scene===id',arg=last)
   assert await page.locator('#title-arc').get_attribute('d')!=initial_path
   runway=await page.evaluate('document.querySelector("#top").offsetHeight-innerHeight');await page.evaluate('(n)=>scrollTo(0,n*.5)',runway);await page.wait_for_timeout(80)
   before=await page.evaluate('openingProgress');scroll=await page.evaluate('scrollY');await choose(page,0)
   assert abs(await page.evaluate('scrollY')-scroll)<1 and await page.evaluate('openingProgress')>=before
   await page.evaluate('(n)=>scrollTo(0,n)',runway);await page.wait_for_function('document.querySelector("#top").classList.contains("opened")');await page.evaluate('scrollTo(0,0)');await choose(page,n-1)
   assert await page.evaluate('document.querySelector("#top").offsetHeight===innerHeight && scrollY===0')
   logo=await page.locator('header a').bounding_box();control=await page.locator('.scene-controls').bounding_box();assert control['x']>=logo['x']+logo['width'] or control['y']>=logo['y']+logo['height']
   assert await page.evaluate('document.documentElement.scrollWidth===innerWidth')
   await page.screenshot(path=str(out/f'slider-{W}.png'));results.append({'viewport':[W,H],'dpr':dpr,'sorted_angles':True,'keyboard':True,'whole_scene_selection':True,'one_way_scroll_preserved':True,'controls_clear_header':True});await context.close()
  context=await browser.new_context();page=await context.new_page();await page.goto(args.url+'/?study=station-aurora');await ready(page)
  slow=await page.evaluate('sceneOrder[0].id');last=await page.evaluate('sceneOrder[sceneOrder.length-1].id');n=await page.evaluate('sceneOrder.length')
  async def delay(route):await asyncio.sleep(.8);await route.continue_()
  await page.route('**/studies/scenes/'+slow+'/**',delay)
  await page.locator('#scene-angle').evaluate('(e)=>{e.value=0;e.dispatchEvent(new Event("change",{bubbles:true}));}')
  await choose(page,n-1);await page.wait_for_timeout(1200);assert await page.locator('.stage').get_attribute('data-scene')==last
  await context.close();await browser.close()
 assert not errors,errors
 receipt={'scene_count':n,'controls':results,'late_decode_cannot_replace_latest_choice':True,'browser_errors':errors}
 Path(__file__).resolve().parent.joinpath('qa/scene-slider-checks.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Passed slider keyboard, geometry selection, responsive controls, one-way scroll and latest-choice loading.')
asyncio.run(run())
