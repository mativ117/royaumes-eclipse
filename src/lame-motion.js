'use strict';
const LOCOMOTION_CLIPS=['walk','run','walk_back','strafe_left','strafe_right'];
function lameLocomotion(a,dt,speed,base,actor=p,heading=aim){
 if(!a.actions.guard)return {name:base,duration:null};
 const position={x:actor.x,z:actor.z},motion=a.lameMotion||(a.lameMotion={x:actor.x,z:actor.z,heading,speed:0,transition:null,timer:0});
 const dx=actor.x-motion.x,dz=actor.z-motion.z,travel=Math.hypot(dx,dz),turn=Math.atan2(Math.sin(heading-motion.heading),Math.cos(heading-motion.heading));let name=base,duration=null;
 const busy=actor.attack||actor.dashT>0||actor.leap>0||actor.stagger>0||actor.shield>0||campaign?.trials.forge.carrying;
 if(!busy){
  if(speed>.18&&travel<1.5&&travel>.0001){const forward=(-Math.sin(heading)*dx-Math.cos(heading)*dz)/travel,side=(Math.cos(heading)*dx-Math.sin(heading)*dz)/travel;if(forward<-.5)name='walk_back';else if(Math.abs(side)>.72)name=side>0?'strafe_right':'strafe_left';}
  else name='guard';
  if(motion.timer<=0){if(motion.speed<.15&&speed>.35){motion.transition='start';motion.timer=.24;}else if(motion.speed>.4&&speed<.15){motion.transition='stop';motion.timer=.26;}else if(speed<.15&&Math.abs(turn)>.045){motion.transition=turn>0?'turn_left':'turn_right';motion.timer=.30;}}
  if(motion.timer>0){motion.timer=Math.max(0,motion.timer-dt);name=motion.transition;duration=name==='start'?.24:name==='stop'?.26:.30;}
 }else{motion.timer=0;motion.transition=null;}
 motion.x=position.x;motion.z=position.z;motion.heading=heading;motion.speed=speed;return {name,duration};
}
function lameDodgeClip(a,actor=p,heading=aim){if(!a.actions.dodge_left)return'dash';const side=actor.dx*Math.cos(heading)-actor.dz*Math.sin(heading);return side<0?'dodge_left':'dodge_right';}
