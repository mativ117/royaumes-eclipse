'use strict';
let stageAssets=null;
function mergedStageParts(parts){
 const positions=[],normals=[],colors=[];
 for(const part of parts){const g=(part.geo||boxGeo).clone().toNonIndexed(),m=new THREE.Matrix4().compose(new THREE.Vector3(...part.pos),new THREE.Quaternion().setFromEuler(new THREE.Euler(...(part.rot||[0,0,0]))),new THREE.Vector3(...part.size)),color=new THREE.Color(part.color||'#738187');g.applyMatrix4(m);const p=g.attributes.position,n=g.attributes.normal;
  for(let i=0;i<p.count;i++){positions.push(p.getX(i),p.getY(i),p.getZ(i));normals.push(n.getX(i),n.getY(i),n.getZ(i));colors.push(color.r,color.g,color.b);}g.dispose();
 }
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));g.computeBoundingSphere();return g;
}
function getStageAssets(){
 if(stageAssets)return stageAssets;
 const body={},weapon={},material={};
 const box=(pos,size,color)=>({pos,size,color}),orb=(pos,size,color)=>({geo:sphereGeo,pos,size,color});
 for(const role of ['warden','archer','sentinel','oracle','shade','porter','boss']){
  const heavy=['sentinel','porter','boss'].includes(role),caster=['oracle','shade'].includes(role),color=caster?'#6f668b':role==='archer'?'#667c79':heavy?'#73777d':'#6e6157',metal=heavy?'#bd9870':'#b2aaa0';
  const parts=[orb([0,.35,0],[heavy?.58:.43,.59,.34],color),box([0,-.15,0],[.68,.22,.48],metal),orb([0,.9,0],[.4,.38,.36],color),box([0,.84,-.33],[.52,.12,.08],'#121723')];
  if(caster){parts.push({geo:coneGeo,pos:[0,-.2,0],size:[.8,.7,.7],color},box([0,1.16,0],[.08,.55,.08],metal));}
  else for(const x of [-.24,.24])parts.push(orb([x,-.5,0],[.19,.44,.2],color),box([x,-.83,-.13],[.32,.17,.5],'#282b34'));
  if(heavy)for(const x of [-.68,.68])parts.push(orb([x,.62,0],[.27,.3,.4],metal));
  if(role==='archer')parts.push(box([.32,.35,.37],[.23,.95,.25],'#9f7856'));
  if(role==='boss')for(const x of [-.22,0,.22])parts.push(box([x,1.3,0],[.09,.5,.13],'#d9b277'));
  body[role]=mergedStageParts(parts);
  const w=role==='archer'?[box([0,-.48,-.2],[.1,1.6,.1],metal),{geo:new THREE.TorusGeometry(.7,.07,4,14,Math.PI),pos:[0,-.45,-.22],size:[1,1,1],rot:[0,Math.PI/2,Math.PI/2],color:metal}]:caster?[box([0,-.3,-.2],[.1,2.1,.1],metal),orb([0,.85,-.2],[.23,.23,.23],'#afd5df')]:[box([0,-.6,-.2],[.12,.7,.12],'#4a3732'),box([0,-1.25,-.2],[role==='warden'?.45:.18,1.1,.15],metal),box([0,-.78,-.2],[.55,.1,.16],metal)];
  weapon[role]=mergedStageParts(w);
  for(const part of w)if(part.geo&&part.geo!==sphereGeo&&part.geo!==coneGeo)part.geo.dispose();
  material[role]=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.63,metalness:heavy?.48:.15});
 }
 stageAssets={body,weapon,material};return stageAssets;
}
function dressEnemy(e){
 if(e.type==='anchor')return;const a=getStageAssets();e.robe.geometry=a.body[e.type]||a.body.warden;e.robe.userData.ownedGeometry=false;e.root.children[1].visible=false;
 if(e.type==='shade'){e.robe.material.vertexColors=true;e.robe.material.color.set('#ffffff');e.roleMaterial=e.robe.material;}
 else e.robe.material=e.roleMaterial=a.material[e.type]||a.material.warden;
 const weapon=new THREE.Mesh(a.weapon[e.type]||a.weapon.warden,a.material[e.type]||a.material.warden);e.rig.arms[1].add(weapon);if(!['archer','oracle','shade'].includes(e.type))weapon.position.y=.35;e.rig.weapon=weapon;
 e.home={x:e.x,z:e.z};e.awareness=0;e.patrolSide=0;e.idleFacing=e.root.rotation.y;
}
function initStageCraft(){
 const root=new THREE.Group();world.root.add(root);const detail=new THREE.Group();art.detail.add(detail);const dummy=new THREE.Object3D();
 function batch(geo,mat,items,parent=root){const o=new THREE.InstancedMesh(geo,mat,items.length);items.forEach((q,i)=>{dummy.position.set(...q.p);dummy.rotation.set(...(q.r||[0,0,0]));dummy.scale.set(...q.s);dummy.updateMatrix();o.setMatrixAt(i,dummy.matrix);if(q.c)o.setColorAt(i,new THREE.Color(q.c));});parent.add(o);return o;}
 const bronzeMat=new THREE.MeshStandardMaterial({color:'#846b53',metalness:.55,roughness:.62}),stoneMat=new THREE.MeshStandardMaterial({color:'#514b59',roughness:.92}),bookMat=new THREE.MeshStandardMaterial({color:'#ffffff',roughness:.9});
 const posts=[],rails=[],books=[],fins=[];
 for(const x of [-27.7,27.7])for(let z=-34;z<0;z+=3){posts.push({p:[x,.9,z],s:[.22,1.8,.22]});rails.push({p:[x,1.5,z+1.5],s:[.12,.12,3]});}
 // Shelves outside the walkable perimeter: the archive has depth without hidden blockers.
 for(const x of [-58,-47,-36,-25]){
  for(const edge of [-4,4])posts.push({p:[x+edge,2.5,-75.2],s:[.4,5,.8]});
  for(let y=.6;y<5;y+=1.05){rails.push({p:[x,y,-75.2],s:[8.4,.14,1]});for(let k=0;k<12;k++)books.push({p:[x-3.5+k*.61,y+.4,-75.05],s:[.35,.62+(k%3)*.1,.5],r:[0,0,(k%4-1)*.04],c:['#715367','#8d795b','#446b75'][k%3]});}
 }
 for(const x of [26,38,50,61]){posts.push({p:[x,3,-75.5],s:[.8,6,.8]});fins.push({p:[x,4.7,-75.5],s:[.35,1.4,.35],r:[0,0,.35]});}
 // Low architectural boundaries and vertical landmarks frame the otherwise open platforms.
 batch(boxGeo,bronzeMat,posts);batch(boxGeo,stoneMat,rails);batch(boxGeo,bookMat,books,detail);batch(boxGeo,bronzeMat,fins);
 const ribs=[];for(const x of [27,39,51,61])ribs.push({p:[x,5.5,-75.5],s:[2.4,2.4,1]});
 batch(new THREE.TorusGeometry(1,.065,5,18,Math.PI),bronzeMat,ribs);
 const pipes=[];for(const z of [-46,-54,-62,-70])pipes.push({p:[63.2,2,z],s:[.32,4,.32]},{p:[63.2,4,z],s:[1.2,1.2,1.2],r:[0,0,Math.PI/2]});batch(cylGeo,bronzeMat,pipes,detail);
 // Furnaces sit inside existing cover footprints; geometry and navigation still agree.
 for(const o of world.obstacles)if((o.x===31&&o.z===-55)||(o.x===45&&o.z===-61)){o.mesh.position.y=.7;o.mesh.scale.y=1.4;}
 const bowls=[{p:[31,1.45,-55],s:[1.2,.22,1.2]},{p:[45,1.45,-61],s:[1.2,.22,1.2]}];batch(cylGeo,bronzeMat,bowls);
 const coals=bowls.map(q=>({p:[q.p[0],1.68,q.p[2]],s:[.95,.08,.95]}));const embers=batch(cylGeo,new THREE.MeshBasicMaterial({color:'#dc874b'}),coals);
 const canopy=[];for(const x of [-31,-34])for(let z=-2;z>-34;z-=4)canopy.push({p:[x,2,z],s:[1.4,2.2,1.4],c:z%3?'#356566':'#496f68'});batch(new THREE.IcosahedronGeometry(1,0),bookMat,canopy,detail);
 world.stage={root,embers};
}
function updateStageCraft(dt){
 if(!world.stage)return;world.stage.embers.material.color.setRGB(.7+Math.sin(t*1.8)*.04,.22,.05);
}
// Patrols remain in the same small encounter; perception respects solid cover.
function perceiveEnemy(e,dt){
 if(!e.home||e.alert>0||e.mode!=='idle'||distance(e,p)<3){e.awareness=1;return true;}
 const seen=distance(e,p)<15&&clearStrikeLine(e.x,e.z);
 e.awareness=clamp(e.awareness+(seen?dt/0.7:-dt*.65),0,1);
 if(e.awareness>=1){e.alert=8;return true;}
 if(seen){e.root.rotation.y+=clamp(wrap(Math.atan2(e.x-p.x,e.z-p.z)-e.root.rotation.y),-dt,dt);}
 else if(['warden','archer'].includes(e.type)){
  const target={x:e.home.x+(e.patrolSide?1.2:-1.2),z:e.home.z};
  if(distance(e,target)<.35)e.patrolSide=1-e.patrolSide;
  else steerToward(e,target,dt,.7);
  e.root.position.set(e.x,0,e.z);
 }
 return false;
}
