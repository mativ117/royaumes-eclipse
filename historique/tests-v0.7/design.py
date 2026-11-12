"""Pact decisions, world consequences and a discoverable persistent secret."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
html=(Path(__file__).resolve().parents[1]/'docs/index.html').read_bytes()
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(html)
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  ctx=b.new_context(viewport={'width':820,'height':480});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/');page.click('#start')
  run=page.evaluate
  run('p.inv=999;p.x=-9;p.z=-7;update(1/60)')
  assert run('boon')=='' and page.locator('#interact').is_visible()
  page.keyboard.press('f');assert run('state')=='choice'
  assert '2,4' in page.locator('#pactCost').inner_text()
  frozen=run('t');page.wait_for_timeout(150);assert run('t')==frozen
  page.click('#leavePact');assert run('boon')=='' and run('state')=='playing'
  page.keyboard.press('f');page.click('#sealPact')
  assert run('boon')=='vigor' and run('p.max')==190
  run('dash()');assert run('p.dash')>2.2
  run('power();p.inv=0;for(let i=0;i<4;i++){p.absorbLock=0;hurt(20)}')
  assert run('p.overcharge')==3 and run('p.hp')==190
  run('p.shot=0;fire()');assert run('bullets[bullets.length-1].damage')==94
  assert run('p.overcharge')==0
  run('p.shot=0;fire()');assert run('bullets[bullets.length-1].damage')==34
  run('setupRoom(1)');assert run('traps.every(t=>t.userData.gap===0)')
  page.screenshot(path='/tmp/eclipse-v04-braise.png')
  # Fresh run: the alternative costs health, leaves a targetable decoy, changes gaps.
  page.click('#pause');page.click('#back');page.click('#start')
  run('p.inv=999;p.x=9;p.z=-7;update(1/60)');page.keyboard.press('f')
  assert '120' in page.locator('#pactCost').inner_text()
  page.click('#sealPact');assert run('boon')=='haste' and run('p.max')==120
  run('p.x=0;p.z=6;dash()');assert run('decoy!==null')
  run('p.x=10;p.z=-5');assert run('enemyTarget(enemies[0])===decoy')
  run('setupRoom(1)');assert run('traps[0].userData.gap')==-7 and run('traps[2].userData.gap')==7
  # Observing is deliberate: moving or firing cancels progress.
  run('p.x=12;p.z=-3;p.vx=p.vz=0;p.inv=999;update(1/60)')
  page.keyboard.down('f');run('updateDesign(.5)');assert run('observeTime')>0
  run('p.vx=1;updateDesign(.1)');assert run('observeTime')==0
  run('p.vx=0;shooting=true;updateDesign(.2)');assert run('observeTime')==0
  run('shooting=false;p.recoil=0;updateDesign(.7)');assert not run('secretFound')
  run('updateDesign(.9)');page.keyboard.up('f');assert run('secretFound')
  assert run('localStorage.getItem(SECRET_KEY)')=='found'
  page.reload();page.click('#start');assert run('secretFound')
  timing=run('chooseBoon("haste");setupRoom(2);boss.timer=0;updateBoss(boss,1/60);({windup:boss.timer,hazard:hazards[0].delay})')
  assert timing['windup']>1.7 and timing['hazard']>1.6,timing
  page.screenshot(path='/tmp/eclipse-v04-boss.png')
  # The secret is optional. A run without the mark can still reach and defeat the boss.
  run('secretFound=false;boss.mode="recover";boss.timer=99;p.x=0;p.z=3;p.inv=999;clearHazards();aim=targetAim=0;mouseAim=false;shooting=true;for(let i=0;i<500;i++)update(1/60);shooting=false')
  assert run('boss.dead') and run('portal.visible')
  run('p.x=0;p.z=-15;update(1/60)');assert run('state')=='won'
  # Touch interactions and choice buttons must work in portrait and landscape.
  for viewport in [{'width':390,'height':740},{'width':740,'height':390}]:
   mobile=b.new_context(viewport=viewport,is_mobile=True,has_touch=True);m=mobile.new_page();m.on('pageerror',lambda e:errors.append(str(e)));m.set_content(html.decode());m.tap('#start')
   m.evaluate('p.inv=999;p.x=9;p.z=-7;update(1/60)');m.tap('#interact');assert m.evaluate('state')=='choice'
   m.tap('#sealPact');assert m.evaluate('boon')=='haste';assert m.evaluate('state')=='playing'
   m.evaluate('setupRoom(1);p.x=12;p.z=-3;p.vx=p.vz=0;p.inv=999;update(1/60)')
   assert m.locator('#interact').is_visible()
   # Hold observation using a real touch input; focus changes do not pause it.
   cdp=mobile.new_cdp_session(m);r=m.locator('#interact').bounding_box()
   cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':r['x']+r['width']/2,'y':r['y']+r['height']/2,'id':1}]})
   m.evaluate('window.dispatchEvent(new Event("blur"));for(let i=0;i<100;i++)update(1/60)')
   cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
   assert m.evaluate('state')=='playing' and m.evaluate('secretFound')
   m.screenshot(path='/tmp/eclipse-v04-mobile.png');mobile.close()
  assert not errors,errors
  b.close();print('PASS: explicit/cancellable pact choices; frozen choice dialog; Braise absorption and overcharge; Élan decoy and health cost; altered routes; secret observation/cancellation/persistence/reward; optional secret; mobile confirm and hold, blur regression. No JS errors.')
finally:server.shutdown();server.server_close()
