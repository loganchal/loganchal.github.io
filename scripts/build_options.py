"""Build a fixed, review-only set of fifteen completed opening compositions."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parent.parent
batch='fifteen-20261109'
allscenes=json.loads(re.fullmatch(r'const openingScenes = (.*);\s*',(root/'studies/catalogue.js').read_text(),re.S).group(1))
scenes=[{k:v for k,v in s.items() if k not in ['assets','active']} for s in allscenes if s.get('review_batch')==batch]
assert len(scenes)==15, f'Exactly fifteen completed options required; found {len(scenes)}'
(root/'options/catalogue.js').write_text('const openingScenes = '+json.dumps(scenes,indent=2)+';\n')
view=(root/'index.html').read_text().replace('<head>','<head><base href="/">',1)
view=view.replace('studies/catalogue.js?v=20261106-delivery','options/catalogue.js?v=20261109-fifteen')
view=view.replace('<title>Logan Chalmers', '<title>Opening option · Logan Chalmers')
view=view.replace('</head>','<meta name="robots" content="noindex,follow"></head>',1)
view=view.replace('<a href="plates/credits.html">Image credits</a>','<a href="options/">All fifteen options</a><a href="plates/credits.html">Image credits</a>')
(root/'options/view.html').write_text(view)
print('Built fifteen-option catalogue and full-screen preview')
