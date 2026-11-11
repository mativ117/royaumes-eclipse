"""Verify distinct kits, facing/cover, pact compatibility and mobile leap controls."""
from pathlib import Path
from playwright.sync_api import sync_playwright
html=(Path(__file__).resolve().parents[1]/'docs/index.html').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':900,'height':600});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html)
 assert page.evaluate('hero')=='rempart';assert page.evaluate('player.heavy.visible')
 page.click('[data-hero=voltigeur]');assert page.evaluate('player.light.visible')
 page.click('#start');run=page.evaluate
 assert run('p.max')==110 and run('hero')=='voltigeur'
 # A slash hits in front, never behind, and creates no rifle projectile.
 hit=run('''enemies.forEach(e=>cleanupObject(e.root));enemies=[];p.x=0;p.z=6;p.vx=p.vz=0;p.inv=999;aim=targetAim=0;mouseAim=false;
 var front=spawn(0,3.5,"archer"),behind=spawn(0,8.5,"archer");front.hp=behind.hp=1000;front.mode=behind.mode="recover";front.timer=behind.timer=999;
 fire();({front:front.hp,behind:behind.hp,bullets:bullets.length,combo:p.combo})''')
 assert hit=={'front':956,'behind':1000,'bullets':0,'combo':1},hit
 combo=run('front.x=0;front.z=3.5;p.shot=0;fire();front.x=0;front.z=3.5;p.shot=0;fire();({hp:front.hp,combo:p.combo})')
 assert combo=={'hp':846,'combo':3},combo
 # Cover blocks the attack, even if the enemy is inside melee range.
 hp=run('front.x=0;front.z=3.5;obstacle(0,4.5,4,.4,2);p.shot=0;fire();front.hp')
 assert hp==846
 # Leap has real airtime, hits once on landing, and interrupts a nearby boss.
 leap=run('''chooseBoon("vigor");setupRoom(2);p.x=0;p.z=-3.5;p.vx=p.vz=0;p.inv=0;boss.mode="windup";boss.timer=999;power();hurt(20);p.absorbLock=0;hurt(20);p.absorbLock=0;hurt(20);({hp:p.hp,charge:p.overcharge,leap:p.leap})''')
 assert leap=={'hp':150,'charge':3,'leap':.75},leap
 run('for(let i=0;i<20;i++)update(1/60)');assert run('player.root.position.y')>2
 landing=run('for(let i=0;i<30;i++)update(1/60);({mode:boss.mode,hp:boss.hp,leap:p.leap})')
 assert landing=={'mode':'recover','hp':605,'leap':0},landing
 run('aim=targetAim=0;p.shot=0;fire()');assert run('boss.hp')==501
 run('p.dash=0;dash()');assert abs(run('p.dash')-1.75)<.1
 run('p.inv=0;p.dashT=0;p.leap=0;hurt(999)');assert run('state')=='lost'
 page.click('#resume');assert run('hero')=='voltigeur' and run('room')==2 and run('p.max')==150
 page.click('#pause');page.click('#back');page.click('#start');run('chooseBoon("haste")');assert run('p.max')==80
 run('dash()');assert run('decoy!==null') and run('p.dash')<=.8
 # Finish all room transitions with the melee hero and win via real melee attacks.
 run('p.inv=999;p.x=0;p.z=-15;p.vx=p.vz=0;update(1/60)');assert run('room')==1
 run('p.x=0;p.z=-11;update(1/60);p.x=0;p.z=-15;update(1/60)');assert run('room')==2
 run('p.x=0;p.z=-3.5;p.inv=999;boss.mode="recover";boss.timer=99;clearHazards();aim=targetAim=0;mouseAim=false;shooting=true;for(let i=0;i<600;i++)update(1/60);shooting=false')
 assert run('boss.dead')
 run('p.x=0;p.z=-15;update(1/60)');assert run('state')=='won'
 # Switch back: a fresh Rempart has its own original stats and ranged weapon.
 page.click('#back');page.click('[data-hero=rempart]');page.click('#start')
 assert run('p.max')==150 and run('player.heavy.visible')
 run('fire()');assert run('bullets.length')>0
 # Portrait and landscape: select Voltigeur, move+attack, keep touch active through blur, then leap.
 for viewport in [{'width':390,'height':844},{'width':844,'height':390}]:
  ctx=b.new_context(viewport=viewport,has_touch=True,is_mobile=True);m=ctx.new_page();m.on('pageerror',lambda e:errors.append(str(e)));m.set_content(html)
  m.tap('[data-hero=voltigeur]');m.tap('#start');m.evaluate('p.inv=999')
  assert m.locator('#fire').inner_text()=='Frapper'
  cdp=ctx.new_cdp_session(m);stick=m.locator('#stick').bounding_box();fire=m.locator('#fire').bounding_box()
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':stick['x']+stick['width']/2+28,'y':stick['y']+stick['height']/2,'id':1},{'x':fire['x']+fire['width']/2,'y':fire['y']+fire['height']/2,'id':2}]})
  m.wait_for_timeout(250);m.evaluate('window.dispatchEvent(new Event("blur"))');m.wait_for_timeout(200)
  assert m.evaluate('state')=='playing' and m.evaluate('shotCount')>0 and m.evaluate('p.x')>0
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
  m.tap('#power');m.wait_for_timeout(150);assert m.evaluate('p.leap')>0
  assert m.evaluate('player.root.position.y')>0
  m.screenshot(path='/tmp/royaumes-v05-voltigeur-'+str(viewport['width'])+'.png');ctx.close()
 assert not errors,errors
 b.close();print('PASS: selection and distinct stats/meshes; front/back melee, 3-hit combo, cover; leap airtime/landing/interrupt; both pacts; retry and whole-level melee victory; switch back to ranged hero; mobile move+attack+blur+leap in portrait and landscape. No JS errors.')
