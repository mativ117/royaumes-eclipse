'use strict';
let classEffects=[];
function clearClassAbilities(){for(const fx of classEffects){scene.remove(fx.root);for(const m of fx.materials||[])m.dispose();if(fx.collider)obstacles=obstacles.filter(o=>!fx.collider.includes(o));}classEffects=[];}
function classLine(from,to){const n=Math.ceil(distance(from,to)/.3);for(let i=1;i<n;i++)if(blocked(from.x+(to.x-from.x)*i/n,from.z+(to.z-from.z)*i/n,.06,true))return false;return true;}
function abilityTargets(owner){return battle?[p,...localParty].filter(a=>!a.downed&&(a.team||0)!==(owner.team||0)):enemies.filter(e=>!e.dead);}
function abilityDamage(target,n,owner,center=owner){if(battle)battleDamage(target,n,owner);else damage(target,n,{...center,heroId:owner.heroId||hero,owner});}
function classBurst(actor,radius,amount,color,interrupt=true){const owner=actor.owner||actor;effect(actor.x,actor.z,radius,color,.7);for(const e of abilityTargets(owner))if(distance(e,actor)<radius&&classLine(actor,e)){if(interrupt){if(e.mode==='windup'){e.mode='recover';e.timer=2;clearHazards();}if(battle)e.attack=null;}abilityDamage(e,amount,owner,actor);}}
function canPhaseBetween(a,b){const n=Math.ceil(distance(a,b)/.2);for(let i=1;i<=n;i++){const x=a.x+(b.x-a.x)*i/n,z=a.z+(b.z-a.z)*i/n;if(obstacles.some(o=>(o.gate||o.questGate)&&solidActive(o,false)&&collisionContact(o,x,z,.48)))return false;}return true;}
function safeBlink(actor,angle,range){const dx=-Math.sin(angle),dz=-Math.cos(angle);let allowed=range;for(let d=.2;d<=range;d+=.2)if(obstacles.some(o=>(o.gate||o.questGate)&&solidActive(o,false)&&collisionContact(o,actor.x+dx*d,actor.z+dz*d,.48))){allowed=d-.3;break;}for(let d=allowed;d>.1;d-=.2){const x=actor.x+dx*d,z=actor.z+dz*d;if(!blocked(x,z)){actor.x=x;actor.z=z;return;}}}
function abilityRoot(color){const root=new THREE.Group(),material=new THREE.MeshStandardMaterial({color,emissive:color,emissiveIntensity:.5,transparent:true,opacity:.75,roughness:.45});scene.add(root);return {root,materials:[material],material};}
function castClassPower(actor,id=hero,heading=aim){
 const def=HERO_DEFS[id];actor.heroId=id;actor.power=def.power;const color=def.color;
 if(id==='rempart'){actor.shield=3;classBurst(actor,5,55,color);return;}
 if(id==='voltigeur'){actor.leap=.75;actor.inv=.85;return;}
 if(id==='lame'){actor.inv=.75;moveEntity(actor,-Math.sin(heading)*3.4,-Math.cos(heading)*3.4);classBurst(actor,3.3,80,color);actor.stagger=0;return;}
 if(id==='tisseuse'){
  const entrance={x:actor.x,z:actor.z};safeBlink(actor,heading,6);const exit={x:actor.x,z:actor.z},fx=abilityRoot(color);fx.kind='rift';fx.life=fx.max=7;fx.entrance=entrance;fx.exit=exit;fx.last=new WeakMap();fx.last.set(actor,Infinity);
  for(const point of [entrance,exit]){const ring=new THREE.Mesh(ringGeo,fx.material);ring.position.set(point.x,1.2,point.z);ring.scale.set(1,1.4,1);fx.root.add(ring);}classEffects.push(fx);classBurst(actor,2,40,color);return;
 }
 if(id==='cendres'){const heat=actor.heat||0;actor.heat=0;classBurst(actor,4.5,65+heat*.7,color);const fx=abilityRoot(color);fx.kind='burn';fx.x=actor.x;fx.z=actor.z;fx.owner=actor;fx.life=fx.max=5;fx.tick=0;const ring=mesh(discGeo,fx.material,actor.x,.04,actor.z,4.5,4.5,4.5,fx.root);ring.rotation.x=-Math.PI/2;classEffects.push(fx);return;}
 if(id==='voleur'){actor.doubleSwapLock=.7;
  const existing=classEffects.find(f=>f.kind==='double'&&f.owner===actor);if(existing){if(!canPhaseBetween(actor,existing)){actor.power=1;announce('Le seuil scellé coupe le lien avec le double.');return;}const x=actor.x,z=actor.z;actor.x=existing.x;actor.z=existing.z;existing.x=x;existing.z=z;existing.root.position.set(x,0,z);actor.power=4;effect(x,z,2,color);return;}
  const fx=abilityRoot(color);fx.kind='double';fx.owner=actor;fx.life=fx.max=8;fx.x=actor.x;fx.z=actor.z;fx.tick=0;fx.root.position.set(actor.x,0,actor.z);mesh(coneGeo,fx.material,0,1,0,.65,1,.65,fx.root);mesh(sphereGeo,fx.material,0,1.9,0,.24,.24,.24,fx.root);classEffects.push(fx);return;
 }
 if(id==='bergere'||id==='neant'||id==='eclipse'){
  const fx=abilityRoot(color);fx.kind=id;fx.owner=actor;fx.life=fx.max=id==='eclipse'?6:8;fx.tick=0;const orb=mesh(sphereGeo,fx.material,0,1.6,0,id==='eclipse'?1:.35,id==='eclipse'?1:.35,id==='eclipse'?1:.35,fx.root);fx.orb=orb;
  if(id==='eclipse'){fx.x=actor.x-Math.sin(heading)*3;fx.z=actor.z-Math.cos(heading)*3;fx.material.color.set('#080811');fx.material.emissive.set('#6c4c21');fx.root.position.set(fx.x,0,fx.z);effect(fx.x,fx.z,7,color,1);}
  if(id==='neant'){actor.formT=8;actor.inv=Math.max(actor.inv||0,.5);fx.material.color.set('#131829');fx.material.emissive.set('#2b3966');mesh(coneGeo,fx.material,0,.85,0,.5,.65,.5,fx.root);}
  classEffects.push(fx);return;
 }
 if(id==='colosse'){
  classBurst(actor,5,100,color);const fx=abilityRoot(color);fx.material.opacity=1;fx.kind='cover';fx.life=fx.max=7;fx.collider=[];const forward={x:-Math.sin(heading),z:-Math.cos(heading)},right={x:Math.cos(heading),z:-Math.sin(heading)};
  for(const side of [-1,0,1]){const x=actor.x+forward.x*2.4+right.x*side*1.05,z=actor.z+forward.z*2.4+right.z*side*1.05;if(!world.onGround(x,z,.5)||blocked(x,z,.5))continue;const root=new THREE.Group();root.position.set(x,0,z);fx.root.add(root);mesh(boxGeo,fx.material,0,.8,0,.9,1.6,.9,root).castShadow=true;const o={x,z,w:.9,d:.9,root};obstacles.push(o);fx.collider.push(o);}classEffects.push(fx);return;
 }
 if(id==='accordeur'){const fx=abilityRoot(color);fx.kind='rhythm';fx.owner=actor;fx.life=fx.max=2;fx.tick=0;fx.pulses=0;classEffects.push(fx);}
}
function updateClassAbilities(dt){
 for(const actor of [p,...(typeof localParty==='undefined'?[]:localParty)]){
  if(actor.heat>0&&!actor.attack)actor.heat=Math.max(0,actor.heat-dt*7);const previousIncarnation=actor.incarnateT||0;for(const key of ['formT','incarnateT','fragileT','wardT','doubleSwapLock'])actor[key]=Math.max(0,(actor[key]||0)-dt);if(previousIncarnation>0&&!actor.incarnateT)actor.fragileT=4;
 }
 for(const fx of classEffects){fx.life-=dt;fx.tick=(fx.tick||0)-dt;
  if(fx.kind==='incarnation'){fx.root.position.set(fx.owner.x,0,fx.owner.z);fx.root.rotation.y=t*.8;}else if(fx.kind==='rift'){
   for(const actor of [p,...enemies.filter(e=>!e.dead&&!e.partyOwner),...(typeof localParty==='undefined'?[]:localParty)]){const from=distance(actor,fx.entrance)<.8?fx.entrance:distance(actor,fx.exit)<.8?fx.exit:null;if(!from){if(distance(actor,fx.entrance)>1.4&&distance(actor,fx.exit)>1.4)fx.last.delete(actor);continue;}if(fx.last.has(actor)||!canPhaseBetween(fx.entrance,fx.exit))continue;if(from){const to=from===fx.entrance?fx.exit:fx.entrance;if(!blocked(to.x,to.z+.9)){actor.x=to.x;actor.z=to.z+.9;fx.last.set(actor,Infinity);}}}
   for(const b of bullets)if(!b.riftUsed){const near=Math.hypot(b.x-fx.entrance.x,b.z-fx.entrance.z)<1?fx.entrance:Math.hypot(b.x-fx.exit.x,b.z-fx.exit.z)<1?fx.exit:null;if(near&&canPhaseBetween(fx.entrance,fx.exit)){const to=near===fx.entrance?fx.exit:fx.entrance;b.x=to.x;b.z=to.z;b.riftUsed=true;}}
  }else if(fx.kind==='double'){
   const attack=fx.owner===p?p.attack:fx.owner.attack;if(attack&&attack!==fx.lastAttack){fx.lastAttack=attack;fx.echoAt=t+.2;fx.heading=attack.aim??fx.owner.aim??aim;}if(fx.echoAt&&t>=fx.echoAt){fx.echoAt=0;classBurst(fx,3,38,HERO_DEFS.voleur.color,false);}
   fx.root.rotation.y=fx.heading||0;
  }else if(fx.kind==='rhythm'&&fx.tick<=0&&fx.pulses<3){fx.tick=.6;fx.pulses++;fx.lastPulse=t;classBurst(fx.owner,5+fx.pulses*.7,26,HERO_DEFS.accordeur.color);tone(280+fx.pulses*120,.12);}
  else if(['burn','bergere','neant','eclipse'].includes(fx.kind)){
   const owner=fx.owner;if(fx.kind==='bergere'){fx.root.position.set(owner.x+Math.sin(t*1.5)*1.7,0,owner.z+Math.cos(t*1.5)*1.7);for(const ally of [p,...localParty])if((ally.team||0)===(owner.team||0)&&distance(ally,owner)<4)ally.wardT=.2;}
   if(fx.kind==='neant'){const target=abilityTargets(owner).filter(e=>battle||trialActive(e)).sort((a,b)=>distance(a,owner)-distance(b,owner))[0];if(target){fx.root.position.lerp(new THREE.Vector3(target.x,0,target.z),1-Math.exp(-dt*5));fx.x=fx.root.position.x;fx.z=fx.root.position.z;}}
   if(fx.tick<=0){fx.tick=.65;const center=fx.kind==='burn'||fx.kind==='eclipse'?fx:fx.kind==='neant'?{x:fx.root.position.x,z:fx.root.position.z}:owner;
    if(fx.kind==='bergere')owner.hp=Math.min(owner.max,owner.hp+4);
    for(const e of abilityTargets(owner))if(distance(e,center)<(fx.kind==='eclipse'?7:fx.kind==='burn'?4.5:fx.kind==='neant'?2.7:4)){if(['bergere','eclipse'].includes(fx.kind)){const d=Math.max(.1,distance(e,center));if(!['boss','porter'].includes(e.type))moveEntity(e,(center.x-e.x)/d*.6,(center.z-e.z)/d*.6,.55);}abilityDamage(e,fx.kind==='neant'?24:fx.kind==='burn'?12:18,owner,center);}
   }
  }
  fx.root.traverse(o=>{if(o.isMesh&&o.geometry===sphereGeo)o.rotation.y+=dt;});if(fx.life<1)fx.material.opacity=Math.max(0,fx.life)*.7;
 }
 const expired=classEffects.filter(f=>f.life<=0);for(const fx of expired){scene.remove(fx.root);for(const m of fx.materials)m.dispose();if(fx.collider)obstacles=obstacles.filter(o=>!fx.collider.includes(o));}classEffects=classEffects.filter(f=>f.life>0);
}
function castIncarnation(actor,id){if(state!=='playing'||battle?.crownOwner===actor||id!=='eclipse'||(actor.incarnation||0)<100||actor.incarnateT>0)return;actor.incarnation=0;actor.incarnateT=8;actor.fragileT=0;actor.hp=Math.min(actor.max,actor.hp+30);classBurst(actor,7,80,'#ffdb85');const fx=abilityRoot('#f7ce7c');fx.kind='incarnation';fx.owner=actor;fx.life=fx.max=8;for(let i=0;i<3;i++){const ring=mesh(ringGeo,fx.material,0,1.1+i*.5,0,1.1+i*.18,1.1+i*.18,1.1+i*.18,fx.root);ring.rotation.x=i===1?Math.PI/2:.3;}classEffects.push(fx);announce('Incarnation · huit secondes, puis quatre secondes de fragilité.');}
function activateIncarnation(){castIncarnation(p,hero);}
