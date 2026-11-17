"""Authored Lame attacks must keep their clip rhythm and exactly one damage contact."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page();page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=lame');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
  page.click('#start');run('soundOn=false;p.inv=999;clearRoom();resetHeroAt(0,24);aim=0;')
  for combo in [1,2,3]:
   run(f'cancelAttack();p.shot=0;p.combo={combo-1};p.comboWindow=1;beginAttack();')
   assert run(f'p.attack.combo==={combo}&&p.attack.duration===avatarRuntime.heroes.lame.actions.attack{combo}.getClip().duration')
   result=run("""()=>{const duration=p.attack.duration,hitAt=p.attack.hitAt;var e=spawn(p.x,p.z-1.5);e.hp=e.max=10000;const before=e.hp,shots=shotCount;updateRigAvatar(.01);const scale=avatarRuntime.current.action.getEffectiveTimeScale();updateAttack(hitAt-.001);const early=e.hp;updateAttack(.002);const contact=e.hp;updateAttack(Math.max(.001,duration-hitAt+.001));const after=e.hp;const ended=p.attack===null;cleanupObject(e.root);enemies=enemies.filter(q=>q!==e);return {before,early,contact,after,ended,scale,shotDelta:shotCount-shots};}""")
   assert result['early']==result['before'] and result['contact']<result['early'],result
   assert result['contact']==result['after'] and result['shotDelta']==1,result
   assert result['ended'] and abs(result['scale']-1)<1e-5,result
  # Other classes retain existing rhythm; they are not silently retimed to Lame clips.
  run('hero="voltigeur";applyHero();cancelAttack();p.shot=0;p.comboWindow=0;beginAttack()')
  assert run('Math.abs(p.attack.duration-.43*HEROES.voltigeur.attackRate)<1e-6')
  run('hero="rempart";applyHero();cancelAttack();p.shot=0;beginAttack()')
  assert run('Math.abs(p.attack.duration-.28*HEROES.rempart.attackRate)<1e-6')
  # Missing optional Lame model retains the legacy duration rather than throwing.
  assert run('meleeClipDuration("absent",1,.43)===.43')
  assert not errors,errors;b.close()
 print('PASS: Lame attack duration equals actual clips, animation runs at 1x, damage only at contact and once, recovery finishes; ordinary hero timing unchanged. Human balance not measured.')
finally:server.shutdown();server.server_close()
