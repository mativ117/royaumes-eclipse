'use strict';
const avatarRuntime={status:'loading',heroes:Object.create(null),current:null,lastAttack:null,lastWorldUse:null,error:null};
const heroLoads=Object.create(null);
function restoreAvatarBindPose(root){
 // A model cloned while walking/attacking must not define its bind lengths from that pose.
 const saved=root.userData.avatarBindPose;
 if(saved&&typeof saved==='object')root.traverse(o=>{if(!o.isBone||!Object.hasOwn(saved,o.name))return;const b=saved[o.name];if(Array.isArray(b)&&b.length===10&&b.every(Number.isFinite)){o.position.fromArray(b,0);o.quaternion.fromArray(b,3);o.scale.fromArray(b,7);}});
 else{const pose=Object.create(null);root.traverse(o=>{if(o.isBone)pose[o.name]=[...o.position.toArray(),...o.quaternion.toArray(),...o.scale.toArray()];});root.userData.avatarBindPose=pose;}
 root.updateWorldMatrix(true,true);
}
function guardAvatarAnimationPose(avatar){
 // PropertyMixer skips writing a track when its sampled value is unchanged.
 // Restore the last keyed pose first so lean, cloth and IK never accumulate
 // into those constant tracks. Wrapping this mixer covers the workshop,
 // adventure, duel, companions and LAN resynchronisation through one path.
 const bones=[];avatar.root.traverse(bone=>{if(bone.isBone)bones.push({bone,position:bone.position.clone(),rotation:bone.quaternion.clone(),scale:bone.scale.clone()});});
 const update=avatar.mixer.update.bind(avatar.mixer);avatar.mixer.update=delta=>{for(const pose of bones){pose.bone.position.copy(pose.position);pose.bone.quaternion.copy(pose.rotation);pose.bone.scale.copy(pose.scale);}const result=update(delta);for(const pose of bones){pose.position.copy(pose.bone.position);pose.rotation.copy(pose.bone.quaternion);pose.scale.copy(pose.bone.scale);}return result;};
}
function makeHeroAvatar(root,clips,name,parent=player.root){
 restoreAvatarBindPose(root);
 // A cloned PI yaw can be represented by Euler X=PI, Y=0, Z=PI.
 // Setting only Y then adds a second half-turn and reverses the whole actor.
 root.scale.setScalar(name==='neant'?.86:name==='colosse'?1.16:1.07);root.rotation.set(0,Math.PI,0);root.position.y=0;root.visible=false;
 const calibration=readMotionCalibration(root,name),visualRoot=calibration?new THREE.Group():root;if(visualRoot!==root){visualRoot.name=name+'_VisualOrigin';visualRoot.position.y=-calibration.soleClearance*Math.abs(root.scale.y);visualRoot.add(root);}
 const mixer=new THREE.AnimationMixer(root),actions={},lowerActions={},materialCopies=new Map();
 for(const clip of clips){const lower=q=>/^(root|pelvis|thigh[LR]|shin[LR]|foot[LR])$/.test(THREE.PropertyBinding.parseTrackName(q.name).nodeName);actions[clip.name]=mixer.clipAction(new THREE.AnimationClip(clip.name,clip.duration,clip.tracks.filter(q=>!lower(q))));lowerActions[clip.name]=mixer.clipAction(new THREE.AnimationClip(clip.name+'_lower',clip.duration,clip.tracks.filter(lower)));}
 root.traverse(o=>{if(o.isMesh){const copy=m=>{if(!materialCopies.has(m)){const cloned=m.clone();if(cloned.userData.morphBase&&cloned.isMeshStandardMaterial){const base=cloned.userData.morphBase;cloned.color.copy(base.color);cloned.emissive.copy(base.emissive);cloned.emissiveIntensity=base.strength;}materialCopies.set(m,cloned);}return materialCopies.get(m);};o.material=Array.isArray(o.material)?o.material.map(copy):copy(o.material);o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false;}});parent.add(visualRoot);
 const avatar={heroId:name,motionCalibration:calibration,visualRoot,ownedMaterials:[...materialCopies.values()],root,clips,mixer,actions,lowerActions,lowerAction:null,lowerState:'',state:'',action:null,muzzle:root.getObjectByName('muzzle'),blade:root.getObjectByName('blade_tip'),bladeBase:root.getObjectByName('blade_base')||root.getObjectByName('bladebase'),hand:root.getObjectByName('handR'),weapon:root.getObjectByName(name+'_Weapon'),lastAttack:null,lastUse:null,aimHold:0};const parentQuaternion=parent.quaternion.clone(),parentPosition=parent.position.clone();parent.quaternion.identity();parent.position.set(0,0,0);initAvatarKinematics(avatar);guardAvatarAnimationPose(avatar);refineHeroMaterials(avatar);parent.quaternion.copy(parentQuaternion);parent.position.copy(parentPosition);parent.updateWorldMatrix(true,true);return avatar;
}
async function ensureHeroModel(name){
 if(!isHeroId(name))throw Error('Héros inconnu.');
 if(Object.hasOwn(avatarRuntime.heroes,name))return avatarRuntime.heroes[name];if(Object.hasOwn(heroLoads,name))return heroLoads[name];
 heroLoads[name]=(async()=>{let buffer;if(Object.hasOwn(ROYAUMES_CHARACTER_DATA,name))buffer=Uint8Array.from(atob(ROYAUMES_CHARACTER_DATA[name]),c=>c.charCodeAt(0)).buffer;else{const response=await fetch('./assets/characters/'+name+'.glb?v='+encodeURIComponent(ROYAUMES_VERSION));if(!response.ok)throw Error('Modèle indisponible : '+name);buffer=await response.arrayBuffer();}const gltf=await new Promise((resolve,reject)=>new RoyaumesGLTFLoader().parse(buffer,'',resolve,reject));const avatar=makeHeroAvatar(gltf.scene,gltf.animations,name);avatarRuntime.heroes[name]=avatar;return avatar;})();
 try{return await heroLoads[name];}catch(e){delete heroLoads[name];throw e;}
}
async function prepareHeroSelection(){
 const selected=hero;$('#start').disabled=true;$('#start').textContent='Préparation du héros…';
 try{await ensureHeroModel(selected);if(hero!==selected)return;syncAvatarSelection();$('#start').disabled=false;$('#start').textContent='Commencer le voyage →';}catch(e){$('#intro').textContent='Ce héros ne peut pas être chargé. Vérifie la connexion et réessaie de le sélectionner.';avatarRuntime.error=String(e);}
}
async function loadAuthoredHeroes(){
 $('#start').disabled=true;$('#start').textContent='Préparation de l’expédition…';
 try{await waitReferenceMaterials();await Promise.all([typeof initCreatureReference==='function'?initCreatureReference():null,typeof initEnemyDirectionV16==='function'?initEnemyDirectionV16():null]);await ensureHeroModel(hero);avatarRuntime.status='ready';syncAvatarSelection();$('#start').disabled=false;$('#start').textContent='Commencer le voyage →';}
 catch(e){avatarRuntime.status='error';avatarRuntime.error=String(e);$('#intro').textContent='Le modèle du héros ne s’est pas chargé. Rechargez la page.';console.error(e);}
}
function syncAvatarSelection(){
 if(avatarRuntime.status!=='ready')return;if(!avatarRuntime.heroes[hero]){prepareHeroSelection();return;}
 for(const [name,avatar]of Object.entries(avatarRuntime.heroes))avatar.root.visible=name===hero;
 avatarRuntime.current=avatarRuntime.heroes[hero];
 for(const object of player.legacyParts)object.visible=false;
 if(avatarRuntime.current.muzzle){avatarRuntime.current.muzzle.add(muzzle);muzzle.position.set(0,.1,0);muzzle.scale.set(.12,.14,.12);}
 resetAvatarPose();
}
function playAvatarAction(avatar,name,fade=.13,restart=false,duration=null){
 const action=avatar.actions[name]||avatar.actions.idle;if(avatar.action===action&&!restart)return;
 const previous=avatar.action,phase=previous&&avatar.motionCalibration&&LOCOMOTION_CLIPS.includes(avatar.state)&&LOCOMOTION_CLIPS.includes(name)?previous.time/previous.getClip().duration:null;action.reset().setEffectiveWeight(1).setEffectiveTimeScale(1);
 if(duration)action.setEffectiveTimeScale(action.getClip().duration/duration);
 if(['attack1','attack2','attack3','shot','dash','leap','interact','hit','power','start','stop','turn_left','turn_right','dodge_left','dodge_right'].includes(name)){action.setLoop(THREE.LoopOnce,1);action.clampWhenFinished=true;}else{action.setLoop(THREE.LoopRepeat,Infinity);action.clampWhenFinished=false;}
 if(phase!==null)action.time=motionTransferPhase(avatar,avatar.state,name,phase)*action.getClip().duration;action.play();if(previous&&previous!==action){previous.fadeOut(fade);action.fadeIn(fade);}avatar.action=action;avatar.state=name;
}
function playLowerAction(avatar,name,fade=.11,restart=false,duration=null){
 const action=avatar.lowerActions[name]||avatar.lowerActions.idle;if(avatar.lowerAction===action&&!restart)return;
 const previous=avatar.lowerAction,phase=previous?previous.time/previous.getClip().duration:0;
 action.reset().setEffectiveWeight(1).setEffectiveTimeScale(duration?action.getClip().duration/duration:1);
 const once=['attack1','attack2','attack3','dash','leap','interact','hit','power','start','stop','turn_left','turn_right','dodge_left','dodge_right'].includes(name);action.setLoop(once?THREE.LoopOnce:THREE.LoopRepeat,once?1:Infinity);action.clampWhenFinished=once;
 if(LOCOMOTION_CLIPS.includes(name)&&LOCOMOTION_CLIPS.includes(avatar.lowerState))action.time=motionTransferPhase(avatar,avatar.lowerState,name,phase)*action.getClip().duration;
 action.play();if(previous&&previous!==action){previous.fadeOut(fade);action.fadeIn(fade);}avatar.lowerAction=action;avatar.lowerState=name;
}
function updateRigAvatar(dt){
 if(avatarRuntime.status!=='ready'||!p)return;const avatar=avatarRuntime.current;
 for(const object of player.legacyParts)object.visible=false;
 if(avatar.weapon)avatar.weapon.visible=!campaign?.trials.forge.carrying;
 const travel=avatar.lastPosition?Math.hypot(p.x-avatar.lastPosition.x,p.z-avatar.lastPosition.z):0;const speed=p.motionSpeed===undefined?Math.hypot(p.vx,p.vz):travel>1.5?0:Math.max(p.motionSpeed,travel/dt),gait=motionGait(avatar,speed);
 const locomotion=avatar.motionCalibration?lameLocomotion(avatar,dt,speed,gait):{name:gait,duration:null};
 avatar.aimHold=Math.max(0,avatar.aimHold-dt);if(!(p.powerVisualT>0))avatar.powerVisualActive=false;let lower=avatar.motionCalibration&&locomotion.name==='start'?locomotion.gait:locomotion.name,lowerRestart=!!locomotion.restart&&lower===locomotion.name,lowerDuration=lower===locomotion.name?locomotion.duration:null;
 if(p.stagger>0){playAvatarAction(avatar,'hit',.035,false,.2);lower=speed>.18?gait:'hit';lowerDuration=lower==='hit'?.2:null;}
 else if(p.leap>0){playAvatarAction(avatar,'leap',.06,false,.75);lower='leap';lowerDuration=.75;}
 else if(p.dashT>0){const dodge=avatar.motionCalibration?lameDodgeClip(avatar):'dash',duration=p.dashDuration||DODGE_DURATION;playAvatarAction(avatar,dodge,avatar.motionCalibration?.075:.045,false,duration);lower=dodge;lowerDuration=duration;}
 else if(p.attack){
  const name=p.attack.melee?'attack'+p.attack.combo:'shot',fresh=avatar.lastAttack!==p.attack;
  if(fresh){playAvatarAction(avatar,name,.035,true,p.attack.duration);avatar.lastAttack=p.attack;}
  if(!p.attack.melee)avatar.aimHold=.24;
  else if(avatar.motionCalibration?motionAttackCommitted(avatar,p):gait==='idle'){lower=name;lowerRestart=fresh;lowerDuration=p.attack.duration;}
 }
 else if(p.powerVisualT>0&&avatar.actions.power){if(!avatar.powerVisualActive||avatar.lastPowerVisualSerial!==p.powerVisualSerial){playAvatarAction(avatar,'power',.06,true,avatar.motionCalibration?.power?.duration);avatar.powerVisualActive=true;avatar.lastPowerVisualSerial=p.powerVisualSerial;}if(speed<.18&&avatar.motionCalibration?.power?.fullBody){lower='power';lowerDuration=avatar.motionCalibration.power.duration;}}
 else if(p.shield>0)playAvatarAction(avatar,'shield',.12);
 else if(campaign?.trials.forge.carrying)playAvatarAction(avatar,'carry',.12);
 else if(campaign?.worldUse&&t-campaign.worldUse.started<.55){if(avatar.lastUse!==campaign.worldUse){playAvatarAction(avatar,'interact',.1,true,.55);avatar.lastUse=campaign.worldUse;}}
 else if(isRifleHero()&&avatar.aimHold>0){/* Keep the rifle ready between successive shots. */}
 else{playAvatarAction(avatar,locomotion.name,.12,!!locomotion.restart,locomotion.duration);if(LOCOMOTION_CLIPS.includes(locomotion.name))avatar.action.setEffectiveTimeScale(avatar.motionCalibration?motionPlaybackRate(avatar,locomotion.name,speed):Math.max(.25,speed*avatar.action.getClip().duration/(locomotion.name==='run'?1.5:1.2)));}
 playLowerAction(avatar,lower,.1,lowerRestart,lowerDuration);
 if(LOCOMOTION_CLIPS.includes(lower))avatar.lowerAction.setEffectiveTimeScale(avatar.motionCalibration?motionPlaybackRate(avatar,lower,speed):Math.max(.2,speed*avatar.lowerAction.getClip().duration/(lower==='run'?1.5:1.2)));
 blendMotionGait(avatar,false,speed);blendMotionGait(avatar,true,speed);avatar.mixer.update(dt);updateHeroMorph(avatar,p,hero,dt);updateBodyDynamics(avatar,p,dt);updateAvatarKinematics(avatar,dt,speed);updateBladeTrail(avatar,dt);
}

const bladeTrail={samples:[],mesh:null,lastTime:-1};
function updateBladeTrail(avatar,dt){
 if(!bladeTrail.mesh){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(new Float32Array(7*18),3));geometry.setAttribute('color',new THREE.BufferAttribute(new Float32Array(7*18),3));geometry.setDrawRange(0,0);bladeTrail.mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide,transparent:true,opacity:.5,depthWrite:false}));bladeTrail.mesh.frustumCulled=false;scene.add(bladeTrail.mesh);}
 slash.visible=false;
 const active=isMeleeHero()&&p.attack?.melee&&p.attack.elapsed>=p.attack.hitAt*.65&&p.attack.elapsed<p.attack.duration*.9;
 if(active&&avatar.blade&&(avatar.bladeBase||avatar.hand)){avatar.root.updateMatrixWorld(true);bladeTrail.samples.push({base:(avatar.bladeBase||avatar.hand).getWorldPosition(new THREE.Vector3()),tip:avatar.blade.getWorldPosition(new THREE.Vector3()),time:t});}
 bladeTrail.samples=bladeTrail.samples.filter(s=>t>=s.time&&t-s.time<.13).slice(-8);const samples=bladeTrail.samples,g=bladeTrail.mesh.geometry;let count=0;
 for(let i=1;i<samples.length;i++){const a=samples[i-1],b=samples[i];for(const v of [a.base,a.tip,b.tip,a.base,b.tip,b.base]){g.attributes.position.setXYZ(count,v.x,v.y,v.z);const f=i/samples.length;g.attributes.color.setXYZ(count,.8*f,.48*f,.16*f);count++;}}
 g.setDrawRange(0,count);g.attributes.position.needsUpdate=true;g.attributes.color.needsUpdate=true;bladeTrail.mesh.visible=count>0;
}

function resetAvatarPose(){
 for(const avatar of Object.values(avatarRuntime.heroes)){avatar.mixer.stopAllAction();avatar.action=avatar.lowerAction=null;avatar.motionBlendLower=avatar.motionBlendUpper=null;avatar.lastAttack=avatar.lastUse=null;avatar.powerVisualActive=false;avatar.aimHold=0;avatar.root.position.y=0;avatar.lameMotion=null;avatar.morphWeight=0;avatar.morphActive=true;updateHeroMorph(avatar,{formT:0,incarnateT:0},hero,0);resetAvatarKinematics(avatar);const baseline=avatar.motionCalibration&&avatar.actions.guard?'guard':'idle';playAvatarAction(avatar,baseline,.05,true);playLowerAction(avatar,baseline,.05,true);avatar.mixer.update(0);}
 bladeTrail.samples=[];if(bladeTrail.mesh)bladeTrail.mesh.visible=false;
}

const morphDark=new THREE.Color('#11172b'),morphBlue=new THREE.Color('#4566b0'),morphGold=new THREE.Color('#bb862d');
function updateHeroMorph(a,actor,id,dt){const target=id==='neant'&&actor.formT>0||id==='eclipse'&&actor.incarnateT>0?1:0;a.morphWeight=(a.morphWeight||0)+(target-(a.morphWeight||0))*(1-Math.exp(-dt*9));if(a.morphWeight<.001&&!target){if(!a.morphActive)return;a.morphWeight=0;}for(const m of a.ownedMaterials||[]){if(!m.isMeshStandardMaterial)continue;if(!m.userData.morphBase)m.userData.morphBase={color:m.color.clone(),emissive:m.emissive.clone(),strength:m.emissiveIntensity};const base=m.userData.morphBase;m.color.copy(base.color).lerp(id==='eclipse'?morphGold:morphDark,a.morphWeight*.65);m.emissive.copy(base.emissive).lerp(id==='eclipse'?morphGold:morphBlue,a.morphWeight*.65);m.emissiveIntensity=base.strength+a.morphWeight*.6;}a.morphActive=target||a.morphWeight>0;}
