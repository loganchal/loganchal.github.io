"""Generate public opening assets and validate distinct motifs per scene."""
import json,hashlib
from subjects import subjects
from pathlib import Path
b=Path(__file__).resolve().parent
scenes=json.loads((b/'scenes.json').read_text())
delivery=json.loads((b/'delivery.json').read_text()) if (b/'delivery.json').exists() else {}
entries=[];css=[]
assert len({scene['id'] for scene in scenes})==len(scenes),'Duplicate scene ID'
for scene in scenes:
 for key in ('id','title','radius','angle','finalInset','lead','motifs'):
  assert scene.get(key) is not None,(scene.get('id'), 'Missing scene field', key)
 for source in scene['source_geometry']:
  for key in ('source_file','circle','source_angle','black_point','page','original','credit','rights','source_sha256'):
   assert source.get(key) is not None,(scene['id'], 'Missing source field', key)
 subject_types=subjects(scene)
 assert len(scene['motifs'])==3 and len(set(scene['motifs']))==3,scene['id']
 entry={k:scene[k] for k in ('id','title','radius','portraitRadius','horizon','angle','finalInset','gap','tone','lead','motifs','portrait_angle','portrait_horizon','openingInset','portrait_openingInset') if k in scene}
 entry['subjects']=subject_types
 stamp=hashlib.sha256(json.dumps(scene,sort_keys=True).encode()).hexdigest()[:12]
 entry['assets']={}
 if scene['id'] in delivery:entry['delivery']=delivery[scene['id']]
 for profile,W in [('wide',1600),('portrait',768)]:
  density=scene.get('portrait_density',scene.get('render_density',2.4)) if profile=='portrait' else scene.get('render_density',2.4)
  size=round(W*density)
  entry['assets'][profile]=[f"studies/scenes/{scene['id']}/{i}-{profile}-{size}.webp?v={stamp}" for i in range(3)]
  if profile=='portrait':css.append('@media(max-aspect-ratio:1/1){')
  for slot,selector in [(0,'first-child'),(1,'last-child'),(2,'nth-child(2)')]:
   prefix='.stage ' if profile=='portrait' else ''
   root=f"scenes/{scene['id']}/{slot}-{profile}"
   css.append(f"{prefix}.arc-study.{scene['id']}>i:{selector}{{background-image:image-set(url({root}-{W}.webp?v={stamp}) 1x,url({root}-{size}.webp?v={stamp}) 2x)}}")
  if profile=='portrait':css.append('}')
 entries.append(entry)
(b/'catalogue.js').write_text('const openingScenes = '+json.dumps(entries,indent=2)+';\n')
(b/'scenes.css').write_text('\n'.join(css)+'\n')
print(f'Generated {len(entries)} curated scenes; every scene has three different motifs.')
