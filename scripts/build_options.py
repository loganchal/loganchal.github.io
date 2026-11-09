"""Build a fixed, review-only set of fifteen completed opening compositions."""
import json,re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent.parent
batch='fifteen-20261109'
allscenes=json.loads(re.fullmatch(r'const openingScenes = (.*);\s*',(root/'studies/catalogue.js').read_text(),re.S).group(1))
scenes=[{k:v for k,v in s.items() if k not in ['assets','active']} for s in allscenes if s.get('review_batch')==batch]
assert len(scenes)==15, f'Exactly fifteen completed options required; found {len(scenes)}'
payload='const openingScenes = '+json.dumps(scenes,indent=2)+';\n'
(root/'options/catalogue.js').write_text(payload)
stamp=hashlib.sha256(payload.encode()).hexdigest()[:12]
view=(root/'index.html').read_text().replace('<head>','<head><base href="/">',1)
view=re.sub(r'studies/catalogue\.js\?v=[A-Za-z0-9-]+','options/catalogue.js?v='+stamp,view)
view=view.replace('<title>Logan Chalmers', '<title>Opening option · Logan Chalmers')
view=view.replace('</head>','<meta name="robots" content="noindex,follow"></head>',1)
view=view.replace('<a href="plates/credits.html">Image credits</a>','<a href="options/">All fifteen options</a><a href="plates/credits.html">Image credits</a>')
(root/'options/view.html').write_text(view)
p=root/'options/index.html';p.write_text(re.sub(r'options/catalogue\.js\?v=[A-Za-z0-9-]+','options/catalogue.js?v='+stamp,p.read_text()))
print('Built fifteen-option catalogue and full-screen preview')
