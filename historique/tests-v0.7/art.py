from pathlib import Path
from playwright.sync_api import sync_playwright
html=(Path(__file__).resolve().parents[1]/'docs/index.html').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 errors=[]
 for viewport in [{'width':1280,'height':800},{'width':844,'height':390},{'width':390,'height':844}]:
  mobile=viewport['width']!=1280
  context=b.new_context(viewport=viewport,is_mobile=mobile,has_touch=mobile)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html)
  page.click('#start');page.evaluate('p.inv=999');page.wait_for_timeout(200)
  state=page.evaluate('({paving:!!floor.material.map, grid:grid.visible, fog:art.haze.visible, blockers:obstacles.length,calls:renderer.info.render.calls,triangles:renderer.info.render.triangles})')
  assert state['paving'] and not state['grid'] and state['fog'] and state['blockers']==3,state
  assert state['calls']<300,state
  page.screenshot(path=f"/tmp/royaumes-v07-{viewport['width']}.png")
  page.click('#pause');page.click('#back');page.select_option('#quality','light');page.click('[data-hero=voltigeur]');page.click('#start');page.wait_for_timeout(200)
  assert not page.evaluate('art.haze.visible') and not page.evaluate('art.detail.visible')
  assert page.evaluate('renderer.getPixelRatio()')==1
  assert page.evaluate('obstacles.length')==3
  page.evaluate('window.dispatchEvent(new Event("blur"))');assert page.evaluate('state')=='playing'
  if mobile:assert page.locator('#mobile').is_visible()
  page.screenshot(path=f"/tmp/royaumes-v07-light-{viewport['width']}.png")
  context.close()
 assert not errors,errors
 b.close();print('PASS: textured rendering on desktop/landscape/portrait, draw-call budget, light quality, both heroes, unchanged collisions and blur regression. No JS errors.')
