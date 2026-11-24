"""Real Three.js gate geometry, clearance and anti-crush; no WebGL renderer.

--integration also checks the current game's solidActive collision hook.
The source thresholds are read from world.js, including the mirrored wide ones.
"""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=process.argv[1],THREE=require(root+'/vendor/three.min.js');
const nativeSource=fs.readFileSync(root+'/src/world.js','utf8'),fixtures=new Map();
for(const match of nativeSource.matchAll(/obstacle\(([^\n;]*?'(?:pact|ritual-entry|seals|boss)')\)/g))for(const side of [-1,1]){
 const collect={side,m:{bronze:{}},obstacle:(x,z,w,d,h,_material,gate)=>{fixtures.set([x,z,w,d,h,gate].join('/'),{x,z,w,d,h,gate});}};
 vm.runInNewContext('obstacle('+match[1]+')',collect);
}
assert(fixtures.size>=8,'Exercise the actual source thresholds, not a single toy gate');
const scene=new THREE.Scene(),worldRoot=new THREE.Group();scene.add(worldRoot);
const obstacles=[...fixtures.values()].map(q=>{const mesh=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshBasicMaterial({transparent:true,opacity:.18}));mesh.scale.set(q.w,q.h,q.d);mesh.position.set(q.x,q.h/2,q.z);worldRoot.add(mesh);return{...q,mesh};});
const closed=new Map(obstacles.map(o=>[o.gate,true]));
const context={THREE,console,Math,Number,world:{obstacles},boxGeo:new THREE.BoxGeometry(1,1,1),p:{x:0,z:30},localParty:[],campaignGateClosed:key=>closed.get(key)};
vm.createContext(context);
vm.runInContext(fs.readFileSync(root+'/src/staging.js','utf8'),context);
vm.runInContext(fs.readFileSync(root+'/src/art-direction.js','utf8'),context);
vm.runInContext('artDirection={gates:[]};sculptGates()',context);
const gates=vm.runInContext('artDirection.gates',context),report=[];
function bounds(o){
 scene.updateMatrixWorld(true);const box=new THREE.Box3(),matrix=new THREE.Matrix4(),composed=new THREE.Matrix4();
 for(const mesh of o.craftedGate.panels)for(let i=0;i<mesh.count;i++){mesh.getMatrixAt(i,matrix);composed.multiplyMatrices(mesh.matrixWorld,matrix);box.union(mesh.geometry.boundingBox.clone().applyMatrix4(composed));}
 return box;
}
for(const obstacle of gates){
 const gate=obstacle.craftedGate,states=[];assert(gate.moduleWidth<=3.2+1e-9);assert(gate.hinges.length===2&&gate.panels.length<=2,'Two instanced batches preserve the draw-call budget');
 assert(obstacle.mesh.scale.equals(new THREE.Vector3(1,1,1)));assert(gate.panels.reduce((n,m)=>n+m.count,0)===gate.moduleCount);
 for(const amount of [0,.5,1]){
  context.setCraftedGateOpen(gate,amount);const b=bounds(obstacle),size=b.getSize(new THREE.Vector3());
  assert(Math.abs(size.x-obstacle.w)<2e-5,'Open panels must not widen their threshold');
  assert(size.z<=.131,'Opening must not turn the corridor width into a deep swinging wall');
  assert(Math.abs(size.y-gate.height)<2e-5);assert(Math.abs(b.min.y-gate.clearance)<2e-5,'Headroom must match the lowest actual vertex');
  assert(Math.abs(b.min.x-(obstacle.x-obstacle.w/2))<2e-5&&Math.abs(b.max.x-(obstacle.x+obstacle.w/2))<2e-5);
  assert(gate.passable===(b.min.y>=gate.requiredClearance));
  assert(gate.hinges.every(group=>group.rotation.y===0),'No long swinging leaves remain');
  assert(gate.panels.every(m=>m.castShadow===!gate.passable));
  assert(gate.panelRoot.visible===(amount<.995));
  for(const panel of gate.panels){const normals=panel.geometry.attributes.normal.array;assert(Array.from(normals).every(Number.isFinite));assert(panel.material.userData.surface==='metal'&&panel.material.metalness>.5&&!panel.material.map,'Original gate metal must not inherit a stretched floor texture');}
  states.push({open:amount,width:size.x,height:size.y,depth:size.z,clearance:gate.clearance,passable:gate.passable,panelsVisible:gate.panelRoot.visible});
 }
 report.push({gate:obstacle.gate,x:obstacle.x,z:obstacle.z,width:obstacle.w,moduleCount:gate.moduleCount,moduleWidth:gate.moduleWidth,oldLeafDepthAt90Degrees:obstacle.w/2,states});
 context.setCraftedGateOpen(gate,0);gate.wasRequestedOpen=false;
}
// Standing next to a never-unlocked gate must not unlock the quest.
const first=gates.find(o=>o.gate==='pact'),gate=first.craftedGate;context.p.x=first.x;context.p.z=first.z;
for(let i=0;i<60;i++)context.updateCraftedGates(1/60);assert(gate.open===0&&!gate.passable&&!gate.heldForActor);
// Once legitimately open, a closing request cannot crush a body on the threshold.
closed.set('pact',false);for(let i=0;i<120;i++)context.updateCraftedGates(1/60);assert(gate.passable);
closed.set('pact',true);for(let i=0;i<120;i++)context.updateCraftedGates(1/60);assert(gate.passable&&gate.heldForActor);
context.p.z+=2;for(let i=0;i<180;i++)context.updateCraftedGates(1/60);assert(!gate.passable&&gate.open===0&&!gate.heldForActor);
// Companion/remote actor bodies receive the same protection.
closed.set('pact',false);for(let i=0;i<120;i++)context.updateCraftedGates(1/60);
closed.set('pact',true);context.localParty.push({x:first.x,z:first.z});for(let i=0;i<60;i++)context.updateCraftedGates(1/60);assert(gate.heldForActor&&gate.passable);context.localParty.length=0;
// Exponential opening is independent of the number of simulation frames.
const progress=[];closed.set('pact',false);
for(const hz of [30,60,120]){context.setCraftedGateOpen(gate,0);gate.wasRequestedOpen=false;for(let i=0;i<hz;i++)context.updateCraftedGates(1/hz);progress.push(gate.open);}
assert(Math.max(...progress)-Math.min(...progress)<1e-12);
// Crown/heavy-body geometry can be taller than the old 2.5-unit threshold.
// Weapon tips are deliberately absent: bodyHeight is authored without weapons.
context.avatarRuntime={current:{motionCalibration:{bodyHeight:3},root:{scale:{y:1}}}};
context.setCraftedGateOpen(gate,.75);context.updateCraftedGates(0);
assert(Math.abs(gate.requiredClearance-3.05)<1e-9&&!gate.passable,'A taller body must wait for actual headroom');
context.setCraftedGateOpen(gate,.8);assert(gate.passable,'The same body can pass once the bars are above its crown');
context.localParty.push({x:20,z:30,avatar:{motionCalibration:{bodyHeight:2.9},root:{scale:{y:1.2}}}});context.updateCraftedGates(0);assert(Math.abs(gate.requiredClearance-3.53)<1e-9&&!gate.passable,'Companion body scales also determine clearance');context.localParty.length=0;
context.avatarRuntime.current.motionCalibration.bodyHeight=4.5;context.updateCraftedGates(0);context.setCraftedGateOpen(gate,1);
assert(!gate.panelRoot.visible&&gate.passable,'Fully stored panels cannot leave an invisible collision for a tall future costume');
delete context.avatarRuntime;context.updateCraftedGates(0);
if(process.argv.includes('--integration')){
 const game=fs.readFileSync(root+'/src/game.js','utf8'),signature='function solidActive(',start=game.indexOf(signature);assert(start>=0);const begin=game.indexOf('{',start);let end=begin+1,level=1;for(;level;end++){if(game[end]==='{')level++;else if(game[end]==='}')level--;}
 vm.runInContext(game.slice(start,end),context);
 closed.set('pact',false);context.setCraftedGateOpen(gate,.2);assert(context.solidActive(first,false),'Quest unlock alone cannot remove a still-visible blocking panel');
 context.setCraftedGateOpen(gate,1);assert(!context.solidActive(first,false));
 closed.set('pact',true);gate.wasRequestedOpen=true;context.p.x=first.x;context.p.z=first.z;context.updateCraftedGates(1/60);assert(!context.solidActive(first,false),'Anti-crush visual opening and collision must agree');
 context.p.z+=2;for(let i=0;i<180;i++)context.updateCraftedGates(1/60);assert(context.solidActive(first,false));
}
console.log('GATE_REPORT '+JSON.stringify({thresholds:report,openingProgressAtOneSecond:progress,integration:process.argv.includes('--integration')}));
console.log('PASS: actual source gates retain their opening width, modules below3.2, constant shallow depth at0/.5/1, exact visible clearance, bounded draw calls, no overhead shadow after retraction, quest-safe anti-crush and30/60/120Hz opening.'+(process.argv.includes('--integration')?' Real collision hook also agrees.':' Collision hook integration remains to run.'));
'''

result = subprocess.run(['node', '-e', PROGRAM, str(ROOT)] + (['--integration'] if '--integration' in sys.argv else []), cwd=ROOT, text=True, capture_output=True)
if result.returncode:
    print(result.stdout)
    print(result.stderr)
    raise SystemExit(result.returncode)
for line in result.stdout.splitlines():
    if line.startswith('GATE_REPORT '):
        Path('/tmp/royaumes-gates-1.5.json').write_text(json.dumps(json.loads(line.removeprefix('GATE_REPORT ')), indent=2) + '\n')
    else:
        print(line)
