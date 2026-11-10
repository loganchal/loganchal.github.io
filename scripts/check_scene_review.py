#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import json,argparse,tempfile
from pathlib import Path
parser=argparse.ArgumentParser(description='Browser regression checks for scene review; requires Playwright and Chrome.')
parser.add_argument('--base-url',default='http://127.0.0.1:8742')
parser.add_argument('--output',type=Path,default=None)
args=parser.parse_args();URL=args.base_url.rstrip('/');output=args.output or Path(tempfile.mkdtemp(prefix='scene-review-check-'));output.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome');context=b.new_context(viewport={'width':1440,'height':1000},accept_downloads=True);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL+'/scene-review/');page.wait_for_selector('#card.ready');first=page.locator('#scene-id').inner_text();assert page.locator('#preview').content_frame.locator('.scene-controls').evaluate('(e)=>getComputedStyle(e).display')=='none'
 assert page.locator('#preview').content_frame.locator('.stage').get_attribute('data-scene')==first
 page.locator('#keep').click();page.wait_for_timeout(250);page.wait_for_selector('#card.ready');second=page.locator('#scene-id').inner_text();assert second!=first
 data=page.evaluate("JSON.parse(localStorage.getItem('opening-scene-review-v1'))");assert data['decisions'][first]['vote']=='keep'
 page.keyboard.press('ArrowLeft');page.wait_for_timeout(250);page.wait_for_selector('#card.ready');assert '1 kept' in page.locator('#counts').inner_text() and '1 rejected' in page.locator('#counts').inner_text()
 page.locator('#undo').click();page.wait_for_selector('#card.ready');assert page.locator('#scene-id').inner_text()==second;assert '0 rejected' in page.locator('#counts').inner_text()
 # A real horizontal gesture votes, without requiring interaction in the iframe.
 box=page.locator('#card').bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
 page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-180,y+10,steps=8);page.mouse.up();page.wait_for_timeout(250);page.wait_for_selector('#card.ready');assert '1 rejected' in page.locator('#counts').inner_text()
 page.locator('#filter').select_option('keep');page.wait_for_selector('#card.ready');assert page.locator('#scene-id').inner_text()==first
 page.locator('[data-frame="expanded"]').click();page.wait_for_timeout(150);expanded=page.locator('#preview').content_frame.locator('.stage').evaluate('(e)=>e.style.getPropertyValue("--inset")')
 page.locator('[data-frame="opening"]').click();opening=page.locator('#preview').content_frame.locator('.stage').evaluate('(e)=>e.style.getPropertyValue("--inset")');assert expanded!=opening,(expanded,opening)
 with page.expect_download() as info:page.locator('#export').click()
 download=info.value;download.save_as(str(output/'export.json'));export=json.load(open(str(output/'export.json')));assert len(export['decisions'])==2
 page.reload();page.wait_for_selector('#card.ready');assert '1 kept' in page.locator('#counts').inner_text()
 page.locator('#import-file').set_input_files(str(output/'export.json'));page.wait_for_selector('#card.ready');assert 'Imported 2' in page.locator('#save-status').inner_text()
 page.get_by_role('button',name='Te Reo Māori',exact=True).click();page.wait_for_function("document.documentElement.lang==='mi'");assert page.locator('#keep').inner_text()=='Tiaki ✓'
 page.get_by_role('button',name='EN',exact=True).click();page.wait_for_timeout(100);page.screenshot(path=str(output/'desktop.png'))
 page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.locator('[data-screen="phone"]').click();page.wait_for_timeout(300);assert page.locator('#card').get_attribute('class').find('phone')>=0;page.screenshot(path=str(output/'mobile.png'))
 page.goto(URL+'/');page.wait_for_function("document.querySelector('.stage').dataset.ready==='true'");assert page.locator('.angle-controls,.angle-step,.scene-angle-value').count()==0;assert page.locator('.scene-switch').count()==1
 assert not errors,errors
 print(json.dumps({'keep':first,'reject':second,'swipe':True,'undo':True,'persistence':True,'import_export':True,'frame_modes':[opening,expanded],'responsive':True,'errors':errors}));b.close()
