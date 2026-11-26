'use strict';
// Presentation only: contacts consume an observed HP delta, never a hit guess.
// Two fixed geometry batches; no light, texture, timer, or gameplay mutation.
const combatFeedbackV17={root:null,glow:null,chips:null,clock:0,serial:41,events:0,traces:0,weapons:new WeakMap(),stats:{contacts:0,blocks:0,rejected:0,dropped:0,peak:0}};
const combatFeedbackProfilesV17=Object.freeze({
 voltigeur:{edge:.026,trail:.10,color:'#e9ba78'},lame:{edge:.017,trail:.12,color:'#ffdfa2'},
 voleur:{edge:.016,trail:.075,color:'#c7a574'},colosse:{edge:.045,trail:.075,color:'#ddc8a0'},
 neant:{edge:.021,trail:.09,color:'#a8987c'},eclipse:{edge:.027,trail:.11,color:'#f3cb7b'},
 rempart:{edge:.012,trail:.045,color:'#f9d99c'},cendres:{edge:.023,trail:.07,color:'#ed9a4d'},
 tisseuse:{edge:.018,trail:.065,color:'#cbb08b'},bergere:{edge:.014,trail:.07,color:'#e9d6ae'},
 accordeur:{edge:.016,trail:.05,color:'#d8b17e'}
});
function combatFeedbackLimitsV17(){
 const reduced=typeof localProfile!=='undefined'&&!!localProfile.settings?.reduced,light=typeof quality!=='undefined'&&quality==='light';
 return reduced?{glow:20,chips:6,events:3,traces:8,reduced:true}:light?{glow:36,chips:12,events:5,traces:14,reduced:false}:{glow:72,chips:24,events:8,traces:24,reduced:false};
}
function combatFeedbackBatchV17(capacity,additive){
 const geometry=new THREE.BufferGeometry(),position=new THREE.BufferAttribute(new Float32Array(capacity*18),3),color=new THREE.BufferAttribute(new Float32Array(capacity*18),3);
 position.setUsage(THREE.DynamicDrawUsage);color.setUsage(THREE.DynamicDrawUsage);geometry.setAttribute('position',position);geometry.setAttribute('color',color);geometry.setDrawRange(0,0);
 const material=new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide,transparent:true,opacity:additive?.86:.92,depthWrite:false,depthTest:true,blending:additive?THREE.AdditiveBlending:THREE.NormalBlending,toneMapped:true});
 const mesh=new THREE.Mesh(geometry,material);mesh.frustumCulled=false;mesh.visible=false;mesh.renderOrder=additive?4:3;combatFeedbackV17.root.add(mesh);
 return{mesh,geometry,position,color,pool:Array.from({length:capacity},()=>({life:0,max:1,x:0,y:0,z:0,dx:0,dy:0,dz:0,vx:0,vy:0,vz:0,length:0,width:0,gravity:0,r:0,g:0,b:0})),active:0,additive};
}
function initCombatFeedbackV17(){
 const s=combatFeedbackV17;if(s.root)return s;if(typeof scene==='undefined')return null;
 s.root=new THREE.Group();s.root.name='combat-feedback-v17';scene.add(s.root);s.glow=combatFeedbackBatchV17(72,true);s.chips=combatFeedbackBatchV17(24,false);
 s.arrow=new THREE.ConeGeometry(.055,.34,3,1);s.arrow.rotateX(-Math.PI/2);s.color=new THREE.Color();s.camera=new THREE.Vector3();return s;
}
function combatFeedbackRandomV17(){const s=combatFeedbackV17;s.serial=(Math.imul(s.serial,1664525)+1013904223)>>>0;return s.serial/4294967296;}
function combatFeedbackSpawnV17(batch,point,direction,length,width,life,color,speed=0,gravity=0,optional=false){
 const s=combatFeedbackV17,limits=combatFeedbackLimitsV17(),limit=batch===s.glow?limits.glow:limits.chips;
 // Optional trails leave contact capacity, and may be replaced by a real hit.
 if(optional&&batch.active>=Math.floor(limit*.7)){s.stats.dropped++;return false;}
 let q=batch.pool.find(particle=>particle.life<=0);if(batch.active>=limit){q=optional?null:batch.pool.find(particle=>particle.life>0&&particle.optional);if(q)batch.active--;}
 if(!q){s.stats.dropped++;return false;}
 const n=Math.hypot(direction.x,direction.y||0,direction.z)||1;s.color.set(color);
 Object.assign(q,{life,max:life,x:point.x,y:point.y,z:point.z,dx:direction.x/n,dy:(direction.y||0)/n,dz:direction.z/n,length,width,gravity,optional,r:s.color.r,g:s.color.g,b:s.color.b});
 q.vx=q.dx*speed;q.vy=q.dy*speed;q.vz=q.dz*speed;batch.active++;s.stats.peak=Math.max(s.stats.peak,s.glow.active+s.chips.active);s.root.visible=true;return true;
}
function combatFeedbackDirectionV17(target,source,options={}){
 const owner=source?.owner||source,heading=owner?.attack?.aim??owner?.aim??0,d=options.direction;
 let x=d?.x??(target.x-(source?.x??owner?.x??target.x)),y=d?.y||0,z=d?.z??(target.z-(source?.z??owner?.z??target.z));
 const n=Math.hypot(x,y,z);if(!Number.isFinite(n)||n<.001){x=-Math.sin(Number.isFinite(heading)?heading:0);y=0;z=-Math.cos(Number.isFinite(heading)?heading:0);return{x,y,z};}return{x:x/n,y:y/n,z:z/n};
}
function combatFeedbackPointV17(target,direction,options={},source=null){
 if(options.point&&[options.point.x,options.point.y,options.point.z].every(Number.isFinite))return options.point;
 const scale=Math.min(2.2,Math.max(.65,Math.abs(target.root?.scale?.y)||1));
 const blade=options.kind==='melee'&&(source?.owner||source)?.attack?.bladeSample;
 if(blade?.base&&blade.tip){const a=blade.base,b=blade.tip,dx=b.x-a.x,dy=b.y-a.y,dz=b.z-a.z,n=dx*dx+dy*dy+dz*dz,u=n?Math.max(0,Math.min(1,((target.x-a.x)*dx+(1.16*scale-a.y)*dy+(target.z-a.z)*dz)/n)):0,point={x:a.x+dx*u,y:a.y+dy*u,z:a.z+dz*u};if(Math.hypot(point.x-target.x,point.z-target.z)<.9*scale)return point;}
 return{x:target.x-direction.x*.32*scale,y:1.16*scale,z:target.z-direction.z*.32*scale};
}
function combatFeedbackMaterialV17(target,options={}){
 if(options.material)return options.material;
 const id=target.heroId||(typeof p!=='undefined'&&target===p&&typeof hero!=='undefined'?hero:'');
 if(target.type==='sentinel'||target.type==='boss'||id==='rempart')return'metal';
 if(target.type==='anchor'||target.type==='porter'||id==='colosse')return'stone';
 if(target.type==='shade'||id==='neant'||id==='eclipse')return'void';return'cloth';
}
function combatFeedbackEventV17(){const s=initCombatFeedbackV17();if(!s)return false;if(s.events>=combatFeedbackLimitsV17().events){s.stats.dropped++;return false;}s.events++;return true;}
function combatFeedbackContactV17(target,beforeHP,source,options={}){
 const s=combatFeedbackV17,amount=beforeHP-target?.hp;
 if(!target||!Number.isFinite(beforeHP)||!Number.isFinite(target.hp)||!(amount>0)||![target.x,target.z].every(Number.isFinite)){s.stats.rejected++;return false;}
 if(!combatFeedbackEventV17())return false;s.stats.contacts++;
 const owner=source?.owner||source,id=options.heroId||source?.heroId||owner?.heroId||(typeof p!=='undefined'&&owner===p&&typeof hero!=='undefined'?hero:''),profile=combatFeedbackProfilesV17[id]||combatFeedbackProfilesV17.lame;
 const kind=options.kind||source?.feedbackKind||(owner?.attack?.melee?'melee':source?'projectile':'power'),direction=combatFeedbackDirectionV17(target,source,options),point=combatFeedbackPointV17(target,direction,{...options,kind},source),material=combatFeedbackMaterialV17(target,options),limits=combatFeedbackLimitsV17();
 const side={x:-direction.z,y:.2,z:direction.x},bright=material==='metal'?'#ffe2aa':profile.color,hefty=id==='colosse',count=limits.reduced?2:material==='metal'?5:3;
 // A small incision, needle, or angular bracket sits at the accepted contact.
 if(kind==='melee')combatFeedbackSpawnV17(s.glow,point,options.tangent||s.weapons.get(owner)?.delta||{x:side.x,y:hefty?-.9:.45,z:side.z},hefty?.34:.48,hefty?.05:.023,limits.reduced?.10:.14,bright);
 else if(kind==='power')for(const sign of[-1,1])combatFeedbackSpawnV17(s.glow,{x:point.x+side.x*.13*sign,y:point.y+.07,z:point.z+side.z*.13*sign},{x:side.x*sign,y:.8,z:side.z*sign},.23,.021,.15,bright);
 else combatFeedbackSpawnV17(s.glow,point,direction,.30,.027,.10,bright);
 for(let i=0;i<count;i++){
  const spread=(combatFeedbackRandomV17()-.5)*1.6,up=.35+combatFeedbackRandomV17()*.8,d={x:direction.x*.35+side.x*spread,y:up,z:direction.z*.35+side.z*spread};
  combatFeedbackSpawnV17(s.glow,point,d,(material==='metal'?.18:.09)+combatFeedbackRandomV17()*.12,material==='metal'?.012:.021,.13+combatFeedbackRandomV17()*.09,bright,limits.reduced?0:1.8+combatFeedbackRandomV17()*2,limits.reduced?0:8);
 }
 if(!limits.reduced)for(let i=0;i<(material==='stone'||hefty?4:2);i++){
  const spread=(combatFeedbackRandomV17()-.5)*2,d={x:direction.x*.5+side.x*spread,y:.6+combatFeedbackRandomV17(),z:direction.z*.5+side.z*spread};
  combatFeedbackSpawnV17(s.chips,point,d,material==='stone'?.105:.065,material==='stone'?.055:.028,.22+combatFeedbackRandomV17()*.12,material==='stone'?'#71614d':material==='void'?'#2b2621':'#59402b',1.8+combatFeedbackRandomV17(),11);
 }
 return true;
}
// Only call from a real shield/plate/invulnerability branch, never from a miss.
function combatFeedbackBlockV17(target,source,options={}){
 if(!target||![target.x,target.z].every(Number.isFinite)||!combatFeedbackEventV17())return false;
 const s=combatFeedbackV17,d=combatFeedbackDirectionV17(target,source,options),point=combatFeedbackPointV17(target,d,options),side={x:-d.z,y:0,z:d.x};s.stats.blocks++;
 for(const sign of[-1,1])combatFeedbackSpawnV17(s.glow,point,{x:side.x*sign-d.x*.4,y:.8,z:side.z*sign-d.z*.4},.30,.024,.16,'#e0c393',combatFeedbackLimitsV17().reduced?0:.8);
 return true;
}
function combatFeedbackWeaponV17(actor,avatar,id,dt=1/60){
 if(!actor||!avatar?.blade||!(avatar.bladeBase||avatar.hand))return;const s=initCombatFeedbackV17();if(!s)return;
 const a=actor.attack,info=a&&avatar.motionCalibration?.attacks?.['attack'+a.combo],end=a&&(a.activeEnd??info?.activeEnd??Math.min(a.duration,a.hitAt+.18));
 // The same active window and world sockets as resolveBladeContacts.
 if(!a?.melee||actor.downed||a.elapsed<a.hitAt||a.elapsed>end){s.weapons.delete(actor);return;}
 avatar.root.updateWorldMatrix(true,true);const base=(avatar.bladeBase||avatar.hand).getWorldPosition(new THREE.Vector3()),tip=avatar.blade.getWorldPosition(new THREE.Vector3()),old=s.weapons.get(actor),profile=combatFeedbackProfilesV17[id]||combatFeedbackProfilesV17.lame;
 s.weapons.set(actor,{attack:a,base,tip,delta:old&&old.attack===a?{x:tip.x-old.tip.x,y:tip.y-old.tip.y,z:tip.z-old.tip.z}:null});if(!old||old.attack!==a||combatFeedbackLimitsV17().reduced)return;
 if(!(dt>0)||old.tip.distanceTo(tip)>3||s.traces>=combatFeedbackLimitsV17().traces)return;
 const travel=old.tip.distanceTo(tip);if(travel<.015)return;s.traces++;
 const direction={x:tip.x-old.tip.x,y:tip.y-old.tip.y,z:tip.z-old.tip.z},point={x:(tip.x+old.tip.x)*.5,y:(tip.y+old.tip.y)*.5,z:(tip.z+old.tip.z)*.5};
 combatFeedbackSpawnV17(s.glow,point,direction,Math.min(.65,travel),profile.edge,profile.trail,profile.color,0,0,true);
 // A short highlight along the actual blade, never a radial proxy for its reach.
 if(id==='colosse'||id==='eclipse')combatFeedbackSpawnV17(s.glow,tip,{x:tip.x-base.x,y:tip.y-base.y,z:tip.z-base.z},.17,profile.edge*.75,.07,'#e5c491',0,0,true);
}
function combatFeedbackProjectileV17(projectile,oldX,oldZ,oldY=projectile?.y??1.35){
 if(!projectile||![oldX,oldZ,oldY,projectile.x,projectile.z].every(Number.isFinite))return false;const s=initCombatFeedbackV17();if(!s)return false;const limits=combatFeedbackLimitsV17();
 if(projectile.enemy&&projectile.mesh?.geometry?.type==='SphereGeometry'&&Number.isFinite(projectile.dx)&&Number.isFinite(projectile.dz)){projectile.mesh.geometry=s.arrow;projectile.mesh.scale.set(1,1,1);projectile.mesh.rotation.set(0,Math.atan2(-projectile.dx,-projectile.dz),0);}
 if(limits.reduced||s.traces>=limits.traces)return false;const y=projectile.y??1.35,dx=projectile.x-oldX,dy=y-oldY,dz=projectile.z-oldZ,n=Math.hypot(dx,dy,dz);
 if(n<.025||n>3)return false;s.traces++;const profile=combatFeedbackProfilesV17[projectile.heroId]||combatFeedbackProfilesV17.rempart;
 return combatFeedbackSpawnV17(s.glow,{x:(oldX+projectile.x)*.5,y:(oldY+y)*.5,z:(oldZ+projectile.z)*.5},{x:dx,y:dy,z:dz},Math.min(n,.85),projectile.enemy?.012:profile.edge,profile.trail,projectile.enemy?'#b88556':profile.color,0,0,true);
}
function updateCombatFeedbackBatchV17(batch,dt){
 const s=combatFeedbackV17,eye=s.camera,positions=batch.position,colors=batch.color,limits=combatFeedbackLimitsV17(),limit=batch===s.glow?limits.glow:limits.chips;let vertices=0,active=0;
 for(const q of batch.pool){if(q.life<=0)continue;q.life=Math.max(0,q.life-dt);if(q.life<=0)continue;if(active>=limit){q.life=0;continue;}active++;if(!limits.reduced){q.vy-=q.gravity*dt;q.x+=q.vx*dt;q.y+=q.vy*dt;q.z+=q.vz*dt;}
  const fade=q.life/q.max,length=q.length*(.60+.4*fade),width=q.width*(.35+.65*fade),cx=eye.x-q.x,cy=eye.y-q.y,cz=eye.z-q.z;
  let rx=q.dy*cz-q.dz*cy,ry=q.dz*cx-q.dx*cz,rz=q.dx*cy-q.dy*cx,rn=Math.hypot(rx,ry,rz);if(rn<.00001){rx=1;ry=0;rz=0;rn=1;}rx=rx/rn*width;ry=ry/rn*width;rz=rz/rn*width;
  const tx=q.dx*length*.5,ty=q.dy*length*.5,tz=q.dz*length*.5,brightness=batch.additive?fade*fade:1;
  for(const index of[0,1,2,0,2,3]){const vx=index===0?tx:index===2?-tx:index===1?rx:-rx,vy=index===0?ty:index===2?-ty:index===1?ry:-ry,vz=index===0?tz:index===2?-tz:index===1?rz:-rz;
   positions.setXYZ(vertices,q.x+vx,q.y+vy,q.z+vz);colors.setXYZ(vertices,q.r*brightness,q.g*brightness,q.b*brightness);vertices++;
  }
 }
 batch.active=active;batch.geometry.setDrawRange(0,vertices);batch.position.needsUpdate=true;batch.color.needsUpdate=true;batch.mesh.visible=vertices>0;
}
function updateCombatFeedbackV17(dt){
 const s=combatFeedbackV17;if(!s.root)return;if(!Number.isFinite(dt)||dt<0)return;s.clock+=Math.min(dt,.1);s.events=0;s.traces=0;
 if(typeof camera!=='undefined')camera.getWorldPosition(s.camera);else s.camera.set(0,10,10);
 updateCombatFeedbackBatchV17(s.glow,Math.min(dt,.1));updateCombatFeedbackBatchV17(s.chips,Math.min(dt,.1));s.root.visible=s.glow.active+s.chips.active>0;
}
function clearCombatFeedbackV17(){
 const s=combatFeedbackV17;if(s.root){for(const batch of[s.glow,s.chips]){for(const q of batch.pool)q.life=0;batch.active=0;batch.geometry.setDrawRange(0,0);batch.mesh.visible=false;}s.root.visible=false;}
 s.weapons=new WeakMap();s.events=s.traces=0;s.clock=0;
}
function disposeCombatFeedbackV17(){
 const s=combatFeedbackV17;if(!s.root)return;clearCombatFeedbackV17();s.root.removeFromParent();for(const batch of[s.glow,s.chips]){batch.geometry.dispose();batch.mesh.material.dispose();}s.arrow.dispose();s.arrow=null;s.root=s.glow=s.chips=null;
}
