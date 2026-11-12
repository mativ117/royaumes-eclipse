'use strict';
let hitPause=0,impactTime=0;
const sparkPool=[];
function initCombatMotion(){
 const material=new THREE.MeshBasicMaterial({color:'#ffd69a'});
 for(let i=0;i<24;i++){const o=new THREE.Mesh(sphereGeo,material);o.visible=false;scene.add(o);sparkPool.push({mesh:o,life:0,vx:0,vy:0,vz:0});}
}
function sparks(x,z,color='#ffd69a'){
 for(let i=0;i<5;i++){const s=sparkPool.find(q=>q.life<=0);if(!s)break;s.life=.25+Math.random()*.1;s.mesh.position.set(x,1.1,z);s.mesh.scale.setScalar(.045+Math.random()*.05);const a=Math.random()*Math.PI*2;s.vx=Math.cos(a)*3;s.vz=Math.sin(a)*3;s.vy=2+Math.random()*3;s.mesh.visible=true;}
 impactTime=.12;hitPause=Math.max(hitPause,.025);
}
function updateSparks(dt){for(const s of sparkPool)if(s.life>0){s.life-=dt;s.vy-=12*dt;s.mesh.position.x+=s.vx*dt;s.mesh.position.y+=s.vy*dt;s.mesh.position.z+=s.vz*dt;s.mesh.visible=s.life>0;}impactTime=Math.max(0,impactTime-dt);}
function requestAttack(){if(state==='playing')p.attackBuffer=t+.22;}
function cancelAttack(){if(p.attack&&!p.attack.struck)p.overcharge=Math.min(3,p.overcharge+(p.attack.charge||0));p.attack=null;}
function beginAttack(){
 if(state!=='playing'||p.shot>0||p.leap>0||p.attack)return;
 if(campaign.trials.forge.carrying)dropCore();
 const melee=hero==='voltigeur';
 p.combo=melee?(p.comboWindow>0?p.combo%3+1:1):0;p.comboWindow=1.05;
 const duration=melee?(p.combo===3?.64:.43):.28;
 p.attack={melee,elapsed:0,duration,hitAt:melee?(p.combo===3?.25:.16):.07,struck:false,combo:p.combo,charge:p.overcharge,aim,};
 p.overcharge=0;p.shot=duration;p.attackBuffer=0;observeTime=0;
}
function updateAttack(dt){
 const a=p.attack;if(!a)return;a.elapsed+=dt;
 if(!a.struck&&a.elapsed>=a.hitAt){
  if(campaign.trials.forge.carrying)dropCore();a.struck=true;shotCount++;p.recoil=1;
  if(a.melee)strikeMelee(a);else shootRifle(a);
 }
 if(a.elapsed>=a.duration)p.attack=null;
}
function shootRifle(a){
 const dx=-Math.sin(a.aim),dz=-Math.cos(a.aim),x=p.x+Math.cos(a.aim)*.5+dx*1.6,z=p.z-Math.sin(a.aim)*.5+dz*1.6;
 const o=mesh(sphereGeo,a.charge?cyan:gold,x,1.35,z,a.charge?.22:.12,a.charge?.22:.12,a.charge?.8:.5);o.rotation.y=a.aim;
 bullets.push({mesh:o,x,z,dx,dz,t:1.8,enemy:false,damage:34+a.charge*20});tone(440,.06,'sawtooth',.009);
}
function strikeMelee(a){
 const dx=-Math.sin(a.aim),dz=-Math.cos(a.aim);let hits=0;
 for(const e of enemies){const d=distance(e,p);if(e.dead||!trialActive(e)||e.type==='boss'&&!campaign.bossAwake)continue;
  if(d<3.5+(e.type==='boss'?1.2:0)&&((e.x-p.x)*dx+(e.z-p.z)*dz)/Math.max(.01,d)>.15&&clearStrikeLine(e.x,e.z)){
   const hp=e.hp;damage(e,(a.combo===3?72:44)+a.charge*20);if(e.hp<hp){hits++;sparks(e.x,e.z);}
   if(!e.dead&&!['boss','porter','anchor'].includes(e.type))moveEntity(e,dx*(a.combo===3?.9:.35),dz*(a.combo===3?.9:.35),.55);
  }
 }
 p.swing=.25;slashMaterial.color.set(a.charge?'#a7ecff':a.combo===3?'#fff2b6':'#ffbc76');tone(a.combo===3?140:320,.1,'triangle');
}
function poseHero(dt){
 const a=p.attack,melee=hero==='voltigeur';
 player.body.rotation.y=0;player.body.rotation.z=0;
 player.arms.forEach((arm,i)=>{arm.rotation.z=i===0?.08:-.08;});
 if(a){
  const before=a.elapsed<a.hitAt,prep=Math.min(1,a.elapsed/a.hitAt),after=Math.min(1,(a.elapsed-a.hitAt)/Math.max(.01,a.duration-a.hitAt));
  player.root.rotation.y=a.aim;
  if(a.melee){
   const side=a.combo%2?1:-1;
   player.body.rotation.y=before?-side*.55*prep:side*(.8*(1-after));
   player.body.rotation.x=a.combo===3?(before?-.18*prep:.3*(1-after)):.05;
   player.arms[1].rotation.x=before?-.8*prep:1.2*(1-after);
   player.arms[1].rotation.z=before?-side*.8*prep:side*(1-after);
   player.sword.rotation.z=before?-.9*side*prep:side*1.2*(1-after);
   player.sword.rotation.x=before?.8*prep:(-Math.PI/2-1.2)*(1-after);
   slash.rotation.x=a.combo===3?-.5:a.combo===2?-1.15:-Math.PI/2;slash.scale.setScalar(a.combo===3?3.7:3.3);slash.visible=!before&&after<.6;slashMaterial.opacity=!before?(1-after)*.8:0;slash.rotation.z=side*after*.9;
  }else{player.arms[0].rotation.x=1.2;player.arms[0].rotation.z=-.7;player.arms[1].rotation.x=1.2+p.recoil*.1;player.body.rotation.x=-p.recoil*.1;}
 }else{player.sword.rotation.x=0;}
 if(p.leap>0){const progress=1-p.leap/.75;player.arms.forEach(arm=>arm.rotation.x=-1.2);player.body.rotation.x=progress<.6?-.15:.35;player.legs.forEach((leg,i)=>leg.rotation.x=(i?1:-1)*.55);}
 if(p.dashT>0){player.body.rotation.x=.22;player.arms.forEach(arm=>arm.rotation.x=.65);}
 if(campaign.trials.forge.carrying){player.arms.forEach((arm,i)=>{arm.rotation.x=1;arm.rotation.z=i?-.45:.45});player.sword.visible=false;player.rifle.visible=false;}else{player.sword.visible=melee;player.rifle.visible=!melee;}
 if(p.stagger>0)player.body.rotation.z=Math.sin(p.stagger*55)*.1;
}
function poseEnemy(e){
 if(!e.rig)return;
 const wind=e.mode==='windup',charge=e.mode==='charge',recover=e.mode==='recover';
 const progress=wind?1-Math.max(0,Math.min(1,e.timer/(e.windupTotal||1.2))):0;
 e.rig.arms.forEach((a,i)=>{a.rotation.x=wind?-progress*(e.type==='boss'?2.5:1.7):charge?.7:recover?.35:Math.sin(t*3+i)*.08;a.rotation.z=wind?(i?1:-1)*progress*.4:0;});
 e.robe.rotation.x=wind?-.08*progress:charge?.2:recover?.12:0;
 e.root.rotation.x=charge?.12:0;
 if(e.flash>0)e.robe.rotation.z=Math.sin(t*65)*.08;else e.robe.rotation.z=0;
}
