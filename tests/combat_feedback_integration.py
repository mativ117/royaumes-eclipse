"""Actual damage/guard/duel lifecycle in the built game; software GPU only."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import json,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':900,'height':600});page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=lame')
  page.wait_for_function('avatarRuntime.status==="ready"&&enemyDirectionV16.status==="ready"',polling=50)
  page.select_option('#quality','light');page.click('#start')
  report=page.evaluate('''()=>{
   soundOn=false;chooseBoon('vigor');for(let i=0;i<120;i++)updateCraftedGates(1/60);
   for(const e of enemies)cleanupObject(e.root);enemies=[];clearFX();resetHeroAt(17.5,-12);
   const check=(v,m)=>{if(!v)throw Error(m)},count=()=>combatFeedbackV17.stats.contacts;
   const e=spawn(17.5,-14,'warden'),hp=e.hp,before=count();
   damage(e,12,{x:p.x,z:p.z,owner:p,heroId:hero,feedbackKind:'melee'});
   check(e.hp===hp-12&&count()===before+1,'One actual HP loss has one contact');
   updateCombatFeedbackV17(1/60);check(combatFeedbackV17.glow.geometry.drawRange.count>0,'Actual contact fills visible GPU geometry');
   const shade=spawn(20,-17,'shade');shade.reveal=0;shade.phaseOffset=0;t=0;const saved=shade.hp,n=count();
   damage(shade,40,p);check(shade.hp===saved&&count()===n,'Hidden phase cannot invent HP or impact');
   p.hp=p.max=150;p.shield=1;p.leap=0;p.inv=p.dashT=0;const blocked=combatFeedbackV17.stats.blocks;
   hurt(20,e);check(p.hp===150&&combatFeedbackV17.stats.blocks===blocked+1,'Real shield uses a guard sign');
   p.shield=0;p.inv=1;hurt(20,e);check(p.hp===150&&count()===n,'Invulnerability has no damage effect');
   p.inv=0;const hurtBefore=count();hurt(20,e);check(p.hp===130&&count()===hurtBefore+1,'Incoming HP loss emits once');
   for(const preset of ['standard','light']){$('#quality').value=preset;$('#quality').onchange({target:$('#quality')});updateCombatFeedbackV17(1/60);updateVisualWorld();renderPresentation();}
   damage(e,9999,p);const deadCount=count();damage(e,10,p);check(count()===deadCount,'Dead target cannot create another contact');
   clearFX();check(!combatFeedbackV17.root.visible&&combatFeedbackV17.glow.geometry.drawRange.count===0,'Room cleanup removes all effects');
   return{contactCount:count(),blocked:combatFeedbackV17.stats.blocks,peak:combatFeedbackV17.stats.peak};
  }''')
  page.evaluate("async()=>{await ensureHeroModel('voleur');await beginDuelMatch({kind:'bot',opponentHero:'voleur',seed:173});}")
  page.evaluate('''()=>{
   const a=localParty[0];a.inv=a.shield=a.leap=a.dashT=0;
   const count=combatFeedbackV17.stats.contacts,hp=a.hp;
   damage(a.proxy,10,{owner:p,x:p.x,z:p.z,heroId:hero,feedbackKind:'melee'});
   if(a.hp!==hp-10||combatFeedbackV17.stats.contacts!==count+1)throw Error('Duel proxy must not double its accepted contact');
   updateCombatFeedbackV17(1/60);resetAvatarPose();if(combatFeedbackV17.root.visible)throw Error('Menu pose reset leaves effects');
  }''')
  assert not errors,errors;browser.close()
finally:server.shutdown();server.server_close()
Path('/tmp/combat-feedback-integration-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS integrated feedback: actual HP deltas, hidden phase, shield/invulnerability, both shaders, death, cleanup and single duel-proxy contact.')
