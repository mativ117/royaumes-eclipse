"""Real keyboard remapping, fixed coop controls, and non-overlapping desktop maps."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/'
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':1366,'height':768});ctx.add_init_script('requestAnimationFrame=()=>0');page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
  page.select_option('#presentation','detailed');page.click('#start');run('soundOn=false;p.inv=999');layouts=[]
  for width,height in [(1024,768),(1366,768),(1920,1080)]:
   page.set_viewport_size({'width':width,'height':height});page.wait_for_function('document.querySelector("#miniMap").getBoundingClientRect().top>=document.querySelector(".hudButtons").getBoundingClientRect().bottom+13',polling=50)
   data=run('''()=>{const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return{x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height}};return{width:innerWidth,toolbar:rect('.hudButtons'),minimap:rect('#miniMap'),plate:rect('.hud .plate')};}''');layouts.append(data);assert data['minimap']['y']>=data['toolbar']['bottom']+13,data
   page.keyboard.press('m');assert run('state==="map"');assert run('getComputedStyle(document.querySelector("#hud")).visibility==="hidden"&&getComputedStyle(document.querySelector("#miniMap")).visibility==="hidden"')
   assert run('getComputedStyle(document.querySelector("#largeMap")).position==="static"');assert run('document.documentElement.scrollWidth<=innerWidth');page.keyboard.press('Escape');assert run('state==="playing"')
  Path('/tmp/royaumes-input-after.json').write_text(json.dumps(layouts,indent=2))
  page.set_viewport_size({'width':1366,'height':768});page.click('#inputSettingsButton');assert run('state==="input-settings"');assert page.locator('#inputRows button').count()==11
  page.focus('#inputSettingsClose');page.keyboard.press('Space');assert run('state==="playing"'),'Space must still activate focused menu buttons';page.click('#inputSettingsButton')
  page.click('[data-input-action=dodge]');page.keyboard.press('e');assert 'déjà' in page.locator('#inputFeedback').text_content();assert run('!inputBindings.dodge&&inputCapture==="dodge"')
  page.keyboard.press('Escape');assert run('state==="input-settings"&&inputCapture===null&&!inputBindings.dodge')
  page.click('[data-input-action=dodge]');page.keyboard.down('h');assert run('inputBindings.dodge.code==="KeyH"');page.click('#inputSettingsClose');page.keyboard.down('h');assert run('p.dash===0'),'Captured key must not echo into gameplay';page.keyboard.up('h');page.keyboard.press('Space');assert run('p.dash===0'),'Old dodge key must stop working';page.keyboard.press('h');assert run('p.dash>0')
  run('p.dash=p.dashT=0;p.dashElapsed=DODGE_DURATION;localProfile.name="Clavier test";persistProfile();var profileBefore=localStorage.getItem("royaumes-profile-v1")')
  def bind(action,key):
   page.click('[data-input-action='+action+']');page.keyboard.press(key);assert run('inputCapture===null'),(action,page.locator('#inputFeedback').text_content())
  page.click('#inputSettingsButton')
  for action,key in [('power','t'),('interact','v'),('map','k'),('guide','o'),('forward','i'),('attack','u'),('extra','l')]:bind(action,key)
  assert run('localStorage.getItem("royaumes-profile-v1")===profileBefore'),'Input settings must not rewrite profile data'
  page.click('#inputSettingsClose');run('p.power=0;p.shield=0');page.keyboard.press('e');assert run('p.power===0');page.keyboard.press('t');assert run('p.power>0&&p.shield>0')
  run('var powerCalls=0,originalPower=power;power=()=>powerCalls++;void 0');page.keyboard.down('t');page.keyboard.down('t');page.keyboard.up('t');assert run('powerCalls===1'),run('({powerCalls,state,suppressed:[...inputSuppressedCodes],capture:inputCapture})');run('power=originalPower;void 0')
  run('resetHeroAt(0,25)');page.keyboard.down('w');assert run('movement().z===0');page.keyboard.up('w');page.keyboard.down('ArrowUp');assert run('movement().z===0');page.keyboard.up('ArrowUp');page.keyboard.down('i');assert run('movement().z<0');run('for(let i=0;i<15;i++)update(1/60)');page.keyboard.up('i');assert run('p.z<25')
  run('resetHeroAt(0,25);p.shot=0;cancelAttack();var oldShots=shotCount');page.keyboard.down('u');run('for(let i=0;i<45;i++)update(1/60)');page.keyboard.up('u');assert run('shotCount-oldShots>=2&&!inputAttackHeld()')
  page.keyboard.press('m');assert run('state==="playing"');page.keyboard.press('k');assert run('state==="map"');page.keyboard.press('k');assert run('state==="playing"');run('guideRevealUntil=0');page.keyboard.press('g');assert run('guideRevealUntil===0');page.keyboard.press('o');assert run('guideRevealUntil>t')
  run('boon="vigor";resetHeroAt(16,-4.5);campaign.trials.bells.read=false;updateDesign(1/60)');assert page.locator('#interact').text_content().startswith('V · ');page.keyboard.press('f');assert run('!campaign.trials.bells.read');page.keyboard.press('v');assert run('campaign.trials.bells.read')
  page.click('#helpButton');assert run('document.querySelector("#helpDialog").open&&state==="paused"');assert 'interaction V' in page.locator('#inputHelpSummary').text_content();page.keyboard.press('Escape');assert run('!document.querySelector("#helpDialog").open&&state==="playing"')
  run('var field=document.createElement("input");field.id="testField";document.body.append(field);field.focus();p.power=0');page.keyboard.type('t');assert run('p.power===0&&document.querySelector("#testField").value==="t"');run('field.remove();releaseMenuFocus()')
  run('pause()');page.click('#inputSettingsPauseButton');assert run('state==="input-settings"&&inputReturnState==="paused"');page.keyboard.press('Escape');assert run('state==="paused"');run('resume()')
  page.reload();page.wait_for_function('avatarRuntime.status==="ready"',polling=50);assert run('inputBindings.dodge.code==="KeyH"&&inputBindings.forward.code==="KeyI"&&localProfile.name==="Clavier test"')
  page.select_option('#playMode','coop');page.click('#inputSettingsMenuButton');assert page.locator('[data-input-action=dodge]').is_disabled();assert 'J2 clavier' in page.locator('#inputCoop').text_content();assert page.locator('[data-input-action=dodge]').text_content()=='Espace';page.click('#inputSettingsClose');page.click('#start');page.wait_for_function('localParty.length===1',polling=50);run('soundOn=false;p.inv=999');page.keyboard.press('h');assert run('p.dash===0');page.keyboard.down('ArrowRight');assert run('movement().x===0&&partyKeys.has("ArrowRight")');page.keyboard.up('ArrowRight');page.keyboard.press('Space');assert run('p.dash>0')
  page.reload();page.wait_for_function('avatarRuntime.status==="ready"',polling=50);page.click('#inputSettingsMenuButton');page.click('#inputReset');assert run('Object.keys(inputBindings).length===0&&JSON.parse(localStorage.getItem(INPUT_STORAGE_KEY)).dodge===undefined');page.keyboard.press('Escape');page.click('#start');page.keyboard.press('Space');assert run('p.dash>0')
  run('localStorage.setItem(INPUT_STORAGE_KEY,"{bad json")');page.reload();page.wait_for_function('avatarRuntime.status==="ready"',polling=50);assert run('Object.keys(inputBindings).length===0&&localProfile.name==="Clavier test"');ctx.close()
  for width,height in [(390,844),(1366,1024)]:
   mobile=b.new_context(viewport={'width':width,'height':height},is_mobile=True,has_touch=True);mobile.add_init_script('requestAnimationFrame=()=>0');p=mobile.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(url);p.wait_for_function('avatarRuntime.status==="ready"',polling=50);p.select_option('#presentation','detailed');p.click('#start');p.wait_for_timeout(80)
   if width>900:assert p.evaluate('document.querySelector("#miniMap").getBoundingClientRect().top>=document.querySelector(".hudButtons").getBoundingClientRect().bottom+13')
   else:assert p.evaluate('getComputedStyle(document.querySelector("#miniMap")).display==="none"')
   p.click('#inputSettingsButton');assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.click('#inputSettingsClose');assert p.evaluate('state==="playing"');mobile.close()
  assert not errors,errors;b.close()
 print('PASS: desktop map/tool separation, map modal isolation, effective solo keyboard remapping, conflict/cancel/reset, held attack, repeat suppression, form focus, Escape/help, persistence and fixed coop/J2 controls; portrait and wide touch layout.')
finally:server.shutdown();server.server_close()
