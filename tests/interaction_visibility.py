"""Regression for screenshots: reachable fresco, readable notice, props hiding the hero."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import sys as _check_sys
from pathlib import Path as _CheckPath
_check_sys.path.insert(0,str(_CheckPath(__file__).resolve().parents[1]/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);errors=[]
  page=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script('requestAnimationFrame=()=>0');page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);page.click('#start');page.wait_for_function('state==="playing"');run=page.evaluate;run('soundOn=false;p.inv=999;chooseBoon("vigor");')
  for x,z in [(16,-5.3),(14.3,-7),(17.7,-7),(16,-8.7)]:
   run(f'campaign.trials.bells.read=false;resetHeroAt({x},{z});updateInteraction();updateLandmarkReadability();')
   assert run('interactionTarget()?.type==="fresco"'),(x,z)
   page.tap('#interact');assert run('campaign.trials.bells.read&&!document.querySelector("#notice").hidden'),(x,z)
  run('updateNotice(noticeUntil+1000)');assert not page.locator('#notice').is_hidden(),run('({state,noticeAnchor,dist:distance(p,noticeAnchor),hidden:document.querySelector("#notice").hidden,rect:document.querySelector("#notice").getBoundingClientRect().toJSON(),x:p.x,z:p.z,text:document.querySelector("#notice").textContent})')
  # Nearest lamp wins over an earlier item in the array; ring matches the real target.
  run('resetHeroAt(17.6,-9);updateInteraction();updateLandmarkReadability();')
  assert run('interactionTarget().type==="lamp"&&interactionTarget().id==="Aube"&&campaign.focusRing.position.distanceTo(new THREE.Vector3(19,.07,-9))<.01')
  run('resetHeroAt(0,24);updateNotice(noticeUntil+1000)');assert page.locator('#notice').is_hidden()
  run('resetHeroAt(16,-8.7);camera.position.set(16,6.7,8);camera.lookAt(16,1.4,-8.7);scene.updateMatrixWorld(true);updateSanctuary(.3)')
  assert run('campaign.trialModels.find(m=>m.kind==="fresco").root.children.some(o=>o.isMesh&&o.material.isMeshStandardMaterial&&o.material.opacity<.5)'),'Fresco fades when it hides the hero'
  # A foreground column has a collision footprint and an independently fading material.
  run('resetHeroAt(10,18);moveEntity(p,0,-6)');assert run('p.z>14.4&&!blocked(p.x,p.z)')
  run('resetHeroAt(16,11);camera.position.set(24,6.7,25);camera.lookAt(16,1.4,11);scene.updateMatrixWorld(true);updateSanctuary(.3)')
  assert run('world.obstacles.find(o=>o.x===18.2&&o.z===15).mesh.material.opacity<.5')
  # Notice avoids the character's central view and touch buttons in both layouts.
  for width,height in [(390,844),(844,390)]:
   page.set_viewport_size({'width':width,'height':height});run('resetHeroAt(16,-5.3);update(1/60);trialInteract({type:"fresco"});updateNoticeLayout()')
   rect=page.locator('#notice').bounding_box();assert rect and rect['y']>100 and rect['y']+rect['height']<height-150,(width,rect)
   assert run('document.documentElement.scrollWidth<=innerWidth')
   run('camera.position.set(p.x,innerWidth<innerHeight?9.2:6.7,p.z+(innerWidth<innerHeight?12.8:10.8));camera.lookAt(p.x,1.8,p.z-4);updateRigAvatar(.1);scene.updateMatrixWorld(true);updateSanctuary(.3);updateVisualWorld();renderPresentation()')
   page.screenshot(path=f'/tmp/royaumes-interaction-{width}.png')
  # Replacing props does not accumulate disposed materials in the camera list.
  run('var counts=[];for(let i=0;i<3;i++){start();counts.push(sanctuary.occluders.length)}');assert run('Math.max(...counts)-Math.min(...counts)===0')
  assert not errors,errors
  b.close()
finally:
 server.shutdown();server.server_close()
print('PASS: fresco tap from four approaches, nearest lamp and matching focus, persistent readable clue, column collisions, prop/column fading, responsive notice and stable occluder list.')
