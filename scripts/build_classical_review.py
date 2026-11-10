"""Build the completed classical-scene comparison using the real homepage player."""
from pathlib import Path
import json,re,hashlib
root=Path(__file__).resolve().parent.parent
scenes=json.loads(re.fullmatch(r'const openingScenes = (.*);\s*',(root/'studies/catalogue.js').read_text(),re.S).group(1))
ids=['gold-earth','bode-artemis-rivals','eimmart-artemis-stairs']
byid={s['id']:s for s in scenes}
assert all(i in byid for i in ids),'Every requested composition must have completed delivery assets'
selected=[{k:v for k,v in byid[i].items()if k not in ['active','assets']}for i in ids]
assert all(s.get('delivery')for s in selected)
out=root/'classical-scenes';out.mkdir(exist_ok=True)
payload='const openingScenes = '+json.dumps(selected,indent=2)+';\n';stamp=hashlib.sha256(payload.encode()).hexdigest()[:12];(out/'catalogue.js').write_text(payload)
view=(root/'index.html').read_text().replace('<head>','<head><base href="/">',1)
view=re.sub(r'studies/catalogue\.js\?v=[A-Za-z0-9-]+','classical-scenes/catalogue.js?v='+stamp,view)
view=view.replace('<title>Logan Chalmers','<title>Classical scene · Logan Chalmers').replace('</head>','<meta name="robots" content="noindex,follow"></head>',1).replace('<a href="plates/credits.html">Image credits</a>','<a href="classical-scenes/">All classical scenes</a><a href="plates/credits.html">Image credits</a>')
(out/'view.html').write_text(view)
gallery=(root/'options/index.html').read_text().replace('options/','classical-scenes/').replace('Fifteen openings','Classical scenes').replace('Fifteen openings.','Classical scenes.').replace('Different materials, different horizons. Each composition shares one curve. Open any scene to try its full-screen entrance.','A new scene variation, followed by the two favourites. Open a composition to try the complete entrance; switch between desktop and phone framing below.')
gallery=re.sub(r'classical-scenes/catalogue\.js\?v=[A-Za-z0-9-]+','classical-scenes/catalogue.js?v='+stamp,gallery)
(out/'index.html').write_text(gallery)
print('Built3completeclassicalscenes:1newvariationand2unchangedbenchmarks')
