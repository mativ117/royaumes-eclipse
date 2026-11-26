"""Actual creature rigs and fair, bounded native AI. CPU only, no renderer/network."""
from pathlib import Path
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
NODE=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
global.THREE=require('./vendor/three.min.js');global.window=global;global.self=global;
vm.runInThisContext(fs.readFileSync('vendor/three-addons.js','utf8'));
vm.runInThisContext(fs.readFileSync('src/creature-reference.js','utf8'));
vm.runInThisContext(fs.readFileSync('src/enemy-direction-v16.js','utf8'));
global.obstacles=[];global.scene=new THREE.Scene();global.enemies=[];global.localParty=[];global.p={x:0,z:-8,inv:0};global.t=0;
global.distance=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);global.solidActive=o=>!o.open;
global.collisionContact=(o,x,z,r)=>Math.abs(x-o.x)<o.w/2+r&&Math.abs(z-o.z)<o.d/2+r;
global.blocked=(x,z,r=.48)=>Math.abs(x)>30||Math.abs(z)>30||obstacles.some(o=>solidActive(o)&&collisionContact(o,x,z,r));
global.classLine=(a,b)=>{const n=Math.max(1,Math.ceil(distance(a,b)/.07));for(let i=1;i<n;i++)if(blocked(a.x+(b.x-a.x)*i/n,a.z+(b.z-a.z)*i/n,.04))return false;return true;};
global.moveEntity=(e,dx,dz,r=.48)=>{const n=Math.max(1,Math.ceil(Math.hypot(dx,dz)/.03));for(let i=0;i<n;i++){const x=e.x+dx/n,z=e.z+dz/n;if(!blocked(x,z,r)){e.x=x;e.z=z;}else{if(!blocked(x,e.z,r))e.x=x;if(!blocked(e.x,z,r))e.z=z;}}};
global.shadeVulnerable=e=>e.reveal>0||e.mode!=='idle';global.perceiveEnemy=()=>true;global.enemyTarget=()=>p;
global.playWorldSound=()=>{};global.hurt=()=>{};global.partyHurt=()=>{};global.effect=()=>{};
global.sphereGeo=new THREE.SphereGeometry(1,8,6);global.red=new THREE.MeshBasicMaterial();global.bullets=[];
global.mesh=(geo,material,x,y,z,sx,sy,sz)=>{const o=new THREE.Mesh(geo,material);o.position.set(x,y,z);o.scale.set(sx,sy,sz);scene.add(o);return o;};
global.projectileBlockedAlong=(x,z,tx,tz,r)=>classLine({x,z},{x:tx,z:tz})?null:{x:(x+tx)/2,z:(z+tz)/2};
function make(role,x=0,z=0){const a=makeEnemyTacticsV16(role);a.cooldown=0;return{x,z,type:role,hp:role==='archer'?80:120,reveal:1,mode:'idle',authoredEnemy:{ai:a,footprintHeading:0}};}
function env(extra={}){return{line:classLine,visible:()=>true,commit:()=>true,steer:enemyV16Steer,move:moveEntity,actors:()=>[],hit:()=>{},shoot:()=>{},tell:()=>{},...extra};}
const timing=[];
for(const hz of[30,60,120]){
 obstacles=[];const e=make('archer'),shots=[],target={x:0,z:-9};
 for(let i=0;i<hz*3;i++){if(i/hz>.70)target.x=6;stepEnemyTacticsV16(e,1/hz,target,env({shoot:(actor,angle)=>shots.push({time:actor.authoredEnemy.ai.clock,angle})}));}
 assert(shots.length===1,'Exactly one native arrow, not a stream');assert(shots[0].time>=1.1+2/30&&shots[0].time<=1.1+2/30+2/hz+.001,'Tell/release must precede contact');assert(Math.abs(shots[0].angle)<1e-9,'The last half of the tell locks direction, not live aim');timing.push({hz,...shots[0]});
}
obstacles=[{x:0,z:-4,w:2,d:.2}];{
 const e=make('archer'),target={x:0,z:-8};let shots=0,path=0;
 for(let i=0;i<240;i++){const old={x:e.x,z:e.z};stepEnemyTacticsV16(e,1/60,target,env({line:()=>false,shoot:()=>shots++}));path+=distance(e,old);assert(!blocked(e.x,e.z,.48),'Native cover steering crosses a wall');}
 assert(path>2&&shots===0,'Occluded shooter must seek an angle, without firing through cover');
}
const charges=[];
for(const hz of[30,60,120]){
 obstacles=[];const e=make('shade'),victim={x:0,z:-3.2},hits=[];
 for(let i=0;i<hz*2;i++)stepEnemyTacticsV16(e,1/hz,victim,env({actors:()=>[victim],hit:(a,n)=>hits.push(n),steer:()=>{}}));
 assert(Math.abs(e.authoredEnemy.ai.chargeTravel-4.4)<1e-8,'Charge distance must integrate exactly');assert(hits.length===1&&hits[0]===18,'One victim, one contact; unchanged damage');charges.push({hz,distance:e.authoredEnemy.ai.chargeTravel,hits:hits.length});
}
obstacles=[{x:0,z:-2,w:4,d:.2}];{
 const e=make('shade'),victim={x:0,z:-4};let hits=0;
 for(let i=0;i<120;i++)stepEnemyTacticsV16(e,1/60,victim,env({line:()=>true,actors:()=>[victim],hit:()=>hits++,steer:()=>{}}));
 assert(e.z>-1.5&&hits===0,'A solid sealed threshold stops the charge and its victim contact');
}
// Real oriented footprint: neither narrow pier nor a turn may sweep a tail through it.
const footprint={};{
 const e=make('shade');obstacles=[{x:.64,z:.1,w:.03,d:.6}];enemyV16Fold(e);assert(e.authoredEnemy.ai.folded===1,'Thin nearby pillar must immediately fold wings');assert(enemyV16FootprintLegal(e,0,0,0),'Folded core fits legally beside the thin pillar');
 obstacles=[{x:0,z:2.2,w:.3,d:.02}];enemyV16Move(e,0,1,.55);assert(e.z<.25,'Segment sweep must stop a long tail before the wall');footprint.tailStoppedAt=e.z;
 e.x=e.z=0;obstacles=[{x:1.4,z:0,w:.03,d:5}];const angle=enemyV16Turn(e,0,Math.PI/2);assert(angle<1.1&&enemyV16FootprintLegal(e,0,0,angle),'Rotation cannot push the tail through a wall');footprint.maximumTurn=angle;
}
async function load(role){
 const name=role==='archer'?'archer-thorn':'shade-manta',raw=fs.readFileSync('assets/creatures/'+name+'.glb'),size=raw.readUInt32LE(12),doc=JSON.parse(raw.subarray(20,20+size)),binary=raw.subarray(20+size);
 for(const m of doc.meshes)for(const p of m.primitives)delete p.material;delete doc.materials;delete doc.images;delete doc.textures;
 let data=Buffer.from(JSON.stringify(doc));data=Buffer.concat([data,Buffer.alloc((4-data.length%4)%4,32)]);const header=Buffer.from(raw.subarray(0,20));header.writeUInt32LE(20+data.length+binary.length,8);header.writeUInt32LE(data.length,12);const packed=Buffer.concat([header,data,binary]);
 return new Promise((resolve,reject)=>new RoyaumesGLTFLoader().parse(packed.buffer.slice(packed.byteOffset,packed.byteOffset+packed.length),'',resolve,reject));
}
function setup(role){const root=new THREE.Group(),robe=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial()),bar=new THREE.Sprite(new THREE.SpriteMaterial());root.add(robe,bar);scene.add(root);return{type:role,x:0,z:0,hp:role==='archer'?80:120,max:role==='archer'?80:120,root,robe,healthBar:bar,mode:'idle',timer:.1,reveal:1,flash:0,alert:10};}
function evaluate(e){scene.updateMatrixWorld(true);const box=new THREE.Box3();e.authoredEnemy.root.traverse(o=>{if(o.isSkinnedMesh){o.skeleton.update();for(let i=0;i<o.geometry.attributes.position.count;i++){const v=o.getVertexPosition(i,new THREE.Vector3()).applyMatrix4(o.matrixWorld);assert(v.toArray().every(Number.isFinite));box.expandByPoint(v);}}});return box;}
(async()=>{
 const models=[];obstacles=[];
 for(const role of['archer','shade']){
  const source=await load(role);global.asset=source;global.role=role;vm.runInThisContext('enemyDirectionV16.templates[role]={root:asset.scene,clips:Object.fromEntries(asset.animations.map(c=>[c.name,c]))};');
  const e=setup(role);assert(buildEnemyDirectionV16(e));const c=e.authoredEnemy;
  assert(c.clips.windup.duration===(role==='archer'?Math.fround(1.1):Math.fround(.9)),'Read actual source duration');
  assert(e.root.children.includes(c.root)&&!e.robe.visible,'Hide legacy anatomy after actual model succeeds');
  const other=setup(role);other.x=17.5;other.z=-20;other.root.position.set(other.x,0,other.z);assert(buildEnemyDirectionV16(other));if(role==='archer')for(let i=0;i<c.legs.length;i++)assert(c.legs[i].local.distanceTo(other.authoredEnemy.legs[i].local)<1e-7,'Nonzero spawn must not corrupt local bind metrics');const first=[];c.root.traverse(o=>{if(o.isBone)first.push(o);});other.authoredEnemy.root.traverse(o=>{if(o.isBone)assert(!first.includes(o),'Independent actor bones');});
  enterEnemyPhaseV16(c.ai,'windup',c.ai.windup);c.ai.elapsed=.7;e.mode='recover';e.timer=1.7;const beforeShots=bullets.length;updateEnemyDirectionV16(e,1/60,p);assert(c.ai.phase==='recover'&&c.ai.duration===1.7&&bullets.length===beforeShots,'An external power interruption must not revive the old attack');enterEnemyPhaseV16(c.ai,'idle',Infinity);c.ai.cooldown=99;e.mode='idle';
  const samples=[],open=[[],[]],stance=[];for(let i=0;i<120;i++){e.z-=1.8/60;e.root.position.set(e.x,0,e.z);poseEnemyDirectionV16(e,1/60);if(i%10===0)samples.push(evaluate(e).min.y);for(let j=0;j<c.legs.length;j++){const leg=c.legs[j];if(i>15&&leg.lastPhase>.08&&leg.lastPhase<.48)open[j].push(leg.end.getWorldPosition(new THREE.Vector3()));else if(open[j].length){if(open[j].length>2)stance.push(open[j]);open[j]=[];}}}
  assert(samples.every(Number.isFinite));
  const drift=stance.length?Math.max(...stance.map(s=>Math.hypot(s.at(-1).x-s[0].x,s.at(-1).z-s[0].z))):null;
  if(role==='archer'){assert(Math.min(...samples)>-.004,'Actual skinned archer toes must stay within4mm of the floor');assert(stance.length>=4&&drift<.05,'Actual core stance drift must stay below5cm '+JSON.stringify({groups:stance.length,drift}));}
  if(role==='shade'){c.ai.folded=1;for(const phase of['idle','windup','release','recover']){c.ai.phase=phase;c.ai.duration=c.clips[phase==='idle'?'idle':phase].duration;c.ai.elapsed=c.ai.duration*.7;poseEnemyDirectionV16(e,1/60);const box=evaluate(e);assert(Math.max(Math.abs(box.min.x-e.x),Math.abs(box.max.x-e.x))<.56,'Fold must remain narrow during the authored pose');}}
  enemyDirectionV16Hit(e,30);assert(c.ai.react>.2&&c.ai.reactLock>.4,'A real hit has a bounded visible reaction');e.hp=0;enemyDirectionV16Hit(e,80);assert(c.ai.phase==='death');assert(poseEnemyDirectionV16Fallen(e.root,.1));assert(c.deathClock===.1);
  const copies=new Map(c.materials.map(m=>[m,m.clone()]));assert(refreshEnemyDirectionV16FallMaterials(e,copies));assert(c.materials.every(m=>[...copies.values()].includes(m)),'Death fade updates live material references');
  const built=vm.runInThisContext('enemyDirectionV16.live.size');assert(disposeEnemyDirectionV16Root(e.root));assert(!disposeEnemyDirectionV16Root(e.root),'Cleanup idempotent');assert(vm.runInThisContext('enemyDirectionV16.live.size')===built-1);disposeEnemyDirectionV16Root(other.root);models.push({role,clips:Object.keys(c.clips),skinnedMinimumY:Math.min(...samples),stanceGroups:stance.length,maxStanceDrift:drift,isolatedBones:first.length});
 }
 assert(vm.runInThisContext('enemyDirectionV16.live.size')===0);
 console.log('ENEMY_DIRECTION_REPORT '+JSON.stringify({timing,charges,footprint,models}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
'''
r=subprocess.run(['node','-'],cwd=ROOT,input=NODE,text=True,capture_output=True)
lines=[s for s in r.stdout.splitlines() if s.startswith('ENEMY_DIRECTION_REPORT ')]
assert r.returncode==0 and lines,r.stderr+r.stdout
report=json.loads(lines[-1].removeprefix('ENEMY_DIRECTION_REPORT '))
Path('/tmp/enemy-direction-v16-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS CPU: source-timed locked arrow; cover flanking; finite 4.4m charge at30/60/120Hz, one18-damage contact and solid-gate stop; thin-pier wing fold, swept tail/turn clearance; both real skinned rigs, pose, independent bones, reaction, death fade references and cleanup. No GPU or artistic-quality claim.')
