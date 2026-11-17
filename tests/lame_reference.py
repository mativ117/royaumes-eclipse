"""First approved hero production: embedded textures, unique clips, studio and game."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);errors=[]
  for width,height in [(1100,760),(390,844)]:
   page=b.new_page(viewport={'width':width,'height':height});page.add_init_script('requestAnimationFrame=()=>0');page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/atelier-lame.html');page.wait_for_function('window.reviewReady===true',polling=50);run=page.evaluate
   assert run('Object.keys(actions).length===23')
   assert run('model.getObjectsByProperty("isSkinnedMesh",true).length>=2')
   assert run('model.getObjectsByProperty("isMesh",true).every(o=>(Array.isArray(o.material)?o.material:[o.material]).every(m=>m.map&&m.normalMap&&m.roughnessMap))')
   for clip in ['walk_back','strafe_left','strafe_right','attack1','attack2','attack3','dodge_left','dodge_right']:
    page.select_option('#motion',clip);run('mixer.update(.18);frame(performance.now())');assert run('active.getClip().name')==clip
   page.select_option('#motion','idle');run('mixer.update(.2);frame(performance.now())');assert run('document.documentElement.scrollWidth<=innerWidth')
   page.screenshot(path=f'/tmp/lame-review-{width}.png');page.close()
  page=b.new_page();page.add_init_script('requestAnimationFrame=()=>0');page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=lame');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate;assert run('hero==="lame"&&!!avatarRuntime.heroes.lame');page.click('#start');run('soundOn=false;p.inv=999;for(let i=0;i<25;i++)update(1/60)');assert run('avatarRuntime.current.state==="guard"')
  result=run('''()=>{const paths=[];for(let combo=1;combo<=3;combo++){resetHeroAt(0,24);p.attack={melee:true,combo,elapsed:0,duration:.7,hitAt:.26,struck:false,aim:0};avatarRuntime.current.lastAttack=null;const samples=[];for(let i=0;i<10;i++){p.attack.elapsed=i*.06;updateRigAvatar(.06);samples.push(avatarRuntime.current.blade.getWorldPosition(new THREE.Vector3()).toArray());}paths.push(samples);}return paths;}''')
  assert len({str(p) for p in result})==3,'Each combo must trace its own blade path'
  run('cancelAttack();resetHeroAt(0,24);p.motionSpeed=2;for(let i=0;i<45;i++){p.x+=.033;player.root.position.set(p.x,0,p.z);updateRigAvatar(1/60)}');assert run('avatarRuntime.current.lowerState==="strafe_right"')
  assert not errors,errors
  b.close()
 print('PASS: 23 Lame clips and embedded PBR textures, actual 3D studio at PC/phone sizes, direct hero selection, guard, distinct blade paths and directional locomotion.')
finally:server.shutdown()
