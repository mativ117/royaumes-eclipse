"""CPU-only material regression: authored GLB maps, load gate, UVs and environment finish.

Loads the actual Three.js classes and GLB loader, but never creates a renderer or
WebGL context. The photographic image decode is deliberately deferred to verify
that the Start button cannot unlock while its maps are placeholders.
"""
from pathlib import Path
import base64
import hashlib
import json
import struct
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'assets/characters/lame.glb'
model=MODEL.read_bytes()
length=struct.unpack_from('<I',model,12)[0]
gltf=json.loads(model[20:20+length])
assert any(m['name']=='Oiled leather' for m in gltf['materials'])
assert all('bufferView' in image for image in gltf['images']), 'Lame images must remain embedded'
provenance=json.loads((ROOT/'assets/characters/PROVENANCE.json').read_text())
production=json.loads((ROOT/'assets/characters/LAME-PRODUCTION.json').read_text())
assert hashlib.sha256(model).hexdigest()==production['sha256']==provenance['sha256']['lame.glb']
assert provenance['per_character']['lame']['sha256']==production['sha256']

surfaces={kind:{field:'data:image/jpeg;base64,'+base64.b64encode((ROOT/f'assets/materials/{kind}-{field}.jpg').read_bytes()).decode() for field in ['map','normal','rough']} for kind in ['stone','masonry']}
bootstrap='''
requestAnimationFrame=()=>0;
const ROYAUMES_SURFACES=SURFACES_JSON;
const originalImage=window.Image, sourceDescriptor=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,'src');
const heldImages=[];
window.Image=function(){const image=new originalImage();Object.defineProperty(image,'src',{get(){return sourceDescriptor.get.call(image)},set(value){heldImages.push(()=>sourceDescriptor.set.call(image,value))}});return image;};
function releaseMaterialImages(){window.Image=originalImage;for(const release of heldImages.splice(0))release();}
window.$=selector=>document.querySelector(selector);
window.renderer={capabilities:{getMaxAnisotropy:()=>4}};
window.hero='lame';
'''.replace('SURFACES_JSON',json.dumps(surfaces))
modules=['vendor/three.min.js','vendor/three-addons.js','src/material-surfaces.js','src/presentation.js','src/environment-finish.js','src/journey.js','src/visual-world.js','src/authored-avatar.js']
html='<button id="start">Commencer</button><p id="intro"></p><script>'+bootstrap+'</script>'
for name in modules:html+='<script>'+(ROOT/name).read_text()+'</script>'

with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu','--disable-software-rasterizer'])
 page=browser.new_page();errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.set_content(html)
 run=page.evaluate
 run('''window.modelLoads=[];
 ensureHeroModel=async name=>{modelLoads.push(name);return{name}};
 syncAvatarSelection=()=>{};
 presentation={surfaces:{stone:referenceSurface('stone',renderer),masonry:referenceSurface('masonry',renderer)},worldTextures:[]};
 presentation.surfaces.cloth=presentation.surfaces.stone;
 var groundMaterial=new THREE.MeshStandardMaterial();applyPbrSurface(groundMaterial,'stone',2,3,presentation.worldTextures);
 var placeholderVersion=groundMaterial.map.version;
 loadAuthoredHeroes();void 0;''')
 assert run('heldImages.length===6&&avatarRuntime.status==="loading"&&document.querySelector("#start").disabled&&modelLoads.length===0'), 'Start must await all photographed maps, before hero loads'
 run('releaseMaterialImages()')
 page.wait_for_function('avatarRuntime.status==="ready"',polling=50)
 assert run('!document.querySelector("#start").disabled&&modelLoads.join(",")==="rempart,voltigeur,lame"')
 assert run('groundMaterial.map.version>placeholderVersion&&groundMaterial.map.image===presentation.surfaces.stone.map.image'), 'Already assigned clones must receive the real photo'
 assert run('''()=>{const c=groundMaterial.map.image,d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let low=255,high=0;for(let i=0;i<d.length;i+=148){low=Math.min(low,d[i]);high=Math.max(high,d[i])}return high-low>30}'''), 'Photographic map must replace the uniform placeholder'

 # Parse actual GLB into real material/texture instances; no renderer is needed.
 run('''async encoded=>{const bytes=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0));const asset=await new Promise((resolve,reject)=>new RoyaumesGLTFLoader().parse(bytes.buffer,'',resolve,reject));
 const source=new Map();asset.scene.traverse(o=>{if(o.isMesh)for(const m of(Array.isArray(o.material)?o.material:[o.material]))source.set(m.name,m)});
 window.authoredAvatar={ownedMaterials:[...source.values()].map(m=>m.clone())};
 window.authoredBefore=authoredAvatar.ownedMaterials.map(m=>({name:m.name,map:m.map,normal:m.normalMap,rough:m.roughnessMap,metal:m.metalnessMap,color:m.color.clone(),roughness:m.roughness,metalness:m.metalness}));
 refineHeroMaterials(authoredAvatar);}
 ''',base64.b64encode(model).decode())
 assert run('authoredBefore.some(m=>m.name==="Oiled leather")')
 assert run('''authoredAvatar.ownedMaterials.every((m,i)=>{const old=authoredBefore[i];return old.map&&old.normal&&old.rough&&m.map===old.map&&m.normalMap===old.normal&&m.roughnessMap===old.rough&&m.metalnessMap===old.metal&&m.color.equals(old.color)&&m.roughness===old.roughness&&m.metalness===old.metalness})'''), 'Authored atlas/ORM/normal maps and material values must survive refinement, including Oiled leather'
 assert run('!authoredAvatar.surfaceTextures?.length'), 'Authored Lame must not allocate replacement cloth maps'

 run('''window.scene=new THREE.Scene();window.world={root:new THREE.Group(),regions:[{x0:-5,x1:5,z0:0,z1:10},{x0:-5,x1:5,z0:-10,z1:0}],obstacles:[]};scene.add(world.root);
 window.boxGeo=new THREE.BoxGeometry(1,1,1);window.stone=new THREE.MeshStandardMaterial();window.dark=new THREE.MeshStandardMaterial({color:'#111111'});
 window.bareGeometry=new THREE.BufferGeometry();bareGeometry.setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,1,0,0,0,1,0],3));bareGeometry.computeVertexNormals();
 window.foundation=new THREE.Mesh(bareGeometry,dark);world.root.add(foundation);
 window.unmappedMetal=new THREE.MeshStandardMaterial({color:'#876b3f',metalness:.8,roughness:.3});window.metalProp=new THREE.Mesh(boxGeo,unmappedMetal);world.root.add(metalProp);
 world.abyss=new THREE.Mesh(new THREE.PlaneGeometry(20,20),new THREE.MeshBasicMaterial());world.root.add(world.abyss);
 window.regionsBefore=JSON.stringify(world.regions);window.obstaclesBefore=world.obstacles;
 initEnvironmentFinish();''')
 assert run('''bareGeometry.attributes.uv.count===bareGeometry.attributes.position.count&&[...bareGeometry.attributes.uv.array].every(Number.isFinite)'''), 'Textured merged geometry needs finite UVs'
 assert run('foundation.material.map&&foundation.material.normalMap&&foundation.material.roughnessMap&&world.abyss.material.map&&world.abyss.material.normalMap'), 'Foundations and abyss must receive a complete surface'
 assert run('metalProp.material===unmappedMetal&&!metalProp.material.map&&metalProp.material.metalness===.8'), 'Unmapped metal must not accidentally match an undefined old stone map'
 assert run('world.materialFinish.rims>0&&world.materialFinish.supports>0&&world.finishRoot.children.some(o=>o.isInstancedMesh&&o.count>0)'), 'World boundaries must have visible finishing geometry'
 assert run('JSON.stringify(world.regions)===regionsBefore&&world.obstacles===obstaclesBefore&&world.obstacles.length===0'), 'Decorative finish must preserve navigation/collision data'
 # Chapter surfaces must honour their material identity instead of coating wood in masonry.
 run('''presentation.surfaces.wood=surfaceTextures('wood');presentation.surfaces.cloth=surfaceTextures('cloth');
 journey={level:3,root:new THREE.Group(),materials:[],textures:[],geometries:[]};
 window.chapterWood=journeyMaterial('#605145',.05,.9,'wood');window.chapterCloth=journeyMaterial('#753c36',.05,.9,'cloth');window.chapterStone=journeyMaterial('#777777');window.chapterMetal=journeyMaterial('#ba8844',.8,.3);
 window.chapterMesh=new THREE.Mesh(bareGeometry.clone(),chapterWood);chapterMesh.geometry.deleteAttribute('uv');journey.root.add(chapterMesh);window.coneGeo=new THREE.ConeGeometry(1,1,8);
 refineJourneyPresentation();''')
 assert run('chapterWood.map.source===presentation.surfaces.wood.map.source&&chapterCloth.map.source===presentation.surfaces.cloth.map.source&&chapterStone.map.source===presentation.surfaces.masonry.map.source'), 'Wood, cloth and stone need their own surface families'
 assert run('!chapterMetal.map&&chapterMetal.metalness===.8'), 'Chapter metal must remain metallic'
 assert run('chapterMesh.geometry.attributes.uv.count===chapterMesh.geometry.attributes.position.count'), 'Textured chapter geometry needs UVs too'
 assert not errors,errors
 browser.close()
print('PASS: actual authored GLB maps/ORM retained, photographic load gate and clone updates, finite UVs, finished foundations/borders/abyss, chapter surface identities and preserved collision data. CPU-only; no WebGL renderer or FPS claim.')
