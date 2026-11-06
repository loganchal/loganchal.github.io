"""Subject-level checks: different vessel materials are still the same object type."""
DIAGRAMS={'aratus','lahire','dewit','eimmart','brunacci'}
CONTAINERS={'red','celadon','crackle','clematis','cobalt-kirin','patina','silver','basket','shoshone-basket'}
HORIZONS={'apollo-earth','artemis','atlantic-dawn','cobalt-cloud-earth','blue-ocean-twilight','cloud-airglow','green-airglow','milky-airglow','eclipse','solar-phi','sunlit-earth','pacific-ocean','polar-ground'}
def subjects(scene):
 result=[]
 for name,g in zip(scene['slots'],scene['source_geometry']):
  kind=g.get('subject_type')
  if not kind:
   if name in CONTAINERS:kind='vessel'
   elif name in DIAGRAMS:kind='mathematical-diagram'
   elif name in HORIZONS or name.lower().startswith(('iss','as17','art00')):kind='celestial-horizon'
   elif name=='belemnite':kind='shell-specimen'
   elif name=='compoundeye':kind='compound-eye'
   elif name=='glass':kind='optical-glass'
   elif any(part in name.lower() for part in ['painting','riv​als','rivals','favourites','golden-stairs','venus','heliogabalus']):kind='painting'
   else:raise ValueError(f'Classify the actual subject type for {scene["id"]}: {name}')
  result.append(kind)
 assert len(set(result))==3,(scene['id'],'Repeated subject type',result)
 return result
