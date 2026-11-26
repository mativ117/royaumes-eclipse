"""Same-camera real engine evidence for the 1.6 art direction pass."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import argparse,json,hashlib,time
from playwright.sync_api import sync_playwright
from browser_checks import install_csp_wait
install_csp_wait()
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--label',choices=['before','after'],required=True);args=parser.parse_args()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
records=[];errors=[]
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page(viewport={'width':740,'height':480});page.add_init_script('requestAnimationFrame=()=>0;Math.random=(()=>{let seed=716;return()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296)})();');page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=rempart');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);page.select_option('#quality','light');page.click('#start');run=page.evaluate;run('soundOn=false;p.inv=999;heroPreviewDispose();');page.add_style_tag(content='#hud,#mobile,#controls,#notice,#zoneBanner,#interact,#bossHUD,#encounterV16{display:none!important}')
  setups={
   'atrium':'resetHeroAt(0,25);camera.position.set(0,6.7,35.8);camera.lookAt(0,1.6,20);',
   'cloitre':"chooseBoon('vigor');for(let i=0;i<120;i++)updateCraftedGates(1/60);resetHeroAt(17.5,-11);for(const e of enemies)cleanupObject(e.root);enemies=[];window.reviewArcher=spawn(17.5,-20,'archer');window.reviewShade=spawn(21,-22,'shade');reviewShade.reveal=99;camera.position.set(22,7,2);camera.lookAt(17.5,1.2,-17);",
   'hunt':'enterChapter(2);resetHeroAt(0,19);camera.position.set(4,7,31);camera.lookAt(0,1.2,10);'
  }
  for name,setup in setups.items():
   run(setup);run('update(1/60);if(typeof updateCameraDirectionV16==="function"){const pos=camera.position.clone(),rot=camera.quaternion.clone();updateCameraDirectionV16(1/60);camera.position.copy(pos);camera.quaternion.copy(rot);camera.updateMatrixWorld(true);}player.root.position.set(p.x,0,p.z);poseHero(1/60);for(const e of enemies){e.root.position.set(e.x,0,e.z);poseEnemy(e);}updateStageCraft(.016);updateArtDirection(.016);updateJourneyScenery(.016);updateSanctuary(.016);if(typeof updateEnvironmentDirectionV16==="function")updateEnvironmentDirectionV16(.016);updateVisualWorld();renderPresentation();')
   target=ROOT/f'docs/previews/r6-{name}-{args.label}.jpg';page.screenshot(path=str(target),type='jpeg',quality=90);records.append({'scene':name,'file':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'calls':run('presentation.stats.sceneCalls'),'quality':'light','camera':'fixed identical before/after; actual game actors, HUD hidden'})
  assert not errors,errors;b.close()
finally:server.shutdown();server.server_close()
path=ROOT/f'design/CAPTURES-DIRECTION-1.6-{args.label}.json';path.write_text(json.dumps({'version':json.loads((ROOT/'docs/version.json').read_text())['version'],'captured_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'html_sha256':hashlib.sha256((ROOT/'docs/index.html').read_bytes()).hexdigest(),'outputs':records,'scope':'Actual engine stills, not concepts or hardware frame-rate evidence'},ensure_ascii=False,indent=2)+'\n')
print('Captured',args.label,len(records),'actual engine scenes')
