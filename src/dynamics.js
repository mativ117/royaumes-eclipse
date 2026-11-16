'use strict';
// Gameplay motion: time-integrated dodge and authored attack advancement.
const DODGE_DURATION=.28,DODGE_DISTANCE=4.2;
function dodgeTravel(from,to){const f=u=>2*u-u*u;return DODGE_DISTANCE*(f(Math.min(1,to/DODGE_DURATION))-f(Math.min(1,from/DODGE_DURATION)));}
function advanceHeroMotion(dt){
 if(p.downed)return;
 if(p.dashElapsed!==undefined&&p.dashElapsed<DODGE_DURATION){const next=Math.min(DODGE_DURATION,p.dashElapsed+dt),travel=dodgeTravel(p.dashElapsed,next);moveEntity(p,p.dx*travel,p.dz*travel);p.dashElapsed=next;}
 else moveEntity(p,p.vx*dt,p.vz*dt);
}
function requestDodge(){if(state!=='playing')return;p.dodgeBuffer=t+.16;if(p.dash<=0)dash();}
function attackAdvance(a,previous){
 if(!a.melee)return;const f=time=>{const u=Math.max(0,Math.min(1,time/a.hitAt));return u*u*(3-2*u);};
 const travel=(a.combo===3?.95:.6)*(f(a.elapsed)-f(previous));if(travel<=0)return;
 // Stop short of a target instead of moving through it on contact.
 const dx=-Math.sin(a.aim),dz=-Math.cos(a.aim);let allowed=travel;
 for(const e of enemies){if(e.dead||!trialActive(e))continue;const along=(e.x-p.x)*dx+(e.z-p.z)*dz,side=Math.abs((e.x-p.x)*dz-(e.z-p.z)*dx);if(along>0&&side<.9)allowed=Math.min(allowed,Math.max(0,along-(e.type==='boss'?1.9:1.05)));}
 moveEntity(p,dx*allowed,dz*allowed);
}
function canCommitMelee(e){return enemies.filter(q=>q!==e&&!q.dead&&q.type==='warden'&&q.mode==='windup'&&distance(q,p)<6).length<2;}
function approachWarden(e,target,dt){
 if(target!==p||distance(e,p)>8){steerToward(e,target,dt,3.3);return;}
 // Reserve different approach lanes instead of sending every actor to the same point.
 const angle=Math.atan2(e.z-p.z,e.x-p.x)+(e.approachSide||1)*.42;
 const waiting=!canCommitMelee(e),radius=waiting?4.4:1.9;
 steerToward(e,{x:p.x+Math.cos(angle)*radius,z:p.z+Math.sin(angle)*radius},dt,waiting?2:3.1);
}
function resolveActorContacts(dt){
 const bodies=enemies.filter(e=>!e.dead&&trialActive(e)&&e.type!=='shade'&&e.type!=='anchor'&&e.type!=='duelist'&&distance(e,p)<18);
 const radius=e=>e.type==='boss'?1.3:e.type==='porter'?.85:.48;
 for(let i=0;i<bodies.length;i++)for(let j=i+1;j<bodies.length;j++){
  const a=bodies[i],b=bodies[j],dx=b.x-a.x,dz=b.z-a.z,d=Math.hypot(dx,dz),limit=radius(a)+radius(b);if(d>=limit)continue;
  const nx=d?dx/d:1,nz=d?dz/d:0,push=Math.min((limit-d)*.5,dt*2);
  if(!['windup','charge'].includes(a.mode))moveEntity(a,-nx*push,-nz*push,radius(a));
  if(!['windup','charge'].includes(b.mode))moveEntity(b,nx*push,nz*push,radius(b));
 }
 if(p.dashT<=0&&p.leap<=0)for(const e of bodies){const dx=p.x-e.x,dz=p.z-e.z,d=Math.hypot(dx,dz),limit=radius(e)+.43;if(d<limit){const push=Math.min(limit-d,dt*4);moveEntity(p,(d?dx/d:1)*push,(d?dz/d:0)*push);}}
 for(const e of bodies)e.root.position.set(e.x,0,e.z);
 player.root.position.x=p.x;player.root.position.z=p.z;
}
