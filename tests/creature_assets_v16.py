"""Actual GLB anatomy, embedded maps, timing and folded-wing geometry. No GPU."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
NAMES = {'archer': 'archer-thorn', 'shade': 'shade-manta'}
for role, name in NAMES.items():
    path = ROOT / f'assets/creatures/{name}.glb'
    data = path.read_bytes()
    doc = json.loads(data[20:20 + struct.unpack_from('<I', data, 12)[0]])
    meta = json.loads((ROOT / f'assets/creatures/{name}-PROVENANCE.json').read_text())
    assert meta['sha256'] == hashlib.sha256(data).hexdigest()
    assert meta['bytes'] == len(data) < 1_500_000
    assert meta['front'] == '-Z' and meta['original_art'] and not meta['third_party_art']
    assert (ROOT / meta['source']).is_file()
    assert len(doc['materials']) == 6 and len(doc['images']) == 3
    assert all('bufferView' in image and 'uri' not in image for image in doc['images'])
    assert all('TEXCOORD_0' in p['attributes'] and 'NORMAL' in p['attributes']
               for mesh in doc['meshes'] for p in mesh['primitives'])
    for animation in doc['animations']:
        duration = max(doc['accessors'][s['input']]['max'][0] for s in animation['samplers'])
        assert abs(duration - meta['clips'][animation['name']]) < 1e-5

NODE = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
global.window=global;global.self=global;global.THREE=require('./vendor/three.min.js');
vm.runInThisContext(fs.readFileSync('vendor/three-addons.js','utf8'));
async function load(name){
 const raw=fs.readFileSync('assets/creatures/'+name+'.glb'),size=raw.readUInt32LE(12),doc=JSON.parse(raw.subarray(20,20+size)),binary=raw.subarray(20+size);
 // The real loader/skeleton are tested; maps were inspected above. No image/GPU dependency.
 for(const mesh of doc.meshes)for(const p of mesh.primitives)delete p.material;
 delete doc.materials;delete doc.images;delete doc.textures;
 let json=Buffer.from(JSON.stringify(doc));json=Buffer.concat([json,Buffer.alloc((4-json.length%4)%4,32)]);
 const header=Buffer.from(raw.subarray(0,20));header.writeUInt32LE(20+json.length+binary.length,8);header.writeUInt32LE(json.length,12);
 const b=Buffer.concat([header,json,binary]);return new Promise((resolve,reject)=>new RoyaumesGLTFLoader().parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.length),'',resolve,reject));
}
function evaluate(asset,all=false){
 asset.scene.updateMatrixWorld(true);asset.scene.traverse(o=>{if(o.isSkinnedMesh)o.skeleton.update();});
 const box=new THREE.Box3();let count=0;
 asset.scene.traverse(o=>{if(!o.isSkinnedMesh)return;const p=o.geometry.attributes.position;
  for(let i=0;i<p.count;i+=all?1:Math.max(1,Math.floor(p.count/70))){const v=o.getVertexPosition(i,new THREE.Vector3()).applyMatrix4(o.matrixWorld);assert(v.toArray().every(Number.isFinite),'Nonfinite skinned vertex');assert(v.length()<5,'Exploded skeleton');box.expandByPoint(v);count++;}
 });assert(count>100);return box;
}
(async()=>{
 const reports=[];
 for(const [role,name] of [['archer','archer-thorn'],['shade','shade-manta']]){
  const asset=await load(name),root=asset.scene,mesh=[];
  root.traverse(o=>{if(o.isSkinnedMesh)mesh.push(o);});assert(mesh.length>=5);
  let total=0;
  for(const o of mesh){const index=o.geometry.attributes.skinIndex,weight=o.geometry.attributes.skinWeight;total+=index.count;
   for(let i=0;i<index.count;i++){let sum=0;for(let j=0;j<4;j++){const w=weight.getComponent(i,j),bone=index.getComponent(i,j);assert(Number.isFinite(w)&&w>=0&&w<=1);if(w>0)assert(bone>=0&&bone<o.skeleton.bones.length);sum+=w;}assert(Math.abs(sum-1)<.002);}
  }
  assert(total>2500);assert(root.getObjectByName('head'));
  const rest=evaluate(asset,true),bind=[];root.traverse(o=>{if(o.isBone)bind.push([o,o.position.clone(),o.quaternion.clone(),o.scale.clone()]);});
  const reset=()=>{for(const [o,p,q,s]of bind){o.position.copy(p);o.quaternion.copy(q);o.scale.copy(s);}};
  const mixer=new THREE.AnimationMixer(root),clips=[];
  for(const clip of asset.animations){
   for(const track of clip.tracks)assert([...track.times,...track.values].every(Number.isFinite));
   mixer.stopAllAction();reset();const action=mixer.clipAction(clip);action.reset().setLoop(THREE.LoopOnce,1);action.clampWhenFinished=true;action.play();
   for(let i=0;i<20;i++){mixer.update(clip.duration/20);evaluate(asset);}
   clips.push({name:clip.name,duration:clip.duration});
  }
  mixer.stopAllAction();reset();evaluate(asset);
  const result={role,vertices:total,bones:mesh[0].skeleton.bones.length,clips,rest:{min:rest.min.toArray(),max:rest.max.toArray()}};
  if(role==='archer'){
   const muzzle=root.getObjectByName('muzzle').getWorldPosition(new THREE.Vector3());
   assert(muzzle.z<-.3&&muzzle.y>1.2&&muzzle.y<1.8,'Socket must be in front and at weapon height');
   assert(rest.min.y>=0&&rest.min.y<.04,'Archer toes retain a grounded origin');result.muzzle=muzzle.toArray();
  }else{
   for(const side of ['L','R'])for(const [name,angle]of [['wing',1.2],['wing_tip',.66]]){
    const bone=root.getObjectByName(name+side);assert(bone);bone.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),angle));
   }
   const folded=evaluate(asset,true),radius=Math.max(Math.abs(folded.min.x),Math.abs(folded.max.x));
   assert(Math.max(Math.abs(rest.min.x),Math.abs(rest.max.x))>1.1,'Distinct broad membrane anatomy');
   assert(radius<.55,'Folded membrane must fit the .55m core laterally');
   assert(folded.min.y>.5&&folded.max.y<2.35,'Folding must not lower a wing through the floor');
   result.folded={min:folded.min.toArray(),max:folded.max.toArray(),lateralRadius:radius};
  }
  reports.push(result);
 }
 console.log('CREATURE_ASSETS_REPORT '+JSON.stringify(reports));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
'''
result = subprocess.run(['node', '-'], cwd=ROOT, input=NODE, text=True, capture_output=True)
lines = [line for line in result.stdout.splitlines() if line.startswith('CREATURE_ASSETS_REPORT ')]
assert result.returncode == 0 and lines, result.stderr + result.stdout
report = json.loads(lines[-1].removeprefix('CREATURE_ASSETS_REPORT '))
Path('/tmp/creature-assets-v16-report.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS CPU: two distinct real skinned creatures; embedded PBR maps, normalized weights, exact clip/event timing, finite animated geometry, grounded archer origin, forward muzzle and measured folded manta wings. No GPU, human play or artistic-quality certification.')
