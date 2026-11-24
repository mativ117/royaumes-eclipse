"""Test thin-cover tunnelling, bounded windup steering and target stability."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
program=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');const context={p:{x:0,z:0},avatarRuntime:{current:{motionCalibration:{}}},distance:(a,b)=>Math.hypot(a.x-b.x,a.z-b.z),wrap:x=>Math.atan2(Math.sin(x),Math.cos(x)),blocked:(x,z)=>Math.abs(x-.26)<.055&&Math.abs(z)<.3};vm.createContext(context);vm.runInContext(fs.readFileSync(process.argv[1]+'/src/combat-control.js','utf8'),context);
assert(!context.blocked(.533,0));assert(context.projectileBlockedAlong(0,0,.533,0),'A 32u/s shot must not cross thin cover between simulation samples');assert(!context.projectileBlockedAlong(0,1,.533,1));
const actor={attack:{melee:true,elapsed:0,hitAt:.4,aim:0}};for(let i=0;i<30;i++)context.steerAttackPreparation(actor,Math.PI/2,1/60);assert(actor.attack.aim<=.650001&&actor.attack.aim>.6);const angle=actor.attack.aim;actor.attack.elapsed=.39;context.steerAttackPreparation(actor,-1,1);assert(actor.attack.aim===angle,'The active strike must retain its announced direction');
const a={x:0,z:4},b={x:0,z:4.1};assert(context.stableCombatTarget([a,b])===a);b.z=3.9;assert(context.stableCombatTarget([b,a])===a,'Tiny distance changes must not flip touch aim');b.z=2;assert(context.stableCombatTarget([b,a])===b);assert(context.stableCombatTarget([])===null);
console.log('PASS: thin-cover swept checks, bounded preparation steering, locked contact direction and stable touch target.');
'''
subprocess.run(['node','-e',program,str(ROOT)],check=True)
