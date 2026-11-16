"""Moving fire must keep live legs, grounded feet, stable grip and recoil."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1100,'height':760});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content('<script>requestAnimationFrame=()=>0</script>'+(ROOT/'docs/index.html').read_text());page.click('#start');run=page.evaluate
 assert run('Object.values(avatarRuntime.heroes).every(a=>Object.values(a.actions).every(u=>u.getClip().tracks.every(t=>!a.lowerActions[u.getClip().name].getClip().tracks.some(l=>l.name===t.name))))'),'Upper and lower channels must be disjoint'
 run('soundOn=false;p.inv=999;enemies.forEach(e=>e.dead=true);enemies=[];resetHeroAt(-6,25);mouseAim=true;shooting=true;joy.x=1;')
 result=run('''var samples=[];for(let i=0;i<80;i++){update(1/60);const a=avatarRuntime.current;if(i>16)samples.push({upper:a.state,lower:a.lowerState,thigh:a.legs[0].upper.quaternion.toArray(),ground:Math.min(...a.legs.map(l=>l.end.getWorldPosition(new THREE.Vector3()).y)),grip:a.arms[1].end.getWorldPosition(new THREE.Vector3()).distanceTo(a.foregrip.getWorldPosition(new THREE.Vector3()))});}({moving:samples.filter(s=>s.upper==='shot'&&['walk','run'].includes(s.lower)).length,poses:new Set(samples.map(s=>s.thigh.map(n=>n.toFixed(2)).join(','))).size,maxGround:Math.max(...samples.map(s=>s.ground)),maxGrip:Math.max(...samples.map(s=>s.grip))})''')
 assert result['moving']>50 and result['poses']>20,result
 assert result['maxGround']<.20,result
 assert result['maxGrip']<.07,result
 # A foot in stance should stay substantially steadier than the translating body.
 run('shooting=false;joy.x=0;resetHeroAt(-6,25);p.motionSpeed=1.8;aim=0;var planted=[];')
 result=run('''for(let i=0;i<90;i++){p.x+=.03;player.root.position.set(p.x,0,p.z);player.root.rotation.set(0,0,0);updateRigAvatar(1/60);const a=avatarRuntime.current,l=a.legs[0];if(a.feetWeight>.98&&l.lastPhase>.08&&l.lastPhase<.3)planted.push({cycle:Math.floor(a.stepPhase),x:l.end.getWorldPosition(new THREE.Vector3()).x});}var cycles=[...new Set(planted.map(s=>s.cycle))];({count:planted.length,drift:Math.max(...cycles.map(c=>{const xs=planted.filter(s=>s.cycle===c).map(s=>s.x);return Math.max(...xs)-Math.min(...xs)}))})''')
 assert result['count']>5 and result['drift']<.08,result
 # Exercise forward, backward and both strafes while the torso continues to aim.
 result=run('''var directionChecks=[];for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1],[.707,.707],[-.707,-.707]]){resetHeroAt(-6,25);p.motionSpeed=2;aim=0;p.attack={melee:false,elapsed:.1,duration:.28,hitAt:.07,aim:0};for(let i=0;i<45;i++){p.x+=dx/30;p.z+=dz/30;player.root.position.set(p.x,0,p.z);player.root.rotation.set(0,0,0);updateRigAvatar(1/60);if(i>20){const a=avatarRuntime.current;directionChecks.push({ground:Math.min(...a.legs.map(l=>l.end.getWorldPosition(new THREE.Vector3()).y)),grip:a.arms[1].end.getWorldPosition(new THREE.Vector3()).distanceTo(a.foregrip.getWorldPosition(new THREE.Vector3()))});}}}({maxGround:Math.max(...directionChecks.map(s=>s.ground)),maxGrip:Math.max(...directionChecks.map(s=>s.grip))})''')
 assert result['maxGround']<.20 and result['maxGrip']<.07,result
 assert run('new THREE.Vector3(0,1,0).applyQuaternion(avatarRuntime.current.muzzle.getWorldQuaternion(new THREE.Quaternion())).dot(new THREE.Vector3(0,0,-1))>.98'),'Barrel and flash axis must remain aligned with the shot direction'
 run('resetHeroAt(0,25);p.motionSpeed=0;p.shot=0;beginAttack();updateRigAvatar(.06);var bolt=avatarBone(avatarRuntime.current,"bolt"),boltStart=bolt.position.clone();updateRigAvatar(.025)')
 assert run('bolt.position.distanceTo(boltStart)>.01'),'Sliding breech must respond to the shot'
 run('cancelAttack();p.dash=0;dash();updateRigAvatar(.02)');assert run('avatarRuntime.current.state==="dash"&&avatarRuntime.current.lowerState==="dash"&&avatarRuntime.current.feetWeight===0')
 run('resetHeroAt(0,25);hero="voltigeur";applyHero();p.motionSpeed=0;aim=0;p.shot=0;beginAttack();updateAttack(.14);updateRigAvatar(.14);var bladeStart=avatarRuntime.current.blade.getWorldPosition(new THREE.Vector3());updateAttack(.09);updateRigAvatar(.09)')
 assert run('avatarRuntime.current.blade.getWorldPosition(new THREE.Vector3()).distanceTo(bladeStart)>.4'),'Blade must sweep through space during contact'
 run('cancelAttack();resetHeroAt(0,25)');assert run('avatarRuntime.current.lowerState==="idle"&&avatarRuntime.current.feetWeight===0&&avatarRuntime.current.weaponWeight===0')
 assert not errors,errors
 b.close()
print('PASS: disjoint animation layers, moving rifle fire with live legs, grounded stance, planted foot stability, two-handed grip, breech recoil, dodge override, blade sweep and reset.')
