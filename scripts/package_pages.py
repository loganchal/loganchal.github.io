#!/usr/bin/env python3
"""Package a committed runtime-only GitHub Pages artifact; leave Git intact.

Usage: python3 scripts/package_pages.py --output /tmp/site-runtime --report /tmp/site-runtime.json

Registered scene masters, registered intermediates, QA and generators stay in
Git, but are not browser dependencies. The staged catalogue omits its unused
legacy `assets` field and the unused legacy scenes.css is not published. URLs
for those full-frame intermediates cease being public Pages endpoints. The
current homepage/gallery use only `delivery` and keep all responsive variants.
Per-scene attribution text, credits, the complete tracked image library and
all other tracked public pages/static assets are retained.

/roms-explorer/ is an independently deployed GitHub project Pages route. It is
intentionally not shadowed by a file in this root-site artifact. Its homepage
link is validated as that declared route, rather than as an artifact file.

Official workflow contract: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
"""
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import tarfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_SUFFIXES = {'.html', '.css', '.js', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.otf', '.txt', '.xml', '.json', '.pdf', '.mp3', '.mp4', '.webm'}
SPECIAL_FILES = {'CNAME', '.nojekyll'}
NON_RUNTIME_ROOTS = {'.github', 'scripts', 'design', 'personal-review'}
NON_RUNTIME_STUDIES = {'qa', 'registered', 'retina'}
EXTERNAL_PROJECT_ROUTES = {'/roms-explorer/'}
OWN_HOSTS = {'loganchalmers.net', 'www.loganchalmers.net', 'loganchal.github.io'}


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def read_revision(revision, path):
    return git('show', f'{revision}:{path}')


def delivery_urls(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == 'urls':
                yield from child
            else:
                yield from delivery_urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from delivery_urls(child)


def exclude_reason(path, required_images):
    parts = PurePosixPath(path).parts
    if parts[0] in NON_RUNTIME_ROOTS:
        return 'development/QA/documentation'
    if len(parts) > 1 and parts[0] == 'studies':
        if parts[1] == 'scenes' and PurePosixPath(path).name != 'ATTRIBUTION.txt':
            return 'registered full-frame intermediate masters'
        if parts[1] in NON_RUNTIME_STUDIES:
            return 'development/QA/registered intermediates'
        if path == 'studies/scenes.css':
            return 'unused legacy full-frame stylesheet'
        if parts[1] == 'scene-assets' and path not in required_images:
            return 'unreferenced delivery asset'
    if path not in SPECIAL_FILES and PurePosixPath(path).suffix.lower() not in PUBLIC_SUFFIXES:
        return 'non-runtime source/documentation'
    return None


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.root_base = False

    def handle_starttag(self, tag, attrs):
        if tag == "base" and dict(attrs).get("href") == "/":
            self.root_base = True
        for name, value in attrs:
            if not value:
                continue
            if name in {'src', 'href', 'poster', 'data'}:
                self.urls.append(value)
            elif name == 'srcset':
                self.urls.extend(item.strip().split()[0] for item in value.split(',') if item.strip())


def validate_links(output, files):
    checked, projects, errors = set(), set(), []

    def check(source, url, root_relative=False):
        if not url or url.startswith('#'):
            return
        parsed = urlsplit(url)
        if parsed.scheme and parsed.scheme not in {'http', 'https'}:
            return
        if parsed.netloc and parsed.hostname not in OWN_HOSTS:
            return
        path = unquote(parsed.path)
        if not path:
            return
        if path.startswith('/'):
            resolved = posixpath.normpath(path).lstrip('/')
        else:
            parent = '' if root_relative else str(PurePosixPath(source).parent)
            resolved = posixpath.normpath(posixpath.join(parent, path))
        if resolved == '..' or resolved.startswith('../'):
            errors.append(f'{source}: reference escapes site root: {url}')
            return
        route = '/' + resolved.rstrip('/') + '/'
        if route in EXTERNAL_PROJECT_ROUTES:
            projects.add(route)
            return
        target = output / resolved
        if path.endswith('/') or target.is_dir() or resolved == '.':
            target = target / 'index.html'
        checked.add((source, url))
        if not target.is_file():
            errors.append(f'{source}: missing {url} -> {target.relative_to(output)}')

    runtime = [path for path in files if PurePosixPath(path).suffix in {'.html', '.css', '.js', '.svg'}]
    for path in runtime:
        text = (output / path).read_text()
        if path.endswith(('.html', '.svg')):
            parser = References()
            parser.feed(text)
            for url in parser.urls:
                check(path, url, root_relative=parser.root_base)
        if path.endswith(('.html', '.css', '.svg')):
            for match in re.finditer(r'''url\(\s*(?:"([^"]*)"|'([^']*)'|([^)]*))\s*\)''', text):
                check(path, next(group for group in match.groups() if group is not None).strip(), root_relative=path.endswith((".html", ".svg")) and parser.root_base)
        if path.endswith('.js'):
            # The catalogue's URL values are site-root paths. Other current JS
            # gets image URLs from that catalogue rather than fetching masters.
            if path == 'studies/catalogue.js':
                for url in delivery_urls(parse_catalogue(text)):
                    check(path, url, root_relative=True)
            else:
                for match in re.finditer(r'(?:fetch\(|import\()\s*[\"\']([^\"\']+)', text):
                    check(path, match.group(1))
        if re.search(r'''\.assets\b|\[\s*["']assets["']\s*\]''', text):
            errors.append(f'{path}: runtime reads the omitted legacy catalogue assets field')
        if re.search(r'(?:studies/)?scenes/[^\s\"\']+\.(?:webp|png|jpe?g)|(?:[\"\'/])scenes\.css', text):
            errors.append(f'{path}: runtime still refers to excluded full-frame masters/stylesheet')
    if errors:
        raise ValueError('Runtime link validation failed:\n' + '\n'.join(errors))
    return {'runtime_text_files': len(runtime), 'local_references_checked': len(checked), 'external_project_routes': sorted(projects), 'missing_local_references': 0}


def parse_catalogue(text):
    match = re.fullmatch(r'\s*const openingScenes\s*=\s*(.*);\s*', text, re.DOTALL)
    if not match:
        raise ValueError('Unsupported catalogue format: expected a single JSON openingScenes declaration')
    return json.loads(match.group(1))


def package(args):
    revision = git('rev-parse', '--verify', args.revision + '^{commit}').decode().strip()
    tracked = {}
    for item in git('ls-tree', '-r', '-z', revision).split(b'\0'):
        if item:
            header, path = item.split(b'\t', 1)
            mode, kind, _ = header.decode().split()
            tracked[path.decode()] = (mode, kind)
    catalogue = parse_catalogue(read_revision(revision, 'studies/catalogue.js').decode())
    definitions = json.loads(read_revision(revision, 'studies/scenes.json'))
    ids = [scene['id'] for scene in catalogue]
    if len(ids) != len(set(ids)) or set(ids) != {scene['id'] for scene in definitions}:
        raise ValueError('Committed scene definitions and runtime catalogue do not match; regenerate the catalogue')
    for scene in catalogue:
        for profile in ['wide', 'portrait']:
            levels = scene.get('delivery', {}).get(profile, {}).get('levels', [])
            if not levels or any(len(level.get('urls', [])) != 3 or len(level.get('widths', [])) != 3 for level in levels):
                raise ValueError(f'{scene["id"]}: incomplete three-layer delivery profile {profile}')
    required_images = {urlsplit(url).path for url in delivery_urls(catalogue)}
    if not required_images or any(not path.startswith('studies/scene-assets/') for path in required_images):
        raise ValueError('Delivery catalogue must reference registered scene-assets variants')
    missing = required_images - tracked.keys()
    if missing:
        raise ValueError('Commit is missing required delivery images: ' + ', '.join(sorted(missing)))
    included, exclusions = [], Counter()
    for path, (mode, kind) in tracked.items():
        reason = exclude_reason(path, required_images)
        if reason:
            exclusions[reason] += 1
        else:
            if kind != 'blob' or mode == '120000':
                raise ValueError(f'Refusing non-regular publishable Git entry: {path}')
            included.append(path)
    required = {'index.html', 'home.css', 'CNAME', '.nojekyll', 'plates/credits.html', 'studies/index.html', 'studies/assets.js', 'studies/catalogue.js', 'image-library/index.html', 'image-library/manifest.json'}
    if required - set(included):
        raise ValueError('Missing required public files: ' + ', '.join(sorted(required - set(included))))
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('Output must be outside the source checkout')
    if output.exists():
        raise ValueError('Output must be a new directory; no existing files are removed')
    output.mkdir(parents=True)
    # Archive the exact commit, not unrelated modifications or untracked local
    # images. Stream only selected blobs; never extract Git metadata or links.
    proc = subprocess.Popen(['git', '-C', str(ROOT), 'archive', '--format=tar', revision, '--', *included], stdout=subprocess.PIPE)
    with tarfile.open(fileobj=proc.stdout, mode='r|') as archive:
        for member in archive:
            if member.isdir():
                continue
            if member.name not in included or not member.isfile():
                raise ValueError('Unexpected archive entry: ' + member.name)
            target = output / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
    if proc.wait() != 0:
        raise ValueError('git archive failed')
    # Remove inert legacy endpoint declarations from the artifact only. Source
    # catalogue and masters remain intact in Git for analysis/reproduction.
    legacy_count = sum('assets' in scene for scene in catalogue)
    for scene in catalogue:
        scene.pop('assets', None)
    (output / 'studies/catalogue.js').write_text('const openingScenes=' + json.dumps(catalogue, ensure_ascii=False, separators=(',', ':')) + ';\n')
    checks = validate_links(output, included)
    inventory = []
    for path in sorted(included):
        content = (output / path).read_bytes()
        inventory.append({'path': path, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
    size = sum(item['bytes'] for item in inventory)
    if size > args.max_bytes:
        raise ValueError(f'Runtime artifact exceeds bound: {size:,} > {args.max_bytes:,} bytes')
    image_library = [item for item in inventory if item['path'].startswith('image-library/')]
    report = {'revision': revision, 'output': str(output), 'files': len(inventory), 'bytes': size, 'max_bytes': args.max_bytes, 'scene_count': len(catalogue), 'delivery_images': len(required_images), 'delivery_image_bytes': sum(item['bytes'] for item in inventory if item['path'] in required_images), 'image_library_files': len(image_library), 'image_library_bytes': sum(item['bytes'] for item in image_library), 'legacy_asset_fields_removed_from_staged_catalogue': legacy_count, 'excluded_file_counts': dict(exclusions), 'validation': checks, 'compatibility': {'excluded_master_urls': 'Full-frame studies/scenes image URLs and studies/registered intermediates are source artifacts, no longer public runtime endpoints.', 'excluded_legacy_stylesheet': 'studies/scenes.css is not imported by any current public page and is omitted.', 'external_project_route': '/roms-explorer/ stays independently served by its own GitHub project Pages deployment; this artifact does not shadow it.', 'source_preservation': 'All source Git files, high-quality registered renders and unrelated working-tree files are untouched.'}, 'inventory': inventory}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'inventory'}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--revision', default='HEAD', help='Committed revision to publish (default: HEAD)')
    parser.add_argument('--max-bytes', type=int, default=400_000_000)
    package(parser.parse_args())


if __name__ == '__main__':
    main()
