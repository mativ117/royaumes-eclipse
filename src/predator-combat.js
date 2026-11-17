'use strict';
// One locked, readable front attack replaces the old circular warden damage zone.
function beginPredatorAttack(e,target){
 e.mode='windup';e.windupTotal=e.timer=.78;e.chargeDuration=.32;e.recoveryTotal=1.4;e.lockAngle=Math.atan2(e.x-target.x,e.z-target.z);e.dx=-Math.sin(e.lockAngle);e.dz=-Math.cos(e.lockAngle);e.predatorVictims=new Set();e.root.rotation.y=e.lockAngle;
 for(const distance of [1.05,2.1])addHazard(e.x+e.dx*distance,e.z+e.dz*distance,.48,e.windupTotal,0,'#eb8b55');
 playWorldSound('threat',.75,{x:e.x,z:e.z});
}
function updatePredatorCombat(e,dt,target){
 e.timer-=dt;const distanceToTarget=distance(e,target);
 if(e.mode==='windup'){e.root.rotation.y=e.lockAngle;if(e.timer<=0){e.mode='charge';e.timer=e.chargeDuration;e.chargeElapsed=0;}}
 else if(e.mode==='charge'){
  const previous=e.chargeElapsed||0,next=Math.min(e.chargeDuration,previous+dt),f=u=>u*u*(3-2*u),travel=2.4*(f(next/e.chargeDuration)-f(previous/e.chargeDuration)),oldX=e.x,oldZ=e.z;
  moveEntity(e,e.dx*travel,e.dz*travel,.65);e.chargeElapsed=next;e.root.rotation.y=e.lockAngle;
  for(const actor of [p,...localParty]){if(actor.downed||e.predatorVictims.has(actor))continue;const dx=actor.x-e.x,dz=actor.z-e.z,d=Math.hypot(dx,dz);if(d<1.12&&(d<.001||(dx*e.dx+dz*e.dz)/d>-.15)){e.predatorVictims.add(actor);if(actor===p)hurt(22);else partyHurt(actor,22);}}
  // Saboteurs retain their objective contact; the decorative lane itself never deals damage.
  if(e.sabotage&&typeof journey!=='undefined'&&journey.level===3&&journey.step===4&&!e.predatorVictims.has(journey)){
   const dx=-e.x,dz=-73-e.z,d=Math.hypot(dx,dz),n=Math.max(.001,d),surface={x:-dx/n*.95,z:-73-dz/n*.95};
   // The core has a .95 solid base; reach its front surface without requiring entry into that collider.
   if(d<1.7&&(d<.001||(dx*e.dx+dz*e.dz)/d>.15)&&classLine(e,surface)){e.predatorVictims.add(journey);onJourneyHazard({x:0,z:-73,r:0,damage:22});playWorldSound('impact',.8,{x:0,z:-73});}
  }
  if(next>=e.chargeDuration||travel>.02&&Math.hypot(e.x-oldX,e.z-oldZ)<.004){e.mode='recover';e.timer=e.recoveryTotal;playWorldSound('step',.8,{x:e.x,z:e.z});}
 }else if(e.mode==='recover'){e.root.rotation.y=e.lockAngle??e.root.rotation.y;if(e.timer<=0){e.mode='idle';e.timer=.55;}}
 else if(e.timer<=0&&distanceToTarget<4.6&&canCommitMelee(e))beginPredatorAttack(e,target);
 else{e.root.rotation.y=Math.atan2(e.x-target.x,e.z-target.z);if(distanceToTarget>2||!canCommitMelee(e))approachWarden(e,target,dt);}
 e.root.position.set(e.x,0,e.z);
}
