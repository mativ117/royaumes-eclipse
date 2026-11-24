"""Remove unused animation export data without modifying any authored keys.

One-time migration for old source blends that retained glTF preview actions.
The retarget generator itself now excludes these actions before exporting.
Never processes the approved Lame binary.
"""
from pathlib import Path
import json,struct,hashlib
ROOT=Path(__file__).resolve().parents[1]
NAMES={'idle','guard','walk','run','walk_back','strafe_left','strafe_right','attack1','attack2','attack3','shot','power','dash','dodge_left','dodge_right','start','stop','turn_left','turn_right','leap','shield','interact','carry','hit'}
ROLES=['rempart','voltigeur','tisseuse','cendres','voleur','bergere','colosse','accordeur','neant','eclipse']
def compact(path):
 raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=raw[28+size:]
 if len(doc['buffers'])!=1:raise ValueError('Only embedded single-buffer GLBs are supported')
 before=len(doc['animations']);doc['animations']=[a for a in doc['animations'] if a['name'] in NAMES]
 if {a['name'] for a in doc['animations']}!=NAMES:raise ValueError('Missing roster clips '+path.stem)
 used=set()
 for mesh in doc.get('meshes',[]):
  for primitive in mesh['primitives']:
   used.update(primitive['attributes'].values())
   if 'indices' in primitive:used.add(primitive['indices'])
   for target in primitive.get('targets',[]):used.update(target.values())
 for skin in doc.get('skins',[]):
  if 'inverseBindMatrices' in skin:used.add(skin['inverseBindMatrices'])
 for animation in doc['animations']:
  for sampler in animation['samplers']:used.update((sampler['input'],sampler['output']))
 accessors={old:new for new,old in enumerate(sorted(used))}
 for mesh in doc.get('meshes',[]):
  for primitive in mesh['primitives']:
   primitive['attributes']={name:accessors[i] for name,i in primitive['attributes'].items()}
   if 'indices' in primitive:primitive['indices']=accessors[primitive['indices']]
   for target in primitive.get('targets',[]):
    for name in target:target[name]=accessors[target[name]]
 for skin in doc.get('skins',[]):
  if 'inverseBindMatrices' in skin:skin['inverseBindMatrices']=accessors[skin['inverseBindMatrices']]
 for animation in doc['animations']:
  for sampler in animation['samplers']:
   for name in ['input','output']:sampler[name]=accessors[sampler[name]]
 doc['accessors']=[doc['accessors'][i] for i in sorted(used)]
 used_views=set()
 for accessor in doc['accessors']:
  if 'bufferView' in accessor:used_views.add(accessor['bufferView'])
  for item in accessor.get('sparse',{}).values():
   if isinstance(item,dict) and 'bufferView' in item:used_views.add(item['bufferView'])
 for image in doc.get('images',[]):
  if 'bufferView' in image:used_views.add(image['bufferView'])
 views={old:new for new,old in enumerate(sorted(used_views))};packed=bytearray()
 new_views=[]
 for old in sorted(used_views):
  view=dict(doc['bufferViews'][old]);offset=view.get('byteOffset',0);length=view['byteLength'];packed.extend(b'\0'*((-len(packed))%4));view['byteOffset']=len(packed);packed.extend(binary[offset:offset+length]);new_views.append(view)
 for accessor in doc['accessors']:
  if 'bufferView' in accessor:accessor['bufferView']=views[accessor['bufferView']]
  for item in accessor.get('sparse',{}).values():
   if isinstance(item,dict) and 'bufferView' in item:item['bufferView']=views[item['bufferView']]
 for image in doc.get('images',[]):
  if 'bufferView' in image:image['bufferView']=views[image['bufferView']]
 doc['bufferViews']=new_views;doc['buffers'][0]['byteLength']=len(packed);packed.extend(b'\0'*((-len(packed))%4))
 data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4)
 result=struct.pack('<III',0x46546c67,2,28+len(data)+len(packed))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(packed),0x004e4942)+packed
 path.write_bytes(result);print(path.stem,before,'->',len(doc['animations']),len(raw),'->',len(result),flush=True)
 return result

def main():
 metadata_path=ROOT/'assets/characters/ROSTER-PRODUCTION.json';metadata=json.loads(metadata_path.read_text());provenance_path=ROOT/'assets/characters/PROVENANCE.json';provenance=json.loads(provenance_path.read_text())
 for role in ROLES:
  raw=compact(ROOT/'assets/characters'/f'{role}.glb');info=metadata['characters'][role];info.update({'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'clips':sorted(NAMES)});provenance['sha256'][role+'.glb']=info['sha256'];provenance['per_character'][role]=info
 metadata_path.write_text(json.dumps(metadata,indent=2)+'\n');provenance_path.write_text(json.dumps(provenance,indent=2)+'\n')
if __name__=='__main__':main()
