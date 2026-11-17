'use strict';
function ensureSurfaceUv(geometry){
 if(geometry.attributes.uv)return;const p=geometry.attributes.position,n=geometry.attributes.normal,uv=new Float32Array(p.count*2);for(let i=0;i<p.count;i++){const nx=Math.abs(n?.getX(i)||0),ny=Math.abs(n?.getY(i)||0),nz=Math.abs(n?.getZ(i)||0);uv[i*2]=(nx>ny&&nx>nz?p.getZ(i):p.getX(i))*.4;uv[i*2+1]=(ny>nx&&ny>nz?p.getZ(i):p.getY(i))*.4;}geometry.setAttribute('uv',new THREE.BufferAttribute(uv,2));
}
function initEnvironmentFinish(){
 const root=new THREE.Group();world.root.add(root);world.finishRoot=root;const owned=presentation.worldTextures;
 const wall=new THREE.MeshStandardMaterial({color:'#9b9182',roughness:1});applyPbrSurface(wall,'masonry',1,1,owned);const ledge=wall.clone();ledge.color.set('#ccc0aa');const plinth=wall.clone();plinth.color.set('#6f6c65');
 // Existing foundations and stone covers receive authored, tiled materials too.
 const oldStoneMap=stone.map,cache=new Map();world.root.traverse(object=>{if(!object.isMesh||object===root)return;const old=object.material;if(Array.isArray(old)||!old?.isMeshStandardMaterial)return;if(old===dark||old===stone||(oldStoneMap&&old.map===oldStoneMap)){if(!cache.has(old)){const material=old.clone();material.color.set(old===dark?'#655e53':'#b3a798');applyPbrSurface(material,'masonry',2,2,owned);cache.set(old,material);}object.material=cache.get(old);ensureSurfaceUv(object.geometry);}});
 const rims=[],supports=[];for(const region of world.regions)for(const [axis,sign]of [['x',-1],['x',1],['z',-1],['z',1]]){
  const start=axis==='x'?region.z0:region.x0,end=axis==='x'?region.z1:region.x1,count=Math.ceil((end-start)/2.5),span=(end-start)/count;
  for(let i=0;i<count;i++){const q=start+(i+.5)*span,x=axis==='x'?(sign<0?region.x0:region.x1):q,z=axis==='z'?(sign<0?region.z0:region.z1):q,ox=x+(axis==='x'?sign*.08:0),oz=z+(axis==='z'?sign*.08:0);if(world.regions.some(r=>r!==region&&ox>r.x0&&ox<r.x1&&oz>r.z0&&oz<r.z1))continue;
   rims.push({p:[x,.025,z],s:axis==='x'?[.28,.16,span]:[span,.16,.28]});if(i%2===0)supports.push({p:[x,-2.35,z],s:axis==='x'?[.65,3.5,.7]:[.7,3.5,.65]});
  }
 }
 const batch=(geometry,material,items)=>{const object=new THREE.InstancedMesh(geometry,material,items.length),dummy=new THREE.Object3D();for(let i=0;i<items.length;i++){dummy.position.set(...items[i].p);dummy.scale.set(...items[i].s);dummy.rotation.set(...(items[i].r||[0,0,0]));dummy.updateMatrix();object.setMatrixAt(i,dummy.matrix);}object.receiveShadow=true;object.castShadow=false;root.add(object);return object;};
 batch(boxGeo,ledge,rims);batch(boxGeo,plinth,supports);
 // Archive recesses sit outside the walkable perimeter, framing existing routes.
 const shelves=[],backs=[];for(const z of [-48,-58,-68]){backs.push({p:[-62.35,2.1,z],s:[.3,4.2,6]});for(const y of [.3,1.3,2.3,3.3])shelves.push({p:[-62.1,y,z],s:[.8,.12,6.2]});}
 batch(boxGeo,plinth,backs);batch(boxGeo,wall,shelves);
 // The forge silhouettes occupy the footprints of the existing solid furnaces.
 const forge=new THREE.MeshStandardMaterial({color:'#75695b',metalness:.6,roughness:.65});for(const [x,z]of [[31,-55],[45,-61]]){const c=world.obstacles.find(o=>o.x===x&&o.z===z);if(!c?.mesh)continue;const chimney=new THREE.Mesh(new THREE.CylinderGeometry(.5,.8,2.0,16,1,true),forge);chimney.position.set(x,2.5,z);chimney.castShadow=true;root.add(chimney);const collar=new THREE.Mesh(new THREE.TorusGeometry(.65,.08,8,24),forge);collar.rotation.x=Math.PI/2;collar.position.set(x,2.1,z);root.add(collar);registerLandmarkOcclusion([{root:chimney},{root:collar}]);}
 const abyssMaterial=new THREE.MeshStandardMaterial({color:'#171b1b',roughness:1});applyPbrSurface(abyssMaterial,'masonry',12,18,owned);world.abyss.material.dispose();world.abyss.material=abyssMaterial;world.abyss.position.y=-6.8;
 world.materialFinish={rims:rims.length,supports:supports.length,photographic:true};
}
