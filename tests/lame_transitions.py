"""Lame-only transition interruption and phase continuity on the actual exported rig."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
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
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page();page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=lame');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
  page.click('#start');run('soundOn=false;p.inv=999;var a=avatarRuntime.current;')
  assert run('a.heroId==="lame"&&a.state==="guard"&&a.lowerState==="guard"'),'Selection must initialize the authored guard immediately'
  run("playAvatarAction(a,'walk',.01,true);a.action.time=a.action.getClip().duration*.73;playAvatarAction(a,'run',.01)")
  assert run('Math.abs(a.action.time/a.action.getClip().duration-.73)<1e-6'),'Changing gait must preserve upper-body cycle phase'
  run('''window.poseStep=function(speed,heading=0,dx=0,dz=-1){const dt=1/60;p.motionSpeed=speed;p.x+=dx*speed*dt;p.z+=dz*speed*dt;aim=heading;player.root.position.set(p.x,0,p.z);player.root.rotation.set(0,heading,0);t+=dt;updateRigAvatar(dt);return a.state;};resetHeroAt(0,24);poseStep(0);''')
  assert run('poseStep(2)==="start"')
  assert run('poseStep(0)==="stop"&&a.lowerState==="stop"'),'A stop must interrupt an unfinished start'
  assert run('poseStep(2)==="start"&&a.lowerState===(a.motionCalibration?"walk":"start")'),'Moving again must interrupt braking; calibrated feet already follow actual translation'
  assert run('Math.abs(a.action.getEffectiveTimeScale()-1)<1e-5'),'Transition timing must follow the authored duration'
  run('for(let i=0;i<40;i++)poseStep(2)');assert run('a.state==="walk"')
  run('for(let i=0;i<40;i++)poseStep(0)');assert run('a.state==="guard"&&a.lowerState==="guard"')
  run('resetHeroAt(0,24);poseStep(0);var heading=0;for(let i=0;i<8;i++){heading+=.02;poseStep(0,heading)}')
  assert run('a.state==="turn_left"'),'Small real turns must accumulate independently of per-frame angle'
  assert run('poseStep(2,heading)==="start"&&!a.lowerState.startsWith("turn_")'),'Translation must interrupt a stationary pivot'
  run('resetHeroAt(0,24);poseStep(0);heading=0;var pivotStarts=0,lastPivotTime=0;for(let i=0;i<100;i++){heading+=.035;poseStep(0,heading);if(a.state==="turn_left"){if(a.action.time<lastPivotTime)pivotStarts++;lastPivotTime=a.action.time;}}')
  assert run('pivotStarts>=2'),'Repeated physical pivots must restart their one-shot clip, not hold its last frame'
  # Other heroes keep their previous gait reset semantics and idle initialization.
  run('hero="rempart";applyHero();start();var ordinary=avatarRuntime.current;playAvatarAction(ordinary,"walk",.01,true);ordinary.action.time=.5;playAvatarAction(ordinary,"run",.01)')
  assert run('ordinary.state==="run"&&ordinary.action.time===0&&ordinary.heroId==="rempart"')
  # Optional Lame clips remain optional; a legacy rig without guard keeps the old gait.
  result=run('lameLocomotion({actions:{}},1/60,2,"walk",{x:0,z:0},0)');assert result['name']=='walk' and result['duration'] is None
  result=run('var partial={actions:{guard:{},walk:{},run:{}}},partialActor={x:0,z:0};lameLocomotion(partial,1/60,0,"idle",partialActor,0);partialActor.x=.03;lameLocomotion(partial,1/60,1.8,"walk",partialActor,0)');assert result['name']=='walk' and result['duration'] is None
  assert not errors,errors;b.close()
 print('PASS: actual Lame guard initialization, gait phase continuity, interruptible start/stop/pivot, authored transition timing and repeated pivot playback; ordinary hero and legacy clip fallback preserved. Not a claim of anatomical or artistic validation.')
finally:server.shutdown();server.server_close()
