"""Bounded contact presentation, using real Three.js without GPU or a browser."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
NODE = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
global.THREE=require('./vendor/three.min.js');global.scene=new THREE.Scene();
global.camera=new THREE.PerspectiveCamera();camera.position.set(5,9,8);
global.localProfile={settings:{reduced:false}};global.quality='standard';
global.p={x:0,z:0,heroId:'lame',attack:{melee:true,aim:0}};global.hero='lame';
vm.runInThisContext(fs.readFileSync('src/combat-feedback-v17.js','utf8'));
const state=()=>vm.runInThisContext('combatFeedbackV17');
const active=()=>state().glow.active+state().chips.active;
const target={x:2,z:0,hp:80,type:'warden',root:new THREE.Group()};
assert(!combatFeedbackContactV17(target,80,p),'A miss, invulnerability or no HP delta cannot flash');
assert(!combatFeedbackContactV17(target,75,p),'Healing is not damage');
assert(!combatFeedbackContactV17(target,NaN,p),'Invalid contacts are refused');
assert(!state().root,'Rejected contacts do not even allocate render resources');
target.hp=50;const before=JSON.stringify({x:target.x,z:target.z,hp:target.hp,source:p});
assert(combatFeedbackContactV17(target,80,p,{kind:'melee'}));
assert(JSON.stringify({x:target.x,z:target.z,hp:target.hp,source:p})===before,'Presentation never changes gameplay');
const first=state().glow.pool.find(q=>q.life>0);assert(first.x<target.x&&Math.abs(first.y-1.16)<1e-8,'Contact sits on the incoming body surface');
updateCombatFeedbackV17(0);assert(state().root.children.length===2,'Exactly two fixed batches');
for(const batch of[state().glow,state().chips])assert(Array.from(batch.position.array).every(Number.isFinite));
clearCombatFeedbackV17();assert(active()===0&&state().root.visible===false);
assert(combatFeedbackBlockV17(target,p));assert(state().stats.blocks===1&&target.hp===50,'Real block feedback has no fabricated damage');

// Every hero uses the actual weapon sockets and the existing active interval.
clearCombatFeedbackV17();
const profiles=vm.runInThisContext('combatFeedbackProfilesV17');assert(Object.keys(profiles).length===11);
for(const id of Object.keys(profiles)){
 const root=new THREE.Group(),base=new THREE.Object3D(),tip=new THREE.Object3D();root.position.set(3,0,-2);root.add(base,tip);tip.position.set(0,1,-1);base.position.set(0,1,0);scene.add(root);
 const actor={x:3,z:-2,attack:{melee:true,combo:1,hitAt:.15,activeEnd:.30,duration:.5,elapsed:.14}},avatar={root,blade:tip,bladeBase:base,motionCalibration:{attacks:{attack1:{activeEnd:.3}}}};
 const count=active();combatFeedbackWeaponV17(actor,avatar,id);assert(active()===count,'No windup trail');
 actor.attack.elapsed=.17;combatFeedbackWeaponV17(actor,avatar,id);assert(active()===count,'First socket sample cannot fabricate a trajectory');
 tip.position.x+=.25;actor.attack.elapsed=.19;combatFeedbackWeaponV17(actor,avatar,id);assert(active()>count,'Actual tip movement produces a bounded trace');
 updateCombatFeedbackV17(.016);actor.attack.elapsed=.4;combatFeedbackWeaponV17(actor,avatar,id);assert(!state().weapons.has(actor),'Recovery releases its socket history');scene.remove(root);clearCombatFeedbackV17();
}
const shot={x:1,y:1.3,z:2,heroId:'rempart'};
assert(combatFeedbackProjectileV17(shot,.6,2,1.3));const trace=state().glow.pool.find(q=>q.life>0);
assert(Math.abs(trace.x-.8)<1e-8&&Math.abs(trace.length-.4)<1e-8&&trace.dx>.99,'Tracer follows only the segment actually travelled');
assert(!combatFeedbackProjectileV17(shot,-8,2,1.3),'Teleport/rift discontinuity is not drawn as a shot through the world');
clearCombatFeedbackV17();
for(let frame=0;frame<8;frame++){for(let i=0;i<24;i++)combatFeedbackProjectileV17(shot,.6,2,1.3);updateCombatFeedbackV17(0);}
assert(state().glow.active<72*.71,'Optional shot tails leave capacity for real contacts');
const contacts=state().stats.contacts;assert(combatFeedbackContactV17(target,80,p));assert(state().stats.contacts===contacts+1&&state().glow.pool.some(q=>q.life>0&&!q.optional));

// Sustained contacts cannot grow the pools, arrays or draw ranges.
clearCombatFeedbackV17();const glowGeometry=state().glow.geometry,chipGeometry=state().chips.geometry;
for(let frame=0;frame<100;frame++){
 for(let i=0;i<40;i++)combatFeedbackContactV17(target,80,p,{kind:i%2?'power':'projectile',material:i%3?'metal':'stone'});
 updateCombatFeedbackV17(.001);assert(state().glow.active<=72&&state().chips.active<=24);assert(state().glow.geometry.drawRange.count<=72*6&&state().chips.geometry.drawRange.count<=24*6);
}
assert(state().stats.dropped>0&&state().glow.geometry===glowGeometry&&state().chips.geometry===chipGeometry,'Excess is dropped, never allocated');
quality='light';updateCombatFeedbackV17(0);assert(state().glow.active<=36&&state().chips.active<=12,'Changing quality applies the smaller live budget');
localProfile.settings.reduced=true;updateCombatFeedbackV17(0);assert(active()<=26);
clearCombatFeedbackV17();assert(!combatFeedbackProjectileV17(shot,.6,2,1.3),'Reduced motion removes optional trajectory tails');
const sphere=new THREE.SphereGeometry(1,6,4),enemy={x:1,y:1.35,z:0,dx:1,dz:0,enemy:true,mesh:new THREE.Mesh(sphere,new THREE.MeshBasicMaterial({color:'red'}))};
combatFeedbackProjectileV17(enemy,.8,0,1.35);assert(enemy.mesh.geometry===state().arrow,'Enemy sphere becomes one shared small arrow even in reduced motion');
const forward=new THREE.Vector3(0,0,-1).applyQuaternion(enemy.mesh.quaternion);assert(forward.x>.999&&Math.abs(forward.z)<1e-8,'Arrow follows its real travelling direction');
sphere.dispose();enemy.mesh.material.dispose();
combatFeedbackContactV17(target,80,p,{kind:'melee'});const stationary=state().glow.pool.filter(q=>q.life>0).map(q=>[q,q.x,q.y,q.z]);updateCombatFeedbackV17(.03);
assert(stationary.every(([q,x,y,z])=>q.x===x&&q.y===y&&q.z===z),'Reduced contacts stay local and do not throw moving particles');
for(let i=0;i<80;i++)updateCombatFeedbackV17(1/60);assert(active()===0,'All effects expire without timers');
for(let i=0;i<20;i++){clearCombatFeedbackV17();initCombatFeedbackV17();assert(state().glow.geometry===glowGeometry);}
let disposed=0;for(const batch of[state().glow,state().chips]){batch.geometry.addEventListener('dispose',()=>disposed++);batch.mesh.material.addEventListener('dispose',()=>disposed++);}state().arrow.addEventListener('dispose',()=>disposed++);
disposeCombatFeedbackV17();disposeCombatFeedbackV17();assert(disposed===5&&!state().root&&scene.children.length===0,'Cleanup is complete and idempotent');
console.log('PASS combat feedback 1.7: accepted HP deltas only; eleven real socket paths; finite directional geometry; actual projectile segments; fixed budgets; reduced motion; quality switch; expiry and cleanup. CPU only.');
'''

result = subprocess.run(['node', '-'], cwd=ROOT, input=NODE, text=True, capture_output=True)
assert result.returncode == 0, result.stderr + result.stdout
print(result.stdout.strip())
