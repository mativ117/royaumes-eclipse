"""Render the new levels and different rigs in high/light, desktop/phone layouts."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);errors=[];console=[];missing=[]
  for width,height,touch in [(1100,760,False),(390,844,True),(844,390,True)]:
   page=b.new_page(viewport={'width':width,'height':height},is_mobile=touch,has_touch=touch);page.add_init_script('requestAnimationFrame=()=>0');page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:missing.append(r.url) if r.status>=400 else None);page.on('console',lambda m:console.append(m.text) if m.type=='error' else None);page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate;run('soundOn=false;')
   for level,hero in [(2,'neant'),(3,'bergere')]:
    run(f'ensureHeroModel("{hero}")');run(f'hero="{hero}";start();enterChapter({level});p.inv=999;')
    for quality in ['standard','light']:
     page.select_option('#quality',quality,force=True);run('for(let i=0;i<10;i++)update(1/60);updateJourneyScenery(.1);updateSanctuary(.1);renderer.render(scene,camera)')
     calls=run('renderer.info.render.calls');assert calls<(650 if quality=='standard' else 400),(level,width,quality,calls)
     assert run('document.documentElement.scrollWidth<=innerWidth'),(width,height)
     assert run('world.onGround(p.x,p.z)&&Number.isFinite(avatarRuntime.current.legs[0].end.getWorldPosition(new THREE.Vector3()).y)')
    run('toggleMap()');assert page.locator('#missionList button').count()>=1;assert run('document.documentElement.scrollWidth<=innerWidth');run('toggleMap()')
    if width==1100:run('updateJourneyScenery(.1);renderer.render(scene,camera)');page.screenshot(path=f'/tmp/royaumes-final-chapter-{level}-{width}.png')
   page.close()
  assert not errors,errors
  assert not console,(console,missing)
  b.close()
 print('PASS: new chapters in desktop, portrait and landscape; Neant/Bergere rigs; high/light shadow shaders and draw budgets; responsive maps and finite grounded poses. Simulated devices, no real-phone frame-rate claim.')
finally:server.shutdown()
