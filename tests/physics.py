"""Physical traversal, wall sliding, locomotion and stable shadow projection."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script('requestAnimationFrame=()=>0');page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('avatarRuntime.status==="ready"');page.click('#start');page.wait_for_function('state==="playing"');run=page.evaluate
  run('soundOn=false;p.inv=999;resetHeroAt(-9,11);moveEntity(p,0,-6)')
  assert run('p.z>8.3&&!blocked(p.x,p.z)'),run('({x:p.x,z:p.z})')
  run('resetHeroAt(-14,25);moveEntity(p,0,-5)')
  assert run('p.z>22.9&&!blocked(p.x,p.z)'),'Torch posts must stop a fast traversal'
  run('resetHeroAt(7,13);moveEntity(p,4,-2)')
  assert run('p.z<11.5&&!blocked(p.x,p.z)'),'Diagonal motion must slide around a pier'
  # Requested velocity into a wall must no longer animate running in place.
  run('resetHeroAt(6,13);joy.x=1;joy.y=0;for(let i=0;i<90;i++)update(1/60);joy.x=0;updateRigAvatar(.2)')
  assert run('p.motionSpeed<.01&&avatarRuntime.current.state==="guard"'),run('({speed:p.motionSpeed,state:avatarRuntime.current.state})')
  # A shared floor boundary is traversable, a void boundary is not.
  run('boon="vigor";resetHeroAt(-20,-9);moveEntity(p,0,-3)')
  assert run('p.z<-11.9&&!blocked(p.x,p.z)')
  run('resetHeroAt(-20,-18);moveEntity(p,15,0)')
  assert run('p.x<-16.4&&!blocked(p.x,p.z)')
  run('resetHeroAt(0,0);updateSanctuary(.02);var anchor=sun.target.position.clone();p.x+=.00001;p.z+=.00001;updateSanctuary(.02)')
  assert run('sun.target.position.clone().sub(anchor).projectOnPlane(sun.position.clone().sub(sun.target.position).normalize()).length()<1e-6'),'Sub-texel movement must not shift the shadow projection plane'
  assert run('sun.target.position.distanceTo(anchor)<.00003'),'Depth tracking must remain continuous'
  assert run('Math.abs(sun.target.position.z)<.04'),'z=0 must not jump back to the arrival court'
  run('p.leap=.375;update(1/60)')
  assert run('heroShadow.material.opacity<.15&&heroShadow.scale.x>1.4'),'Light-mode contacts soften with jump height'
  assert not errors,errors
  b.close()
finally:
 server.shutdown();server.server_close()
print('PASS: interactive bases and torches, fast traversal, sliding, idle against walls, connected ground, void edges, shadow stability and airborne contacts.')
