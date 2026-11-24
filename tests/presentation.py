"""Presentation must preserve rig orientation, render state and resource lifetimes."""
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
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=b.new_page(viewport={'width':720,'height':480});errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('console',lambda m:errors.append(m.text[:1000]) if m.type=='error' else None)
  page.add_init_script('requestAnimationFrame=()=>0');page.goto(f'http://127.0.0.1:{server.server_port}/')
  page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
  run('soundOn=false;start();p.inv=999;for(let i=0;i<20;i++)update(1/60)')
  assert run('scene.environment.isTexture&&presentation.surfaces.sand.normal.isTexture')
  assert run('avatarBone(avatarRuntime.current,"cape_tip").getWorldPosition(new THREE.Vector3()).y < avatarBone(avatarRuntime.current,"chest").getWorldPosition(new THREE.Vector3()).y'), 'Cloth must hang below shoulders'
  run('var testEnemy=spawn(-6,25);var sharedCloak=testEnemy.rig.mantle.material;startEnemyFall(testEnemy,p);testEnemy.dead=true;')
  assert run('presentation.fallen.length===1&&testEnemy.rig.mantle.material!==sharedCloak')
  run('updatePresentation(.25)');assert run('testEnemy.root.parent===scene&&Math.abs(testEnemy.root.rotation.x)>.3')
  run('updatePresentation(.5)');assert run('presentation.fallen.length===0&&!testEnemy.root.parent')
  run('var initialTone=renderer.toneMapping;updateVisualWorld();renderPresentation()')
  assert run('renderer.toneMapping===initialTone&&renderer.getRenderTarget()===null&&presentation.stats.postPasses===3')
  run('quality="light";renderPresentation()');assert run('presentation.stats.postPasses===0')
  run('enterChapter(2);');assert run('journey.pbrFloors.length>0&&journey.pbrFloors.every(f=>f.material.normalMap&&f.material.roughnessMap)&&journey.canopyLeaves.isInstancedMesh')
  run('enterChapter(3);');assert run('journey.pbrFloors.every(f=>f.material.map.source===presentation.surfaces.wood.map.source)')
  run('resetJourneyWorld();clearFallenActors();');assert run('journey.level===1&&presentation.fallen.length===0')
  assert not errors,errors
  b.close()
finally:
 server.shutdown();server.server_close()
print('PASS: downward cloth, PBR surfaces, HDR/post state, light bypass, death/fade cleanup, shared NPC material isolation and chapter surface changes.')
