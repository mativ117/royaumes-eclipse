from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
html=(Path(__file__).resolve().parents[1]/'docs/index.html').read_bytes()
class H(BaseHTTPRequestHandler):
 def do_GET(self):self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(html)
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=b.new_page(viewport={'width':900,'height':600});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/');page.click('#start');run=page.evaluate
  run('soundOn=false;p.inv=999;')
  # The inactive boss cannot be shot from the previous zone.
  assert run('damage(boss,2000,null);boss.hp')==850
  # Absorption, charged shot and frontal guard still matter in the new world.
  result=run('chooseBoon("vigor");power();p.absorbLock=0;hurt(20);p.absorbLock=0;hurt(20);p.absorbLock=0;hurt(20);p.shot=0;fire();({hp:p.hp,charge:bullets[bullets.length-1].damage})')
  assert result=={'hp':190,'charge':94},result
  result=run('var guard=enemies.find(e=>e.type==="sentinel");guard.facing=0;guard.mode="idle";guard.hp=1000;damage(guard,100,{x:guard.x,z:guard.z-4});var front=guard.hp;damage(guard,100,{x:guard.x,z:guard.z+4});({front,hp:guard.hp})')
  assert result=={'front':985,'hp':885},result
  # Checkpoint preserves earlier kills, but restores enemies killed after it.
  run('damage(guard,10000,null);p.x=0;p.z=-38;p.vx=p.vz=0;update(1/60);var later=enemies.find(e=>e.id==="nef-archer");damage(later,10000,null);p.inv=0;p.shield=0;p.leap=0;hurt(999)');page.click('#resume')
  assert not run('enemies.some(e=>e.id==="garden-guard")')
  assert run('enemies.some(e=>e.id==="nef-archer"&&!e.dead)')
  # An archer hit from outside its passive radius reacts and moves into range.
  moved=run('var archer=enemies.find(e=>e.id==="garden-archer");p.x=-20;p.z=-1;p.inv=999;var beforeZ=archer.z;damage(archer,5);for(let i=0;i<20;i++)updateEnemy(archer,1/60);archer.z-beforeZ')
  assert moved>.1,moved
  # The optional garden secret is observed, never granted by proximity or shooting.
  run('p.x=-23;p.z=-29;p.vx=p.vz=0;p.inv=999;update(1/60)');assert not run('secretFound')
  page.keyboard.down('f');run('shooting=true;updateDesign(.8)');assert not run('secretFound')
  run('shooting=false;p.recoil=0;updateDesign(.8)');assert not run('secretFound')
  run('updateDesign(.8)');page.keyboard.up('f');assert run('secretFound')
  page.reload();page.click('#start');assert run('secretFound')
  # A close oracle announces damage, which arrives only after the telegraph.
  run('soundOn=false;var oracle=enemies.find(e=>e.type==="oracle");enemies=enemies.filter(e=>e===oracle);p.x=oracle.x+2;p.z=oracle.z;p.vx=p.vz=0;p.inv=0;p.hp=p.max=100;oracle.timer=0;oracle.mode="idle";updateOracle(oracle,1/60)')
  assert run('p.hp')==100
  hp=run('for(let i=0;i<80;i++)update(1/60);p.hp');assert hp==77,hp
  assert not errors,errors
  b.close();print('PASS: boss encounter lock, Braise, guard direction, checkpoint kill persistence/respawn, secret observation and real persistence, oracle warning before damage. No JS errors.')
finally:server.shutdown();server.server_close()
