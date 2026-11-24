'use strict';
// Original models and textures for the world: painterly stone, copper mechanisms,
// wind in living borders. No third-party game assets are embedded.
let artDirection=null,craftAssets=null;
function makeArtTexture(draw,size=256){const c=document.createElement('canvas');c.width=c.height=size;draw(c.getContext('2d'),size);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;}
function makeCraftAssets(){
 if(craftAssets)return craftAssets;
 const pieces={},stoneColor='#514d56',copper='#a48661',darkMetal='#343942';
 const part=(geo,pos,size,color=copper,rot=[0,0,0])=>({geo,pos,size,color,rot});
 const base=[part(cylGeo,[0,.16,0],[.85,.3,.85],stoneColor),part(cylGeo,[0,.36,0],[.64,.12,.64],copper),part(cylGeo,[0,.63,0],[.33,.6,.33],stoneColor)];
 pieces.pact=mergedStageParts([...base,part(new THREE.TorusGeometry(.65,.1,6,24),[0,1,0],[1,.55,1],copper,[Math.PI/2,0,0])]);
 pieces.lamp=mergedStageParts([...base,part(cylGeo,[0,1.1,0],[.19,.6,.19],darkMetal),part(cylGeo,[0,2.32,0],[.65,.16,.65],copper),...[-1,1].map(x=>part(boxGeo,[x*.4,1.87,0],[.06,.95,.06],copper))]);
 pieces.fresco=mergedStageParts([part(cylGeo,[0,.13,0],[1,.26,.7],stoneColor),part(boxGeo,[0,1.35,.14],[1.65,2.65,.26],stoneColor),part(boxGeo,[0,2.72,.14],[1.8,.12,.32],copper)]);
 const pipe=new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(-.65,0,.1),new THREE.Vector3(-.65,1,.2),new THREE.Vector3(0,1.75,.2),new THREE.Vector3(.7,1.75,.2)]),14,.17,7,false);
 pieces.valve=mergedStageParts([part(cylGeo,[0,.12,0],[.85,.24,.85],darkMetal),part(pipe,[0,0,0],[1,1,1],copper),part(cylGeo,[0,1.8,.25],[.35,.26,.35],darkMetal,[Math.PI/2,0,0])]);pipe.dispose();
 const armillary=[];for(let i=0;i<3;i++)armillary.push(part(new THREE.TorusGeometry(.85,.055,5,28),[0,1.8,0],[1,1,1],copper,[i*Math.PI/3,Math.PI/2*i,0]));
 pieces.archive=mergedStageParts([...base,...armillary]);
 const ribs=[];for(let i=0;i<4;i++)ribs.push(part(new THREE.TorusGeometry(.7,.055,5,20,Math.PI),[0,1.8,0],[1,1,1],copper,[0,i*Math.PI/2,0]));
 pieces.core=mergedStageParts([...base,part(cylGeo,[0,1.22,0],[.8,.16,.8],darkMetal),...ribs]);
 pieces.ritual=mergedStageParts([part(cylGeo,[0,.18,0],[1.12,.36,1.12],stoneColor),...[-1,1].map(x=>part(boxGeo,[x*.85,1.1,0],[.15,2,.22],copper)),part(new THREE.TorusGeometry(.85,.09,6,26,Math.PI),[0,2,0],[1,1,1],copper)]);
 pieces.camp=mergedStageParts([part(cylGeo,[0,.14,0],[1.25,.28,1.25],stoneColor),part(cylGeo,[0,.4,0],[.85,.34,.85],copper),part(new THREE.TorusGeometry(.85,.06,5,24),[0,.7,0],[1,1,1],copper,[Math.PI/2,0,0])]);
 pieces.soul=mergedStageParts([part(new THREE.TorusGeometry(.5,.035,4,24,Math.PI*1.4),[0,1.45,0],[.7,1.25,1],'#d9e5db',[0,0,.4])]);
 pieces.relic=pieces.pact;
 const material=new THREE.MeshStandardMaterial({vertexColors:true,metalness:.35,roughness:.7});
 // Etched fresco is a texture drawn here, not text baked from another game.
 const fresco=makeArtTexture((g,n)=>{g.fillStyle='#3c3945';g.fillRect(0,0,n,n);g.strokeStyle='#bda57a';g.lineWidth=3;for(let i=0;i<3;i++){g.beginPath();g.arc(n*.5,n*(.25+i*.25),n*(.09+i*.025),0,Math.PI*2);g.stroke();}g.beginPath();g.moveTo(n*.5,n*.1);g.lineTo(n*.5,n*.9);g.stroke();g.strokeStyle='#847052';g.strokeRect(14,14,n-28,n-28);});
 craftAssets={pieces,material,fresco};return craftAssets;
}
function craftLandmarks(){
 const a=makeCraftAssets();
 for(const m of campaign.landmarks){
  const kind=m.kind||'relic',pedestal=m.root.children[0],geometry=a.pieces[kind];
  if(geometry){pedestal.geometry=geometry;pedestal.material=a.material;pedestal.position.set(0,0,0);pedestal.scale.set(1,1,1);pedestal.visible=true;}
  m.craft={turn:landmarkState(m)==='done'?1:0,pulse:0};m.root.userData.craftKind=kind;const solid=obstacles.find(o=>o.root===m.root);if(solid){solid.radius=kind==='camp'?1.25:kind==='ritual'?1.12:.85;solid.projectilePass=!['fresco','lamp','archive','valve'].includes(kind);solid.w=solid.d=solid.radius*2;if(['soul','mirror','bell'].includes(kind))solid.intangible=true;if(kind==='bell')for(const offsetX of [-1,1])obstacles.push({root:m.root,offsetX,x:m.x+offsetX,z:m.z,w:.28,d:.4});}m.root.traverse(o=>{if(o.isMesh&&o.material?.isMeshStandardMaterial)o.castShadow=true;});
  // Original glow becomes a restrained footprint instead of a bright arcade halo.
  const footprint=m.root.children.find(o=>o.geometry===ringGeo);if(footprint){footprint.scale.setScalar(1.05);footprint.material.opacity=.18;}
  if(kind==='fresco'){m.crystal.scale.set(1.15,12,.3);m.crystal.position.set(0,1.4,-.08);m.crystal.rotation.set(0,0,0);m.crystal.children.forEach(c=>c.visible=false);m.crystal.material.map=a.fresco;m.crystal.material.emissive.set('#3c2c15');m.crystal.material.needsUpdate=true;}
  if(kind==='valve'){m.crystal.rotation.z=m.craft.turn*Math.PI/2;m.crystal.position.z=-.08;}
  if(kind==='core')m.crystal.scale.setScalar(.65);
  if(kind==='camp'){m.crystal.scale.set(.38,.5,.38);m.crystal.position.y=1.05;}
  if(kind==='soul')m.crystal.scale.setScalar(.3);
 }
 for(const pointer of campaign.guidePointers){pointer.geometry=artDirection.leafGeometry;pointer.scale.set(.45,.65,.45);pointer.material.opacity=.42;pointer.material.transparent=true;}
}
function animateWorldUse(type){
 if(!campaign)return;
 campaign.worldUse={type,started:t};
 const nearest=(campaign.landmarks||[]).filter(m=>distance(m,p)<3.5).sort((a,b)=>distance(a,p)-distance(b,p))[0];if(nearest)nearest.craft.pulse=1;
}
function animateLandmarkCraft(dt){
 if(!campaign?.landmarks)return;
 for(const m of campaign.landmarks){if(!m.craft)continue;
  m.craft.pulse=Math.max(0,m.craft.pulse-dt*1.4);const done=landmarkState(m)==='done';
  m.craft.turn+=(Number(done)-m.craft.turn)*(1-Math.exp(-dt*3.5));
  if(m.kind==='valve')m.crystal.rotation.z=m.craft.turn*Math.PI/2;
  if(m.kind==='archive')m.crystal.rotation.y=Math.sin(t*.35)*.45;
  if(m.kind==='soul'){m.crystal.position.y=1.65+Math.sin(t*1.1)*.09;m.crystal.material.emissiveIntensity=.7;}
  if(m.kind==='core')m.crystal.rotation.y+=dt*.18;
  if(m.craft.pulse>0&&m.kind!=='fresco')m.crystal.material.emissiveIntensity=(done?.12:landmarkState(m)==='locked'?.2:.7)+m.craft.pulse*.4;
 }
}
function initArtDirection(){
 const root=new THREE.Group();world.root.add(root);const detail=new THREE.Group();art.detail.add(detail);
 const dummy=new THREE.Object3D(),windTime={value:0},windDirection={value:new THREE.Vector2(.6,-.2)};
 function batch(geometry,material,items,parent=root){const mesh=new THREE.InstancedMesh(geometry,material,items.length);items.forEach((q,i)=>{dummy.position.set(...q.p);dummy.rotation.set(...(q.r||[0,0,0]));dummy.scale.set(...q.s);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);if(q.c)mesh.setColorAt(i,new THREE.Color(q.c));});parent.add(mesh);return mesh;}
 let seed=2233;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 const stoneMap=makeArtTexture((g,n)=>{g.fillStyle='#696a6d';g.fillRect(0,0,n,n);for(let row=0;row<6;row++)for(let col=-1;col<5;col++){const x=col*n/4+(row%2)*n/8,y=row*n/6,v=140+rand()*30;g.fillStyle=`rgb(${v},${v},${v+3})`;g.fillRect(x+1,y+1,n/4-2,n/6-2);g.strokeStyle='#d4d0c644';g.strokeRect(x+3,y+3,n/4-6,n/6-6);g.strokeStyle='#3c414a55';g.beginPath();g.moveTo(x+n/8,y);g.lineTo(x+n/8+rand()*n/10,y+n/12);g.stroke();}for(let i=0;i<1800;i++){g.fillStyle=i%2?'#f4e8d70c':'#10182a18';g.fillRect(rand()*n,rand()*n,1,1);}},512);
 for(let i=0;i<world.floors.length;i++){const floor=world.floors[i],region=world.regions[i],map=stoneMap.clone();map.wrapS=map.wrapT=THREE.RepeatWrapping;map.repeat.set((region.x1-region.x0)/6,(region.z1-region.z0)/6);map.needsUpdate=true;floor.material.map.dispose();floor.material.map=map;floor.material.roughness=['Cloître','Nef'].includes(region.name)?.4:.8;floor.material.metalness=.22;floor.material.needsUpdate=true;}

 const blade=new THREE.BufferGeometry();blade.setAttribute('position',new THREE.Float32BufferAttribute([-.07,0,0,.07,0,0,-.04,.65,.06,.04,.65,.06,0,1,.14],3));blade.setIndex([0,1,2,1,3,2,2,3,4]);blade.computeVertexNormals();
 const grassMaterial=new THREE.MeshStandardMaterial({color:'#a99c74',roughness:.95,side:THREE.DoubleSide});
 grassMaterial.onBeforeCompile=shader=>{shader.uniforms.natureTime=windTime;shader.uniforms.natureDirection=windDirection;shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nuniform float natureTime;uniform vec2 natureDirection;');shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
 #ifdef USE_INSTANCING
 float wave=sin(natureTime*1.3+instanceMatrix[3].x*.7+instanceMatrix[3].z*.4);
 transformed.x+=position.y*position.y*(wave*.14+natureDirection.x*.13);
 transformed.z+=position.y*position.y*(wave*.09+natureDirection.y*.13);
 #endif`);};
 const grass=[];for(let i=0;i<550;i++){const z=-rand()*35,x=-26.8+rand()*1.7;if(world.onGround(x,z,.08))grass.push({p:[x,.02,z],s:[.8,.45+rand()*.75,.8],r:[0,rand()*6.28,0],c:i%4?'#b1a27e':'#746c58'});}
 for(let i=0;i<150;i++)grass.push({p:[-60+rand()*43,.03,-72-rand()],s:[.7,.35+rand()*.45,.7],r:[0,rand()*6.28,0],c:'#b9a584'});
 const grassMesh=batch(blade,grassMaterial,grass,detail);
 // A wind-swept grove outside the traversable garden, replacing blocky canopy masses.
 const obsolete=[];art.detail.traverse(o=>{if(o.isInstancedMesh&&o.geometry.type==='IcosahedronGeometry'&&o.count===16)obsolete.push(o);if(o.isInstancedMesh&&o.geometry.type==='ConeGeometry'&&o.count===32){o.geometry.dispose();o.geometry=new THREE.IcosahedronGeometry(.8,0);o.material.color.set('#30484b');o.material.emissive.set('#0a1117');}});for(const o of obsolete){o.parent.remove(o);o.geometry.dispose();}
 const trunks=[],leaves=[];
 for(const [x,z]of[[-31,-8],[-32,-28]]){
  const path=new THREE.CatmullRomCurve3([new THREE.Vector3(x,0,z),new THREE.Vector3(x-.4,3,z),new THREE.Vector3(x+1.1,6,z-.5)]);const tube=new THREE.TubeGeometry(path,10,.3,7,false);const trunk=new THREE.Mesh(tube,new THREE.MeshStandardMaterial({color:'#332c30',roughness:1}));detail.add(trunk);trunks.push(trunk);
  for(let i=0;i<65;i++){const angle=rand()*6.28,r=rand()*4;leaves.push({p:[x+Math.cos(angle)*r,4.3+rand()*3,z+Math.sin(angle)*r],s:[1.5+rand(),1.1+rand(),1],r:[-.55+rand()*.3,rand()*.8-.4,rand()*.4],c:i%3?'#815958':'#a67d68'});}
 }
 const leafMap=makeArtTexture((g,n)=>{g.clearRect(0,0,n,n);for(let i=0;i<95;i++){const x=rand()*n,y=rand()*n,r=4+rand()*12;g.fillStyle=['#ded1bd','#ad947c','#f2dec0'][i%3];g.beginPath();g.ellipse(x,y,r,r*.5,rand()*3,0,Math.PI*2);g.fill();}},128);
 batch(new THREE.PlaneGeometry(1,1),new THREE.MeshStandardMaterial({map:leafMap,color:'#ffffff',alphaTest:.35,side:THREE.DoubleSide,roughness:1}),leaves,detail);
 // Broken monumental windows make a composed, distant silhouette, not a wall across a path.
 const archParts=[];for(const side of [-1,1])for(const z of [-83,-103]){
  const x=side*26;archParts.push({geo:new THREE.TorusGeometry(3,.18,6,24,Math.PI),pos:[x,7,z],size:[1,1.3,1],rot:[0,side*Math.PI/2,0],color:'#9d8266'});
  for(const dz of [-3,3])archParts.push({pos:[x,3.5,z+dz],size:[.65,7,.65],color:'#49434c'});
 }
 const architecture=new THREE.Mesh(mergedStageParts(archParts),new THREE.MeshStandardMaterial({vertexColors:true,roughness:.78,metalness:.2}));root.add(architecture);for(const p of archParts)if(p.geo)p.geo.dispose();
 const rose=new THREE.Mesh(new THREE.TorusGeometry(4,.12,6,48),new THREE.MeshBasicMaterial({color:'#bc9165'}));rose.position.set(0,9,-116);root.add(rose);
 // Soft shadows ground actors with one instanced draw call on both quality levels.
 const shadowMaterial=new THREE.MeshBasicMaterial({color:'#050711',map:contactTexture,transparent:true,opacity:.4,depthWrite:false});const contacts=new THREE.InstancedMesh(new THREE.CircleGeometry(1,16),shadowMaterial,32);contacts.instanceMatrix.setUsage(THREE.DynamicDrawUsage);root.add(contacts);contacts.count=0;contacts.frustumCulled=false;
 const leafGeometry=new THREE.SphereGeometry(.15,6,4);leafGeometry.scale(.45,.12,1.6);
 const windMaterial=new THREE.MeshBasicMaterial({color:'#f0ddbb',transparent:true,opacity:.48,depthWrite:false});const wind=new THREE.InstancedMesh(leafGeometry,windMaterial,22);wind.instanceMatrix.setUsage(THREE.DynamicDrawUsage);wind.visible=false;wind.frustumCulled=false;root.add(wind);
 const palettes={};for(const [zone,color]of Object.entries({'Atrium des serments':'#29232e','Jardins suspendus':'#27363c','Cloître des cendres':'#3a2b29','Croisée des pèlerins':'#2c3039','Archives du Reflet':'#272b40','Forge du brasier':'#402b24','Nef des marées':'#29303d','Cour du Veilleur':'#34252e'})){const fog=new THREE.Color(color);palettes[zone]={fog,background:fog.clone().multiplyScalar(.3),abyss:fog.clone().multiplyScalar(.55)};}
 scene.children.filter(o=>o.isAmbientLight).forEach(o=>o.color.set('#acadb8'));sun.color.set('#f0cda7');sun.intensity=3.1;
 artDirection={palettes,root,detail,grassMesh,grassMaterial,windTime,windDirection,contacts,wind,leafGeometry,dummy,petalPhase:0,clock:0,gates:[]};
 sculptGates();
}
// Ritual thresholds use short vertical modules. A wide corridor must never
// become a pair of 24-unit blades sweeping into the neighbouring lanes.
function craftedGateModuleGeometry(width,height,depth){
 const parts=[],metal='#baa17b',dark='#49434a',barDepth=Math.min(.13,Math.max(.08,depth*.28));
 const add=(pos,size,color=metal)=>parts.push({pos,size,color});
 add([0,.065,0],[width,.13,barDepth],dark);
 for(const y of [.15,height*.43,height-.09])add([0,y,0],[width,.045,barDepth]);
 const count=Math.max(3,Math.ceil(width/.42));
 for(let i=0;i<=count;i++)add([-width/2+.0225+i*(width-.045)/count,height/2,0],[i===0||i===count?.045:.028,height,barDepth]);
 const radius=Math.min(.68,width*.27),arch=new THREE.TorusGeometry(radius,.014,5,24,Math.PI),seal=new THREE.TorusGeometry(.15,.013,5,24);
 parts.push({geo:arch,pos:[0,height*.64,0],size:[1,1,1],color:'#d0b589'},{geo:seal,pos:[0,height*.40,0],size:[1,1,1],color:'#d0b589'});
 const geometry=mergedStageParts(parts);arch.dispose();seal.dispose();geometry.computeBoundingBox();geometry.computeBoundingSphere();return geometry;
}
function setCraftedGateOpen(gate,progress){
 gate.open=THREE.MathUtils.clamp(Number.isFinite(progress)?progress:0,0,1);
 gate.lift=gate.maxLift*gate.open;gate.panelRoot.position.y=gate.lift;
 gate.clearance=gate.moduleBottom+gate.lift;gate.passable=gate.open>=.995||gate.clearance>=gate.requiredClearance;
 // Fully retracted bars are stored above the threshold rather than casting a
 // phantom ceiling shadow. The groups keep their transforms for inspection.
 gate.panelRoot.visible=gate.open<.995;
 for(const panel of gate.panels)panel.castShadow=!gate.passable;
}
function craftedGateRequiredClearance(){
 let required=2.5;
 const consider=avatar=>{const height=avatar?.motionCalibration?.bodyHeight,scale=Math.abs(avatar?.root?.scale?.y||1);if(Number.isFinite(height)&&height>0&&Number.isFinite(scale))required=Math.max(required,height*scale+.05);};
 if(typeof avatarRuntime!=='undefined')consider(avatarRuntime.current);
 if(typeof localParty!=='undefined')for(const actor of localParty)consider(actor.avatar);
 return required;
}
function craftedGateOccupied(obstacle){
 const actors=typeof p!=='undefined'&&p?[p,...(typeof localParty!=='undefined'?localParty:[])]:[];
 return actors.some(actor=>Number.isFinite(actor.x)&&Number.isFinite(actor.z)&&Math.abs(actor.x-obstacle.x)<obstacle.w/2+.6&&Math.abs(actor.z-obstacle.z)<obstacle.d/2+.6);
}
function updateCraftedGates(dt){
 if(!artDirection)return;const blend=1-Math.exp(-Math.max(0,dt)*4),requiredClearance=craftedGateRequiredClearance();
 for(const obstacle of artDirection.gates){
  const gate=obstacle.craftedGate,requestedOpen=!campaignGateClosed(obstacle.gate);gate.requiredClearance=requiredClearance;
  if(requestedOpen)gate.wasRequestedOpen=true;
  const hold=gate.wasRequestedOpen&&gate.open>.0001&&!requestedOpen&&craftedGateOccupied(obstacle),target=requestedOpen||hold?1:0;
  let next=gate.open+(target-gate.open)*blend;if(target===0&&next<.0001){next=0;gate.wasRequestedOpen=false;}
  gate.heldForActor=hold;setCraftedGateOpen(gate,next);obstacle.mesh.visible=true;
 }
}
function sculptGates(){
 const empty=new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute([],3)),material=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.54,metalness:.58});
 material.name='Ritual brushed bronze';material.userData.surface='metal';
 for(const obstacle of world.obstacles.filter(item=>item.gate)){
  const height=obstacle.mesh.scale.y;for(const child of [...obstacle.mesh.children])obstacle.mesh.remove(child);
  obstacle.mesh.geometry=empty;obstacle.mesh.material.opacity=0;obstacle.mesh.scale.set(1,1,1);obstacle.mesh.rotation.set(0,0,0);obstacle.mesh.position.set(obstacle.x,0,obstacle.z);
  const moduleCount=Math.max(1,Math.ceil(obstacle.w/3.2)),moduleWidth=obstacle.w/moduleCount,geometry=craftedGateModuleGeometry(moduleWidth,height,obstacle.d),panelRoot=new THREE.Group(),hinges=[],panels=[],matrix=new THREE.Matrix4();
  panelRoot.name='Ritual vertical panels';obstacle.mesh.add(panelRoot);
  // Two instanced batches retain the old gate's draw-call budget. These groups
  // no longer rotate; hinges is retained only for old art inspection consumers.
  for(const [start,count]of [[0,Math.ceil(moduleCount/2)],[Math.ceil(moduleCount/2),Math.floor(moduleCount/2)]]){
   const group=new THREE.Group();panelRoot.add(group);hinges.push(group);if(!count)continue;
   const batch=new THREE.InstancedMesh(geometry,material,count);batch.name='Ritual modules';batch.receiveShadow=true;batch.castShadow=true;
   for(let i=0;i<count;i++){matrix.makeTranslation(-obstacle.w/2+(start+i+.5)*moduleWidth,0,0);batch.setMatrixAt(i,matrix);}
   batch.instanceMatrix.needsUpdate=true;batch.computeBoundingBox();batch.computeBoundingSphere();group.add(batch);panels.push(batch);
  }
  const gate={hinges,panels,panelRoot,moduleCount,moduleWidth,height,moduleBottom:geometry.boundingBox.min.y,maxLift:height+.18,requiredClearance:2.5,open:0,lift:0,clearance:0,passable:false,wasRequestedOpen:false,heldForActor:false};
  obstacle.craftedGate=gate;setCraftedGateOpen(gate,0);artDirection.gates.push(obstacle);
 }
}
function updateArtDirection(dt){
 if(journey.level>1)return;
 if(!artDirection)return;const a=artDirection,dummy=a.dummy,zone=p?world.zoneAt(p.x,p.z):'Atrium des serments',palette=a.palettes[zone]||a.palettes['Atrium des serments'],blend=1-Math.exp(-dt*.7);scene.fog.color.lerp(palette.fog,blend);scene.background.lerp(palette.background,blend);world.abyss.material.color.lerp(palette.abyss,blend);a.clock+=dt;a.windTime.value=a.clock;
 const guided=campaign&&state==='playing'&&guidanceOn&&t<guideRevealUntil,desired=guided&&guideHeading!==null?new THREE.Vector2(Math.sin(guideHeading),-Math.cos(guideHeading)):new THREE.Vector2(.6,-.2);a.windDirection.value.lerp(desired,1-Math.exp(-dt*1.2));
 a.contacts.visible=quality==='light';a.contacts.count=0;if(campaign)for(const e of enemies)if(!e.dead&&e.root.visible&&a.contacts.count<32){dummy.position.set(e.x,.025,e.z);dummy.rotation.set(-Math.PI/2,0,0);const r=['boss','porter'].includes(e.type)?1.5:.65;dummy.scale.set(r,r*.65,1);dummy.updateMatrix();a.contacts.setMatrixAt(a.contacts.count++,dummy.matrix);}a.contacts.instanceMatrix.needsUpdate=true;
 a.wind.visible=guided;const path=navCache?.route.slice(navCache.cursor)||[];
 if(guided&&path.length>1){const length=Math.min(routeDistance(path),12);for(let i=0;i<a.wind.count;i++){let distanceAlong=(i*.65+(a.clock*.6))%Math.max(.1,length),j=0;while(j<path.length-2&&distanceAlong>distance(path[j],path[j+1])){distanceAlong-=distance(path[j],path[j+1]);j++;}const from=path[j],to=path[j+1],f=Math.min(1,distanceAlong/Math.max(.01,distance(from,to)));dummy.position.set(from.x+(to.x-from.x)*f,.45+Math.sin(a.clock+i)*.18,from.z+(to.z-from.z)*f);dummy.rotation.set(0,Math.atan2(to.x-from.x,to.z-from.z),Math.sin(a.clock+i)*.3);dummy.scale.set(.7,.7,.7);dummy.updateMatrix();a.wind.setMatrixAt(i,dummy.matrix);}a.wind.instanceMatrix.needsUpdate=true;}else a.wind.visible=false;
 updateCraftedGates(dt);
 if(state==='playing')animateLandmarkCraft(dt);
}
function wireArtDirectionUI(){
 const select=$('#presentation');try{select.value=localStorage.getItem('royaumes-presentation')||'immersive';}catch(_){}
 function apply(){document.body.classList.toggle('immersive',select.value==='immersive');try{localStorage.setItem('royaumes-presentation',select.value)}catch(_){}}
 select.onchange=apply;apply();
}
