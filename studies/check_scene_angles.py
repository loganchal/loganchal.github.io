"""Click distinct scene angles without rotating photographs or replaying the intro."""
import asyncio,json,argparse
from pathlib import Path
from playwright.async_api import async_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8732');parser.add_argument('--screenshots',type=Path,default=Path('/tmp/scene-compose-2026-11-06/tests/angles'));args=parser.parse_args();out=args.screenshots;out.mkdir(parents=True,exist_ok=True)
async def run():
 results=[];errors=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(channel='chrome')
  async def click(page,direction=1):
   old=await page.evaluate('scene.angle');expected=await page.evaluate('(d)=>sceneAngles[(sceneAngles.indexOf(scene.angle)+d+sceneAngles.length)%sceneAngles.length]',direction)
   await page.locator('.angle-next' if direction==1 else '.angle-previous').click()
   await page.wait_for_function('(a)=>scene.angle===a && !document.querySelector(".scene-controls").hasAttribute("aria-busy")',arg=expected)
   assert expected!=old
   assert await page.evaluate('new DOMMatrix(getComputedStyle(document.querySelector(".arc-study")).transform).b===0')
   return expected
  for W,H,dpr in [(1512,982,2),(390,844,2),(320,740,2),(844,390,1)]:
   context=await browser.new_context(viewport={'width':W,'height':H},device_scale_factor=dpr);page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   await page.goto(args.url+'/?study=apollo-earth');await page.wait_for_selector('.stage[data-ready=true]')
   assert await page.locator('input[type=range]').count()==0
   await page.locator('.angle-next').focus();await page.keyboard.press('Enter');await page.wait_for_function('scene.angle!==0 && !document.querySelector(".scene-controls").hasAttribute("aria-busy")')
   path=await page.locator('#title-arc').get_attribute('d');await click(page,-1);assert await page.locator('#title-arc').get_attribute('d')!=path
   runway=await page.evaluate('document.querySelector("#top").offsetHeight-innerHeight');await page.evaluate('(n)=>scrollTo(0,n*.5)',runway);await page.wait_for_timeout(100)
   progress=await page.evaluate('openingProgress');scroll=await page.evaluate('scrollY');await click(page)
   assert await page.evaluate('openingProgress')>=progress and abs(await page.evaluate('scrollY')-scroll)<1
   await page.evaluate('(n)=>scrollTo(0,n)',runway);await page.wait_for_function('document.querySelector("#top").classList.contains("opened")');await page.evaluate('scrollTo(0,0)');await click(page,-1)
   assert await page.evaluate('document.querySelector("#top").offsetHeight===innerHeight && scrollY===0')
   logo=await page.locator('header a').bounding_box();controls=await page.locator('.scene-controls').bounding_box();assert controls['x']>=logo['x']+logo['width'] or controls['y']>=logo['y']+logo['height']
   assert await page.evaluate('document.documentElement.scrollWidth===innerWidth')
   for button in ['.angle-previous','.angle-next']:
    box=await page.locator(button).bounding_box();assert box['width']>=44 and box['height']>=44
   await page.screenshot(path=str(out/f'clicks-{W}.png'));results.append({'viewport':[W,H],'dpr':dpr,'distinct_angle_on_each_click':True,'keyboard':True,'one_way_scroll_preserved':True,'tap_targets':True});await context.close()
  context=await browser.new_context();page=await context.new_page();await page.goto(args.url+'/?study=apollo-earth');await page.wait_for_selector('.stage[data-ready=true]')
  for _ in range(await page.evaluate('sceneAngles.length')):await click(page)
  assert await page.evaluate('scene.angle===0')
  await context.close()
  context=await browser.new_context();page=await context.new_page();await page.goto(args.url+'/?study=apollo-earth');await page.wait_for_selector('.stage[data-ready=true]')
  delayed=[]
  async def delay(route):
   delayed.append(route.request.url);await asyncio.sleep(.9)
   try:await route.continue_()
   except Exception:pass # Aborting an obsolete image can cancel its pending route.
  await page.route('**/studies/scene-assets/**',delay)
  old_frame=await page.locator('.arc-study').evaluate('(e)=>[e.dataset.assetKey,...[...e.children].map(layer=>layer.style.backgroundImage)]')
  await page.locator('.angle-next').click();await page.locator('.angle-next').click();expected=await page.evaluate('requestedAngle')
  assert await page.locator('.scene-controls').get_attribute('aria-busy')=='true'
  assert await page.locator('.arc-study').evaluate('(e)=>[e.dataset.assetKey,...[...e.children].map(layer=>layer.style.backgroundImage)]')==old_frame
  await page.wait_for_function('(a)=>scene.angle===a && !document.querySelector(".scene-controls").hasAttribute("aria-busy")',arg=expected);await page.wait_for_timeout(1200);assert await page.evaluate('scene.angle')==expected
  assert len(delayed)>=3,delayed
  count=await page.evaluate('sceneOrder.length');await context.close();await browser.close()
 assert not errors,errors
 Path(__file__).resolve().parent.joinpath('qa/scene-angle-checks.json').write_text(json.dumps({'scene_count':count,'controls':results,'full_angle_cycle':True,'late_load_cannot_override_latest_click':True,'rapid_click_keeps_complete_old_frame':True,'browser_errors':errors},indent=2)+'\n');print('Passed click angles, keyboard, responsive controls, one-way scroll, angle wrap and latest-choice loading.')
asyncio.run(run())
