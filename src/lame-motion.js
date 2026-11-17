'use strict';
const LOCOMOTION_CLIPS=['walk','run','walk_back','strafe_left','strafe_right'];
function readMotionCalibration(root,id){
 if(id!=='lame')return null;let raw=root.userData?.motionCalibration;root.traverse(object=>{if(!raw&&object.userData?.motionCalibration)raw=object.userData.motionCalibration;});
 try{const data=typeof raw==='string'?JSON.parse(raw):raw;if(data?.version!==1||data.units!=='model')return null;const gaits={};
  for(const name of LOCOMOTION_CLIPS){const item=data.gaits?.[name];if(!item||!Number.isFinite(item.cycleDistance)||item.cycleDistance<.2||item.cycleDistance>10)continue;const contacts={L:[],R:[]};for(const side of ['L','R'])for(const interval of (Array.isArray(item.contacts?.[side])?item.contacts[side]:[]).slice(0,4)){if(!Array.isArray(interval)||interval.length!==2||interval.some(n=>!Number.isFinite(n)||n<0||n>1))continue;const span=(interval[1]-interval[0]+1)%1;if(span>.04&&span<.9)contacts[side].push(interval.slice());}gaits[name]={cycleDistance:item.cycleDistance,duration:Number.isFinite(item.duration)&&item.duration>0&&item.duration<=4?item.duration:null,contacts,phaseOrigin:Number.isFinite(item.phaseOrigin)?((item.phaseOrigin%1)+1)%1:contacts.L[0]?.[0]||0};}
  if(!gaits.walk||!gaits.run||['walk','run'].some(name=>!gaits[name].contacts.L.length||!gaits[name].contacts.R.length))return null;const attacks={};for(const name of ['attack1','attack2','attack3']){const item=data.attacks?.[name];if(!item||!Number.isFinite(item.duration)||item.duration<=.1||item.duration>4||!Number.isFinite(item.hitAt)||item.hitAt<0||!Number.isFinite(item.activeEnd)||item.activeEnd<=item.hitAt||item.activeEnd>item.duration||!Number.isFinite(item.travel)||item.travel<0||item.travel>3)continue;attacks[name]={duration:item.duration,hitAt:item.hitAt,activeEnd:item.activeEnd,travel:item.travel};}const dodge=data.dodge;return{version:1,units:'model',gaits,attacks,rootOffset:Number.isFinite(data.rootOffset)?THREE.MathUtils.clamp(data.rootOffset,-.2,.2):0,dodge:dodge&&Number.isFinite(dodge.distance)&&dodge.distance>.2&&dodge.distance<3&&Number.isFinite(dodge.duration)&&dodge.duration>=.2&&dodge.duration<=.8?{distance:dodge.distance,duration:dodge.duration}:null};
 }catch(_){return null;}
}
function motionModelScale(a){return Math.abs(a?.root?.scale.y)||1;}
function motionCycleDistance(a,name){return a?.motionCalibration?.gaits[name]?.cycleDistance*motionModelScale(a)||(name==='run'?1.5:1.2);}
function motionNaturalSpeed(a,name){const duration=a?.actions[name]?.getClip().duration;return duration?motionCycleDistance(a,name)/duration:0;}
function motionSpeedScale(a,id=a?.heroId,actor=null,heading=0){if(id!=='lame'||!a?.motionCalibration)return 1;let gait='run';const vx=actor?.vx||0,vz=actor?.vz||0,n=Math.hypot(vx,vz);if(n>.001){const forward=(-Math.sin(heading)*vx-Math.cos(heading)*vz)/n,side=(Math.cos(heading)*vx-Math.sin(heading)*vz)/n;if(forward<-.5)gait='walk_back';else if(Math.abs(side)>.72)gait=side>0?'strafe_right':'strafe_left';}const natural=motionNaturalSpeed(a,gait),requested=HERO_DEFS[id]?.speed;return natural&&requested?Math.min(1,natural/requested):1;}
function motionGait(a,speed){if(speed<=.18)return'idle';if(!a?.motionCalibration)return speed>3?'run':'walk';const walk=motionNaturalSpeed(a,'walk'),run=motionNaturalSpeed(a,'run'),threshold=(walk+run)*.5;return speed>threshold?'run':'walk';}
function motionPlaybackRate(a,name,speed){return Math.max(.05,speed*(a.actions[name]?.getClip().duration||1)/motionCycleDistance(a,name));}
function motionTransferPhase(a,from,to,phase){const old=a.motionCalibration?.gaits[from],next=a.motionCalibration?.gaits[to];return old&&next?((phase-old.phaseOrigin+next.phaseOrigin)%1+1)%1:phase;}
function motionGaitMix(a,speed){const walk=motionNaturalSpeed(a,'walk'),run=motionNaturalSpeed(a,'run'),weight=THREE.MathUtils.clamp((speed-walk)/Math.max(.001,run-walk),0,1),distance=THREE.MathUtils.lerp(motionCycleDistance(a,'walk'),motionCycleDistance(a,'run'),weight);return{weight,distance,frequency:Math.max(0,speed/distance)};}
function blendMotionGait(a,lower,speed){
 const key=lower?'motionBlendLower':'motionBlendUpper',state=lower?a.lowerState:a.state,selected=lower?a.lowerAction:a.action,actions=lower?a.lowerActions:a.actions;
 if(!a.motionCalibration||!['walk','run'].includes(state)){if(a[key]){for(const name of ['walk','run'])if(actions[name]!==selected)actions[name].fadeOut(.10);a[key]=null;}return;}
 const mix=motionGaitMix(a,speed),origin=a.motionCalibration.gaits[state].phaseOrigin,phase=(selected.time/selected.getClip().duration-origin+1)%1;
 for(const name of ['walk','run']){const action=actions[name],duration=action.getClip().duration,offset=a.motionCalibration.gaits[name].phaseOrigin;action.enabled=true;action.stopFading().setEffectiveWeight(name==='run'?mix.weight:1-mix.weight).setEffectiveTimeScale(mix.frequency*duration).setLoop(THREE.LoopRepeat,Infinity);action.clampWhenFinished=false;action.time=((phase+offset)%1)*duration;action.play();}
 a[key]=mix;
}
function motionDodgeConfig(id,a){const config=id==='lame'?a?.motionCalibration?.dodge:null;return config?{distance:config.distance*motionModelScale(a),duration:config.duration,profile:'step'}:{distance:DODGE_DISTANCE,duration:DODGE_DURATION,profile:'legacy'};}
function motionAttackCommitted(a,actor){const attack=actor.attack;if(!attack?.melee||!a.motionCalibration)return false;const definition=a.motionCalibration.attacks?.['attack'+attack.combo];return !definition||attack.elapsed<(attack.activeEnd??definition.activeEnd)+.10;}
function beginDodgeMotion(actor,id,a){const config=motionDodgeConfig(id,a);actor.dashDuration=config.duration;actor.dashDistance=config.distance;actor.dashProfile=config.profile;actor.dashT=config.duration;actor.dashElapsed=0;if(a)a.lameDodge=null;return config;}
function actorDodgeConfig(actor){return{distance:actor.dashDistance||DODGE_DISTANCE,duration:actor.dashDuration||DODGE_DURATION,profile:actor.dashProfile||'legacy'};}
function lameTransitionDuration(a,name){return a.actions[name]?.getClip?.().duration||({start:.30,stop:.32,turn_left:.45,turn_right:.45})[name];}
function lameLocomotion(a,dt,speed,base,actor=p,heading=aim){
 if(actor.dashT<=0)a.lameDodge=null;if(!a.actions.guard)return {name:base,duration:null,restart:false};
 const motion=a.lameMotion||(a.lameMotion={x:actor.x,z:actor.z,heading,speed:0,moving:false,turnAmount:0,transition:null,timer:0});
 const dx=actor.x-motion.x,dz=actor.z-motion.z,travel=Math.hypot(dx,dz),turn=Math.atan2(Math.sin(heading-motion.heading),Math.cos(heading-motion.heading)),moving=speed>.18&&travel>.0001&&travel<1.5;
 let name=base,duration=null,restart=false,cycle=base;
 const busy=actor.attack||actor.dashT>0||actor.leap>0||actor.stagger>0||actor.shield>0||campaign?.trials.forge.carrying;
 const begin=clip=>{motion.transition=null;motion.timer=0;if(a.actions[clip]){motion.transition=clip;motion.timer=lameTransitionDuration(a,clip);restart=true;}};
 if(travel>=1.5){motion.transition=null;motion.timer=0;motion.moving=false;motion.turnAmount=0;}
 if(!busy){
  if(moving){const forward=(-Math.sin(heading)*dx-Math.cos(heading)*dz)/travel,side=(Math.cos(heading)*dx-Math.sin(heading)*dz)/travel;if(forward<-.5&&a.actions.walk_back)name='walk_back';else if(Math.abs(side)>.72){const strafe=side>0?'strafe_right':'strafe_left';if(a.actions[strafe])name=strafe;}}
  else name='guard';
  cycle=name;
  // A new physical intention interrupts the old transition rather than finishing it as a canned gesture.
  if(moving&&!motion.moving)begin('start');
  else if(!moving&&motion.moving)begin('stop');
  if(moving){motion.turnAmount=0;if(motion.transition==='stop'||motion.transition?.startsWith('turn_'))begin('start');}
  else{motion.turnAmount+=turn;const opposite=motion.transition==='turn_left'&&motion.turnAmount<-.12||motion.transition==='turn_right'&&motion.turnAmount>.12;if((motion.timer<=0||opposite)&&Math.abs(motion.turnAmount)>.12){begin(motion.turnAmount>0?'turn_left':'turn_right');motion.turnAmount=0;}}
  if(motion.timer>0){name=motion.transition;duration=lameTransitionDuration(a,name);motion.timer=Math.max(0,motion.timer-dt);}
 }else{motion.timer=0;motion.transition=null;motion.turnAmount=0;}
 motion.x=actor.x;motion.z=actor.z;motion.heading=heading;motion.speed=speed;motion.moving=moving;return {name,duration,restart,gait:cycle};
}
function lameDodgeClip(a,actor=p,heading=aim){
 if(!a.actions.dodge_left)return'dash';if(a.lameDodge&&actor.dashElapsed>=a.lameDodge.elapsed){a.lameDodge.elapsed=actor.dashElapsed;return a.lameDodge.clip;}
 const side=actor.dx*Math.cos(heading)-actor.dz*Math.sin(heading),candidate=Math.abs(side)>.45?(side<0?'dodge_left':'dodge_right'):'dash',clip=a.actions[candidate]?candidate:'dash';a.lameDodge={clip,elapsed:actor.dashElapsed};return clip;
}
