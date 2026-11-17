'use strict';
const LOCOMOTION_CLIPS=['walk','run','walk_back','strafe_left','strafe_right'];
function lameTransitionDuration(a,name){return a.actions[name]?.getClip?.().duration||({start:.30,stop:.32,turn_left:.45,turn_right:.45})[name];}
function lameLocomotion(a,dt,speed,base,actor=p,heading=aim){
 if(!a.actions.guard)return {name:base,duration:null,restart:false};
 const motion=a.lameMotion||(a.lameMotion={x:actor.x,z:actor.z,heading,speed:0,moving:false,turnAmount:0,transition:null,timer:0});
 const dx=actor.x-motion.x,dz=actor.z-motion.z,travel=Math.hypot(dx,dz),turn=Math.atan2(Math.sin(heading-motion.heading),Math.cos(heading-motion.heading)),moving=speed>.18&&travel>.0001&&travel<1.5;
 let name=base,duration=null,restart=false;
 const busy=actor.attack||actor.dashT>0||actor.leap>0||actor.stagger>0||actor.shield>0||campaign?.trials.forge.carrying;
 const begin=clip=>{motion.transition=null;motion.timer=0;if(a.actions[clip]){motion.transition=clip;motion.timer=lameTransitionDuration(a,clip);restart=true;}};
 if(travel>=1.5){motion.transition=null;motion.timer=0;motion.moving=false;motion.turnAmount=0;}
 if(!busy){
  if(moving){const forward=(-Math.sin(heading)*dx-Math.cos(heading)*dz)/travel,side=(Math.cos(heading)*dx-Math.sin(heading)*dz)/travel;if(forward<-.5&&a.actions.walk_back)name='walk_back';else if(Math.abs(side)>.72){const strafe=side>0?'strafe_right':'strafe_left';if(a.actions[strafe])name=strafe;}}
  else name='guard';
  // A new physical intention interrupts the old transition rather than finishing it as a canned gesture.
  if(moving&&!motion.moving)begin('start');
  else if(!moving&&motion.moving)begin('stop');
  if(moving){motion.turnAmount=0;if(motion.transition==='stop'||motion.transition?.startsWith('turn_'))begin('start');}
  else{motion.turnAmount+=turn;const opposite=motion.transition==='turn_left'&&motion.turnAmount<-.12||motion.transition==='turn_right'&&motion.turnAmount>.12;if((motion.timer<=0||opposite)&&Math.abs(motion.turnAmount)>.12){begin(motion.turnAmount>0?'turn_left':'turn_right');motion.turnAmount=0;}}
  if(motion.timer>0){name=motion.transition;duration=lameTransitionDuration(a,name);motion.timer=Math.max(0,motion.timer-dt);}
 }else{motion.timer=0;motion.transition=null;motion.turnAmount=0;}
 motion.x=actor.x;motion.z=actor.z;motion.heading=heading;motion.speed=speed;motion.moving=moving;return {name,duration,restart};
}
function lameDodgeClip(a,actor=p,heading=aim){if(!a.actions.dodge_left)return'dash';const side=actor.dx*Math.cos(heading)-actor.dz*Math.sin(heading);return side<0?'dodge_left':'dodge_right';}
