"""Measured Lame locomotion on the real Three.js skeleton, with no WebGL by default.

--unit-only exercises the metadata/controller contract while the GLB is being
authored. The default requires the calibrated production GLB. --integration
also opens the built game in Chromium and compares actual keyboard/joystick.
The numeric report is evidence about timing/contacts, not an artistic verdict.
"""
from pathlib import Path
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--unit-only', action='store_true')
parser.add_argument('--integration', action='store_true')
args = parser.parse_args()

NODE = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
global.window=global;global.self=global;global.THREE=require('./vendor/three.min.js');
vm.runInThisContext(fs.readFileSync('vendor/three-addons.js','utf8'));
global.player={root:new THREE.Group(),legacyParts:[]};global.scene=new THREE.Scene();scene.add(player.root);
global.hero='lame';global.aim=0;global.t=0;global.campaign={trials:{forge:{carrying:false}}};
global.enemies=[];global.state='playing';global.refineHeroMaterials=()=>{};
global.moveEntity=(actor,dx,dz)=>{actor.x+=dx;actor.z+=dz;};global.trialActive=()=>true;
global.p={};
for(const file of ['roster.js','lame-motion.js','avatar-kinematics.js','authored-avatar.js','blade-contact.js','dynamics.js'])vm.runInThisContext(fs.readFileSync('src/'+file,'utf8'),{filename:file});
vm.runInThisContext('updateBladeTrail=()=>{};');

// Loading geometry and animation needs no renderer. Ignore the material/image
// data here; this is explicitly not a texture, shader, or visual-quality test.
const raw=fs.readFileSync('assets/characters/lame.glb'),len=raw.readUInt32LE(12),doc=JSON.parse(raw.subarray(20,20+len)),bin=raw.subarray(20+len);
for(const mesh of doc.meshes)for(const primitive of mesh.primitives)delete primitive.material;
delete doc.materials;delete doc.textures;delete doc.images;
let json=Buffer.from(JSON.stringify(doc));json=Buffer.concat([json,Buffer.alloc((4-json.length%4)%4,32)]);
const header=Buffer.from(raw.subarray(0,20));header.writeUInt32LE(20+json.length+bin.length,8);header.writeUInt32LE(json.length,12);
const packed=Buffer.concat([header,json,bin]);
const source=packed.buffer.slice(packed.byteOffset,packed.byteOffset+packed.length);
new RoyaumesGLTFLoader().parse(source,'',gltf=>{
try{
 global.a=makeHeroAvatar(gltf.scene,gltf.animations,'lame');
 vm.runInThisContext('avatarRuntime.current=a;avatarRuntime.heroes.lame=a;avatarRuntime.status="ready";');
 const unitOnly=process.argv.includes('--unit-only'),actual=!!a.motionCalibration;
 if(!unitOnly)assert(actual,'Production GLB has no valid motionCalibration; use --unit-only only during authoring');
 const fixture={version:1,units:'model',gaits:{walk:{cycleDistance:1.4,contacts:{L:[[.9,.3]],R:[[.4,.8]]}},run:{cycleDistance:4.8,contacts:{L:[[0,.2]],R:[[.5,.7]]}}},dodge:{distance:1.6,duration:.4},attacks:{attack1:{duration:.93,hitAt:.13,activeEnd:.25,travel:.5},attack2:{duration:1,hitAt:.8,activeEnd:.3,travel:1},attack3:{duration:2,hitAt:.4,activeEnd:.6,travel:0}}};
 const fake=new THREE.Group();fake.userData.motionCalibration=JSON.stringify(fixture);
 const parsed=readMotionCalibration(fake,'lame');assert(parsed&&parsed.attacks.attack1&&!parsed.attacks.attack2&&parsed.attacks.attack3.travel===0);
 assert.strictEqual(readMotionCalibration(fake,'rempart'),null);
 assert(motionContactAt(parsed.gaits.walk,'L',.95));assert(motionContactAt(parsed.gaits.walk,'L',.1));assert(!motionContactAt(parsed.gaits.walk,'L',.5));
 fake.userData.motionCalibration='{';assert.strictEqual(readMotionCalibration(fake,'lame'),null);
 if(unitOnly)a.motionCalibration=parsed;

 const clean=()=>{Object.assign(p,{x:0,z:0,vx:0,vz:0,motionSpeed:0,shield:0,stagger:0,leap:0,dashT:0,dash:0,attack:null});delete p.dashElapsed;delete p.dashDuration;delete p.dashDistance;delete p.dashProfile;player.root.position.set(0,0,0);player.root.rotation.set(0,0,0);aim=0;t=0;resetAvatarPose();};
 clean();
 // Measure rendered boot vertices after skinning: ankle bone height alone is
 // not evidence that a sole touches the floor. The model's measured bind sole
 // has a 2.5 cm origin pad; a fixed non-animated wrapper removes that pad.
 const bootVertices={L:[],R:[]};a.root.traverse(mesh=>{if(!mesh.isSkinnedMesh)return;const indices=mesh.geometry.attributes.skinIndex,weights=mesh.geometry.attributes.skinWeight;for(const side of ['L','R']){const vertices=[];for(let i=0;i<indices.count;i++){let influence=0;for(let k=0;k<4;k++)if(mesh.skeleton.bones[indices.getComponent(i,k)]?.name==='foot'+side)influence+=weights.getComponent(i,k);if(influence>.4)vertices.push(i);}if(vertices.length)bootVertices[side].push({mesh,vertices});}});
 function bootSoles(){scene.updateMatrixWorld(true);a.root.traverse(mesh=>{if(mesh.isSkinnedMesh)mesh.skeleton.update();});return ['L','R'].map(side=>{let minimum=Infinity;for(const {mesh,vertices}of bootVertices[side])for(const i of vertices)minimum=Math.min(minimum,mesh.getVertexPosition(i,new THREE.Vector3()).applyMatrix4(mesh.matrixWorld).y);return minimum;});}
 const restSoles={};for(const name of ['idle','guard']){clean();playAvatarAction(a,name,0,true);playLowerAction(a,name,0,true);const samples=[],offset=a.visualRoot.position.y,step=a.actions[name].getClip().duration/120;for(let frame=0;frame<=120;frame++){a.mixer.update(step);updateBodyDynamics(a,p,step);updateAvatarKinematics(a,step,0,p,'lame',0);samples.push(bootSoles());assert.strictEqual(a.root.position.y,0,'The animated GLTF root must not accumulate an origin correction');assert.strictEqual(a.visualRoot.position.y,offset,'The visual origin must stay fixed across poses');}restSoles[name]=[0,1].map(side=>[Math.min(...samples.map(s=>s[side])),Math.max(...samples.map(s=>s[side]))]);if(!unitOnly){assert(a.visualRoot!==a.root&&a.root.parent===a.visualRoot);assert(restSoles[name].flat().every(y=>y>-.015&&y<.015),'Actual idle/guard boot soles must remain within 1.5 cm of the floor');}}
 clean();
 const oldFrequency=5.5/1.5;
 const curve=Array.from({length:301},(_,i)=>{const speed=.2+i*(5.5-.2)/300,m=motionGaitMix(a,speed);return{speed,frequency:m.frequency,weight:m.weight};});
 const maxJump=Math.max(...curve.slice(1).map((item,i)=>Math.abs(item.frequency-curve[i].frequency)));
 assert(maxJump<.05,'Walk/run cadence must not jump at a gait-selection threshold');
 assert(curve.every(v=>Number.isFinite(v.frequency)&&v.frequency>=0&&v.weight>=0&&v.weight<=1));
 const selectedRunRate=motionPlaybackRate(a,'run',5.5);
 if(!unitOnly){assert(selectedRunRate>=.7&&selectedRunRate<=1.3,'Source run style must suit full-input speed; do not hide mismatch with a timescale cap');for(const name of ['walk','run'])if(a.motionCalibration.gaits[name].duration)assert(Math.abs(a.actions[name].getClip().duration-a.motionCalibration.gaits[name].duration)<.002,'Export must not add a blank frame to the measured source cycle');}

 const dodges=[];
 for(const hz of [30,60,120]){clean();p.dx=1;p.dz=0;const cfg=beginDodgeMotion(p,'lame',a);for(let i=0;i<Math.ceil(cfg.duration*hz)+2;i++){p.dashT=Math.max(0,p.dashT-1/hz);advanceHeroMotion(1/hz);}dodges.push(p.x);assert(Math.abs(p.x-cfg.distance)<1e-9);}
 clean();p.dx=-1;p.dz=0;beginDodgeMotion(p,'lame',a);const dodge=lameDodgeClip(a,p,0);p.dashElapsed=.1;assert.strictEqual(lameDodgeClip(a,p,Math.PI),dodge,'Aim changes must not switch dodge clips during a gesture');
 const cfg=actorDodgeConfig(p),first=dodgeTravel(0,cfg.duration*.05,cfg),middle=dodgeTravel(cfg.duration*.45,cfg.duration*.5,cfg);assert(first<middle*.25,'Step dodge needs a finite anticipation, rather than instant peak speed');
 assert(Math.abs(dodgeTravel(0,.28)-4.2)<1e-12,'Other heroes keep exact legacy dodge integration');
 assert.strictEqual(motionSpeedScale(null,'rempart',p,0),1);
 clean();const originalCalibration=a.motionCalibration;a.motionCalibration=parsed;
 attackAdvance({melee:true,combo:3,elapsed:.4,hitAt:.4,aim:0},0);assert.strictEqual(p.z,0,'An authored stationary attack must not receive the legacy lunge');
 attackAdvance({melee:true,combo:1,elapsed:.13,hitAt:.13,aim:0},0);assert(Math.abs(p.z+.5*motionModelScale(a))<1e-9,'Attack travel is scaled from model to world once');a.motionCalibration=originalCalibration;

 const movement=[];
 // Capture the authored feet before the bounded post-animation correction.
 const original=updateCalibratedFeet;global.currentFrame=null;
 vm.runInThisContext('var motionMeasurementHook=null;');
 global.captureCalibrated=(avatar,dt,speed,actor,heading,special,travel)=>{
  const before=avatar.legs.map(l=>l.end.getWorldPosition(new THREE.Vector3()));
  original(avatar,dt,speed,actor,heading,special,travel);
  currentFrame={before,after:avatar.legs.map(l=>l.end.getWorldPosition(new THREE.Vector3()))};
 };
 vm.runInThisContext('updateCalibratedFeet=captureCalibrated;');
 for(const hz of [30,60,120])for(const input of [.2,.45,.7,1]){
  clean();const dt=1/hz,groups=[[],[]],finished=[],coreGroups=[[],[]],coreFinished=[],samples=[];let startSerial=0,maxCorrection=0,maxBeforeVertical=-Infinity,minBeforeVertical=Infinity,released=0,contacts=0,upperRunWeight=0;
  for(let frame=0;frame<hz*9;frame++){
   p.vx=0;p.vz=-5.5*input;const old=p.z;advanceHeroMotion(dt);p.motionSpeed=Math.abs(p.z-old)/dt;player.root.position.set(p.x,0,p.z);t+=dt;updateRigAvatar(dt);
   if(frame===hz)startSerial=a.motionFootstepSerial;if(frame<hz)continue;
   for(let legIndex=0;legIndex<2;legIndex++){
    const leg=a.legs[legIndex],pos=leg.end.getWorldPosition(new THREE.Vector3()),before=currentFrame?.before[legIndex];
    if(before){maxBeforeVertical=Math.max(maxBeforeVertical,before.y);minBeforeVertical=Math.min(minBeforeVertical,before.y);}
    maxCorrection=Math.max(maxCorrection,leg.motionCorrection||0);
    if(leg.motionContact){contacts++;if(leg.motionReleased)released++;groups[legIndex].push(pos.clone());}
    else if(groups[legIndex].length){finished.push(groups[legIndex]);groups[legIndex]=[];}
    if(leg.motionContact&&!leg.motionReleased&&leg.motionWeight>.75)coreGroups[legIndex].push(pos.clone());
    else if(coreGroups[legIndex].length){coreFinished.push(coreGroups[legIndex]);coreGroups[legIndex]=[];}
   }
   upperRunWeight=a.motionBlendUpper?.weight||0;samples.push({speed:p.motionSpeed,phase:a.motionPhase,runWeight:upperRunWeight});
  }
  const drift=finished.filter(g=>g.length>1).map(g=>Math.hypot(g.at(-1).x-g[0].x,g.at(-1).z-g[0].z));
  const coreDrift=coreFinished.filter(g=>g.length>1).map(g=>Math.hypot(g.at(-1).x-g[0].x,g.at(-1).z-g[0].z));
  const speed=samples.reduce((sum,s)=>sum+s.speed,0)/samples.length,mix=motionGaitMix(a,speed),steps=(a.motionFootstepSerial-startSerial)/8;
  assert(maxCorrection<=.14001,'Post-animation IK must stay within its correction budget');
  assert(Math.abs(steps-2*mix.frequency)<.4,'Footstep events must follow the normalized two-contact cycle');
  assert(maxBeforeVertical-minBeforeVertical>.035,'Swing feet must retain vertical source motion');
  if(!unitOnly){assert(drift.length>=8&&Math.max(...drift)<.05,'Production planted feet must stay within 5 cm over the actual annotated support');assert(released/Math.max(1,contacts)<.05,'The correction must not appear stable only because most supports were discarded');assert(coreDrift.length>=4&&Math.max(...coreDrift)<.025,'The core of support must remain stable within 2.5 cm');}
  movement.push({hz,input,speed,stepsPerSecond:steps,expectedSteps:2*mix.frequency,runWeight:upperRunWeight,walkRate:a.lowerActions.walk.getEffectiveTimeScale(),runRate:a.lowerActions.run.getEffectiveTimeScale(),maxCorrection,maxContactDrift:drift.length?Math.max(...drift):null,meanContactDrift:drift.length?drift.reduce((x,y)=>x+y,0)/drift.length:null,maxCoreSupportDrift:coreDrift.length?Math.max(...coreDrift):null,contactGroups:drift.length,coreSupportGroups:coreDrift.length,releasedFraction:contacts?released/contacts:0,swingHeight:maxBeforeVertical-minBeforeVertical});
 }
 // A moving full-body attack must keep the source legs, rather than walking IK.
 clean();p.vz=-2;p.motionSpeed=2;p.attack={melee:true,combo:1,elapsed:0,duration:a.actions.attack1.getClip().duration,hitAt:.2,aim:0};
 let attackCorrection=0;for(let i=0;i<30;i++){p.z-=.02;player.root.position.set(p.x,0,p.z);t+=1/120;updateRigAvatar(1/120);attackCorrection=Math.max(attackCorrection,...a.legs.map(l=>l.motionCorrection||0));assert.strictEqual(a.lowerState,'attack1');}
 assert.strictEqual(attackCorrection,0,'Lame attack feet must follow the full-body source pose');
 if(a.motionCalibration.attacks.attack1){p.attack.elapsed=a.motionCalibration.attacks.attack1.activeEnd+.12;p.motionSpeed=2;let recoverySupport=0;for(let i=0;i<90;i++){p.z-=2/120;player.root.position.set(p.x,0,p.z);t+=1/120;updateRigAvatar(1/120);assert(['walk','run'].includes(a.lowerState),'Recovery must release the legs while the attack upper-body pose continues');assert.strictEqual(a.state,'attack1');recoverySupport=Math.max(recoverySupport,a.feetWeight);}assert(recoverySupport>.5,'Recovery locomotion must regain its contact correction');const attackLowerTime=a.lowerActions.attack1.time;p.motionSpeed=0;for(let i=0;i<15;i++)updateRigAvatar(1/120);assert.strictEqual(a.lowerState,'idle','Stopping during recovery must not replay the attack legs');assert(a.lowerActions.attack1.time>=attackLowerTime,'The attack lower layer must not rewind on a recovery stop');p.motionSpeed=2;for(let i=0;i<15;i++){p.z-=2/120;player.root.position.set(p.x,0,p.z);updateRigAvatar(1/120);}assert(['walk','run'].includes(a.lowerState),'Recovery must allow moving again after a stop');}
 clean();const pose=(speed)=>{p.motionSpeed=speed;p.z-=speed/120;player.root.position.set(p.x,0,p.z);t+=1/120;updateRigAvatar(1/120);};
 pose(0);pose(2);assert.strictEqual(a.state,'start');assert(['walk','run'].includes(a.lowerState),'A moving anticipation must not freeze the legs');
 for(let i=0;i<120;i++)pose(2);for(let i=0;i<120;i++)pose(0);
 assert(!a.motionBlendLower&&!a.motionBlendUpper,'Guard must release both locomotion blends');
 for(let i=0;i<120;i++)pose(2);
 for(const actions of [a.actions,a.lowerActions])assert(actions.walk.enabled&&actions.run.enabled,'Faded gait siblings must reactivate on the next departure');
 assert(Math.abs(a.lowerActions.walk.getEffectiveWeight()+a.lowerActions.run.getEffectiveWeight()-1)<1e-6);
 console.log('MOTION_REPORT '+JSON.stringify({actualAsset:actual&&!unitOnly,modelSha256:require('crypto').createHash('sha256').update(raw).digest('hex'),restSoles,oldStepsPerSecond:2*oldFrequency,maxCadenceIncrement:maxJump,runRateAt5_5:selectedRunRate,dodgeDistances:dodges,movement,attackCorrection}));
}catch(e){console.error(e.stack);process.exitCode=1;}
},error=>{console.error(error);process.exitCode=1;});
'''

command = ['node', '-'] + (['--unit-only'] if args.unit_only else [])
result = subprocess.run(command, cwd=ROOT, input=NODE, text=True, capture_output=True)
if result.returncode:
    print(result.stdout)
    print(result.stderr)
    raise SystemExit(result.returncode)
report_line = next(line for line in result.stdout.splitlines() if line.startswith('MOTION_REPORT '))
report = json.loads(report_line.removeprefix('MOTION_REPORT '))
print(json.dumps(report, indent=2))

if args.integration:
    from functools import partial
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread
    from playwright.sync_api import sync_playwright

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *items):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'docs')))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
            page = browser.new_page(viewport={'width': 1100, 'height': 760})
            page.add_init_script('requestAnimationFrame=()=>0')
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=lame')
            page.wait_for_function('avatarRuntime.status==="ready"', polling=50)
            page.click('#start')
            measured = page.evaluate('''()=>{
             soundOn=false;p.inv=999;enemies.forEach(e=>e.dead=true);enemies=[];
             world.onGround=()=>true;obstacles=[];world.obstacles=obstacles;
             function travel(kind){clearInputs();resetHeroAt(0,24);aim=0;
              if(kind==='keyboard')keys.add('w');else joy.y=-1;
              const samples=[];for(let i=0;i<240;i++){update(1/120);if(i>120)samples.push({speed:p.motionSpeed,rate:avatarRuntime.current.lowerAction.getEffectiveTimeScale()});}
              clearInputs();return{z:p.z,samples};}
             return{keyboard:travel('keyboard'),joystick:travel('joystick')};
            }''')
            assert abs(measured['keyboard']['z'] - measured['joystick']['z']) < .02, measured
            page.evaluate('camera.position.set(p.x+3,3,p.z+5);camera.lookAt(p.x,1,p.z);renderer.render(scene,camera)')
            page.screenshot(path='/tmp/lame-motion-quality.png')
            assert not errors, errors
            browser.close()
        print('PASS integration: actual keyboard/joystick displacement parity; capture /tmp/lame-motion-quality.png')
    finally:
        server.shutdown()
        server.server_close()

print('PASS CPU: metadata, continuous gait cadence, bounded source-foot correction, footstep phase, full-body attack legs and calibrated dodge. Artistic review remains separate.' if not args.unit_only else 'PASS unit contract only; production animation measurements still required.')
