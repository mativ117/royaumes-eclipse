from pathlib import Path
from playwright.sync_api import sync_playwright
html=(Path(__file__).resolve().parents[1]/'docs/index.html').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':840,'height':540});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.click('#start');run=page.evaluate
 # Fixed facing makes front protection and flanking materially different.
 result=run('var guard=enemies.find(e=>e.type==="sentinel");guard.mode="idle";guard.facing=0;guard.hp=1000;damage(guard,100,{x:guard.x,z:guard.z-4});var frontDamage=1000-guard.hp;damage(guard,100,{x:guard.x,z:guard.z+4});({front:frontDamage,total:1000-guard.hp})')
 assert result=={'front':15,'total':115},result
 result=run('guard.mode="recover";guard.hp=1000;damage(guard,100,{x:guard.x,z:guard.z-4});guard.hp')
 assert result==900
 # A charge locks its direction; an obstacle stops it and exposes the guard.
 run('guard.x=0;guard.z=5;guard.mode="idle";guard.timer=0;p.x=0;p.z=12;p.inv=999;updateSentinel(guard,1/60)');assert run('guard.mode')=='windup'
 facing=run('guard.facing');run('p.x=8;updateSentinel(guard,.5)');assert run('guard.facing')==facing
 run('obstacle(0,7.2,3,.5,2);updateSentinel(guard,.6);for(let i=0;i<40;i++)updateSentinel(guard,1/60)');assert run('guard.mode')=='recover'
 # Bell is a single-use context action, clears danger and yields a real recovery window.
 run('chooseBoon("vigor");setupRoom(2);p.x=0;p.z=5;p.vx=p.vz=0;p.inv=999;boss.mode="windup";boss.timer=99;addHazard(0,5,3,1);enemyShot(boss,0);updateInteraction()')
 page.keyboard.press('f')
 assert run('bell.used') and run('boss.mode')=='recover' and run('boss.timer')>3
 assert run('hazards.length')==0 and not run('bullets.some(b=>b.enemy)')
 result=run('boss.timer=1;ringBell();boss.timer');assert result==1
 # Retry resets the encounter and bell, not the selected hero or pact.
 run('p.inv=0;p.shield=0;hurt(999)');page.click('#resume');assert not run('bell.used') and run('boon')=='vigor'
 page.screenshot(path='/tmp/royaumes-v06-bell.png')
 for viewport in [{'width':390,'height':844},{'width':844,'height':390}]:
  ctx=b.new_context(viewport=viewport,is_mobile=True,has_touch=True);m=ctx.new_page();m.on('pageerror',lambda e:errors.append(str(e)));m.set_content(html);m.tap('[data-hero=voltigeur]');m.tap('#start');m.evaluate('chooseBoon("haste");setupRoom(2);p.x=0;p.z=5;p.inv=999;updateInteraction()');m.tap('#interact');assert m.evaluate('bell.used');assert m.evaluate('state')=='playing';m.evaluate('window.dispatchEvent(new Event("blur"))');assert m.evaluate('state')=='playing';ctx.close()
 assert not errors,errors
 b.close();print('PASS: directional guard, flank damage, recovery, locked charge, wall collision, one-use bell, danger cancellation, retry and portrait/landscape context action. No JS errors.')
