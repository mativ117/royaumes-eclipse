'use strict';
const bladeContactScratch={u:new THREE.Vector3(),v:new THREE.Vector3(),r:new THREE.Vector3(),a:new THREE.Vector3(),b:new THREE.Vector3()};
function segmentDistanceSquared(p1,q1,p2,q2){
 const k=bladeContactScratch,u=k.u.subVectors(q1,p1),v=k.v.subVectors(q2,p2),r=k.r.subVectors(p1,p2),a=u.dot(u),e=v.dot(v),f=v.dot(r),clamp=THREE.MathUtils.clamp;let s=0,t=0;
 if(a<1e-10&&e<1e-10)return p1.distanceToSquared(p2);
 if(a<1e-10)t=clamp(f/e,0,1);else{const c=u.dot(r);if(e<1e-10)s=clamp(-c/a,0,1);else{const b=u.dot(v),denom=a*e-b*b;s=denom>1e-10?clamp((b*f-c*e)/denom,0,1):0;t=(b*s+f)/e;if(t<0){t=0;s=clamp(-c/a,0,1);}else if(t>1){t=1;s=clamp((b-c)/a,0,1);}}}
 return k.a.copy(p1).addScaledVector(u,s).distanceToSquared(k.b.copy(p2).addScaledVector(v,t));
}
function sourceAttackDefinition(a,avatar=avatarRuntime.current,id=hero){return avatar?.motionCalibration?.attacks?.['attack'+a.combo]||null;}
function usesBladeContacts(a,avatar=avatarRuntime.current,id=hero){return !!(a?.melee&&sourceAttackDefinition(a,avatar,id)&&avatar?.hand&&avatar?.blade);}
function bladeBodyCapsule(enemy){
 const scale=Math.abs(enemy.root?.scale.y)||1,creature=!!enemy.creatureReference;
 if(creature){const root=enemy.creatureReference.root,hips=creatureBone(root,'hips'),head=creatureBone(root,'head');if(hips&&head){root.updateWorldMatrix(true,true);return{a:hips.getWorldPosition(new THREE.Vector3()),b:head.getWorldPosition(new THREE.Vector3()),radius:.37*scale};}}
 const radius=(enemy.type==='boss'?1.05:enemy.type==='porter'?.65:creature?.48:.40)*scale;
 return {a:new THREE.Vector3(enemy.x,(creature?.28:.45)*scale,enemy.z),b:new THREE.Vector3(enemy.x,(creature?.96:1.70)*scale,enemy.z),radius};
}
function sweptBladeHits(previous,current,body,bladeRadius=.10){
 const distance=Math.max(previous.base.distanceTo(current.base),previous.tip.distanceTo(current.tip)),steps=Math.min(16,Math.max(1,Math.ceil(distance/.12))),base=new THREE.Vector3(),tip=new THREE.Vector3();
 for(let i=0;i<=steps;i++){const u=i/steps;base.lerpVectors(previous.base,current.base,u);tip.lerpVectors(previous.tip,current.tip,u);if(segmentDistanceSquared(base,tip,body.a,body.b)<=(body.radius+Math.min(.10,bladeRadius))**2||segmentDistanceSquared(tip,tip,body.a,body.b)<=(body.radius+bladeRadius)**2)return true;}return false;
}
function resolveBladeContacts(actor=p,avatar=avatarRuntime.current,id=hero){
 const attack=actor?.attack;if(!usesBladeContacts(attack,avatar,id))return;avatar.root.updateWorldMatrix(true,true);
 const sample={base:(avatar.bladeBase||avatar.hand).getWorldPosition(new THREE.Vector3()),tip:avatar.blade.getWorldPosition(new THREE.Vector3())},previous=attack.bladeSample||sample;attack.bladeSample=sample;
 const info=sourceAttackDefinition(attack,avatar,id),start=attack.hitAt,end=attack.activeEnd??info.activeEnd??Math.min(attack.duration,start+.18);
 if(attack.elapsed<start||attack.elapsed>end||previous.tip.distanceTo(sample.tip)>3)return;
 attack.hitTargets=attack.hitTargets||new Set();const targets=actor===p?enemies:abilityTargets(actor);
 for(const enemy of targets){if(enemy.dead||enemy.downed||enemy===actor||attack.hitTargets.has(enemy)||enemy.root&&!enemy.partyOwner&&actor===p&&!trialActive(enemy)||enemy.type==='boss'&&!campaign.bossAwake)continue;
  if(Math.hypot(enemy.x-actor.x,enemy.z-actor.z)>4.5||!(actor===p?clearStrikeLine(enemy.x,enemy.z):classLine(actor,enemy)))continue;
  if(!sweptBladeHits(previous,sample,bladeBodyCapsule(enemy),avatar.motionCalibration.weaponRadius?avatar.motionCalibration.weaponRadius*motionModelScale(avatar):.10))continue;attack.hitTargets.add(enemy);
  const amount=((attack.combo===3?72:44)+(attack.charge||0)*20)*(id==='colosse'?1.4:id==='eclipse'?1.1:1),before=enemy.hp;
  if(actor===p)damage(enemy,amount,{x:actor.x,z:actor.z,owner:actor,heroId:id,feedbackKind:'melee'});else abilityDamage(enemy,amount,actor,actor,{feedbackKind:'melee'});
  if(enemy.hp<before){sparks(enemy.x,enemy.z);actor.recoil=1;const dx=enemy.x-actor.x,dz=enemy.z-actor.z,n=Math.max(.001,Math.hypot(dx,dz));if(!enemy.dead&&!enemy.partyOwner&&!['boss','porter','anchor'].includes(enemy.type))moveEntity(enemy,dx/n*.18,dz/n*.18,.55);}
 }
}
