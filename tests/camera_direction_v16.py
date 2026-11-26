"""Actual camera projection and bounded solo/party behavior, CPU Three.js only."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
code=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
global.THREE=require('./vendor/three.min.js');vm.runInThisContext(fs.readFileSync('src/camera-direction-v16.js','utf8'));
global.scene=new THREE.Scene();global.camera=new THREE.PerspectiveCamera(49,1.5,.1,180);
global.camDesired=new THREE.Vector3();global.cameraTarget=new THREE.Vector3();global.cameraLook=new THREE.Vector3();
global.p={x:0,z:0,vx:0,vz:0};global.player={root:new THREE.Group()};global.avatarRuntime={current:{motionCalibration:{bodyHeight:2.3},root:{scale:{y:1.07}}}};
global.motionModelScale=a=>a.root.scale.y;global.innerWidth=1200;global.innerHeight=800;global.localProfile={settings:{reduced:false}};global.state='playing';global.localParty=[];global.campaign={bossAwake:false};
global.distance=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);global.trialActive=()=>true;global.shadeVulnerable=()=>true;global.clearStrikeLine=()=>true;global.cameraVisibleTarget=()=>true;
global.partyCameraCenter=()=>({x:2,z:-2,radius:1});global.enemies=[];
const cases=[];
for(const aspect of [.462,1.5,2.16])for(const height of[2.8,6])for(const [x,z]of[[0,-6],[4,-5],[-4,2],[1,4]]){
 const focus={x,z};const f=cameraFramingV16(p,focus,aspect<1,1,aspect,height),c=new THREE.PerspectiveCamera(49,aspect,.1,180);c.position.set(f.position.x,f.position.y,f.position.z);c.lookAt(f.look.x,f.look.y,f.look.z);c.updateMatrixWorld(true);
 let bound=0;for(const [body,h]of[[p,height],[focus,2.8]])for(const dx of[-.7,.7])for(const y of[0,h])for(const dz of[-.7,.7]){const q=new THREE.Vector3(body.x+dx,y,body.z+dz).project(c);assert(q.z>-1&&q.z<1,'Body clipped in depth');bound=Math.max(bound,Math.abs(q.x),Math.abs(q.y));}
 assert(bound<=.861,'Both bodies must remain framed '+bound);cases.push(bound);
}
const settled=[];
for(const hz of[30,60,120]){
 vm.runInThisContext('encounterCamera.mix=0;encounterCamera.focus=null;');enemies=[{x:1,z:-5,root:{visible:true},mode:'windup',type:'archer'}];camera.position.set(0,6.7,10.8);cameraLook.set(0,1.6,-5);
 for(let i=0;i<hz*3;i++)updateCameraDirectionV16(1/hz);
 settled.push(camera.position.clone());assert(vm.runInThisContext('encounterCamera.mix')>.99);assert(vm.runInThisContext('encounterCamera.fill.castShadow')===false);
}
assert(settled.every(v=>v.distanceTo(settled[1])<.015),'Unstable framing across time steps');
const first=enemies[0];enemies.push({x:1,z:-4.9,root:{visible:true},mode:'idle',type:'archer'});updateCameraDirectionV16(1/60);assert(vm.runInThisContext('encounterCamera.focus')===first,'Tiny range changes must not flip framing focus');
localProfile.settings.reduced=true;for(let i=0;i<180;i++)updateCameraDirectionV16(1/60);assert(vm.runInThisContext('encounterCamera.mix')<.001,'Reduced motion disables combat zoom');
localParty=[{}];updateCameraDirectionV16(.016);assert(Math.abs(camDesired.y-7.8)<1e-9&&Math.abs(camDesired.z-9.7)<1e-9,'Keep existing party/LAN frame');
assert(scene.children.filter(o=>o.isPointLight).length===1,'Do not leak lights');
console.log('PASS: 24 real projected body pairs, portrait/landscape and jump height, stable30/60/120Hz framing, target hysteresis, reduced motion, one unshadowed fill and unchanged party frame. CPU only.');
'''
subprocess.run(['node','-'],input=code,text=True,cwd=ROOT,check=True)
