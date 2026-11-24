'use strict';
const combatAssist={target:null};
function stableCombatTarget(candidates,actor=p){
 const next=candidates.slice().sort((a,b)=>distance(a,actor)-distance(b,actor))[0],current=combatAssist.target;
 if(current&&candidates.includes(current)&&(!next||distance(current,actor)<=distance(next,actor)*1.25+.35))return current;
 combatAssist.target=next||null;return combatAssist.target;
}
function steerAttackPreparation(actor,desired,dt,avatar=avatarRuntime.current){
 const a=actor.attack;if(!a?.melee||!avatar?.motionCalibration||a.elapsed>=a.hitAt-.055)return;
 a.initialAim??=a.aim;const cap=.65,delta=wrap(desired-a.initialAim),target=a.initialAim+Math.max(-cap,Math.min(cap,delta));a.aim+=Math.max(-dt*3.5,Math.min(dt*3.5,wrap(target-a.aim)));
}
function projectileBlockedAlong(fromX,fromZ,toX,toZ,r=.1){
 const steps=Math.max(1,Math.ceil(Math.hypot(toX-fromX,toZ-fromZ)/.08));
 for(let i=1;i<=steps;i++){const x=fromX+(toX-fromX)*i/steps,z=fromZ+(toZ-fromZ)*i/steps;if(blocked(x,z,r,true))return{x,z};}return null;
}

function beginPowerVisual(actor,id){const a=actor===p?avatarRuntime.current:actor.avatar,definition=a?.motionCalibration?.power;if(!definition||!a.actions[definition.clip||'power'])return;actor.powerVisualSerial=(actor.powerVisualSerial||0)+1;actor.powerVisualDuration=definition.duration;actor.powerVisualT=definition.duration;}
