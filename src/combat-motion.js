'use strict';
let hitPause=0,impactTime=0;
const sparkPool=[];
function initCombatMotion(){
 const material=new THREE.MeshBasicMaterial({color:'#ffd69a'});
 for(let i=0;i<24;i++){const o=new THREE.Mesh(sphereGeo,material);o.visible=false;scene.add(o);sparkPool.push({mesh:o,life:0,vx:0,vy:0,vz:0});}
}
function sparks(x,z,color='#ffd69a'){
 if(typeof combatFeedbackContactV17==='function'){impactTime=.12;if(!localProfile.settings.reduced)hitPause=Math.max(hitPause,.025);return;}
 for(let i=0;i<5;i++){const s=sparkPool.find(q=>q.life<=0);if(!s)break;s.life=.25+Math.random()*.1;s.mesh.position.set(x,1.1,z);s.mesh.scale.setScalar(.045+Math.random()*.05);const a=Math.random()*Math.PI*2;s.vx=Math.cos(a)*3;s.vz=Math.sin(a)*3;s.vy=2+Math.random()*3;s.mesh.visible=true;}
 impactTime=.12;if(!localProfile.settings.reduced)hitPause=Math.max(hitPause,.025);
}
function updateSparks(dt){for(const s of sparkPool)if(s.life>0){s.life-=dt;s.vy-=12*dt;s.mesh.position.x+=s.vx*dt;s.mesh.position.y+=s.vy*dt;s.mesh.position.z+=s.vz*dt;s.mesh.visible=s.life>0;}impactTime=Math.max(0,impactTime-dt);}
function requestAttack(){if(typeof queueLanAction==='function'&&queueLanAction('fire'))return;if(state==='playing'){const remaining=p.attack?Math.max(0,p.attack.duration-p.attack.elapsed):0;p.attackBuffer=t+(p.attack&&remaining<.35?remaining+.14:.22);}}
function cancelAttack(){if(p.attack){if(!p.attack.struck)p.overcharge=Math.min(3,p.overcharge+(p.attack.charge||0));p.shot=Math.min(p.shot||0,.16);}p.attack=null;}
function meleeClipDuration(id,combo,fallback){const clip=isHeroId(id)?avatarRuntime.heroes[id]?.motionCalibration?.attacks?.['attack'+combo]&&avatarRuntime.heroes[id]?.actions['attack'+combo]?.getClip():null;return clip?.duration||fallback;}
function beginAttack(){
 if(typeof queueLanAction==='function'&&queueLanAction('fire'))return;
 if(state!=='playing'||p.downed||battle?.crownOwner===p||p.shot>0||p.leap>0||p.stagger>0||p.attack)return;
 if(campaign.trials.forge.carrying)dropCore();
 const melee=isMeleeHero();
 p.combo=melee?(p.comboWindow>0?p.combo%3+1:1):0;p.comboWindow=1.05;
 const slow=hero==='cendres'&&p.heat>=100?1.6:1,baseDuration=(melee?(p.combo===3?.64:.43):.28)*(HEROES[hero].attackRate||1),duration=(melee?meleeClipDuration(hero,p.combo,baseDuration):(avatarRuntime.current?.motionCalibration?.shot?.duration||baseDuration))*slow;
 const definition=melee?avatarRuntime.current?.motionCalibration?.attacks?.['attack'+p.combo]:avatarRuntime.current?.motionCalibration?.shot;
 p.attack={id:p.attackSerial=(p.attackSerial||0)+1,melee,elapsed:0,duration,hitAt:definition?.hitAt!==undefined?definition.hitAt*slow:(melee?duration*(p.combo===3?.390625:.372093):duration*.25),activeEnd:definition?.activeEnd!==undefined?definition.activeEnd*slow:undefined,struck:false,combo:p.combo,charge:p.overcharge,aim,};
 if(melee&&avatarRuntime.current?.motionCalibration){p.vx=p.vz=0;p.comboWindow=duration+.35;}
 if(hero==='accordeur'&&classEffects.some(f=>f.kind==='rhythm'&&f.owner===p&&t-(f.lastPulse||-100)<.13))p.attack.charge=Math.min(3,p.attack.charge+1);p.overcharge=0;p.shot=duration;p.attackBuffer=0;observeTime=0;
}
function updateAttack(dt){
 const a=p.attack;if(!a)return;const previous=a.elapsed;a.elapsed+=dt;attackAdvance(a,previous);
 if(!a.struck&&a.elapsed>=a.hitAt){
  if(campaign.trials.forge.carrying)dropCore();a.struck=true;shotCount++;p.recoil=1;playWorldSound(a.melee?'blade':'shot');
  if(a.melee)strikeMelee(a);else shootRifle(a);
 }
 if(a.elapsed>=a.duration)p.attack=null;
}
function shootRifle(a){
 const dx=-Math.sin(a.aim),dz=-Math.cos(a.aim);let x=p.x+Math.cos(a.aim)*.5+dx*1.6,z=p.z-Math.sin(a.aim)*.5+dz*1.6,y=1.35;
 const anchor=avatarRuntime.current?.muzzle;if(anchor){avatarRuntime.current.root.updateMatrixWorld(true);const origin=anchor.getWorldPosition(new THREE.Vector3());x=origin.x+dx*.08;z=origin.z+dz*.08;y=origin.y;}
 if(hero==='cendres')p.heat=Math.min(100,(p.heat||0)+12);
 // A long weapon can visually reach through nearby cover. Its muzzle must not
 // spawn a shot on the far side without crossing the same collision boundary.
 const muzzleWall=projectileBlockedAlong(p.x,p.z,x,z,.1);if(muzzleWall){effect(muzzleWall.x,muzzleWall.z,.6,'#ffc17b',.2);return;}
 const projectileMaterial=a.charge?cyan:hero==='rempart'?gold:classProjectileMaterial(hero);const o=mesh(sphereGeo,projectileMaterial,x,y,z,a.charge?.14:.065,a.charge?.14:.065,a.charge?.7:.4);o.rotation.y=a.aim;
 bullets.push({mesh:o,x,z,y,dx,dz,t:1.8,enemy:false,heroId:hero,owner:p,arcStart:isRifleHero()?null:y,damage:(hero==='cendres'?30:hero==='accordeur'?32:34)+a.charge*20});
}
function strikeMelee(a){
 if(usesBladeContacts(a)){p.swing=.25;return;}
 const dx=-Math.sin(a.aim),dz=-Math.cos(a.aim);let hits=0;
 for(const e of enemies){const d=distance(e,p);if(e.dead||!trialActive(e)||e.type==='boss'&&!campaign.bossAwake)continue;
  if(d<2.7+(e.type==='boss'?1.2:0)&&((e.x-p.x)*dx+(e.z-p.z)*dz)/Math.max(.01,d)>.15&&clearStrikeLine(e.x,e.z)){
   const hp=e.hp;damage(e,((a.combo===3?72:44)+a.charge*20)*(hero==='colosse'?1.4:hero==='eclipse'?1.1:1),{...p,owner:p,heroId:hero,feedbackKind:'melee'});if(e.hp<hp){hits++;sparks(e.x,e.z);}
   if(!e.dead&&!['boss','porter','anchor'].includes(e.type))moveEntity(e,dx*(a.combo===3?.9:.35),dz*(a.combo===3?.9:.35),.55);
  }
 }
 p.swing=.25;slashMaterial.color.set(a.charge?'#a7ecff':a.combo===3?'#fff2b6':'#ffbc76');
}
function poseHero(dt){
 const a=p.attack,melee=isMeleeHero();
 player.body.rotation.y=0;player.body.rotation.z=0;
 if(artDirection){player.cape.rotation.x+=Math.sin(artDirection.clock*1.3)*.025;player.cape.rotation.z=Math.sin(artDirection.clock*.8)*.035;}
 player.arms.forEach((arm,i)=>{arm.rotation.z=i===0?.08:-.08;});
 if(a){
  const before=a.elapsed<a.hitAt,prep=Math.min(1,a.elapsed/a.hitAt),after=Math.min(1,(a.elapsed-a.hitAt)/Math.max(.01,a.duration-a.hitAt));
  player.root.rotation.y=a.melee&&avatarRuntime.current?.motionCalibration&&!motionAttackCommitted(avatarRuntime.current,p)?aim:a.aim;
  if(a.melee){
   const side=a.combo%2?1:-1;
   player.legs.forEach((leg,i)=>{leg.rotation.x=(i?-.12:.15)*(a.combo===3?1.4:1);});
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
 if(!a&&p.leap<=0&&p.dashT<=0&&campaign.worldUse&&t-campaign.worldUse.started<.55){const reach=Math.sin((t-campaign.worldUse.started)/.55*Math.PI);player.arms[1].rotation.x=reach*1.3;player.body.rotation.y=-reach*.12;}
 if(p.stagger>0)player.body.rotation.z=Math.sin(p.stagger*55)*.1;updateRigAvatar(dt);
}
function poseEnemy(e,dt=1/60){if(typeof poseEnemyDirectionV16==='function'&&poseEnemyDirectionV16(e,dt))return;
 if(updateCreatureReference(e,1/60))return;
 if(!e.rig)return;
 const moved=e.poseX===undefined?0:Math.hypot(e.x-e.poseX,e.z-e.poseZ),poseDt=Math.max(.001,t-(e.poseTime??t-1/60));e.poseX=e.x;e.poseZ=e.z;e.poseTime=t;e.gaitPhase=(e.gaitPhase||0)+moved/(['boss','porter'].includes(e.type)?1.8:1.3)*Math.PI*2;
 const walking=Math.min(1,moved/poseDt/2.5);for(let i=0;i<(e.rig.legs||[]).length;i++){const leg=e.rig.legs[i],wave=Math.sin(e.gaitPhase+i*Math.PI);leg.root.rotation.x=wave*.5*walking;leg.shin.rotation.x=Math.max(0,-wave)*.8*walking;}
 if(e.visualFacing===undefined)e.visualFacing=e.root.rotation.y;e.visualFacing+=wrap(e.root.rotation.y-e.visualFacing)*(1-Math.exp(-poseDt*12));e.root.rotation.y=e.visualFacing;
 const wind=e.mode==='windup',charge=e.mode==='charge',recover=e.mode==='recover';
 const progress=wind?1-Math.max(0,Math.min(1,e.timer/(e.windupTotal||1.2))):0;
 e.rig.arms.forEach((a,i)=>{a.rotation.x=wind?-progress*(e.type==='boss'?2.5:1.7):charge?.7:recover?.35:Math.sin(t*3+i)*.08;a.rotation.z=wind?(i?1:-1)*progress*.4:0;});
 e.robe.rotation.x=wind?-.08*progress:charge?.2:recover?.12:0;
 e.root.rotation.x=charge?.12:0;
 if(journey.level===2&&e===boss&&e.mode==='recover'&&localProfile.secret[0]&&!localProfile.secret[1]){e.rig.arms[0].rotation.x=-1.2;e.rig.arms[0].rotation.z=-.6;}
 if(e.rig.mantle){e.rig.mantle.visible=e.type!=='shade'||shadeVulnerable(e);e.rig.eyes.visible=e.rig.mantle.visible;e.rig.mantle.rotation.x=walking*.06+Math.sin(t*1.1)*.018;}
 if(e.flash>0)e.robe.rotation.z=Math.sin(t*65)*.08;else e.robe.rotation.z=0;
}

const classProjectileMaterials={};function classProjectileMaterial(id){return classProjectileMaterials[id]||(classProjectileMaterials[id]=new THREE.MeshBasicMaterial({color:HERO_DEFS[id].color}));}
