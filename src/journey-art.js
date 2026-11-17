'use strict';
// Shared sculpted silhouettes and instancing keep the new chapters detailed without hundreds of draw calls.
function makeJourneyRock(){const g=new THREE.IcosahedronGeometry(1,quality==='light'?1:2),p=g.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),noise=1+.16*Math.sin(x*17+z*13+y*7);p.setXYZ(i,x*noise,y*(.8+.25*Math.sin(z*11)),z*noise);}for(let i=0;i<p.count;i++){const n=new THREE.Vector3(p.getX(i),p.getY(i),p.getZ(i)).normalize();g.attributes.normal.setXYZ(i,n.x,n.y,n.z);}journey.geometries.push(g);return g;}
function makeJourneyTree(){
 const parts=[{geo:new THREE.CylinderGeometry(.10,.36,5.6,9),pos:[0,2.8,0],size:[1,1,1],color:'#414447'}];
 for(const side of [-1,1])for(let i=0;i<4;i++){const length=2.8-i*.35,angle=side*(.8+i*.1);parts.push({geo:new THREE.CylinderGeometry(.025,.12,length,6),pos:[side*(.8+i*.12),3.5+i*.5,Math.sin(i*2)*.7],size:[1,1,1],rot:[.25,0,angle],color:'#53504a'});}
 const geometry=mergedStageParts(parts);for(const part of parts)part.geo.dispose();journey.geometries.push(geometry);return geometry;
}
function dressJourneyEnvironment(){
 const root=new THREE.Group(),detail=new THREE.Group();journey.root.add(root);root.add(detail);journey.artRoot=root;journey.detailRoot=detail;
 journey.roughRails&&(journey.roughRails.visible=false);journey.roughRock&&(journey.roughRock.visible=false);journey.roughCanopy&&(journey.roughCanopy.visible=false);
 const rock=makeJourneyRock(),stone=journeyMaterial('#7a7d75',.1,.93),darkStone=journeyMaterial('#424c51',.15,.8),copper=journeyMaterial('#9d7c50',.6,.45),ivory=journeyMaterial('#c7bc9f',.1,.8),wood=journeyMaterial('#605145',.05,.9,'wood');
 const edges=[],posts=[],ropes=[],pavers=[],cliffs=[],trees=[],leaves=[];let seed=1937;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 for(const region of world.regions){
  for(const [axis,sign]of[['x',-1],['x',1],['z',-1],['z',1]]){
   const start=axis==='x'?region.z0:region.x0,end=axis==='x'?region.z1:region.x1,span=end-start,count=Math.max(1,Math.floor(span/3));
   for(let i=0;i<count;i++){const q=start+(i+.5)*span/count,x=axis==='x'?(sign<0?region.x0:region.x1):q,z=axis==='z'?(sign<0?region.z0:region.z1):q,outX=x+(axis==='x'?sign*.1:0),outZ=z+(axis==='z'?sign*.1:0);
    if(world.regions.some(r=>r!==region&&outX>r.x0&&outX<r.x1&&outZ>r.z0&&outZ<r.z1))continue;
    cliffs.push({p:[x,-.9-random()*.6,z],s:[1.2+random(),1.3,1.2+random()],r:[random()*.1,random()*3,0]});
    if(journey.level===3){posts.push({p:[x,.65,z],s:[.13,1.3,.13]});const next=q+span/count*.45,px=axis==='x'?x:next,pz=axis==='z'?z:next;ropes.push({p:[px,1,z===pz?z:pz],s:axis==='x'?[.05,.05,span/count]:[span/count,.05,.05]});}
    else edges.push({p:[x,.12,z],s:[1.1,.25,1.1],r:[0,random(),0]});
   }
  }
  // Small paving fragments give the walkable ground a readable scale.
  for(let z=region.z0+1;z<region.z1;z+=1.8)for(let x=region.x0+1;x<region.x1;x+=2.2)if(random()>.25)pavers.push({p:[x+(random()-.5)*.3,.015,z+(random()-.5)*.3],s:[.7+random()*.6,.025,.6+random()*.5],r:[0,(random()-.5)*.08,0]});
 }
 journeyBatch(rock,darkStone,cliffs);journeyBatch(rock,stone,edges);journeyBatch(boxGeo,wood,posts);journeyBatch(boxGeo,copper,ropes,false);const paving=journeyBatch(boxGeo,journey.level===2?stone:ivory,pavers,false);detail.add(paving);journey.paving=paving;
 for(const arch of journey.archesData||[])for(const side of [-1,1]){const x=arch.p[0]+side*arch.s[0],z=arch.p[2];if(!world.onGround(x,z,.1))continue;journeyBox(x,arch.p[1]/2,z,.55,arch.p[1],.7,copper,true);journeyBox(x,.2,z,1.3,.4,1.3,ivory,true);}
 for(const node of journey.nodes){
  const base=mesh(cylGeo,ivory,0,.16,0,.92,.3,.92,node.root);base.castShadow=true;const band=mesh(ringGeo,copper,0,.33,0,.88,.88,.88,node.root);band.rotation.x=-Math.PI/2;
  for(const side of [-1,1])mesh(boxGeo,copper,side*.58,.55,0,.06,.55,.1,node.root);
  if(node.id==='rain'){node.crystal.geometry=coneGeo;node.crystal.rotation.z=Math.PI;node.crystal.scale.set(.35,.5,.35);}
  if(node.id==='silence'){node.crystal.visible=false;for(const side of [-1,1])mesh(boxGeo,node.material,side*.16,1.25,0,.08,.7,.08,node.root);mesh(boxGeo,node.material,0,.93,0,.4,.08,.08,node.root);}
  if(node.id==='ember'){node.crystal.geometry=rock;node.crystal.scale.set(.26,.5,.26);}
  if(node.kind==='camp'){const canopy=mesh(new THREE.TorusGeometry(.8,.04,5,24,Math.PI),copper,0,1.55,0,1,1,1,node.root);journey.geometries.push(canopy.geometry);}
 }
 if(journey.level===2){
  const treeGeometry=makeJourneyTree(),treeMaterial=journeyMaterial('#ffffff',.03,.95,'wood'),leafMaterial=journeyMaterial('#a24132',.03,.9);treeMaterial.vertexColors=true;
  for(const side of [-1,1])for(let i=0;i<16;i++){const z=22-i*8.1,x=side*(i<8?30.5:27.8),scale=.8+random()*.55;trees.push({p:[x,0,z],s:[scale,scale,scale],r:[0,random()*6,side*.07]});for(let j=0;j<23;j++){const a=random()*Math.PI*2,r=1+random()*2.4;leaves.push({p:[x+Math.cos(a)*r*scale,(4.7+random()*1.6)*scale,z+Math.sin(a)*r*scale],s:[.8+random(),.35+random()*.45,.7+random()]});}}
  journey.treeTransforms=trees;journeyBatch(treeGeometry,treeMaterial,trees);journey.foliage=journeyBatch(rock,leafMaterial,leaves,false);
  const columns=[];for(const side of [-1,1])for(let i=0;i<7;i++)columns.push({p:[side*(21+i*.6),2.5,-85-i*3],s:[.5,5+i*.3,.5],r:[0,0,side*.08]});journeyBatch(cylGeo,ivory,columns);
  const astrolabeGeometry=new THREE.TorusGeometry(8,.15,8,64);journey.geometries.push(astrolabeGeometry);for(const side of [-1,1]){const disk=mesh(astrolabeGeometry,copper,side*24,8,-63,1,1,1,root);disk.rotation.y=side*.5;disk.rotation.z=side*.2;}
  const mountainItems=[];for(let i=0;i<25;i++)mountainItems.push({p:[Math.sin(i*2.3)*65,-7,-145-i*3],s:[10+random()*13,18+random()*18,9+random()*14],r:[0,i,0]});journeyBatch(rock,darkStone,mountainItems,false);
 }else{
  // A continuous tapered body and segmented armor replace the block silhouette below the decks.
  const vertices=[],indices=[];for(let i=0;i<=24;i++){const f=i/24,z=30-f*153,rx=5+7*Math.sin(Math.PI*Math.min(.99,f*.9+.05)),ry=3.5+2*Math.sin(f*Math.PI);for(let j=0;j<16;j++){const a=j/16*Math.PI*2;vertices.push(Math.cos(a)*rx,-7+Math.sin(a)*ry,z);}}
  for(let i=0;i<24;i++)for(let j=0;j<16;j++){const a=i*16+j,b=i*16+(j+1)%16,c=a+16,d=b+16;indices.push(a,c,b,b,c,d);}const bodyGeometry=new THREE.BufferGeometry();bodyGeometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));bodyGeometry.setIndex(indices);bodyGeometry.computeVertexNormals();journey.geometries.push(bodyGeometry);const body=mesh(bodyGeometry,darkStone,0,0,0,1,1,1,root);body.castShadow=true;
  const plates=[];for(let z=18;z>-110;z-=7)for(const side of [-1,1])plates.push({p:[side*10,-1.6,z],s:[1.8,.6,3],r:[0,side*.1,side*.3]});journeyBatch(rock,ivory,plates);
  const brow=[];for(const side of [-1,1]){brow.push({p:[side*7,-.4,-116],s:[4,1.4,4],r:[0,side*.3,0]});const horn=mesh(coneGeo,copper,side*9,-.8,-119,.8,3,.8,root);horn.rotation.x=-.8;mesh(sphereGeo,classProjectileMaterial('eclipse'),side*7,-1,-120,.55,.35,.65,root);}journeyBatch(rock,ivory,brow);
  const flags=[];for(const side of [-1,1])for(const z of [-25,-42,-87,-104]){const x=side*(z<-80?20:17);journeyBox(x,2.3,z,.09,4.6,.09,copper);flags.push({p:[x+side*.8,3.1,z],s:[1.4,2,.035],r:[0,side*.2,side*.07]});}journey.banners=journeyBatch(boxGeo,journeyMaterial('#753c36',.1,.8,'cloth'),flags,false);
 }
 journey.artRoot.userData.completeArt=true;
}
