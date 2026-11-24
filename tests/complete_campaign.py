"""Three-chapter state/route integration and all class models, not a duration playtest."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import sys as _check_sys
from pathlib import Path as _CheckPath
_check_sys.path.insert(0,str(_CheckPath(__file__).resolve().parents[1]/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1100,'height':760});page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
  assert page.locator('[data-hero]:enabled').count()==10
  assert page.locator('[data-hero=eclipse]').is_disabled()
  run('soundOn=false;')
  for name in run('Object.keys(HERO_DEFS)'):
   run(f'ensureHeroModel("{name}")')
   assert run(f'Object.keys(avatarRuntime.heroes["{name}"].actions).length>=13&&avatarRuntime.heroes["{name}"].weapon'),name
  # Every ordinary kit can enter the existing expedition and activate its power.
  for name in run('Object.keys(HERO_DEFS).filter(id=>!HERO_DEFS[id].secret)'):
   run(f'hero="{name}";start();p.inv=999;p.heat=72;resetHeroAt(0,25);p.power=0;power();update(1/60);')
   assert run('p.power>0'),name
   assert run('Number.isFinite(p.x)&&Number.isFinite(p.z)&&p.hp>0'),name
   if name=='cendres':assert run('p.heat===0&&classEffects.some(f=>f.kind==="burn")')
   if name=='tisseuse':assert run('Math.hypot(p.x,p.z-25)>2&&classEffects.some(f=>f.kind==="rift")'),'Portal must not immediately send its caster back'
   if name=='voleur':
    run('moveEntity(p,3,0);p.doubleSwapLock=0;power()');assert run('Math.abs(p.x)<.1&&classEffects.some(f=>f.kind==="double")'),'Double must allow an actual early swap'
   if name=='neant':
    run('var colorBefore=avatarRuntime.current.ownedMaterials.find(m=>m.isMeshStandardMaterial).color.clone();updateRigAvatar(.5)');assert run('p.formT>0&&!avatarRuntime.current.ownedMaterials.find(m=>m.isMeshStandardMaterial).color.equals(colorBefore)'),'Void form must visibly transform its own materials'

  run('hero="rempart";start();p.inv=999;enterChapter(2);')
  run('window.clearGroup=()=>{for(const e of enemies){if(e.dead)continue;e.mode="recover";if(e.type==="boss")campaign.bossAwake=true;damage(e,100000,null);}};window.useNode=id=>{const n=journey.nodes.find(n=>n.id===id);p.x=n.x;p.z=n.z+1.8;p.recoil=0;p.attack=null;const target=interactionTarget();if(!target)throw Error("No interaction at "+id);interact();};void 0;')
  assert run('buildGuideRoute(journeyGoals()[0]).length>0')
  run('clearGroup();useNode("trace-fer")');assert run('journey.step')==1
  assert run('buildGuideRoute(journeyGoals()[0]).every(q=>!blocked(q.x,q.z,.55))')
  run('clearGroup();useNode("trace-pluie")');assert run('journey.step')==2
  run('useNode("memoire");useNode("ember")');assert run('journey.runes')==0
  run('clearHazards();useNode(journey.order[0]);useNode(journey.order[1]);');assert run('journey.step')==3
  run('clearGroup();updateJourney(.02)');assert run('journey.step')==4
  run('p.x=0;p.z=-86;updateJourney(.02);boss.hp=boss.max*.6;updateBoss(boss,.02)');assert run('boss.phase===2&&journey.arenaPillars.every(o=>o.visible)')
  run('recordSecret(0);boss.mode="recover";p.x=boss.x;p.z=boss.z+3;p.recoil=0;p.attack=null;interact()');assert run('localProfile.secret[1]')
  run('clearGroup();updateJourney(.02);useNode("exit")');assert run('state==="won"&&localProfile.completed.includes(2)&&!document.querySelector("#nextChapter").hidden')
  page.click('#nextChapter');assert run('journey.level')==3
  run('useNode("wake")');assert run('journey.step')==1
  run('clearGroup();for(const i of [0,1,2])useNode("link"+i)');assert run('journey.step')==2
  run('useNode("route")');assert run('state==="choice"')
  page.locator('#journeyChoices button').first.click();assert run('journey.route==="sun"&&journey.step===3')
  run('clearGroup();useNode("supply-west")');page.locator('#journeyChoices button').last.click();assert run('journey.step===4&&journey.core>=240')
  # The optional third secret unfolds a real reachable island and a finite fight.
  run('useNode("secret-shore")');assert run('journey.secretOpen&&buildGuideRoute({x:41,z:-60}).length>0')
  run('for(const e of enemies.filter(e=>e.journeyGroup==="secret")){e.mode="recover";damage(e,100000,null);}p.x=41;p.z=-60;p.attack=null;p.recoil=0;interact()');assert run('secretUnlocked()')
  run('clearGroup();useNode("heart")');assert run('journey.step')==5
  run('p.x=0;p.z=-88;updateJourney(.02);boss.hp=boss.max*.25;updateBoss(boss,.02)');assert run('boss.phase')==3
  run('clearGroup();updateJourney(.02);useNode("exit")');assert run('state==="won"&&localProfile.completed.includes(3)&&localProfile.journey===null')
  run('hero="eclipse";start();p.incarnation=100;activateIncarnation()');assert run('p.incarnateT===8&&p.incarnation===0')
  run('updateClassAbilities(8.1)');assert run('p.fragileT===4')
  run('enterChapter(2,3);saveJourneyCheckpoint(false);restoreJourney()');assert run('journey.level===2&&journey.step===3&&Number.isFinite(p.x)')
  run('updateHUD();updateJourneyScenery(.02);updateSanctuary(.02);renderer.render(scene,camera)');page.screenshot(path='/tmp/royaumes-complete-hunt.png')
  run('enterChapter(3,3);updateHUD();updateJourneyScenery(.02);updateSanctuary(.02);renderer.render(scene,camera)');page.screenshot(path='/tmp/royaumes-complete-convoy.png')
  assert not errors,errors
  browser.close()
 print('PASS: eleven skinned class models; ten available kits; hunt traces, puzzle, terrain boss and ending; convoy repairs, route, supply, secret island, final boss and ending; secret hero and Incarnation; chapter retry. Controlled integration, not human playtime.')
finally:server.shutdown()
