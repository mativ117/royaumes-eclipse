'use strict';
let journey={level:1,step:0,root:null,route:'',checkpoint:0,nodes:[],core:180,elapsed:0},baseWorld=null;
const CHAPTERS={1:{title:'La Cathédrale vivante',subtitle:'Le Carillon des Âmes'},2:{title:'La Chasse aux Souverains',subtitle:'Le Jardin des noms effacés'},3:{title:'Le Convoi de l’Impossible',subtitle:'La dernière aube'}};
function resetJourneyWorld(){
 if(!baseWorld)baseWorld={regions:world.regions,onGround:world.onGround,zoneAt:world.zoneAt,obstacles:world.obstacles,occluders:sanctuary?.occluders};
 if(journey.root){scene.remove(journey.root);for(const g of journey.geometries||[])g.dispose();for(const m of journey.materials||[])m.dispose();for(const tx of journey.textures||[])tx.dispose();}
 journey={level:1,step:0,root:null,route:'',checkpoint:0,nodes:[],core:180,elapsed:0};Object.assign(world,{regions:baseWorld.regions,onGround:baseWorld.onGround,zoneAt:baseWorld.zoneAt,obstacles:baseWorld.obstacles});world.root.visible=true;if(sanctuary)sanctuary.occluders=baseWorld.occluders;navCache=null;
}
function chapterGround(regions,x,z,r=.48){return [[x-r,z-r],[x+r,z-r],[x-r,z+r],[x+r,z+r]].every(([a,b])=>regions.some(q=>a>=q.x0&&a<=q.x1&&b>=q.z0&&b<=q.z1));}
function journeyMaterial(color,metal=.1,rough=.8){const m=new THREE.MeshStandardMaterial({color,metalness:metal,roughness:rough});journey.materials.push(m);return m;}
function journeyBox(x,y,z,w,h,d,material,solid=false){const o=mesh(boxGeo,material,x,y,z,w,h,d,journey.root);o.castShadow=h>1&&y<4;o.receiveShadow=true;if(solid){o.material=material.clone();o.material.transparent=true;journey.materials.push(o.material);const c={x,z,w,d,mesh:o};obstacles.push(c);journey.occluders.push(o);}return o;}
function journeyNode(id,x,z,title,color='#b8eedb',kind='ritual'){
 const root=new THREE.Group();root.position.set(x,0,z);journey.root.add(root);const material=journeyMaterial(color,.4,.4),base=mesh(cylGeo,journey.stone,0,.2,0,.8,.4,.8,root);base.castShadow=true;const shape=getLandmarkAssets()[kind==='fresco'?'book':kind==='relic'?'lens':kind]||sphereGeo,scale=shape===sphereGeo?.3:.7;const crystal=mesh(shape,material,0,1.2,0,scale,scale,scale,root);const ring=mesh(ringGeo,material,0,.035,0,1.2,1.2,1.2,root);ring.rotation.x=-Math.PI/2;const tag=label(title,x,z,color,3.5);tag.visible=false;const node={id,x,z,title,kind,root,crystal,material,tag};journey.nodes.push(node);obstacles.push({x,z,w:1.9,d:1.9,radius:.95,root,projectilePass:true});return node;
}
function journeyGate(x,z,w,open){const root=new THREE.Group();root.position.set(x,0,z);journey.root.add(root);const material=journeyMaterial('#cea66d',.6,.35);for(let i=0;i<Math.floor(w/2);i++)mesh(boxGeo,material,-w/2+1+i*2,1.4,0,.12,2.8,.22,root);const gate={x,z,w,d:.3,root,questGate:true,enabled:()=>!open()};obstacles.push(gate);journey.gates.push({root,open});}
function journeyBatch(geo,material,items,cast=true){const mesh=new THREE.InstancedMesh(geo,material,items.length),dummy=new THREE.Object3D();for(let i=0;i<items.length;i++){const q=items[i];dummy.position.set(...q.p);dummy.rotation.set(...(q.r||[0,0,0]));dummy.scale.set(...q.s);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);}mesh.castShadow=cast;mesh.receiveShadow=true;journey.root.add(mesh);return mesh;}
function buildJourneyScenery(level,regions){
 journey.stone=journeyMaterial(level===2?'#6d7b7c':'#6c6254');const ground=journeyMaterial(level===2?'#87928b':'#b8a58b'),ivory=journeyMaterial('#d5c5a8'),copper=journeyMaterial('#9c7449',.65,.5),redLeaves=journeyMaterial(level===2?'#9a4037':'#d39b64');
 const texture=makeArtTexture((g,n)=>{g.fillStyle=level===2?'#b3b8a2':'#c6b99c';g.fillRect(0,0,n,n);let seed=29;for(let i=0;i<2200;i++){seed=(seed*1664525+1013904223)>>>0;g.fillStyle=i%3?'#fff8db18':'#263b3b24';const x=seed%n;seed=(seed*1664525+1013904223)>>>0;g.fillRect(x,seed%n,1+(i%3),1);}g.strokeStyle='#66685d55';for(let i=0;i<8;i++){g.beginPath();g.moveTo(0,i*n/8);g.lineTo(n,i*n/8);g.stroke();}},512);texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.repeat.set(6,6);ground.map=texture;journey.textures=[texture];
 for(const r of regions){const x=(r.x0+r.x1)/2,z=(r.z0+r.z1)/2;journeyBox(x,-.35,z,r.x1-r.x0,.7,r.z1-r.z0,ground);journeyBox(x,-1.1,z,r.x1-r.x0,1.1,r.z1-r.z0,journey.stone);}
 const trunks=[],crowns=[],stones=[],archGeo=new THREE.TorusGeometry(1,.06,6,28,Math.PI);journey.geometries.push(archGeo);const arches=[];
 if(level===2){
  for(const side of [-1,1])for(let i=0;i<15;i++){const z=22-i*8.4,x=side*(i<8?31:28);trunks.push({p:[x,2.4,z],s:[.3,4.8,.3],r:[0,0,side*.12]});for(let j=0;j<3;j++)crowns.push({p:[x+Math.sin(i+j)*1.3,5+j*.7,z+Math.cos(i+j)],s:[2.8-j*.3,1.2,2.8-j*.2]});}
  for(const side of [-1,1])for(const z of [-50,-65])journeyBox(side*15,2,z,1.2,4,1.2,ivory,true);
  for(const z of [-43,-78])arches.push({p:[0,3.7,z],s:[14,7,1]});
  for(let i=0;i<18;i++)stones.push({p:[Math.sin(i*2.4)*39,3+(i%5),-126-i*2],s:[3+(i%4),8+(i%6),3],r:[0,i,0]});
 }else{
  // Visible articulated colossus beneath the walkable decks, with a village on its back.
  const body=journeyMaterial('#252d36',.35,.65),bone=journeyMaterial('#a69b83',.2,.7);journeyBox(0,-4.5,-35,19,6,100,body);
  for(let i=0;i<14;i++)journeyBox(0,-1.35,20-i*9,23,.6,1.2,bone);
  for(const side of [-1,1])for(let i=0;i<5;i++){const leg=journeyBox(side*15,-7,3-i*22,13,2,5,body);leg.rotation.z=side*.22;journey.legs.push({mesh:leg,side,index:i});}
  const head=mesh(sphereGeo,body,0,-2,-112,13,5,16,journey.root);head.castShadow=true;for(const side of [-1,1])mesh(sphereGeo,classProjectileMaterial('eclipse'),side*8,0,-117,.4,.3,1,journey.root);
  for(const side of [-1,1])for(const z of [-28,-42]){journeyBox(side*14,1.6,z,3,3.2,5,ivory,true);const roof=mesh(coneGeo,redLeaves,side*14,3.9,z,3,1,3,journey.root);roof.castShadow=true;}
  for(const z of [5,-18,-56,-83])arches.push({p:[0,3,z],s:[z===5?5:9,5,1]});
  for(let i=0;i<20;i++)stones.push({p:[(i%2?1:-1)*(35+i%5*6),-9,-100+i*9],s:[6+(i%5),8+(i%4)*3,7],r:[0,i*.3,.1]});
 }
 if(level===2){for(const [x,z]of[[-14,-7],[-25,-28],[13,-9],[25,-29]]){const tree=mesh(cylGeo,journey.stone,x,1.6,z,.5,3.2,.5,journey.root);tree.castShadow=true;obstacles.push({x,z,w:1,d:1,radius:.5,mesh:tree});crowns.push({p:[x,3.8,z],s:[2.4,1.2,2.4]});}}
 const waterGeometry=new THREE.PlaneGeometry(150,190),waterMaterial=sanctuary.fallback.material.clone();journey.geometries.push(waterGeometry);journey.materials.push(waterMaterial);journey.water=mesh(waterGeometry,waterMaterial,0,level===2?-1.3:-13,-40,1,1,1,journey.root);journey.water.rotation.x=-Math.PI/2;
 journeyBatch(cylGeo,journey.stone,trunks);journey.roughCanopy=journeyBatch(sphereGeo,redLeaves,crowns,false);journey.archesData=arches;journeyBatch(archGeo,copper,arches,false);journey.roughRock=journeyBatch(coneGeo,journey.stone,stones,false);
 const railPosts=[];for(const side of [-1,1])for(let z=20;z>-110;z-=5)railPosts.push({p:[side*(level===2?32:24),1,z],s:[.15,2,.15]});journey.roughRails=journeyBatch(boxGeo,copper,railPosts);
 const motes=new Float32Array(180*3);for(let i=0;i<180;i++){motes[i*3]=Math.sin(i*17)*40;motes[i*3+1]=1+i%12;motes[i*3+2]=25-i*.85;}const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(motes,3));journey.geometries.push(geo);const pm=new THREE.PointsMaterial({color:level===2?'#efb586':'#e8d4b4',size:.1,transparent:true,opacity:.65});journey.materials.push(pm);journey.particles=new THREE.Points(geo,pm);journey.root.add(journey.particles);
 if(level===3){const backdrop=new THREE.Group();journey.root.add(backdrop);journey.backdrop=backdrop;for(let i=0;i<20;i++){const m=mesh(coneGeo,journey.stone,(i%2?1:-1)*(36+i%4*9),-12,-120+i*10,9,18+(i%4)*4,8,backdrop);m.rotation.y=i*.4;}}
}
function enterChapter(level,checkpoint=0){
 clearLocalParty();clearRoom();if(journey.root){scene.remove(journey.root);for(const g of journey.geometries||[])g.dispose();for(const m of journey.materials||[])m.dispose();for(const tx of journey.textures||[])tx.dispose();}
 journey={level,step:checkpoint,checkpoint,root:new THREE.Group(),route:'',core:180,nodes:[],gates:[],materials:[],geometries:[],textures:[],occluders:[],legs:[],elapsed:0,stageSpawned:-1,runes:0,repairs:0,secretOpen:false};scene.add(journey.root);scene.background.set(level===2?'#a3907a':'#af8262');scene.fog.color.set(level===2?'#444448':'#675343');scene.fog.density=.012;world.root.visible=false;clearInputs();obstacles=[];world.obstacles=obstacles;campaign.landmarks=[];campaign.guidePointers=[];campaign.focusRing=null;campaign.time=campaign.activeSeconds=0;kills=0;campaign.bossAwake=false;campaign.defeated=new Set();campaign.trials=freshTrials();campaign.zone='';boss=null;boon=boon||'vigor';p.max=HEROES[hero].hp+(boon==='vigor'?40:-30);room=0;
 const regions=level===2?[[-16,16,4,29,'Le Jardin des noms'],[-29,-10,-35,4,'La trace de fer'],[10,29,-35,4,'La trace de pluie'],[-29,29,-43,-32,'Le Gué des serments'],[-18,18,-80,-43,'L’Observatoire muet'],[-24,24,-112,-80,'Le Trône des racines']]:[[-12,12,8,29,'La Queue des lanternes'],[-5,5,-18,8,'L’Échine du vent'],[-18,18,-55,-18,'Le Village mobile'],[-32,-18,-70,-42,'L’Escale du couchant'],[18,32,-70,-42,'L’Escale de l’orage'],[-10,10,-84,-55,'Le Cœur des liens'],[-23,23,-112,-84,'Le Front de l’aube']];
 world.regions=regions.map(([x0,x1,z0,z1,name])=>({x0,x1,z0,z1,name}));world.onGround=(x,z,r=.48)=>chapterGround(world.regions,x,z,r);world.zoneAt=(x,z)=>world.regions.find(q=>x>=q.x0&&x<=q.x1&&z>=q.z0&&z<=q.z1)?.name||CHAPTERS[level].title;
 buildJourneyScenery(level,world.regions);
 if(level===2){
  journeyNode('trace-fer',-20,-12,'Lire la trace de fer','#e3bd87','archive');journeyNode('trace-pluie',20,-25,'Lire la trace de pluie','#a3e6ed','archive');journeyNode('memoire',0,-38,'Lire la mémoire du gué','#e4d4ae','fresco');
  journeyNode('rain',-10,-55,'Appeler la pluie','#91d9e7','lamp');journeyNode('ember',0,-55,'Appeler la cendre','#ffb082','lamp');journeyNode('silence',10,-55,'Appeler le silence','#dbb9ee','lamp');journeyNode('exit',0,-108,'Quitter le jardin','#e9dba6','camp');
  journeyGate(0,-43,36,()=>journey.step>=2);journeyGate(0,-80,48,()=>journey.step>=4);journey.order=boon==='vigor'?['silence','rain']:['rain','silence'];
  journey.arenaPillars=[];for(const x of [-13,13])for(const z of [-92,-104]){const pillar=journeyBox(x,1.5,z,1.5,3,1.5,journey.stone);const o={x,z,w:1.5,d:1.5,mesh:pillar,enabled:()=>journey.bossPhase>=2};obstacles.push(o);journey.arenaPillars.push(pillar);pillar.visible=false;}
 }else{
  journeyNode('wake',0,18,'Éveiller le colosse','#e8cf91','camp');journeyNode('link0',0,10,'Réparer le lien de queue');journeyNode('link1',0,-8,'Réparer le lien d’échine');journeyNode('link2',10,-29,'Réparer le lien du village');journeyNode('route',0,-37,'Choisir une route','#e6c493','fresco');
  journeyNode('supply-west',-25,-53,'Accueillir l’escale','#e9c2aa','camp');journeyNode('supply-east',25,-53,'Accueillir l’escale','#b5dce9','camp');journeyNode('heart',0,-73,'Ancrer le cœur','#9ce8d8','core');journeyNode('exit',0,-108,'Rendre l’aube','#edcf8b','camp');
  journeyGate(0,-18,10,()=>journey.step>=1);journeyGate(0,-56,20,()=>journey.step>=3);journeyGate(0,-84,46,()=>journey.step>=5);
  journeyNode('secret-shore',29,-61,'Écouter le vide','#b8a1df','relic');
 }
 dressJourneyEnvironment();
 const spawnPoints=level===2?[[0,23],[-20,-9],[0,-36],[0,-46],[0,-76],[0,-88]]:[[0,24],[0,21],[0,-32],[0,-39],[0,-57],[0,-80],[0,-90]];
 const point=spawnPoints[Math.min(checkpoint,spawnPoints.length-1)];resetHeroAt(...point);journey.checkpointPoint={x:point[0],z:point[1]};if(localProfile.journey?.level===level&&checkpoint>0)journey.core=localProfile.journey.core||180;if(level===3&&checkpoint>=3)journey.route=localProfile.journey?.route||'sun';
 sanctuary.occluders=journey.occluders;navCache=null;trackedGoal='';state='playing';$('#pausePanel').hidden=true;$('#hud').hidden=false;$('#mobile').classList.add('playing');$('#menu').hidden=true;$('#bossHUD').firstElementChild.textContent=level===2?'LE SOUVERAIN SANS NOM':'LE MANGE-AUBE';saveJourneyCheckpoint(false);spawnJourneyStage();if(selectedMode()==='coop')setupLocalParty();announce(CHAPTERS[level].title+' · '+CHAPTERS[level].subtitle);updateJourney(0);updateHUD();
}
function spawnJourneyFoes(group,definitions){for(const [x,z,type]of definitions){const e=spawn(x,z,type);e.id='journey-'+group+'-'+enemies.length;e.journeyGroup=group;e.alert=10;if(type==='boss'){boss=e;e.hp=e.max=journey.level===2?1550:1800;e.pattern=0;e.phase=1;e.mode='idle';e.timer=1.8;e.root.scale.setScalar(journey.level===2?2.4:2.8);const m=journeyMaterial(journey.level===2?'#c1b192':'#352e42',.45,.5);for(const side of [-1,1]){const horn=mesh(coneGeo,m,side*.42,2.4,0,.17,.65,.17,e.root);horn.rotation.z=side*.45;}e.mode='idle';}if(group==='heart')e.sabotage=true;}}
function spawnJourneyStage(){
 if(journey.stageSpawned===journey.step)return;journey.stageSpawned=journey.step;
 if(journey.level===2){const groups={0:[[-20,-17,'sentinel'],[-24,-21,'archer']],1:[[18,-23,'oracle'],[24,-30,'warden'],[15,-29,'warden']],3:[[0,-69,'porter'],[-9,-66,'archer']],4:[[0,-98,'boss']]};if(groups[journey.step])spawnJourneyFoes('stage'+journey.step,groups[journey.step]);}
 else{const groups={1:[[0,-2,'warden'],[0,-12,'archer'],[10,-27,'sentinel']],3:[[(journey.route==='sun'?-25:25),-58,'sentinel'],[(journey.route==='sun'?-21:21),-64,journey.route==='sun'?'archer':'oracle']],4:[[-6,-67,'sentinel'],[6,-75,'oracle'],[0,-78,'warden']],5:[[0,-99,'boss']]};if(groups[journey.step])spawnJourneyFoes(journey.step===4?'heart':'stage'+journey.step,groups[journey.step]);}
}
function journeyGroupClear(group='stage'+journey.step){return !enemies.some(e=>!e.dead&&e.journeyGroup===group);}
function saveJourneyCheckpoint(show=true){
 journey.checkpoint=journey.step;journey.checkpointPoint={x:p.x,z:p.z};localProfile.journey={level:journey.level,hero,boon,checkpoint:journey.step,route:journey.route,core:journey.core};persistProfile();if(show){p.hp=p.max;p.inv=2;p.power=0;for(const actor of localParty){actor.hp=actor.max;actor.downed=false;}announce('Ancre du voyage · santé restaurée et progression locale enregistrée.');}
}
function advanceJourney(){journey.step++;saveJourneyCheckpoint();spawnJourneyStage();navCache=null;updateLandmarkReadability();}
function journeyGoals(){
 const node=id=>journey.nodes.find(n=>n.id===id),goal=(id,title,action,point)=>({...point,id,title,action,kind:point?.kind||'boss',targetId:point?.id||id});
 if(journey.level===2){const s=journey.step;
  if(s<2){const n=node(s===0?'trace-fer':'trace-pluie');return[goal(n.id,s===0?'La trace de fer':'La trace de pluie',journeyGroupClear()?'Lire la trace et retenir la faiblesse.':'Traverser le jardin et vaincre les gardes de la trace.',n)];}
  if(s===2){if(!journey.memoryRead)return[goal('memoire','L’Observatoire muet','Lire la mémoire au gué.',node('memoire'))];return ['rain','ember','silence'].map(id=>goal(id,'Les deux voix du jardin',`Fer contre silence ; cendre contre pluie. ${journey.runes}/2 accords. Premier appel : ${journey.order[0]==='rain'?'pluie':'silence'}.`,node(id)));}
  if(s===3)return[goal('duel','Le Gardien des racines','Contourner sa charge ; frapper pendant sa récupération.',enemies.find(e=>!e.dead&&e.journeyGroup==='stage3')||{x:0,z:-69})];
  if(s===4)return[goal('sovereign','Le Souverain sans nom',campaign.bossAwake?'Le terrain change à chaque phase. Lire les marques et frapper sa récupération.':'Traverser le dernier seuil.',boss||{x:0,z:-98})];
  return[goal('exit','Le jardin retrouve un nom','Rejoindre la porte et poursuivre le voyage.',node('exit'))];
 }
 const s=journey.step;if(s===0)return[goal('wake','Le Convoi de l’Impossible','Faire sonner la lanterne pour éveiller le colosse.',node('wake'))];
 if(s===1)return[0,1,2].filter(i=>!journey.repaired?.includes(i)).map(i=>goal('link'+i,'Les liens de l’échine','Vaincre les saboteurs proches puis réparer le lien.',node('link'+i)));
 if(s===2)return[goal('route','Les deux horizons','Choisir la route du couchant ou celle de l’orage.',node('route'))];
 if(s===3)return[goal('supply','L’escale du voyage',journeyGroupClear()?'Choisir le don de l’escale.':'Libérer le passage de l’escale.',node(journey.route==='sun'?'supply-west':'supply-east'))];
 if(s===4)return[goal('heart','Le cœur des liens',`Intégrité du cœur : ${Math.ceil(journey.core)}/180. Éliminer les saboteurs puis ancrer le cœur.`,node('heart'))];
 if(s===5)return[goal('dawn','Le Mange-Aube',campaign.bossAwake?'Traverser ses vagues puis frapper son cœur ouvert.':'Rejoindre le front du colosse.',boss||{x:0,z:-99})];
 return[goal('exit','Rendre l’aube','Rejoindre la proue et choisir de laisser partir la nuit.',node('exit'))];
}
function journeyInteraction(actor=p){
 if(journey.level<=1)return null;const near=id=>{const n=journey.nodes.find(n=>n.id===id);return n&&distance(actor,n)<2.8?n:null;};
 if(journey.level===2){
  if(journey.step<2&&near(journey.step===0?'trace-fer':'trace-pluie'))return{type:'journey',action:'trace',label:journeyGroupClear()?'Lire la trace':'Les gardes protègent la trace'};
  if(journey.step===2){if(near('memoire'))return{type:'journey',action:'memory',label:'Lire la mémoire des Souverains'};for(const id of ['rain','ember','silence'])if(near(id))return{type:'journey',action:'rune',id,label:journey.nodes.find(n=>n.id===id).title};}
  if(journey.step===4&&localProfile.secret[0]&&!localProfile.secret[1]&&boss?.mode==='recover'&&distance(actor,boss)<4&&!p.attack&&p.recoil===0)return{type:'journey',action:'bow',label:'Répondre au geste, arme baissée'};
  if(journey.step>=5&&near('exit'))return{type:'journey',action:'exit',label:'Quitter le jardin'};
 }else{
  if(localProfile.secret[0]&&localProfile.secret[1]&&!localProfile.secret[2]&&journey.step>=3&&near('secret-shore'))return{type:'journey',action:'secret',label:'Écouter le reflet qui n’a pas de rive'};
  if(journey.secretOpen&&journeyGroupClear('secret')&&Math.hypot(actor.x-41,actor.z+60)<3)return{type:'journey',action:'secret-take',label:'Accueillir le soleil noir'};
  if(journey.step===0&&near('wake'))return{type:'journey',action:'wake',label:'Éveiller le colosse'};
  if(journey.step===1)for(let i=0;i<3;i++)if(!journey.repaired?.includes(i)&&near('link'+i))return{type:'journey',action:'repair',index:i,label:'Réparer le lien'};
  if(journey.step===2&&near('route'))return{type:'journey',action:'route',label:'Choisir un horizon'};
  if(journey.step===3&&near(journey.route==='sun'?'supply-west':'supply-east'))return{type:'journey',action:'supply',label:journeyGroupClear()?'Accueillir le don de l’escale':'Libérer l’escale'};
  if(journey.step===4&&near('heart'))return{type:'journey',action:'heart',label:journeyGroupClear('heart')?'Ancrer le cœur':'Les saboteurs menacent le cœur'};
  if(journey.step>=6&&near('exit'))return{type:'journey',action:'exit',label:'Rendre l’aube'};
 }
 return null;
}
function performJourneyInteraction(target,actor=p){
 const a=target.action;
 if(a==='trace'){if(!journeyGroupClear())return announce('Vainquez les gardes pour approcher la trace.');announce(journey.step===0?'Le métal boit le silence. La cendre craint la pluie.':'Deux Souverains, deux appels : retenez ce que le jardin vous a montré.');advanceJourney();}
 if(a==='memory'){journey.memoryRead=true;announce('Le fer répond au silence, la cendre à la pluie. Premier appel : '+(journey.order[0]==='rain'?'la pluie.':'le silence.'));}
 if(a==='rune'){
  if(!journey.memoryRead)return announce('La mémoire du gué donne un sens à ces trois appels.');
  if(target.id!==journey.order[journey.runes]){journey.runes=0;if(!journey.puzzlePenalty||t>journey.puzzlePenalty){journey.puzzlePenalty=t+5;addHazard(actor.x,actor.z,2,1.3,15);}return announce('Le jardin refuse cet appel. Relisez les deux faiblesses.');}
  journey.runes++;effect(actor.x,actor.z,4,'#bbe9dd');if(journey.runes===2)advanceJourney();else announce('Premier appel juste. Le second Souverain attend l’autre faiblesse.');
 }
 if(a==='bow'){recordSecret(1);actor.inv=2;campaign.worldUse={type:'bow',started:t};announce('Le Souverain répond à votre salut. Un second reflet rejoint votre marque.');}
 if(a==='wake'){journey.awake=true;advanceJourney();}
 if(a==='repair'){
  if(enemies.some(e=>!e.dead&&e.journeyGroup==='stage1'&&distance(e,p)<12))return announce('Écartez les saboteurs avant de réparer ce lien.');journey.repaired=journey.repaired||[];journey.repaired.push(target.index);actor.hp=Math.min(actor.max,actor.hp+15);effect(actor.x,actor.z,3,'#a9ebd6');if(journey.repaired.length===3)advanceJourney();else announce('Lien réparé · '+journey.repaired.length+'/3.');
 }
 if(a==='route')openJourneyChoice('route');
 if(a==='supply'){if(journeyGroupClear())openJourneyChoice('supply');}
 if(a==='heart'){if(!journeyGroupClear('heart'))return;advanceJourney();}
 if(a==='secret'){
  if(journey.secretOpen)return;journey.secretOpen=true;world.regions.push({x0:30,x1:45,z0:-63,z1:-57,name:'L’Escale invisible'},{x0:35,x1:47,z0:-68,z1:-51,name:'Le Reflet dernier'});journeyBox(38,-.4,-60,18,.8,6,journey.stone);journeyBox(41,-.4,-60,12,.8,17,journey.stone);spawnJourneyFoes('secret',[[41,-60,'porter']]);announce('L’escale prend forme. Affrontez l’ombre qui vous attend.');navCache=null;
 }
 if(a==='secret-take'){recordSecret(2);effect(41,-60,6,'#ffdb85',1);}
 if(a==='exit')finish(true);
}
function openJourneyChoice(kind){state='choice';clearInputs();$('#journeyChoice').hidden=false;$('#journeyChoiceTitle').textContent=kind==='route'?'Deux horizons, un seul voyage.':'Le don de l’escale';const choices=kind==='route'?[['sun','Le Couchant','Archers et rafales sèches ; le cœur sera moins exposé.'],['storm','L’Orage','Oracles et pluies électriques ; le cœur recevra une protection.']]:[['heal','La sève','Soigne tout le groupe et restaure le cœur.'],['ward','Le dernier lien','Renforce le cœur de 60 points pour la traversée finale.']];const container=$('#journeyChoices');container.replaceChildren();for(const [id,title,description]of choices){const button=document.createElement('button');button.className='heroCard';const strong=document.createElement('strong'),small=document.createElement('small');strong.textContent=title;small.textContent=description;button.append(strong,small);button.onclick=()=>{if(kind==='route'){journey.route=id;if(id==='storm')journey.core=220;}else{journey.core=id==='ward'?Math.max(180,journey.core)+60:180;p.hp=p.max;for(const a of localParty)a.hp=a.max;}$('#journeyChoice').hidden=true;state='playing';releaseMenuFocus();advanceJourney();};container.append(button);}}
function updateJourneyBoss(e,dt){
 e.timer-=dt;e.root.rotation.y=Math.atan2(e.x-p.x,e.z-p.z);const phase=e.hp<e.max*.3?3:e.hp<e.max*.65?2:1;
 if(phase>e.phase){e.phase=phase;journey.bossPhase=phase;effect(e.x,e.z,8,'#f4cb95',1);if(journey.arenaPillars)for(const pillar of journey.arenaPillars)pillar.visible=true;announce(journey.level===2?'Les racines soulèvent le terrain. Gardez un passage pour esquiver.':'Le Mange-Aube change de rythme. Le second impact suit le premier.');}
 if(e.timer<=0){if(e.mode==='idle'){e.mode='windup';e.windupTotal=e.timer=1.35;e.attackKind=(e.pattern++||0)%3;const target=enemyTarget(e);if(e.attackKind===0){addHazard(target.x,target.z,3.2,1.25,26);if(phase>=2)addHazard(target.x+4,target.z,2.3,1.8,20);}else if(e.attackKind===1){const dx=target.x-e.x,dz=target.z-e.z,d=Math.max(.1,Math.hypot(dx,dz));for(let i=1;i<7;i++)addHazard(e.x+dx/d*i*2.4,e.z+dz/d*i*2.4,1.4,1.2+i*.04,24);}else{addHazard(e.x,e.z,5.5,1.2,28);if(phase===3)for(const side of [-1,1])addHazard(target.x+side*3,target.z+3,2.2,1.7,22);}}
 else if(e.mode==='windup'){e.mode='recover';e.timer=phase===3?2.5:3.2;if(e.attackKind===2)for(let i=0;i<8;i++)enemyShot(e,i*Math.PI/4,5);}
 else{e.mode='idle';e.timer=1.1;}}
 e.root.position.set(e.x,0,e.z);e.robe.material=e.flash>0?red:e.mode==='recover'?bronze:e.roleMaterial||enemyArmor;
 if(journey.level===2&&localProfile.secret[0]&&!localProfile.secret[1]&&e.mode==='recover'){e.rig.arms[0].rotation.z=-.6;e.rig.arms[0].rotation.x=-1.2;}
}
function updateJourney(dt){
 journey.elapsed+=dt;campaign.time+=dt;const zone=world.zoneAt(p.x,p.z);if(zone!==campaign.zone){campaign.zone=zone;$('#chapter').textContent=CHAPTERS[journey.level].title+' · '+zone;$('#zoneBanner').textContent=zone;$('#zoneBanner').classList.remove('show');void $('#zoneBanner').offsetWidth;$('#zoneBanner').classList.add('show');}
 if(journey.level===2){if(journey.step===3&&journeyGroupClear())advanceJourney();if(journey.step===4&&p.z<-80)campaign.bossAwake=true;if(journey.step===4&&boss?.dead)advanceJourney();}
 else{
  if(journey.step===5&&p.z<-85)campaign.bossAwake=true;if(journey.step===5&&boss?.dead)advanceJourney();
  if(journey.step>=1&&p.z<7&&p.z>-18){const phase=t%8;if(phase>6)moveEntity(p,dt*(journey.route==='storm'?1.7:.9),0);if(phase>5&&phase<5.08)announce('La rafale arrive. Gardez le centre de l’échine.');}
 }
 for(const gate of journey.gates)gate.root.visible=!gate.open();
 const visibleGoals=journeyGoals();for(const node of journey.nodes){if(node.tag)node.tag.visible=distance(node,p)<5&&(visibleGoals.some(g=>g.targetId===node.id)||node.id==='secret-shore'&&localProfile.secret[0]&&localProfile.secret[1]&&!localProfile.secret[2]);node.crystal.rotation.y+=dt*.7;node.crystal.position.y=1.2+Math.sin(t*1.3+node.x)*.08;}
 updateLandmarkReadability();mapClock+=dt;if(mapClock>.15){drawCampaignMap($('#miniMap'));mapClock=0;}if(journey.core<=0&&journey.level===3){announce('Les liens ont cédé. Reprenez depuis la dernière ancre.');finish(false);}
}
function updateJourneyScenery(dt){
 if(journey.level<=1)return;const fog=journey.level===2?'#444448':journey.route==='storm'?'#3c465b':'#675343';scene.fog.color.lerp(new THREE.Color(fog),1-Math.exp(-dt));scene.background.lerp(new THREE.Color(journey.level===2?'#a3907a':'#af8262'),1-Math.exp(-dt));scene.fog.density=.012;
 if(journey.detailRoot)journey.detailRoot.visible=quality!=='light';if(journey.foliage)journey.foliage.rotation.y=Math.sin(t*.1)*.001;if(journey.banners)journey.banners.rotation.z=Math.sin(t*.9)*.002;if(journey.particles){journey.particles.visible=quality!=='light';journey.particles.position.x=Math.sin(t*.2)*3;journey.particles.position.y=Math.sin(t*.17);}
 if(journey.water)journey.water.material.uniforms.waterTime.value=t;if(journey.backdrop&&journey.step>0)journey.backdrop.children.forEach((m,i)=>m.position.z=-135+((t*2+i*10)%200));
 for(const leg of journey.legs)leg.mesh.rotation.z=leg.side*(.2+Math.sin(t*1.5+leg.index)*.12);
}
function onJourneyHazard(h){if(journey.level===3&&journey.step===4&&!h.coreChecked&&Math.hypot(h.x,h.z+73)<h.r+1.5){h.coreChecked=true;journey.core=Math.max(0,journey.core-h.damage*.65);effect(0,-73,2,'#ff8b6c');}}
function restoreJourney(){const step=journey.checkpoint,level=journey.level;enterChapter(level,step);}
function recordChapterWin(){const level=journey.level||1;if(!localProfile.completed.includes(level))localProfile.completed.push(level);localProfile.stats.wins++;localProfile.stats.kills+=kills;localProfile.stats.seconds+=Math.round(campaign.activeSeconds||campaign.time);localProfile.journey=level<3?{level:level+1,hero,boon,checkpoint:0}:null;persistProfile();}
