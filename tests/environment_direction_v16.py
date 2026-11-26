"""Actual Three.js geometry/material lifecycle, without renderer or GPU.

Shader source assembly is checked against the bundled r160 chunks. The parent
must still compile/render the generated material in the game before release.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
global.THREE=require('./vendor/three.min.js');
global.boxGeo=new THREE.BoxGeometry(1,1,1);
global.scene=new THREE.Scene();global.battle=null;global.baseWorld=null;
global.presentation={surfaces:{}};
for(const kind of ['stone','masonry','wood','cloth']){
 const make=()=>new THREE.DataTexture(new Uint8Array([128,128,255,255]),1,1);
 presentation.surfaces[kind]={map:make(),normal:make(),rough:make()};
}
let originalTextureDisposals=0;
for(const surface of Object.values(presentation.surfaces))for(const tx of Object.values(surface))tx.addEventListener('dispose',()=>originalTextureDisposals++);
const presentationCode=fs.readFileSync('src/presentation.js','utf8');
vm.runInThisContext(presentationCode.slice(presentationCode.indexOf('function applyPbrSurface('),presentationCode.indexOf('function refineHeroMaterials(')));
vm.runInThisContext(fs.readFileSync('src/staging.js','utf8'));
vm.runInThisContext(fs.readFileSync('src/environment-finish.js','utf8'));
vm.runInThisContext(fs.readFileSync('src/environment-direction-v16.js','utf8'));
const baseRegions=[[-17,17,0,29],[-27,-8,-10,0],[-24,-16,-26,-10],[-27,-8,-35,-26],[8,27,-35,0],[-27,27,-42,-35],[-14,14,-74,-42],[-62,-14,-74,-42],[14,62,-74,-42],[-23,23,-111,-74]].map(([x0,x1,z0,z1])=>({x0,x1,z0,z1}));
const huntRegions=[[-16,16,4,29],[-29,-10,-35,4],[10,29,-35,4],[-29,29,-43,-32],[-18,18,-80,-43],[-24,24,-112,-80]].map(([x0,x1,z0,z1])=>({x0,x1,z0,z1}));
const convoyRegions=[[-12,12,8,29],[-5,5,-18,8],[-18,18,-55,-18],[-32,-18,-70,-42],[18,32,-70,-42],[-10,10,-84,-55],[-23,23,-112,-84]].map(([x0,x1,z0,z1])=>({x0,x1,z0,z1}));
function floors(regions,parent){return regions.map(r=>{const material=new THREE.MeshStandardMaterial();applyPbrSurface(material,'stone');const f=new THREE.Mesh(boxGeo,material);f.position.set((r.x0+r.x1)/2,-.45,(r.z0+r.z1)/2);f.scale.set(r.x1-r.x0,.9,r.z1-r.z0);parent.add(f);return f;});}
global.world={root:new THREE.Group(),regions:baseRegions,obstacles:[],floors:[]};scene.add(world.root);world.floors=floors(baseRegions,world.root);
for(const x of [12,23])for(const z of [-9,-21,-31]){const mesh=new THREE.Mesh(boxGeo,new THREE.MeshStandardMaterial());mesh.scale.set(2.5,4,3.5);mesh.position.set(x,2,z);world.root.add(mesh);world.obstacles.push({x,z,w:2.5,d:3.5,mesh});}
global.journey={level:1,root:null};global.campaign={trials:{bells:{done:false}}};
const originals=world.floors.map(f=>f.material),piers=world.obstacles.map(o=>o.mesh.geometry),obstacles=world.obstacles;
const navJSON=JSON.stringify(baseRegions),colliderJSON=JSON.stringify(obstacles.map(({x,z,w,d})=>({x,z,w,d})));
function finiteGeometry(geometry){assert(geometry.attributes.uv,'Textured geometry has UVs');for(const attr of Object.values(geometry.attributes))assert([...attr.array].every(Number.isFinite),'Nonfinite geometry attribute');}
function outwardFoundation(){
 const one=[{x0:-3,x1:3,z0:-4,z1:4}],edges=environmentExteriorEdgesV16(one),g=environmentFoundationGeometryV16(one,1),p=g.attributes.position,normal=g.attributes.normal;
 finiteGeometry(g);assert(g.index.count===edges.length*6);
 for(let i=0;i<edges.length;i++){
  const edge=edges[i],n=new THREE.Vector3(normal.getX(i*4),normal.getY(i*4),normal.getZ(i*4));
  assert((edge.axis==='x'?n.x:n.z)*edge.sign>.5,'Skirt faces inward and disappears from outside');
  const top=p.getY(i*4);assert(top===p.getY(i*4+1)&&top<0);
  const coord=edge.axis==='x'?p.getX(i*4):p.getZ(i*4);assert(Math.abs(coord-(edge.axis==='x'?edge.x:edge.z))<1e-5,'Skirt must meet the existing foundation, without a floating slit');
 }
 const joined=[{x0:-3,x1:3,z0:-4,z1:0},{x0:-3,x1:3,z0:0,z1:4}];
 assert(!environmentExteriorEdgesV16(joined).some(e=>e.axis==='z'&&Math.abs(e.z)<1e-6),'Shared floor boundary must not receive an internal retaining wall');g.dispose();
}
outwardFoundation();
const stats=[];
function inspectOwner(owner,regions){
 owner.root.updateMatrixWorld(true);
 owner.root.traverse(o=>{if(o.isMesh){finiteGeometry(o.geometry);assert(!o.castShadow,'Decorative overhead parts must not project false ceiling shadows');}});
 assert(owner.stats.batches<=7,'Small bounded decorative draw-call increment');
 const brass=[...owner.materials].filter(m=>m.metalness>.4);assert(brass.length&&brass.every(m=>!m.map&&m.metalness===.7),'Brass may not become textured masonry or lose metalness');
 assert(owner.root.children.some(o=>o.name==='Continuous retaining foundations'));
 stats.push({level:owner.level,batches:owner.stats.batches,foundationVertices:owner.stats.foundationVertices});
}
function inspectShaders(owner){
 for(const floor of owner.parent===world.root?world.floors:journey.floorMeshes){
  const shader={uniforms:{},vertexShader:THREE.ShaderLib.standard.vertexShader,fragmentShader:THREE.ShaderLib.standard.fragmentShader};floor.material.onBeforeCompile(shader);
  assert(shader.vertexShader.includes('v16FloorWorld=v16WorldPosition.xyz'));
  assert(shader.vertexShader.includes('v16WorldPosition.zy')&&shader.vertexShader.includes('v16WorldPosition.xy'),'Floor side faces need vertical UVs, not stretched xz');
  assert(shader.vertexShader.includes('vMapUv=v16GroundUv')&&shader.vertexShader.includes('vNormalMapUv=v16GroundUv')&&shader.vertexShader.includes('vRoughnessMapUv=v16GroundUv'),'PBR maps must share the same world scale');
  assert(shader.fragmentShader.includes('float v16Inlay=')&&shader.fragmentShader.includes('roughnessFactor=mix'));
  assert(shader.uniforms.v16Completed&&floor.material.customProgramCacheKey().endsWith(String(owner.level)));
 }
}
initEnvironmentDirectionV16();const base=vm.runInThisContext('environmentDirectionV16.base');inspectOwner(base,baseRegions);inspectShaders(base);
assert(world.obstacles===obstacles&&JSON.stringify(baseRegions)===navJSON&&JSON.stringify(obstacles.map(({x,z,w,d})=>({x,z,w,d})))===colliderJSON,'Navigation and collision footprints changed');
assert(world.floors.every((f,i)=>f.material!==originals[i]));
campaign.trials.bells.done=true;updateEnvironmentDirectionV16(.016);assert(base.progress.every(u=>u.value===1));
let parent=new THREE.Group();scene.add(parent);journey={level:2,root:parent,floorMeshes:floors(huntRegions,parent)};world.regions=huntRegions;updateEnvironmentDirectionV16(.016);
let current=vm.runInThisContext('environmentDirectionV16.journey');inspectOwner(current,huntRegions);inspectShaders(current);
const beforeRoots=parent.children.length,former=current;
world.regions.push({x0:35,x1:47,z0:-68,z1:-51});journey.floorMeshes.push(...floors([world.regions.at(-1)],parent));updateEnvironmentDirectionV16(.016);current=vm.runInThisContext('environmentDirectionV16.journey');assert(current!==former&&!former.root.parent,'New optional ground must get the same material pass without leaking the old composition');inspectOwner(current,world.regions);
parent=new THREE.Group();scene.add(parent);journey={level:3,root:parent,floorMeshes:floors(convoyRegions,parent)};world.regions=convoyRegions;updateEnvironmentDirectionV16(.016);current=vm.runInThisContext('environmentDirectionV16.journey');inspectOwner(current,convoyRegions);inspectShaders(current);
assert(journey.floorMeshes.every(f=>f.material.map.source===presentation.surfaces.wood.map.source),'The living convoy deck must use wood, rather than inherited masonry');
// Every raised outboard cargo box is outside the actual union, including the
// side-route shoulders. An omitted collider must never create walk-through cargo.
current.root.traverse(o=>{if(!o.isInstancedMesh||o.geometry.type!=='BoxGeometry')return;for(let i=0;i<o.count;i++){const matrix=new THREE.Matrix4();o.getMatrixAt(i,matrix);const bounds=new THREE.Box3().setFromBufferAttribute(o.geometry.attributes.position).applyMatrix4(matrix);for(const r of convoyRegions)assert(!(bounds.max.x>r.x0&&bounds.min.x<r.x1&&bounds.max.z>r.z0&&bounds.min.z<r.z1&&bounds.max.y>.05),'Raised cargo entered a walkable route');}});
let disposedMaterials=0,disposedGeometry=0;for(const owner of [base,current]){for(const m of owner.materials)m.addEventListener('dispose',()=>disposedMaterials++);for(const g of owner.geometries)g.addEventListener('dispose',()=>disposedGeometry++);}
const materialCount=base.materials.size+current.materials.size,geometryCount=base.geometries.size+current.geometries.size;
disposeEnvironmentDirectionV16();assert(!base.root.parent&&!current.root.parent);assert(world.floors.every((f,i)=>f.material===originals[i]));assert(world.obstacles.every((o,i)=>o.mesh.geometry===piers[i]));assert(disposedMaterials===materialCount&&disposedGeometry===geometryCount);assert(originalTextureDisposals===0,'Original shared texture maps were disposed');
// A duel clears only the chapter layer; it never modifies the arena or leaks it
// into the previous chapter on return.
world.regions=baseRegions;journey={level:1,root:null};initEnvironmentDirectionV16();battle={kind:'bot'};updateEnvironmentDirectionV16(.016);assert(vm.runInThisContext('environmentDirectionV16.journey')===null);disposeEnvironmentDirectionV16();
console.log(JSON.stringify(stats));console.log('PASS: actual geometry faces outward and joins foundations; coherent PBR/wood/metal, world UVs on top and sides, raised props outside routes, dynamic secret-ground rebuild, bounded batches and complete lifecycle. CPU only, shader assembly not GPU compilation.');
'''
result = subprocess.run(['node', '-'], cwd=ROOT, input=SCRIPT, text=True, capture_output=True)
print(result.stdout, end='')
if result.returncode:
    print(result.stderr)
raise SystemExit(result.returncode)
