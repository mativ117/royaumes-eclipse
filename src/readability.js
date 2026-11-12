'use strict';
// Shapes, words and colour share the same meaning on the map and in the world.
const SIGN_COLORS={soul:'#97efd7',lamp:'#ffe0a0',fresco:'#e8dcc8',archive:'#d9bcff',valve:'#ffca86',core:'#ffca86',ritual:'#a8e4ff',camp:'#97efd7',pact:'#ffe0a0',relic:'#d9bcff',boss:'#ffac9a'};
let trackedGoal='',guidanceOn=true,mapThreats=true,navCache=null,readabilityAssets=null;
try{guidanceOn=localStorage.getItem('royaumes-guidance')!=='off'}catch(_){}
function missionGoals(){
 if(!campaign||!p)return[];
 const q=campaign.trials,goal=(id,title,action,kind,point)=>({id,title,action,kind,...point});
 if(!boon)return[goal('braise','Serment de Braise','Examiner le don et sa contrepartie.','pact',{x:-9,z:7}),goal('elan','Serment d’Élan','Examiner le don et sa contrepartie.','pact',{x:9,z:7})];
 if(campaign.keys.size<2){const a=[];
  if(!q.escort.done){const remaining=enemies.filter(e=>!e.dead&&trialActive(e)&&e.stage===ESCORT_PATH[q.escort.waypoint]?.gate);a.push(goal('soul','L’âme des jardins',!q.escort.started?'Accueillir l’âme, puis rester près d’elle.':remaining.length&&distance(q.escort,ESCORT_PATH[q.escort.waypoint])<1.5?'Éliminer l’embuscade pour libérer l’âme.':'Accompagner l’âme jusqu’à la croisée.','soul',q.escort));}
  if(!q.bells.done){const next=LAMPS.find(l=>l.id===q.bells.order[q.bells.step]);a.push(goal('bells','Le carillon du cloître',q.bells.read?`Accorder ${next.id} · ${q.bells.step}/3 accords justes.`:'Lire la fresque pour connaître la mélodie.',q.bells.read?'lamp':'fresco',q.bells.read?next:{x:16,z:-7}));}return a;
 }
 if(!q.archive||!q.forge.done){const a=[];
  if(!q.archive){const foes=enemies.filter(e=>!e.dead&&e.stage==='shades').sort((a,b)=>distance(a,p)-distance(b,p));a.push(goal('archive','La lentille des Archives',foes.length?`Vaincre les Reflets · ${3-foes.length}/3. Le pouvoir les révèle.`:'Prendre la lentille au fond des Archives.','archive',foes[0]||{x:-52,z:-68}));}
  if(!q.forge.done){const valves=VALVES.filter(v=>!q.forge.valves.includes(v.id)).sort((a,b)=>distance(a,p)-distance(b,p));a.push(goal('forge','Le noyau de la forge',q.forge.carrying?'Rapporter le noyau au refuge de la croisée.':valves.length?`Fermer les vannes · ${q.forge.valves.length}/3.`:'Prendre le noyau, puis le rapporter au refuge.',q.forge.carrying?'camp':valves.length?'valve':'core',q.forge.carrying?CAMPS[0]:valves[0]||q.forge));}return a;
 }
 if(q.ritual.length<2)return SEALS.filter(s=>!q.ritual.includes(s.id)).map(s=>goal(s.id,'Sceau '+(s.id==='west'?'des mémoires':'du brasier'),'Charger le sceau avec l’offrande retrouvée.','ritual',s));
 if(!campaign.defeated.has('carillonneur')){const chains=enemies.filter(e=>e.type==='anchor'&&!e.dead).sort((a,b)=>distance(a,p)-distance(b,p));return[goal('porter','Le Carillonneur',chains.length?`Briser les chaînes · ${2-chains.length}/2.`:'Frapper le gardien pendant sa récupération.','boss',chains[0]||enemies.find(e=>e.type==='porter')||{x:0,z:-65})];}
 if(q.extraction)return[goal('return','L’ancre de retour',`Rejoindre l’âme au refuge · ${Math.ceil(campaign.escapeLeft)} s.`,'soul',CAMPS[0])];
 return[goal('boss','Le Veilleur du seuil',campaign.bossAwake?'Esquiver ses marques, puis frapper sa récupération.':'Traverser le seuil pour entrer dans la cour.','boss',campaign.bossAwake?boss:{x:0,z:-78})];
}
function selectedMission(){const goals=missionGoals();let goal=goals.find(g=>g.id===trackedGoal);if(!goal){goal=goals.slice().sort((a,b)=>distance(a,p)-distance(b,p))[0];trackedGoal=goal?.id||'';navCache=null;}return goal;}
function setTrackedGoal(id){trackedGoal=id;navCache=null;renderMissionJournal();drawCampaignMap($('#largeMap'));}
function mapGlyph(ctx,kind,x,y,r,color,filled=true){
 ctx.save();ctx.translate(x,y);ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=Math.max(1.5,r*.2);ctx.beginPath();
 if(kind==='player'){ctx.moveTo(0,-r*1.5);ctx.lineTo(r,r);ctx.lineTo(0,r*.55);ctx.lineTo(-r,r);ctx.closePath();}
 else if(kind==='camp'){ctx.rect(-r,-r,r*2,r*2);}
 else if(kind==='boss'||kind==='enemy'){ctx.moveTo(0,-r);ctx.lineTo(r,r);ctx.lineTo(-r,r);ctx.closePath();}
 else if(kind==='core'||kind==='pact'||kind==='relic'||kind==='ritual'){ctx.moveTo(0,-r*1.25);ctx.lineTo(r,0);ctx.lineTo(0,r*1.25);ctx.lineTo(-r,0);ctx.closePath();}
 else ctx.arc(0,0,r,0,Math.PI*2);
 if(filled)ctx.fill();else ctx.stroke();
 if(kind==='camp'){ctx.strokeStyle='#10151b';ctx.beginPath();ctx.moveTo(-r*.55,0);ctx.lineTo(r*.55,0);ctx.moveTo(0,-r*.55);ctx.lineTo(0,r*.55);ctx.stroke();}
 if(kind==='valve'||kind==='archive'){ctx.strokeStyle=filled?'#10151b':color;ctx.beginPath();ctx.moveTo(-r*.65,0);ctx.lineTo(r*.65,0);ctx.moveTo(0,-r*.65);ctx.lineTo(0,r*.65);ctx.stroke();}
 ctx.restore();
}
// A walkable route, never a straight line through the void or a closed gate.
function buildGuideRoute(goal){
 const W=129,H=143,N=W*H,idx=(x,z)=>(z+112)*W+x+64,point=i=>({x:i%W-64,z:Math.floor(i/W)-112});
 const sx=Math.round(p.x),sz=Math.round(p.z);if(sx<-64||sx>64||sz<-112||sz>30)return[];
 const queue=new Int32Array(N),parent=new Int32Array(N);parent.fill(-2);let head=0,tail=0,end=-1;
 const start=idx(sx,sz);queue[tail++]=start;parent[start]=-1;
 while(head<tail){const i=queue[head++],{x,z}=point(i);if(Math.hypot(x-goal.x,z-goal.z)<1.8&&!blocked(x,z,.55)){end=i;break;}
  for(const [dx,dz]of[[1,0],[-1,0],[0,-1],[0,1]]){const a=x+dx,b=z+dz;if(a<-64||a>64||b<-112||b>30)continue;const next=idx(a,b);if(parent[next]!==-2||blocked(a,b,.55))continue;parent[next]=i;queue[tail++]=next;}
 }
 if(end<0)return[];const route=[];while(end>=0){route.push(point(end));end=parent[end];}return route.reverse();
}
function guideRoute(goal=selectedMission()){
 if(!goal||!guidanceOn)return[];
 const key=[goal.id,Math.round(goal.x),Math.round(goal.z),boon,campaign.keys.size,campaign.trials.ritual.length,campaign.defeated.has('carillonneur'),campaign.bossAwake].join(':');
 if(!navCache||navCache.key!==key||Math.hypot(p.x-navCache.x,p.z-navCache.z)>3.5||t-navCache.time>2){navCache={key,x:p.x,z:p.z,time:t,route:buildGuideRoute(goal)};}
 return navCache.route;
}
function landmarkState(m){
 const q=campaign.trials;
 if(m.kind==='valve')return q.forge.valves.includes(m.id)?'done':'ready';
 if(m.kind==='lamp')return q.bells.done||q.bells.order.slice(0,q.bells.step).includes(m.id)?'done':'ready';
 if(m.kind==='ritual')return q.ritual.includes(m.id)?'done':(m.id==='west'?q.archive:q.forge.done)?'ready':'locked';
 if(m.kind==='core')return q.forge.valves.length===3?'ready':'locked';
 if(m.kind==='archive')return trialDead('shades')?'ready':'locked';
 return 'ready';
}
function getLandmarkAssets(){
 if(!readabilityAssets)readabilityAssets={wheel:new THREE.TorusGeometry(.65,.13,6,16),lens:new THREE.TorusGeometry(.62,.16,6,20),book:new THREE.BoxGeometry(1.2,.16,.9),core:new THREE.IcosahedronGeometry(.7,0),lamp:new THREE.SphereGeometry(.4,10,8),camp:new THREE.ConeGeometry(.75,1.2,4),pact:new THREE.OctahedronGeometry(.65),ritual:new THREE.TorusGeometry(.65,.13,6,14,Math.PI),spoke:new THREE.BoxGeometry(1.2,.09,.1),pointer:new THREE.ConeGeometry(.26,.8,3),focus:new THREE.RingGeometry(1.55,1.68,40)};
 return readabilityAssets;
}
function dressLandmarks(){
 navCache=null;const assets=getLandmarkAssets();
 for(const m of shrines)m.kind='pact';for(const m of campaign.campModels)m.kind='camp';
 const all=[...shrines,...campaign.trialModels,...campaign.campModels,...campaign.collectibles];
 campaign.landmarks=all;
 for(const m of all){
  if(m===campaign.soul)m.kind='soul';const kind=m.kind||'relic';
  const geo=assets[kind==='fresco'?'book':kind==='valve'?'wheel':kind==='archive'?'lens':kind];
  if(geo&&m.crystal.geometry!==geo){if(m.crystal.userData.ownedGeometry)m.crystal.geometry.dispose();m.crystal.geometry=geo;m.crystal.userData.ownedGeometry=false;}
  m.crystal.scale.setScalar(kind==='soul'?.4:1);m.crystal.position.y=kind==='camp'?1.1:1.8;
  if(kind==='valve'){const spoke=new THREE.Mesh(assets.spoke,bronze);m.crystal.add(spoke);const second=spoke.clone();second.rotation.z=Math.PI/2;m.crystal.add(second);}
  if(kind==='fresco'){m.crystal.rotation.x=.55;const page=new THREE.Mesh(assets.book,bronze);page.scale.set(.05,1.2,1);m.crystal.add(page);}
  if(kind==='ritual')retitleWorldLabel(m,m.id==='west'?'SCEAU DES MÉMOIRES':'SCEAU DU BRASIER');
  m.root.userData.landmarkKind=kind;
 }
 const focus=new THREE.Mesh(assets.focus,new THREE.MeshBasicMaterial({color:'#fff3cd',side:THREE.DoubleSide,transparent:true,opacity:.95,depthWrite:false}));focus.rotation.x=-Math.PI/2;focus.visible=false;scene.add(focus);roomObject(focus);campaign.focusRing=focus;focus.userData.ownedMaterial=true;
 const pointerMaterial=new THREE.MeshBasicMaterial({color:'#ffe9b2'});campaign.guidePointers=[];
 for(let i=0;i<4;i++){const mesh=new THREE.Mesh(assets.pointer,pointerMaterial);mesh.rotation.x=-Math.PI/2;mesh.visible=false;scene.add(mesh);roomObject(mesh);campaign.guidePointers.push(mesh);}
 campaign.guidePointers[0].userData.ownedMaterial=true;
}
function updateLandmarkReadability(){
 const goal=selectedMission(),route=guideRoute(goal);let focus=null,nearest=Infinity;
 for(const m of campaign.landmarks||[]){
  const d=distance(m,p),state=landmarkState(m),active=m.root.visible&&state!=='done';
  if(m.tag){m.tag.visible=active&&d<7.5;m.tag.scale.set(4.5,.844,1);}
  if(m.crystal){m.crystal.material.emissiveIntensity=state==='done'?.12:state==='locked'?.2:.7;if(m.kind==='lamp')m.crystal.scale.setScalar(state==='done'?.65:1);}
  if(active&&d<3.1&&d<nearest){focus=m;nearest=d;}
 }
 if(campaign.focusRing){campaign.focusRing.visible=!!focus;if(focus)campaign.focusRing.position.set(focus.x,.07,focus.z);}
 for(let i=0;i<(campaign.guidePointers||[]).length;i++){
  const mesh=campaign.guidePointers[i],index=3+i*2,a=route[index],b=route[index+1];mesh.visible=guidanceOn&&!!a&&!!b&&state==='playing';
  if(mesh.visible){mesh.position.set(a.x,.14,a.z);mesh.rotation.z=-Math.atan2(b.x-a.x,-(b.z-a.z));}
 }
 if(goal){$('#trackedTitle').textContent=goal.title;$('#trackedAction').textContent=goal.action;$('#trackedDistance').textContent=!guidanceOn?'Repères désactivés':route.length?`${route.length} m de chemin`:'Consulter la carte';
  const a=route[Math.min(5,route.length-1)];$('#guideArrow').hidden=!guidanceOn||!a;if(a)$('#guideArrow').style.rotate=Math.atan2(a.x-p.x,-(a.z-p.z))+'rad';}
}
function journalRows(){
 const q=campaign.trials;return[
  {title:'Âme des jardins',done:q.escort.done},
  {title:'Carillon du cloître',done:q.bells.done},
  {title:'Lentille des Archives',done:q.archive},
  {title:'Noyau de la forge',done:q.forge.done},
  {title:'Sceaux de la nef',done:q.ritual.length===2},
  {title:'Carillonneur',done:campaign.defeated.has('carillonneur')},
  {title:'Veilleur',done:!!boss?.dead},
  {title:'Retour à l’âme',done:state==='won'}];
}
function renderMissionJournal(){
 const goal=selectedMission(),container=$('#missionList');container.replaceChildren();
 for(const g of missionGoals()){
  const button=document.createElement('button');button.className='missionChoice';button.setAttribute('aria-pressed',String(g.id===goal?.id));
  const title=document.createElement('strong'),description=document.createElement('span');title.textContent=(g.id===goal?.id?'◈ Suivi · ':'◇ ')+g.title;description.textContent=g.action;button.append(title,description);button.onclick=()=>setTrackedGoal(g.id);container.append(button);
 }
 $('#questProgress').textContent=journalRows().map(r=>(r.done?'✓ ':'○ ')+r.title).join(' · ');
 const q=campaign.trials;$('#questItems').textContent=`Empreintes : ${campaign.keys.size}/2 · Lentille : ${q.archive?'obtenue':'à retrouver'} · Noyau : ${q.forge.done?'livré':q.forge.carrying?'transporté':'à retrouver'}`;
 if(q.bells.read)$('#melodyReminder').textContent='Mélodie de la fresque : '+q.bells.order.join(' → ')+(q.bells.done?' · Accordée':'');else $('#melodyReminder').textContent='La mélodie apparaîtra ici après lecture de la fresque.';
 $('#guidanceToggle').checked=guidanceOn;$('#threatToggle').checked=mapThreats;
}
function wireReadabilityUI(){
 $('#guidanceToggle').onchange=e=>{guidanceOn=e.target.checked;navCache=null;try{localStorage.setItem('royaumes-guidance',guidanceOn?'on':'off')}catch(_){}drawCampaignMap($('#largeMap'));};
 $('#threatToggle').onchange=e=>{mapThreats=e.target.checked;drawCampaignMap($('#largeMap'));};
}
