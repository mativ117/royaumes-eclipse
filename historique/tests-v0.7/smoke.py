from pathlib import Path
from playwright.sync_api import sync_playwright
html=(Path(__file__).resolve().parents[1] / 'docs/index.html').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.click('#start')
 def run(js):return page.evaluate(js)
 # Fixed-step movement accelerates, brakes, and slides against cover.
 run('p.inv=999;keys.add("d");update(1/60)');assert 0<run('p.vx')<6
 run('for(let i=0;i<60;i++)update(1/60);keys.clear()');assert run('p.x')>4
 run('for(let i=0;i<30;i++)update(1/60)');assert abs(run('p.vx'))<.01
 run('p.x=0;p.z=3;p.vx=p.vz=0;keys.add("w");for(let i=0;i<90;i++)update(1/60);keys.clear()');assert run('p.z')>=1.48
 run('dash();for(let i=0;i<15;i++)update(1/60)');assert run('p.z')>=1.48
 # No endless spawning, and neither initial guard is required to open the exit.
 assert run('enemies.length')==2
 run('p.x=9;p.z=-7;update(1/60)');assert run('boon')=='';page.keyboard.press('f');assert run('state')=='choice';page.click('#sealPact');assert run('boon')=='haste';assert run('portal.visible');assert run('kills')==0
 run('p.x=0;p.z=-15;update(1/60)');assert run('room')==1;assert run('traps.length')==6
 # Trap warning, safe gap, active damage, then invulnerability during dodge.
 run('enemies.forEach(e=>e.timer=999);bullets.forEach(b=>scene.remove(b.mesh));bullets=[];p.x=-7;p.z=5;p.hp=150;p.inv=0;t=2.5;update(1/60)');assert run('p.hp')==150
 run('p.x=0;p.inv=0;update(1/60)');assert run('p.hp')==128
 run('p.inv=0;p.dashT=.1;p.hp=150;update(1/60)');assert run('p.hp')==150
 run('p.dashT=0;p.inv=999;p.x=0;p.z=-11;update(1/60)');assert run('shard');assert run('portal.visible')
 run('p.x=0;p.z=-15;update(1/60)');assert run('room')==2
 # Armour matters, vulnerability window improves damage by 4x.
 run('boss.mode="idle";damage(boss,40)');assert run('boss.hp')==690
 run('boss.mode="recover";damage(boss,40)');assert run('boss.hp')==650
 # Interrupt only while close and winding up.
 run('p.x=0;p.z=-3;p.inv=999;boss.mode="windup";boss.timer=1;addHazard(0,-3,3,1);power()');assert run('boss.mode')=='recover';assert run('hazards.length')==0;assert run('p.shield')>2
 hp=run('p.hp');run('p.inv=0;hurt(50)');assert run('p.hp')==hp
 # Boss announces area, then recovers, and phase II adds projectiles.
 run('p.inv=999;boss.mode="idle";boss.timer=0;update(1/60)');assert run('hazards.length')>0
 run('boss.mode="windup";boss.timer=0;boss.hp=300;update(1/60)');assert run('boss.phase')==2;assert run('bullets.some(b=>b.enemy)')
 # Win through player projectiles rather than directly setting the boss dead.
 run('p.x=0;p.z=3;p.vx=p.vz=0;p.inv=999;boss.mode="recover";boss.timer=99;clearHazards();aim=targetAim=0;mouseAim=false;shooting=true;for(let i=0;i<360;i++)update(1/60);shooting=false')
 assert run('boss.dead');assert run('portal.visible')
 run('p.x=0;p.z=-15;update(1/60)');assert run('state')=='won'
 page.click('#back');page.click('#start');run('p.x=-9;p.z=-7;update(1/60)');page.keyboard.press('f');page.click('#sealPact');assert run('boon')=='vigor';assert run('p.max')==190
 page.keyboard.press('Escape');assert run('state')=='paused';old=run('t');page.wait_for_timeout(100);assert run('t')==old;page.click('#resume')
 run('p.inv=0;p.shield=0;p.dashT=0;hurt(999)');assert run('state')=='lost'
 page.click('#back');page.select_option('#quality','light');page.click('#start');run('p.inv=999');page.screenshot(path='/tmp/eclipse-v03-choice.png')
 run('setupRoom(2);p.inv=999;boss.mode="windup";boss.timer=1.2;addHazard(0,7,3.6,1.2)');page.screenshot(path='/tmp/eclipse-v03-boss.png')
 # Real multi-touch events: simultaneous movement + fire, then release.
 context=b.new_context(viewport={'width':844,'height':390},has_touch=True,is_mobile=True)
 m=context.new_page();m.on('pageerror',lambda e:errors.append(str(e)));m.set_content(html);m.tap('#start');m.evaluate('p.inv=999');assert m.locator('#mobile').is_visible()
 cdp=context.new_cdp_session(m);r=m.locator('#stick').bounding_box();f=m.locator('#fire').bounding_box();sx=r['x']+r['width']/2;sy=r['y']+r['height']/2
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':sx+30,'y':sy,'id':1},{'x':f['x']+30,'y':f['y']+30,'id':2}]})
 m.wait_for_timeout(350);assert m.evaluate('p.x')>0;assert m.evaluate('shotCount')>0
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});m.wait_for_timeout(100);assert not m.evaluate('shooting');assert m.evaluate('joy.x')==0
 m.tap('#power');assert m.evaluate('p.shield')>0
 m.screenshot(path='/tmp/eclipse-v03-mobile.png');assert not errors,errors
 print('PASS: acceleration/braking, cover and dash collisions, two exclusive boons, finite encounters, room transitions, trap gaps/damage/dodge, boss armour/recovery/interrupt/phase II, projectile victory, pause, defeat, real simultaneous mobile move+fire and shield. No JS errors.')
 b.close()
