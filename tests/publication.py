"""Verify the generated site, reproducible build and historical URL redirect."""
from pathlib import Path
import functools
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import subprocess
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
paths=['index.html','cathedrale-v03.html','version.json','.nojekyll']
before={p:(ROOT/'docs'/p).read_bytes() for p in paths}
subprocess.run(['python',str(ROOT/'scripts/build.py')],check=True)
assert before=={p:(ROOT/'docs'/p).read_bytes() for p in paths},'Build must be reproducible'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}'
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  ctx=b.new_context(viewport={'width':740,'height':390},has_touch=True,is_mobile=True)
  page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url+'/cathedrale-v03.html?v=04')
  page.wait_for_url('**/index.html?v=04')
  assert 'Version 0.4' in page.locator('#menu').text_content()
  page.tap('#start');assert page.evaluate('state')=='playing'
  page.evaluate('window.dispatchEvent(new Event("blur"))');assert page.evaluate('state')=='playing'
  page.evaluate('p.inv=999;p.x=9;p.z=-7;update(1/60)');page.tap('#interact')
  assert page.evaluate('state')=='choice';page.tap('#sealPact')
  assert page.evaluate('boon')=='haste'
  page.goto(url+'/');assert 'Version 0.4' in page.locator('#menu').text_content()
  response=ctx.request.get(url+'/version.json');assert response.json()['version']=='0.4'
  assert ctx.request.get(url+'/src/game.js').status==404
  assert ctx.request.get(url+'/design/CONCEPTION.md').status==404
  assert not errors,errors
  # Also support the current Pages setting (repository root) without admin API access.
  fallback=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
  Thread(target=fallback.serve_forever,daemon=True).start()
  try:
   for entry in ['/', '/cathedrale-v03.html']:
    page.goto(f'http://127.0.0.1:{fallback.server_port}'+entry+'?entry=root')
    page.wait_for_url('**/docs/index.html?entry=root')
    assert 'Version 0.4' in page.locator('#menu').text_content()
  finally:fallback.shutdown();fallback.server_close()
  page.screenshot(path='/tmp/royaumes-publication-preview.png')
  b.close()
 print('PASS: reproducible build; historical URL preserves query and opens current game; mobile gameplay and choice; blur fix; canonical homepage; version metadata; source and design not published.')
finally:server.shutdown();server.server_close()
