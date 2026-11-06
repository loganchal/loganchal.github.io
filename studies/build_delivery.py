"""Encode responsive, registered delivery crops without changing image geometry.

The centre can only reveal pixels between the final inset boundaries. Standard
side crops include every pixel exposed by the authored initial inset, plus a
2-pixel guard. Extremely tall portrait viewports use half-width side crops.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import math

from PIL import Image

BASE = Path(__file__).resolve().parent
ENCODER_VERSION = 'delivery-v2-q90'


def urls_exist(profile):
    for level in profile['levels']:
        variants = [level] + ([level['tall']] if 'tall' in level else [])
        for variant in variants:
            if not all((BASE.parent / url.split('?')[0]).is_file() for url in variant['urls']):
                return False
    return True


def build(scene, manifest):
    result = {}
    for profile, width, height in [('wide', 1600, 960), ('portrait', 768, 1280)]:
        maximum = scene.get('render_density', 2.4)
        if profile == 'portrait':
            maximum = scene.get('portrait_density', maximum)
        sources = [BASE / 'scenes' / scene['id'] / f'{slot}-{profile}-{round(width * maximum)}.webp' for slot in range(3)]
        settings = (scene['finalInset'], scene.get('openingInset', 26), scene.get('portrait_openingInset', 25))
        fingerprint = hashlib.sha256((ENCODER_VERSION + str(settings)).encode())
        for source in sources:
            fingerprint.update(source.read_bytes())
        stamp = fingerprint.hexdigest()[:12]
        prior = manifest.get(scene['id'], {}).get(profile)
        if prior and prior.get('stamp') == stamp and urls_exist(prior):
            result[profile] = prior
            continue
        densities = sorted(set([1, round(min(1.5, maximum), 4), round(maximum, 4)] + ([2] if maximum > 2.2 else [])))
        folder = BASE / 'scene-assets' / scene['id']
        folder.mkdir(parents=True, exist_ok=True)
        opened = [Image.open(source).convert('RGB') for source in sources]
        levels = []
        # Gallery cards use a 26% inset. Wide homepage viewports have aspect
        # ratio >1, so their responsive minimum inset cannot exceed 23.6%.
        coverage = max(scene['finalInset'], scene.get('portrait_openingInset', 25) if profile == 'portrait' else scene.get('openingInset', 26), 26 if profile == 'wide' else 0) / 100
        for density in densities:
            w, h = round(width * density), round(height * density)
            images = [original if original.size == (w, h) else original.resize((w, h), Image.Resampling.LANCZOS) for original in opened]
            edge = min((w + 1) // 2, math.ceil(w * coverage) + 2)
            inset = int(w * scene['finalInset'] / 100)
            boxes = [(0, 0, edge, h), (inset, 0, w - inset, h), (w - edge, 0, w, h)]

            def encode(slot, box, suffix=''):
                name = f'{slot}-{profile}{suffix}-{w}.webp'
                images[slot].crop(box).save(folder / name, format='WEBP', quality=90, method=5)
                return f'studies/scene-assets/{scene["id"]}/{name}?v={stamp}', (box[2] - box[0]) / w

            encoded = [encode(slot, box) for slot, box in enumerate(boxes)]
            level = {'density': density, 'urls': [item[0] for item in encoded], 'widths': [item[1] for item in encoded]}
            if profile == 'portrait':
                tall = list(encoded)
                for slot, box in [(0, (0, 0, (w + 1) // 2, h)), (2, (w // 2, 0, w, h))]:
                    tall[slot] = encode(slot, box, '-tall')
                # The centre URL is shared: switching crop variants only needs
                # two side images if that centre is already decoded.
                level['tall'] = {'urls': [item[0] for item in tall], 'widths': [item[1] for item in tall]}
            levels.append(level)
        result[profile] = {'width': width, 'height': height, 'stamp': stamp, 'levels': levels}
    return scene['id'], result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', action='append')
    args = parser.parse_args()
    scenes = json.loads((BASE / 'scenes.json').read_text())
    manifest_path = BASE / 'delivery.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    selected = [scene for scene in scenes if not args.scene or scene['id'] in args.scene]
    with ThreadPoolExecutor(max_workers=4) as workers:
        for scene_id, result in workers.map(lambda scene: build(scene, manifest), selected):
            manifest[scene_id] = result
            print('Delivery', scene_id, flush=True)
    active = {scene['id'] for scene in scenes}
    manifest = {key: value for key, value in manifest.items() if key in active}
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print('Built responsive delivery crops for', len(manifest), 'scenes')


if __name__ == '__main__':
    main()
