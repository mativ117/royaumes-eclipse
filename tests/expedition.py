"""Mission state, physical routes, combat contact and persistent checkpoint integration.
Uses controlled damage/positions; does not measure human completion time.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
NAV='''function route(start,goal){const queue=[start],seen=new Set([start.join(',')]);for(let i=0;i<queue.length;i++){const[x,z]=queue[i];if(x===goal[0]&&z===goal[1])return true;for(const[dx,dz]of[[1,0],[-1,0],[0,1],[0,-1]]){const a=x+dx,b=z+dz,k=a+','+b;if(a<-65||a>65||b<-113||b>30||seen.has(k)||blocked(a,b))continue;seen.add(k);queue.push([a,b]);}}return false;}'''
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=b.new_page(viewport={'width':1100,'height':760});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script('window.requestAnimationFrame=()=>0');page.goto(f'http://127.0.0.1:{server.server_port}/');page.click('[data-hero=voltigeur]');page.click('#start')
  run=page.evaluate
  run('(code)=>{(0,eval)(code)}',NAV)
  run('soundOn=false;p.inv=999;')
  assert run('route([0,23],[0,-38])') is False
  run('p.x=9;p.z=7;interact()');page.click('#sealPact');assert run('boon')=='haste'
  assert run('route([0,23],[-20,-8])')
  assert not run('route([0,-38],[-52,-68])')
  # Soul travels its actual route, stopping for finite ambushes, with player nearby.
  run('p.x=-20;p.z=-8;trialInteract(trialTarget());')
  run('''for(let i=0;i<4000&&!campaign.trials.escort.done;i++){
   const e=campaign.trials.escort;p.x=e.x;p.z=e.z;
   for(const foe of enemies)if(trialActive(foe)&&foe.stage?.startsWith('escort')){foe.mode='recover';damage(foe,10000,null)}
   updateTrials(1/60);
  }''')
  assert run('campaign.trials.escort.done'),run('campaign.trials.escort')
  assert run('campaign.keys.has("west")')
  run('p.x=16;p.z=-7;trialInteract(trialTarget());trialInteract({type:"lamp",id:campaign.trials.bells.order[1]});')
  assert run('campaign.trials.bells.read&&campaign.trials.bells.step===0&&hazards.length>0')
  run('for(const id of campaign.trials.bells.order)trialInteract({type:"lamp",id});')
  assert run('campaign.keys.size')==2
  # Both wings, every interactive object and ritual reachable; court still locked.
  for x,z in [(-52,-68),(-54,-51),(-40,-67),(-27,-53),(26,-47),(53,-47),(39,-68),(54,-68),(-9,-62),(9,-55)]:
   assert run(f'route([0,-38],[{x},{z}])'),(x,z)
  assert not run('route([0,-38],[0,-80])'),'Wing must not bypass the Carillonneur'
  run('''var shade=enemies.find(e=>e.type==='shade');shade.reveal=0;shade.mode='idle';shade.phaseOffset=-t;var hp=shade.hp;damage(shade,50);''')
  assert run('shade.hp===hp')
  run('p.x=shade.x;p.z=shade.z;revealShades();damage(shade,50)');assert run('shade.hp<hp')
  run('for(const e of enemies)if(e.type==="shade"){e.reveal=5;damage(e,10000)};p.x=-52;p.z=-68;trialInteract(trialTarget())')
  assert run('campaign.trials.archive')
  run('p.x=54;p.z=-68;trialInteract(trialTarget())');assert not run('campaign.trials.forge.carrying')
  run('for(const v of VALVES){p.x=v.x;p.z=v.z;trialInteract(trialTarget())};p.x=54;p.z=-68;trialInteract(trialTarget())')
  assert run('campaign.trials.forge.carrying')
  run('p.dash=0;dash()');assert not run('campaign.trials.forge.carrying')
  run('p.dashT=0;trialInteract({type:"core"});p.inv=0;p.leap=0;p.shield=0;hurt(1)');assert not run('campaign.trials.forge.carrying')
  run('trialInteract({type:"core"});p.shot=0;beginAttack()');assert not run('campaign.trials.forge.carrying')
  run('cancelAttack();trialInteract({type:"core"});p.x=0;p.z=-38;updateTrials(.01)');assert run('campaign.trials.forge.done')
  assert run('readRun()!==null')
  run('trialInteract({type:"ritual",id:"west"});trialInteract({type:"ritual",id:"east"});var porter=enemies.find(e=>e.type==="porter"), hp=porter.hp;damage(porter,10000)')
  assert run('porter.hp===hp')
  run('for(const e of enemies)if(e.type==="anchor")damage(e,10000);porter.mode="recover";damage(porter,10000)')
  assert run('campaign.defeated.has("carillonneur")')
  assert run('route([0,-65],[0,-80])')
  run('p.x=0;p.z=-71;updateCampaign(.01)');assert run('campaign.checkpoint.id')=='threshold'
  page.reload();page.click('#continueRun');assert run('campaign.trials.archive&&campaign.trials.forge.done&&campaign.defeated.has("carillonneur")')
  assert run('hero')=='voltigeur' and run('boon')=='haste'
  # Contact timing: attacks do not deal instant/repeated damage, cancellation refunds charge.
  run('p.x=0;p.z=-50;p.shot=0;p.combo=0;p.comboWindow=0;aim=0;var target=spawn(0,-52,"warden");target.hp=target.max=300;var hp=target.hp;beginAttack();updateAttack(.1);poseHero(.1);var wind=player.arms[1].rotation.x;')
  assert run('target.hp===hp')
  run('updateAttack(.07);poseHero(.07);var contact=player.arms[1].rotation.x');assert run('target.hp')==256
  run('updateAttack(.03)');assert run('target.hp')==256
  assert run('wind!==contact&&player.sword.parent===player.arms[1]&&player.rifle.parent===player.arms[1]')
  run('cancelAttack();p.shot=0;p.overcharge=2;beginAttack();cancelAttack()');assert run('p.overcharge')==2
  run('p.shot=0;p.attack=null;p.combo=2;p.comboWindow=1;beginAttack()');assert run('p.attack.combo===3&&p.attack.hitAt===.25')
  run('cancelAttack();hero="rempart";applyHero();p.shot=0;var count=bullets.length;beginAttack();updateAttack(.06)');assert run('bullets.length===count')
  run('updateAttack(.02)');assert run('bullets.length===count+1')
  # Boss phases, extraction checkpoint, retry keeps defeated boss and completes at original soul.
  run('cancelAttack();var hp=boss.hp;damage(boss,99999)');assert run('boss.hp===hp')
  run('p.x=0;p.z=-80;updateCampaign(.01);boss.hp=boss.max*.6;updateBoss(boss,.01)');assert run('boss.phase')==2
  run('boss.hp=boss.max*.25;updateBoss(boss,.01)');assert run('boss.phase')==3
  run('boss.mode="recover";damage(boss,99999);updateCampaign(.01)');assert run('campaign.trials.extraction&&campaign.checkpoint.id==="return"')
  run('restoreCampaign();');assert run('boss.dead&&campaign.trials.extraction&&campaign.escapeLeft===70')
  run('p.x=0;p.z=-38;updateTrials(.01)');assert run('state')=='won'
  assert run('localStorage.getItem(RUN_KEY)===null')
  assert run('JSON.parse(expeditionReport()).finished')
  assert not errors,errors
  b.close()
 print('PASS: complete mission, escort navigation, all objective routes, gates, puzzle errors, phase immunity, cargo risks, ritual, checkpoint reload, timed melee/rifle, three boss phases, extraction retry and victory. Controlled integration, not a duration playtest.')
finally:server.shutdown();server.server_close()
