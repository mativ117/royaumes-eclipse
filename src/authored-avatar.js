'use strict';
const avatarRuntime={status:'loading',heroes:{},current:null,lastAttack:null,lastWorldUse:null,error:null};
async function loadAuthoredHeroes(){
 $('#start').disabled=true;$('#start').textContent='Préparation de l’expédition…';
 try{
  for(const name of ['rempart','voltigeur']){
   const bytes=Uint8Array.from(atob(ROYAUMES_CHARACTER_DATA[name]),c=>c.charCodeAt(0));
   const gltf=await new Promise((resolve,reject)=>new RoyaumesGLTFLoader().parse(bytes.buffer,'',resolve,reject));
   const root=gltf.scene;root.scale.setScalar(1.07);root.rotation.y=Math.PI;root.position.y=0;root.visible=false;
   const mixer=new THREE.AnimationMixer(root),actions={};for(const clip of gltf.animations)actions[clip.name]=mixer.clipAction(clip);
   root.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false;}});
   player.root.add(root);avatarRuntime.heroes[name]={root,mixer,actions,state:'',action:null,muzzle:root.getObjectByName('muzzle'),blade:root.getObjectByName('blade_tip'),hand:root.getObjectByName('handR')||root.getObjectByName('hand.R'),weapon:root.getObjectByName(name+'_Weapon'),lastAttack:null,lastUse:null};
  }
  avatarRuntime.status='ready';syncAvatarSelection();
 }catch(e){avatarRuntime.status='error';avatarRuntime.error=String(e);$('#intro').textContent='Le modèle du héros ne s’est pas chargé. Rechargez la page pour retrouver la version complète.';console.error('Authored avatar:',e);}
 $('#start').disabled=avatarRuntime.status!=='ready';$('#start').textContent=avatarRuntime.status==='ready'?'Entrer dans la cathédrale →':'Recharger le jeu';
}
function syncAvatarSelection(){
 if(avatarRuntime.status!=='ready')return;
 for(const [name,avatar]of Object.entries(avatarRuntime.heroes))avatar.root.visible=name===hero;
 avatarRuntime.current=avatarRuntime.heroes[hero];
 for(const object of player.legacyParts)object.visible=false;
 if(avatarRuntime.current.muzzle){avatarRuntime.current.muzzle.add(muzzle);muzzle.position.set(0,0,0);muzzle.scale.set(.12,.12,.22);}
 playAvatarAction(avatarRuntime.current,'idle',.12,true);
}
function playAvatarAction(avatar,name,fade=.13,restart=false,duration=null){
 const action=avatar.actions[name]||avatar.actions.idle;if(avatar.action===action&&!restart)return;
 const previous=avatar.action;action.reset().setEffectiveWeight(1).setEffectiveTimeScale(1);
 if(duration)action.setEffectiveTimeScale(action.getClip().duration/duration);
 if(['attack1','attack2','attack3','shot','dash','leap','interact','hit'].includes(name)){action.setLoop(THREE.LoopOnce,1);action.clampWhenFinished=true;}else{action.setLoop(THREE.LoopRepeat,Infinity);action.clampWhenFinished=false;}
 action.play();if(previous&&previous!==action){previous.fadeOut(fade);action.fadeIn(fade);}avatar.action=action;avatar.state=name;
}
function updateRigAvatar(dt){
 if(avatarRuntime.status!=='ready'||!p)return;const avatar=avatarRuntime.current;
 for(const object of player.legacyParts)object.visible=false;
 if(avatar.weapon)avatar.weapon.visible=!campaign?.trials.forge.carrying;
 const speed=p.motionSpeed??Math.hypot(p.vx,p.vz);
 if(p.stagger>0){playAvatarAction(avatar,'hit',.035,false,.2);}
 else if(p.attack){const name=p.attack.melee?'attack'+p.attack.combo:'shot';if(avatar.lastAttack!==p.attack){playAvatarAction(avatar,name,.055,true,p.attack.duration);avatar.lastAttack=p.attack;}}
 else if(p.leap>0){playAvatarAction(avatar,'leap',.06,false,.75);}
 else if(p.dashT>0){playAvatarAction(avatar,'dash',.045,false,.2);}
 else if(p.shield>0){playAvatarAction(avatar,'shield',.15);}
 else if(campaign?.trials.forge.carrying){playAvatarAction(avatar,'carry',.15);}
 else if(campaign?.worldUse&&t-campaign.worldUse.started<.55){if(avatar.lastUse!==campaign.worldUse){playAvatarAction(avatar,'interact',.1,true,.55);avatar.lastUse=campaign.worldUse;}}
 else{const gait=speed>3?'run':speed>.2?'walk':'idle';playAvatarAction(avatar,gait,.16);if(gait!=='idle')avatar.action.setEffectiveTimeScale(Math.max(.6,speed/(gait==='run'?5:2.4)));}
 avatar.mixer.update(dt);updateBladeTrail(avatar,dt);
}

const bladeTrail={samples:[],mesh:null,lastTime:-1};
function updateBladeTrail(avatar,dt){
 if(!bladeTrail.mesh){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(new Float32Array(7*18),3));geometry.setAttribute('color',new THREE.BufferAttribute(new Float32Array(7*18),3));geometry.setDrawRange(0,0);bladeTrail.mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide,transparent:true,opacity:.5,depthWrite:false}));bladeTrail.mesh.frustumCulled=false;scene.add(bladeTrail.mesh);}
 slash.visible=false;
 const active=hero==='voltigeur'&&p.attack?.melee&&p.attack.elapsed>=p.attack.hitAt*.65&&p.attack.elapsed<p.attack.duration*.9;
 if(active&&avatar.blade&&avatar.hand){avatar.root.updateMatrixWorld(true);bladeTrail.samples.push({base:avatar.hand.getWorldPosition(new THREE.Vector3()),tip:avatar.blade.getWorldPosition(new THREE.Vector3()),time:t});}
 bladeTrail.samples=bladeTrail.samples.filter(s=>t>=s.time&&t-s.time<.13).slice(-8);const samples=bladeTrail.samples,g=bladeTrail.mesh.geometry;let count=0;
 for(let i=1;i<samples.length;i++){const a=samples[i-1],b=samples[i];for(const v of [a.base,a.tip,b.tip,a.base,b.tip,b.base]){g.attributes.position.setXYZ(count,v.x,v.y,v.z);const f=i/samples.length;g.attributes.color.setXYZ(count,.8*f,.48*f,.16*f);count++;}}
 g.setDrawRange(0,count);g.attributes.position.needsUpdate=true;g.attributes.color.needsUpdate=true;bladeTrail.mesh.visible=count>0;
}

function resetAvatarPose(){
 if(avatarRuntime.current){avatarRuntime.current.lastAttack=null;avatarRuntime.current.lastUse=null;playAvatarAction(avatarRuntime.current,'idle',.05,true);avatarRuntime.current.mixer.update(0);}
 bladeTrail.samples=[];if(bladeTrail.mesh)bladeTrail.mesh.visible=false;
}
