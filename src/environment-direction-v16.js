'use strict';
// Authored spatial hierarchy, not extra gameplay geometry. All raised additions
// are outside navigation; floor colour/normal/roughness share world-space UVs.
let environmentDirectionV16=null;

function environmentExteriorEdgesV16(regions){
 const result=[];
 for(const r of regions)for(const [axis,sign]of [['x',-1],['x',1],['z',-1],['z',1]]){
  const start=axis==='x'?r.z0:r.x0,end=axis==='x'?r.z1:r.x1,count=Math.max(1,Math.ceil((end-start)/2));
  for(let i=0;i<count;i++){
   const a=start+(end-start)*i/count,b=start+(end-start)*(i+1)/count,q=(a+b)/2;
   const x=axis==='x'?(sign<0?r.x0:r.x1):q,z=axis==='z'?(sign<0?r.z0:r.z1):q;
   const outsideX=x+(axis==='x'?sign*.02:0),outsideZ=z+(axis==='z'?sign*.02:0);
   if(regions.some(other=>other!==r&&outsideX>other.x0&&outsideX<other.x1&&outsideZ>other.z0&&outsideZ<other.z1))continue;
   result.push({axis,sign,a,b,x,z});
  }
 }
 return result;
}

function environmentFoundationGeometryV16(regions,level){
 const positions=[],uv=[],indices=[],colors=[];
 const color=new THREE.Color(level===2?'#65706a':level===3?'#635e58':'#6b6260');
 for(const edge of environmentExteriorEdgesV16(regions)){
  const base=positions.length/3,axis=edge.axis,normal=edge.sign;
  const depth=level===3?3.8:level===2?4.4:6.6;
  const offset=0,spread=level===3?.42:1.05;
  for(const [u,y,out]of [[edge.a,-.44,offset],[edge.b,-.44,offset],[edge.a,-depth,spread],[edge.b,-depth,spread]]){
   const x=axis==='x'?edge.x+normal*out:u,z=axis==='z'?edge.z+normal*out:u;
   positions.push(x,y,z);uv.push(u*.22,y*.22);
   const shade=y<-.5?.62:1;colors.push(color.r*shade,color.g*shade,color.b*shade);
  }
  if((axis==='x'&&normal>0)||(axis==='z'&&normal<0))indices.push(base,base+1,base+2,base+1,base+3,base+2);
  else indices.push(base,base+2,base+1,base+1,base+2,base+3);
 }
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geometry.setIndex(indices);geometry.computeVertexNormals();geometry.computeBoundingBox();geometry.computeBoundingSphere();return geometry;
}

function environmentFloorMaterialV16(original,level,owner){
 const material=original.clone();material.name='World-aligned '+(level===3?'aged deck':'mineral paving');if(level===3&&typeof applyPbrSurface==='function')applyPbrSurface(material,'wood',1,1,owner.textures);material.roughness=.9;material.metalness=level===3?.02:.055;
 const completed={value:0};owner.progress.push(completed);
 material.onBeforeCompile=shader=>{
  shader.uniforms.v16Completed=completed;
  shader.vertexShader='varying vec3 v16FloorWorld;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <uv_vertex>',`#include <uv_vertex>
    vec4 v16WorldPosition=modelMatrix*vec4(position,1.0);
    v16FloorWorld=v16WorldPosition.xyz;
    vec3 v16SurfaceNormal=abs(mat3(modelMatrix)*normal);
    vec2 v16GroundUv=(v16SurfaceNormal.y>=max(v16SurfaceNormal.x,v16SurfaceNormal.z)?v16WorldPosition.xz:v16SurfaceNormal.x>v16SurfaceNormal.z?v16WorldPosition.zy:v16WorldPosition.xy)*.2;
    #ifdef USE_MAP
      vMapUv=v16GroundUv;
    #endif
    #ifdef USE_NORMALMAP
      vNormalMapUv=v16GroundUv;
    #endif
    #ifdef USE_ROUGHNESSMAP
      vRoughnessMapUv=v16GroundUv;
    #endif
    #ifdef USE_METALNESSMAP
      vMetalnessMapUv=v16GroundUv;
    #endif`);
  shader.fragmentShader='varying vec3 v16FloorWorld;\nuniform float v16Completed;\n'+shader.fragmentShader;
  let surface;
  if(level===1)surface=`
    float v16Arrival=(1.-step(29.,v16FloorWorld.z))*step(0.,v16FloorWorld.z);
    float v16Lane=1.-smoothstep(1.4,2.5,abs(abs(v16FloorWorld.x)-6.8));
    float v16Radius=length(v16FloorWorld.xz-vec2(0.,13.));
    float v16Rings=min(abs(v16Radius-8.8),min(abs(v16Radius-11.6),abs(v16Radius-14.2)));
    float v16Cloister=step(8.,v16FloorWorld.x)*step(-35.,v16FloorWorld.z)*(1.-step(0.,v16FloorWorld.z));
    float v16Procession=1.-smoothstep(1.2,2.3,abs(v16FloorWorld.x-17.5));
    float v16Inlay=max((1.-smoothstep(.035,.09,v16Rings))*v16Arrival,(1.-smoothstep(.035,.09,abs(abs(v16FloorWorld.x-17.5)-2.7)))*v16Cloister);
    vec3 v16Tint=mix(vec3(.62,.76,.86),vec3(1.06,1.03,.91),v16Lane*v16Arrival);
    v16Tint=mix(v16Tint,mix(vec3(.64,.73,.78),vec3(1.14,1.09,.93),v16Procession),v16Cloister);
    diffuseColor.rgb*=v16Tint;
    diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.31,.16,.045)+v16Completed*vec3(.045,.04,.025),v16Inlay*.72);`;
  else if(level===2)surface=`
    float v16Natural=.5+.5*sin(v16FloorWorld.x*.43+sin(v16FloorWorld.z*.21))*sin(v16FloorWorld.z*.37);
    float v16Path=1.-smoothstep(2.5,4.5,abs(abs(v16FloorWorld.x)-19.5));
    float v16Start=step(4.,v16FloorWorld.z),v16Observatory=1.-step(-43.,v16FloorWorld.z);
    float v16Inlay=(1.-smoothstep(.045,.11,abs(length(v16FloorWorld.xz-vec2(0.,-62.))-12.8)))*v16Observatory;
    vec3 v16Soil=mix(vec3(.40,.60,.55),vec3(.65,.74,.61),v16Natural);
    diffuseColor.rgb*=mix(v16Soil,vec3(.97,1.02,.91),max(v16Path,(1.-smoothstep(5.,8.,abs(v16FloorWorld.x)))*v16Start));
    diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.27,.30,.23),v16Inlay*.75);`;
  else surface=`
    float v16Inlay=1.-smoothstep(.03,.075,abs(mod(v16FloorWorld.x+1.25,2.5)-1.25));
    float v16Wear=.75+.25*sin(v16FloorWorld.x*3.9+sin(v16FloorWorld.z*.08)*.15);
    diffuseColor.rgb*=vec3(.91,.91,.83)*v16Wear;
    diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.16,.12,.07),v16Inlay*.23);`;
  shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>','#include <map_fragment>\n'+surface);
  shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\nroughnessFactor=mix(roughnessFactor,.48,v16Inlay*.65);');
 };
 material.customProgramCacheKey=()=> 'eclipse-ground-composition-v16-'+level;
 owner.materials.add(material);return material;
}

function environmentOwnedStateV16(parent,level){return{parent,level,root:new THREE.Group(),geometries:new Set(),materials:new Set(),textures:[],restores:[],progress:[],cloth:[],age:0,stats:{batches:0,foundationVertices:0}};}
function environmentMaterialV16(owner,color,surface='masonry',metalness=.05){
 const material=new THREE.MeshStandardMaterial({color,roughness:metalness>.4?.48:.9,metalness});
 if(metalness<.4&&typeof applyPbrSurface==='function')applyPbrSurface(material,surface,1,1,owner.textures);material.metalness=metalness;material.roughness=metalness>.4?.48:.9;
 owner.materials.add(material);return material;
}
function environmentBatchV16(owner,geometry,material,items){
 if(!items.length)return null;owner.geometries.add(geometry);
 const mesh=new THREE.InstancedMesh(geometry,material,items.length),dummy=new THREE.Object3D();
 items.forEach((item,i)=>{dummy.position.set(...item.p);dummy.scale.set(...item.s);dummy.rotation.set(...(item.r||[0,0,0]));dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);});
 mesh.castShadow=false;mesh.receiveShadow=true;mesh.name='Environment composition batch';owner.root.add(mesh);owner.stats.batches++;return mesh;
}
function environmentCurveGeometryV16(points,radius=.2){return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p))),18,radius,7,false);}
function environmentMergedV16(owner,parts,material){
 const geometry=mergedStageParts(parts);ensureSurfaceUv(geometry);owner.geometries.add(geometry);const mesh=new THREE.Mesh(geometry,material);mesh.castShadow=false;mesh.receiveShadow=true;owner.root.add(mesh);owner.stats.batches++;return mesh;
}
function environmentDrapeGeometryV16(){
 const positions=[],uv=[],indices=[],columns=20,rows=18;
 for(let j=0;j<=rows;j++)for(let i=0;i<=columns;i++){
  const u=i/columns,v=j/rows,spread=.33+v*.67;
  positions.push((u-.5)*spread*2,4.8*(1-v),Math.sin(u*Math.PI*8)*(.035+v*.1)+v*v*.45);
  uv.push(u*2,v*3);
 }
 for(let j=0;j<rows;j++)for(let i=0;i<columns;i++){const a=j*(columns+1)+i;indices.push(a,a+1,a+columns+1,a+1,a+columns+2,a+columns+1);}
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geometry.setIndex(indices);geometry.computeVertexNormals();return geometry;
}

function buildEnvironmentDirectionV16(parent,level,floors,regions){
 const owner=environmentOwnedStateV16(parent,level);owner.root.name='EnvironmentDirectionV16';parent.add(owner.root);
 for(const floor of floors||[]){const previous=floor.material;floor.material=environmentFloorMaterialV16(previous,level,owner);owner.restores.push(()=>floor.material=previous);}
 const stone=environmentMaterialV16(owner,level===2?'#8b9c8e':'#b6ad99'),dark=environmentMaterialV16(owner,level===2?'#485f59':'#41464a'),bronze=environmentMaterialV16(owner,'#b2905d','metal',.7),cloth=environmentMaterialV16(owner,level===3?'#273e42':'#393a42','cloth');
 const skirt=environmentFoundationGeometryV16(regions,level);owner.geometries.add(skirt);owner.stats.foundationVertices=skirt.attributes.position.count;const bank=new THREE.Mesh(skirt,stone);bank.material=stone.clone();bank.material.vertexColors=true;owner.materials.add(bank.material);bank.receiveShadow=true;bank.name='Continuous retaining foundations';owner.root.add(bank);owner.stats.batches++;
 if(level===1){
  // Carved profiles replace the same six collision footprints, not extra piers.
  const points=[[-.5,0],[-.5,.48],[-.43,.48],[-.38,.41],[-.30,.39],[.31,.39],[.37,.43],[.40,.49],[.48,.49],[.5,.43],[.5,0]].map(([y,r])=>new THREE.Vector2(r,y));
  const profile=new THREE.LatheGeometry(points,20);owner.geometries.add(profile);
  const baseObstacles=typeof baseWorld!=='undefined'&&baseWorld?.obstacles||((typeof journey==='undefined'||journey.level===1)?world.obstacles:[]);
  for(const obstacle of baseObstacles||[])if([12,23].includes(obstacle.x)&&[-9,-21,-31].includes(obstacle.z)&&obstacle.mesh){const previous=obstacle.mesh.geometry;obstacle.mesh.geometry=profile;owner.restores.push(()=>obstacle.mesh.geometry=previous);}
  // A real outer cloister wall: arches and alcoves stand beyond x=27, never
  // across the playable aisles or the three lamps. Overhead pieces cast no shadow.
  const parts=[];
  for(const z of [-9,-21,-31]){
   parts.push({pos:[29.4,3.8,z],size:[1.1,7.6,1.2],color:'#a9a18e'},{pos:[29.1,1.2,z],size:[1.7,2.4,2.8],color:'#858577'});
   const arch=new THREE.TorusGeometry(3.5,.22,7,30,Math.PI);parts.push({geo:arch,pos:[29.4,6,z+4.2],size:[1,1,1],rot:[0,Math.PI/2,0],color:'#b6ab93'});
  }
  environmentMergedV16(owner,parts,stone);for(const part of parts)if(part.geo)part.geo.dispose();
  // Interrupted votive wings give the arrival court an asymmetric human trace.
  environmentBatchV16(owner,environmentDrapeGeometryV16(),cloth,[{p:[-19.4,.3,10],s:[1.25,1.45,1],r:[0,1.1,-.08]},{p:[18.6,.3,23],s:[.6,.8,.7],r:[0,-.6,.05]}]);
  environmentBatchV16(owner,new THREE.CylinderGeometry(1,1,1,8),bronze,[{p:[-19.4,3.63,10.12],s:[.065,7.26,.065]},{p:[-19.4,7.26,10],s:[.055,1.1,.055],r:[0,1.1,Math.PI/2]},{p:[18.6,2.07,23.12],s:[.055,4.14,.055]},{p:[18.6,4.14,23],s:[.045,.6,.045],r:[0,-.6,Math.PI/2]}]);
  const offerings=[];for(let i=0;i<11;i++)offerings.push({p:[-18.2-i%3*.33,.18,6+i*.72],s:[.15,.36+(i%4)*.11,.15],r:[0,i*.7,0]});environmentBatchV16(owner,new THREE.CylinderGeometry(.8,1,1,7),bronze,offerings);
 }else if(level===2){
  // The inaccessible central water becomes a drowned observatory, while the
  // two existing side routes remain entirely open and mechanically identical.
  const rootParts=[];
  for(const side of [-1,1])for(const z of [-6,-21]){const geo=environmentCurveGeometryV16([[side*7,-2,z+5],[side*6,1.5,z+2],[side*4,5,z],[side*1.1,6.2,z-2]],.32);rootParts.push({geo,pos:[0,0,0],size:[1,1,1],color:'#5e7568'});}
  environmentMergedV16(owner,rootParts,dark);rootParts.forEach(p=>p.geo.dispose());
  const ring=new THREE.TorusGeometry(4.4,.18,8,64,Math.PI*1.7);owner.geometries.add(ring);const astrolabe=new THREE.Mesh(ring,bronze);astrolabe.position.set(1.2,.45,-17);astrolabe.rotation.set(.48,-.22,-.3);astrolabe.castShadow=false;owner.root.add(astrolabe);owner.stats.batches++;
  const reeds=[];for(const side of [-1,1])for(let i=0;i<14;i++){const z=1-i*2.25,x=side*(8.6+.35*Math.sin(i*1.7));reeds.push({p:[x,-.15,z],s:[.10,.55+(i%5)*.12,.10],r:[0,i,.15*side]});}environmentBatchV16(owner,new THREE.ConeGeometry(1,1,5),dark,reeds);
 }else{
  // Outboard cargo and tension ribs explain that the route rides a living hull.
  const cargo=[],rivets=[];
  for(const side of [-1,1])for(let i=0;i<5;i++){const x=side*(i<2?13.4:19.3),z=i<2?23-i*7:[-25,-33,-39][i-2];cargo.push({p:[x,.55,z],s:[1.1,1.1+(i%2)*.55,1.7],r:[0,side*.08,0]});}
  environmentBatchV16(owner,new THREE.BoxGeometry(1,1,1),cloth,cargo);
  for(const r of regions)for(const side of [-1,1])for(let z=r.z0+1;z<r.z1;z+=3.5)rivets.push({p:[side<0?r.x0-.18:r.x1+.18,-.19,z],s:[.12,.12,.08]});environmentBatchV16(owner,new THREE.SphereGeometry(1,6,4),bronze,rivets);
  const tension=[];for(const side of [-1,1])for(const z of [-27,-38]){const geo=environmentCurveGeometryV16([[side*18.25,-2,z],[side*20,1,z],[side*19,4.7,z]],.055);tension.push({geo,pos:[0,0,0],size:[1,1,1],color:'#bdad87'});}environmentMergedV16(owner,tension,bronze);tension.forEach(p=>p.geo.dispose());
 }
 owner.root.updateMatrixWorld(true);owner.regionKey=environmentRegionKeyV16(regions);owner.floorCount=(floors||[]).length;return owner;
}

function environmentRegionKeyV16(regions){return regions.map(r=>[r.x0,r.x1,r.z0,r.z1].join(',')).join(';');}
function environmentBaseRegionsV16(){return world.floors.map(f=>({x0:f.position.x-Math.abs(f.scale.x)*.5,x1:f.position.x+Math.abs(f.scale.x)*.5,z0:f.position.z-Math.abs(f.scale.z)*.5,z1:f.position.z+Math.abs(f.scale.z)*.5}));}
function disposeEnvironmentDirectionOwnerV16(owner){
 if(!owner)return;for(const restore of owner.restores)restore();owner.root.removeFromParent();for(const geometry of owner.geometries)geometry.dispose();for(const material of owner.materials)material.dispose();for(const texture of owner.textures)texture.dispose();
}
function disposeEnvironmentDirectionV16(){if(!environmentDirectionV16)return;disposeEnvironmentDirectionOwnerV16(environmentDirectionV16.base);disposeEnvironmentDirectionOwnerV16(environmentDirectionV16.journey);environmentDirectionV16=null;}
function initEnvironmentDirectionV16(){
 if(!world?.root||!presentation)return;
 if(environmentDirectionV16?.worldRoot===world.root)return;
 disposeEnvironmentDirectionV16();environmentDirectionV16={worldRoot:world.root,base:buildEnvironmentDirectionV16(world.root,1,world.floors,environmentBaseRegionsV16()),journey:null};
}
function updateEnvironmentDirectionV16(dt=0){
 initEnvironmentDirectionV16();if(!environmentDirectionV16)return;
 const state=environmentDirectionV16,chapter=typeof battle!=='undefined'&&battle?null:journey?.level>1?journey:null;
 if(state.journey?.parent!==chapter?.root||chapter&&state.journey&&(state.journey.regionKey!==environmentRegionKeyV16(world.regions)||state.journey.floorCount!==(chapter.floorMeshes||[]).length)){disposeEnvironmentDirectionOwnerV16(state.journey);state.journey=chapter?.root?buildEnvironmentDirectionV16(chapter.root,chapter.level,chapter.floorMeshes,world.regions):null;}
 const progress=campaign?.trials?.bells?.done?1:0;for(const uniform of state.base.progress)uniform.value=progress;
}
