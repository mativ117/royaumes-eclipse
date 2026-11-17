"""Actual creature GLB and runtime math, CPU only: no WebGL context or rendered FPS claim."""
from pathlib import Path
import base64,json,struct,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];model=(ROOT/'assets/creatures/obsidian-warden.glb').read_bytes();size=struct.unpack_from('<I',model,12)[0];gltf=json.loads(model[20:20+size]);proof=json.loads((ROOT/'assets/creatures/PROVENANCE.json').read_text())
assert len(gltf['materials'])==4 and len(gltf['skins'])>=1
assert all('bufferView' in image for image in gltf['images'])
assert hashlib.sha256(model).hexdigest()==proof['sha256']
html='<script>requestAnimationFrame=()=>0</script>'
for file in ['vendor/three.min.js','vendor/three-addons.js','src/creature-reference.js']:html+='<script>'+(ROOT/file).read_text()+'</script>'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu','--disable-software-rasterizer']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);run=p.evaluate
 run('encoded=>initCreatureReference({data:encoded})',base64.b64encode(model).decode());assert run('creatureReference.status==="ready"')
 run('''window.makeEnemy=function(type,x=0,z=0){const root=new THREE.Group(),legacy=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshStandardMaterial()),health=new THREE.Sprite();root.add(legacy,health);root.position.set(x,0,z);health.position.y=2.5;return{type,x,z,root,robe:legacy,healthBar:health,mode:'idle',timer:.5,hp:80,reward:7}};
 var other=makeEnemy('archer');var a=makeEnemy('warden'),b=makeEnemy('warden',3,0);''')
 assert not run('buildCreatureReference(other)') and run('other.robe.visible&&other.root.children.length===2')
 assert run('buildCreatureReference(a)&&buildCreatureReference(b)&&creatureReference.live.size===2')
 assert run('!a.robe.visible&&a.healthBar.position.y===1.35&&a.creatureReference.legs.length===4')
 assert run('a.creatureReference.legs[0].upper!==b.creatureReference.legs[0].upper&&a.creatureReference.warning!==b.creatureReference.warning')
 run('var startPhase=a.creatureReference.phase;for(let i=0;i<90;i++)updateCreatureReference(a,1/60)')
 assert run('a.creatureReference.phase===startPhase&&!a.creatureReference.moving'),'Stationary or blocked actors must not run in place'
 run('a.root.visible=false;var hiddenClock=a.creatureReference.clock;a.x+=.5;a.root.position.x=a.x;updateCreatureReference(a,1/60)');assert run('a.creatureReference.clock===hiddenClock'),'Culled actors should skip bone posing'
 run('a.root.visible=true;updateCreatureReference(a,1/60)')
 result=run('''()=>{const samples=[];for(let i=0;i<100;i++){a.x+=.02;a.z-=.025;a.root.position.set(a.x,0,a.z);a.root.rotation.y=.2;updateCreatureReference(a,1/60);for(const leg of a.creatureReference.legs){const foot=leg.end.getWorldPosition(new THREE.Vector3());samples.push({y:foot.y,finite:foot.toArray().every(Number.isFinite),stance:leg.lastPhase<.58,error:foot.distanceTo(leg.anchor)});}}return{phase:a.creatureReference.phase,finite:samples.every(s=>s.finite),minY:Math.min(...samples.map(s=>s.y)),maxY:Math.max(...samples.map(s=>s.y)),stanceError:Math.max(...samples.filter(s=>s.stance).map(s=>s.error))}}''')
 assert result['phase']>.5 and result['finite'] and -.05<result['minY'] and result['maxY']<.3,result
 assert result['stanceError']<.10,result
 run("a.mode='windup';a.timer=a.windupTotal=.75;updateCreatureReference(a,1/60);for(let i=0;i<45;i++){a.timer=Math.max(0,a.timer-1/60);updateCreatureReference(a,1/60)}")
 assert run('a.creatureReference.contacts===0&&a.creatureReference.attackSequence===1'), 'Preparation is not a damage or landing event'
 assert run('b.creatureReference.warning.emissiveIntensity<.6'),'Warning intensity must be per instance'
 result=run("""()=>{const height=[];a.mode='charge';a.timer=a.chargeDuration=.32;for(let i=0;i<21;i++){a.timer=Math.max(0,.32-i/60);a.z-=.12;a.root.position.set(a.x,0,a.z);updateCreatureReference(a,1/60);height.push(a.creatureReference.root.position.y);}return{max:Math.max(...height),min:Math.min(...height),contacts:a.creatureReference.contacts,event:a.creatureReference.lastEvent?.type};}""")
 assert -.112<=result['min'] and .07<result['max']<=.121 and result['contacts']==1,result
 run("a.mode='recover';a.timer=a.recoveryTotal=1.4;for(let i=0;i<84;i++){a.timer=Math.max(0,a.timer-1/60);updateCreatureReference(a,1/60)}")
 assert run('a.creatureReference.contacts===1'),'Recovery must not create a second landing'
 assert run('a.hp===80&&a.reward===7&&a.type==="warden"'),'Visuals must not alter rules or rewards'
 run("a.mode='idle';updateCreatureReference(a,1/60);a.mode='windup';a.timer=.75;updateCreatureReference(a,1/60);a.mode='recover';a.timer=1.4;updateCreatureReference(a,1/60)")
 assert run('a.creatureReference.contacts===1'), 'An interrupted anticipation must not invent a contact'
 run("a.mode='windup';a.timer=.75;updateCreatureReference(a,1/60);a.mode='charge';a.timer=.32;updateCreatureReference(a,1/60);a.timer=.001;updateCreatureReference(a,1/60)")
 assert run('a.creatureReference.contacts===2&&a.creatureReference.lastEvent.type==="landing"'),'Each committed attack can produce exactly one cosmetic landing'
 run('''var geometryDisposed=0;creatureReference.template.traverse(o=>{if(o.isMesh)o.geometry.addEventListener('dispose',()=>geometryDisposed++)});disposeCreatureReferenceRoot(a.root,{restoreLegacy:true});disposeCreatureReferenceRoot(a.root);''')
 assert run('!a.creatureReference&&a.robe.visible&&a.healthBar.position.y===2.5&&creatureReference.live.size===1&&geometryDisposed===0')
 assert run('b.creatureReference.legs.every(l=>l.upper.parent)&&!b.creatureReference.disposed')
 run('disposeCreatureReference(b)');assert run('creatureReference.live.size===0&&creatureReference.disposed===2')
 assert not errors,errors;b.close()
print('PASS: original embedded quadruped, warden-only replacement, four articulated planted limbs, actual-distance gait, bounded feet, per-instance warning, short bounded lunge, no contact on interruption, one cosmetic landing per attack, unchanged rules and shared-resource-safe disposal. CPU-only.')
