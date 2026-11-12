'use strict';
const $=s=>document.querySelector(s),canvas=$('#world');let renderer;
try{renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'})}catch(e){$('#intro').textContent='La 3D est indisponible dans ce navigateur. Active WebGL ou essaie Safari / Chrome à jour.';$('#start').disabled=true;throw e}
renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;
const scene=new THREE.Scene();scene.background=new THREE.Color('#140f19');scene.fog=new THREE.FogExp2('#241722',.018);
const camera=new THREE.PerspectiveCamera(49,innerWidth/innerHeight,.1,180);camera.position.set(0,25,30);camera.lookAt(0,0,-4);
scene.add(new THREE.AmbientLight('#c0a397',1.45));scene.add(new THREE.HemisphereLight('#b5c7df','#4f2920',2));const sun=new THREE.DirectionalLight('#ffba76',3.6);sun.position.set(-10,24,10);scene.add(sun);const blueLight=new THREE.DirectionalLight('#609ed6',1.7);blueLight.position.set(15,8,-10);scene.add(blueLight);
const mat=(color,metalness=.1,roughness=.6,emission)=>new THREE.MeshStandardMaterial({color,metalness,roughness,emissive:emission||'#000000',emissiveIntensity:emission?2:0});
const stone=mat('#302933',.25),dark=mat('#11121b',.4),bronze=mat('#88634a',.6),gold=mat('#ffbd69',.5,.3,'#d86616'),armor=mat('#627e70',.65,.3),joint=mat('#20262d'),red=mat('#e65a47',.2,.3,'#9d2218'),cyan=mat('#9eefff',.3,.2,'#219bd9');
const boxGeo=new THREE.BoxGeometry(1,1,1),sphereGeo=new THREE.SphereGeometry(1,12,8),cylGeo=new THREE.CylinderGeometry(1,1,1,12);
function mesh(geo,m,x,y,z,sx=1,sy=1,sz=1,parent=scene){const o=new THREE.Mesh(geo,m);o.position.set(x,y,z);o.scale.set(sx,sy,sz);parent.add(o);return o}
function box(m,x,y,z,sx,sy,sz,parent){return mesh(boxGeo,m,x,y,z,sx,sy,sz,parent)}
const world=buildCampaign(THREE,scene,renderer,{stone,bronze,gold,dark});const art=world.art,floor=world.floor,portal=world.exit,dust=world.dust,halo=world.halo;
const ember=mat('#ad4935',.2,.65),cloth=mat('#342d45',.05,.9),bladeMaterial=mat('#ffd09a',.5,.25,'#f47320');
let hero='rempart';
const HEROES={
 rempart:{name:'Le Dernier Rempart',hp:150,speed:6,dash:1.8,power:9,powerName:'Bouclier'},
 voltigeur:{name:'Le Voltigeur',hp:110,speed:7.4,dash:1.15,power:7,powerName:'Bond'}
};
function soldier(){
 const root=new THREE.Group();scene.add(root);
 const body=mesh(new THREE.CylinderGeometry(.53,.38,1,6),armor,0,1.35,0,.95,1,.68,root);
 const helmet=mesh(sphereGeo,armor,0,2.12,0,.42,.42,.4,root);
 box(gold,0,2.15,-.36,.61,.17,.12,root);
 const heavy=new THREE.Group();root.add(heavy);
 box(joint,0,.88,0,.75,.22,.58,root);box(bronze,0,.89,-.32,.3,.19,.08,root);
 for(const x of [-.27,.27]){box(bronze,x,.47,-.23,.29,.25,.09,root);box(joint,x,.11,-.12,.42,.22,.66,root)}
 for(const x of [-.7,.7]){const pad=mesh(cylGeo,armor,x,1.65,0,.33,.35,.4,heavy);pad.rotation.x=Math.PI/2;box(gold,x,1.63,-.38,.2,.06,.035,heavy)}
 box(armor,0,1.3,.4,.6,.85,.3,heavy);box(cyan,0,1.35,.57,.09,.5,.03,heavy);
 box(bronze,0,1.4,-.3,.65,.55,.12,heavy);
 for(const x of [-.67,.67]){box(armor,x,1.65,0,.4,.45,.55,heavy);box(joint,x,1.15,0,.25,.6,.3,root)}
 const rifle=new THREE.Group();box(joint,0,0,-.25,.28,.3,1.35,rifle);box(cyan,0,0,-.95,.14,.14,.12,rifle);
 const light=new THREE.Group();root.add(light);
 const cape=new THREE.Mesh(new THREE.PlaneGeometry(1.1,1.25),new THREE.MeshStandardMaterial({color:'#682f35',side:THREE.DoubleSide,roughness:1}));cape.position.set(0,1.1,.4);cape.rotation.x=.12;light.add(cape);
 for(const x of [-.33,.33])box(bronze,x,1.35,-.3,.08,.7,.05,light);
 box(ember,0,1.87,0,1,.18,.72,light);
 const scarf=box(ember,.25,1.6,.65,.36,.85,.06,light);scarf.rotation.x=-.45;
 const sword=new THREE.Group();sword.position.set(.58,1.2,-.3);light.add(sword);
 box(joint,0,0,0,.13,.32,.13,sword);box(bronze,0,.19,0,.42,.09,.15,sword);
 const edge=box(bladeMaterial,0,.85,0,.1,1.25,.1,sword);edge.rotation.z=-.08;
 const arms=[];for(const side of [-1,1]){const arm=new THREE.Group();arm.position.set(side*.6,1.55,0);root.add(arm);mesh(new THREE.CapsuleGeometry(.14,.46,3,7),joint,0,-.35,0,1,1,1,arm);arms.push(arm);}
 const legs=[box(armor,-.25,.5,0,.35,.9,.4,root),box(armor,.25,.5,0,.35,.9,.4,root)];
 arms[1].add(sword,rifle);sword.position.set(0,-.65,0);rifle.position.set(0,-.6,0);rifle.rotation.x=-1.2;return{root,legs,body,helmet,heavy,light,sword,scarf,cape,arms,rifle};
}
function applyHero(){
 const light=hero==='voltigeur';player.heavy.visible=!light;player.light.visible=light;player.sword.visible=light;player.rifle.visible=!light;
 player.body.material=light?cloth:armor;player.helmet.material=light?cloth:armor;
 player.legs.forEach(l=>l.material=light?cloth:armor);player.root.scale.setScalar(light?.92:1);
 $('#heroIdentity').textContent=HEROES[hero].name;
 document.querySelectorAll('[data-hero]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.hero===hero)));
}
function dodgeCooldown(){return boon==='haste'?Math.max(.8,HEROES[hero].dash*.583333):HEROES[hero].dash+(boon==='vigor'?.6:0)}
const player=soldier();const shield=new THREE.Mesh(new THREE.SphereGeometry(1.65,24,16),new THREE.MeshBasicMaterial({color:'#79daff',transparent:true,opacity:.17,wireframe:true}));shield.position.y=1.3;player.root.add(shield);shield.visible=false;
const carriedCore=mesh(sphereGeo,gold,0,1.2,-.8,.35,.35,.35,player.root);carriedCore.visible=false;
const reticle=new THREE.Mesh(new THREE.RingGeometry(.26,.34,24),new THREE.MeshBasicMaterial({color:'#ffe1a3',side:THREE.DoubleSide}));reticle.rotation.x=-Math.PI/2;reticle.position.y=.05;scene.add(reticle);

// Simulation at a fixed timestep; rendering remains independent of display refresh.
let state='menu',p,enemies=[],bullets=[],effects=[],hazards=[],obstacles=[],roomMeshes=[],shrines=[],t=0,kills=0,last=0,accumulator=0,noticeUntil=0,aim=0,targetAim=0,shotCount=0,quality='standard',room=0,boon='',shard=false,boss=null,walkPhase=0,trailTimer=0;
let bell=null;
let decoy=null,secretMirror=null,secretFound=false,observing=false,observeTime=0,pendingPact='',interactId=null,secretNewThisRun=false;
const SECRET_KEY='royaumes-eclipse-reflet-v1';
try{secretFound=localStorage.getItem(SECRET_KEY)==='found'}catch(_){}
const keys=new Set(),joy={x:0,y:0};let shooting=false,mouseDown=false,stickId=null,mouseAim=false,fireId=null;
const pointer=new THREE.Vector2(),ray=new THREE.Raycaster(),ground=new THREE.Plane(new THREE.Vector3(0,1,0),0),aimPoint=new THREE.Vector3();
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),distance=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z),coarse=()=>matchMedia('(pointer:coarse)').matches;
const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a));
const cameraTarget=new THREE.Vector3(),cameraLook=new THREE.Vector3(0,0,-4),camDesired=new THREE.Vector3();
const ringGeo=new THREE.RingGeometry(.84,1,40),discGeo=new THREE.CircleGeometry(1,40),coneGeo=new THREE.ConeGeometry(.72,1.8,8),enemyRobeGeo=new THREE.CylinderGeometry(.34,.75,1.8,8);
const enemyArmor=mat('#62505c',.45),floorRoute=mat('#493844',.2),runeGold=mat('#c99a65',.5,.4,'#593319');
const muzzle=mesh(sphereGeo,gold,.5,1.35,-1.65,.32,.25,.4,player.root);player.rifle.add(muzzle);muzzle.position.set(0,0,-1.05);muzzle.visible=false;
const slashMaterial=new THREE.MeshBasicMaterial({color:'#ffcb83',side:THREE.DoubleSide,transparent:true,opacity:.8,depthWrite:false});
const slash=new THREE.Mesh(new THREE.RingGeometry(.7,1,36,1,Math.PI/2-1.15,2.3),slashMaterial);slash.rotation.x=-Math.PI/2;slash.position.y=1.15;slash.scale.setScalar(3.3);player.root.add(slash);slash.visible=false;
const landingMarker=new THREE.Mesh(new THREE.RingGeometry(.94,1,48),new THREE.MeshBasicMaterial({color:'#ffb763',side:THREE.DoubleSide,transparent:true,opacity:.65,depthWrite:false}));landingMarker.rotation.x=-Math.PI/2;landingMarker.position.y=.08;landingMarker.scale.setScalar(4.6);scene.add(landingMarker);landingMarker.visible=false;
const heroShadow=new THREE.Mesh(new THREE.CircleGeometry(.95,24),new THREE.MeshBasicMaterial({color:'#05040a',transparent:true,opacity:.55,depthWrite:false}));heroShadow.rotation.x=-Math.PI/2;heroShadow.position.y=.04;scene.add(heroShadow);
let audio=null,soundOn=true;
function tone(freq,dur=.06,type='sine',volume=.025){if(!soundOn||!audio||audio.state!=='running')return;const o=audio.createOscillator(),gain=audio.createGain();o.type=type;o.frequency.setValueAtTime(freq,audio.currentTime);o.frequency.exponentialRampToValueAtTime(Math.max(35,freq*.5),audio.currentTime+dur);gain.gain.setValueAtTime(volume,audio.currentTime);gain.gain.exponentialRampToValueAtTime(.001,audio.currentTime+dur);o.connect(gain);gain.connect(audio.destination);o.start();o.stop(audio.currentTime+dur)}
function unlockAudio(){try{if(!audio)audio=new(window.AudioContext||window.webkitAudioContext)();audio.resume().catch(()=>{})}catch(_){soundOn=false}}
$('#sound').onclick=()=>{soundOn=!soundOn;$('#sound').textContent=soundOn?'Son : oui':'Son : non';$('#sound').setAttribute('aria-pressed',String(soundOn));if(soundOn)unlockAudio()};
function announce(s){$('#notice').textContent=s;$('#notice').hidden=false;noticeUntil=performance.now()+6000}
function clearInputs(){
 observing=false;interactId=null;
 keys.clear();joy.x=joy.y=0;shooting=mouseDown=false;
 const oldStick=stickId,oldFire=fireId;stickId=fireId=null;
 for(const [el,id] of [[$('#stick'),oldStick],[$('#fire'),oldFire]]){
  try{if(id!==null&&el.hasPointerCapture(id))el.releasePointerCapture(id)}catch(_){}
 }
 $('#knob').style.transform='';if(p)p.vx=p.vz=0;
}
function releaseMenuFocus(){
 // A hidden menu button must not receive the gameplay Space key as a click.
 const el=document.activeElement;if(el&&el!==document.body&&typeof el.blur==='function')el.blur();
}
function cleanupObject(o){scene.remove(o);o.traverse(child=>{if(child.userData.labelTexture){child.userData.labelTexture.dispose();child.material.dispose()}if(child.userData.ownedMaterial)child.material.dispose();if(child.userData.ownedGeometry)child.geometry.dispose()})}
function clearFX(){effects.forEach(e=>{scene.remove(e.mesh);e.mesh.material.dispose()});effects=[];hazards.forEach(e=>{scene.remove(e.mesh);e.mesh.material.dispose()});hazards=[]}
function clearRoom(){bell=null;clearDecoy();secretMirror=null;observeTime=0;observing=false;enemies.forEach(e=>cleanupObject(e.root));enemies=[];bullets.forEach(b=>scene.remove(b.mesh));bullets=[];clearFX();roomMeshes.forEach(o=>cleanupObject(o));roomMeshes=[];obstacles=[];shrines=[];boss=null}
function roomObject(o){roomMeshes.push(o);return o}
function label(text,x,z,color='#ffd496',width=6){const c=document.createElement('canvas');c.width=512;c.height=96;const ctx=c.getContext('2d');ctx.fillStyle='#100d19d9';ctx.fillRect(0,0,512,96);ctx.font='bold 30px system-ui';ctx.textAlign='center';ctx.fillStyle=color;ctx.fillText(text,256,60,480);const texture=new THREE.CanvasTexture(c),material=new THREE.SpriteMaterial({map:texture,depthTest:false});const sprite=new THREE.Sprite(material);sprite.position.set(x,3.6,z);sprite.scale.set(width,width*96/512,1);scene.add(sprite);sprite.userData.labelTexture=texture;roomObject(sprite);return sprite}
function obstacle(x,z,w,d,height=2.4){const o=box(stone,x,height/2,z,w,height,d);roomObject(o);box(bronze,0,0,0,1.015,.035,1.015,o);obstacles.push({x,z,w,d});return o}
function blocked(x,z,r=.48,projectile=false){
 if(!projectile&&!world.onGround(x,z,r))return true;
 if(x<-70||x>70||z<-120||z>38)return true;
 return obstacles.some(o=>(!o.gate||campaignGateClosed(o.gate))&&Math.abs(x-o.x)<o.w/2+r&&Math.abs(z-o.z)<o.d/2+r);
}
function moveEntity(e,dx,dz,r=.48){
 const steps=Math.max(1,Math.ceil(Math.hypot(dx,dz)/.22));
 for(let i=0;i<steps;i++){if(!blocked(e.x+dx/steps,e.z,r))e.x+=dx/steps;if(!blocked(e.x,e.z+dz/steps,r))e.z+=dz/steps;}
}
function makeShrine(x,z,color,name){const group=new THREE.Group();group.position.set(x,0,z);scene.add(group);roomObject(group);box(bronze,0,.45,0,1.8,.9,1.8,group);const crystal=mesh(new THREE.OctahedronGeometry(.65),mat(color,.4,.25,color),0,1.8,0,1,1,1,group);crystal.userData.ownedMaterial=true;crystal.userData.ownedGeometry=true;const glow=mesh(ringGeo,new THREE.MeshBasicMaterial({color,side:THREE.DoubleSide,transparent:true,opacity:.7}),0,.05,0,2,2,2,group);glow.rotation.x=-Math.PI/2;glow.userData.ownedMaterial=true;const tag=label(name,x,z, color);return{root:group,crystal,x,z,tag}}
function start(){unlockAudio();applyHero();p={x:0,z:12,vx:0,vz:0,hp:HEROES[hero].hp,max:HEROES[hero].hp,shot:0,dash:0,dashT:0,dx:0,dz:-1,power:0,shield:0,inv:0,recoil:0,overcharge:0,absorbLock:0,leap:0,swing:0,combo:0,comboWindow:0};kills=shotCount=walkPhase=0;secretNewThisRun=false;boon='';clearInputs();beginCampaign();state='playing';$('#menu').hidden=true;$('#pausePanel').hidden=true;$('#hud').hidden=false;$('#controls').hidden=false;$('#mobile').classList.add('playing');accumulator=0;last=performance.now();updateHUD()}
let pauseReason='',pactConfirmTimer=null;
function pause(reason='manual'){
 if(state!=='playing')return;
 pauseReason=reason;state='paused';clearInputs();$('#pausePanel').hidden=false;
 $('#resume').hidden=false;$('#resume').textContent='Reprendre';
 $('#endTag').textContent='Version 0.9 · Pause';$('#endTitle').textContent='En pause';
 $('#endText').textContent=reason==='hidden'?'La page a été masquée. Votre progression dans cette tentative est conservée.':reason==='graphics'?'Le rendu 3D a été interrompu. Rechargez la page et choisissez la qualité légère.':'Votre pacte et la progression de cette tentative sont conservés.';
 $('#mobile').classList.remove('playing');
}
function finish(won){if(!won)campaign.deaths=(campaign.deaths||0)+1;else try{localStorage.removeItem(RUN_KEY)}catch(_){}$('#copyReport').hidden=false;$('#copyReport').textContent='Copier le bilan';state=won?'won':'lost';clearInputs();$('#pausePanel').hidden=false;$('#resume').hidden=won;$('#resume').textContent='Réessayer cette salle';$('#endTag').textContent=won?'Premier chapitre terminé':'La cathédrale se souvient';$('#endTitle').textContent=won?'Le Veilleur s’incline.':'Votre héros est tombé.';$('#endText').textContent=won?`Les Marches traversées · ${kills} adversaires vaincus · Durée active ${Math.floor((campaign.activeSeconds||campaign.time)/60)} min ${Math.floor((campaign.activeSeconds||campaign.time)%60)} s · ${campaign.deaths||0} défaite(s) · Serment ${boon==='vigor'?'de Braise':'d’Élan'} · ${secretFound?'Marque du Reflet trouvée':'Un secret reste à découvrir'}. Expédition terminée. Le bilan permet de mesurer la durée réelle et d’affiner l’équilibrage.`:'Observez les préparations rouges, utilisez les abris et gardez votre bouclier pour les moments difficiles. Vous pouvez reprendre au dernier refuge atteint, avec votre serment.';$('#mobile').classList.remove('playing');tone(won?660:100,.4)}
function resume(){
 if(document.hidden)return;
 if(state==='lost'){
  restoreCampaign();
 }else if(state!=='paused')return;
 state='playing';pauseReason='';$('#pausePanel').hidden=true;
 $('#mobile').classList.add('playing');releaseMenuFocus();last=performance.now();accumulator=0;
}
$('#start').onclick=()=>{start();releaseMenuFocus()};
$('#pause').onclick=()=>pause('manual');
$('#resume').onclick=resume;
$('#back').onclick=()=>{state='menu';clearInputs();$('#menu').hidden=false;$('#pausePanel').hidden=true;$('#hud').hidden=true;$('#controls').hidden=true;$('#mobile').classList.remove('playing');$('#notice').hidden=true;$('#bossHUD').hidden=true};
document.querySelectorAll('[data-hero]').forEach(b=>b.onclick=()=>{if(state==='menu'){hero=b.dataset.hero;applyHero()}});
applyHero();
$('#quality').onchange=e=>{quality=e.target.value;renderer.setPixelRatio(quality==='light'?1:Math.min(devicePixelRatio||1,1.5));renderer.setSize(innerWidth,innerHeight);dust.visible=quality!=='light';art.setQuality(quality==='light')};
function effect(x,z,r,color,duration=.45){const o=new THREE.Mesh(ringGeo,new THREE.MeshBasicMaterial({color,transparent:true,opacity:.8,side:THREE.DoubleSide,depthWrite:false}));o.rotation.x=-Math.PI/2;o.position.set(x,.09,z);scene.add(o);effects.push({mesh:o,r,t:duration,max:duration})}
function addHazard(x,z,r,delay,damageAmount=26,color='#ff6049'){const o=new THREE.Mesh(discGeo,new THREE.MeshBasicMaterial({color,transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false}));o.rotation.x=-Math.PI/2;o.position.set(x,.07,z);o.scale.setScalar(r);scene.add(o);const h={mesh:o,x,z,r,delay,max:delay,damage:damageAmount,fired:false,tail:.3};hazards.push(h);return h}
function clearHazards(){hazards.forEach(e=>{scene.remove(e.mesh);e.mesh.material.dispose()});hazards=[]}
function damage(e,n,source=p){if(e.dead||!trialActive(e))return;if(e.type==='shade'&&!shadeVulnerable(e)){effect(e.x,e.z,1.3,'#c6a3ff',.2);return;}if(e.type==='porter'&&enemies.some(q=>q.type==='anchor'&&!q.dead)){effect(e.x,e.z,2,'#a8cdff');return;}if(e.type==='boss'&&!campaign.bossAwake){effect(e.x,e.z,2.5,'#a3b7ff',.2);return;}
 if(e.type==='sentinel'&&e.mode!=='recover'&&source){
  const dx=source.x-e.x,dz=source.z-e.z,d=Math.max(.01,Math.hypot(dx,dz));
  if((dx*-Math.sin(e.facing)+dz*-Math.cos(e.facing))/d>.35){
   n*=.15;effect(e.x,e.z,1.3,'#bba2ff',.2);
   if(e.blockHint<=0){announce('La Sentinelle bloque de face. Contournez-la ou attendez sa charge.');e.blockHint=6;}
  }
 }
if(['boss','porter'].includes(e.type)&&e.mode!=='recover')n*=.25;e.hp-=n;e.flash=.12;if(e.type!=='boss')e.alert=10;tone(e.type==='boss'?150:260,.04,'triangle',.012);if(e.hp<=0){e.dead=true;kills++;if(e.id)campaign.defeated.add(e.id);effect(e.x,e.z,e.type==='boss'?5:2,'#ffc17b');cleanupObject(e.root);if(e.type==='boss'){clearHazards();bullets.filter(b=>b.enemy).forEach(b=>scene.remove(b.mesh));bullets=bullets.filter(b=>!b.enemy);portal.visible=true;announce('Le Veilleur est vaincu. La porte du fond est ouverte.')}else if(kills%2===0)p.hp=Math.min(p.max,p.hp+8)}}
function fire(){beginAttack()}
function dash(){if(state!=='playing'||p.dash>0)return;cancelAttack();if(campaign.trials.forge.carrying)dropCore();const v=movement(),n=Math.hypot(v.x,v.z);p.dx=n?v.x/n:-Math.sin(aim);p.dz=n?v.z/n:-Math.cos(aim);p.dash=dodgeCooldown();if(boon==='haste')createDecoy();p.dashT=.2;p.inv=.28;effect(p.x,p.z,1.5,'#c4abff');tone(200,.1,'sine')}
function power(){if(state!=='playing'||p.power>0)return;cancelAttack();revealShades();if(hero==='voltigeur'&&campaign.trials.forge.carrying)dropCore();if(hero==='voltigeur'){p.power=7;p.leap=.75;p.inv=.85;p.swing=0;observeTime=0;effect(p.x,p.z,2,'#ffb964');tone(240,.2);return;}p.power=9;p.shield=3;effect(p.x,p.z,5,'#76dcff',.7);tone(110,.3,'sine');for(const e of enemies)if(!e.dead&&distance(e,p)<5){if(['boss','porter'].includes(e.type)&&e.mode==='windup'){clearHazards();e.mode='recover';e.timer=2.8;announce('Préparation interrompue ! Le Veilleur est vulnérable.')}damage(e,55,null);if(e.type!=='boss'){const d=Math.max(.1,distance(e,p));moveEntity(e,(e.x-p.x)/d*1.4,(e.z-p.z)/d*1.4)}}}
function hurt(n){
 if(state!=='playing')return;
 if(p.shield>0||(hero==='voltigeur'&&p.leap>0)){
  if(boon==='vigor'&&p.absorbLock<=0){p.overcharge=Math.min(3,p.overcharge+1);p.absorbLock=.35;effect(p.x,p.z,2.1,'#91ecff',.25);tone(580,.08,'sine')}
  return;
 }
 if(p.inv>0||p.dashT>0)return;if(campaign.trials.forge.carrying)dropCore();p.stagger=.2;p.hp=Math.max(0,p.hp-n);p.inv=.65;observeTime=0;effect(p.x,p.z,1.6,'#ff564b');tone(70,.15,'triangle');$('#damageFlash').classList.remove('hit');void $('#damageFlash').offsetWidth;$('#damageFlash').classList.add('hit');if(p.hp<=0)finish(false)}
// Melee respects facing and cover; it never damages through a wall.
function clearStrikeLine(x,z){
 const d=Math.hypot(x-p.x,z-p.z),steps=Math.max(1,Math.ceil(d/.3));
 for(let i=1;i<steps;i++)if(blocked(p.x+(x-p.x)*i/steps,p.z+(z-p.z)*i/steps,.05,true))return false;
 return true;
}
function landLeap(){
 effect(p.x,p.z,4.6,'#ffac50',.65);effect(p.x,p.z,3.5,'#fff1b4',.4);tone(75,.25,'triangle');
 for(const e of enemies)if(!e.dead&&distance(e,p)<4.6+(e.type==='boss'?1:0)&&clearStrikeLine(e.x,e.z)){
  if(['boss','porter'].includes(e.type)&&e.mode==='windup'){clearHazards();e.mode='recover';e.timer=2;announce('Frappe au sol : le Veilleur est interrompu !')}
  damage(e,95,null);
 }
}
function movement(){return{x:joy.x+Number(keys.has('d')||keys.has('arrowright'))-Number(keys.has('a')||keys.has('q')||keys.has('arrowleft')),z:joy.y+Number(keys.has('s')||keys.has('arrowdown'))-Number(keys.has('w')||keys.has('z')||keys.has('arrowup'))}}
function spawn(x,z,type='warden'){const root=new THREE.Group();scene.add(root);const robe=mesh(enemyRobeGeo,type==='boss'?enemyArmor:dark,0,.9,0,1,1,1,root);mesh(sphereGeo,joint,0,1.7,0,.4,.4,.4,root);box(type==='archer'?cyan:red,0,1.7,-.35,.45,.09,.1,root);const armBones=[];for(const x of [-.5,.5]){const a=new THREE.Group();a.position.set(x,1.45,0);root.add(a);mesh(cylGeo,joint,0,-.3,0,.13,.65,.13,a);armBones.push(a);}if(type==='oracle'){const crown=mesh(new THREE.TorusGeometry(.65,.08,6,16),cyan,0,2.2,0,1,1,1,root);crown.rotation.x=Math.PI/2;crown.userData.ownedGeometry=true;}if(type==='archer')box(cyan,.6,1.2,-.4,.14,.8,.14,root);if(type==='boss'){root.scale.setScalar(2.2);for(const x of [-.6,.6])box(bronze,x,1.65,0,.4,.4,.5,root);const crown=mesh(new THREE.TorusGeometry(.45,.08,6,16),gold,0,2.3,0,1,1,1,root);crown.rotation.x=Math.PI/2;crown.userData.ownedGeometry=true}root.position.set(x,0,z);const e={root,robe,rig:{arms:armBones},x,z,hp:type==='boss'?700:80,max:type==='boss'?700:80,type,mode:'idle',timer:1.2,dead:false,flash:0};if(type==='archer'){e.sight=box(new THREE.MeshBasicMaterial({color:'#ff7154',transparent:true,opacity:.45,depthWrite:false}),0,.04,-7,.055,.02,14,root);e.sight.userData.ownedMaterial=true;e.sight.visible=false;}if(type!=='boss'){const health=new THREE.Sprite(new THREE.SpriteMaterial({color:'#f5a391',depthTest:false}));health.position.set(0,2.5,0);health.scale.set(1.2,.07,1);health.visible=false;health.userData.ownedMaterial=true;root.add(health);e.healthBar=health;}if(type==='shade'){e.hp=e.max=120;e.reveal=0;e.phaseOffset=Math.random()*6;e.robe.material=cloth.clone();e.robe.material.transparent=true;e.robe.userData.ownedMaterial=true;}if(type==='porter'){e.hp=e.max=380;e.root.scale.setScalar(1.6);}if(type==='anchor'){e.hp=e.max=65;root.children.forEach(c=>c.visible=c===e.robe||c===e.healthBar);e.robe.geometry=new THREE.OctahedronGeometry(.8);e.robe.material=cyan;e.robe.userData.ownedGeometry=true;e.robe.position.y=1.5;}if(type==='oracle')e.hp=e.max=110;if(type==='sentinel'){e.hp=e.max=160;e.facing=Math.PI;e.blockHint=0;e.plate=box(bronze,0,1.3,-.65,1.25,1.7,.25,root);box(runeGold,0,1.3,-.79,.65,.75,.03,root);}enemies.push(e);return e}
function enemyShot(e,angle,speed=7){const dx=-Math.sin(angle),dz=-Math.cos(angle),o=mesh(sphereGeo,red,e.x,1.25,e.z,.23,.23,.23);bullets.push({mesh:o,x:e.x,z:e.z,dx,dz,t:5,enemy:true,speed})}
function updateBoss(e,dt){
 if(e.dead)return;e.timer-=dt;e.root.rotation.y=Math.atan2(e.x-p.x,e.z-p.z);
 const next=e.hp<e.max*.3?3:e.hp<e.max*.65?2:1;
 if(next>e.phase){e.phase=next;announce(next===2?'Le Veilleur appelle deux Oracles. Vous pouvez les éliminer pour libérer la cour.':'Dernière sonnerie : les fissures se croisent. Gardez une esquive pour la seconde marque.');effect(e.x,e.z,6,'#ffb16b',.8);}
 if(e.timer<=0){
  if(e.mode==='idle'){
   e.mode='windup';e.windupTotal=e.timer=1.4+(secretFound?.45:0);e.attackKind=e.pattern++%3;
   const target=enemyTarget(e),delay=e.windupTotal-.04;
   if(e.attackKind===0){addHazard(target.x,target.z,3.5,delay,28);if(e.phase===3)addHazard(clamp(target.x-4,-20,20),target.z,2.5,delay+.5,22);}
   else if(e.attackKind===1){const dx=target.x-e.x,dz=target.z-e.z,n=Math.max(.1,Math.hypot(dx,dz));for(let i=1;i<=7;i++)addHazard(clamp(e.x+dx/n*i*2.4,-20,20),clamp(e.z+dz/n*i*2.4,-105,-77),1.5,delay+i*.035,24);}
   else{addHazard(e.x,e.z,5,delay,30);if(e.phase>1)addHazard(target.x,target.z,2.5,delay+.35,22);}
  }else if(e.mode==='windup'){
   e.mode='recover';e.timer=e.phase===1?3.2:e.phase===2?2.8:2.5;
   if(e.attackKind===2||e.phase===3)for(let i=0;i<8;i++)enemyShot(e,i/8*Math.PI*2,5);
   tone(80,.2);
  }else{e.mode='idle';e.timer=1.1;}
 }
 e.robe.material=e.flash>0?red:e.mode==='recover'?bronze:enemyArmor;
}
// The sentinel locks its facing during an announced charge: a chance to flank it.
function updateSentinel(e,dt){
 e.timer-=dt;e.blockHint=Math.max(0,e.blockHint-dt);
 const target=enemyTarget(e),desired=Math.atan2(e.x-target.x,e.z-target.z);
 if(e.mode==='idle'){
  e.facing+=clamp(wrap(desired-e.facing),-dt*1.15,dt*1.15);
  if(distance(e,target)<13&&e.timer<=0){
   e.mode='windup';e.timer=1;e.facing=desired;e.dx=-Math.sin(e.facing);e.dz=-Math.cos(e.facing);
   for(let i=1;i<=5;i++)addHazard(e.x+e.dx*i*1.5,e.z+e.dz*i*1.5,.45,1.2,0,'#eeb481');
  }
 }else if(e.mode==='windup'&&e.timer<=0){e.mode='charge';e.timer=.55;}
 else if(e.mode==='charge'){
  const beforeX=e.x,beforeZ=e.z;moveEntity(e,e.dx*13*dt,e.dz*13*dt,.7);
  if(distance(e,p)<1.4)hurt(25);
  if(e.timer<=0||Math.hypot(e.x-beforeX,e.z-beforeZ)<.01){e.mode='recover';e.timer=2.6;effect(e.x,e.z,2,'#ffd191',.45);}
 }else if(e.mode==='recover'&&e.timer<=0){e.mode='idle';e.timer=1.3;}
 e.root.position.set(e.x,0,e.z);e.root.rotation.y=e.facing;
 e.plate.rotation.x=e.mode==='recover'?-.8:0;
 e.robe.material=e.flash>0?red:e.mode==='recover'?bronze:dark;
}
function buildBell(x=9,z=-82){
 const root=new THREE.Group();root.position.set(x,0,z);scene.add(root);roomObject(root);
 for(const x of [-1,1])box(stone,x,1.7,0,.28,3.4,.4,root);
 box(bronze,0,3.3,0,2.3,.25,.5,root);
 const body=mesh(cylGeo,bronze,0,2.3,0,.65,1.15,.65,root);
 mesh(sphereGeo,gold,0,1.8,0,.18,.18,.18,root);
 label('CLOCHE',x,z,'#ffc98b',3);
 bell={root,body,x,z,used:false,swing:0};
}
function ringBell(){
 if(!bell||bell.used||!boss||boss.dead)return;
 bell.used=true;bell.swing=1.6;clearHazards();
 bullets.filter(b=>b.enemy).forEach(b=>scene.remove(b.mesh));bullets=bullets.filter(b=>!b.enemy);
 boss.mode='recover';boss.timer=4;effect(bell.x,bell.z,14,'#f5cf8f',1);tone(440,.8,'sine',.045);
 announce('La cloche impose le silence : 4 secondes pour approcher et frapper. Elle ne peut sonner qu’une fois.');
}
function updateEnemy(e,dt){if(e.dead||!trialActive(e))return;if(e.type==='anchor')return;if(e.type==='shade'){updateShade(e,dt);return;}if(e.type==='porter'){if(distance(e,p)<24)updatePorter(e,dt);return;}e.alert=Math.max(0,(e.alert||0)-dt);if(e.type==='boss'&&!campaign.bossAwake)return;if(e.type!=='boss'&&distance(e,p)>26&&e.alert<=0)return;if(e.type==='oracle'){updateOracle(e,dt);return;}if(e.type==='boss'){updateBoss(e,dt);return}if(e.type==='sentinel'){updateSentinel(e,dt);return}e.timer-=dt;const target=enemyTarget(e),d=distance(e,target);e.root.rotation.y=Math.atan2(e.x-target.x,e.z-target.z);
if(e.mode==='windup'){if(e.timer<=0){if(e.type==='archer'){enemyShot(e,e.lockAngle);effect(e.x,e.z,1,'#85d9ff',.2)}e.mode='recover';e.timer=1.1}}
else if(e.mode==='recover'){if(e.timer<=0){e.mode='idle';e.timer=.5}}
else if(e.timer<=0&&d<(e.type==='archer'?17:4)){e.mode='windup';e.timer=e.type==='archer'?1.1:.9;if(e.type==='archer'){e.lockAngle=Math.atan2(e.x-target.x,e.z-target.z);effect(e.x,e.z,1.4,'#85d9ff',1.1)}else addHazard(e.x,e.z,2.6,.85,22)}
else if(e.type==='warden'&&d>2){steerToward(e,target,dt,3.3)}else if(e.type==='archer'&&d>17&&e.alert>0){steerToward(e,target,dt,1.8)}else if(e.type==='archer'&&d<5){steerToward(e,{x:e.x+(e.x-target.x),z:e.z+(e.z-target.z)},dt,1.8)}
if(e.sight){e.sight.visible=e.mode==='windup';if(e.mode==='windup')e.root.rotation.y=e.lockAngle;}e.root.position.set(e.x,Math.sin(t*3+e.x)*.06,e.z);e.robe.material=e.flash>0?red:dark;}
// Pact effects are mechanical changes, with explicit trade-offs.
function chooseBoon(value){
 if(boon||!['vigor','haste'].includes(value))return;
 boon=value;
 if(value==='vigor'){p.max=HEROES[hero].hp+40;p.hp=p.max}else{p.max=HEROES[hero].hp-30;p.hp=Math.min(p.hp,p.max)}
 shrines.forEach(s=>s.root.visible=false);
 announce(value==='vigor'?'Braise : les impacts absorbés par votre pouvoir chargent votre prochaine attaque. Esquive plus lente. Les portes des deux chemins sont ouvertes.':'Élan : vos esquives laissent un leurre. Vous êtes plus fragile. Les portes des deux chemins sont ouvertes.');
 for(const trap of campaign.traps){const row=Math.round((-45-trap.userData.z)/8);const gap=value==='vigor'?0:(row%2===0?-6:6);trap.userData.gap=gap;const a=trap.userData.side===0?-14:gap+2.5,b=trap.userData.side===0?gap-2.5:14;trap.position.x=(a+b)/2;trap.scale.x=b-a;}
 for(const marker of campaign.safeMarkers)marker.position.x=value==='vigor'?0:(marker.userData.row%2===0?-6:6);updateCampaignGates();tone(620,.25);updateHUD();updateInteraction();
}
function clearDecoy(){if(decoy){cleanupObject(decoy.root);decoy=null}}
function createDecoy(){
 clearDecoy();const root=new THREE.Group();root.position.set(p.x,0,p.z);scene.add(root);
 const material=new THREE.MeshBasicMaterial({color:'#c7abff',transparent:true,opacity:.45,depthWrite:false});
 const shape=mesh(coneGeo,material,0,1,0,.85,1.05,.85,root);shape.userData.ownedMaterial=true;
 mesh(sphereGeo,material,0,2,0,.3,.3,.3,root);
 decoy={root,x:p.x,z:p.z,t:1.8,material};effect(p.x,p.z,1.5,'#c7abff',.4);
}
function enemyTarget(e){return decoy&&decoy.t>0&&distance(e,decoy)<17?decoy:p}
function interactionTarget(){
 const trial=trialTarget();if(trial)return trial;
 if(room===2&&bell&&!bell.used&&boss&&!boss.dead&&distance(p,bell)<2.7)return{type:'bell',label:'Sonner · 1 usage'};
 if(!boon){for(let i=0;i<shrines.length;i++)if(distance(p,shrines[i])<2.7)return{type:'pact',value:i===0?'vigor':'haste',label:'Examiner le serment'};}
 if(secretMirror&&!secretFound&&distance(p,secretMirror)<2.6)return{type:'mirror',label:'Maintenir · observer'};
 return null;
}
function openPact(value){
 if(state!=='playing'||boon)return;
 pendingPact=value;state='choice';clearTimeout(pactConfirmTimer);$('#sealPact').disabled=true;pactConfirmTimer=setTimeout(()=>{if(state==='choice')$('#sealPact').disabled=false;},250);clearInputs();$('#choicePanel').hidden=false;$('#mobile').classList.remove('playing');$('#interact').hidden=true;
 const heavy=value==='vigor',isLight=hero==='voltigeur';
 $('#pactTitle').textContent=heavy?'Serment de Braise':'Serment d’Élan';
 $('#pactGift').textContent=heavy?`${HEROES[hero].hp+40} PV maximum. Les impacts absorbés ${isLight?'pendant le bond':'par le bouclier'} renforcent la prochaine ${isLight?'frappe':'attaque'}, jusqu’à trois charges.`:`L’esquive se recharge en ${Math.max(.8,HEROES[hero].dash*.583333).toFixed(2).replace('.',',')} seconde et laisse une ombre de 1,8 seconde qui détourne les ennemis.`;
 $('#pactCost').textContent=heavy?`L’esquive se recharge en ${(HEROES[hero].dash+.6).toFixed(hero==='rempart'?1:2).replace('.',',')} secondes.`:`Corps fragile : vos PV maximum passent à ${HEROES[hero].hp-30}.`;
 $('#pactWorld').textContent=heavy?'La nef ouvrira une voie centrale, avec un brasier plus long.':'La nef ouvrira des passages latéraux alternés, avec un brasier plus court.';
}
function closePact(confirm){
 if(state!=='choice')return;
 clearTimeout(pactConfirmTimer);$('#sealPact').disabled=false;const value=pendingPact;pendingPact='';$('#choicePanel').hidden=true;state='playing';
 if(confirm)chooseBoon(value);
 $('#mobile').classList.add('playing');releaseMenuFocus();last=performance.now();accumulator=0;updateInteraction();
}
$('#sealPact').onclick=()=>closePact(true);$('#leavePact').onclick=()=>closePact(false);
function interact(){
 if(state!=='playing')return;const target=interactionTarget();if(!target)return;
 if(!['pact','bell','mirror'].includes(target.type)){trialInteract(target);return;}if(target.type==='pact')openPact(target.value);else if(target.type==='bell')ringBell();else observing=true;
}
$('#interact').onpointerdown=e=>{
 e.preventDefault();if(state!=='playing')return;interactId=e.pointerId;
 try{$('#interact').setPointerCapture(e.pointerId)}catch(_){}
 if(interactionTarget()?.type==='mirror')observing=true;
};
function stopInteract(e){
 if(e.pointerId!==interactId)return;
 const target=interactionTarget(),rect=$('#interact').getBoundingClientRect();
 const inside=e.clientX>=rect.left&&e.clientX<=rect.right&&e.clientY>=rect.top&&e.clientY<=rect.bottom;
 observing=false;interactId=null;
 if(e.type==='pointerup'&&inside&&target?.type!=='mirror'){e.preventDefault();interact();}
}
$('#interact').onpointerup=$('#interact').onpointercancel=$('#interact').onlostpointercapture=stopInteract;
$('#interact').onclick=e=>{if(e.detail===0)interact()};
function updateInteraction(){
 const target=state==='playing'?interactionTarget():null;
 $('#interact').hidden=!target;document.body.classList.toggle('has-interaction',!!target);
 if(target)$('#interact').textContent=target.type==='mirror'&&observing?`Observer · ${Math.min(100,Math.floor(observeTime/1.5*100))}%`:(coarse()?'':'F · ')+target.label;
 $('#pactStatus').textContent=!boon?'Serment : à choisir':boon==='vigor'?`Braise · charges ${p.overcharge}/3`:'Élan · leurre à chaque esquive';
 $('#secretStatus').textContent=secretFound?'✧ Marque du Reflet retrouvée':'';
}
function buildMirror(x=-23,z=-29){
 const root=new THREE.Group();root.position.set(x,0,z);scene.add(root);roomObject(root);
 const surface=mesh(discGeo,new THREE.MeshStandardMaterial({color:'#35425d',metalness:.85,roughness:.16,emissive:'#161226',side:THREE.DoubleSide}),0,.06,0,2,2,2,root);surface.rotation.x=-Math.PI/2;surface.userData.ownedMaterial=true;
 const rim=mesh(ringGeo,bronze,0,.08,0,2.15,2.15,2.15,root);rim.rotation.x=-Math.PI/2;
 const reflection=mesh(coneGeo,joint,0,.5,0,.55,.55,.55,root);reflection.rotation.z=Math.PI;
 secretMirror={root,x,z,reflection};
 label('REFLET',x,z,'#bba8e2',3);
}
function findSecret(){
 if(secretFound)return;secretFound=true;secretNewThisRun=true;observing=false;observeTime=0;
 try{localStorage.setItem(SECRET_KEY,'found')}catch(_){}
 effect(secretMirror.x,secretMirror.z,3,'#baa0ff',1);tone(860,.3);announce('Marque du Reflet retrouvée. Le Veilleur la reconnaîtra : ses préparations seront plus lentes. C’est un premier indice vers l’Éclipse.');
}
function updateDesign(dt){
 if(bell){bell.swing=Math.max(0,bell.swing-dt);bell.body.rotation.z=Math.sin(bell.swing*17)*bell.swing*.2;}
 if(decoy){decoy.t-=dt;decoy.material.opacity=Math.max(0,decoy.t/1.8*.45);if(decoy.t<=0)clearDecoy()}
 const target=interactionTarget();
 if(target?.type==='mirror'&&observing&&Math.hypot(p.vx,p.vz)<.3&&!shooting&&!mouseDown&&p.recoil===0&&p.leap<=0){observeTime+=dt;if(observeTime>=1.5)findSecret()}
 else observeTime=0;
 updateInteraction();
}
function updateRoom(dt){return updateCampaign(dt)}
function updateHUD(){
 $('#hp i').style.width=p.hp/p.max*100+'%';
 const q=campaign.trials;
 $('#objective').textContent=!boon?'I · Choisir un serment':campaign.keys.size<2?`II · Âme ${q.escort.done?'✓':'à guider'} · Carillon ${q.bells.done?'✓':q.bells.step+'/3'}`:!q.archive||!q.forge.done?`III · Archives ${q.archive?'✓':'à purifier'} · Forge ${q.forge.done?'✓':q.forge.carrying?'noyau à rapporter':q.forge.valves.length+'/3 vannes'}`:q.ritual.length<2?`IV · Charger les sceaux ${q.ritual.length}/2`:!campaign.defeated.has('carillonneur')?'V · Briser les chaînes et vaincre le Carillonneur':q.extraction?`VII · Extraction · ${Math.ceil(campaign.escapeLeft)} s`:'VI · Affronter le Veilleur';
 const active=campaign.activeSeconds||campaign.time;$('#runClock').textContent=`${Math.floor(active/60)}:${String(Math.floor(active%60)).padStart(2,'0')} · cible 10–15 min`;
 $('#cooldown').textContent=`${Math.ceil(p.hp)}/${p.max} PV · Esquive ${p.dash>0?p.dash.toFixed(1)+' s':'prête'} · ${HEROES[hero].powerName} ${(p.shield>0||p.leap>0)?'ACTIF':p.power>0?Math.ceil(p.power)+' s':'prêt'}`;
 $('#power').textContent=(p.shield>0||p.leap>0)?'Actif':p.power>0?Math.ceil(p.power)+' s':HEROES[hero].powerName;
 $('#fire').textContent=hero==='voltigeur'?'Frapper':'Tirer';$('#heroIdentity').textContent=HEROES[hero].name;
 $('#combatHint').textContent=p.attack?.melee?`Enchaînement ${p.attack.combo}/3 · ${p.attack.struck?'récupération':'préparation'}`:'';
 const zone=world.zoneAt(p.x,p.z);
 $('#roomHint').textContent=q.extraction?'Rejoignez l’âme à la croisée.':zone==='Jardins suspendus'&&!q.escort.done?(q.escort.started?'Restez près de l’âme ; libérez ses passages.':'Approchez l’âme et accueillez-la.'):zone==='Cloître des cendres'&&!q.bells.done?(q.bells.read?q.bells.order.join(' → '):'La fresque révèle l’ordre des lanternes.'):zone==='Archives du Reflet'&&!q.archive?'Frappez les Reflets matérialisés ; le pouvoir les révèle.':zone==='Forge du brasier'&&!q.forge.done?(q.forge.carrying?'Retour au refuge · attaquer pose le noyau.':'Fermez les vannes, puis rapportez le noyau.'):zone==='Nef des marées'&&q.ritual.length===2&&!campaign.defeated.has('carillonneur')?'Les deux chaînes protègent le Carillonneur.':'';$('#dash').textContent=p.dash>0?p.dash.toFixed(1):'Esquive';
 $('#bossHUD').hidden=!campaign.bossAwake||!boss||boss.dead;document.body.classList.toggle('has-boss',!$('#bossHUD').hidden);
 if(boss&&!boss.dead){$('#bossHP').style.width=Math.max(0,boss.hp/boss.max*100)+'%';$('#bossState').textContent=boss.mode==='recover'?'VULNÉRABLE · attaquez !':boss.mode==='windup'?'PRÉPARATION · esquivez':'GARDE · dégâts réduits';}
}
function update(dt){if(hitPause>0){hitPause=Math.max(0,hitPause-dt);return;}t+=dt;updateSparks(dt);const wasLeaping=p.leap>0;for(const k of ['stagger','leap','swing','comboWindow','shot','dash','dashT','power','shield','inv','absorbLock'])p[k]=Math.max(0,p[k]-dt);p.recoil=Math.max(0,p.recoil-dt*7);if(wasLeaping&&p.leap===0)landLeap();const v=movement(),n=Math.hypot(v.x,v.z),deadzone=.12;let x=n<deadzone?0:v.x,z=n<deadzone?0:v.z;if(n>deadzone){const magnitude=Math.min(1,(n-deadzone)/(1-deadzone));x=x/n*magnitude;z=z/n*magnitude;}const response=1-Math.exp(-dt*(n>deadzone?18:26));const carry=campaign.trials.forge.carrying?.72:1;p.vx+=(x*HEROES[hero].speed*carry-p.vx)*response;p.vz+=(z*HEROES[hero].speed*carry-p.vz)*response;if(p.dashT>0)moveEntity(p,p.dx*24*dt,p.dz*24*dt);else moveEntity(p,p.vx*dt,p.vz*dt);
if(coarse()){const target=enemies.filter(e=>!e.dead&&trialActive(e)&&(e.type!=='shade'||shadeVulnerable(e))&&distance(e,p)<16&&(e.type!=='boss'||campaign.bossAwake)&&clearStrikeLine(e.x,e.z)).sort((a,b)=>distance(a,p)-distance(b,p))[0];if(target)targetAim=Math.atan2(p.x-target.x,p.z-target.z);else if(n>deadzone)targetAim=Math.atan2(-x,-z);reticle.visible=false}else{reticle.visible=mouseAim;if(mouseAim){ray.setFromCamera(pointer,camera);if(ray.ray.intersectPlane(ground,aimPoint)){targetAim=Math.atan2(p.x-aimPoint.x,p.z-aimPoint.z);reticle.position.set(aimPoint.x,.07,aimPoint.z)}}else if(n>deadzone)targetAim=Math.atan2(-x,-z)}
aim+=wrap(targetAim-aim)*(1-Math.exp(-dt*20));const speed=Math.hypot(p.vx,p.vz);walkPhase+=(p.dashT>0?12:speed)*dt*1.9;player.root.rotation.x=p.dashT>0?-.22*(p.dx*-Math.sin(aim)+p.dz*-Math.cos(aim)):0;const jumpHeight=p.leap>0?Math.sin((1-p.leap/.75)*Math.PI)*3.2:0;player.root.position.set(p.x,jumpHeight+Math.abs(Math.sin(walkPhase))*Math.min(.07,speed*.012),p.z);player.root.rotation.y=aim;player.legs.forEach((leg,i)=>leg.rotation.x=Math.sin(walkPhase+i*Math.PI)*.42*Math.min(1,speed/3));player.arms.forEach((a,i)=>a.rotation.x=hero==='rempart'&&i===1?1.2+p.recoil*.1:Math.sin(walkPhase+i*Math.PI)*.28*Math.min(1,speed/3));player.body.rotation.x=-p.recoil*.09;player.root.rotation.z=Math.sin(walkPhase)*.025*Math.min(1,speed/3);muzzle.visible=hero==='rempart'&&p.recoil>.55;slash.visible=hero==='voltigeur'&&p.swing>0;slashMaterial.opacity=p.swing/.28*.85;slash.rotation.z=(p.combo%2?1:-1)*(1-p.swing/.28)*.65;player.sword.rotation.z=p.swing>0?-1+(1-p.swing/.28)*2:.1;player.scarf.rotation.x=-.45-speed*.025+Math.sin(walkPhase*.7)*.08;player.cape.rotation.x=.12+speed*.035+Math.sin(walkPhase*.6)*.05;landingMarker.visible=p.leap>0;landingMarker.position.set(p.x,.08,p.z);shield.visible=p.shield>0;shield.rotation.y+=dt;player.body.material=p.inv>0?bronze:hero==='voltigeur'?cloth:armor;heroShadow.position.set(p.x,.035,p.z);trailTimer-=dt;if(p.dashT>0&&trailTimer<=0){effect(p.x,p.z,.8,'#baa4ef',.25);trailTimer=.055}carriedCore.visible=campaign.trials.forge.carrying;poseHero(dt);if(shooting||mouseDown||p.attackBuffer>t)fire();updateAttack(dt);
for(const e of enemies){e.root.visible=trialActive(e)&&distance(e,p)<52;e.flash=Math.max(0,e.flash-dt);updateEnemy(e,dt);poseEnemy(e);e.root.rotation.z=e.flash>0?Math.sin(t*75)*.06:0;if(e.healthBar){e.healthBar.visible=e.hp<e.max;e.healthBar.scale.x=1.2*Math.max(0,e.hp/e.max);}}
for(const b of bullets){const oldX=b.x,oldZ=b.z;b.x+=b.dx*(b.enemy?b.speed:32)*dt;b.z+=b.dz*(b.enemy?b.speed:32)*dt;b.t-=dt;b.mesh.position.set(b.x,1.35,b.z);if(blocked(b.x,b.z,.1,true)){b.t=0;effect(b.x,b.z,.6,b.enemy?'#ff8065':'#ffc17b',.2)}if(b.t>0){if(b.enemy){if(distance(b,p)<.8){hurt(14);b.t=0}}else for(const e of enemies)if(!e.dead&&distance(e,b)<(e.type==='boss'?1.7:.85)){const previousHP=e.hp;damage(e,b.damage||34,{x:oldX,z:oldZ});if(e.hp<previousHP)sparks(e.x,e.z);b.t=0;effect(b.x,b.z,.9,'#ffd292',.18);break}}if(b.t<=0){scene.remove(b.mesh)}}bullets=bullets.filter(b=>b.t>0);enemies=enemies.filter(e=>!e.dead);
for(const h of hazards){h.delay-=dt;if(h.delay<=0&&!h.fired){h.fired=true;h.mesh.material.opacity=.85;if(h.damage>0&&distance(p,h)<h.r+.3)hurt(h.damage);effect(h.x,h.z,h.r,'#ff6542',.35)}if(h.fired)h.tail-=dt;else h.mesh.material.opacity=.16+(1-h.delay/h.max)*.3}hazards=hazards.filter(h=>{if(h.tail<=0){scene.remove(h.mesh);h.mesh.material.dispose();return false}return true});
for(const e of effects){e.t-=dt;e.mesh.scale.setScalar(Math.max(.01,e.r*(1-e.t/e.max)));e.mesh.material.opacity=Math.max(0,e.t/e.max)}effects=effects.filter(e=>{if(e.t<=0){scene.remove(e.mesh);e.mesh.material.dispose();return false}return true});for(const s of shrines){s.crystal.rotation.y+=dt;s.crystal.position.y=1.8+Math.sin(t*2)*.15}updateDesign(dt);if(state==='playing')updateRoom(dt);updateHUD()}
// Focus changes are not a reliable indication of leaving the game on mobile.
// Clear desktop inputs on blur; only real page visibility changes auto-pause.
addEventListener('blur',()=>{keys.clear();mouseDown=false});
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')pause('hidden')});
addEventListener('pagehide',()=>{if(document.visibilityState==='hidden')pause('hidden')});
addEventListener('keydown',e=>{
 const k=e.key.toLowerCase();
 if(k==='escape'&&state==='map'&&!e.repeat){e.preventDefault();toggleMap();return;}
 if(k==='m'&&state==='playing'&&!e.repeat){e.preventDefault();toggleMap();return;}
 if(k==='escape'&&state==='choice'&&!e.repeat){e.preventDefault();closePact(false);return;}
 if(k==='escape'&&!e.repeat){
  if(state==='paused'){e.preventDefault();resume()}
  else if(state==='playing'){e.preventDefault();pause('manual')}
  return;
 }
 if(state!=='playing')return;
 if([' ','arrowup','arrowdown','arrowleft','arrowright','e'].includes(k))e.preventDefault();
 keys.add(k);
 if(!e.repeat){if(k===' ')dash();if(k==='e')power();if(k==='f')interact()}
});
addEventListener('keyup',e=>{keys.delete(e.key.toLowerCase());if(e.key.toLowerCase()==='f')observing=false;if(state==='playing'&&e.key===' ')e.preventDefault()});
// Prevent browser scroll/selection gestures only over active gameplay, not menus.
document.addEventListener('touchmove',e=>{
 if(state==='playing'&&e.target instanceof Element&&e.target.closest('#mobile, #world, #interact'))e.preventDefault();
},{passive:false});
function point(e){pointer.set(e.clientX/innerWidth*2-1,-e.clientY/innerHeight*2+1);mouseAim=true}canvas.onpointermove=e=>{if(e.pointerType==='mouse')point(e)};canvas.onpointerdown=e=>{if(e.pointerType==='mouse'){point(e);mouseDown=true;requestAttack()}};addEventListener('pointerup',e=>{if(e.pointerType==='mouse')mouseDown=false});canvas.oncontextmenu=e=>e.preventDefault();
const stick=$('#stick');function moveStick(e){const r=stick.getBoundingClientRect(),x=e.clientX-r.left-r.width/2,y=e.clientY-r.top-r.height/2,n=Math.hypot(x,y),f=Math.min(1,40/(n||1));joy.x=x*f/40;joy.y=y*f/40;$('#knob').style.transform=`translate(${x*f}px,${y*f}px)`}stick.onpointerdown=e=>{if(state!=='playing'||stickId!==null)return;e.preventDefault();stickId=e.pointerId;try{stick.setPointerCapture(e.pointerId)}catch(_){}moveStick(e)};stick.onpointermove=e=>{if(e.pointerId===stickId)moveStick(e)};function stopStick(e){if(e.pointerId===stickId){stickId=null;joy.x=joy.y=0;$('#knob').style.transform=''}}stick.onpointerup=stick.onpointercancel=stick.onlostpointercapture=stopStick;
$('#fire').onpointerdown=e=>{if(state!=='playing'||fireId!==null)return;e.preventDefault();fireId=e.pointerId;try{$('#fire').setPointerCapture(e.pointerId)}catch(_){}shooting=true;requestAttack()};function stopFire(e){if(e.pointerId===fireId){shooting=false;fireId=null}}$('#fire').onpointerup=$('#fire').onpointercancel=$('#fire').onlostpointercapture=stopFire;
$('#dash').onpointerdown=e=>{e.preventDefault();dash()};$('#power').onpointerdown=e=>{e.preventDefault();power()};
function resize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)}addEventListener('resize',resize);
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();pause('graphics');announce('La 3D a été interrompue. Rechargez la page et essayez la qualité légère.')});
function frame(now){const rawElapsed=(now-(last||now))/1000,elapsed=Math.min(.1,rawElapsed);last=now;if(state==='playing'&&campaign)campaign.activeSeconds+=Math.max(0,rawElapsed);if(state==='playing'){accumulator+=elapsed;while(accumulator>=1/60&&state==='playing'){update(1/60);accumulator-=1/60}}else accumulator=0;
if(state!=='playing')$('#interact').hidden=true;
if(p){const portrait=innerWidth<innerHeight;camDesired.set(p.x+p.vx*.08,portrait?19:13,p.z+(portrait?20:16));camera.position.lerp(camDesired,1-Math.exp(-elapsed*5));cameraTarget.set(p.x+p.vx*.12,1,p.z-4+p.vz*.1);cameraLook.lerp(cameraTarget,1-Math.exp(-elapsed*7));camera.lookAt(cameraLook)}art.update(elapsed);dust.rotation.y+=elapsed*.015;halo.rotation.z+=elapsed*.02;renderer.render(scene,camera);if(now>noticeUntil)$('#notice').hidden=true;requestAnimationFrame(frame)}initCombatMotion();wireCampaignUI();requestAnimationFrame(frame);
