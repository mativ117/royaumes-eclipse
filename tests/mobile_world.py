from pathlib import Path
from playwright.sync_api import sync_playwright
html=(Path(__file__).resolve().parents[1]/'docs/index.html').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 errors=[]
 for viewport in [{'width':390,'height':844},{'width':844,'height':390}]:
  ctx=b.new_context(viewport=viewport,is_mobile=True,has_touch=True);m=ctx.new_page();m.on('pageerror',lambda e:errors.append(str(e)));m.set_content(html);m.select_option('#quality','light');m.tap('[data-hero=voltigeur]');m.tap('#start');m.evaluate('soundOn=false;p.inv=999')
  assert m.evaluate('world.onGround(p.x,p.z)')
  cdp=ctx.new_cdp_session(m);stick=m.locator('#stick').bounding_box();attack=m.locator('#fire').bounding_box()
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':stick['x']+stick['width']/2+28,'y':stick['y']+stick['height']/2,'id':1},{'x':attack['x']+attack['width']/2,'y':attack['y']+attack['height']/2,'id':2}]})
  m.wait_for_timeout(250);m.evaluate('window.dispatchEvent(new Event("blur"))');m.wait_for_timeout(200)
  assert m.evaluate('state')=='playing' and m.evaluate('p.x')>0 and m.evaluate('shotCount')>0
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});assert not m.evaluate('shooting')
  m.tap('#mapButton');assert m.evaluate('state')=='map';t=m.evaluate('t');m.wait_for_timeout(150);assert m.evaluate('t')==t
  m.screenshot(path='/tmp/royaumes-v08-map-'+str(viewport['width'])+'.png');m.tap('#closeMap');assert m.evaluate('state')=='playing'
  m.evaluate('p.x=9;p.z=7;p.vx=p.vz=0;update(1/60)');m.tap('#interact');assert m.evaluate('state')=='choice',m.evaluate('({state,boon,target:interactionTarget(),choice:document.querySelector("#choicePanel").hidden})');m.tap('#sealPact');assert m.evaluate('boon')=='haste'
  assert not m.evaluate('shrines[0].tag.visible')
  m.evaluate('p.x=0;p.z=-38;p.inv=999;update(1/60)');assert m.evaluate('campaign.checkpoint.id')=='crossing'
  m.evaluate('p.inv=0;p.shield=0;p.leap=0;p.dashT=0;hurt(999)');m.tap('#resume');assert m.evaluate('state')=='playing' and m.evaluate('p.z')<-30
  m.evaluate('p.x=20;p.z=-18;p.inv=999;');m.wait_for_timeout(350);m.screenshot(path='/tmp/royaumes-v08-mobile-'+str(viewport['width'])+'.png')
  assert m.evaluate('renderer.info.render.calls')<400
  ctx.close()
 assert not errors,errors
 b.close();print('PASS: portrait+landscape real multitouch, blur, map pause/resume, pact selection, hidden consumed labels, refuge retry, light quality and render budget. No JS errors.')
