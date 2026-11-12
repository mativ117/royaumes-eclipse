'use strict';
// Procedural art: no external models, images, post-processing or shadow maps.
function buildCathedralArt(THREE,scene,renderer,materials){
 const {stone,bronze,gold,dark}=materials;
 const detail=new THREE.Group(),haze=new THREE.Group(),glows=new THREE.Group();
 scene.add(detail,haze,glows);
 const block=new THREE.BoxGeometry(1,1,1),circle=new THREE.PlaneGeometry(1,1);
 function texture(draw,w=512,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;}
 let seed=1729;function random(){seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;}
 const paving=texture((g,w,h)=>{
  g.fillStyle='#7c7782';g.fillRect(0,0,w,h);
  for(let y=0;y<4;y++)for(let x=0;x<4;x++){
   const a=95+Math.floor(random()*35);g.fillStyle=`rgb(${a},${a-3},${a+6})`;g.fillRect(x*128+3,y*128+3,122,122);
   g.strokeStyle='#b6a69b55';g.strokeRect(x*128+6,y*128+6,116,116);
   g.strokeStyle='#24212b66';g.beginPath();let px=x*128+20+random()*90,py=y*128+10;g.moveTo(px,py);
   for(let i=0;i<4;i++){px+=(random()-.5)*25;py+=20;g.lineTo(px,py)}g.stroke();
  }
 });
 paving.wrapS=paving.wrapT=THREE.RepeatWrapping;paving.repeat.set(3,3);paving.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
 const masonry=texture((g,w,h)=>{g.fillStyle='#57515d';g.fillRect(0,0,w,h);for(let y=0;y<8;y++)for(let x=-1;x<5;x++){const px=x*128+(y%2)*64;g.fillStyle=`rgba(8,5,12,${.1+random()*.18})`;g.fillRect(px+2,y*64+2,124,60);g.strokeStyle='#c5a58333';g.strokeRect(px+4,y*64+4,120,56)}});
 masonry.wrapS=masonry.wrapT=THREE.RepeatWrapping;stone.map=masonry;stone.needsUpdate=true;
 const glowMap=texture((g,w,h)=>{const gradient=g.createRadialGradient(w/2,h/2,0,w/2,h/2,w/2);gradient.addColorStop(0,'rgba(255,225,161,1)');gradient.addColorStop(.12,'rgba(255,140,45,.7)');gradient.addColorStop(.45,'rgba(220,66,12,.14)');gradient.addColorStop(1,'rgba(160,30,0,0)');g.fillStyle=gradient;g.fillRect(0,0,w,h)},128,128);
 const fogMap=texture((g,w,h)=>{const grad=g.createRadialGradient(w/2,h/2,0,w/2,h/2,w/2);grad.addColorStop(0,'rgba(195,173,190,.6)');grad.addColorStop(.5,'rgba(160,135,170,.18)');grad.addColorStop(1,'rgba(160,135,170,0)');g.fillStyle=grad;g.fillRect(0,0,w,h)},128,128);
 const windowMap=texture((g,w,h)=>{
  const grad=g.createLinearGradient(0,0,0,h);grad.addColorStop(0,'#ffdb98');grad.addColorStop(.5,'#f87d2a');grad.addColorStop(1,'#5a2435');
  g.beginPath();g.arc(w/2,150,95,Math.PI,0);g.lineTo(w/2+95,h-12);g.lineTo(w/2-95,h-12);g.closePath();g.fillStyle=grad;g.fill();g.strokeStyle='#3c2530';g.lineWidth=10;g.stroke();g.lineWidth=6;
  for(const x of [85,128,171]){g.beginPath();g.moveTo(x,100);g.lineTo(x,h);g.stroke()}for(const y of [205,340]){g.beginPath();g.moveTo(20,y);g.lineTo(w-20,y);g.stroke()}
 },256,512);
 const arcGeo=new THREE.TorusGeometry(3,.27,6,24,Math.PI),archMaterial=new THREE.MeshStandardMaterial({color:'#685044',metalness:.5,roughness:.5,map:masonry});
 const windowMaterial=new THREE.MeshBasicMaterial({map:windowMap,transparent:true,side:THREE.DoubleSide,color:'#ffb474',depthWrite:false});
 for(const side of [-1,1])for(const z of [-12,-6,0,6,12]){
  const arch=new THREE.Mesh(arcGeo,archMaterial);arch.rotation.y=Math.PI/2;arch.position.set(side*16.6,7,z);scene.add(arch);
  const pane=new THREE.Mesh(circle,windowMaterial);pane.rotation.y=Math.PI/2;pane.position.set(side*17,5,z);pane.scale.set(4.2,7,1);scene.add(pane);
  const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:glowMap,color:'#ffa05a',transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,opacity:.6}));sprite.position.set(side*13.5,2.8,z);sprite.scale.set(5.5,7,1);glows.add(sprite);
 }
 // Repeated bands and inlays use instancing rather than one draw call per brick.
 const inlays=new THREE.InstancedMesh(block,bronze,36);let count=0;const dummy=new THREE.Object3D();
 for(const x of [-15,-12,12,15])for(let z=-16;z<=16;z+=4){dummy.position.set(x,.032,z);dummy.scale.set(.08,.035,3.7);dummy.updateMatrix();inlays.setMatrixAt(count++,dummy.matrix)}scene.add(inlays);
 // Large robed statues live outside the walkable arena and cannot obscure collision routes.
 const statueGeo=new THREE.ConeGeometry(1,1,7),headGeo=new THREE.SphereGeometry(1,10,8);
 for(const x of [-22,22]){
  const body=new THREE.Mesh(statueGeo,dark);body.position.set(x,5,-18);body.scale.set(3.2,10,3);detail.add(body);
  const head=new THREE.Mesh(headGeo,bronze);head.position.set(x,10,-18);head.scale.set(.85,1.2,.85);detail.add(head);
  const plinth=new THREE.Mesh(block,stone);plinth.position.set(x,.5,-18);plinth.scale.set(7,1,7);detail.add(plinth);
 }
 const fogs=[];
 for(let i=0;i<5;i++){const fog=new THREE.Mesh(circle,new THREE.MeshBasicMaterial({map:fogMap,transparent:true,opacity:.15,color:'#d2a9b7',depthWrite:false,side:THREE.DoubleSide}));fog.rotation.x=-Math.PI/2;fog.position.set((i%2?1:-1)*8,.14+i*.015,-12+i*6);fog.scale.set(19,13,1);haze.add(fog);fogs.push(fog)}
 const halo=new THREE.Mesh(new THREE.RingGeometry(2.7,2.78,64),new THREE.MeshBasicMaterial({color:'#c49a68',transparent:true,opacity:.45,side:THREE.DoubleSide}));halo.rotation.x=-Math.PI/2;halo.position.set(0,.035,-8);scene.add(halo);
 let time=0;
 return {paving,detail,haze,glows,
  setQuality(light){haze.visible=!light;detail.visible=!light;glows.children.forEach((o,i)=>o.visible=!light||i%2===0)},
  update(dt){time+=dt;fogs.forEach((o,i)=>{o.position.x=Math.sin(time*.12+i)*7;o.rotation.z=Math.sin(time*.06+i)*.2});glows.children.forEach((o,i)=>{o.material.opacity=.53+Math.sin(time*2.1+i)*.06})}
 };
}
