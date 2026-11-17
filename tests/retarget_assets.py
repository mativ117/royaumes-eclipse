"""Static integrity of the CC0 retarget, original geometry and runtime metadata.
No renderer, Blender process or network is needed.
"""
from pathlib import Path
import json,struct,hashlib,math,zipfile
ROOT=Path(__file__).resolve().parents[1]
def glb(raw):
 assert raw[:4]==b'glTF' and struct.unpack_from('<I',raw,4)[0]==2
 size=struct.unpack_from('<I',raw,12)[0]
 return json.loads(raw[20:20+size]),raw[20+size+8:]
def accessor(document,binary,index):
 a=document['accessors'][index];view=document['bufferViews'][a['bufferView']]
 size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
 code,width={5126:('f',4),5125:('I',4),5123:('H',2),5121:('B',1)}[a['componentType']]
 offset=view.get('byteOffset',0)+a.get('byteOffset',0);stride=view.get('byteStride',size*width)
 return [struct.unpack_from('<'+code*size,binary,offset+i*stride) for i in range(a['count'])]
def geometry_digest(document,binary):
 result=[]
 for mesh in document['meshes']:
  values=set()
  for primitive in mesh['primitives']:
   attrs=primitive['attributes'];p=accessor(document,binary,attrs['POSITION']);uv=accessor(document,binary,attrs['TEXCOORD_0'])
   values.update(tuple(round(x,5) for x in point+coord) for point,coord in zip(p,uv))
  result.append((mesh['name'],sorted(values)))
 return hashlib.sha256(json.dumps(sorted(result),separators=(',',':')).encode()).hexdigest()
raw=(ROOT/'assets/characters/lame.glb').read_bytes();document,binary=glb(raw)
production=json.loads((ROOT/'assets/characters/LAME-PRODUCTION.json').read_text())
assert hashlib.sha256(raw).hexdigest()==production['sha256']
assert len(document['animations'])==23 and len({a['name'] for a in document['animations']})==23
assert len(document['materials'])==8 and len(document['images'])==3
assert all('bufferView' in image for image in document['images'])
lookup={node.get('name'):i for i,node in enumerate(document['nodes'])}
for name in ['weaponGrip','blade_base','blade_tip','hand.R']:assert name in lookup,name
assert lookup['weaponGrip'] in document['nodes'][lookup['hand.R']].get('children',[])
assert {lookup['blade_base'],lookup['blade_tip']}<=set(document['nodes'][lookup['weaponGrip']].get('children',[]))
metadata=next(node['extras']['motionCalibration'] for node in document['nodes'] if 'motionCalibration' in node.get('extras',{}))
if isinstance(metadata,str):metadata=json.loads(metadata)
assert metadata==production['motion_calibration'] and metadata['units']=='model'
animations={a['name']:a for a in document['animations']}
for name in ['walk','run']:
 gait=metadata['gaits'][name];duration=max(document['accessors'][s['input']]['max'][0] for s in animations[name]['samplers'])
 assert abs(duration-gait['duration'])<1e-5,(name,duration,gait['duration'])
 assert gait['cycleDistance']>0 and all(gait['contacts'][side] for side in ['L','R'])
 assert all(0<=start<end<=1 for values in gait['contacts'].values() for start,end in values)
rate=5.5*metadata['gaits']['run']['duration']/(metadata['gaits']['run']['cycleDistance']*1.07)
assert .8<rate<1.1,rate
for name in ['attack1','attack2','attack3']:
 attack=metadata['attacks'][name];duration=max(document['accessors'][s['input']]['max'][0] for s in animations[name]['samplers'])
 assert abs(duration-attack['duration'])<1e-5,(name,duration,attack['duration'])
 assert 0<attack['hitAt']<attack['activeEnd']<duration
 assert .1<=attack['travel']<=1.2
assert metadata['attacks']['attack3']['duration']<=1.5
assert production['base_geometry_uv_sha256']==geometry_digest(document,binary),'Approved geometry/UVs must not change during animation work'
for animation in document['animations']:
 for sampler in animation['samplers']:
  assert all(math.isfinite(x) for values in accessor(document,binary,sampler['output']) for x in values)
 # New actor displacement remains under the physical controller, not hidden root translations.
 if animation['name'] in production['retargeted_clips']:
  for channel in animation['channels']:
   if channel['target']=={'node':lookup['root'],'path':'translation'}:
    assert all(abs(v[0])+abs(v[2])<1e-6 for v in accessor(document,binary,animation['samplers'][channel['sampler']]['output']))
provenance=json.loads((ROOT/'assets/animations/quaternius/PROVENANCE.json').read_text())
for source in provenance['assets']:
 path=ROOT/'assets/animations/quaternius'/source['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256']
 assert 'Standard' in source['download_edition'] and 'CC0' in source['license']
assert 'https://' not in json.dumps(production.get('temporary_download_urls',[]))
print('PASS: original geometry/UVs and PBR atlas retained; 23 valid clips, independent weapon anchors, exact timing metadata, realistic jog cadence, finite keys, in-place root and immutable CC0 Standard sources. Artistic quality still needs normal-speed review.')
