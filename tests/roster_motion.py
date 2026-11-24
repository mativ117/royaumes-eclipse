"""CPU verification of the eleven real skinned hero assets and their controller.

Requires Node and the retained Three.js loader; no renderer, GPU or network.
Geometry is evaluated after skinning. Materials are omitted only from this
CPU test. This test measures contracts and motion, not artistic quality.
"""
from pathlib import Path
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ROLES = ['rempart', 'voltigeur', 'lame', 'tisseuse', 'cendres', 'voleur',
         'bergere', 'colosse', 'accordeur', 'neant', 'eclipse']
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--hero', choices=ROLES, action='append')
parser.add_argument('--report', type=Path, default=Path('/tmp/roster-motion-report.json'))
args = parser.parse_args()

NODE = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
global.window=global;global.self=global;global.THREE=require('./vendor/three.min.js');
vm.runInThisContext(fs.readFileSync('vendor/three-addons.js','utf8'));
global.hero=process.argv[2];global.player={root:new THREE.Group(),legacyParts:[]};
global.scene=new THREE.Scene();scene.add(player.root);global.aim=0;global.t=0;
global.campaign={trials:{forge:{carrying:false}}};global.enemies=[];global.state='playing';
global.refineHeroMaterials=()=>{};global.p={};
global.moveEntity=(actor,dx,dz)=>{actor.x+=dx;actor.z+=dz;};global.trialActive=()=>true;
for(const file of ['roster.js','lame-motion.js','avatar-kinematics.js','authored-avatar.js','blade-contact.js','dynamics.js'])
 vm.runInThisContext(fs.readFileSync('src/'+file,'utf8'),{filename:file});
vm.runInThisContext('updateBladeTrail=()=>{};');
const raw=fs.readFileSync('assets/characters/'+hero+'.glb');
const hash=crypto.createHash('sha256').update(raw).digest('hex');
if(hero==='lame')assert.strictEqual(hash,'200c30d20d5ef4735f27871ebcd8165d95a8bedbf98a7cb3d3c23b43a72312f6','Approved Lame asset changed');
const length=raw.readUInt32LE(12),doc=JSON.parse(raw.subarray(20,20+length)),binary=raw.subarray(20+length);
const imageCount=doc.images?.length||0,materialCount=doc.materials?.length||0;
assert(imageCount>=3&&materialCount>=8,'Retain the authored PBR material maps');
for(const mesh of doc.meshes)for(const primitive of mesh.primitives)delete primitive.material;
delete doc.materials;delete doc.images;delete doc.textures;
let json=Buffer.from(JSON.stringify(doc));json=Buffer.concat([json,Buffer.alloc((4-json.length%4)%4,32)]);
const header=Buffer.from(raw.subarray(0,20));header.writeUInt32LE(20+json.length+binary.length,8);header.writeUInt32LE(json.length,12);
const packed=Buffer.concat([header,json,binary]);
function load(){return new Promise((resolve,reject)=>new RoyaumesGLTFLoader().parse(packed.buffer.slice(packed.byteOffset,packed.byteOffset+packed.length),'',resolve,reject));}
(async()=>{
const gltf=await load();global.a=makeHeroAvatar(gltf.scene,gltf.animations,hero);
vm.runInThisContext('avatarRuntime.current=a;avatarRuntime.heroes[hero]=a;avatarRuntime.status="ready";');
assert(a.motionCalibration,'Missing or rejected physical motion calibration: '+hero);
assert.strictEqual(a.motionCalibration.heroId,hero);
const required=['idle','guard','walk','run','walk_back','strafe_left','strafe_right','attack1','attack2','attack3','shot','power','dash','dodge_left','dodge_right','start','stop','turn_left','turn_right','leap','shield','interact','carry','hit'];
for(const name of required)if(name!=='power'||hero!=='lame')assert(a.actions[name]&&a.lowerActions[name],hero+' missing '+name);
for(const clip of gltf.animations){assert(clip.duration>0&&clip.duration<=5,clip.name+' invalid duration');for(const track of clip.tracks)assert([...track.times,...track.values].every(Number.isFinite),clip.name+' nonfinite authored keys');}
for(const name of ['walk','run'])assert(Math.abs(a.actions[name].getClip().duration-a.motionCalibration.gaits[name].duration)<.002,'Blank/missing cycle frame '+name);
for(const name of ['attack1','attack2','attack3']){
 const c=a.motionCalibration.attacks[name];assert(c,hero+' invalid '+name+' calibration');
 assert(c.hitAt>=0&&c.activeEnd>c.hitAt&&c.activeEnd<=c.duration&&c.travel>=0);
 assert(Math.abs(a.actions[name].getClip().duration-c.duration)<.002,hero+' clip/event duration mismatch '+name);
}
if(hero!=='lame'){
 assert(a.motionCalibration.shot&&a.motionCalibration.power&&a.motionCalibration.dodge,'Missing kit timing');
 assert(Math.abs(a.actions.shot.getClip().duration-a.motionCalibration.shot.duration)<.002,'Shot duration mismatch');
 assert(Math.abs(a.actions.power.getClip().duration-a.motionCalibration.power.duration)<.002,'Power duration mismatch');
 const wrong=new THREE.Group();wrong.userData.motionCalibration={version:1,heroId:hero,units:'model'};
 assert.strictEqual(readMotionCalibration(wrong,hero==='rempart'?'voltigeur':'rempart'),null,'Cross-hero metadata accepted');
}
const meshes=[],boots={L:[],R:[]},weaponWeights={};let vertices=0;
a.root.traverse(mesh=>{
 if(!mesh.isSkinnedMesh)return;meshes.push(mesh);vertices+=mesh.geometry.attributes.position.count;
 const index=mesh.geometry.attributes.skinIndex,weight=mesh.geometry.attributes.skinWeight;
 for(let i=0;i<index.count;i++){
  let totalWeight=0;
  for(let k=0;k<4;k++){
   const w=weight.getComponent(i,k),joint=index.getComponent(i,k);
   assert(Number.isFinite(w)&&w>=0&&w<=1,'Invalid skin weight');
   if(w>0)assert(Number.isInteger(joint)&&joint>=0&&joint<mesh.skeleton.bones.length,'Invalid skin joint');
   totalWeight+=w;
  }
  assert(Math.abs(totalWeight-1)<.002,'Unbound or nonnormalized skinned vertex');
  for(const side of ['L','R']){
   let influence=0;for(let k=0;k<4;k++)if(mesh.skeleton.bones[index.getComponent(i,k)]?.name==='foot'+side)influence+=weight.getComponent(i,k);
   if(influence>.4){let entry=boots[side].find(e=>e.mesh===mesh);if(!entry){entry={mesh,indices:[]};boots[side].push(entry);}entry.indices.push(i);}
  }
  if(mesh===a.weapon||a.weapon?.getObjectById(mesh.id))for(let k=0;k<4;k++)if(weight.getComponent(i,k)>.5){const bone=mesh.skeleton.bones[index.getComponent(i,k)]?.name;weaponWeights[bone]=(weaponWeights[bone]||0)+1;}
 }
});
assert(meshes.length>=2&&vertices>10000,'Authored body/weapon geometry missing');
assert(boots.L.length&&boots.R.length,'Missing actual boot geometry');
if(['rempart','cendres'].includes(hero))assert(weaponWeights.forearmL>0&&weaponWeights.weaponGrip>0,'Left shield was rebound to the gun hand');
if(hero==='voleur')assert(weaponWeights.handL>0&&weaponWeights.weaponGrip>0,'Offhand dagger was rebound to the main hand');
function evaluate(){
 scene.updateMatrixWorld(true);for(const mesh of meshes)mesh.skeleton.update();
 a.root.traverse(o=>{if(o.isBone)assert(o.matrixWorld.elements.every(Number.isFinite),'Nonfinite bone '+o.name);});
 for(const mesh of meshes){const count=mesh.geometry.attributes.position.count;for(let i=0;i<count;i+=Math.max(1,Math.floor(count/80))){const v=mesh.getVertexPosition(i,new THREE.Vector3()).applyMatrix4(mesh.matrixWorld);assert(v.toArray().every(Number.isFinite),'Nonfinite skinned vertex');assert(v.distanceTo(player.root.position)<12,'Exploded skinned mesh');}}
 return ['L','R'].map(side=>{let y=Infinity;for(const {mesh,indices}of boots[side])for(const i of indices)y=Math.min(y,mesh.getVertexPosition(i,new THREE.Vector3()).applyMatrix4(mesh.matrixWorld).y);return y;});
}
function reset(){
 Object.assign(p,{x:0,z:0,vx:0,vz:0,motionSpeed:0,shield:0,stagger:0,leap:0,dashT:0,dash:0,attack:null,powerVisualT:0});
 delete p.dashElapsed;delete p.dashDuration;delete p.dashDistance;delete p.dashProfile;
 player.root.position.set(0,0,0);player.root.rotation.set(0,0,0);aim=0;t=0;resetAvatarPose();
}
const idle={};
for(const name of ['idle','guard']){
 reset();playAvatarAction(a,name,0,true);playLowerAction(a,name,0,true);const samples=[];
 for(let i=0;i<60;i++){a.mixer.update(a.actions[name].getClip().duration/60);updateBodyDynamics(a,p,1/60);updateAvatarKinematics(a,1/60,0);samples.push(evaluate());}
 idle[name]=[0,1].map(side=>[Math.min(...samples.map(v=>v[side])),Math.max(...samples.map(v=>v[side]))]);
 assert(idle[name].flat().every(v=>v>-.015&&v<.015),hero+' actual '+name+' boot soles exceed 1.5 cm floor tolerance '+JSON.stringify(idle[name]));
}
const movement=[];
for(const hz of [30,60,120])for(const fraction of [.45,1]){
 reset();const dt=1/hz,groups=[[],[]],complete=[];let correction=0,soleCorrection=0,released=0,support=0,soleMin=Infinity,soleMax=-Infinity;
 for(let frame=0;frame<hz*4;frame++){
  p.vz=-HERO_DEFS[hero].speed*fraction;const old=p.z;advanceHeroMotion(dt);p.motionSpeed=Math.abs(p.z-old)/dt;player.root.position.set(p.x,0,p.z);t+=dt;updateRigAvatar(dt);
  const soles=evaluate();if(frame<hz)continue;
  soleMin=Math.min(soleMin,...soles);soleMax=Math.max(soleMax,...soles);
  for(let side=0;side<2;side++){
   const leg=a.legs[side];correction=Math.max(correction,leg.motionCorrection||0);soleCorrection=Math.max(soleCorrection,leg.soleCorrection||0);
   if(leg.motionContact){support++;if(leg.motionReleased)released++;groups[side].push(leg.end.getWorldPosition(new THREE.Vector3()));}
   else if(groups[side].length){complete.push(groups[side]);groups[side]=[];}
  }
 }
 const drifts=complete.filter(g=>g.length>1).map(g=>Math.hypot(g.at(-1).x-g[0].x,g.at(-1).z-g[0].z));
 assert(correction<=.14001,'Correction budget exceeded');
 assert(soleCorrection<=.14001*motionModelScale(a),'Sole correction budget exceeded');
 assert(soleMin>-.01&&soleMax<.8,'Actual boot geometry penetrates the floor by over 1 cm, or flies during forward locomotion');
 assert(support>0,'No source foot contacts registered during locomotion');
 assert(drifts.length>=3&&Math.max(...drifts)<.05,'Actual annotated support drifts beyond 5 cm');
 movement.push({hz,input:fraction,maxCorrection:correction,maxSoleCorrection:soleCorrection,maxContactDrift:drifts.length?Math.max(...drifts):null,releasedFraction:released/Math.max(1,support),contactGroups:drifts.length,bootSoles:[soleMin,soleMax],steps:a.motionFootstepSerial});
}
const attacks=[];
for(let combo=1;combo<=3;combo++){
 reset();const name='attack'+combo,definition=a.motionCalibration.attacks[name],points=[];
 p.attack={melee:true,combo,elapsed:0,...definition,aim:0};
 for(let frame=0;frame<=60;frame++){
  p.attack.elapsed=Math.min(definition.duration-.0001,frame*definition.duration/60);t+=definition.duration/60;updateRigAvatar(definition.duration/60);evaluate();
  if(p.attack.elapsed>=definition.hitAt&&p.attack.elapsed<=definition.activeEnd)points.push(a.blade.getWorldPosition(new THREE.Vector3()));
 }
 const box=new THREE.Box3().setFromPoints(points),span=points.length?box.getSize(new THREE.Vector3()).length():0;
 if(isMeleeHero())assert(span>.02,hero+' degenerate primary weapon path '+name+' '+span);
 attacks.push({clip:name,activeSamples:points.length,activeTipSpan:span,...definition});
}
reset();const dodges=[];
for(const hz of [30,60,120]){
 reset();p.dx=1;p.dz=0;const config=beginDodgeMotion(p,hero,a);
 for(let frame=0;frame<Math.ceil(config.duration*hz)+2;frame++){advanceHeroMotion(1/hz);p.dashT=Math.max(0,p.dashT-1/hz);player.root.position.set(p.x,0,p.z);t+=1/hz;updateRigAvatar(1/hz);evaluate();}
 assert(Math.abs(p.x-config.distance)<1e-8,'Frame-rate-dependent dodge');dodges.push(p.x);
}
reset();const muzzle=a.muzzle?.getWorldPosition(new THREE.Vector3()),foregrip=a.foregrip?.getWorldPosition(new THREE.Vector3());
if(isRifleHero())assert(muzzle&&foregrip&&muzzle.distanceTo(foregrip)>.2,'Collapsed gun anchors');
const shots=[];let shotSpineReference=null;
if(a.motionCalibration.shot)for(const walking of [false,true]){
 reset();const definition=a.motionCalibration.shot;let minAimDot=1,maxAimDot=-1,fireAimDot=1,fireSampleCount=0,maxSpineDelta=0;const directions=[];
 p.attack={melee:false,elapsed:0,duration:definition.duration,hitAt:definition.hitAt,aim:0};
 for(let frame=0;frame<60;frame++){
  const dt=definition.duration/60;p.attack.elapsed=frame*dt;
  if(walking){p.motionSpeed=2;p.vz=-2;p.z-=2*dt;player.root.position.z=p.z;}
  t+=dt;updateRigAvatar(dt);evaluate();
  if(isRifleHero()){
   const rotation=avatarBone(a,'spine').quaternion;
   if(!shotSpineReference)shotSpineReference=rotation.clone();
   maxSpineDelta=Math.max(maxSpineDelta,rotation.angleTo(shotSpineReference));
  }
  if(isRifleHero()){
   const muzzle=a.muzzle.getWorldPosition(new THREE.Vector3()),grip=a.foregrip.getWorldPosition(new THREE.Vector3());
   const direction=muzzle.sub(grip).normalize(),dot=direction.dot(new THREE.Vector3(0,0,-1));
   minAimDot=Math.min(minAimDot,dot);maxAimDot=Math.max(maxAimDot,dot);directions.push(direction.toArray());
   if(Math.abs(p.attack.elapsed-definition.hitAt)<definition.duration/60){fireAimDot=Math.min(fireAimDot,dot);fireSampleCount++;}
  }
 }
 shots.push({walking,minAimDot:isRifleHero()?minAimDot:null,maxAimDot:isRifleHero()?maxAimDot:null,fireAimDot:isRifleHero()?fireAimDot:null,fireSampleCount,maxSpineDelta,directions:isRifleHero()?[directions[0],directions[20],directions[40],directions.at(-1)]:[]});
}
const diagnostics={maxWalkPenetration:Math.max(0,-Math.min(...movement.map(m=>m.bootSoles[0]))),rifleAimAligned:!isRifleHero()||shots.every(s=>s.minAimDot>.8)};
console.log('ROSTER_MOTION_REPORT '+JSON.stringify({hero,sha256:hash,bytes:raw.length,vertices,images:imageCount,materials:materialCount,clips:gltf.animations.length,profile:a.motionCalibration.profile,idle,movement,attacks,shots,diagnostics,dodgeDistances:dodges,weaponWeights,muzzleForegripDistance:muzzle&&foregrip?muzzle.distanceTo(foregrip):null}));
if(isRifleHero())assert(shots.every(s=>s.fireSampleCount>0&&s.fireAimDot>.8),'Actual rifle axis points away from aim at the authored release event');
if(isRifleHero())assert(shots.every(s=>s.maxSpineDelta<.25),'Procedural torso lean accumulates outside its bounded additive pose');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
'''

reports = []
failures = []
for hero in args.hero or ROLES:
    result = subprocess.run(['node', '-', hero], cwd=ROOT, input=NODE,
                            text=True, capture_output=True)
    lines = [line for line in result.stdout.splitlines() if line.startswith('ROSTER_MOTION_REPORT ')]
    if lines:
        reports.append(json.loads(lines[-1].removeprefix('ROSTER_MOTION_REPORT ')))
    if result.returncode or not lines:
        failures.append({'hero': hero, 'output': result.stdout[-2000:], 'error': result.stderr[-3000:]})
        print(f'FAIL {hero}: {result.stderr[-1800:]}')
    else:
        print(f'PASS {hero}: real skeleton, kit timing, source contacts, equipment weights, finite skinned geometry and frame-rate independent dodge')
args.report.write_text(json.dumps({'reports': reports, 'failures': failures}, indent=2)+'\n')
print(f'CPU report: {args.report}')
print('These measurements do not validate materials, lighting, performance on a GPU or artistic quality.')
raise SystemExit(bool(failures))
