"""Actual engine before/after, fixed simulation at normal playback speed.

Software rendering is not hardware FPS evidence. The video has no audio track.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import argparse, hashlib, json, subprocess, tempfile, time
from playwright.sync_api import sync_playwright
from browser_checks import install_csp_wait
install_csp_wait()
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--label',choices=['before','after'],required=True)
parser.add_argument('--stills-only',action='store_true')
args=parser.parse_args()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
outputs=[]
try:
 with sync_playwright() as pw, tempfile.TemporaryDirectory(prefix='combat-review-') as tmp:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':800,'height':500});page.add_init_script('requestAnimationFrame=()=>0;Math.random=(()=>{let s=917;return()=>((s=(s*1664525+1013904223)>>>0)/4294967296)})();')
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=lame')
  page.wait_for_function('avatarRuntime.status==="ready"&&enemyDirectionV16.status==="ready"',polling=50)
  page.select_option('#quality','light');page.click('#start');run=page.evaluate
  run("soundOn=false;chooseBoon('vigor');for(let i=0;i<120;i++)updateCraftedGates(1/60);for(const e of enemies)cleanupObject(e.root);enemies=[];clearFallenActors();resetHeroAt(17.5,-10);p.inv=999;window.reviewActors=[spawn(14.5,-17,'warden'),spawn(17.5,-17,'archer'),spawn(20.5,-17,'shade')];for(const e of reviewActors){e.reveal=999;e.timer=99;if(e.authoredEnemy)e.authoredEnemy.ai.cooldown=999;e.root.rotation.y=Math.PI;if(e.authoredEnemy)e.authoredEnemy.ai.heading=Math.PI;e.root.position.set(e.x,0,e.z);poseEnemy(e,0);}camera.position.set(17.5,5,-8);camera.lookAt(17.5,1,-17);updateVisualWorld();renderPresentation();")
  page.add_style_tag(content='#hud,#mobile,#controls,#notice,#zoneBanner,#interact,#bossHUD,#encounterV16{display:none!important}')
  def save(name):
   target=ROOT/f'docs/previews/r7-{name}-{args.label}.jpg';page.screenshot(path=str(target),type='jpeg',quality=92);outputs.append({'file':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
  save('enemies')
  for index,name in [(0,'warden'),(1,'archer'),(2,'shade')]:
   run(f'camera.position.set(reviewActors[{index}].x+2.8,2.8,-13);camera.lookAt(reviewActors[{index}].x,1,-17);renderPresentation();');save(name)
  run("for(const e of enemies)cleanupObject(e.root);enemies=[];resetHeroAt(17.5,-12);p.inv=999;window.reviewVictim=spawn(17.5,-14,'warden');reviewVictim.hp=reviewVictim.max=9999;reviewVictim.alert=20;reviewVictim.timer=999;aim=targetAim=0;camera.position.set(21,5.4,-6);camera.lookAt(17.5,.9,-13);soundOn=false;")
  hp_before=run('reviewVictim.hp')
  contact_saved=False
  for frame in range(0 if args.stills_only else 96):
   run(f"if({frame}%24===0)requestAttack();for(let j=0;j<5;j++){{reviewVictim.timer=999;update(1/120);}}camera.position.set(21,5.4,-6);camera.lookAt(17.5,.9,-13);updateVisualWorld();renderPresentation();")
   page.screenshot(path=f'{tmp}/{frame:04}.jpg',type='jpeg',quality=85)
   if not contact_saved and run('reviewVictim.hp')<hp_before:
    save('contact');contact_saved=True
  video=ROOT/f'docs/previews/r7-combat-{args.label}.mp4'
  if not args.stills_only:subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','24','-i',tmp+'/%04d.jpg','-c:v','libx264','-preset','fast','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
  if video.exists():outputs.append({'file':video.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'seconds':4,'simulation_hz':120,'playback_fps':24,'audio':False,'hp_lost':hp_before-run('reviewVictim.hp')})
  assert not errors,errors;browser.close()
finally:server.shutdown();server.server_close()
report={'version':json.loads((ROOT/'docs/version.json').read_text())['version'],'captured_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'html_sha256':hashlib.sha256((ROOT/'docs/index.html').read_bytes()).hexdigest(),'viewport':[800,500],'quality':'light','scope':'Actual engine, identical camera/input; fixed simulation normal-speed video, no audio, not hardware FPS','outputs':outputs}
(ROOT/f'design/CAPTURES-COMBAT-1.7-{args.label}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Captured',args.label,'actual silhouettes and four-second normal-playback combat')
