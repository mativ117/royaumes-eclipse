"""Dodge integration, input buffer, melee motion and crowd spacing."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content('<script>requestAnimationFrame=()=>0</script>'+(ROOT/'docs/index.html').read_text());page.click('#start');run=page.evaluate
 run('soundOn=false;p.inv=999;for(const e of enemies)e.dead=true;enemies=[];')
 result=run('''(()=>{function travel(hz){resetHeroAt(-6,25);p.dx=1;p.dz=0;p.dashElapsed=0;for(let i=0;i<Math.ceil(DODGE_DURATION*hz);i++)advanceHeroMotion(1/hz);return p.x+6;}return {slow:travel(30),fast:travel(120),burst:dodgeTravel(0,.04),tail:dodgeTravel(.24,.28)};})()''')
 assert abs(result['slow']-4.2)<1e-6 and abs(result['fast']-4.2)<1e-6,result
 assert result['burst']>result['tail']*5,result
 run('resetHeroAt(-6,25);p.dash=.08;requestDodge();for(let i=0;i<6;i++)update(1/60)')
 assert run('p.dashT>0&&p.dash>0&&p.dodgeBuffer===0'),'A near-ready dodge press must be retained'
 run('resetHeroAt(-6,25);p.dash=.3;requestDodge();for(let i=0;i<24;i++)update(1/60)')
 assert run('p.dashT===0'),'Expired buffer must not trigger a surprise dodge'
 run('resetHeroAt(0,25);hero="voltigeur";applyHero();aim=0;beginAttack();updateAttack(.16)')
 assert run('p.z<24.45&&p.z>24.35'),'A melee strike must advance with its windup'
 run('cancelAttack();resetHeroAt(0,-98);var a=spawn(.2,-97.7,"warden"),b=spawn(.22,-97.7,"warden");for(let i=0;i<60;i++)resolveActorContacts(1/60)')
 assert run('distance(a,b)>.94&&distance(p,a)>.90&&distance(p,b)>.90'),'Bodies must separate instead of stacking'
 run('a.mode=b.mode="windup";var c=spawn(1,-97,"warden")')
 assert not run('canCommitMelee(c)'),'Two nearby committed wardens reserve the attack slots'
 run('a.mode="recover"');assert run('canCommitMelee(c)')
 assert run('sanctuary.root.children.filter(o=>o.userData.shadowRole==="overhead").length>=3')
 assert run('sanctuary.root.children.filter(o=>o.userData.shadowRole==="overhead").every(o=>!o.castShadow)&&!sanctuary.monument.castShadow'),'Overhead ornaments must not stripe the arena with shadows'
 assert not errors,errors
 b.close()
print('PASS: frame-independent decelerating dodge, buffer expiry, melee advancement, actor separation, attack slots and overhead shadow exclusion.')
