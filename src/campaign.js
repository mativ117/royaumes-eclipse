'use strict';
let campaign=null,mapPreviousState='playing',mapClock=0;
const CAMPS=[{id:'crossing',x:0,z:-38},{id:'threshold',x:0,z:-71}];
const SEALS=[{id:'west',x:-9,z:-62},{id:'east',x:9,z:-55}];
const ENCOUNTERS=[
 {id:'garden-guard',x:-20,z:-17,type:'sentinel',stage:'escort0'},
 {id:'garden-hunter',x:-19,z:-20,type:'warden',stage:'escort0'},
 {id:'garden-archer',x:-24,z:-29,type:'archer',stage:'escort1'},
 {id:'garden-hunter-two',x:-17,z:-32,type:'warden',stage:'escort1'},
 {id:'cloister-oracle',x:19,z:-14,type:'oracle'},
 {id:'cloister-hunter',x:20,z:-25,type:'warden'},
 {id:'cloister-archer',x:19,z:-33,type:'archer'},
 {id:'crossing-hunter',x:10,z:-35,type:'warden'},
 {id:'crossing-archer',x:-18,z:-35,type:'archer'},
 {id:'archive-one',x:-54,z:-51,type:'shade',stage:'shades'},
 {id:'archive-two',x:-40,z:-67,type:'shade',stage:'shades'},
 {id:'archive-three',x:-27,z:-53,type:'shade',stage:'shades'},
 {id:'forge-archer',x:34,z:-60,type:'archer',stage:'vault'},
 {id:'forge-archer-two',x:52,z:-58,type:'archer',stage:'vault'},
 {id:'forge-guard',x:43,z:-64,type:'sentinel',stage:'vault'},
 {id:'nef-archer',x:-10,z:-49,type:'archer',stage:'vault'},
 {id:'nef-oracle',x:10,z:-59,type:'oracle',stage:'vault'},
 {id:'carillonneur',x:0,z:-65,type:'porter',stage:'ritual'},
 {id:'chain-west',x:-10,z:-66,type:'anchor',stage:'ritual'},
 {id:'chain-east',x:10,z:-66,type:'anchor',stage:'ritual'},
 {id:'court-oracle-west',x:-15,z:-94,type:'oracle',stage:'final-adds'},
 {id:'court-oracle-east',x:15,z:-98,type:'oracle',stage:'final-adds'},
 {id:'keeper',x:0,z:-94,type:'boss'}
];
function campaignGateClosed(gate){
 if(!campaign)return false;
 return gate==='pact'?!boon:gate==='ritual-entry'?campaign.keys.size<2:gate==='seals'?campaign.trials.ritual.length<2||!campaign.defeated.has('carillonneur'):gate==='boss'?campaign.bossAwake&&!boss?.dead:false;
}
function resetHeroAt(x,z){
 p.x=x;p.z=z;p.vx=p.vz=0;p.hp=p.max;
 for(const k of ['shot','dash','dashT','power','shield','recoil','overcharge','absorbLock','leap','swing','combo','comboWindow','stagger'])p[k]=0;
 p.attack=null;p.attackBuffer=0;p.inv=1.5;aim=targetAim=0;player.root.position.set(x,0,z);
 camera.position.set(x,innerWidth<innerHeight?19:13,z+18);cameraLook.set(x,1,z-4);
}
function beginCampaign(){
 t=0;campaign={keys:new Set(),completed:new Set(),checkpoint:null,bossAwake:false,zone:'',collectibles:[],campModels:[],traps:[],time:0,activeSeconds:0,deaths:0,chapterTimes:{},defeated:new Set(),trials:freshTrials()};
 rebuildCampaign();resetHeroAt(0,23);
 announce('La route se divise. Choisissez un serment dans l’atrium, puis explorez les jardins à l’ouest ou le cloître à l’est.');
}
function rebuildCampaign(snapshot=null){
 clearRoom();obstacles=world.obstacles.slice();
 campaign.collectibles=[];campaign.campModels=[];campaign.traps=[];campaign.safeMarkers=[];campaign.bossAwake=false;campaign.zone='';
 if(snapshot){campaign.keys=new Set(snapshot.keys);campaign.completed=new Set(snapshot.completed);campaign.defeated=new Set(snapshot.dead);campaign.trials=JSON.parse(JSON.stringify(snapshot.trials));campaign.trials.forge.carrying=false;campaign.escapeLeft=70;kills=snapshot.kills;}
 portal.visible=false;
 shrines=[makeShrine(-9,7,'#7ee2ff','BRAISE'),makeShrine(9,7,'#c4a1ff','ÉLAN')];
 if(boon)shrines.forEach(q=>q.root.visible=false);
 for(const definition of ENCOUNTERS){
  if(snapshot?.dead.includes(definition.id)&&definition.type!=='boss')continue;
  const e=spawn(definition.x,definition.z,definition.type);e.id=definition.id;e.stage=definition.stage;
  if(e.type==='boss'){boss=e;e.hp=e.max=1300;e.timer=2;e.mode='idle';e.pattern=0;e.phase=1;if(snapshot?.dead.includes(e.id)){e.dead=true;cleanupObject(e.root);}}
 }
 const relic=makeShrine(-25,-27,'#d3afff','RELIQUE');relic.id='garden-relic';relic.kind='relic';relic.root.visible=!campaign.completed.has(relic.id);campaign.collectibles.push(relic);
 for(const point of CAMPS){
  const q=makeShrine(point.x,point.z,'#88e0c9','REFUGE');q.id=point.id;q.crystal.geometry=sphereGeo;q.crystal.userData.ownedGeometry=false;q.crystal.scale.setScalar(.4);q.crystal.position.y=1;const pool=mesh(cylGeo,cyan,0,.5,0,1.1,.06,1.1,q.root);campaign.campModels.push(q);
 }
 buildMirror(-23,-29);buildBell(9,-82);
 // The three hazards now belong to the nave, with visible safe gaps.
 for(let i=0;i<3;i++){
  const z=-45-i*8,gap=boon==='vigor'?0:(i%2===0?-6:6);
  for(const [a,b] of [[-14,gap-2.5],[gap+2.5,14]]){
   const q=box(new THREE.MeshBasicMaterial({color:'#f69b5b',transparent:true,opacity:.1,depthWrite:false}),(a+b)/2,.045,z,b-a,.025,1.1);
   q.userData.ownedMaterial=true;q.userData.z=z;q.userData.gap=gap;q.userData.side=a===-14?0:1;roomObject(q);campaign.traps.push(q);
  }
  const q=box(new THREE.MeshBasicMaterial({color:'#8de7eb',transparent:true,opacity:.45}),gap,.05,z,4.5,.02,.2);q.userData.ownedMaterial=true;q.userData.row=i;roomObject(q);campaign.safeMarkers.push(q);
 }
 buildTrials();dressLandmarks();
 // Visual gates follow collision state; they do not rebuild the scene each frame.
 updateCampaignGates();
}
function snapshotCampaign(point){
 campaign.checkpoint={id:point.id,x:point.x,z:point.z+2,keys:[...campaign.keys],completed:[...campaign.completed],dead:[...campaign.defeated],trials:JSON.parse(JSON.stringify(campaign.trials)),kills};
 p.hp=p.max;p.power=0;p.inv=1.5;saveRun();
 effect(point.x,point.z,4,'#8dffe2',.8);tone(650,.25);
 announce('Refuge atteint : santé restaurée et point de reprise enregistré pour cette expédition.');
}
function restoreCampaign(){
 const saved=campaign.checkpoint;
 if(saved){rebuildCampaign(saved);resetHeroAt(saved.x,saved.z);}
 else {campaign.keys=new Set();campaign.completed=new Set();campaign.defeated=new Set();campaign.trials=freshTrials();kills=0;rebuildCampaign();resetHeroAt(0,23);}
}
function updateCampaignGates(){for(const o of world.obstacles)if(o.gate)o.mesh.visible=campaignGateClosed(o.gate);}
function objectiveTargets(){
 const q=campaign.trials;
 if(!boon)return[{x:-9,z:7},{x:9,z:7}];
 if(campaign.keys.size<2){const targets=[];if(!q.escort.done)targets.push(q.escort);if(!q.bells.done)targets.push(...(!q.bells.read?[{x:16,z:-7}]:LAMPS));return targets;}
 if(!q.archive||!q.forge.done){const targets=[];if(!q.archive)targets.push(...(trialDead('shades')?[{x:-52,z:-68}]:enemies.filter(e=>e.stage==='shades'&&!e.dead)));if(!q.forge.done)targets.push(q.forge.carrying?CAMPS[0]:q.forge.valves.length<3?VALVES.find(v=>!q.forge.valves.includes(v.id)):q.forge);return targets;}
 if(q.ritual.length<2)return SEALS.filter(qs=>!q.ritual.includes(qs.id));
 if(!campaign.defeated.has('carillonneur'))return enemies.filter(e=>e.stage==='ritual'&&!e.dead);
 if(q.extraction)return[CAMPS[0]];
 if(!campaign.bossAwake)return[{x:0,z:-77}];
 return[boss];
}
function updateCampaign(dt){
 campaign.time+=dt;for(const q of [...shrines,...campaign.collectibles,...campaign.campModels])if(q.tag)q.tag.visible=q.root.visible&&distance(p,q)<22;
 const zone=world.zoneAt(p.x,p.z);
 room=p.z<-74?2:p.z<-28?1:0;
 if(zone!==campaign.zone){campaign.zone=zone;if(!(zone in campaign.chapterTimes))campaign.chapterTimes[zone]=Math.round(campaign.activeSeconds||campaign.time);$('#chapter').textContent=zone;$('#zoneBanner').textContent=zone;$('#zoneBanner').classList.remove('show');void $('#zoneBanner').offsetWidth;$('#zoneBanner').classList.add('show');}
 if(!campaign.bossAwake&&!boss.dead&&!campaign.trials.extraction&&p.z<-76){campaign.bossAwake=true;p.inv=Math.max(1,p.inv);announce('Le Veilleur ferme la cour. La cloche à l’est peut interrompre son assaut une seule fois.');}
 for(const item of campaign.collectibles){
  if(!item.root.visible||distance(p,item)>1.9)continue;
  item.root.visible=false;
  if(item.kind==='seal'){campaign.keys.add(item.id);effect(item.x,item.z,3,'#91e6ff');tone(800,.16);announce(campaign.keys.size===2?'Deux sceaux réunis. Le seuil du Veilleur est ouvert, au nord.':'Premier sceau retrouvé. Explorez l’autre côté de la nef.');}
  else {campaign.completed.add(item.id);p.overcharge=3;p.hp=Math.min(p.max,p.hp+20);announce('Relique des jardins : prochaine attaque renforcée et 20 PV récupérés.');}
 }
 for(const point of CAMPS){
  if(point.id==='threshold'&&!campaign.defeated.has('carillonneur'))continue;
  if(!campaign.completed.has('camp-'+point.id)&&distance(p,point)<2.8){campaign.completed.add('camp-'+point.id);snapshotCampaign(point);}
 }
 const cycle=t%5,active=cycle>2.1&&cycle<(boon==='vigor'?3.65:3),warning=cycle>1&&cycle<=2.1;
 for(const trap of campaign.traps){trap.material.opacity=active?.7:warning?.22:.06;trap.material.color.set(active?'#ff5635':warning?'#ffae65':'#7bc4c9');if(active&&Math.abs(p.z-trap.userData.z)<.65&&Math.abs(p.x-trap.userData.gap)>2.3)hurt(22);}
 updateTrials(dt);if(boss?.dead){portal.visible=true;startExtraction();}
 updateCampaignGates();updateLandmarkReadability();
 mapClock+=dt;if(mapClock>.12){drawCampaignMap($('#miniMap'));mapClock=0;}
 return false;
}
function steerToward(e,target,dt,speed=2.8){
 const a=Math.atan2(target.z-e.z,target.x-e.x);
 for(const offset of [0,.55,-.55,1.1,-1.1,1.6,-1.6]){
  const dx=Math.cos(a+offset)*speed*dt,dz=Math.sin(a+offset)*speed*dt;
  if(!blocked(e.x+dx*4,e.z+dz*4,.55)){moveEntity(e,dx,dz,.55);return;}
 }
}
function updateOracle(e,dt){
 if(e.mode==='idle'&&distance(e,p)>18&&e.alert>0)steerToward(e,p,dt,1.5);
 e.timer-=dt;e.root.rotation.y+=dt*.6;
 if(e.mode==='recover'){if(e.timer<=0){e.mode='idle';e.timer=1.3;}return;}
 if(e.mode==='windup'){if(e.timer<=0){e.mode='recover';e.timer=2.2;}return;}
 if(e.timer<=0&&distance(e,p)<19){
  const target=enemyTarget(e);e.mode='windup';e.timer=1.3;
  addHazard(target.x,target.z,2.4,1.25,23,'#d982de');
  if(e.hp<e.max*.6)addHazard(target.x+2,target.z+2,1.7,1.6,18,'#d982de');
  effect(e.x,e.z,1.7,'#d89bff',1.2);
 }
}
function drawCampaignMap(canvas){
 if(!canvas||!campaign||!p)return;
 const ctx=canvas.getContext('2d'),W=canvas.width,H=canvas.height,large=W>300,pad=large?34:13,s=Math.min((W-pad*2)/128,(H-pad*2)/146),ox=W/2;
 const X=x=>ox+x*s,Z=z=>pad+(z+112)*s;
 ctx.fillStyle='#10131d';ctx.fillRect(0,0,W,H);
 // Ground, void and solid cover are distinct. The map uses the same obstacles as movement.
 for(const region of world.regions){ctx.fillStyle=region.name==='Archives'?'#3b405a':region.name==='Forge'?'#554231':'#3f4755';ctx.fillRect(X(region.x0),Z(region.z0),(region.x1-region.x0)*s,(region.z1-region.z0)*s);ctx.strokeStyle='#9ca9bc';ctx.lineWidth=large?1.5:.7;ctx.strokeRect(X(region.x0),Z(region.z0),(region.x1-region.x0)*s,(region.z1-region.z0)*s);}
 for(const o of obstacles){if(o.gate&&!campaignGateClosed(o.gate))continue;ctx.fillStyle=o.gate?'#f5c285':'#171c29';ctx.fillRect(X(o.x-o.w/2),Z(o.z-o.d/2),Math.max(large?2:1,o.w*s),Math.max(large?2:1,o.d*s));}
 const goal=selectedMission(),route=guideRoute(goal);
 if(guidanceOn&&route.length){ctx.strokeStyle='#ffe3a2';ctx.lineWidth=large?3:1.5;ctx.setLineDash(large?[7,5]:[3,2]);ctx.beginPath();route.forEach((q,i)=>i?ctx.lineTo(X(q.x),Z(q.z)):ctx.moveTo(X(q.x),Z(q.z)));ctx.stroke();ctx.setLineDash([]);}
 function caption(text,x,z){ctx.font=`600 ${large?18:9}px system-ui`;const w=ctx.measureText(text).width;ctx.fillStyle='#10131ded';ctx.fillRect(X(x)-w/2-6,Z(z)-15,w+12,22);ctx.fillStyle='#e8edf7';ctx.textAlign='center';ctx.fillText(text,X(x),Z(z)+1);}
 if(large){for(const [name,x,z]of[['ATRIUM',0,26],['JARDINS',-18,-31],['CLOÎTRE',18,-30],['CROISÉE',0,-38],['ARCHIVES',-40,-71],['FORGE',39,-71],['NEF',0,-47],['COUR DU VEILLEUR',0,-107]])caption(name,x,z);}
 for(const camp of CAMPS){const visited=campaign.completed.has('camp-'+camp.id);mapGlyph(ctx,'camp',X(camp.x),Z(camp.z),large?7:3.5,visited?'#97efd7':'#acb9c9',visited);}
 const goals=missionGoals();for(const g of goals){const selected=g.id===goal?.id;if(selected){ctx.strokeStyle='#fff6de';ctx.lineWidth=large?2:1;ctx.beginPath();ctx.arc(X(g.x),Z(g.z),large?13:6.5,0,Math.PI*2);ctx.stroke();}mapGlyph(ctx,g.kind,X(g.x),Z(g.z),large?7:3.5,SIGN_COLORS[g.kind]||'#ffe0a0');}
 if(mapThreats)for(const e of enemies)if(!e.dead&&trialActive(e)&&distance(e,p)<17)mapGlyph(ctx,'enemy',X(e.x),Z(e.z),large?4:2,'#ffac9a');
 ctx.save();ctx.translate(X(p.x),Z(p.z));ctx.rotate(-aim);mapGlyph(ctx,'player',0,0,large?7:4,'#ffffff');ctx.restore();
 ctx.fillStyle='#f5e4c7';ctx.font=`600 ${large?17:11}px system-ui`;ctx.textAlign='right';ctx.fillText('N ↑',W-9,large?24:15);
 if(large){ctx.textAlign='left';ctx.font='16px system-ui';ctx.fillText('Vous : flèche blanche',16,H-12);}
}

function toggleMap(){
 if(state==='map'){state=mapPreviousState;$('#mapPanel').hidden=true;$('#mobile').classList.add('playing');last=performance.now();accumulator=0;return;}
 if(state!=='playing')return;
 mapPreviousState=state;state='map';clearInputs();$('#mapPanel').hidden=false;$('#mobile').classList.remove('playing');renderMissionJournal();drawCampaignMap($('#largeMap'));
}
function wireCampaignUI(){wireExpeditionUI();wireReadabilityUI();$('#mapButton').onclick=toggleMap;$('#closeMap').onclick=toggleMap;}
