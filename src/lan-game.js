'use strict';

// The host browser owns the simulation. A guest sends intent and renders bounded
// snapshots; this module never writes profiles, expedition saves or SDP to storage.
const lanSession={peer:null,generation:0,selfHero:null,selfName:'',remote:null,localReady:false,remoteReady:false,starting:false,started:false,timer:null,tick:0,lastSnapshotAt:0,lastSnapshotTick:-1,snapshot:null,previousSnapshot:null,queued:{},attackIds:new WeakMap(),nextAttackId:1,bulletIds:new WeakMap(),nextBulletId:1,effectIds:new WeakMap(),nextEffectId:1,bulletViews:new Map(),effectViews:new Map(),lastSounds:new Map(),stats:{sentSnapshots:0,receivedSnapshots:0,sentInputs:0,disconnects:0}};
const LAN_ACTOR_TIMERS=['inv','dash','dashT','power','shield','leap','recoil','stagger','shot','formT','incarnateT','fragileT','wardT','absorbLock','doubleSwapLock','comboWindow','powerVisualT'];
const LAN_ACTOR_FIELDS=[...LAN_ACTOR_TIMERS,'heat','incarnation','overcharge','combo','dx','dz','dashElapsed','dashDuration','dashDistance','dashProfile','motionSpeed','powerVisualDuration','powerVisualSerial'];
const lanAngle=value=>Math.atan2(Math.sin(Number(value)||0),Math.cos(Number(value)||0));
const lanFinite=(value,min,max,fallback=0)=>typeof value==='number'&&Number.isFinite(value)?Math.max(min,Math.min(max,value)):fallback;
function lanActive(){return !!lanSession.peer&&!lanSession.peer.closed;}
function isLanGuest(){return !!battle&&battle.kind==='lan-guest';}
function lanMatchActive(){return !!battle&&['lan-host','lan-guest'].includes(battle.kind);}
function lanTell(message){if(typeof setLanStatus==='function')setLanStatus(message);}
function lanUi(){if(typeof refreshSessionUI==='function')refreshSessionUI();}
function lanSelfHello(){return{hero:lanSession.selfHero,name:lanSession.selfName};}
function lanHeroAllowed(id){return typeof id==='string'&&Object.hasOwn(HERO_DEFS,id)&&(!HERO_DEFS[id].secret||secretUnlocked());}
function queueLanAction(action){
 if(!isLanGuest())return false;
 if(state==='playing'&&!p?.downed&&lanSession.peer?.connected){const name=action==='attack'?'fire':action;if(['fire','dash','power','extra','interact'].includes(name))lanSession.queued[name]=true;}
 return true;
}
function requestLanPause(paused){
 if(!lanMatchActive())return false;
 if(paused&&state!=='playing'||!paused&&state!=='paused')return false;
 const peer=lanSession.peer;if(!peer?.connected){lanTell('La connexion est fermée. Revenez au menu pour créer une nouvelle partie.');return true;}
 lanSession.queued={};
 if(isLanGuest()){peer.send('request',{action:paused?'pause':'resume'});lanTell(paused?'Pause demandée à l’hôte…':'Reprise demandée à l’hôte…');return true;}
 if(paused&&localParty[0])setDuelRemoteInput({x:0,z:0,aim:lanAngle(localParty[0].aim),fire:false,dash:false,power:false,extra:false,interact:false});
 peer.send('pause',{paused:!!paused});return false;
}
function lanShowConnectionStopped(message){
 if(!lanMatchActive())return;
 state='paused';clearInputs();$('#pausePanel').hidden=false;$('#resume').hidden=true;$('#nextChapter').hidden=true;$('#copyReport').hidden=true;
 $('#endTag').textContent='Réseau local';$('#endTitle').textContent='La connexion est interrompue.';$('#endText').textContent=message+' Revenez au menu pour refaire l’appairage. Votre aventure et ses sauvegardes sont conservées.';
 $('#mobile').classList.remove('playing');updateSoundscape(0);lastRenderedState=null;
}
function lanSetGuestPhase(phase){
 if(!isLanGuest())return;
 if(phase==='round-over'||phase==='finished'){if(state!=='won')presentDuelRound();else renderPartyStatus();return;}
 if(phase==='paused'){
  if(state!=='paused'){clearInputs();state='paused';$('#pausePanel').hidden=false;$('#resume').hidden=false;$('#resume').textContent='Demander la reprise';$('#nextChapter').hidden=true;$('#endTag').textContent='Réseau local · pause partagée';$('#endTitle').textContent='Le duel est en pause.';$('#endText').textContent='Les deux appareils sont en pause. Vous pouvez demander la reprise à l’hôte.';$('#mobile').classList.remove('playing');updateSoundscape(0);lastRenderedState=null;}
 }else if(phase==='playing'&&state!=='playing'){
  state='playing';clearInputs();$('#pausePanel').hidden=true;$('#mobile').classList.add('playing');$('#hud').hidden=false;last=performance.now();accumulator=0;lastRenderedState=null;
 }
}
function closeLanSession(reason='manual',quiet=false){
 const peer=lanSession.peer;lanSession.generation++;lanSession.peer=null;
 if(lanSession.timer!==null)clearInterval(lanSession.timer);lanSession.timer=null;
 if(peer?.connected)peer.send('bye',{reason:'leave'});peer?.close('manual');
 lanSession.started=lanSession.starting=lanSession.localReady=lanSession.remoteReady=false;lanSession.remote=null;lanSession.snapshot=lanSession.previousSnapshot=null;lanSession.queued={};lanSession.lastSnapshotAt=0;lanSession.lastSnapshotTick=-1;
 clearLanGuestVisuals();if(typeof clearLanInvitation==='function')clearLanInvitation();if(!quiet)lanTell(reason==='manual'?'Connexion fermée.':'Créez une nouvelle invitation pour recommencer.');lanUi();
}
function makeLanPeer(){
 closeLanSession('replace',true);
 if(!lanHeroAllowed(hero))throw Error('Choisissez d’abord un personnage disponible dans votre galerie.');
 lanSession.selfHero=hero;lanSession.selfName=(localProfile.name||'Voyageur').replace(/[\u0000-\u001f\u007f\u202a-\u202e\u2066-\u2069]/g,'').trim().slice(0,24)||'Voyageur';
 lanSession.tick=0;lanSession.lastSnapshotTick=-1;lanSession.attackIds=new WeakMap();lanSession.nextAttackId=1;lanSession.bulletIds=new WeakMap();lanSession.nextBulletId=1;lanSession.effectIds=new WeakMap();lanSession.nextEffectId=1;lanSession.lastSounds.clear();
 const generation=lanSession.generation;
 const peer=new EclipseLanPeer({
  onStatus:status=>{if(generation===lanSession.generation){lanTell(status.message);lanUi();}},
  onOpen:()=>{if(generation!==lanSession.generation)return;peer.send('hello',lanSelfHello());lanSession.timer=setInterval(lanNetworkTick,50);lanUi();},
  onPacket:packet=>{if(generation===lanSession.generation)handleLanPacket(packet).catch(()=>{lanTell('L’échange de partie n’a pas pu être terminé. Refaites l’appairage.');peer.close('protocol');});},
  onClose:reason=>{if(generation!==lanSession.generation)return;if(lanSession.timer!==null)clearInterval(lanSession.timer);lanSession.timer=null;lanSession.queued={};lanSession.stats.disconnects++;if(localParty[0])setDuelRemoteInput({x:0,z:0,aim:0,fire:false,dash:false,power:false,extra:false,interact:false});lanShowConnectionStopped(reason==='protocol'?'Une donnée non valide a été reçue.':'L’autre appareil ne répond plus.');lanUi();}
 });lanSession.peer=peer;return peer;
}
async function createLanInvitation(){const peer=makeLanPeer();lanUi();return peer.createOffer();}
async function acceptLanInvitation(raw){const peer=makeLanPeer();lanUi();return peer.acceptOffer(raw);}
async function acceptLanAnswer(raw){if(!lanSession.peer||lanSession.peer.role!=='host')throw Error('Créez d’abord votre invitation sur cet appareil.');return lanSession.peer.acceptAnswer(raw);}
async function readyLanPlayer(){
 const peer=lanSession.peer;if(!peer?.connected||!lanSession.remote)throw Error('Connectez les deux appareils avant de vous préparer.');
 await Promise.all([ensureHeroModel(lanSession.selfHero),ensureHeroModel(lanSession.remote.hero)]);
 if(peer!==lanSession.peer||!peer.connected)throw Error('La connexion a été fermée.');
 lanSession.localReady=true;if(peer.role==='guest')peer.send('ready',{ready:true});lanTell(peer.role==='host'?'Votre héros est prêt. Attendez l’autre joueur puis lancez le duel.':'Votre héros est prêt. L’hôte peut lancer le duel.');lanUi();
}
async function startLanDuel(){
 const peer=lanSession.peer;if(!peer?.connected||peer.role!=='host'||!lanSession.remote||!lanSession.localReady||!lanSession.remoteReady||lanSession.starting||lanSession.started)throw Error('Les deux joueurs doivent être prêts.');
 lanSession.starting=true;lanUi();const generation=lanSession.generation;
 try{const seedArray=new Uint32Array(1);crypto.getRandomValues(seedArray);const seed=seedArray[0]&2147483647;
  hero=lanSession.selfHero;await ensureHeroModel(hero);applyHero();
  const success=await beginDuelMatch({kind:'lan-host',opponentHero:lanSession.remote.hero,seed,localSlot:0});
  if(!success||generation!==lanSession.generation||!peer.connected)throw Error('La connexion a été fermée pendant le chargement.');
  lanSession.started=true;if(!peer.send('start',{seed,round:1}))throw Error('La partie n’a pas pu être transmise.');lanNetworkTick();
 }finally{lanSession.starting=false;lanUi();}
}
async function handleLanPacket(packet){
 const peer=lanSession.peer;if(!peer?.connected)return;
 if(packet.type==='hello'){
  if(lanSession.remote){if(lanSession.remote.hero!==packet.payload.hero||lanSession.remote.name!==packet.payload.name)throw Error('Le personnage distant a changé après l’appairage.');return;}
  lanSession.remote=packet.payload;lanTell(packet.payload.name+' est connecté. Préparez vos personnages.');lanUi();return;
 }
 if(packet.type==='ready'){lanSession.remoteReady=packet.payload.ready;lanUi();return;}
 if(packet.type==='input'){if(lanSession.started&&battle?.kind==='lan-host')setDuelRemoteInput(state==='playing'?packet.payload:{x:0,z:0,aim:lanAngle(localParty[0]?.aim),fire:false,dash:false,power:false,extra:false,interact:false});return;}
 if(packet.type==='request'){
  if(battle?.kind!=='lan-host')return;
  if(packet.payload.action==='pause')pause('réseau');else if(packet.payload.action==='resume'&&state==='paused')resume();else if(packet.payload.action==='leave')peer.close('remote');return;
 }
 if(packet.type==='pause'){if(isLanGuest()&&lanSession.started)lanSetGuestPhase(packet.payload.paused?'paused':'playing');return;}
 if(packet.type==='start'){
  if(peer.role!=='guest'||!lanSession.remote||!lanSession.localReady||lanSession.starting||lanSession.started)throw Error('Démarrage inattendu.');
  const generation=lanSession.generation;lanSession.starting=true;lanUi();
  try{hero=lanSession.selfHero;await ensureHeroModel(hero);applyHero();const success=await beginDuelMatch({kind:'lan-guest',opponentHero:lanSession.remote.hero,seed:packet.payload.seed,localSlot:1});if(!success||generation!==lanSession.generation||!peer.connected)throw Error('Connexion interrompue.');lanSession.started=true;lanSession.lastSnapshotAt=performance.now();}
  finally{lanSession.starting=false;lanUi();}return;
 }
 if(packet.type==='snapshot'){
  if(peer.role!=='guest'||!lanSession.started||!isLanGuest())return;const value=packet.payload;
  if(value.tick<=lanSession.lastSnapshotTick)return;
  const own=value.actors.find(a=>a.slot===1),other=value.actors.find(a=>a.slot===0);if(own.hero!==lanSession.selfHero||other.hero!==lanSession.remote.hero)throw Error('Le personnage de la partie ne correspond pas à l’appairage.');
  lanSession.previousSnapshot=lanSession.snapshot;lanSession.snapshot=value;lanSession.lastSnapshotAt=performance.now();lanSession.lastSnapshotTick=value.tick;lanSession.stats.receivedSnapshots++;applyLanSnapshot(value);return;
 }
}
function lanInputIntent(){
 const neutral={x:0,z:0,aim:lanAngle(targetAim),fire:false,dash:false,power:false,extra:false,interact:false};
 if(document.hidden||state!=='playing'||!p||p.downed){lanSession.queued={};return neutral;}
 const move=movement(),magnitude=Math.hypot(move.x,move.z),scale=Math.max(1,magnitude),held=typeof inputAttackHeld==='function'&&inputAttackHeld();
 return{x:lanFinite(move.x/scale,-1,1),z:lanFinite(move.z/scale,-1,1),aim:lanAngle(primaryPadAim??targetAim),fire:!!(shooting||mouseDown||primaryPadFire||held||lanSession.queued.fire),dash:!!lanSession.queued.dash,power:!!lanSession.queued.power,extra:!!lanSession.queued.extra,interact:!!lanSession.queued.interact};
}
function lanSerializeAttack(attack){
 if(!attack)return null;let id=lanSession.attackIds.get(attack);if(!id){id=lanSession.nextAttackId++;lanSession.attackIds.set(attack,id);}
 const duration=lanFinite(attack.duration,.01,4,.3),result={id,melee:!!attack.melee,combo:Math.round(lanFinite(attack.combo,0,3)),elapsed:lanFinite(attack.elapsed,0,duration+.099),duration,hitAt:lanFinite(attack.hitAt,0,duration),aim:lanAngle(attack.aim),charge:lanFinite(attack.charge,0,3),struck:!!attack.struck};
 if(Number.isFinite(attack.activeEnd))result.activeEnd=lanFinite(attack.activeEnd,result.hitAt,duration);return result;
}
function lanSerializeActor(actor,id,slot){
 const out={slot,hero:id,x:lanFinite(actor.x,-18,18),z:lanFinite(actor.z,-28,14),vx:lanFinite(actor.vx,-12,12),vz:lanFinite(actor.vz,-12,12),aim:lanAngle(actor===p?aim:actor.aim),hp:lanFinite(actor.hp,0,HERO_DEFS[id].hp),max:HERO_DEFS[id].hp,downed:!!actor.downed,attack:lanSerializeAttack(actor.attack)};
 for(const field of LAN_ACTOR_TIMERS)out[field]=lanFinite(actor[field],0,30);
 for(const field of ['heat','incarnation'])out[field]=lanFinite(actor[field],0,100);
 for(const field of ['overcharge','combo'])out[field]=Math.round(lanFinite(actor[field],0,3));
 for(const field of ['dx','dz'])out[field]=lanFinite(actor[field],-1,1);
 out.dashElapsed=lanFinite(actor.dashElapsed,0,1);out.dashDuration=lanFinite(actor.dashDuration,0,1);out.dashDistance=lanFinite(actor.dashDistance,0,6);out.dashProfile=actor.dashProfile==='step'?'step':'legacy';out.motionSpeed=lanFinite(actor.motionSpeed,0,40);out.comboWindow=lanFinite(actor.comboWindow,0,3);out.powerVisualT=lanFinite(actor.powerVisualT,0,4);out.powerVisualDuration=lanFinite(actor.powerVisualDuration,0,4);out.powerVisualSerial=Math.round(lanFinite(actor.powerVisualSerial,0,2147483647));return out;
}
function lanSerializeEffects(){
 return classEffects.filter(fx=>fx.life>0).slice(0,24).map(fx=>{
  let id=lanSession.effectIds.get(fx);if(!id){id=lanSession.nextEffectId++;lanSession.effectIds.set(fx,id);}
  const owner=fx.owner||p,ownerSlot=owner===p?0:1,root=fx.root.position,point=fx.kind==='rift'?fx.entrance:fx.kind==='cover'?(fx.collider?.[0]||owner):fx.kind==='rhythm'?owner:['burn','double','eclipse'].includes(fx.kind)?fx:root;
  const result={id,kind:fx.kind,owner:ownerSlot,x:lanFinite(point?.x,-24,24),z:lanFinite(point?.z,-34,20),r:fx.kind==='burn'?4.5:fx.kind==='eclipse'?7:fx.kind==='rhythm'?Math.min(8,5+(fx.pulses||0)*.7):fx.kind==='neant'?2.7:1.4,life:lanFinite(fx.life,0,12),color:'#'+fx.material.color.getHexString()};
  if(fx.kind==='rift'){result.x2=lanFinite(fx.exit.x,-24,24);result.z2=lanFinite(fx.exit.z,-34,20);}
  if(fx.kind==='cover')result.boxes=(fx.collider||[]).slice(0,3).map(o=>({x:lanFinite(o.x,-24,24),z:lanFinite(o.z,-34,20),w:lanFinite(o.w,.1,2,.9),d:lanFinite(o.d,.1,2,.9)}));return result;
 });
}
function lanSerializeSnapshot(){
 const phase=battle.finished?'finished':battle.ended?'round-over':state==='paused'||document.hidden?'paused':'playing';
 return{tick:lanSession.tick++,time:lanFinite(battle.time,0,180),phase,round:Math.round(lanFinite(battle.round,1,5,1)),wins:battle.wins.map(n=>Math.round(lanFinite(n,0,3))),winner:battle.winner===0||battle.winner===1?battle.winner:-1,actors:[lanSerializeActor(p,hero,0),lanSerializeActor(localParty[0],localParty[0].heroId,1)],bullets:bullets.filter(b=>b.t>0&&!b.enemy).slice(0,64).map(b=>{let id=lanSession.bulletIds.get(b);if(!id){id=lanSession.nextBulletId++;lanSession.bulletIds.set(b,id);}return{id,x:lanFinite(b.x,-80,80),z:lanFinite(b.z,-128,48),y:lanFinite(b.y,-1,12,1.35),dx:lanFinite(b.dx,-1,1),dz:lanFinite(b.dz,-1,1),life:lanFinite(b.t,0,3),owner:b.owner===p?0:1,type:Object.hasOwn(HERO_DEFS,b.heroId)?b.heroId:'shot'};}),effects:lanSerializeEffects()};
}
function lanNetworkTick(){
 const peer=lanSession.peer;if(!peer?.connected||!lanSession.started||!battle||battle.loading)return;
 if(peer.role==='host'){
  if(document.hidden&&state==='playing')pause('hidden');
  if(peer.send('snapshot',lanSerializeSnapshot()))lanSession.stats.sentSnapshots++;
 }else if(peer.send('input',lanInputIntent())){lanSession.stats.sentInputs++;lanSession.queued={};}
}
function lanPatchActor(actor,data,local=false){
 const beforeHP=actor.hp,hadSnapshot=actor._lanInitialized;
 actor.heroId=data.hero;actor.slot=actor.team=data.slot;actor.max=data.max;actor.hp=data.hp;actor.downed=data.downed;actor._lanTarget={x:data.x,z:data.z,aim:data.aim};
 if(!actor._lanInitialized||Math.hypot(actor.x-data.x,actor.z-data.z)>1.8){actor.x=data.x;actor.z=data.z;actor._lanInitialized=true;if(actor.avatar)resetAvatarKinematics(actor.avatar);}
 for(const field of LAN_ACTOR_FIELDS)if(Object.hasOwn(data,field))actor[field]=data[field];
 const old=actor.attack,next=data.attack;
 if(!next)actor.attack=null;
 else if(old&&old.id===next.id){const elapsed=Math.max(next.elapsed,Math.min(old.elapsed,next.elapsed+.05));Object.assign(old,next,{elapsed});}
 else actor.attack={...next};
 if(local){aim=lanAngle(data.aim);if(!actor.attack&&state==='playing'&&!document.hidden)aim=lanAngle(targetAim);}
 actor.aim=data.aim;
 if(hadSnapshot&&typeof combatFeedbackContactV17==='function'){const other=actor===p?localParty[0]:p;if(actor.hp<beforeHP)combatFeedbackContactV17(actor,beforeHP,other,{kind:'contact'});}
}
function applyLanSnapshot(value){
 const changedRound=battle.round!==value.round;battle.round=value.round;battle.wins=value.wins.slice();battle.time=value.time;battle.winner=value.winner<0?null:value.winner;battle.finished=value.phase==='finished';battle.ended=value.phase==='round-over'||battle.finished;
 if(changedRound){clearInputs();clearFX();lanSession.lastSounds.clear();p._lanInitialized=false;for(const actor of localParty)actor._lanInitialized=false;}
 lanPatchActor(p,value.actors.find(a=>a.slot===1),true);lanPatchActor(localParty[0],value.actors.find(a=>a.slot===0));
 applyLanBulletViews(value.bullets);applyLanEffectViews(value.effects||[]);lanSetGuestPhase(value.phase);renderPartyStatus();updateHUD();
}
function clearLanView(view){view.root.removeFromParent();for(const material of view.materials||[])material.dispose();for(const geometry of view.geometries||[])geometry.dispose();if(view.colliders?.length){obstacles=obstacles.filter(o=>!view.colliders.includes(o));world.obstacles=obstacles;}}
function clearLanGuestVisuals(){for(const view of lanSession.bulletViews.values())clearLanView(view);for(const view of lanSession.effectViews.values())clearLanView(view);lanSession.bulletViews.clear();lanSession.effectViews.clear();}
function applyLanBulletViews(values){
 const alive=new Set();for(let index=0;index<values.length;index++){const data=values[index],id=data.id??index;alive.add(id);let view=lanSession.bulletViews.get(id);
  if(!view){const material=new THREE.MeshBasicMaterial({color:data.type==='shot'?'#ffe3a7':HERO_DEFS[data.type].color}),root=new THREE.Mesh(sphereGeo,material);root.scale.set(.065,.065,.4);root.position.set(data.x,data.y,data.z);scene.add(root);view={root,materials:[material]};lanSession.bulletViews.set(id,view);}
  view.data=data;view.receivedAt=performance.now();view.root.rotation.y=Math.atan2(-data.dx,-data.dz);
 }
 for(const [id,view]of lanSession.bulletViews)if(!alive.has(id)){clearLanView(view);lanSession.bulletViews.delete(id);}
}
function makeLanEffectView(data){
 const root=new THREE.Group(),material=new THREE.MeshStandardMaterial({color:data.color,emissive:data.color,emissiveIntensity:.5,transparent:true,opacity:.65,roughness:.45,depthWrite:false}),view={root,materials:[material],colliders:[],geometries:[],kind:data.kind};scene.add(root);
 const add=(geometry,x,y,z,sx,sy,sz)=>{const o=new THREE.Mesh(geometry,material);o.position.set(x,y,z);o.scale.set(sx,sy,sz);root.add(o);return o;};
 if(data.kind==='cover')for(const box of data.boxes||[]){const piece=add(boxGeo,box.x,.8,box.z,box.w,1.6,box.d);piece.castShadow=true;const collider={x:box.x,z:box.z,w:box.w,d:box.d,mesh:piece};view.colliders.push(collider);obstacles.push(collider);}
 else if(data.kind==='rift'){for(const [x,z]of[[data.x,data.z],[data.x2,data.z2]])add(ringGeo,x,1.2,z,1,1.4,1);}
 else if(data.kind==='double'){add(coneGeo,0,1,0,.65,1,.65);add(sphereGeo,0,1.9,0,.24,.24,.24);}
 else if(data.kind==='burn'||data.kind==='rhythm'){const ring=add(data.kind==='burn'?discGeo:ringGeo,0,.045,0,data.r,data.r,data.r);ring.rotation.x=-Math.PI/2;}
 else if(data.kind==='incarnation')for(let i=0;i<3;i++){const ring=add(ringGeo,0,1.1+i*.5,0,1.1+i*.18,1.1+i*.18,1.1+i*.18);ring.rotation.x=i===1?Math.PI/2:.3;}
 else{const radius=data.kind==='eclipse'?1:.35;add(sphereGeo,0,1.6,0,radius,radius,radius);if(data.kind==='neant')add(coneGeo,0,.85,0,.5,.65,.5);}
 return view;
}
function applyLanEffectViews(values){
 const alive=new Set();for(const data of values){alive.add(data.id);let view=lanSession.effectViews.get(data.id);
  if(!view){view=makeLanEffectView(data);lanSession.effectViews.set(data.id,view);}view.data=data;view.receivedAt=performance.now();view.materials[0].color.set(data.color);view.materials[0].emissive.set(data.color);if(!['cover','rift'].includes(data.kind))view.root.position.set(data.x,0,data.z);
 }
 for(const [id,view]of lanSession.effectViews)if(!alive.has(id)){clearLanView(view);lanSession.effectViews.delete(id);}
}
function lanGuestAim(dt){
 pollPrimaryGamepad();const move=movement(),magnitude=Math.hypot(move.x,move.z),other=localParty[0];
 if(coarse()){
  const combatIntent=shooting||mouseDown||inputAttackHeld()||lanSession.queued.fire||p.powerVisualT>0||p.attack&&motionAttackCommitted(avatarRuntime.current,p);
  if(combatIntent&&other&&!other.downed&&distance(other,p)<18&&classLine(p,other))targetAim=Math.atan2(p.x-other.x,p.z-other.z);else if(magnitude>.12)targetAim=Math.atan2(-move.x,-move.z);reticle.visible=false;
 }else if(mouseAim){reticle.visible=true;ray.setFromCamera(pointer,camera);if(ray.ray.intersectPlane(ground,aimPoint)){targetAim=Math.atan2(p.x-aimPoint.x,p.z-aimPoint.z);reticle.position.set(aimPoint.x,.07,aimPoint.z);}}
 else if(magnitude>.12)targetAim=Math.atan2(-move.x,-move.z);
 if(primaryPadAim!==null)targetAim=primaryPadAim;aim+=lanAngle(targetAim-aim)*(1-Math.exp(-dt*20));
}
function lanPoseGuestPlayer(dt){
 const jump=p.leap>0?Math.sin((1-p.leap/.75)*Math.PI)*3.2:0;player.root.position.set(p.x,jump,p.z);player.root.rotation.set(0,p.attack?.aim??aim,p.downed?1.15:0);heroShadow.position.set(p.x,.035,p.z);heroShadow.scale.setScalar(1+jump*.18);heroShadow.material.opacity=.5/(1+jump*1.4);shield.visible=p.shield>0;shield.rotation.y+=dt;landingMarker.visible=p.leap>0;landingMarker.position.set(p.x,.08,p.z);carriedCore.visible=false;muzzle.visible=isRifleHero()&&p.recoil>.65;muzzle.material.opacity=Math.min(.95,p.recoil);poseHero(dt);
 const a=avatarRuntime.current;if(p.attack){const name=p.attack.melee?'attack'+p.attack.combo:'shot';for(const [stateName,action]of [[a.state,a.action],[a.lowerState,a.lowerAction]])if(stateName===name&&Math.abs(action.time-p.attack.elapsed)>.08)action.time=Math.min(action.getClip().duration,p.attack.elapsed);a.mixer.update(0);}
}
function updateLanGuest(dt){
 if(!isLanGuest()||!lanSession.started||!lanSession.snapshot||!p||!localParty[0])return;
 dt=Math.max(0,Math.min(.05,dt));const fresh=performance.now()-lanSession.lastSnapshotAt<350;
 if(state==='playing'&&fresh){
  t+=dt;lanGuestAim(dt);const intent=lanInputIntent(),n=Math.hypot(intent.x,intent.z),deadzone=.12,magnitude=n>deadzone?Math.min(1,(n-deadzone)/(1-deadzone)):0,scale=n>0?magnitude/n:0;
  const engaged=p.attack?.melee&&avatarRuntime.current?.motionCalibration&&motionAttackCommitted(avatarRuntime.current,p),speed=HERO_DEFS[hero].speed*(engaged?0:p.attack?.melee?.75:1),response=1-Math.exp(-dt*(n>deadzone?18:26));p.vx+=(intent.x*scale*speed-p.vx)*response;p.vz+=(intent.z*scale*speed-p.vz)*response;
  const oldX=p.x,oldZ=p.z;if(!p.downed&&p.dashT<=0&&p.leap<=0){const calibration=motionSpeedScale(avatarRuntime.current,hero,p,aim);moveEntity(p,p.vx*calibration*dt,p.vz*calibration*dt);}
  const target=p._lanTarget;if(target){const gain=1-Math.exp(-dt*9);moveEntity(p,(target.x-p.x)*gain,(target.z-p.z)*gain);}p.motionSpeed=Math.min(40,Math.hypot(p.x-oldX,p.z-oldZ)/Math.max(.001,dt));
  for(const actor of [p,...localParty])if(actor.attack)actor.attack.elapsed=Math.min(actor.attack.duration,actor.attack.elapsed+dt);
  const other=localParty[0],remoteTarget=other._lanTarget;if(remoteTarget){const gain=1-Math.exp(-dt*18),oldX=other.x,oldZ=other.z;other.x+=(remoteTarget.x-other.x)*gain;other.z+=(remoteTarget.z-other.z)*gain;other.aim+=lanAngle(remoteTarget.aim-other.aim)*gain;other.motionSpeed=Math.min(40,Math.hypot(other.x-oldX,other.z-oldZ)/Math.max(.001,dt));}
  updateSparks(dt);updatePresentation(dt);
 }
 if(state==='playing'&&fresh){lanPoseGuestPlayer(dt);poseDuelActor(localParty[0],dt);}
 for(const actor of [p,...localParty]){const attack=actor.attack;if(attack&&(attack.struck||attack.elapsed>=attack.hitAt)&&lanSession.lastSounds.get(actor.slot)!==attack.id){lanSession.lastSounds.set(actor.slot,attack.id);playWorldSound(attack.melee?'blade':'shot',.75,{x:actor.x,z:actor.z});}}
 for(const view of lanSession.bulletViews.values()){const age=Math.max(0,Math.min(.1,(performance.now()-view.receivedAt)/1000)),b=view.data;view.root.position.set(b.x+b.dx*32*age,b.y,b.z+b.dz*32*age);}
 for(const view of lanSession.effectViews.values()){const age=Math.max(0,(performance.now()-view.receivedAt)/1000),life=Math.max(0,view.data.life-age);view.materials[0].opacity=Math.min(.7,life*.7);if(view.kind==='incarnation')view.root.rotation.y=t*.8;else if(view.kind==='rhythm')view.root.scale.setScalar(.8+.2*Math.sin(t*9));}
 if(state==='playing'&&fresh&&typeof updateCombatFeedbackV17==='function')updateCombatFeedbackV17(dt);
 renderPartyStatus();updateHUD();
}
addEventListener('blur',()=>{lanSession.queued={};if(lanSession.peer?.connected&&isLanGuest())lanSession.peer.send('input',{x:0,z:0,aim:lanAngle(targetAim),fire:false,dash:false,power:false,extra:false,interact:false});});
addEventListener('pagehide',()=>closeLanSession('manual',true));
