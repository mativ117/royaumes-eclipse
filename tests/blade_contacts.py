"""Geometric contact regression, without a renderer: sweep, whiff, wall, timing and one hit."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
program=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');const THREE=require(process.argv[1]+'/vendor/three.min.js');
const c={THREE,console};vm.createContext(c);vm.runInContext(fs.readFileSync(process.argv[1]+'/src/blade-contact.js','utf8'),c);
const V=(x,y,z)=>new THREE.Vector3(x,y,z),body={a:V(0,.25,0),b:V(0,1.7,0),radius:.4};
assert(Math.abs(c.segmentDistanceSquared(V(-1,1,0),V(1,1,0),body.a,body.b))<1e-9);
assert(Math.abs(c.segmentDistanceSquared(V(2,1,0),V(3,1,0),body.a,body.b)-4)<1e-9);
assert(Math.abs(c.segmentDistanceSquared(V(0,2,0),V(0,2,0),V(0,0,0),V(0,1,0))-1)<1e-9);
assert(c.sweptBladeHits({base:V(-1,1,-.4),tip:V(-1,1,.4)},{base:V(1,1,-.4),tip:V(1,1,.4)},body),'Fast blade must not tunnel between fixed steps');
assert(!c.sweptBladeHits({base:V(-1,2.8,-.4),tip:V(-1,2.8,.4)},{base:V(1,2.8,-.4),tip:V(1,2.8,.4)},body),'Blade above creature must whiff');
let base=V(-.2,1,-.4),tip=V(.2,1,.4);const a={melee:true,combo:1,elapsed:.1,hitAt:.25,activeEnd:.45,duration:.8,aim:0};
c.hero='lame';c.p={x:0,z:0,attack:a};c.avatarRuntime={current:{root:{updateWorldMatrix(){}},hand:{getWorldPosition(o){return o.copy(base)}},blade:{getWorldPosition(o){return o.copy(tip)}},motionCalibration:{attacks:{attack1:{hitAt:.25,activeEnd:.45}}}}};
const enemy={x:0,z:0,hp:100,root:{scale:{y:1}}};c.enemies=[enemy];c.campaign={bossAwake:false};c.trialActive=()=>true;c.clearStrikeLine=()=>true;c.damage=(e,n)=>e.hp-=n;c.sparks=()=>{};c.moveEntity=()=>{};
c.resolveBladeContacts();assert(enemy.hp===100,'No damage before active contact');a.elapsed=.3;c.resolveBladeContacts();assert(enemy.hp===56,'Real intersection inside active window must hurt');c.resolveBladeContacts();assert(enemy.hp===56,'A swing cannot repeatedly damage the same target');
a.hitTargets.clear();a.elapsed=.5;c.resolveBladeContacts();assert(enemy.hp===56,'Recovery must not hurt');a.elapsed=.3;c.clearStrikeLine=()=>false;c.resolveBladeContacts();assert(enemy.hp===56,'A wall blocks the blade');
c.clearStrikeLine=()=>true;base=V(0,3,0);tip=V(1,3,0);a.bladeSample=null;c.resolveBladeContacts();assert(enemy.hp===56,'Near enemy is not enough without weapon contact');
console.log('PASS: swept 3D blade capsule, fast-swing tunneling, vertical whiff, active window, wall occlusion and one hit per target. No render-quality claim.');
'''
subprocess.run(['node','-e',program,str(ROOT)],check=True)
