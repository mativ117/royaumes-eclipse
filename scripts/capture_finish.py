"""Actual 1.3 renderer captures at controlled positions, without retouching."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import sys as _check_sys
from pathlib import Path as _CheckPath
_check_sys.path.insert(0,str(_CheckPath(__file__).resolve().parents[1]/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);errors=[];missing=[]
  page=browser.new_page(viewport={'width':1100,'height':760});page.add_init_script('requestAnimationFrame=()=>0');page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:missing.append(r.url) if r.status>=400 else None)
  page.goto(f'http://127.0.0.1:{server.server_port}/atelier-lame.html');page.wait_for_function('window.reviewReady===true',polling=50);page.evaluate('mixer.update(.2);frame(performance.now())');page.screenshot(path=str(OUT/'r3-lame-atelier.jpg'),type='jpeg',quality=93);print('Captured studio',flush=True)
  page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=lame');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
  # Only the visible embedded studio renders while the selection is open.
  page.locator('.hero-preview').scroll_into_view_if_needed();page.wait_for_function('heroPreviewRuntime.readyHero==="lame"',polling=50)
  child=page.frame_locator('.hero-preview-frame');child.locator('#view').evaluate('()=>{mixer.update(.2);frame(performance.now())}');page.screenshot(path=str(OUT/'r3-selection.jpg'),type='jpeg',quality=92);print('Captured selection',flush=True)
  page.click('#heroPreviewPlay');page.wait_for_function('!heroPreviewRuntime.frame',polling=50);run('soundOn=false;p.inv=999;')
  for name,level,x,z in [('atrium',1,0,23),('archives',1,-44,-57),('forge',1,40,-54),('jardin',2,0,-46),('convoi',3,0,-39)]:
   if level>1:run(f'enterChapter({level},3)')
   run(f'''resetHeroAt({x},{z});p.inv=999;for(let i=0;i<15;i++)update(1/60);camera.position.set({x},6.7,{z}+10.8);camera.lookAt({x},1.6,{z}-5);updateJourneyScenery(.1);updateSanctuary(.1);updateHUD();$('#zoneBanner').hidden=true;updateVisualWorld();renderPresentation();''')
   assert run('world.onGround(p.x,p.z)&&Number.isFinite(p.x)&&Number.isFinite(p.z)'),name
   page.screenshot(path=str(OUT/f'r3-{name}.jpg'),type='jpeg',quality=92);print('Captured',name,'calls',run('presentation.stats.sceneCalls'),flush=True)
  assert not errors,errors
  assert not missing,missing
  browser.close()
finally:server.shutdown();server.server_close()
