"""Build image credits only for the approved opening deck."""
import html,json,re
from pathlib import Path
base=Path(__file__).resolve().parent;scenes=json.loads((base/'scenes.json').read_text());used={g['source_sha256']:g for s in scenes for g in s['source_geometry']}
for scene in scenes:
 lines=[scene['title'],'','Found originals: uniformly scaled, rotated and cropped; contours are not warped.','']
 for source in scene['source_geometry']:
  lines.extend([source['credit'],source['page'],source['rights'],'Original: '+source['original'],'SHA-256: '+source['source_sha256'],'Global black point: '+str(source['black_point']),source.get('contour_kind',''),''])
 (base/'scenes'/scene['id']/'ATTRIBUTION.txt').write_text('\n'.join(lines).rstrip()+'\n')
page=base.parent/'plates/credits.html';old=page.read_text();head=old[:re.search(r'<main[^>]*>',old).end()];escape=html.escape
licences={'CC BY-SA 4.0':'https://creativecommons.org/licenses/by-sa/4.0/','Public Domain Mark':'https://creativecommons.org/publicdomain/mark/1.0/','CC0':'https://creativecommons.org/publicdomain/zero/1.0/','CC BY 2.0':'https://creativecommons.org/licenses/by/2.0/','CC BY 3.0':'https://creativecommons.org/licenses/by/3.0/','CC BY 4.0':'https://creativecommons.org/licenses/by/4.0/','CC BY-SA 2.0':'https://creativecommons.org/licenses/by-sa/2.0/','CC BY-SA 3.0 IGO':'https://creativecommons.org/licenses/by-sa/3.0/igo/','CC BY-NC-SA 3.0':'https://creativecommons.org/licenses/by-nc-sa/3.0/'}
parts=['<a href="../">← Home</a><h1>Image credits</h1><p>Found photographs and historical images used in the opening scenes. Originals are cropped, rotated and uniformly scaled; their contours are not warped. Fine stationary grain is added over the page.</p>']
for digest,g in used.items():
 rights=g['rights'];licence=next((k for k in licences if rights.startswith(k)),None);label=f'<a href="{licences[licence]}">{escape(rights)}</a>' if licence else escape(rights)
 text=f'<p><a href="{escape(g["page"],quote=True)}">{escape(g["credit"])}</a>. {label}. Cropped, rotated and uniformly scaled.'
 points=sorted({x['black_point'] for s in scenes for x in s['source_geometry'] if x['source_sha256']==digest})
 if any(points):text+=' Global black-point adjustments: '+', '.join(map(str,points))+'.'
 if 'BY-SA' in rights or 'BY-NC-SA' in rights:text+=' These cropped derivatives retain the same licence.'
 parts.append(text+'</p>')
parts.append('<p><a href="https://www.nasa.gov/nasa-brand-center/images-and-media/">NASA image use guidelines</a>.</p>');page.write_text(head+'\n'+'\n'.join(parts)+'\n</main></html>\n')
print('Credited',len(used),'originals in',len(scenes),'approved compositions')
