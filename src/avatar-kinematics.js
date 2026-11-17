'use strict';
const ikScratch={h:new THREE.Vector3(),k:new THREE.Vector3(),f:new THREE.Vector3(),axis:new THREE.Vector3(),bend:new THREE.Vector3(),knee:new THREE.Vector3(),end:new THREE.Vector3(),from:new THREE.Vector3(),to:new THREE.Vector3(),q:new THREE.Quaternion(),world:new THREE.Quaternion(),parent:new THREE.Quaternion(),old:new THREE.Quaternion()};
function avatarBone(a,name){return a.root.getObjectByName(name.replaceAll('.',''))||a.root.getObjectByName(name);}
function initAvatarKinematics(a){
 a.root.updateWorldMatrix(true,true);a.legs=['L','R'].map(side=>({upper:avatarBone(a,'thigh.'+side),middle:avatarBone(a,'shin.'+side),end:avatarBone(a,'foot.'+side),side:side==='L'?-1:1}));
 a.arms=['R','L'].map(side=>({upper:avatarBone(a,'upper_arm.'+side),middle:avatarBone(a,'forearm.'+side),end:avatarBone(a,'hand.'+side)}));
 for(const limb of [...a.legs,...a.arms]){
  const h=limb.upper.getWorldPosition(new THREE.Vector3()),k=limb.middle.getWorldPosition(new THREE.Vector3()),f=limb.end.getWorldPosition(new THREE.Vector3());
  limb.length1=h.distanceTo(k);limb.length2=k.distanceTo(f);limb.bind=limb.end.getWorldQuaternion(new THREE.Quaternion());limb.anchor=f.clone();limb.destination=f.clone();limb.lastPhase=0;
 }
 a.groundHeight=a.legs.reduce((sum,leg)=>sum+leg.end.getWorldPosition(new THREE.Vector3()).y,0)/a.legs.length;a.foregrip=avatarBone(a,'foregrip');a.feetWeight=0;a.weaponWeight=0;a.stepPhase=0;a.lastPosition=null;
}
function resetAvatarKinematics(a){a.feetWeight=0;a.weaponWeight=0;a.stepPhase=0;a.lastPosition=null;a.motion=null;}
function pointJointAt(joint,child,target,weight){
 const s=ikScratch; joint.getWorldPosition(s.h);child.getWorldPosition(s.f);s.from.copy(s.f).sub(s.h).normalize();s.to.copy(target).sub(s.h).normalize();
 if(s.from.lengthSq()<.9||s.to.lengthSq()<.9)return;
 s.old.copy(joint.quaternion);s.q.setFromUnitVectors(s.from,s.to);joint.getWorldQuaternion(s.world);joint.parent.getWorldQuaternion(s.parent).invert();s.q.premultiply(s.parent).multiply(s.world);joint.quaternion.slerp(s.q,weight);joint.updateWorldMatrix(false,true);
}
function solveAvatarLimb(limb,target,pole,weight,endOrientation=null){
 const s=ikScratch;limb.upper.getWorldPosition(s.h);s.axis.copy(target).sub(s.h);const raw=s.axis.length();if(raw<.001)return;s.axis.divideScalar(raw);
 const d=Math.min(raw,limb.length1+limb.length2-.002),x=(limb.length1**2-limb.length2**2+d*d)/(2*d),y=Math.sqrt(Math.max(0,limb.length1**2-x*x));
 s.bend.copy(pole).addScaledVector(s.axis,-pole.dot(s.axis));if(s.bend.lengthSq()<.001)s.bend.set(0,0,1);s.bend.normalize();
 // Copy the knee before the scratch vectors are reused by the joint solver.
 const knee=s.knee.copy(s.h).addScaledVector(s.axis,x).addScaledVector(s.bend,y),end=s.end.copy(s.h).addScaledVector(s.axis,d);
 pointJointAt(limb.upper,limb.middle,knee,weight);pointJointAt(limb.middle,limb.end,end,weight);
 if(endOrientation){limb.end.parent.getWorldQuaternion(s.parent).invert();s.q.copy(s.parent).multiply(endOrientation);limb.end.quaternion.slerp(s.q,weight);limb.end.updateWorldMatrix(false,true);}
}
function updateAvatarKinematics(a,dt,speed,actor=p,heroId=hero,heading=aim){
 a.root.updateWorldMatrix(true,true);const current=new THREE.Vector3(actor.x,0,actor.z),delta=a.lastPosition?current.clone().sub(a.lastPosition):new THREE.Vector3();a.lastPosition=current;
 heading=actor.attack?.aim??heading;const distance=delta.length(),special=actor.dashT>0||actor.leap>0;
 if(distance>1.5||special){a.feetWeight=0;a.stepPhase=0;for(const leg of a.legs){leg.end.getWorldPosition(leg.anchor);leg.destination.copy(leg.anchor);leg.lastPhase=0;}}
 const walking=!special&&distance>.0005&&speed>.18,blend=1-Math.exp(-dt*18);a.feetWeight+=((walking?1:0)-a.feetWeight)*blend;
 a.root.position.y=-.10*a.feetWeight;a.root.updateWorldMatrix(true,true);
 if(walking||a.feetWeight>.02){
  const stride=speed>3?1.5:1.2;a.stepPhase+=distance/stride;
  const forward=delta.lengthSq()>.000001?delta.normalize():new THREE.Vector3(-Math.sin(heading),0,-Math.cos(heading)),right=new THREE.Vector3(Math.cos(heading),0,-Math.sin(heading));
  const pole=new THREE.Vector3(-Math.sin(heading),0,-Math.cos(heading)),yaw=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),heading);
  for(let i=0;i<a.legs.length;i++){
   const leg=a.legs[i],phase=(a.stepPhase+i*.5)%1;
   if(a.feetWeight<.3){leg.end.getWorldPosition(leg.anchor);leg.anchor.y=a.groundHeight;leg.destination.copy(leg.anchor);}
   // Balance the stance ahead/behind the hip instead of exhausting reach before toe-off.
   if(phase>=.55&&leg.lastPhase<.55){leg.destination.copy(current).addScaledVector(right,leg.side*.16).addScaledVector(forward,stride*.725);leg.destination.y=a.groundHeight;}
   if(phase<leg.lastPhase){leg.anchor.copy(leg.destination);}
   const target=leg.anchor.clone();if(phase>=.55){const u=(phase-.55)/.45,f=u*u*(3-2*u);target.lerp(leg.destination,f);target.y+=Math.sin(u*Math.PI)*(speed>3?.19:.11);}
   // Keep a stance target on the floor when a late step reaches leg extension.
   const hip=leg.upper.getWorldPosition(new THREE.Vector3()),vertical=hip.y-target.y,reach=leg.length1+leg.length2-.004,horizontal=Math.sqrt(Math.max(0,reach*reach-vertical*vertical));
   const tx=target.x-hip.x,tz=target.z-hip.z,span=Math.hypot(tx,tz);if(span>horizontal&&span>.001){target.x=hip.x+tx/span*horizontal;target.z=hip.z+tz/span*horizontal;if(phase<.55)leg.anchor.copy(target);}
   solveAvatarLimb(leg,target,pole,a.feetWeight,yaw.clone().multiply(leg.bind));leg.lastPhase=phase;
  }
 }
 // Two-handed rifle grip, independent of the walking legs and torso recoil.
 const armed=isRifleHero(heroId)&&!special&&!(actor===p&&campaign?.trials.forge.carrying)&&actor.shield<=0&&(actor.attack&&!actor.attack.melee||a.aimHold>0);
 a.weaponWeight+=((armed?1:0)-a.weaponWeight)*(1-Math.exp(-dt*24));
 if(a.weaponWeight>.01){
  const firing=actor.attack&&!actor.attack.melee,phase=firing?actor.attack.elapsed:1,pulse=firing&&phase>=actor.attack.hitAt?Math.exp(-(phase-actor.attack.hitAt)*26):0;
  const yawAngle=actor.attack?.aim??heading,yaw=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),yawAngle),right=new THREE.Vector3(Math.cos(yawAngle),0,-Math.sin(yawAngle)),forward=new THREE.Vector3(-Math.sin(yawAngle),0,-Math.cos(yawAngle));
  const wrist=current.clone().addScaledVector(right,.12).addScaledVector(forward,.02-pulse*.055);wrist.y=1.33+pulse*.015;
  const orientation=yaw.clone().multiply(a.arms[0].bind),pitch=new THREE.Quaternion().setFromAxisAngle(right,pulse*.075);orientation.premultiply(pitch);
  solveAvatarLimb(a.arms[0],wrist,right,a.weaponWeight,orientation);
  if(a.foregrip){const grip=a.foregrip.getWorldPosition(new THREE.Vector3());solveAvatarLimb(a.arms[1],grip,right.clone().negate(),a.weaponWeight,yaw.clone().multiply(a.arms[1].bind));}
 }
 a.root.updateWorldMatrix(true,true);
}

function updateBodyDynamics(a,actor,dt){
 const heading=actor.attack?.aim??actor.aim??aim,m=a.motion||(a.motion={x:actor.x,z:actor.z,vx:0,vz:0,lean:0,side:0}),step=Math.max(.001,dt),dx=actor.x-m.x,dz=actor.z-m.z;let vx=dx/step,vz=dz/step;if(Math.hypot(dx,dz)>1.5)vx=vz=0;const ax=(vx-m.vx)/step,az=(vz-m.vz)/step,blend=1-Math.exp(-dt*12);m.x=actor.x;m.z=actor.z;m.vx+=(vx-m.vx)*blend;m.vz+=(vz-m.vz)*blend;m.lean+=(THREE.MathUtils.clamp((-Math.sin(heading)*ax-Math.cos(heading)*az)*.0025,-.085,.085)-m.lean)*blend;m.side+=(THREE.MathUtils.clamp((Math.cos(heading)*ax-Math.sin(heading)*az)*.002,-.07,.07)-m.side)*blend;
 if(actor.leap>0||actor.dashT>0)return;const spine=avatarBone(a,'spine'),chest=avatarBone(a,'chest');spine.rotation.x+=m.lean;chest.rotation.z-=m.side;const cape=avatarBone(a,'cape_mid'),tip=avatarBone(a,'cape_tip');if(cape){cape.rotation.x+=.035*Math.sin(t*1.4)+(Math.hypot(m.vx,m.vz)*.018);tip.rotation.x+=.065*Math.sin(t*1.6+.6)+Math.hypot(m.vx,m.vz)*.022;}
}
