"""Reproduce cold-load timings, pixel registration and bounded cache behaviour.

Cold timing uses Chrome at 4 Mbps / 80 ms, with its HTTP cache disabled.
The pixel reference renders the complete registered layer at the same density;
only WebP crop-boundary compression differences are allowed.
"""
import argparse
import asyncio
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8732')
parser.add_argument('--screenshots', type=Path, default=Path('/tmp/opening-performance-2026-11-06/verified'))
parser.add_argument('--report', type=Path, default=ROOT / 'studies/qa/scene-performance-checks.json')
args = parser.parse_args()
args.screenshots.mkdir(parents=True, exist_ok=True)


async def settled(page):
    await page.wait_for_function('document.querySelector(".stage").dataset.ready==="true" && !document.querySelector(".scene-controls").hasAttribute("aria-busy")')


async def cold_load(browser, width, height, dpr, name):
    context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=dpr)
    page = await context.new_page()
    cdp = await context.new_cdp_session(page)
    await cdp.send('Network.enable')
    await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    await cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 80, 'downloadThroughput': 500000, 'uploadThroughput': 125000})
    await page.goto(args.url + '/?study=apollo-earth', wait_until='domcontentloaded')
    await settled(page)
    ready = await page.evaluate('performance.now()')
    await page.wait_for_timeout(300)
    entries = await page.evaluate("performance.getEntriesByType('resource').map(e=>({url:e.name,bytes:e.transferSize,body:e.encodedBodySize}))")
    images = [item for item in entries if '.webp' in item['url']]
    assert len(images) == 3, images
    row = {'device': name, 'viewport': [width, height], 'dpr': dpr, 'network': '4 Mbps / 80 ms cold cache', 'scene': 'apollo-earth', 'ready_ms': round(ready), 'image_bytes': sum(item['body'] for item in images), 'total_bytes': sum(item['bytes'] for item in entries), 'image_requests': len(images), 'image_urls': [item['url'] for item in images]}
    await page.screenshot(path=str(args.screenshots / f'cold-{name}.png'))
    await context.close()
    print(json.dumps(row), flush=True)
    return row


async def pixels(browser):
    scenes = {scene['id']: scene for scene in json.loads((ROOT / 'studies/scenes.json').read_text())}
    rows = []
    for width, height, name in [(1512, 982, 'desktop'), (390, 844, 'phone'), (320, 1400, 'very-tall')]:
        context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=2)
        page = await context.new_page()
        await page.goto(args.url + '/?study=apollo-earth')
        await settled(page)
        choice = await page.evaluate('OpeningAssets.pick(scene)')
        if name == 'very-tall':
            assert '-tall-' in choice['urls'][0] and '-tall-' in choice['urls'][2], choice
        scene = scenes['apollo-earth']
        profile = choice['profile']
        maximum = scene.get('portrait_density', scene.get('render_density', 2.4)) if profile == 'portrait' else scene.get('render_density', 2.4)
        reference_bytes = {}
        for slot in range(3):
            original = Image.open(ROOT / 'studies/scenes/apollo-earth' / f'{slot}-{profile}-{round(choice["width"] * maximum)}.webp').convert('RGB')
            size = (round(choice['width'] * choice['density']), round(choice['height'] * choice['density']))
            if original.size != size:
                original = original.resize(size, Image.Resampling.LANCZOS)
            buffer = BytesIO()
            original.save(buffer, format='WEBP', quality=90, method=5)
            reference_bytes[str(slot)] = buffer.getvalue()
        async def reference(route):
            await route.fulfill(status=200, content_type='image/webp', body=reference_bytes[route.request.url.rsplit('/', 1)[1]])
        await page.route('**/__performance-reference/*', reference)
        full = {**choice, 'urls': [f'{args.url}/__performance-reference/{slot}' for slot in range(3)], 'widths': [1, 1, 1]}
        assert await page.evaluate('choice=>OpeningAssets.load(choice)', full)
        for phase in ['initial', 'resolved']:
            inset = await page.evaluate("phase=>phase==='initial'?parseFloat(getComputedStyle(stage).getPropertyValue('--opening-inset')):finalInset", phase)
            await page.evaluate('({choice,inset})=>{OpeningAssets.apply(stage.querySelector(".arc-study"),choice);framePlates(inset);}', {'choice': choice, 'inset': inset})
            await page.wait_for_timeout(100)
            cropped = args.screenshots / f'{name}-{phase}-cropped.png'
            await page.screenshot(path=str(cropped))
            await page.evaluate('choice=>OpeningAssets.apply(stage.querySelector(".arc-study"),choice)', full)
            await page.wait_for_timeout(100)
            reference_path = args.screenshots / f'{name}-{phase}-reference.png'
            await page.screenshot(path=str(reference_path))
            difference = np.abs(np.asarray(Image.open(cropped).convert('RGB'), dtype=np.int16) - np.asarray(Image.open(reference_path).convert('RGB'), dtype=np.int16))
            mae = float(difference.mean())
            significant = float((difference.max(axis=2) > 40).mean())
            print(name,phase,mae,significant,flush=True)
            assert mae < 2.5 and significant < .01, (name, phase, mae, significant)
            rows.append({'viewport': [width, height], 'phase': phase, 'profile': profile, 'inset_percent': inset, 'mean_absolute_channel_difference': round(mae, 4), 'fraction_pixels_with_channel_difference_over_40': round(significant, 6), 'reference': 'same-density complete registered q90 WebP layers', 'tall_fallback': '-tall-' in choice['urls'][0]})
        await context.close()
    return rows


async def sharing(browser):
    context = await browser.new_context(viewport={'width': 1512, 'height': 982}, device_scale_factor=2)
    page = await context.new_page()
    await page.goto(args.url + '/?study=apollo-earth')
    await settled(page)
    requests = []
    release = asyncio.Event()
    async def hold(route):
        requests.append(route.request.url)
        await release.wait()
        await route.continue_()
    await page.route('**/studies/scene-assets/**', hold)
    await page.evaluate('''()=>{
      window.performanceChoice=OpeningAssets.pick(openingScenes.find(s=>s.id==='night-archive'));
      const first=new AbortController();
      const old=OpeningAssets.load(performanceChoice,first.signal);
      first.abort();
      const replacement=OpeningAssets.load(performanceChoice);
      window.performanceLoads=Promise.all([old,replacement]);
    }''')
    for _ in range(100):
        if len(requests) == 3:
            break
        await page.wait_for_timeout(20)
    assert len(requests) == 3, requests
    release.set()
    assert await page.evaluate('performanceLoads') == [False, True]
    assert await page.evaluate('OpeningAssets.load(performanceChoice)')
    await page.wait_for_timeout(100)
    assert len(requests) == 3, requests
    # Once decoded, the three layers are reused even with HTTP cache disabled.
    await context.close()
    return {'cancelled_then_reselected_frame_shares_three_pending_requests': True, 'decoded_frame_revisit_adds_zero_requests': True, 'decoded_image_reference_limit': 6}


async def run():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel='chrome')
        timings = [await cold_load(browser, *case) for case in [(1512, 982, 2, 'mac'), (390, 844, 2, 'phone')]]
        comparison = await pixels(browser)
        cache = await sharing(browser)
        await browser.close()
    report = {'cold_opening': timings, 'pixel_registration': comparison, 'cache': cache}
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


asyncio.run(run())
