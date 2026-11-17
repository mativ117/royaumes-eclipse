"""Inline hero viewer: lifecycle/security with a stub, then real responsive embedding."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/index.html?hero=rempart'
STUB='''<!doctype html><html><body><label>Geste <select><option>Garde</option><option>Marcher</option></select></label><script>
let selected=new URLSearchParams(location.search).get('hero');window.reviewActive=false;window.received=[];
const ready=()=>parent.postMessage({type:'review-ready',hero:selected},location.origin);
addEventListener('message',e=>{if(e.source!==parent||e.origin!==location.origin)return;received.push(e.data);if(e.data.type==='review-hero'){selected=e.data.hero;ready();}else if(e.data.type==='review-active')window.reviewActive=e.data.active;else if(e.data.type==='review-dispose')window.disposed=true;});addEventListener('load',ready);
</script></body></html>'''
FAKE_IO='''window.IntersectionObserver=class{constructor(callback,options){this.callback=callback;this.options=options;}observe(target){this.target=target;}disconnect(){}emit(visible){this.callback([{target:this.target,isIntersecting:visible,intersectionRatio:visible?1:0}]);}};'''
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);errors=[]
  ctx=b.new_context(viewport={'width':1366,'height':900});ctx.add_init_script('requestAnimationFrame=()=>0;'+FAKE_IO);page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/atelier-lame.html?**',lambda route:route.fulfill(content_type='text/html',body=STUB));page.goto(url);page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
  assert run('typeof initHeroPreview==="function"&&!!heroPreviewRuntime.panel')
  assert page.locator('.hero-preview-frame').count()==0,'No iframe before intersection'
  run('heroPreviewRuntime.observer.emit(true)');page.wait_for_function('heroPreviewRuntime.readyHero==="rempart"',polling=50);assert run('heroPreviewActive()')
  frame=page.locator('.hero-preview-frame').element_handle().content_frame();frame.wait_for_function('window.reviewActive===true',polling=50)
  run('heroPreviewRuntime.observer.emit(false)');page.wait_for_function('!heroPreviewRuntime.active',polling=50);assert not run('heroPreviewActive()');assert page.locator('.hero-preview-frame').count()==1;frame.wait_for_function('window.reviewActive===false',polling=50)
  run('heroPreviewRuntime.observer.emit(true)');page.wait_for_function('heroPreviewRuntime.active',polling=50)
  page.click('[data-hero=voltigeur]');page.wait_for_function('heroPreviewRuntime.readyHero==="voltigeur"',polling=50);assert page.locator('#heroPreviewName').text_content()=='Le Voltigeur';assert 'prototype' in page.locator('#heroPreviewTruth').text_content()
  run('heroPreviewRuntime.readyHero=null;heroPreviewRuntime.message="Sentinelle";heroPreviewFeedback();window.dispatchEvent(new MessageEvent("message",{origin:"https://invalid.example",source:heroPreviewRuntime.frame.contentWindow,data:{type:"review-ready",hero:"voltigeur"}}))');assert run('heroPreviewRuntime.readyHero===null')
  run('window.dispatchEvent(new MessageEvent("message",{origin:location.origin,source:window,data:{type:"review-ready",hero:"voltigeur"}}))');assert run('heroPreviewRuntime.readyHero===null')
  run('heroPreviewSelect("eclipse")');assert run('heroPreviewRuntime.selected==="voltigeur"'),'Locked secret must not be previewed'
  frame.evaluate('parent.postMessage({type:"review-ready",hero:"eclipse"},location.origin)');page.wait_for_timeout(40);assert run('heroPreviewRuntime.readyHero===null')
  frame.evaluate('parent.postMessage({type:"review-ready",hero:"voltigeur"},location.origin)');page.wait_for_function('heroPreviewRuntime.readyHero==="voltigeur"',polling=50)
  frame.evaluate('parent.postMessage({type:"review-error",hero:"voltigeur"},location.origin)');page.wait_for_function('document.querySelector("#heroPreviewFeedback").textContent.includes("n’a pas pu")',polling=50);assert run('heroPreviewRuntime.readyHero===null&&heroPreviewRuntime.timeout===null');frame.evaluate('parent.postMessage({type:"review-ready",hero:"voltigeur"},location.origin)');page.wait_for_function('heroPreviewRuntime.readyHero==="voltigeur"',polling=50)
  run('document.querySelector("#start").disabled=true');page.wait_for_function('document.querySelector("#heroPreviewPlay").disabled',polling=50);run('document.querySelector("#start").disabled=false');page.wait_for_function('!document.querySelector("#heroPreviewPlay").disabled',polling=50)
  run('buildHeroGallery()');page.click('[data-hero=rempart]');page.wait_for_function('heroPreviewRuntime.readyHero==="rempart"',polling=50)
  page.select_option('#playMode','coop');page.click('#partyOptions summary');page.select_option('#partySize','4');page.click('#heroPreviewPlay');assert run('state==="menu"');page.wait_for_function('document.querySelector("#heroPreviewFeedback").textContent.includes("manette")',polling=50);assert page.locator('.hero-preview-frame').count()==1
  page.select_option('#playMode','solo');page.click('#heroPreviewPlay');assert run('state==="playing"');page.wait_for_function('document.querySelectorAll(".hero-preview-frame").length===0',polling=50);assert not run('heroPreviewActive()')
  run('pause()');page.click('#back');page.wait_for_function('heroPreviewRuntime.frame!==null',polling=50);page.wait_for_function('heroPreviewRuntime.readyHero==="rempart"',polling=50)
  run('localProfile.secret=[true,true,true];persistProfile();buildHeroGallery()');page.click('[data-hero=eclipse]');page.wait_for_function('heroPreviewRuntime.readyHero==="eclipse"',polling=50);assert not page.locator('[data-hero=eclipse]').is_disabled();ctx.close()
  # Native observer + stub iframe: actual responsive layout/scroll without a second WebGL renderer.
  for width,height in [(1024,768),(1366,900),(390,844),(844,390)]:
   ctx=b.new_context(viewport={'width':width,'height':height},is_mobile=width<900,has_touch=width<900);ctx.add_init_script('requestAnimationFrame=()=>0');p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/atelier-lame.html?**',lambda route:route.fulfill(content_type='text/html',body=STUB));p.goto(url);p.wait_for_function('avatarRuntime.status==="ready"',polling=50);p.locator('.hero-preview').scroll_into_view_if_needed();p.wait_for_function('heroPreviewRuntime.readyHero==="rempart"',polling=50)
   result=p.evaluate('''()=>{const gallery=document.querySelector('.heroChoices'),panel=document.querySelector('.hero-preview'),r=gallery.getBoundingClientRect(),s=panel.getBoundingClientRect();return{width:innerWidth,scroll:document.documentElement.scrollWidth,galleryHeight:r.height,columns:getComputedStyle(document.querySelector('.hero-selection')).gridTemplateColumns.split(' ').length,overlap:r.left<s.right&&r.right>s.left&&r.top<s.bottom&&r.bottom>s.top};}''');assert result['scroll']<=width and not result['overlap'] and result['galleryHeight']<=500,result
   assert result['columns']==(1 if width<=700 else 2),result
   assert p.locator('#chapterSelect').count()==1 and p.locator('#playMode').count()==1 and p.locator('#start').count()==1
   p.screenshot(path=f'/tmp/hero-selection-{width}.png');ctx.close()
  # Autonomous HTML/about:blank must never attempt a relative embedded viewer.
  p=b.new_page();p.add_init_script('requestAnimationFrame=()=>0');p.on('pageerror',lambda e:errors.append(str(e)));p.set_content('<script>requestAnimationFrame=()=>0</script>'+(ROOT/'docs/index.html').read_text());p.wait_for_function('avatarRuntime.status==="ready"',polling=50);assert p.locator('.hero-preview-frame').count()==0;assert not p.evaluate('heroPreviewActive()');assert 'page en ligne' in p.locator('#heroPreviewFeedback').text_content();p.close()
  assert not errors,errors;b.close()
 print('PASS: lazy inline viewer, source/origin checks, secret gate, current selection and rebuilt cards, loading/play feedback, pause/dispose/recreate, responsive bounded gallery and standalone fallback. Stub validates parent protocol; real viewer integration is checked separately.')
finally:server.shutdown();server.server_close()
