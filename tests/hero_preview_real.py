"""Exercise the real inline 3D viewer and single-active-renderer lifecycle."""
from pathlib import Path
import sys
from urllib.parse import urlsplit,urlunsplit
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def copyfile(self,source,outputfile):
  try:super().copyfile(source,outputfile)
  except (BrokenPipeError,ConnectionResetError):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
url=sys.argv[1] if len(sys.argv)>1 else f'http://127.0.0.1:{server.server_port}/index.html?hero=rempart'
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page(viewport={'width':1366,'height':900});page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.wait_for_function('avatarRuntime.status==="ready"',polling=50);page.locator('.hero-preview').scroll_into_view_if_needed();page.wait_for_function('heroPreviewRuntime.readyHero==="rempart"',polling=50);run=page.evaluate
  child=page.locator('.hero-preview-frame').element_handle().content_frame();child.wait_for_function('window.reviewReady===true&&reviewActive===true',polling=50)
  before=run('renderer.info.render.frame');run('frame(performance.now());frame(performance.now()+17)');assert run('renderer.info.render.frame')==before,'Parent must not draw while preview is active'
  child.evaluate('frame(performance.now())');assert child.evaluate('renderer.info.render.calls>0')
  page.click('[data-hero=lame]');page.wait_for_function('heroPreviewRuntime.readyHero==="lame"&&!document.querySelector("#start").disabled',polling=50);run('document.querySelector("[data-hero=voltigeur]").click();document.querySelector("[data-hero=lame]").click()');page.wait_for_function('heroPreviewRuntime.readyHero==="lame"&&!document.querySelector("#start").disabled',polling=50);child.wait_for_function('reviewHero==="lame"&&requestedReviewHero==="lame"&&window.reviewReady',polling=50);child.select_option('#motion','attack1');child.evaluate('mixer.update(.17);frame(performance.now()+33)');assert child.evaluate('active.getClip().name==="attack1"');assert page.locator('#heroPreviewName').text_content()=='La Lame d’Éclipse'
  run('var spacer=document.createElement("div");spacer.style.height="2000px";document.querySelector("#menu .panel").append(spacer);document.querySelector("#menu").scrollTop=document.querySelector("#menu").scrollHeight');page.wait_for_function('!heroPreviewRuntime.active',polling=50);child.wait_for_function('reviewActive===false',polling=50);child_before=child.evaluate('renderer.info.render.frame');child.evaluate('frame(performance.now()+50)');assert child.evaluate('renderer.info.render.frame')==child_before
  page.locator('.hero-preview').scroll_into_view_if_needed();page.wait_for_function('heroPreviewRuntime.active',polling=50);page.screenshot(path='/tmp/hero-preview-real-pc.png');page.click('#heroPreviewPlay');assert run('state==="playing"&&hero==="lame"');page.wait_for_function('document.querySelectorAll(".hero-preview-frame").length===0',polling=50);run('pause()');page.click('#back');page.locator('.hero-preview').scroll_into_view_if_needed();page.wait_for_function('heroPreviewRuntime.readyHero==="lame"',polling=50);assert run('heroPreviewActive()')
  assert run('!["constructor","toString","__proto__"].some(heroPreviewAllowed)')
  parts=urlsplit(page.url);page.goto(urlunsplit((parts.scheme,parts.netloc,parts.path,'hero=constructor','')));page.wait_for_function('avatarRuntime.status==="ready"',polling=50);assert run('hero==="rempart"&&!heroPreviewAllowed("constructor")')
  assert not errors,errors;b.close()
 print('PASS REAL: Rempart/Lame/Voltigeur/Lame, actual rendered model and attack clip, parent render frozen while visible, child render frozen offscreen, start disposes iframe, menu return recreates viewer.')
finally:server.shutdown();server.server_close()
