"""Actual in-engine reference enemy and public resource lifecycle, fixed simulation steps."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page(viewport={'width':1100,'height':760});p.add_init_script('requestAnimationFrame=()=>0');errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{server.server_port}/index.html');p.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=p.evaluate
  assert run('creatureReference.status==="ready"');p.click('#start');run('soundOn=false;clearRoom();clearHazards();resetHeroAt(4,26);p.inv=0;window.w=spawn(4,23);w.alert=20;w.timer=0;')
  assert run('!!w.creatureReference&&w.creatureReference.legs.length===4&&w.creatureReference.materials.every(m=>m.map&&m.normalMap&&m.roughnessMap)')
  run('for(let i=0;i<85;i++){t+=1/60;updateEnemy(w,1/60);poseEnemy(w);}camera.position.set(4,4.6,32);camera.lookAt(4,.7,23);updateVisualWorld();renderPresentation()')
  assert run('p.hp===p.max-22&&w.mode==="recover"&&w.creatureReference.contacts===1'),run('({hp:p.hp,max:p.max,mode:w.mode,contacts:w.creatureReference.contacts})')
  assert run('hazards.every(h=>h.damage===0)&&w.creatureReference.legacy.every(q=>!q.object.visible)')
  p.screenshot(path='/tmp/reference-creature-in-game.png')
  run('var created=creatureReference.built;clearRoom();');assert run('creatureReference.live.size===0&&creatureReference.disposed===created')
  # A new body/attack must preserve the Convoi's actual objective threat.
  run('enterChapter(3);clearRoom();clearHazards();journey.step=4;journey.core=180;resetHeroAt(5,-73);p.inv=999;window.w=spawn(0,-69.6);w.sabotage=true;w.alert=20;w.timer=0;for(let i=0;i<90;i++){t+=1/60;updateEnemy(w,1/60);poseEnemy(w);}')
  assert run('Math.abs(journey.core-(180-22*.65))<1e-6&&w.mode==="recover"'),run('({core:journey.core,mode:w.mode,x:w.x,z:w.z})')
  run('for(let i=0;i<15;i++){t+=1/60;updateEnemy(w,1/60);poseEnemy(w);}');assert run('Math.abs(journey.core-(180-22*.65))<1e-6'),'Recovery must not damage the core again'
  run('clearRoom()');assert run('creatureReference.live.size===0')
  assert not errors,errors;b.close()
 print('PASS: actual textured quadruped, locked lunge damages player/core once, four feet and recovery, no legacy meshes, decorative telegraphs and disposed cloned resources.')
finally:server.shutdown();server.server_close()
