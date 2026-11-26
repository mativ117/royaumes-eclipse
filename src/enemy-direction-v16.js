'use strict';
// Two original creatures. Their model, tells and contacts share one timed state.
const enemyDirectionV16={status:'idle',promise:null,templates:Object.create(null),live:new Set(),owners:new WeakMap(),built:0,disposed:0,error:null};
const ENEMY_DIRECTION_FILES_V16=Object.freeze({archer:'archer-thorn.glb',shade:'shade-manta.glb'});
async function initEnemyDirectionV16(options={}){
 if(enemyDirectionV16.status==='ready')return enemyDirectionV16.templates;
 if(enemyDirectionV16.promise)return enemyDirectionV16.promise;
 enemyDirectionV16.status='loading';
 enemyDirectionV16.promise=(async()=>{
  const encoded=options.data??(typeof ROYAUMES_ENEMY_DIRECTION_DATA!=='undefined'?ROYAUMES_ENEMY_DIRECTION_DATA:null);
  const assets=await Promise.all(Object.entries(ENEMY_DIRECTION_FILES_V16).map(async([role,file])=>{
   let bytes;const embedded=encoded&&Object.hasOwn(encoded,role)?encoded[role]:null;
   if(embedded instanceof ArrayBuffer)bytes=embedded;
   else if(typeof embedded==='string'&&embedded)bytes=Uint8Array.from(atob(embedded),c=>c.charCodeAt(0)).buffer;
   else{const suffix=typeof ROYAUMES_VERSION==='undefined'?'':('?v='+encodeURIComponent(ROYAUMES_VERSION)),response=await fetch((options.base||'./assets/creatures/')+file+suffix);if(!response.ok)throw Error('Créature indisponible : '+file);bytes=await response.arrayBuffer();}
   const gltf=await new Promise((resolve,reject)=>(options.loader||new RoyaumesGLTFLoader()).parse(bytes,'',resolve,reject));
   const clips=Object.create(null);for(const clip of gltf.animations)clips[clip.name]=clip;
   for(const key of ['idle','move','windup','release','recover','hit','death'])if(!clips[key])throw Error(role+' : mouvement manquant '+key);
   let metadata=null;gltf.scene.traverse(o=>{if(!metadata&&o.userData.enemyProduction){try{metadata=typeof o.userData.enemyProduction==='string'?JSON.parse(o.userData.enemyProduction):o.userData.enemyProduction;}catch(_){}}});
   return[role,{root:gltf.scene,clips,metadata}];
  }));
  for(const [role,asset]of assets)enemyDirectionV16.templates[role]=asset;
  enemyDirectionV16.status='ready';return enemyDirectionV16.templates;
 })();
 try{return await enemyDirectionV16.promise;}catch(error){enemyDirectionV16.status='error';enemyDirectionV16.error=String(error);enemyDirectionV16.promise=null;throw error;}
}
function enemyV16Sound(kind,e,strength=.7){if(typeof encounterSound==='function')encounterSound(kind,{x:e.x,z:e.z},strength);else if(typeof playWorldSound==='function')playWorldSound(kind==='ceramic_hit'?'impact':kind==='bow_release'?'shot':'threat',strength,{x:e.x,z:e.z});}
function makeEnemyTacticsV16(role,durations={}){
 return{role,phase:'idle',elapsed:0,duration:Infinity,cooldown:.55,clock:0,heading:0,locked:false,angle:0,attackSerial:0,shot:false,chargeTravel:0,victims:new Set(),react:0,reactLock:0,folded:0,side:1,windup:durations.windup||(role==='archer'?1.1:.9),release:durations.release||(role==='archer'?.2:.4),recover:durations.recover||(role==='archer'?1.1:1.3),shotAt:Math.min(.066666667,(durations.release||.2)*.5)};
}
function enterEnemyPhaseV16(a,phase,duration){a.phase=phase;a.elapsed=0;a.duration=duration;a.shot=false;if(phase==='windup'){a.attackSerial++;a.locked=false;a.victims.clear();a.chargeTravel=0;}}
// Env contains the real collision/movement/damage functions in production and
// deterministic geometry in tests. There is no input-reading or API request.
function stepEnemyTacticsV16(e,dt,target,env){
 const a=e.authoredEnemy.ai;dt=Math.max(0,Math.min(.1,dt));a.clock+=dt;a.cooldown=Math.max(0,a.cooldown-dt);a.react=Math.max(0,a.react-dt);a.reactLock=Math.max(0,a.reactLock-dt);
 if(a.phase==='death')return;
 const dist=Math.hypot(target.x-e.x,target.z-e.z),facing=Math.atan2(e.x-target.x,e.z-target.z),wrap=n=>Math.atan2(Math.sin(n),Math.cos(n));
 if(a.phase==='idle'){
  a.heading+=Math.max(-dt*4,Math.min(dt*4,wrap(facing-a.heading)));
  const seen=env.line(e,target),visible=a.role!=='shade'||env.visible(e);
  if(a.cooldown<=0&&seen&&visible&&Math.abs(wrap(facing-a.heading))<.12&&dist<(a.role==='archer'?17:12)&&env.commit(e)){
   a.angle=a.heading;enterEnemyPhaseV16(a,'windup',a.windup);a.angle=facing;a.heading=facing;env.tell(e);a.cooldown=.3;
  }else{
   let goal=null,speed=0;
   if(a.role==='archer'){
    if(dist<5){goal={x:e.x+(e.x-target.x),z:e.z+(e.z-target.z)};speed=1.8;}
    else if(!seen){const angle=Math.atan2(e.z-target.z,e.x-target.x)+a.side*.62;goal={x:target.x+Math.cos(angle)*8,z:target.z+Math.sin(angle)*8};speed=2.1;}
    else if(dist>15){goal=target;speed=1.8;}
   }else if(dist>3.2||Math.abs(wrap(facing-a.heading))>.18){const angle=Math.atan2(e.z-target.z,e.x-target.x)+a.side*.36;goal={x:target.x+Math.cos(angle)*2.9,z:target.z+Math.sin(angle)*2.9};speed=visible?2.1:2.8;}
   if(goal)env.steer(e,goal,dt,speed);
  }
  e.mode=a.phase;e.timer=a.phase==='idle'?a.cooldown:a.duration;return;
 }
 let remaining=dt,guard=0;
 while(remaining>1e-9&&guard++<5&&a.phase!=='idle'){
  const step=Math.min(remaining,Math.max(0,a.duration-a.elapsed)),previous=a.elapsed;a.elapsed+=step;remaining-=step;
  if(a.phase==='windup'){
   if(a.elapsed<a.windup*.5){a.angle+=Math.max(-step*2.8,Math.min(step*2.8,wrap(facing-a.angle)));}else a.locked=true;
   a.heading=a.angle;
  }else if(a.phase==='release'){
   a.heading=a.angle;
   if(a.role==='archer'){
    if(!a.shot&&a.elapsed+1e-8>=a.shotAt){a.shot=true;env.shoot(e,a.angle);}
   }else{
    const f=u=>{u=Math.max(0,Math.min(1,u));return u*u*(3-2*u);},travel=4.4*(f(a.elapsed/a.release)-f(previous/a.release)),x=e.x,z=e.z,dx=-Math.sin(a.angle),dz=-Math.cos(a.angle);
    env.move(e,dx*travel,dz*travel,.55);a.chargeTravel+=Math.hypot(e.x-x,e.z-z);
    for(const actor of env.actors())if(!actor.downed&&!a.victims.has(actor)&&Math.hypot(actor.x-e.x,actor.z-e.z)<1.35&&env.line(e,actor)){a.victims.add(actor);env.hit(actor,18,e);}
    if(travel>.002&&Math.hypot(e.x-x,e.z-z)<.001)a.elapsed=a.duration;
   }
  }
  if(a.elapsed+1e-8<a.duration)break;
  if(a.phase==='windup'){enterEnemyPhaseV16(a,'release',a.release);a.locked=true;}
  else if(a.phase==='release'){enterEnemyPhaseV16(a,'recover',a.recover);}
  else if(a.phase==='recover'){enterEnemyPhaseV16(a,'idle',Infinity);a.cooldown=a.role==='archer'?.65:1.4;a.side*=-1;}
 }
 e.mode=a.phase==='release'&&a.role==='shade'?'charge':a.phase;e.timer=a.phase==='idle'?a.cooldown:Math.max(0,a.duration-a.elapsed);e.lockAngle=a.angle;
}
function buildEnemyDirectionV16(e){
 const template=Object.hasOwn(enemyDirectionV16.templates,e.type)?enemyDirectionV16.templates[e.type]:null;if(!template||e.authoredEnemy)return !!e.authoredEnemy;
 const root=cloneCreatureSkeleton(template.root),materials=new Map(),legacy=[];
 e.root.traverse(o=>{if((o.isMesh||o.isSprite)&&o!==e.healthBar)legacy.push({object:o,visible:o.visible});});for(const item of legacy)item.object.visible=false;
 root.name='AuthoredEnemy_'+e.type;root.rotation.set(0,0,0);root.position.set(0,e.type==='archer'?-.025:0,0);e.root.add(root);
 const bind=[];root.traverse(o=>{if(o.isBone)bind.push({bone:o,p:o.position.clone(),q:o.quaternion.clone(),s:o.scale.clone()});if(o.isMesh){const copy=m=>{if(!materials.has(m))materials.set(m,m.clone());return materials.get(m);};o.material=Array.isArray(o.material)?o.material.map(copy):copy(o.material);o.castShadow=o.receiveShadow=true;o.frustumCulled=false;o.userData.ownedMaterial=true;}});
 const mixer=new THREE.AnimationMixer(root),actions=Object.create(null);for(const [key,clip]of Object.entries(template.clips))actions[key]=mixer.clipAction(clip);
 const laneMat=new THREE.MeshBasicMaterial({color:e.type==='archer'?'#e6bf85':'#b4b8e5',transparent:true,opacity:.35,depthWrite:false}),lane=new THREE.Mesh(new THREE.PlaneGeometry(e.type==='archer'?.055:.6,1),laneMat);lane.rotation.x=-Math.PI/2;lane.visible=false;lane.userData.ownedMaterial=true;e.root.add(lane);
 const c={root,mixer,actions,clips:template.clips,metadata:template.metadata,bind,materials:[...materials.values()],legacy,lane,laneMat,ai:makeEnemyTacticsV16(e.type,Object.fromEntries(Object.entries(template.clips).map(([key,clip])=>[key,clip.duration]))),state:'',action:null,clock:0,gait:0,lastX:e.x,lastZ:e.z,speed:0,disposed:false,hitSerial:0,deathClock:0,footprintHeading:e.root.rotation.y,healthY:e.healthBar?.position.y,legs:[]};
 c.ai.heading=e.root.rotation.y;c.ai.side=e.approachSide||((enemyDirectionV16.built%2)?1:-1);
 if(Number.isFinite(c.metadata?.release_event_at))c.ai.shotAt=Math.max(0,Math.min(c.ai.release,c.metadata.release_event_at));
 c.muzzle=root.getObjectByName('muzzle');c.warning=c.materials.filter(m=>m.name.includes('Threat glow'));
 c.wings=['L','R'].map(side=>root.getObjectByName('wing'+side)||root.getObjectByName('wing.'+side));
 c.wingTips=['L','R'].map(side=>root.getObjectByName('wing_tip'+side)||root.getObjectByName('wing_tip.'+side));
 if(e.type==='archer'){e.root.updateWorldMatrix(true,false);e.root.updateMatrixWorld(true);for(const [i,side]of ['L','R'].entries()){const upper=root.getObjectByName('thigh'+side),lower=root.getObjectByName('shin'+side),end=root.getObjectByName('foot'+side);if(!upper||!lower||!end)continue;const hip=upper.getWorldPosition(new THREE.Vector3()),knee=lower.getWorldPosition(new THREE.Vector3()),foot=end.getWorldPosition(new THREE.Vector3());c.legs.push({upper,lower,end,side:i?1:-1,offset:i*.5,length1:hip.distanceTo(knee),length2:knee.distanceTo(foot),local:e.root.worldToLocal(foot.clone()),ground:foot.y-e.root.position.y,anchor:foot.clone(),destination:foot.clone(),orientation:end.getWorldQuaternion(new THREE.Quaternion()).premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),-e.root.rotation.y)),lastPhase:0});}}
 if(e.healthBar)e.healthBar.position.y=e.type==='archer'?2.5:2.1;
 e.authoredEnemy=c;enemyDirectionV16.live.add(c);enemyDirectionV16.owners.set(e.root,e);enemyDirectionV16.owners.set(root,e);enemyDirectionV16.built++;
 settleEnemySpawnV16(e);poseEnemyDirectionV16(e,0);return true;
}
// Resolve a new long-bodied creature before its first visible frame. Never
// cross a sealed threshold or pass through a second solid after leaving an
// initial overlap inherited from the old small-body spawn coordinates.
function settleEnemySpawnV16(e){
 if(e.type!=='shade')return;const c=e.authoredEnemy,origin={x:e.x,z:e.z},heading=c.ai.heading;
 if(enemyV16FootprintLegal(e,e.x,e.z,heading))return;c.ai.folded=1;
 const pathLegal=(x,z)=>{let free=false;const steps=Math.max(1,Math.ceil(Math.hypot(x-origin.x,z-origin.z)/.1));for(let i=0;i<=steps;i++){const a=origin.x+(x-origin.x)*i/steps,b=origin.z+(z-origin.z)*i/steps;if(obstacles.some(o=>(o.gate||o.questGate)&&solidActive(o,false)&&collisionContact(o,a,b,.48)))return false;const hit=blocked(a,b,.48);if(free&&hit)return false;if(!hit)free=true;}return free;};
 for(const radius of[0,.25,.5,.75,1,1.5,2])for(let side=0;side<(radius?8:1);side++){const x=origin.x+Math.cos(side*Math.PI/4)*radius,z=origin.z+Math.sin(side*Math.PI/4)*radius;if(!pathLegal(x,z))continue;for(const turn of[0,Math.PI/2,-Math.PI/2,Math.PI]){const angle=heading+turn;if(!enemyV16FootprintLegal(e,x,z,angle,1))continue;e.x=x;e.z=z;c.ai.heading=c.footprintHeading=angle;c.lastX=x;c.lastZ=z;e.root.position.set(x,0,z);e.root.rotation.set(0,angle,0);e.root.updateMatrixWorld(true);return;}}
}
function enemyV16ObstacleAt(x,z,r){return obstacles.some(o=>solidActive(o,false)&&collisionContact(o,x,z,r));}
function enemyV16FootprintLegal(e,x,z,angle,folded=e.authoredEnemy.ai.folded){
 if(e.type!=='shade')return !blocked(x,z,.48);const cosine=Math.cos(angle),sine=Math.sin(angle),points=[[0,-.45,.47],[0,-1.02,.09],[0,.55,.24],[0,1.2,.13],[0,1.88,.09]];
 for(let tail=.5;tail<=1.97;tail+=.1)points.push([0,tail,.09]);for(let nose=-.5;nose>=-1.1;nose-=.1)points.push([0,nose,.09]);
 if(folded<.99)for(const side of[-1,1])for(let wing=.5;wing<=1.16;wing+=.12)for(const depth of[0,.4])points.push([side*wing,depth,.1]);
 return !blocked(x,z,.55)&&points.every(([px,pz,r])=>!enemyV16ObstacleAt(x+cosine*px+sine*pz,z-sine*px+cosine*pz,r));
}
function enemyV16Fold(e){
 const c=e.authoredEnemy;if(e.type!=='shade')return .48;
 const angle=c.ai.heading,right={x:Math.cos(angle),z:-Math.sin(angle)},front={x:-Math.sin(angle),z:-Math.cos(angle)};
 const tight=[-1,1].some(side=>[0,-.4].some(a=>{for(let span=.5;span<=1.16;span+=.12)if(enemyV16ObstacleAt(e.x+right.x*side*span+front.x*a,e.z+right.z*side*span+front.z*a,.1))return true;return false;}));
 // Immediate when necessary: the wing cannot spend a frame inside a pillar.
 if(tight)c.ai.folded=1;return .55;
}
function enemyV16Move(e,dx,dz,r=.48){
 if(e.type!=='shade'){moveEntity(e,dx,dz,r);return;}
 const c=e.authoredEnemy,steps=Math.max(1,Math.ceil(Math.hypot(dx,dz)/.07));
 for(let i=0;i<steps;i++){const x=e.x+dx/steps,z=e.z+dz/steps;if(!enemyV16FootprintLegal(e,x,z,c.ai.heading)||!enemyV16FootprintLegal(e,x,z,c.footprintHeading))break;const oldX=e.x,oldZ=e.z;moveEntity(e,dx/steps,dz/steps,.55);if(!enemyV16FootprintLegal(e,e.x,e.z,c.ai.heading)||!enemyV16FootprintLegal(e,e.x,e.z,c.footprintHeading)){e.x=oldX;e.z=oldZ;break;}}
}
function enemyV16Turn(e,oldAngle,desired){
 if(e.type!=='shade')return desired;const delta=Math.atan2(Math.sin(desired-oldAngle),Math.cos(desired-oldAngle)),steps=Math.max(1,Math.ceil(Math.abs(delta)/.035));let accepted=oldAngle;
 for(let i=1;i<=steps;i++){const candidate=oldAngle+delta*i/steps;if(!enemyV16FootprintLegal(e,e.x,e.z,candidate))break;accepted=candidate;}return accepted;
}
function enemyV16Steer(e,goal,dt,speed){
 const c=e.authoredEnemy,radius=enemyV16Fold(e),angle=Math.atan2(goal.z-e.z,goal.x-e.x),side=c.ai.side;
 for(const offset of[0,side*.55,-side*.55,side*1.1,-side*1.1,side*1.6]){const dx=Math.cos(angle+offset)*speed*dt,dz=Math.sin(angle+offset)*speed*dt;if(!blocked(e.x+dx*4,e.z+dz*4,radius)&&enemyV16FootprintLegal(e,e.x+dx*4,e.z+dz*4,c.ai.heading)){enemyV16Move(e,dx,dz,radius);return;}}
}
function enemyV16Shoot(e,angle){
 const c=e.authoredEnemy;poseEnemyDirectionV16(e,0);e.root.updateMatrixWorld(true);
 const origin=c.muzzle?c.muzzle.getWorldPosition(new THREE.Vector3()):new THREE.Vector3(e.x,1.25,e.z),wall=projectileBlockedAlong(e.x,e.z,origin.x,origin.z,.1);
 enemyV16Sound('bow_release',e,.7);if(wall){effect(wall.x,wall.z,.6,'#e6bf85',.2);return;}
 const dx=-Math.sin(angle),dz=-Math.cos(angle),o=mesh(sphereGeo,red,origin.x,origin.y,origin.z,.1,.1,.5);o.rotation.y=angle;
 bullets.push({mesh:o,x:origin.x,y:origin.y,z:origin.z,dx,dz,t:5,enemy:true,speed:7,owner:e});
}
function updateEnemyDirectionV16(e,dt,target=null){
 const c=e.authoredEnemy;if(!c||c.disposed||e.dead)return false;
 // Powers such as classBurst already expose interruption through the native
 // enemy mode. Keep that contract instead of reviving a cancelled windup.
 if(e.mode==='recover'&&!['recover','death'].includes(c.ai.phase))enterEnemyPhaseV16(c.ai,'recover',Math.max(.3,Math.min(4,e.timer||.65)));
 if(e.type==='shade'&&Number.isFinite(c.lastX)&&Number.isFinite(c.lastZ)&&!enemyV16FootprintLegal(e,e.x,e.z,c.ai.heading)&&enemyV16FootprintLegal(e,c.lastX,c.lastZ,c.ai.heading)){e.x=c.lastX;e.z=c.lastZ;}
 target=target||enemyTarget(e);e.alert=Math.max(0,(e.alert||0)-dt);if(e.type==='shade')e.reveal=Math.max(0,(e.reveal||0)-dt);
 if(c.ai.phase==='idle'&&distance(e,p)>26&&e.alert<=0){e.root.position.set(e.x,0,e.z);return true;}
 if(c.ai.phase==='idle'&&typeof perceiveEnemy==='function'&&!perceiveEnemy(e,dt)){e.root.position.set(e.x,0,e.z);return true;}
 c.ai.folded=Math.max(0,c.ai.folded-dt*4.8);enemyV16Fold(e);
 const env={line:(from,to)=>classLine(from,to),visible:actor=>shadeVulnerable(actor),commit:actor=>actor.type==='archer'||enemies.filter(q=>q!==actor&&!q.dead&&['warden','shade'].includes(q.type)&&['windup','charge'].includes(q.mode)&&distance(q,p)<7).length<2,steer:enemyV16Steer,move:enemyV16Move,actors:()=>[p,...localParty],hit:(actor,n)=>actor===p?hurt(n):partyHurt(actor,n),shoot:enemyV16Shoot,tell:actor=>enemyV16Sound(actor.type==='archer'?'bow_draw':'shade_reveal',actor,.7)};
 const oldHeading=c.ai.heading;stepEnemyTacticsV16(e,dt,target,env);c.ai.heading=enemyV16Turn(e,oldHeading,c.ai.heading);if(c.ai.phase==='windup'&&!c.ai.locked)c.ai.angle=c.ai.heading;c.footprintHeading=c.ai.heading;e.root.rotation.set(0,c.ai.heading,0);e.root.position.set(e.x,0,e.z);return true;
}
function playEnemyClipV16(c,name){
 const action=c.actions[name]||c.actions.idle;if(c.action===action)return action;
 const old=c.action;action.reset().setEffectiveWeight(1).setEffectiveTimeScale(1);action.paused=true;const once=!['idle','move','phase'].includes(name);action.setLoop(once?THREE.LoopOnce:THREE.LoopRepeat,once?1:Infinity);action.clampWhenFinished=once;action.play();if(old){old.fadeOut(.1);action.fadeIn(.1);}c.action=action;c.state=name;return action;
}
function poseEnemyDirectionV16(e,dt){
 const c=e.authoredEnemy;if(!c||c.disposed)return false;dt=Math.max(0,Math.min(.1,dt));c.clock+=dt;
 for(const item of c.legacy)item.object.visible=false;
 const distanceMoved=Math.hypot(e.x-c.lastX,e.z-c.lastZ);c.speed=dt>0&&distanceMoved<1.5?distanceMoved/dt:0;c.lastX=e.x;c.lastZ=e.z;if(distanceMoved<1.5)c.gait+=distanceMoved/(e.type==='archer'?1.2:1.7);
 const a=c.ai,phase=a.phase,name=phase==='death'?'death':a.react>0?'hit':phase==='idle'?(c.speed>.06?'move':e.type==='shade'&&!shadeVulnerable(e)&&c.actions.phase?'phase':'idle'):phase;
 if(e.type==='archer'){const walking=c.speed>.06&&phase==='idle';if(walking&&!c.wasMoving){c.gait=.3;for(const leg of c.legs)leg.planted=false;}c.wasMoving=walking;c.walkWeight=(c.walkWeight||0)+((walking?1:0)-(c.walkWeight||0))*(1-Math.exp(-dt*18));c.root.position.y=-.025-.09*c.walkWeight;}
 for(const item of c.bind){item.bone.position.copy(item.p);item.bone.quaternion.copy(item.q);item.bone.scale.copy(item.s);}
 const action=playEnemyClipV16(c,name),duration=action.getClip().duration;
 action.time=name==='move'?(c.gait%1)*duration:name==='idle'||name==='phase'?c.clock%duration:name==='hit'?Math.max(0,Math.min(duration,.3-a.react)):name==='death'?Math.min(duration,c.deathClock):Math.min(duration,a.elapsed/Math.max(.001,a.duration)*duration);c.mixer.update(dt);
 const visible=e.type!=='shade'||shadeVulnerable(e)||phase==='death';for(const material of c.materials){if(e.type==='shade'&&phase!=='death'){const transparent=!visible;if(material.transparent!==transparent){material.transparent=transparent;material.needsUpdate=true;}material.opacity=visible?1:.23;material.depthWrite=visible;}if(material.name.includes('Threat glow'))material.emissiveIntensity=phase==='windup'?.7+1.8*Math.min(1,a.elapsed/a.windup):phase==='release'?1.6:.45;else{material.emissive.setRGB(e.flash>0?.18:0,e.flash>0?.045:0,0);material.emissiveIntensity=e.flash>0?.65:0;}}
 // The rig contract supplies fold bones; actual axes are set from its metadata.
 if(e.type==='shade'&&a.folded>0){const fold=c.metadata?.wing_fold||{},axis=new THREE.Vector3(1,0,0);for(let i=0;i<c.wings.length;i++){const bone=c.wings[i],tip=c.wingTips[i];if(bone){const bind=c.bind.find(item=>item.bone===bone);bone.quaternion.copy(bind.q).multiply(new THREE.Quaternion().setFromAxisAngle(axis,(fold.main_radians||1.2)*a.folded));}if(tip){const bind=c.bind.find(item=>item.bone===tip);tip.quaternion.copy(bind.q).multiply(new THREE.Quaternion().setFromAxisAngle(axis,(fold.tip_radians||.66)*a.folded));}}}
 if(e.type==='archer'&&c.speed>.06&&phase==='idle'&&typeof solveCreatureLeg==='function'){
  const yaw=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),a.heading),pole=new THREE.Vector3(-Math.sin(a.heading),0,-Math.cos(a.heading)),dx=e.x-(c.plantX??e.x),dz=e.z-(c.plantZ??e.z),n=Math.hypot(dx,dz),travel=n>.00001?new THREE.Vector3(dx/n,0,dz/n):pole;
  c.root.updateWorldMatrix(true,true);for(const leg of c.legs){const phase=(c.gait+leg.offset)%1,base=e.root.localToWorld(leg.local.clone());base.y=e.root.position.y+leg.ground;if(!leg.planted||n>1.5){leg.anchor.copy(base);leg.destination.copy(base);if(phase>=.58)leg.destination.addScaledVector(travel,(1-phase)*1.2+.36);leg.lastPhase=phase;leg.planted=true;}if(phase>=.58&&leg.lastPhase<.58){leg.destination.copy(base).addScaledVector(travel,1.2*.725);leg.destination.y=base.y;}if(phase<leg.lastPhase)leg.anchor.copy(leg.destination);const target=leg.anchor.clone();if(phase>=.58){const u=(phase-.58)/.42;target.lerp(leg.destination,u*u*(3-2*u));target.y+=Math.sin(u*Math.PI)*.11;}const hip=leg.upper.getWorldPosition(new THREE.Vector3()),reach=leg.length1+leg.length2-.003,vertical=hip.y-target.y,horizontal=Math.sqrt(Math.max(0,reach*reach-vertical*vertical)),tx=target.x-hip.x,tz=target.z-hip.z,span=Math.hypot(tx,tz);if(span>horizontal&&span>.001){target.x=hip.x+tx/span*horizontal;target.z=hip.z+tz/span*horizontal;if(phase<.58)leg.anchor.copy(target);}solveCreatureLeg(leg,target,pole,yaw.clone().multiply(leg.orientation));leg.lastPhase=phase;}
 }else for(const leg of c.legs)leg.planted=false;c.plantX=e.x;c.plantZ=e.z;
 c.lane.visible=phase==='windup'||e.type==='shade'&&phase==='release';const length=e.type==='archer'?16:4.4;c.lane.scale.set(1,length,1);c.lane.position.set(0,.046,-length/2);c.laneMat.opacity=phase==='windup'?.18+.22*Math.min(1,a.elapsed/a.windup):.2;
 c.root.rotation.set(0,0,0);c.root.updateMatrixWorld(true);return true;
}
function enemyDirectionV16Hit(e,amount){
 const c=e.authoredEnemy;if(!c||c.disposed||!(amount>0))return false;
 if(e.hp<=0){enterEnemyPhaseV16(c.ai,'death',c.clips.death.duration);c.deathClock=0;c.lane.visible=false;return true;}
 if(c.ai.reactLock<=0){c.ai.react=.3;c.ai.reactLock=.5;c.hitSerial++;if(c.ai.phase==='windup'&&amount>=20){enterEnemyPhaseV16(c.ai,'recover',.65);c.ai.cooldown=.3;}enemyV16Sound('ceramic_hit',e,Math.min(1,amount/60));}return true;
}
function poseEnemyDirectionV16Fallen(root,dt){
 const e=enemyDirectionV16.owners.get(root),c=e?.authoredEnemy;if(!c||c.disposed)return false;
 if(c.ai.phase!=='death'){enterEnemyPhaseV16(c.ai,'death',c.clips.death.duration);c.deathClock=0;}c.deathClock+=Math.max(0,Math.min(.1,dt));poseEnemyDirectionV16(e,dt);return true;
}
function refreshEnemyDirectionV16FallMaterials(e,copies){const c=e.authoredEnemy;if(!c||c.disposed)return false;c.materials=c.materials.map(m=>copies.get(m)||m);c.warning=c.materials.filter(m=>m.name.includes('Threat glow'));c.laneMat=copies.get(c.laneMat)||c.laneMat;return true;}
function disposeEnemyDirectionV16Root(root){
 const e=enemyDirectionV16.owners.get(root),c=e?.authoredEnemy;if(!c||c.disposed)return false;c.disposed=true;c.mixer.stopAllAction();c.mixer.uncacheRoot(c.root);
 const skeletons=new Set(),materials=new Set(c.materials);c.root.traverse(o=>{if(o.isSkinnedMesh)skeletons.add(o.skeleton);if(o.isMesh)for(const m of(Array.isArray(o.material)?o.material:[o.material]))materials.add(m);});for(const s of skeletons)s.dispose();for(const m of materials)m.dispose();c.root.removeFromParent();c.lane.removeFromParent();c.lane.geometry.dispose();c.laneMat.dispose();if(e.healthBar&&c.healthY!==undefined)e.healthBar.position.y=c.healthY;enemyDirectionV16.live.delete(c);enemyDirectionV16.owners.delete(e.root);enemyDirectionV16.owners.delete(c.root);enemyDirectionV16.disposed++;delete e.authoredEnemy;return true;
}
