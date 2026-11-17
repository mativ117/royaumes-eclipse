"""Shared-keyboard coop, simulated gamepads, revival, local duels and crown rules."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
# This regression describes archived 1.3 modes, intentionally absent from 1.4.
import json,sys
if json.loads((ROOT/'docs/version.json').read_text()).get('modes')==['solo']:
 print('SKIP: local coop/arena modes are archived in 1.3 and excluded from the published solo bundle.')
 sys.exit(0)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=browser.new_page(viewport={'width':1100,'height':760});page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
  run('soundOn=false;document.querySelector("#playMode").value="coop";beginCompleteRun();releaseMenuFocus();p.inv=999;')
  page.wait_for_function('localParty.length===1&&!partyLoading',polling=50)
  run('window.partyX=localParty[0].x;window.leaderX=p.x;');page.keyboard.down('ArrowRight');run('for(let i=0;i<45;i++)update(1/60)');page.keyboard.up('ArrowRight')
  assert run('localParty[0].x>partyX+1&&Math.abs(p.x-leaderX)<.01'),'Arrow keys must move J2 independently'
  page.keyboard.down('j');run('for(let i=0;i<12;i++)update(1/60)');page.keyboard.up('j');assert run('localParty[0].shot>0||localParty[0].attack'),'J2 attacks'
  page.keyboard.down('ControlRight');run('update(1/60)');page.keyboard.up('ControlRight');assert run('localParty[0].power>0&&p.power===0'),'Independent class ability'
  run('localParty[0].x=p.x+1.6;localParty[0].z=p.z;localParty[0].leap=0;localParty[0].vx=localParty[0].vz=0;p.inv=0;p.hp=1;hurt(10)');assert run('p.downed&&state==="playing"')
  page.keyboard.down('Enter');run('for(let i=0;i<165;i++)update(1/60)');page.keyboard.up('Enter');assert run('!p.downed&&p.hp>0'),'Ally revives leader through held interaction'
  run('localParty[0].hp=1;localParty[0].inv=0;localParty[0].shield=0;partyHurt(localParty[0],10);p.hp=1;p.inv=0;hurt(10)');assert run('state')=='lost'
  run('resume()');assert run('state==="playing"&&!p.downed&&localParty.every(a=>!a.downed&&a.hp===a.max)'),'Retry restores the local group'
  # Two extra gamepads control J3 and J4; no network/signaling involved.
  run('''window.fakePads=[0,1].map(i=>({axes:[i? -1:1,0,0,-1],buttons:Array.from({length:16},()=>({pressed:false}))}));Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>fakePads});document.querySelector('#partySize').value='4';beginCompleteRun();releaseMenuFocus();''')
  page.wait_for_function('localParty.length===3&&!partyLoading',polling=50)
  run('window.thirdX=localParty[1].x;window.fourthX=localParty[2].x;for(let i=0;i<40;i++)update(1/60)')
  assert run('localParty[1].x>thirdX+1&&localParty[2].x<fourthX-1'),'Both simulated gamepads move separate members'
  run('document.querySelector("#playMode").value="battle";document.querySelector("#arenaOpponents").value="human";beginBattle("battle")');page.wait_for_function('localParty.length===3&&!partyLoading',polling=50)
  assert run('localParty.every(a=>!a.bot)&&localParty.filter(a=>a.team===1).length===2'),'Human 2v2 assigns two opponents instead of AI'
  run('document.querySelector("#arenaOpponents").value="bots"')
  run('window.adventureBeforeArena=JSON.stringify(localProfile.journey);fakePads=[];document.querySelector("#playMode").value="duel-local";beginBattle("duel-local");');page.wait_for_function('localParty.length===1&&!partyLoading',polling=50)
  run('toggleMap()');assert 'Duel' in page.locator('#missionList').text_content();run('toggleMap()')
  assert run('boon===""&&p.max===HERO_DEFS[hero].hp&&JSON.stringify(localProfile.journey)===adventureBeforeArena'),'Arena keeps the adventure and removes pact advantages'
  run('localParty[0].inv=0;window.beforeHP=localParty[0].hp;damage(localParty[0].proxy,28,{owner:p});')
  assert run('localParty[0].hp<beforeHP')
  run('window.leaderHP=p.hp;battleDamage(p,30,{team:0})');assert run('p.hp===leaderHP'),'No friendly fire'
  for round_number in range(3):
   run('localParty[0].inv=0;partyHurt(localParty[0],9999);updateBattle(.02)')
   assert run('state==="won"&&battle.wins[0]')==round_number+1
   if round_number<2:
    page.click('#nextChapter');page.wait_for_function('localParty.length===1&&!partyLoading',polling=50)
  assert page.locator('#nextChapter').is_hidden()
  assert run('JSON.stringify(localProfile.journey)===adventureBeforeArena')
  run('document.querySelector("#playMode").value="duel";beginBattle("duel");');page.wait_for_function('localParty.length===1&&!partyLoading',polling=50)
  run('p.inv=999;window.aiStart=localParty[0].x;for(let i=0;i<240;i++)update(1/60)')
  assert run('localParty[0].bot&&Math.abs(localParty[0].x-aiStart)>1'),'Duel AI approaches the opponent'
  run('document.querySelector("#playMode").value="crown";beginBattle("crown");');page.wait_for_function('localParty.length===3&&!partyLoading',polling=50)
  run('p.x=0;p.z=-7;crownInteract();p.shot=0;p.attack=null;beginAttack();');assert run('battle.crownOwner===p&&p.attack===null'),'Carrier cannot attack'
  run('p.inv=0;hurt(5)');assert run('battle.crownOwner===null'),'An impact drops the crown'
  run('battle.crownCooldown=0;crownInteract();p.inv=999;updateBattle(60.1)');assert run('state==="won"&&battle.ended&&battle.scores[0]>=60'),'Crown score reaches a real match conclusion'
  assert not errors,errors
  browser.close()
 print('PASS: two-player keyboard coop, independent attacks/powers, held revival, full-group retry, two simulated gamepads for four players, friendly-fire rules, three-win local duel, AI movement and crown pickup/drop/attack restriction/scoring.')
finally:server.shutdown()
