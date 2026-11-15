"""Authored GLB rigs, animation playback, basin routing, mirror quality and occlusion."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1100,'height':760});errors=[];logs=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:logs.append(m.text) if m.type=='error' else None)
 page.set_content('<script>requestAnimationFrame=()=>0</script>'+(ROOT/'docs/index.html').read_text());page.click('#start');run=page.evaluate
 assert run('avatarRuntime.status')=='ready'
 assert run('Object.values(avatarRuntime.heroes).every(a=>a.root.getObjectsByProperty("isSkinnedMesh",true).length>=2&&Object.keys(a.actions).length===13&&a.weapon&&a.muzzle&&a.hand&&a.blade)')
 assert run('player.legacyParts.every(o=>!o.visible)')
 run('soundOn=false;p.inv=999;p.vx=4.9;updateRigAvatar(.12);var thigh=avatarRuntime.current.root.getObjectByName("thighL"),q=thigh.quaternion.clone();updateRigAvatar(.16)')
 assert run('avatarRuntime.current.state')=='run'
 assert run('Math.abs(q.dot(thigh.quaternion))<.999'),'Running must move the imported skeleton'
 run('p.vx=p.vz=0;campaign.trials.forge.carrying=true;updateRigAvatar(.1)')
 assert run('avatarRuntime.current.state==="carry"&&!avatarRuntime.current.weapon.visible')
 run('campaign.trials.forge.carrying=false;hero="voltigeur";applyHero();p.shot=0;beginAttack();updateAttack(.17);updateRigAvatar(.1)')
 assert run('avatarRuntime.current.state')=='attack1'
 run('cancelAttack();p.stagger=.2;updateRigAvatar(.02)');assert run('avatarRuntime.current.state')=='hit'
 run('p.stagger=0;hero="rempart";applyHero();p.shot=0;beginAttack();updateAttack(.08);var shot=bullets.at(-1),tip=avatarRuntime.current.muzzle.getWorldPosition(new THREE.Vector3());')
 assert run('Math.hypot(shot.x-tip.x,shot.z-tip.z)<.2'),'Bullet must originate at the model muzzle'
 run('cancelAttack();p.shot=0;resetHeroAt(0,23)')
 assert run('blocked(0,13)') and not run('blocked(0,13,.1,true)')
 result=run('var path=buildGuideRoute({x:-9,z:7});({safe:path.every(q=>!blocked(q.x,q.z,.55)),count:path.length,detour:path.some(q=>Math.abs(q.x)>4)})')
 assert result['safe'] and result['count'] and result['detour'],result
 # Follow the route through real movement and collision, not a teleport.
 run('''for(const node of path.slice(1)){let i=0;while(Math.hypot(node.x-p.x,node.z-p.z)>.3&&i++<130){const d=Math.hypot(node.x-p.x,node.z-p.z);joy.x=(node.x-p.x)/d;joy.y=(node.z-p.z)/d;update(1/60);}if(i>=130)throw Error('Movement stuck near basin');}joy.x=joy.y=0;''')
 assert run('Math.hypot(p.x+9,p.z-7)<2.7&&interactionTarget()?.type==="pact"')
 run('resetHeroAt(10,8);world.root.updateMatrixWorld(true);updateSanctuary(.2);')
 assert run('world.obstacles.find(o=>o.x===10&&o.z===13).mesh.material.opacity')<.6
 run('resetHeroAt(0,23);update(1/60);updateArtDirection(.02);updateSanctuary(.1);renderer.render(scene,camera)')
 assert run('sanctuary.reflection.visible&&renderer.shadowMap.enabled&&!heroShadow.visible')
 assert run('renderer.info.render.calls')<650
 page.screenshot(path='/tmp/royaumes-012-sanctuary.png')
 page.select_option('#quality','light',force=True);run('updateSanctuary(.1);renderer.render(scene,camera)')
 assert run('!sanctuary.reflection.visible&&sanctuary.fallback.visible&&!renderer.shadowMap.enabled&&heroShadow.visible')
 assert run('renderer.info.render.calls')<400
 run('p.power=0;power();update(1/60);updateSanctuary(.02);renderer.render(scene,camera)');assert run('shield.visible&&avatarRuntime.current.state==="shield"')
 assert not errors,errors
 assert not logs,logs
 b.close()
 print('PASS: two real skinned GLBs, 13 clips each, animated bones, weapon carry state, attack/hit playback, model muzzle origin, basin collision and traversal, camera occlusion, reflection/shadow quality switch, draw budgets. No JS/shader errors.')
