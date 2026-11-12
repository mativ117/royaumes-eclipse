'use strict';
// A connected world. Rectangles describe real walkable ground, not invisible rooms.
function buildCampaign(THREE,scene,renderer,m){
 const root=new THREE.Group();scene.add(root);
 const boxGeo=new THREE.BoxGeometry(1,1,1),cylinder=new THREE.CylinderGeometry(1,1,1,10),sphere=new THREE.SphereGeometry(1,10,7);
 const regions=[
  {x0:-17,x1:17,z0:0,z1:29,color:'#b9a69d',name:'Atrium'},
  {x0:-27,x1:-8,z0:-10,z1:0,color:'#819a96',name:'Jardins'},
  {x0:-24,x1:-16,z0:-26,z1:-10,color:'#879a98',name:'Pont'},
  {x0:-27,x1:-8,z0:-35,z1:-26,color:'#819a96',name:'Jardins'},
  {x0:8,x1:27,z0:-35,z1:0,color:'#ad9283',name:'Cloître'},
  {x0:-27,x1:27,z0:-42,z1:-35,color:'#9b929d',name:'Croisée'},
  {x0:-14,x1:14,z0:-74,z1:-42,color:'#95a5ae',name:'Nef'},
  {x0:-62,x1:-14,z0:-74,z1:-42,color:'#8e92b4',name:'Archives'},
  {x0:14,x1:62,z0:-74,z1:-42,color:'#b99b79',name:'Forge'},
  {x0:-23,x1:23,z0:-111,z1:-74,color:'#b79d8d',name:'Cour'}
 ];
 let seed=473;function rand(){seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;}
 function tex(draw,size=512){const c=document.createElement('canvas');c.width=c.height=size;draw(c.getContext('2d'),size);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;}
 const paving=tex((g,n)=>{g.fillStyle='#b9b2b8';g.fillRect(0,0,n,n);for(let y=0;y<4;y++)for(let x=0;x<4;x++){const v=145+rand()*45;g.fillStyle=`rgb(${v},${v-5},${v+3})`;g.fillRect(x*128+3,y*128+3,122,122);g.strokeStyle='#554b5a88';g.beginPath();let px=x*128+rand()*100,py=y*128+10;g.moveTo(px,py);for(let k=0;k<4;k++){px+=(rand()-.5)*25;py+=24;g.lineTo(px,py)}g.stroke();g.strokeStyle='#e6d5bb66';g.strokeRect(x*128+5,y*128+5,118,118)}});
 paving.wrapS=paving.wrapT=THREE.RepeatWrapping;paving.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
 function block(x,y,z,w,h,d,mat=m.stone,parent=root){const o=new THREE.Mesh(boxGeo,mat);o.position.set(x,y,z);o.scale.set(w,h,d);parent.add(o);return o;}
 const ground=[];
 for(const r of regions){const texture=paving.clone();texture.repeat.set((r.x1-r.x0)/12,(r.z1-r.z0)/12);const mat=new THREE.MeshStandardMaterial({color:r.color,map:texture,roughness:.65,metalness:.2});const f=block((r.x0+r.x1)/2,-.45,(r.z0+r.z1)/2,r.x1-r.x0,.9,r.z1-r.z0,mat);ground.push(f);block((r.x0+r.x1)/2,-1.5,(r.z0+r.z1)/2,r.x1-r.x0,2,r.z1-r.z0,m.dark);}
 const wallTexture=tex((g,n)=>{g.fillStyle='#a89ca9';g.fillRect(0,0,n,n);for(let y=0;y<8;y++)for(let x=-1;x<5;x++){g.fillStyle='#665d6d';g.fillRect(x*128+(y%2)*64+3,y*64+3,122,58);}});m.stone.map=wallTexture;m.stone.color.set('#85788a');m.stone.needsUpdate=true;
 const pillarGeo=new THREE.CylinderGeometry(.5,.54,1,10);
 const colliders=[],gateMeshes=[];
 function obstacle(x,z,w,d,h=2.5,mat=m.stone,gate=''){const o=block(x,h/2,z,w,h,d,mat);if(!gate&&w<4&&d<4&&h>=3)o.geometry=pillarGeo;if(gate){o.material=new THREE.MeshBasicMaterial({color:'#efa456',transparent:true,opacity:.18,depthWrite:false});for(let i=0;i<10;i++){const bar=new THREE.Mesh(boxGeo,m.gold);bar.position.set(-.46+i*.102,0,0);bar.scale.set(.008,1,.3);o.add(bar);}}colliders.push({x,z,w,d,gate,mesh:o});if(gate)gateMeshes.push(o);return o;}
 // Intentional cover, landmarks and alternate lanes; no repeated identical arenas.
 for(const x of [-10,10])obstacle(x,13,2.2,3,3.2);
 obstacle(-17.5,-5,19,.55,3.8,m.bronze,'pact');obstacle(17.5,-5,19,.55,3.8,m.bronze,'pact');
 for(const z of [-9,-21,-31]){obstacle(12,z,2.5,3.5,4);obstacle(23,z,2.5,3.5,4);}
 obstacle(-21,-29,3,1.7,1.3,m.bronze);
 for(const z of [-46,-58])for(const x of [-9,9])obstacle(x,z,2.5,2.5,5);
 obstacle(0,-43,28,.5,3,m.bronze,'ritual-entry');
 for(const side of [-1,1]){obstacle(side*38,-42,48,.5,3,m.bronze,'ritual-entry');obstacle(side*14,-65,.7,18,3.5);obstacle(side*14,-46,.7,8,3.5);}
 for(const x of [-50,-34])for(const z of [-49,-64])obstacle(x,z,2.2,7,3.8);
 for(const [x,z]of[[31,-55],[45,-61]])obstacle(x,z,2.8,2.8,3);
 obstacle(0,-69,28,.7,4,m.bronze,'seals');
 for(const side of [-1,1])obstacle(side*38,-74,48,.5,4,m.bronze,'seals');
 obstacle(0,-74,46,.45,3,m.bronze,'boss');
 for(const x of [-12,12])obstacle(x,-88,2.5,3,3.7);
 const abyss=new THREE.Mesh(new THREE.PlaneGeometry(100,180),new THREE.MeshBasicMaterial({color:'#261325',transparent:true,opacity:.8}));abyss.rotation.x=-Math.PI/2;abyss.position.set(0,-8,-40);root.add(abyss);
 const ornament=new THREE.Group(),haze=new THREE.Group(),glows=new THREE.Group();root.add(ornament,haze,glows);
 const glowMap=tex((g,n)=>{const q=g.createRadialGradient(n/2,n/2,0,n/2,n/2,n/2);q.addColorStop(0,'rgba(255,229,175,.9)');q.addColorStop(.2,'rgba(255,136,39,.35)');q.addColorStop(1,'rgba(255,90,0,0)');g.fillStyle=q;g.fillRect(0,0,n,n)},128);
 for(const [x,z] of [[-14,22],[14,22],[-25,-2],[25,-2],[-25,-31],[25,-31],[-11,-40],[11,-40],[-11,-64],[11,-64],[-20,-80],[20,-80],[-20,-104],[20,-104]]){
  const post=new THREE.Mesh(cylinder,m.bronze);post.scale.set(.45,1.8,.45);post.position.set(x,.9,z);root.add(post);
  const flame=new THREE.Mesh(sphere,m.gold);flame.scale.set(.15,.65,.15);flame.position.set(x,2.1,z);root.add(flame);
  const glow=new THREE.Sprite(new THREE.SpriteMaterial({map:glowMap,color:'#ffac66',transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,opacity:.65}));glow.scale.set(7,8,1);glow.position.set(x,2.3,z);glows.add(glow);
 }
 // Exterior architecture on the cloister; the garden side stays open over the abyss.
 const arch=new THREE.TorusGeometry(5,.35,6,24,Math.PI);
 for(const z of [-6,-18,-30]){const a=new THREE.Mesh(arch,m.bronze);a.rotation.y=Math.PI/2;a.position.set(28,6,z);root.add(a);for(const dz of [-5,5])block(28,3,z+dz,1.1,6,1.1,m.stone);}
 const greatArch=new THREE.TorusGeometry(17,.6,7,32,Math.PI);
 for(const z of [-73,-91,-109]){const a=new THREE.Mesh(greatArch,m.bronze);a.position.set(0,7,z);root.add(a);for(const x of [-17,17])block(x,3.5,z,1.6,7,1.6,m.stone);}
 // Instanced crystals and broken masonry make each route recognizable at low cost.
 const crystals=new THREE.InstancedMesh(new THREE.ConeGeometry(1,1,5),new THREE.MeshStandardMaterial({color:'#527f80',emissive:'#123a3f',roughness:.6}),32),dummy=new THREE.Object3D();
 for(let i=0;i<32;i++){dummy.position.set(-29-rand()*6,rand()*1.5,-rand()*36);dummy.rotation.set(0,rand()*6,(rand()-.5)*.8);dummy.scale.set(.5+rand(),2+rand()*6,.5+rand());dummy.updateMatrix();crystals.setMatrixAt(i,dummy.matrix)}ornament.add(crystals);
 const rubble=new THREE.InstancedMesh(boxGeo,m.stone,24);
 for(let i=0;i<24;i++){dummy.position.set(28+rand()*5,-.3,-rand()*37);dummy.rotation.set(rand()*.5,rand()*3,rand()*.5);dummy.scale.set(1+rand()*2,1+rand()*2,1+rand()*2);dummy.updateMatrix();rubble.setMatrixAt(i,dummy.matrix)}ornament.add(rubble);
 const fogMap=tex((g,n)=>{const q=g.createRadialGradient(n/2,n/2,0,n/2,n/2,n/2);q.addColorStop(0,'rgba(174,175,205,.5)');q.addColorStop(1,'rgba(145,140,175,0)');g.fillStyle=q;g.fillRect(0,0,n,n)},128);
 for(const z of [14,-13,-35,-55,-83,-102]){const f=new THREE.Mesh(new THREE.PlaneGeometry(36,22),new THREE.MeshBasicMaterial({map:fogMap,transparent:true,opacity:.17,depthWrite:false,side:THREE.DoubleSide}));f.rotation.x=-Math.PI/2;f.position.set(0,.12,z);haze.add(f);}
 const particles=new Float32Array(160*3);for(let i=0;i<160;i++){particles[i*3]=(rand()-.5)*70;particles[i*3+1]=rand()*17;particles[i*3+2]=25-rand()*150;}
 const dustGeo=new THREE.BufferGeometry();dustGeo.setAttribute('position',new THREE.BufferAttribute(particles,3));const dust=new THREE.Points(dustGeo,new THREE.PointsMaterial({color:'#ffc187',size:.07,transparent:true,opacity:.6}));root.add(dust);
 const halo=new THREE.Mesh(new THREE.TorusGeometry(7,.17,8,72),m.gold);halo.position.set(0,16,-116);root.add(halo);const eclipse=new THREE.Mesh(new THREE.CircleGeometry(6.8,64),new THREE.MeshBasicMaterial({color:'#080a12'}));eclipse.position.set(0,16,-116.1);root.add(eclipse);
 const exit=new THREE.Group();exit.position.set(0,0,-107);root.add(exit);for(const x of [-2,2])block(x,2.5,0,.4,5,.8,m.bronze,exit);block(0,5,0,4.4,.4,.8,m.bronze,exit);block(0,2.5,0,3.6,4.8,.1,m.gold,exit);exit.visible=false;
 let time=0;
 return {root,regions,obstacles:colliders,exit,dust,halo,floor:ground[0],
  onGround(x,z,r=.48){return [[x-r,z-r],[x+r,z-r],[x-r,z+r],[x+r,z+r]].every(([a,b])=>regions.some(q=>a>=q.x0&&a<=q.x1&&b>=q.z0&&b<=q.z1));},
  zoneAt(x,z){return x<-14&&z<-42&&z>=-74?'Archives du Reflet':x>14&&z<-42&&z>=-74?'Forge du brasier':z<-74?'Cour du Veilleur':z<-42?'Nef des marées':z<-28?'Croisée des pèlerins':z<0?(x<0?'Jardins suspendus':'Cloître des cendres'):'Atrium des serments';},
  art:{haze,detail:ornament,glows,setQuality(light){haze.visible=!light;ornament.visible=!light;dust.visible=!light;glows.children.forEach((o,i)=>o.visible=!light||i%2===0)},update(dt){time+=dt;haze.children.forEach((f,i)=>f.position.x=Math.sin(time*.12+i)*4);glows.children.forEach((g,i)=>g.material.opacity=.58+Math.sin(time*2+i)*.05)}}
 };
}
