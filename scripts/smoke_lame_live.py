"""Review the real published studio and launch its hero in the actual game."""
from pathlib import Path
from playwright.sync_api import sync_playwright
version=(Path(__file__).resolve().parents[1]/'VERSION').read_text().strip()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page(viewport={'width':1100,'height':760});page.add_init_script('requestAnimationFrame=()=>0');errors=[];missing=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:missing.append(r.url) if r.status>=400 else None)
 page.goto('https://mativ117.github.io/royaumes-eclipse/docs/atelier-lame.html?v='+version);page.wait_for_function('window.reviewReady===true',polling=50);assert page.evaluate('Object.keys(actions).length')==23
 for name in ['idle','attack1','attack2','attack3','dodge_left']:
  page.select_option('#motion',name);page.evaluate('mixer.update(.16);frame(performance.now())')
 page.click('a.play');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);assert page.evaluate('hero')=='lame';page.click('#start');page.evaluate('soundOn=false;p.inv=999;for(let i=0;i<20;i++)update(1/60);updateVisualWorld();renderPresentation()')
 assert page.evaluate('avatarRuntime.current.state')=='guard'
 page.click('#inputSettingsButton');assert page.evaluate('state')=='input-settings';page.keyboard.press('Escape');assert page.evaluate('state')=='playing'
 assert not errors,errors
 assert not missing,missing
 b.close()
print('PASS: public 3D studio, 23 clips, three attacks and dodge, link selects Lame, game starts and Commands opens/closes without missing requests or JS errors.')
