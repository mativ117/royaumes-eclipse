"""Ten legacy heroes retain their procedural support on every body size.

The calibrated Lame preserves authored swing/contact data and is measured by
tests/lame_motion_quality.py, rather than forcing the legacy phase model on it.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=b.new_page();page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('avatarRuntime.status==="ready"',polling=50)
  page.evaluate('Promise.all(Object.keys(HERO_DEFS).filter(id=>id!=="lame").map(ensureHeroModel))')
  result=page.evaluate('''()=>{soundOn=false;const outcomes=[];for(const id of Object.keys(HERO_DEFS).filter(id=>id!=="lame")){hero=id;start();for(const speed of [1.8,HEROES[id].speed])for(const [dx,dz] of [[0,-1],[0,1],[1,0],[-1,0]]){resetHeroAt(-6,25);p.motionSpeed=speed;aim=0;const samples=[];for(let i=0;i<180;i++){t+=1/60;p.x+=dx*speed/60;p.z+=dz*speed/60;player.root.position.set(p.x,0,p.z);player.root.rotation.set(0,0,0);updateRigAvatar(1/60);const a=avatarRuntime.current;if(i>45&&a.feetWeight>.99)for(let leg=0;leg<2;leg++){const l=a.legs[leg];if(l.lastPhase>.03&&l.lastPhase<.545){const pos=l.end.getWorldPosition(new THREE.Vector3());samples.push({key:leg+':'+Math.floor(a.stepPhase+leg*.5),x:pos.x,z:pos.z,y:pos.y});}}}const groups=[...new Set(samples.map(s=>s.key))].map(key=>samples.filter(s=>s.key===key)).filter(a=>a.length>2),drift=Math.max(...groups.map(a=>Math.hypot(a.at(-1).x-a[0].x,a.at(-1).z-a[0].z)));outcomes.push({id,speed,dx,dz,drift,groups:groups.length,ground:Math.max(...samples.map(s=>s.y))});}}return outcomes;}''')
  assert len(result)==80,result
  for check in result:
   assert check['groups']>=4 and check['drift']<.05 and check['ground']<.20,check
  assert not errors,errors
  b.close()
 print('PASS: ten legacy heroes, walk/run, four directions, late-stance foot drift below 5 cm and grounded feet. Calibrated Lame: run tests/lame_motion_quality.py. Controlled kinematic measurement, not an animation-quality claim.')
finally:server.shutdown();server.server_close()
