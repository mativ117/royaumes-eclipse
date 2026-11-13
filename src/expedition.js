'use strict';
const RUN_KEY='royaumes-eclipse-run-09';
const LAMPS=[{id:'Aube',x:19,z:-9,color:'#ffc783'},{id:'Cendre',x:16,z:-21,color:'#91dce5'},{id:'Nuit',x:19,z:-31,color:'#c5a6ff'}];
const VALVES=[{id:'one',x:26,z:-47},{id:'two',x:53,z:-47},{id:'three',x:39,z:-68}];
const ESCORT_PATH=[{x:-20,z:-14,gate:'escort0'},{x:-18,z:-24},{x:-18,z:-32,gate:'escort1'},{x:0,z:-38}];
function freshTrials(){
 const orders=[['Aube','Cendre','Nuit'],['Nuit','Aube','Cendre'],['Cendre','Nuit','Aube']];
 return {escort:{started:false,waypoint:0,x:-20,z:-8,done:false},bells:{order:orders[Math.floor(Math.random()*orders.length)],step:0,done:false,read:false},archive:false,forge:{valves:[],carrying:false,x:54,z:-68,done:false},ritual:[],extraction:false};
}
function retitleWorldLabel(model,text){const texture=model.tag.material.map,c=texture.image,g=c.getContext('2d');g.clearRect(0,0,c.width,c.height);g.fillStyle='#100d19d9';g.fillRect(0,0,c.width,c.height);g.font='bold 30px system-ui';g.textAlign='center';g.fillStyle='#f5d5a8';g.fillText(text,256,60,480);texture.needsUpdate=true;}
function trialActive(e){
 if(!campaign?.trials)return true;
 const q=campaign.trials;
 if(e.stage==='escort0')return q.escort.started;
 if(e.stage==='escort1')return q.escort.started&&q.escort.waypoint>=2;
 if(e.stage==='shades')return campaign.keys.size===2;
 if(e.stage==='final-adds')return (campaign.bossAwake&&boss?.phase>=2)||q.extraction;
 if(e.stage==='vault')return campaign.keys.size===2;
 if(e.stage==='ritual')return q.ritual.length===2;
 return true;
}
function trialDead(stage){return ENCOUNTERS.filter(e=>e.stage===stage).every(e=>campaign.defeated.has(e.id));}
function buildTrials(){
 campaign.trialModels=[];campaign.ventModels=[];
 const q=campaign.trials;
 const soul=makeShrine(q.escort.x,q.escort.z,'#85f0d0',q.escort.done?'ANCRE DE RETOUR':'ÂME ÉGARÉE');soul.root.children[0].visible=false;soul.crystal.geometry=sphereGeo;soul.crystal.userData.ownedGeometry=false;soul.crystal.scale.setScalar(.4);campaign.soul=soul;campaign.trialModels.push(soul);
 for(const lamp of LAMPS){const m=makeShrine(lamp.x,lamp.z,lamp.color,lamp.id.toUpperCase());m.id=lamp.id;m.kind='lamp';campaign.trialModels.push(m);}
 const fresco=makeShrine(16,-7,'#cfb99c','FRESQUE');fresco.kind='fresco';campaign.trialModels.push(fresco);
 const archive=makeShrine(-52,-68,'#c7a4ff','LENTILLE');archive.kind='archive';archive.root.visible=!q.archive;campaign.trialModels.push(archive);
 for(const valve of VALVES){const m=makeShrine(valve.x,valve.z,'#ffb175','VANNE');m.kind='valve';m.id=valve.id;campaign.trialModels.push(m);
  const warning=box(new THREE.MeshBasicMaterial({color:'#ff6842',transparent:true,opacity:.1,depthWrite:false}),valve.x,.05,valve.z-4,5,.02,4);warning.userData.ownedMaterial=true;roomObject(warning);campaign.ventModels.push({mesh:warning,x:valve.x,z:valve.z-4,id:valve.id,offset:campaign.ventModels.length});}
 const core=makeShrine(q.forge.x,q.forge.z,'#ffad5d','NOYAU');core.kind='core';core.root.visible=!q.forge.done&&!q.forge.carrying;campaign.core=core;campaign.trialModels.push(core);
 for(const seal of SEALS){const m=makeShrine(seal.x,seal.z,'#addef5','RITUEL');m.kind='ritual';m.id=seal.id;campaign.trialModels.push(m);}
}
function trialTarget(){
 const q=campaign.trials;
 if(q.forge.carrying)return {type:'drop-core',label:'Poser le noyau'};
 const e=q.escort;
 if(!e.done&&distance(p,e)<2.8)return {type:'soul',label:e.started?'Guider l’âme vers le refuge':'Accueillir l’âme'};
 for(const m of campaign.trialModels){
  if(!m.root.visible||distance(p,m)>2.7)continue;
  if(m.kind==='fresco')return {type:'fresco',label:'Lire la fresque'};
  if(m.kind==='lamp'&&!q.bells.done)return {type:'lamp',id:m.id,label:'Accorder · '+m.id};
  if(m.kind==='valve'&&!q.forge.valves.includes(m.id))return{type:'valve',id:m.id,label:'Fermer la vanne'};
  if(m.kind==='core'&&!q.forge.done)return{type:'core',label:q.forge.valves.length===3?'Transporter le noyau':'Désactiver les 3 vannes'};
  if(m.kind==='archive'&&!q.archive)return{type:'archive',label:trialDead('shades')?'Prendre la lentille':'Affronter les trois Reflets'};
  if(m.kind==='ritual'&&!q.ritual.includes(m.id))return{type:'ritual',id:m.id,label:'Charger le sceau'};
 }
 const camp=CAMPS.find(c=>campaign.completed.has('camp-'+c.id)&&distance(p,c)<2.7);
 if(camp&&!campaign.bossAwake)return{type:'rest',camp,label:'Se reposer et sauvegarder'};
 return null;
}
function trialInteract(target){
 const q=campaign.trials;
 if(target.type==='soul'){q.escort.started=true;announce('Restez près de l’âme. Elle attendra que les embuscades soient dispersées.');return;}
 if(target.type==='fresco'){q.bells.read=true;announce('La fresque chante : '+q.bells.order.join(' → ')+'. Accordez ces trois lanternes dans cet ordre.');return;}
 if(target.type==='lamp'){
  if(target.id===q.bells.order[q.bells.step]){q.bells.step++;tone(400+q.bells.step*150,.22);effect(p.x,p.z,2,'#a5f0e6');
   if(q.bells.step===3){q.bells.done=true;campaign.keys.add('east');announce('Le carillon retrouve sa voix. Empreinte du cloître obtenue.');}else announce(`Accord juste · ${q.bells.step}/3`);
  }else{q.bells.step=0;addHazard(p.x,p.z,2.4,1.1,16);announce('L’accord se brise. Relisez la fresque, puis recommencez.');}return;
 }
 if(target.type==='valve'){q.forge.valves.push(target.id);effect(p.x,p.z,3,'#ffca88');announce(`Vanne fermée · ${q.forge.valves.length}/3`);return;}
 if(target.type==='core'){
  if(q.forge.valves.length<3){announce('Le noyau est encore sous pression : fermez les trois vannes.');return;}
  q.forge.carrying=true;campaign.core.root.visible=false;announce('Rapportez le noyau au refuge de la croisée. Attaquer, esquiver ou subir un coup le fera tomber.');return;
 }
 if(target.type==='drop-core'){dropCore();return;}
 if(target.type==='archive'){
  if(!trialDead('shades')){announce('Les trois Reflets gardent la lentille. Ils se matérialisent pour attaquer ; votre pouvoir les révèle aussi.');return;}
  q.archive=true;campaign.trialModels.find(m=>m.kind==='archive').root.visible=false;p.hp=Math.min(p.max,p.hp+30);announce('Lentille des mémoires obtenue. Apportez sa lumière au sceau de l’ouest dans la nef.');return;
 }
 if(target.type==='ritual'){
  if(target.id==='west'&&!q.archive){announce('Ce sceau attend la lentille des Archives du Reflet, à l’ouest.');return;}
  if(target.id==='east'&&!q.forge.done){announce('Ce sceau attend le noyau de la forge, à l’est. Ramenez-le d’abord au refuge.');return;}
  q.ritual.push(target.id);effect(p.x,p.z,6,'#a4e7ff',1);
  announce(q.ritual.length===2?'Le Carillonneur s’éveille. Brisez ses deux chaînes, puis affrontez-le.':'Premier sceau chargé. L’autre attend son offrande.');return;
 }
 if(target.type==='rest'){
  if(enemies.some(e=>!e.dead&&trialActive(e)&&distance(e,p)<10)){announce('Écartez les ennemis proches avant de vous reposer.');return;}
  snapshotCampaign(target.camp);return;
 }
}
function dropCore(){
 const q=campaign?.trials?.forge;if(!q?.carrying)return;
 q.carrying=false;q.x=p.x;q.z=p.z;campaign.core.x=p.x;campaign.core.z=p.z;campaign.core.root.position.set(p.x,0,p.z);campaign.core.root.visible=true;campaign.core.tag.position.set(p.x,3.6,p.z);
 effect(p.x,p.z,1.5,'#ffb36c');
}
function shadeVulnerable(e){return e.reveal>0||e.mode!=='idle'||(t+(e.phaseOffset||0))%6>3.8;}
function revealShades(){for(const e of enemies)if(e.type==='shade'&&distance(e,p)<12){e.reveal=5;effect(e.x,e.z,2,'#c4a5ff',.4)}}
function updateShade(e,dt){
 e.reveal=Math.max(0,(e.reveal||0)-dt);e.timer-=dt;const target=enemyTarget(e);e.root.rotation.y=Math.atan2(e.x-target.x,e.z-target.z);
 const visible=shadeVulnerable(e);e.robe.material.opacity=visible?1:.18;
 if(e.mode==='idle'&&e.timer<=0&&visible&&distance(e,target)<15){e.mode='windup';e.timer=.85;e.dx=target.x-e.x;e.dz=target.z-e.z;const d=Math.max(.1,Math.hypot(e.dx,e.dz));e.dx/=d;e.dz/=d;effect(e.x,e.z,2,'#c5a4ff',.85);}
 else if(e.mode==='windup'&&e.timer<=0){e.mode='charge';e.timer=.4;}
 else if(e.mode==='charge'){moveEntity(e,e.dx*11*dt,e.dz*11*dt,.55);if(distance(e,p)<1.5)hurt(18);if(e.timer<=0){e.mode='recover';e.timer=1.3;}}
 else if(e.mode==='recover'&&e.timer<=0){e.mode='idle';e.timer=1.4;}
 e.root.position.set(e.x,Math.sin(t*3)*.1,e.z);
}
function updatePorter(e,dt){
 e.timer-=dt;e.root.rotation.y=Math.atan2(e.x-p.x,e.z-p.z);
 if(e.mode==='idle'&&e.timer<=0){e.mode='windup';e.timer=1.1;addHazard(p.x,p.z,3,1.05,25);}
 else if(e.mode==='windup'&&e.timer<=0){e.mode='recover';e.timer=2.2;}
 else if(e.mode==='recover'&&e.timer<=0){e.mode='idle';e.timer=1.1;}
}
function updateTrials(dt){
 const q=campaign.trials,e=q.escort;
 if(e.started&&!e.done){
  const waypoint=ESCORT_PATH[e.waypoint];
  if(distance(e,p)<12){
   if(distance(e,waypoint)>.7)steerToward(e,waypoint,dt,2.6);
   else if(!waypoint.gate||trialDead(waypoint.gate)){
    e.waypoint++;
    if(e.waypoint===ESCORT_PATH.length){e.done=true;e.x=0;e.z=-38;campaign.keys.add('west');retitleWorldLabel(campaign.soul,'ANCRE DE RETOUR');announce('L’âme a rejoint le refuge. Empreinte des jardins obtenue.');}
   }
  }
  campaign.soul.x=e.x;campaign.soul.z=e.z;campaign.soul.root.position.set(e.x,0,e.z);campaign.soul.tag.position.set(e.x,3.6,e.z);
 }
 for(const v of campaign.ventModels){const active=!q.forge.valves.includes(v.id)&&((t+v.offset*1.1)%4)>2;v.mesh.material.opacity=q.forge.valves.includes(v.id)?.03:active?.7:.14;if(active&&Math.abs(p.x-v.x)<2.5&&Math.abs(p.z-v.z)<2)hurt(18);}
 if(q.forge.carrying&&distance(p,CAMPS[0])<3){q.forge.carrying=false;q.forge.done=true;campaign.core.root.visible=false;snapshotCampaign(CAMPS[0]);announce('Noyau stabilisé au refuge. Le sceau oriental peut maintenant être chargé.');}
 for(const model of campaign.trialModels)if(model.tag)model.tag.visible=model.root.visible&&distance(p,model)<20;
 const anchorAlive=enemies.some(a=>a.type==='anchor'&&!a.dead);
 const porter=enemies.find(a=>a.type==='porter'&&!a.dead);if(porter)porter.robe.material=anchorAlive?enemyArmor:bronze;
 if(q.extraction){
  campaign.escapeLeft=Math.max(0,campaign.escapeLeft-dt);
  if(distance(p,CAMPS[0])<3){finish(true);}
  else if(campaign.escapeLeft<=0){announce('La faille s’est refermée. Reprenez depuis votre dernier refuge.');finish(false);}
 }
}
function startExtraction(){
 if(campaign.trials.extraction)return;
 campaign.trials.extraction=true;campaign.escapeLeft=70;clearHazards();p.hp=p.max;p.power=0;campaign.bossAwake=false;
 snapshotCampaign({id:'return',x:0,z:-100});
 announce('Le Veilleur tombe, mais la cour s’effondre. L’âme que vous avez guidée maintient une ancre au refuge de la croisée. Rejoignez-la avant la fermeture !');
}
function saveRun(){
 if(!campaign?.checkpoint)return;
 try{localStorage.setItem(RUN_KEY,JSON.stringify({version:'0.9',hero,boon,snapshot:campaign.checkpoint,time:campaign.activeSeconds||campaign.time,deaths:campaign.deaths||0}));$('#continueRun').hidden=false;}catch(_){}
}
function readRun(){
 try{
  const raw=localStorage.getItem(RUN_KEY);if(!raw||raw.length>60000)return null;
  const d=JSON.parse(raw),s=d.snapshot,q=s?.trials;
  if(d.version!=='0.9'||!['rempart','voltigeur'].includes(d.hero)||!['vigor','haste'].includes(d.boon)||!q?.escort||!q?.bells||!q?.forge||!Array.isArray(q.ritual))return null;
  if(!Number.isFinite(s.x)||!Number.isFinite(s.z)||!world.onGround(s.x,s.z))return null;
  if(!Array.isArray(s.keys)||s.keys.some(x=>!['west','east'].includes(x))||!Array.isArray(s.completed)||!Array.isArray(s.dead)||s.dead.some(id=>!ENCOUNTERS.some(e=>e.id===id)))return null;
  if(!Array.isArray(q.bells.order)||q.bells.order.length!==3||new Set(q.bells.order).size!==3||q.bells.order.some(x=>!LAMPS.some(l=>l.id===x)))return null;
  if(!Number.isInteger(q.bells.step)||q.bells.step<0||q.bells.step>3||!q.bells.done&&q.bells.step===3)return null;
  if(!Number.isInteger(q.escort.waypoint)||q.escort.waypoint<0||q.escort.waypoint>4||!q.escort.done&&q.escort.waypoint===4)return null;
  if(!Number.isFinite(q.escort.x)||!Number.isFinite(q.escort.z)||!Array.isArray(q.forge.valves)||q.forge.valves.some(x=>!VALVES.some(v=>v.id===x)))return null;
  if(q.ritual.some(x=>!['west','east'].includes(x)))return null;
  return d;
 }catch(_){return null;}
}
function continueRun(){
 const saved=readRun();if(!saved)return;
 hero=saved.hero;start();boon=saved.boon;p.max=HEROES[hero].hp+(boon==='vigor'?40:-30);campaign.checkpoint=saved.snapshot;campaign.time=Math.max(0,Number(saved.time)||0);campaign.activeSeconds=campaign.time;campaign.deaths=Math.max(0,Number(saved.deaths)||0);restoreCampaign();updateHUD();
}
function wireExpeditionUI(){
 $('#continueRun').hidden=!readRun();$('#continueRun').onclick=continueRun;
 $('#copyReport').onclick=async()=>{const text=expeditionReport();try{await navigator.clipboard.writeText(text);$('#copyReport').textContent='Bilan copié';}catch(_){$('#endText').textContent+=' '+text;}};
}
function expeditionReport(){return JSON.stringify({version:'0.10',hero,serment:boon,activeSeconds:Math.round(campaign.activeSeconds||campaign.time),deaths:campaign.deaths||0,kills,finished:state==='won',chapters:campaign.chapterTimes||{}},null,2)}
