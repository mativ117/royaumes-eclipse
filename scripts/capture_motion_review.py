"""In-engine 1x motion evidence, using exactly two 1/60 simulation calls per 30fps frame.

This is deterministic frame export, not a hardware FPS measurement. Git history is
read into /tmp; no historical file is modified. Frames and logs stay temporary.
Only three MP4s and the current studio JPEG are written into docs/previews.
"""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from urllib.parse import unquote,urlsplit
import argparse,hashlib,json,subprocess,tempfile,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/previews'
BEFORE='8f787ee328eb2396ee00da7067123159e22cdef5' # Published 1.3, pinned before this pass.
FPS=30;WIDTH=720;HEIGHT=480

def git_bytes(ref,name):return subprocess.check_output(['git','show',f'{ref}:{name}'],cwd=ROOT)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encode(folder,target):
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-i',str(folder/'frame-%04d.png'),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
 metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]));streams=metadata['streams'];video=next(s for s in streams if s['codec_type']=='video');assert not any(s['codec_type']=='audio' for s in streams)
 return {'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'duration':float(metadata['format']['duration']),'width':video['width'],'height':video['height'],'fps':FPS,'audio':False,'playback_speed':1,'hardware_fps_measured':False}

SETUP="""soundOn=false;clearHazards();clearInputs();resetHeroAt(-6,25);p.inv=999;
if(typeof heroPreviewDispose==='function')heroPreviewDispose();
camera.position.set(p.x,6.7,p.z+10.8);cameraLook.set(p.x,1.6,p.z-5);camera.lookAt(cameraLook);
last=1000-1000/30;accumulator=0;lastRenderedState=null;
window.proofCalls=0;window.proofOriginalUpdate=update;update=function(dt){proofCalls++;return proofOriginalUpdate(dt)};
mouseAim=true;pointer.set(0,.2);"""
STEP="""({index,input})=>{joy.x=input.x||0;joy.y=input.z||0;shooting=!!input.attack;mouseDown=false;
const now=1000+index*1000/30,elapsed=Math.min(.1,(now-(last||now))/1000),before=proofCalls;
accumulator=Math.max(0,2/60-elapsed)+1e-9;frame(now);
if(proofCalls-before!==2)throw Error('Expected two simulation steps, got '+(proofCalls-before));
return{state,t,combo:p.combo,mode:window.proofEnemy?.mode};}"""
HIDE="#hud,#mobile,#controls,#notice,#zoneBanner,#interact,#bossHUD,.hero-preview{display:none!important}"
def controls(seconds):
 if .30<=seconds<1.30:return {'z':-.72}
 if 1.70<=seconds<2.25:return {'x':.65}
 if 2.55<=seconds<3.85:return {'attack':True}
 return {}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--before-ref',default=BEFORE);parser.add_argument('--only',nargs='+',choices=['before','after','creature','studio'],default=['before','after','creature','studio']);args=parser.parse_args();OUT.mkdir(exist_ok=True)
 ref=subprocess.check_output(['git','rev-parse',args.before_ref],cwd=ROOT,text=True).strip();report={'captured_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'before_commit':ref,'outputs':[],'notes':['Actual game frames; fixed 60Hz simulation exported at 30fps, playback 1x; not measured device performance.','Same Lame input timeline and normal gameplay camera before/after; HUD hidden identically.','Quiet existing Atrium; quest context, colliders and distant actors retained.','Creature clip uses a fixed spectator three-quarter camera; actual actor positions and AI charge, no visual relocation.']}
 with tempfile.TemporaryDirectory(prefix='royaumes-motion-',dir='/tmp') as scratch:
  scratch=Path(scratch);before=scratch/'before';before.mkdir();names=['docs/index.html','docs/version.json','docs/favicon.svg','docs/atelier-lame.html'];names+=subprocess.check_output(['git','ls-tree','-r','--name-only',ref,'docs/assets/characters/'],cwd=ROOT,text=True).splitlines()
  for name in names:
   target=before/Path(name).relative_to('docs');target.parent.mkdir(parents=True,exist_ok=True)
   try:target.write_bytes(git_bytes(ref,name))
   except subprocess.CalledProcessError:
    if name in ['docs/index.html','docs/version.json'] or name.endswith('/lame.glb'):raise
  roots={'before':before,'after':ROOT/'docs'}
  class Quiet(SimpleHTTPRequestHandler):
   def log_message(self,*a):pass
   def translate_path(self,url):
    parts=[p for p in unquote(urlsplit(url).path).split('/') if p and p not in ['.','..']]
    if parts and parts[0] in roots:return str(roots[parts[0]].joinpath(*parts[1:]))
    return str(scratch/'not-found')
  server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
  try:
   with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
    def open_game(site,hero='lame'):
     context=browser.new_context(viewport={'width':WIDTH,'height':HEIGHT},device_scale_factor=1);page=context.new_page();page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base+'/'+site+'/index.html?hero='+hero);page.wait_for_function('avatarRuntime.status==="ready"',polling=50);version=page.evaluate('ROYAUMES_VERSION');page.evaluate('soundOn=false');page.click('#heroPreviewPlay' if page.locator('#heroPreviewPlay').count() else '#start');page.wait_for_function('state==="playing"',polling=50);page.add_style_tag(content=HIDE);page.evaluate(SETUP);return context,page,errors,version
    for site in ['before','after']:
     if site not in args.only:continue
     context,page,errors,version=open_game(site);expected=json.loads((roots[site]/'version.json').read_text())['version'];assert version==expected
     if site=='after':assert version==(ROOT/'VERSION').read_text().strip(),'Build docs before capturing'
     frames=scratch/('frames-'+site);frames.mkdir();combos=set();sim_start=page.evaluate('t')
     for index in range(FPS*4):
      value=page.evaluate(STEP,{'index':index,'input':controls(index/FPS)});assert value['state']=='playing',value;combos.add(value['combo']);page.screenshot(path=str(frames/f'frame-{index:04d}.png'))
      if index%15==0:print(site,index,'/',FPS*4,flush=True)
     target=OUT/f'r4-motion-{site}.mp4';record=encode(frames,target);record.update({'version':version,'html_sha256':sha(roots[site]/'index.html'),'lame_sha256':sha(roots[site]/'assets/characters/lame.glb'),'frames':FPS*4,'simulation_calls':page.evaluate('proofCalls'),'simulation_seconds':page.evaluate('t')-sim_start,'camera':'ordinary gameplay','combos_seen':sorted(combos),'hud_hidden':True});report['outputs'].append(record);assert not errors,errors;context.close()
    if 'creature' in args.only:
     context,page,errors,version=open_game('after','rempart');page.evaluate("""resetHeroAt(4,25);p.inv=0;p.hp=p.max;window.proofEnemy=spawn(4,21.7);proofEnemy.alert=20;proofEnemy.timer=0;
window.proofOriginalRender=renderPresentation;renderPresentation=function(){camera.position.set(9,4.0,28.6);camera.lookAt(4,.65,23.1);updateVisualWorld();return proofOriginalRender()};""")
     assert page.evaluate('!!proofEnemy.creatureReference');frames=scratch/'frames-creature';frames.mkdir();states=set()
     for index in range(FPS*5//2):
      value=page.evaluate(STEP,{'index':index,'input':{}});states.add(value['mode']);page.screenshot(path=str(frames/f'frame-{index:04d}.png'))
      if index%15==0:print('creature',index,'/',FPS*5//2,flush=True)
     target=OUT/'r4-creature.mp4';record=encode(frames,target);record.update({'version':version,'creature_sha256':sha(ROOT/'assets/creatures/obsidian-warden.glb'),'frames':FPS*5//2,'simulation_calls':page.evaluate('proofCalls'),'camera':'fixed spectator three-quarter; actors retain actual positions','states_seen':sorted(states),'hud_hidden':True});report['outputs'].append(record);assert {'windup','charge','recover'}.issubset(states),states;assert not errors,errors;context.close()
    if 'studio' in args.only:
     context=browser.new_context(viewport={'width':1000,'height':760});page=context.new_page();page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base+'/after/atelier-lame.html?hero=lame');page.wait_for_function('window.reviewReady===true',polling=50);page.evaluate('spin=false;mixer.update(.2);frame(performance.now())');target=OUT/'r4-lame-studio.jpg';page.screenshot(path=str(target),type='jpeg',quality=94);report['outputs'].append({'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'width':1000,'height':760,'version':(ROOT/'VERSION').read_text().strip(),'kind':'actual in-engine studio still'});assert not errors,errors;context.close()
    browser.close()
  finally:server.shutdown();server.server_close()
 report_path=Path('/tmp/royaumes-r4-motion-report.json');report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report,indent=2,ensure_ascii=False));print('Report',report_path,flush=True)
if __name__=='__main__':main()
