'use strict';
// Fauche-Cendre: visual replacement for warden only. AI, collision and damage remain authoritative.
const creatureReference={status:'idle',template:null,promise:null,error:null,live:new Set(),owners:new WeakMap(),built:0,disposed:0};
async function initCreatureReference(options={}){
 if(creatureReference.status==='ready')return creatureReference.template;if(creatureReference.promise)return creatureReference.promise;
 creatureReference.status='loading';creatureReference.promise=(async()=>{
  const encoded=options.data??(typeof ROYAUMES_CREATURE_DATA!=='undefined'?ROYAUMES_CREATURE_DATA:null);let buffer;
  if(encoded instanceof ArrayBuffer)buffer=encoded;else if(encoded)buffer=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0)).buffer;else{const response=await fetch(options.url||'./assets/creatures/obsidian-warden.glb');if(!response.ok)throw Error('Créature manquante : '+response.status);buffer=await response.arrayBuffer();}
  const loader=options.loader||new RoyaumesGLTFLoader();const gltf=await new Promise((resolve,reject)=>loader.parse(buffer,'',resolve,reject));creatureReference.template=gltf.scene;creatureReference.status='ready';return gltf.scene;
 })();try{return await creatureReference.promise;}catch(error){creatureReference.status='error';creatureReference.error=String(error);creatureReference.promise=null;throw error;}
}
function cloneCreatureSkeleton(source){
 const root=source.clone(true),map=new Map(),skeletons=new Map();function pair(a,b){map.set(a,b);for(let i=0;i<a.children.length;i++)pair(a.children[i],b.children[i]);}pair(source,root);
 source.traverse(old=>{if(old.isSkinnedMesh){const copy=map.get(old);if(!skeletons.has(old.skeleton))skeletons.set(old.skeleton,new THREE.Skeleton(old.skeleton.bones.map(b=>map.get(b)),old.skeleton.boneInverses.map(m=>m.clone())));copy.bind(skeletons.get(old.skeleton),old.bindMatrix.clone());}});return root;
}
function creatureBone(root,name){return root.getObjectByName(name.replaceAll('.',''))||root.getObjectByName(name);}
function buildCreatureReference(e){
 if(e.type!=='warden'||creatureReference.status!=='ready')return false;if(e.creatureReference)return true;
 const root=cloneCreatureSkeleton(creatureReference.template),copies=new Map(),legacy=[];e.root.traverse(o=>{if(o.isMesh)legacy.push({object:o,visible:o.visible});});
 for(const old of legacy)old.object.visible=false;root.name='FaucheCendreReference';root.rotation.y=Math.PI;e.root.add(root);
 const bind=new Map();root.traverse(o=>{if(o.isBone)bind.set(o,{position:o.position.clone(),quaternion:o.quaternion.clone()});if(o.isMesh){const copy=m=>{if(!copies.has(m)){const material=m.clone();material.envMapIntensity=.6;copies.set(m,material);}return copies.get(m);};o.material=Array.isArray(o.material)?o.material.map(copy):copy(o.material);o.castShadow=o.receiveShadow=true;o.frustumCulled=false;o.userData.ownedMaterial=true;if(o.isSkinnedMesh)o.userData.enemySkin=true;}});
 root.updateWorldMatrix(true,true);const orientation=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),-e.root.rotation.y),legs=[];
 for(const [family,side,offset]of [['fore','L',0],['fore','R',.5],['hind','L',.5],['hind','R',0]]){
  const upper=creatureBone(root,family+'_upper.'+side),lower=creatureBone(root,family+'_lower.'+side),end=creatureBone(root,family+'_foot.'+side);if(!upper||!lower||!end)throw Error('Quadrupède incomplet : '+family+'/'+side);
  const hip=upper.getWorldPosition(new THREE.Vector3()),knee=lower.getWorldPosition(new THREE.Vector3()),foot=end.getWorldPosition(new THREE.Vector3());const local=e.root.worldToLocal(foot.clone());
  legs.push({family,side,offset,upper,lower,end,length1:hip.distanceTo(knee),length2:knee.distanceTo(foot),anchor:foot.clone(),destination:foot.clone(),local,lastPhase:offset,baseOrientation:end.getWorldQuaternion(new THREE.Quaternion()).premultiply(orientation),ground:foot.y-e.root.position.y-.025});
 }
 const materials=[...copies.values()],warning=materials.find(m=>m.name==='Amber warning');if(warning)warning.emissiveIntensity=.35;const instance={root,bind,materials,legacy,legs,warning,clock:0,phase:0,oldX:e.x,oldZ:e.z,heading:e.root.rotation.y,lastHeading:e.root.rotation.y,mode:e.mode,windDuration:.75,chargeDuration:.32,recoverDuration:1.4,didCharge:false,windWeight:0,attackSequence:0,contactSequence:-1,contacts:0,lastEvent:null,disposed:false,healthY:e.healthBar?.position.y};
 if(e.healthBar)e.healthBar.position.y=1.35;e.creatureReference=instance;creatureReference.owners.set(e.root,e);creatureReference.owners.set(root,e);creatureReference.live.add(instance);creatureReference.built++;return true;
}
const creatureIk={h:new THREE.Vector3(),k:new THREE.Vector3(),f:new THREE.Vector3(),axis:new THREE.Vector3(),bend:new THREE.Vector3(),knee:new THREE.Vector3(),end:new THREE.Vector3(),from:new THREE.Vector3(),to:new THREE.Vector3(),q:new THREE.Quaternion(),world:new THREE.Quaternion(),parent:new THREE.Quaternion()};
function pointCreatureJoint(joint,child,target){
 const s=creatureIk;joint.getWorldPosition(s.h);child.getWorldPosition(s.f);s.from.copy(s.f).sub(s.h).normalize();s.to.copy(target).sub(s.h).normalize();if(s.to.lengthSq()<.9)return;s.q.setFromUnitVectors(s.from,s.to);joint.getWorldQuaternion(s.world);joint.parent.getWorldQuaternion(s.parent).invert();s.q.premultiply(s.parent).multiply(s.world);joint.quaternion.copy(s.q);joint.updateWorldMatrix(false,true);
}
function solveCreatureLeg(leg,target,pole,orientation){
 const s=creatureIk;leg.upper.getWorldPosition(s.h);s.axis.copy(target).sub(s.h);const raw=s.axis.length();if(raw<.001)return;s.axis.divideScalar(raw);const d=Math.min(raw,leg.length1+leg.length2-.001),along=(leg.length1**2-leg.length2**2+d*d)/(2*d),lift=Math.sqrt(Math.max(0,leg.length1**2-along*along));s.bend.copy(pole).addScaledVector(s.axis,-pole.dot(s.axis)).normalize();if(s.bend.lengthSq()<.1)s.bend.set(1,0,0);
 const knee=s.knee.copy(s.h).addScaledVector(s.axis,along).addScaledVector(s.bend,lift),end=s.end.copy(s.h).addScaledVector(s.axis,d);pointCreatureJoint(leg.upper,leg.lower,knee);pointCreatureJoint(leg.lower,leg.end,end);leg.end.parent.getWorldQuaternion(s.parent).invert();leg.end.quaternion.copy(s.parent).multiply(orientation);leg.end.updateWorldMatrix(false,true);
}
function updateCreatureReference(e,dt,options={}){
 const c=e.creatureReference;if(!c||c.disposed||e.type!=='warden')return false;if(e.dead)return true;if(!e.root.visible){c.culled=true;c.oldX=e.x;c.oldZ=e.z;return true;}const wasCulled=!!c.culled;c.culled=false;dt=Math.max(0,Math.min(.1,dt));c.clock+=dt;c.lastEvent=null;
 for(const old of c.legacy)old.object.visible=false;for(const [bone,bind]of c.bind){bone.position.copy(bind.position);bone.quaternion.copy(bind.quaternion);}
 const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a)),desired=e.root.rotation.y;c.heading=e.mode==='windup'||e.mode==='charge'?desired:c.heading+wrap(desired-c.heading)*(1-Math.exp(-dt*12));e.root.rotation.y=c.heading;
 const dx=e.x-c.oldX,dz=e.z-c.oldZ,distance=Math.hypot(dx,dz),teleport=distance>1.5||wasCulled,speed=dt>0&& !teleport?distance/dt:0,turn=Math.abs(wrap(c.heading-c.lastHeading));c.oldX=e.x;c.oldZ=e.z;c.lastHeading=c.heading;
 if(e.mode!==c.mode){if(e.mode==='windup'){c.windDuration=Math.max(.05,e.windupTotal||e.timer||.75);c.attackSequence++;c.didCharge=false;}if(e.mode==='charge'){c.chargeDuration=Math.max(.05,e.chargeDuration||e.timer||.32);c.didCharge=true;}if(e.mode==='recover')c.recoverDuration=Math.max(.05,e.recoveryTotal||e.timer||1.4);c.mode=e.mode;}
 const wind=e.mode==='windup',charge=e.mode==='charge',recover=e.mode==='recover',chargeProgress=charge?1-THREE.MathUtils.clamp(e.timer/c.chargeDuration,0,1):0,progress=wind?1-THREE.MathUtils.clamp(e.timer/c.windDuration,0,1):0,recovery=recover?1-THREE.MathUtils.clamp(e.timer/c.recoverDuration,0,1):0;
 c.windWeight+=((wind?1:charge?.35:recover?Math.max(0,1-recovery*2)*.35:0)-c.windWeight)*(1-Math.exp(-dt*18));
 if(c.didCharge&&(charge&&chargeProgress>=.96||recover)&&c.attackSequence>0&&c.contactSequence!==c.attackSequence){c.contactSequence=c.attackSequence;c.contacts++;c.lastEvent={type:'landing',sequence:c.attackSequence,x:e.x,z:e.z};if(options.onContact)options.onContact(e,c.lastEvent);}
 const pitch=(name,x=0,y=0,z=0)=>{const bone=creatureBone(c.root,name);if(bone)bone.quaternion.multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(x,y,z)));};
 const bound=charge?Math.sin(chargeProgress*Math.PI):0;c.root.position.y=charge?.12*bound-.11*(1-THREE.MathUtils.smoothstep(chargeProgress,0,.2)):-.11*c.windWeight+.008*Math.sin(c.clock*2.1);pitch('spine',.02*Math.sin(c.clock*1.7),0,0);pitch('chest',wind?-.10*c.windWeight:charge?-.08*bound:recover?.11*(1-recovery):0);pitch('neck',.17*c.windWeight,0,.025*Math.sin(c.clock*.9));pitch('head',-.08*c.windWeight);pitch('jaw',wind?.26*progress:charge?.34:recover?.16*(1-recovery):.015);pitch('tail_1',0,.05*Math.sin(c.clock*1.4),.07*Math.sin(c.clock*1.7));pitch('tail_2',0,.07*Math.sin(c.clock*1.4+.6),.10*Math.sin(c.clock*1.7+.6));
 const flinch=e.flash>0?Math.sin(THREE.MathUtils.clamp((.12-e.flash)/.12,0,1)*Math.PI)*.15:0;if(flinch){pitch('chest',-flinch);pitch('neck',flinch*.7);pitch('jaw',flinch*.5);}
 if(c.warning)c.warning.emissiveIntensity=.35+(wind?1.6*progress*progress:charge?.8:0);
 c.root.updateWorldMatrix(true,true);for(const material of c.materials)if(material!==c.warning){material.emissive.setRGB(e.flash>0?.16:0,e.flash>0?.025:0,0);material.emissiveIntensity=e.flash>0?.45:0;}
 const moving=!wind&&!charge&&!recover&&(speed>.04||turn>.003),stride=speed>2?1.45:1.05;if(moving)c.phase+=(distance+turn*.14)/stride;
 const forward=new THREE.Vector3(-Math.sin(c.heading),0,-Math.cos(c.heading)),right=new THREE.Vector3(Math.cos(c.heading),0,-Math.sin(c.heading)),travel=distance>.00001&&!teleport?new THREE.Vector3(dx/distance,0,dz/distance):forward,yaw=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),c.heading);
 for(const leg of c.legs){
  const phase=(c.phase+leg.offset)%1,base=e.root.localToWorld(leg.local.clone());base.y=e.root.position.y+leg.ground;
  if(teleport||!Number.isFinite(leg.anchor.x)){leg.anchor.copy(base);leg.destination.copy(base);leg.lastPhase=phase;}
  if(moving&&phase>=.62&&leg.lastPhase<.62){leg.destination.copy(base).addScaledVector(travel,stride*.46);leg.destination.y=base.y;}
  if(phase<leg.lastPhase)leg.anchor.copy(leg.destination);
  const target=leg.anchor.clone();if(moving&&phase>=.62){const u=(phase-.62)/.38;target.lerp(leg.destination,u*u*(3-2*u));target.y+=Math.sin(u*Math.PI)*(speed>2?.12:.075);}
  if(wind&&leg.family==='fore'&&progress>.55)target.y+=Math.sin((progress-.55)/.45*Math.PI)*.055;
  if(charge){target.copy(base).addScaledVector(forward,(leg.family==='fore'?1:-1)*bound*.16);target.y+=bound*.075;leg.anchor.copy(base);leg.destination.copy(base);}
  const hip=leg.upper.getWorldPosition(new THREE.Vector3()),maxReach=leg.length1+leg.length2-.002,vertical=hip.y-target.y,horizontal=Math.sqrt(Math.max(0,maxReach*maxReach-vertical*vertical)),tx=target.x-hip.x,tz=target.z-hip.z,span=Math.hypot(tx,tz);if(span>horizontal&&span>.001){target.x=hip.x+tx/span*horizontal;target.z=hip.z+tz/span*horizontal;if(phase<.62)leg.anchor.copy(target);}
  const pole=forward.clone().multiplyScalar(leg.family==='fore'?-1:1).addScaledVector(right,leg.side==='L'?.25:-.25);solveCreatureLeg(leg,target,pole,yaw.clone().multiply(leg.baseOrientation));leg.lastPhase=phase;
 }
 c.root.updateWorldMatrix(true,true);c.speed=speed;c.moving=moving;return true;
}
function disposeCreatureReference(e,options={}){
 const c=e.creatureReference;if(!c||c.disposed)return;c.disposed=true;const skeletons=new Set(),materials=new Set(c.materials);c.root.traverse(o=>{if(o.isSkinnedMesh)skeletons.add(o.skeleton);if(o.isMesh)for(const material of(Array.isArray(o.material)?o.material:[o.material]))materials.add(material);});for(const skeleton of skeletons)skeleton.dispose();for(const material of materials)material.dispose();c.root.removeFromParent();if(options.restoreLegacy)for(const old of c.legacy)old.object.visible=old.visible;if(e.healthBar&&c.healthY!==undefined)e.healthBar.position.y=c.healthY;creatureReference.owners.delete(e.root);creatureReference.owners.delete(c.root);creatureReference.live.delete(c);creatureReference.disposed++;delete e.creatureReference;
}

function disposeCreatureReferenceRoot(root,options={}){const owner=creatureReference.owners.get(root);if(!owner)return false;disposeCreatureReference(owner,options);return true;}
