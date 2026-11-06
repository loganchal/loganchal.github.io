"""Check bounded responsive image requests and atomic scene delivery in Chrome."""
import argparse
import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.async_api import async_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8732')
parser.add_argument('--screenshots', type=Path, default=Path('/tmp/scene-compose-2026-11-06/tests/delivery'))
args = parser.parse_args()
args.screenshots.mkdir(parents=True, exist_ok=True)
repo = Path(__file__).resolve().parent.parent
ASSETS = '**/studies/scene-assets/**'

async def snapshot(page):
    return await page.locator('.stage .arc-study').evaluate('''e=>({
      key:e.dataset.assetKey,profile:e.dataset.assetProfile,
      layers:[...e.children].map(layer=>layer.style.backgroundImage)
    })''')

async def settled(page):
    await page.wait_for_function('document.querySelector(".stage").dataset.ready==="true" && !document.querySelector(".scene-controls").hasAttribute("aria-busy")')

async def run():
    errors, profiles = [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome')
        # A cold page must request exactly the three visible layers, at the
        # smallest adequate delivery level, without fetching the other profile.
        for width, height, dpr, profile, density in [
            (1512, 982, 2, 'wide', 2),
            (390, 844, 2, 'portrait', 1.5),
            (390, 844, 3, 'portrait', 2),
            (844, 390, 1, 'wide', 1),
        ]:
            context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=dpr)
            page = await context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            requested = []
            page.on('request', lambda request: requested.append(request.url) if '/studies/scene-assets/' in request.url else None)
            await page.goto(args.url + '/?study=lion-dawn')
            await settled(page)
            await page.wait_for_timeout(250)
            choice = await page.evaluate('OpeningAssets.pick(scene)')
            expected = {args.url + '/' + url for url in choice['urls']}
            assert len(requested) == 3 and set(requested) == expected, requested
            assert choice['profile'] == profile and choice['density'] == density, choice
            assert all('/lion-dawn/' in url and f'-{profile}-' in url for url in requested), requested
            state = await snapshot(page)
            assert len(state['layers']) == 3 and all(f'-{profile}-' in layer for layer in state['layers']), state
            await page.screenshot(path=str(args.screenshots / f'{profile}-{width}-{dpr}x.png'))
            profiles.append({'viewport': [width, height], 'dpr': dpr, 'profile': profile, 'density': density, 'delivery_requests': len(requested)})
            await context.close()

        # A resize is a complete frame transaction: keep the wide frame while
        # portrait loading is pending or failed, then replace all three layers.
        context = await browser.new_context(viewport={'width': 1512, 'height': 982}, device_scale_factor=2)
        page = await context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        await page.goto(args.url + '/?study=lion-dawn')
        await settled(page)
        original = await snapshot(page)
        failed = []
        async def fail_portrait(route):
            failed.append(route.request.url)
            await route.abort()
        await page.route(ASSETS, fail_portrait)
        await page.set_viewport_size({'width': 390, 'height': 844})
        await page.wait_for_function('document.querySelector("#scene-status").textContent.includes("could not load")')
        await settled(page)
        assert len(failed) == 3 and all('-portrait-' in url for url in failed), failed
        assert await snapshot(page) == original
        assert await page.locator('.stage').get_attribute('data-scene') == 'lion-dawn'
        await page.screenshot(path=str(args.screenshots / 'resize-failure-keeps-wide.png'))
        await page.unroute(ASSETS)
        release = asyncio.Event()
        pending = []
        async def hold_portrait(route):
            pending.append(route.request.url)
            await release.wait()
            await route.continue_()
        await page.route(ASSETS, hold_portrait)
        await page.evaluate('''() => {
          window.deliveryFrames=[];
          new MutationObserver(()=>deliveryFrames.push([...document.querySelector('.arc-study').children].map(e=>e.style.backgroundImage)))
            .observe(document.querySelector('.arc-study'),{attributes:true,subtree:true,attributeFilter:['style']});
          dispatchEvent(new Event('resize'));
        }''')
        for _ in range(100):
            if len(pending) == 3:
                break
            await page.wait_for_timeout(25)
        assert len(pending) == 3 and all('-portrait-' in url for url in pending), pending
        assert await snapshot(page) == original
        assert await page.locator('.scene-controls').get_attribute('aria-busy') == 'true'
        await page.screenshot(path=str(args.screenshots / 'resize-pending-keeps-wide.png'))
        release.set()
        await page.wait_for_function('document.querySelector(".arc-study").dataset.assetProfile==="portrait"')
        await settled(page)
        final = await snapshot(page)
        assert final['key'] != original['key'] and all('-portrait-' in layer for layer in final['layers'])
        frames = await page.evaluate('deliveryFrames')
        assert frames and all(all('-wide-' in layer for layer in frame) or all('-portrait-' in layer for layer in frame) for frame in frames), frames
        await page.screenshot(path=str(args.screenshots / 'resize-complete-portrait.png'))
        await context.close()

        # The gallery loads only near-visible thumbnails. Jumping to its last
        # card must load that card without downloading the full intervening deck.
        context = await browser.new_context(viewport={'width': 1512, 'height': 982}, device_scale_factor=2)
        page = await context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        gallery_requests = []
        page.on('request', lambda request: gallery_requests.append(request.url) if '/studies/scene-assets/' in request.url else None)
        await page.goto(args.url + '/studies/')
        await page.wait_for_function('document.querySelector(".frame .arc-study[data-asset-key]")')
        await page.wait_for_timeout(300)
        total = await page.locator('.frame').count()
        initial_ids = {urlparse(url).path.split('/')[-2] for url in gallery_requests}
        near_ids = await page.locator('.frame').evaluate_all('(frames)=>frames.filter(e=>e.getBoundingClientRect().top<=innerHeight+200).map(e=>e.dataset.scene)')
        assert initial_ids and initial_ids.issubset(set(near_ids)), (initial_ids, near_ids)
        assert len(initial_ids) < total and len(gallery_requests) == len(initial_ids) * 3
        assert all('-wide-' in url for url in gallery_requests)
        last = page.locator('.frame').last
        last_id = await last.get_attribute('data-scene')
        assert last_id not in initial_ids
        await last.scroll_into_view_if_needed()
        await page.wait_for_function('(id)=>document.querySelector(`.frame[data-scene="${id}"] .arc-study`).hasAttribute("data-asset-key")', arg=last_id)
        await page.wait_for_timeout(200)
        loaded_ids = {urlparse(url).path.split('/')[-2] for url in gallery_requests}
        assert last_id in loaded_ids and len(loaded_ids) < total
        assert len(gallery_requests) == len(loaded_ids) * 3
        await page.screenshot(path=str(args.screenshots / 'gallery-last-card.png'))
        gallery = {'scene_count': total, 'initial_loaded_cards': len(initial_ids), 'loaded_after_jump': len(loaded_ids), 'requests_per_card': 3}
        await context.close()
        await browser.close()
    assert not errors, errors
    report = {'cold_opening_profiles': profiles, 'failed_resize_keeps_complete_old_frame': True, 'pending_resize_keeps_complete_old_frame': True, 'resize_profile_applied_atomically': True, 'gallery_lazy': gallery, 'browser_errors': errors}
    (repo / 'studies/qa/scene-delivery-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

asyncio.run(run())
