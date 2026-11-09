"""Verify the fifteen-option comparison and complete entrance on desktop and phone."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8735'
out=Path('/tmp/fifteen-options-browser');out.mkdir(exist_ok=True);ids=[s['id']for s in json.loads(Path(__file__).with_name('scenes.json').read_text())if s.get('review_batch')=='fifteen-20261109'];rows=[];errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome')
 for W,H,profile in [(1512,982,'wide'),(390,844,'portrait')]:
  for id in ids:
   c=b.new_context(viewport={'width':W,'height':H},device_scale_factor=2)
   q=c.new_page();q.on('pageerror',lambda e:errors.append(str(e)))
   q.goto(base+'/options/view.html?study='+id);q.wait_for_selector('.stage[data-ready=true]');q.evaluate('document.fonts.ready');q.wait_for_timeout(60)
   assert q.evaluate('scene.id')==id
   assert q.evaluate('openingScenes.length')==15
   assert q.locator('.arc-study > i').count()==3
   assert not q.evaluate('document.documentElement.scrollWidth>innerWidth')
   assert q.evaluate('''()=>{const stage=document.querySelector('.stage'),art=stage.querySelector('.arc-study').getBoundingClientRect(),t=stage.querySelector('.cover-title text').getBoundingClientRect();const span=(1-2*parseFloat(stage.style.getPropertyValue('--opening-inset'))/100)*art.width;return t.left>=innerWidth/2-span/2-2&&t.right<=innerWidth/2+span/2+2}'''),(id,profile,'title spills outside central window')
   assert q.evaluate('new DOMMatrix(getComputedStyle(document.querySelector(".arc-study")).transform).b===0')
   q.screenshot(scale="css",animations="disabled",path=str(out/f'{id}-{profile}-opening.png'))
   runway=q.evaluate('document.querySelector("#top").offsetHeight-innerHeight');q.evaluate('(r)=>scrollTo(0,r)',runway);q.wait_for_selector('#top.opened');q.evaluate('scrollTo(0,0)');q.wait_for_timeout(80)
   assert q.evaluate('document.querySelector("#top").offsetHeight===innerHeight')
   q.screenshot(scale="css",animations="disabled",path=str(out/f'{id}-{profile}-settled.png'))
   rows.append({'scene':id,'profile':profile,'ready':True,'three_layers':True,'one_way_scroll':True,'no_horizontal_overflow':True})
   print(id,profile,flush=True)
   c.close()
 c=b.new_context(viewport={'width':1512,'height':982},device_scale_factor=2);q=c.new_page();q.on('pageerror',lambda e:errors.append(str(e)));q.goto(base+'/options/');q.wait_for_function('cards.length===15');q.wait_for_timeout(600)
 assert q.locator('article').count()==15
 q.locator('#portrait').click();q.wait_for_function('cards.filter(c=>c.seen).every(c=>c.frame.classList.contains("portrait"))');q.locator('#framing').click();q.wait_for_timeout(200)
 q.locator('#wide').click();q.wait_for_function('cards.filter(c=>c.seen).every(c=>!c.frame.classList.contains("portrait"))')
 q.screenshot(scale="css",animations="disabled",path=str(out/'gallery.png'));assert not q.evaluate('document.documentElement.scrollWidth>innerWidth')
 # The approved homepage rotation stays unchanged; review options are isolated.
 q.goto(base+'/');q.wait_for_selector('.stage[data-ready=true]');assert q.evaluate('openings.length')==47
 c.close();b.close()
assert not errors,errors
Path(__file__).with_name('qa').joinpath('fifteen-options-browser-checks.json').write_text(json.dumps({'options':15,'layouts':rows,'gallery_profiles':True,'gallery_framing':True,'existing_rotation':47,'page_errors':errors},indent=2)+'\n')
# Five review sheets, each showing actual browser desktop and phone renders.
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
for start in range(0,15,3):
 sheet=Image.new('RGB',(1190,3*590),'#eeeade');d=ImageDraw.Draw(sheet)
 for row,id in enumerate(ids[start:start+3]):
  a=Image.open(out/f'{id}-wide-settled.png');a.thumbnail((870,550));sheet.paste(a,(0,row*590+25))
  a=Image.open(out/f'{id}-portrait-settled.png');a.thumbnail((260,550));sheet.paste(a,(900,row*590+25));d.text((8,row*590),f'{start+row+1:02d}  {id}',font=font,fill='#242a26')
 sheet.save(out/f'review-{start//3+1}.jpg',quality=94)
print('PASS15options30layouts, gallery controls, original47-scene rotation, zero page errors')
