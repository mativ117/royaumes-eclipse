"""Actual 1.6 HTTP game, creatures, contacts and lifecycle. Serial GPU only.

Fixed-step software rendering is not a hardware FPS, listening or balance test.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import json
import sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()


class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass


SCENARIO=r'''() => {
 soundOn=false;chooseBoon('vigor');
 const check=(v,m)=>{if(!v)throw Error(m);};
 const clear=()=>{clearFallenActors();for(const e of enemies)cleanupObject(e.root);enemies=[];for(const b of bullets)b.mesh.removeFromParent();bullets=[];clearHazards();};
 clear();resetHeroAt(16,-16);p.inv=999;p.max=p.hp=150;
 const archer=spawn(16,-8,'archer');archer.alert=20;archer.authoredEnemy.ai.cooldown=0;
 check(classLine(archer,p),'Reference lane must be open in the real cloister');
 const c=archer.authoredEnemy;check(c&&c.muzzle&&c.clips.release,'Actual archer asset and release socket');
 check(c.materials.every(m=>m.map?.image?.width>=512&&m.normalMap?.image?.width>=256&&m.roughnessMap?.image?.width>=256),'Real archer PBR images must decode');
 let first=null,events=0;const dt=1/120;
 for(let i=0;i<324;i++){
  if(c.ai.phase==='windup'&&c.ai.elapsed>.7)p.x=19;
  const before=bullets.length;t+=dt;updateEnemy(archer,dt);
  if(bullets.length>before){events++;const shot=bullets.at(-1),socket=c.muzzle.getWorldPosition(new THREE.Vector3());check(Math.hypot(shot.x-socket.x,shot.z-socket.z)<1e-5,'Projectile is emitted from actual posed socket');check(Math.abs(shot.dx)<.001&&shot.dz<-.99,'Direction stays locked after last-half target move');first={time:c.ai.clock,x:shot.x,y:shot.y,z:shot.z,phase:c.ai.phase,releaseElapsed:c.ai.elapsed};}
  poseEnemy(archer);
 }
 check(events===1&&first&&first.time>=c.clips.windup.duration+2/30,'One source-timed native arrow after its complete tell');
 const second=spawn(19,-8,'archer'),sourceBones=[];c.root.traverse(o=>{if(o.isBone)sourceBones.push(o);});second.authoredEnemy.root.traverse(o=>{if(o.isBone)check(!sourceBones.includes(o),'Runtime creatures cannot share bones');});
 clear();resetHeroAt(17.5,-17.1);p.hp=p.max=150;for(const field of ['inv','shield','leap','dashT','formT','wardT','incarnateT','fragileT'])p[field]=0;
 const shade=spawn(17.5,-14,'shade');check(enemyV16FootprintLegal(shade,shade.x,shade.z,shade.authoredEnemy.ai.heading),'Native charge starts with a legal full footprint');shade.alert=20;shade.reveal=10;shade.authoredEnemy.ai.cooldown=0;
 check(shade.authoredEnemy.materials.every(m=>m.map?.image?.width>=512&&m.normalMap?.image?.width>=256),'Real manta maps must decode');
 const before=p.hp;for(let i=0;i<204;i++){t+=dt;p.inv=Math.max(0,p.inv-dt);updateEnemy(shade,dt);poseEnemy(shade);}
 check(before-p.hp===18,'Actual charge deals exactly one native 18-damage contact: '+JSON.stringify({lost:before-p.hp,phase:shade.authoredEnemy.ai.phase,elapsed:shade.authoredEnemy.ai.elapsed,travel:shade.authoredEnemy.ai.chargeTravel,x:shade.x,z:shade.z,heading:shade.authoredEnemy.ai.heading,awareness:shade.awareness,inv:p.inv,boon,shield:p.shield}));
 const contact={lost:before-p.hp,travel:shade.authoredEnemy.ai.chargeTravel,phase:shade.authoredEnemy.ai.phase};
 // A true phase transition recompiles opacity state; death keeps ownership of fade.
 const material=shade.authoredEnemy.materials[0],version=material.version;
 shade.authoredEnemy.ai.phase='idle';shade.mode='idle';shade.reveal=0;
 const savedT=t;t=0;shade.phaseOffset=0;poseEnemy(shade);check(material.transparent&&material.opacity<.3&&material.version>version,'Hidden phase updates shader opacity state');
 const hiddenVersion=material.version;shade.reveal=10;poseEnemy(shade);check(!material.transparent&&material.opacity===1&&material.version>hiddenVersion,'Reveal restores opaque shader state');t=savedT;
 damage(shade,30,p);check(shade.authoredEnemy.ai.react>0,'A real nonlethal hit enters its bounded reaction');
 const instance=shade.authoredEnemy;damage(shade,10000,p);
 check(shade.dead&&presentation.fallen.some(f=>f.root===shade.root),'Native damage starts the authored death lifecycle');
 enemies=enemies.filter(e=>!e.dead);const deathMaterials=instance.materials.slice(),disposed=new Map(deathMaterials.map(m=>[m,0]));for(const m of deathMaterials)m.addEventListener('dispose',()=>disposed.set(m,disposed.get(m)+1));
 for(let i=0;i<20;i++)updatePresentation(1/60);
 check(instance.state==='death'&&instance.deathClock>.2&&instance.root.parent,'Actual death clip advances before cleanup');check(instance.materials.every(m=>m.transparent),'Death preserves the owning fade material state');
 for(let i=0;i<90;i++)updatePresentation(1/60);
 check(instance.disposed&&!instance.root.parent&&[...disposed.values()].every(v=>v===1),'Death clones and skeletons dispose once');
 const settled=spawn(16,-8,'shade');check(enemyV16FootprintLegal(settled,settled.x,settled.z,settled.authoredEnemy.ai.heading),'Legacy fresco spawn resolves its full body before rendering');clearRoom();check(enemyDirectionV16.live.size===0,'No authored enemy survives room cleanup');
 return {archer:first,arrowEvents:events,shade:contact,isolatedBones:sourceBones.length,deathMaterials:deathMaterials.length};
}'''

server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1100,'height':760});page.add_init_script('requestAnimationFrame=()=>0');errors=[];console=[];missing=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
  page.on('response',lambda r:missing.append(r.url) if r.status>=400 else None)
  page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=rempart')
  page.wait_for_function('avatarRuntime.status==="ready"&&enemyDirectionV16.status==="ready"',polling=50)
  assert page.locator('#start').is_enabled();page.click('#start');run=page.evaluate
  report=run(SCENARIO)
  # Actual shader compilation in both presets; camera and navigation are unchanged by fixture setup.
  run('start();resetHeroAt(16,-16);spawn(16,-8,"archer");spawn(19,-10,"shade");p.inv=999;')
  for quality in ['standard','light']:
   page.select_option('#quality',quality,force=True)
   run('camera.position.set(19,7,1);camera.lookAt(17,1.2,-11);updateSanctuary(.016);if(typeof updateEnvironmentDirectionV16==="function")updateEnvironmentDirectionV16(.016);for(const e of enemies)poseEnemy(e);updateVisualWorld();renderPresentation()')
   assert run('Number.isFinite(presentation.stats.sceneCalls)&&presentation.stats.sceneCalls>0')
  run('clearRoom();window.profileBeforeCreatureDuel=JSON.stringify(localProfile.journey)')
  run("async()=>{await ensureHeroModel('voleur');await beginDuelMatch({kind:'bot',opponentHero:'voleur',seed:163});}")
  assert run('localParty.length===1&&!localParty[0].proxy.authoredEnemy&&enemyDirectionV16.live.size===0&&JSON.stringify(localProfile.journey)===profileBeforeCreatureDuel')
  assert not errors,errors
  assert not console,console
  assert not missing,missing
  browser.close()
 Path('/tmp/direction-v16-integration-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS GAME: actual two PBR creatures, locked source-timed socket arrow, one18-damage charge, phase shader updates, independent bones, real damage/reaction/death/fade cleanup, both render presets and preserved duel/profile. Controlled software browser, not phone performance or artistic certification.')
finally:
 server.shutdown();server.server_close()
