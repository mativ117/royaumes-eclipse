'use strict';

// Two useful duel modes. The historical shared-keyboard/crown module stays archived.
let localParty=[],partyKeys=new Set(),partyGeneration=0,battle=null,partyLoading=false;
const DUEL_HEROES=Object.freeze(Object.keys(HERO_DEFS));
const DUEL_ARENA_BOUNDS=Object.freeze({minX:-18,maxX:18,minZ:-28,maxZ:14});
const DUEL_NEUTRAL_INPUT=Object.freeze({x:0,z:0,ax:0,az:0,fire:false,dash:false,power:false,extra:false,interact:false});

function selectedMode(){return ['solo','duel','lan'].includes($('#playMode')?.value)?$('#playMode').value:'solo';}
function duelAuthority(){return !!battle&&battle.kind!=='lan-guest';}
function cloneHeroSkeleton(source){
 const root=source.clone(true),mapping=new Map();
 const pair=(a,b)=>{mapping.set(a,b);for(let i=0;i<a.children.length;i++)pair(a.children[i],b.children[i]);};pair(source,root);
 source.traverse(old=>{if(old.isSkinnedMesh){const copy=mapping.get(old);copy.skeleton=new THREE.Skeleton(old.skeleton.bones.map(b=>mapping.get(b)),old.skeleton.boneInverses.map(m=>m.clone()));copy.bind(copy.skeleton,old.bindMatrix.clone());}});
 // A cache model may contain the player's runtime muzzle flash; it is not part of the asset.
 if(typeof muzzle!=='undefined')mapping.get(muzzle)?.removeFromParent();
 return root;
}
function disposeDuelActor(actor){
 actor.root.removeFromParent();actor.trailMesh?.removeFromParent();
 actor.avatar.mixer.stopAllAction();actor.avatar.mixer.uncacheRoot(actor.avatar.root);
 const skeletons=new Set();actor.avatar.root.traverse(o=>{if(o.isSkinnedMesh)skeletons.add(o.skeleton);});for(const s of skeletons)s.dispose();
 for(const m of actor.avatar.ownedMaterials||[])m.dispose();for(const t of actor.avatar.surfaceTextures||[])t.dispose();
 actor.marker.material.dispose();actor.marker.geometry.dispose();actor.shieldShell.material.dispose();
 actor.trailMesh?.geometry.dispose();actor.trailMesh?.material.dispose();
}
function clearLocalParty(){
 partyGeneration++;
 if(typeof enemies!=='undefined')enemies=enemies.filter(e=>!localParty.some(a=>a.proxy===e));
 for(const actor of localParty)disposeDuelActor(actor);
 localParty=[];partyKeys.clear();partyLoading=false;
}
function makeDuelMaterial(color,kind,repeatX=1,repeatY=repeatX,metal=.1){
 const material=journeyMaterial(color,metal,.83,kind);
 if(typeof applyPbrSurface==='function')applyPbrSurface(material,kind,repeatX,repeatY,journey.textures);
 return material;
}
function buildDuelArena(){
 clearRoom();world.root.visible=false;
 journey={level:2,step:0,checkpoint:0,root:new THREE.Group(),route:'',core:180,nodes:[],gates:[],materials:[],geometries:[],textures:[],occluders:[],legs:[],elapsed:0,stageSpawned:-1,runes:0,repairs:0,secretOpen:false};
 journey.root.name='DuelArena';scene.add(journey.root);
 world.regions=[{x0:-18,x1:18,z0:-28,z1:14,name:'Le Cercle des deux lunes'}];
 world.onGround=(x,z,r=.48)=>chapterGround(world.regions,x,z,r);world.zoneAt=()=> 'Le Cercle des deux lunes';obstacles=[];world.obstacles=obstacles;
 campaign.landmarks=[];campaign.guidePointers=[];campaign.focusRing=null;campaign.collectibles=[];campaign.safeMarkers=[];campaign.time=campaign.activeSeconds=0;campaign.bossAwake=false;campaign.trials=freshTrials();campaign.zone='';boss=null;boon='';room=0;kills=0;
 const floor=makeDuelMaterial('#9a8772','stone',7.2,8.4),stoneCover=makeDuelMaterial('#807368','masonry',1,1),edge=makeDuelMaterial('#5a514a','masonry',2,1),copper=journeyMaterial('#ba8950',.7,.4,'metal');
 journey.floorMeshes=[journeyBox(0,-.32,-7,36,.64,42,floor)];
 // Four separate covers leave a readable central lane and two flanking routes.
 for(const x of [-5.5,5.5])for(const z of [-16,2]){
  journeyBox(x,.94,z,1.85,1.88,1.85,stoneCover,true);
  journeyBox(x,1.94,z,2.02,.12,2.02,copper);
 }
 for(const x of [-18,18])journeyBox(x,-.02,-7,.24,.28,42,edge);
 for(const z of [-28,14])journeyBox(0,-.02,z,36,.28,.24,edge);
 const ringGeometry=new THREE.RingGeometry(9.65,9.72,96),ring=new THREE.Mesh(ringGeometry,new THREE.MeshStandardMaterial({color:'#d3a56c',metalness:.6,roughness:.55,side:THREE.DoubleSide}));
 ring.rotation.x=-Math.PI/2;ring.position.set(0,.014,-7);journey.root.add(ring);journey.geometries.push(ringGeometry);journey.materials.push(ring.material);
 for(const x of [-21,21])for(const z of [-23,9]){
  const monument=journeyBox(x,3,z,1.1,6,1.1,edge);monument.castShadow=true;
  journeyBox(x,6.1,z,1.45,.2,1.45,copper);
 }
 if(sanctuary)sanctuary.occluders=journey.occluders;navCache=null;trackedGoal='';
 scene.background.set('#bc702d');scene.fog.color.set('#70452f');scene.fog.density=.012;
}
function initialDuelActor(heroId,slot,root,avatar){
 const actor={root,avatar,heroId,slot,team:slot,x:slot?9:-9,z:-7,vx:0,vz:0,aim:slot?Math.PI/2:-Math.PI/2,hp:HERO_DEFS[heroId].hp,max:HERO_DEFS[heroId].hp,shot:0,dash:0,dashT:0,power:0,shield:0,absorbLock:0,overcharge:0,inv:1,leap:0,recoil:0,combo:0,comboWindow:0,attackSerial:0,attack:null,downed:false,stagger:0,motionSpeed:0,networkInput:null,networkInputAt:-Infinity};
 const marker=new THREE.Mesh(new THREE.RingGeometry(.67,.72,32),new THREE.MeshBasicMaterial({color:'#ed947d',side:THREE.DoubleSide,transparent:true,opacity:.75,depthWrite:false}));marker.rotation.x=-Math.PI/2;marker.position.y=.035;root.add(marker);actor.marker=marker;
 const shell=new THREE.Mesh(sphereGeo,new THREE.MeshBasicMaterial({color:'#75d9ff',wireframe:true,transparent:true,opacity:.24,depthWrite:false}));shell.scale.set(1.55,1.65,1.55);shell.position.y=1.15;shell.visible=false;root.add(shell);actor.shieldShell=shell;
 actor.proxy={x:actor.x,z:actor.z,hp:actor.hp,max:actor.max,type:'duelist',root,partyOwner:actor,dead:false};
 return actor;
}
async function beginDuelMatch(options={}){
 const kind=options.kind||'bot',opponentHero=options.opponentHero||'rempart',localSlot=options.localSlot===1?1:0;
 if(!['bot','lan-host','lan-guest'].includes(kind)||!DUEL_HEROES.includes(hero)||!DUEL_HEROES.includes(opponentHero))throw Error('Choisissez deux héros connus pour entrer dans le cercle.');
 const seed=Number.isSafeInteger(options.seed)?options.seed:104729;
 const savedJourney=localProfile.journey===null?null:JSON.parse(JSON.stringify(localProfile.journey));
 start();buildDuelArena();
 battle={mode:'duel',kind,localSlot,round:1,wins:[0,0],scores:[0,0],time:90,ended:false,finished:false,winner:null,seed,opponentHero,loading:true};
 localProfile.journey=savedJourney; // Arena construction never writes adventure checkpoints.
 p.heroId=hero;p.slot=p.team=localSlot;p.max=HERO_DEFS[hero].hp;p.incarnation=p.heat=0;p.attackSerial=0;
 resetHeroAt(localSlot?9:-9,-7);p.aim=aim=targetAim=localSlot?Math.PI/2:-Math.PI/2;p.inv=1;
 partyLoading=true;state='paused';$('#pausePanel').hidden=true;const generation=partyGeneration;
 try{
  const source=await ensureHeroModel(opponentHero);
  if(generation!==partyGeneration||!battle)return false;
  const root=new THREE.Group();root.name='DuelOpponent';scene.add(root);
  const avatar=makeHeroAvatar(cloneHeroSkeleton(source.root),source.clips,opponentHero,root);avatar.root.visible=true;
  const actor=initialDuelActor(opponentHero,1-localSlot,root,avatar);
  if(kind==='bot')actor.bot=new TacticalDuelBot({difficulty:$('#botDifficulty')?.value||'tactician',seed});
  localParty.push(actor);enemies.push(actor.proxy);partyLoading=false;battle.loading=false;
  if(kind==='lan-guest'){
   poseDuelActor(actor,0);state='playing';$('#pausePanel').hidden=true;$('#nextChapter').hidden=true;$('#mobile').classList.add('playing');$('#hud').hidden=false;accumulator=0;last=performance.now();renderPartyStatus();
  }else resetDuelRound({first:true});
  announce(kind==='bot'?'Le Cercle des deux lunes · trois manches gagnantes contre un adversaire tactique.':'Le Cercle des deux lunes · duel direct entre vos deux appareils.');
  updateHUD();drawCampaignMap($('#miniMap'));return true;
 }catch(error){partyLoading=false;if(battle)battle.loading=false;state='menu';$('#menu').hidden=false;$('#hud').hidden=true;$('#mobile').classList.remove('playing');clearLocalParty();battle=null;throw error;}
}
function resetDuelActor(actor,slot){
 actor.hp=actor.max;actor.x=slot?9:-9;actor.z=-7;actor.vx=actor.vz=actor.motionSpeed=0;actor.aim=slot?Math.PI/2:-Math.PI/2;actor.downed=false;actor.inv=1;actor.attack=null;actor.attackSerial=(actor.attackSerial||0)+1;for(const key of ['shot','dash','dashT','power','shield','stagger','recoil','combo','comboWindow','leap','overcharge','heat','incarnation','formT','incarnateT','fragileT','wardT','doubleSwapLock','powerVisualT'])actor[key]=0;actor.dashElapsed=undefined;actor.dashHeld=actor.powerHeld=actor.extraHeld=false;actor.networkInput=null;actor.networkInputAt=-Infinity;
 actor.root.visible=true;actor.root.rotation.set(0,actor.aim,0);actor.root.position.set(actor.x,0,actor.z);resetAvatarKinematics(actor.avatar);actor.avatar.lastAttack=null;actor.bot?.reset((battle.seed+battle.round*101)>>>0);syncDuelProxy(actor);
}
function resetDuelRound({first=false}={}){
 if(!duelAuthority()||!localParty.length)return;
 if(!first){if(battle.finished){battle.round=1;battle.wins=[0,0];}else if(battle.winner!==null)battle.round++;}
 battle.ended=false;battle.finished=false;battle.winner=null;battle.time=90;
 clearInputs();clearHazards();clearFX();clearClassAbilities();for(const shot of bullets)shot.mesh.removeFromParent();bullets=[];hitPause=0;
 resetHeroAt(battle.localSlot?9:-9,-7);p.heroId=hero;p.slot=p.team=battle.localSlot;p.aim=aim=targetAim=battle.localSlot?Math.PI/2:-Math.PI/2;p.inv=1;p.attackSerial=(p.attackSerial||0)+1;p.heat=p.incarnation=p.powerVisualT=0;
 for(const actor of localParty)resetDuelActor(actor,actor.slot);
 state='playing';$('#pausePanel').hidden=true;$('#nextChapter').hidden=true;$('#mobile').classList.add('playing');$('#hud').hidden=false;accumulator=0;last=performance.now();renderPartyStatus();
 if(typeof onDuelRoundReset==='function')onDuelRoundReset();
}
function duelPublicAttack(actor){
 if(!actor.attack)return null;const a=actor.attack;
 return{phase:a.elapsed<a.hitAt?'windup':a.elapsed<(a.activeEnd??a.hitAt+.12)?'active':'recover',combo:a.combo,melee:!!a.melee};
}
function duelBotObservation(actor){
 const publicTarget={heroId:hero,x:p.x,z:p.z,vx:p.vx,vz:p.vz,aim,hp:p.hp,max:p.max,visible:classLine(actor,p)&&distance(actor,p)<24,shield:p.shield,attack:duelPublicAttack(p)};
 const projectiles=bullets.filter(b=>!b.enemy&&b.owner!==actor).map(b=>({x:b.x,z:b.z,dx:b.dx,dz:b.dz,speed:32,hostile:true}));
 const double=classEffects.find(f=>f.kind==='double'&&f.owner===actor),canSwap=!!double&&!(actor.doubleSwapLock>0);
 return{self:{id:actor.slot,heroId:actor.heroId,x:actor.x,z:actor.z,vx:actor.vx,vz:actor.vz,aim:actor.aim,hp:actor.hp,max:actor.max,shot:actor.shot,dash:actor.dash,attackReach:actor.avatar.motionCalibration?.combatReach?Math.max(.65,Math.min(5,actor.avatar.motionCalibration.combatReach*motionModelScale(actor.avatar)+.3)):undefined,power:canSwap?0:actor.power,shield:actor.shield,stagger:actor.stagger,heat:actor.heat||0,incarnation:actor.incarnation||0,incarnateT:actor.incarnateT||0,formT:actor.formT||0,hasDouble:!!double,canSwap,doublePosition:double?{x:double.x,z:double.z}:null,attack:duelPublicAttack(actor)},target:publicTarget,projectiles,obstacles:obstacles.filter(o=>solidActive(o,false)).map(o=>({x:o.root?o.root.position.x:o.x,z:o.root?o.root.position.z:o.z,w:o.w,d:o.d,radius:o.radius,enabled:true})),arenaBounds:DUEL_ARENA_BOUNDS};
}
function setDuelRemoteInput(input){
 const actor=localParty[0];if(!battle||battle.kind!=='lan-host'||!actor)return false;
 const finite=n=>typeof n==='number'&&Number.isFinite(n),axis=n=>finite(n)?Math.max(-1,Math.min(1,n)):0;
 actor.networkInput={x:axis(input?.x),z:axis(input?.z),ax:finite(input?.aim)?-Math.sin(input.aim):0,az:finite(input?.aim)?-Math.cos(input.aim):0,fire:input?.fire===true,dash:input?.dash===true,power:input?.power===true,extra:input?.extra===true,interact:false};actor.networkInputAt=performance.now();return true;
}
function partyInput(actor,dt){
 if(actor.bot)return actor.bot.update(duelBotObservation(actor),dt);
 return actor.networkInput&&performance.now()-actor.networkInputAt<=250?actor.networkInput:DUEL_NEUTRAL_INPUT;
}
function partyHurt(actor,amount,source=null){
 if(!duelAuthority()||battle.ended||state!=='playing'||actor.downed||!Number.isFinite(amount)||amount<=0)return;
 if(actor.shield>0||actor.leap>0||actor.inv>0||actor.dashT>0)return;
 amount*=actor.formT>0?.55:actor.incarnateT>0?.5:actor.wardT>0?.6:actor.fragileT>0?1.5:1;const beforeHP=actor.hp;actor.hp=Math.max(0,actor.hp-amount);if(typeof combatFeedbackContactV17==='function')combatFeedbackContactV17(actor,beforeHP,source);actor.inv=.65;actor.stagger=.2;cancelDuelAttack(actor);actor.recoil=.4;
 playWorldSound('impact',.8,{x:actor.x,z:actor.z});
 if(actor.hp<=0){actor.downed=true;actor.root.rotation.z=1.15;actor.proxy.dead=true;}
 syncDuelProxy(actor);
}
function battleDamage(actor,amount,source){
 if(!duelAuthority()||battle.ended||!Number.isFinite(amount)||amount<=0)return;const owner=source?.owner||source||p;
 if((owner.team||0)===(actor.team||0))return;const before=actor.hp;if(owner.incarnateT>0)amount*=1.5;if(actor===p)hurt(amount,source);else partyHurt(actor,amount,source);
 if((owner.heroId||(owner===p?hero:null))==='eclipse'&&actor.hp<before)owner.incarnation=Math.min(100,(owner.incarnation||0)+(before-actor.hp)*.12);
}
function cancelDuelAttack(actor){if(actor.attack&&!actor.attack.struck)actor.overcharge=Math.min(3,(actor.overcharge||0)+(actor.attack.charge||0));actor.attack=null;actor.shot=Math.min(actor.shot||0,.16);}
function partyFire(actor){
 if(actor.shot>0||actor.downed||actor.stagger>0||actor.leap>0||actor.attack)return;
 const def=HERO_DEFS[actor.heroId],melee=def.melee;actor.combo=melee?(actor.comboWindow>0?actor.combo%3+1:1):0;actor.comboWindow=1.05;
 const fallback=(melee?(actor.combo===3?.64:.43):.28)*def.attackRate,calibration=actor.avatar.motionCalibration,definition=melee?calibration?.attacks?.['attack'+actor.combo]:calibration?.shot,slow=actor.heroId==='cendres'&&actor.heat>=100?1.6:1,duration=(melee?meleeClipDuration(actor.heroId,actor.combo,fallback):definition?.duration||fallback)*slow;
 const charge=Math.min(3,(actor.overcharge||0)+(actor.heroId==='accordeur'&&classEffects.some(f=>f.kind==='rhythm'&&f.owner===actor&&t-(f.lastPulse||-100)<.13)?1:0));
 actor.attack={id:++actor.attackSerial,melee,combo:actor.combo,elapsed:0,duration,hitAt:definition?.hitAt!==undefined?definition.hitAt*slow:melee?duration*(actor.combo===3?.390625:.372093):duration*.25,activeEnd:definition?.activeEnd!==undefined?definition.activeEnd*slow:undefined,aim:actor.aim,charge,struck:false};actor.overcharge=0;actor.shot=duration;if(melee&&calibration){actor.vx=actor.vz=0;actor.comboWindow=duration+.35;}
}
function partyStrike(actor){
 const attack=actor.attack;if(!attack)return;playWorldSound(attack.melee?'blade':'shot',.75,{x:actor.x,z:actor.z});
 if(usesBladeContacts(attack,actor.avatar,actor.heroId)){actor.recoil=1;return;}
 const dx=-Math.sin(attack.aim),dz=-Math.cos(attack.aim);
 if(attack.melee){const amount=((attack.combo===3?72:44)+(attack.charge||0)*20)*(actor.heroId==='colosse'?1.4:actor.heroId==='eclipse'?1.1:1);for(const target of abilityTargets(actor)){const d=distance(actor,target);if(d<2.7&&((target.x-actor.x)*dx+(target.z-actor.z)*dz)/Math.max(.01,d)>.15&&classLine(actor,target))abilityDamage(target,amount,actor);}}
 else{
  actor.root.updateWorldMatrix(true,true);const origin=actor.avatar.muzzle?.getWorldPosition(new THREE.Vector3())||new THREE.Vector3(actor.x,1.35,actor.z);origin.x+=dx*.08;origin.z+=dz*.08;
  if(actor.heroId==='cendres')actor.heat=Math.min(100,(actor.heat||0)+12);
  const muzzleWall=projectileBlockedAlong(actor.x,actor.z,origin.x,origin.z,.1);if(muzzleWall){effect(muzzleWall.x,muzzleWall.z,.6,'#ffc17b',.2);return;}
  const o=mesh(sphereGeo,classProjectileMaterial(actor.heroId),origin.x,origin.y,origin.z,.065,.065,.4);o.rotation.y=attack.aim;bullets.push({mesh:o,x:origin.x,y:origin.y,z:origin.z,dx,dz,t:1.8,enemy:false,partyShot:true,heroId:actor.heroId,owner:actor,arcStart:isRifleHero(actor.heroId)?null:origin.y,damage:(actor.heroId==='cendres'?30:actor.heroId==='accordeur'?32:34)+(attack.charge||0)*20});
 }
 actor.recoil=1;
}
function advanceDuelAttack(actor,dt){
 const a=actor.attack;if(!a)return;const previous=a.elapsed;a.elapsed+=dt;
 if(a.melee){const definition=sourceAttackDefinition(a,actor.avatar,actor.heroId),length=definition?definition.travel*motionModelScale(actor.avatar):(a.combo===3?.95:.6),curve=time=>{const v=Math.max(0,Math.min(1,time/Math.max(.001,a.hitAt)));return v*v*(3-2*v);},dx=-Math.sin(a.aim),dz=-Math.cos(a.aim);let amount=length*(curve(a.elapsed)-curve(previous));
  const along=(p.x-actor.x)*dx+(p.z-actor.z)*dz,side=Math.abs((p.x-actor.x)*dz-(p.z-actor.z)*dx);if(along>0&&side<.9)amount=Math.min(amount,Math.max(0,along-1.05));if(amount>0)moveEntity(actor,dx*amount,dz*amount);
 }
 if(!a.struck&&a.elapsed>=a.hitAt){a.struck=true;partyStrike(actor);}
 if(a.elapsed>=a.duration)actor.attack=null;
}
function poseDuelActor(actor,dt){
 const a=actor.avatar,speed=actor.motionSpeed||0,gait=motionGait(a,speed),heading=actor.attack?.melee&&a.motionCalibration&&!motionAttackCommitted(a,actor)?actor.aim:actor.attack?.aim??actor.aim;
 actor.root.position.set(actor.x,actor.leap>0?Math.sin((1-actor.leap/.75)*Math.PI)*3.2:0,actor.z);actor.root.rotation.set(0,heading,actor.downed?1.15:0);
 const locomotion=a.motionCalibration?lameLocomotion(a,dt,speed,gait,actor,heading):{name:gait,duration:null};
 a.aimHold=Math.max(0,a.aimHold-dt);let lower=a.motionCalibration&&locomotion.name==='start'?locomotion.gait:locomotion.name,lowerRestart=!!locomotion.restart&&lower===locomotion.name,lowerDuration=lower===locomotion.name?locomotion.duration:null;
 if(actor.stagger>0){playAvatarAction(a,'hit',.035,false,.2);lower=speed>.18?gait:'hit';lowerDuration=lower==='hit'?.2:null;}
 else if(actor.leap>0){playAvatarAction(a,'leap',.06,false,.75);lower='leap';lowerDuration=.75;}
 else if(actor.dashT>0){const name=a.motionCalibration?lameDodgeClip(a,actor,heading):'dash',duration=actor.dashDuration||DODGE_DURATION;playAvatarAction(a,name,.06,false,duration);lower=name;lowerDuration=duration;}
 else if(actor.attack){const name=actor.attack.melee?'attack'+actor.attack.combo:'shot',fresh=a.lastAttack!==actor.attack&&(actor.attack.id===undefined||a.lastAttack?.id!==actor.attack.id);if(fresh){playAvatarAction(a,name,.035,true,actor.attack.duration);a.lastAttack=actor.attack;}if(!actor.attack.melee)a.aimHold=.24;else if(a.motionCalibration?motionAttackCommitted(a,actor):gait==='idle'){lower=name;lowerRestart=fresh;lowerDuration=actor.attack.duration;}}
 else if(actor.powerVisualT>0&&a.actions.power){const fresh=a.lastPowerVisualSerial!==actor.powerVisualSerial;playAvatarAction(a,'power',.08,fresh,a.motionCalibration?.power?.duration||.55);a.lastPowerVisualSerial=actor.powerVisualSerial;if(a.motionCalibration?.power?.fullBody&&speed<.18){lower='power';lowerRestart=fresh;lowerDuration=a.motionCalibration.power.duration;}}
 else if(actor.shield>0)playAvatarAction(a,'shield',.12);
 else if(!(isRifleHero(actor.heroId)&&a.aimHold>0)){playAvatarAction(a,locomotion.name,.12,!!locomotion.restart,locomotion.duration);if(LOCOMOTION_CLIPS.includes(locomotion.name))a.action.setEffectiveTimeScale(a.motionCalibration?motionPlaybackRate(a,locomotion.name,speed):Math.max(.25,speed*a.action.getClip().duration/(locomotion.name==='run'?1.5:1.2)));}
 playLowerAction(a,lower,.1,lowerRestart,lowerDuration);if(LOCOMOTION_CLIPS.includes(lower))a.lowerAction.setEffectiveTimeScale(a.motionCalibration?motionPlaybackRate(a,lower,speed):Math.max(.2,speed*a.lowerAction.getClip().duration/(lower==='run'?1.5:1.2)));
 blendMotionGait(a,false,speed);blendMotionGait(a,true,speed);a.mixer.update(dt);updateHeroMorph(a,actor,actor.heroId,dt);updateBodyDynamics(a,actor,dt);updateAvatarKinematics(a,dt,speed,actor,actor.heroId,heading);actor.shieldShell.visible=actor.shield>0&&!actor.downed;updateDuelBladeTrail(actor);
 actor.marker.material.opacity=actor.downed?.22:.75;syncDuelProxy(actor);
}
function updateDuelBladeTrail(actor){
 if(typeof combatFeedbackWeaponV17==='function'){if(actor.trailMesh)actor.trailMesh.visible=false;actor.trailSamples=[];combatFeedbackWeaponV17(actor,actor.avatar,actor.heroId,1/60);return;}
 if(!actor.avatar.blade||!actor.avatar.bladeBase)return;
 if(!actor.trailMesh){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(7*18),3));g.setDrawRange(0,0);actor.trailMesh=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:'#f2cc93',side:THREE.DoubleSide,transparent:true,opacity:.42,depthWrite:false}));actor.trailMesh.frustumCulled=false;scene.add(actor.trailMesh);actor.trailSamples=[];}
 const attack=actor.attack,active=attack?.melee&&attack.elapsed>=attack.hitAt*.75&&attack.elapsed<(attack.activeEnd??attack.duration*.8)+.10;
 if(active){actor.avatar.root.updateWorldMatrix(true,true);actor.trailSamples.push({base:actor.avatar.bladeBase.getWorldPosition(new THREE.Vector3()),tip:actor.avatar.blade.getWorldPosition(new THREE.Vector3()),time:t});}
 actor.trailSamples=actor.trailSamples.filter(s=>t>=s.time&&t-s.time<.13).slice(-8);const g=actor.trailMesh.geometry;let count=0;
 for(let i=1;i<actor.trailSamples.length;i++){const x=actor.trailSamples[i-1],y=actor.trailSamples[i];for(const v of [x.base,x.tip,y.tip,x.base,y.tip,y.base])g.attributes.position.setXYZ(count++,v.x,v.y,v.z);}
 g.setDrawRange(0,count);g.attributes.position.needsUpdate=true;actor.trailMesh.visible=count>0&&!actor.downed;
}
function syncDuelProxy(actor){if(!actor.proxy)return;Object.assign(actor.proxy,{x:actor.x,z:actor.z,hp:actor.hp,max:actor.max,dead:!!actor.downed});if(!actor.downed&&!enemies.includes(actor.proxy))enemies.push(actor.proxy);}
function duelPowerPose(actor){const spec=actor.avatar?.motionCalibration?.power;if(spec&&actor.avatar.actions.power){actor.powerVisualT=spec.duration;actor.powerVisualSerial=(actor.powerVisualSerial||0)+1;}}
function resolveDuelBodyContacts(dt=1/60){
 const actor=localParty[0];if(!actor||actor.downed||p.downed||actor.dashT>0||p.dashT>0||actor.leap>0||p.leap>0)return;
 const dx=actor.x-p.x,dz=actor.z-p.z,d=Math.hypot(dx,dz),radius=.92;if(d>=radius)return;
 const nx=d>.001?dx/d:1,nz=d>.001?dz/d:0,push=Math.min((radius-d)*.5,Math.max(0,dt)*4);
 moveEntity(actor,nx*push,nz*push);moveEntity(p,-nx*push,-nz*push);
 actor.root.position.x=actor.x;actor.root.position.z=actor.z;player.root.position.x=p.x;player.root.position.z=p.z;syncDuelProxy(actor);
}
function updateLocalParty(dt){
 if(!battle||battle.kind==='lan-guest'||battle.ended||partyLoading)return;
 for(const actor of localParty){
  const wasLeaping=actor.leap>0;for(const key of ['shot','dash','dashT','power','shield','inv','stagger','leap','absorbLock','comboWindow','powerVisualT'])actor[key]=Math.max(0,(actor[key]||0)-dt);actor.recoil=Math.max(0,(actor.recoil||0)-dt*7);if(wasLeaping&&actor.leap===0)classBurst(actor,4.6,95,HERO_DEFS.voltigeur.color);
  if(actor.downed){poseDuelActor(actor,dt);continue;}
  const input=partyInput(actor,dt),n=Math.hypot(input.x||0,input.z||0),strength=n>.12?Math.min(1,(n-.12)/.88):0,x=n>0?(input.x||0)/n*strength:0,z=n>0?(input.z||0)/n*strength:0;
  if(Math.hypot(input.ax||0,input.az||0)>.2)actor.aim=Math.atan2(-input.ax,-input.az);if(typeof steerAttackPreparation==='function')steerAttackPreparation(actor,actor.aim,dt,actor.avatar);
  const committed=actor.attack?.melee?(actor.avatar.motionCalibration?(motionAttackCommitted(actor.avatar,actor)?0:.75):(actor.attack.struck?.72:.55)):actor.attack&&actor.attack.elapsed<.1?.8:1,response=1-Math.exp(-dt*(n>.12?18:26));
  actor.vx+=(x*HERO_DEFS[actor.heroId].speed*committed-actor.vx)*response;actor.vz+=(z*HERO_DEFS[actor.heroId].speed*committed-actor.vz)*response;
  if(input.dash&&!actor.dashHeld&&actor.dash<=0){actor.dash=HERO_DEFS[actor.heroId].dash;beginDodgeMotion(actor,actor.heroId,actor.avatar);actor.dx=n>.12?x/strength:-Math.sin(actor.aim);actor.dz=n>.12?z/strength:-Math.cos(actor.aim);actor.inv=Math.min(.3,actor.dashDuration);actor.stagger=0;cancelDuelAttack(actor);actor.shot=Math.min(actor.shot,.16);}
  actor.dashHeld=!!input.dash;const previousX=actor.x,previousZ=actor.z,config=actorDodgeConfig(actor);
  if(actor.dashElapsed!==undefined&&actor.dashElapsed<config.duration){const next=Math.min(config.duration,actor.dashElapsed+dt),travel=dodgeTravel(actor.dashElapsed,next,config);moveEntity(actor,actor.dx*travel,actor.dz*travel);actor.dashElapsed=next;}
  else{const scale=motionSpeedScale(actor.avatar,actor.heroId,actor,actor.aim);moveEntity(actor,actor.vx*scale*dt,actor.vz*scale*dt);}
  actor.motionSpeed=Math.hypot(actor.x-previousX,actor.z-previousZ)/dt;
  const canSwap=actor.heroId==='voleur'&&classEffects.some(f=>f.kind==='double'&&f.owner===actor)&&!(actor.doubleSwapLock>0);
  if(input.power&&!actor.powerHeld&&(actor.power<=0||canSwap)){cancelDuelAttack(actor);const serial=actor.powerVisualSerial||0;castClassPower(actor,actor.heroId,actor.aim);if((actor.powerVisualSerial||0)===serial)duelPowerPose(actor);if(actor.heroId==='rempart'&&distance(actor,p)<5&&classLine(actor,p)){const d=Math.max(.001,distance(actor,p));moveEntity(p,(p.x-actor.x)/d*1.4,(p.z-actor.z)/d*1.4);}}
  if(input.extra&&!actor.extraHeld){const before=actor.incarnateT||0,serial=actor.powerVisualSerial||0;castIncarnation(actor,actor.heroId);if(actor.incarnateT>before&&(actor.powerVisualSerial||0)===serial)duelPowerPose(actor);}actor.extraHeld=!!input.extra;
  actor.powerHeld=!!input.power;
  poseDuelActor(actor,dt);resolveBladeContacts(actor,actor.avatar,actor.heroId);if(input.fire)partyFire(actor);advanceDuelAttack(actor,dt);actor.root.position.x=actor.x;actor.root.position.z=actor.z;syncDuelProxy(actor);
 }
 resolveDuelBodyContacts(dt);updateBattle(dt);renderPartyStatus();
}
function hitBattleProjectile(b){
 if(!duelAuthority()||!b.partyShot)return false;
 for(const target of [p,...localParty])if(!target.downed&&(target.team||0)!==(b.owner?.team||0)&&distance(target,b)<.85){battleDamage(target,b.damage||34,b.owner);b.t=0;effect(target.x,target.z,1,HERO_DEFS[b.heroId].color,.2);return true;}return false;
}
function hitPartyProjectile(b){for(const actor of localParty)if(!battle&&!actor.downed&&distance(actor,b)<.8){partyHurt(actor,14);b.t=0;return true;}return false;}
function hurtPartyFromHazard(h){if(!battle)for(const actor of localParty)if(!actor.downed&&distance(actor,h)<h.r+.3)partyHurt(actor,h.damage);}
function updateBattle(dt){
 if(!duelAuthority()||battle.ended||partyLoading)return;battle.time=Math.max(0,battle.time-dt);mapClock+=dt;if(mapClock>.15){drawCampaignMap($('#miniMap'));mapClock=0;}
 const opponent=localParty[0];if(!opponent)return;
 if(p.downed||opponent.downed){endBattleRound(p.downed?opponent.slot:p.slot);return;}
 if(battle.time<=0){const difference=p.hp/p.max-opponent.hp/opponent.max;endBattleRound(Math.abs(difference)<.001?null:difference>0?p.slot:opponent.slot);}
}
function presentDuelRound(){
 if(!battle)return;state='won';clearInputs();$('#pausePanel').hidden=false;$('#resume').hidden=true;$('#copyReport').hidden=true;
 const localWon=battle.winner===battle.localSlot,draw=battle.winner===null;
 $('#endTag').textContent=(battle.kind==='bot'?'Duel tactique':'Duel en réseau local')+' · '+battle.wins.join(' — ');
 $('#endTitle').textContent=draw?'La lune reste indécise.':battle.finished?(localWon?'Le cercle vous reconnaît.':'Votre adversaire remporte le duel.'):(localWon?'Manche remportée.':'Manche concédée.');
 $('#endText').textContent=battle.kind==='lan-guest'?'L’hôte peut lancer la prochaine manche ou rejouer. Votre progression d’aventure est conservée.':battle.finished?'Le duel se conclut en trois manches gagnantes. Rejouez ou revenez à votre aventure ; ses sauvegardes sont conservées.':'La prochaine manche rétablit santé et pouvoirs pour les deux adversaires.';
 const button=$('#nextChapter');button.hidden=battle.kind==='lan-guest';button.textContent=battle.finished?'Rejouer le duel':'Manche suivante';button.onclick=()=>resetDuelRound();$('#mobile').classList.remove('playing');updateSoundscape(0);
}
function endBattleRound(team){if(!duelAuthority()||battle.ended)return;if(team===0||team===1)battle.wins[team]++;battle.winner=team;battle.finished=battle.wins.some(n=>n>=3);battle.ended=true;presentDuelRound();}
function partyCameraCenter(){const other=localParty.find(a=>!a.downed);if(!other)return{x:p.x,z:p.z,radius:0};const d=distance(other,p);return{x:p.x+(other.x-p.x)*.22,z:p.z+(other.z-p.z)*.22,radius:Math.min(2.5,d/8)};}
function renderPartyStatus(){const panel=$('#partyStatus');if(!panel)return;const actor=localParty[0];panel.hidden=!battle||!actor;if(!actor)return;panel.textContent=(actor.bot?'Adversaire tactique':'Adversaire LAN')+' · '+HERO_DEFS[actor.heroId].name+' · '+Math.ceil(actor.hp)+' / '+actor.max+' PV';const reason=$('#duelBrain');if(reason){reason.hidden=!actor.bot;reason.textContent=actor.bot?.debug?.reason||'';}}
function resetLocalPartyAtLeader(){}
function applyPartyPact(){}
