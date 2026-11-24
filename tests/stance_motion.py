"""All eleven heroes: real-game directional support, without pretending fallback
strafe/back clips are newly authored motions. Full skinned boot-surface/metadata inspection
is covered separately by roster_motion.py; this measures the rigid sole support hull and skeleton support
and displacement after the game has selected calibrated or analytical IK.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import sys
import json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()

class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=browser.new_page();page.add_init_script('requestAnimationFrame=()=>0');errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/')
  page.wait_for_function('avatarRuntime.status==="ready"',polling=50)
  page.evaluate('async()=>{await Promise.all(Object.keys(HERO_DEFS).map(ensureHeroModel));return true;}')
  result=page.evaluate(r'''()=>{
   soundOn=false;const outcomes=[];
   for(const id of Object.keys(HERO_DEFS)){
    hero=id;start();const avatar=avatarRuntime.current;
    if(!avatar.motionCalibration)throw Error('Missing production calibration '+id);
    for(const requested of [1.8,HEROES[id].speed])for(const [dx,dz] of [[0,-1],[0,1],[1,0],[-1,0]]){
     resetHeroAt(-6,25);aim=0;
     const cap=HEROES[id].speed*motionSpeedScale(avatar,id,{vx:dx,vz:dz},0),speed=Math.min(requested,cap);
     const finished=[],open=[[],[]],states=new Set();let correction=0,released=0,contacts=0,coreReleased=0,coreContacts=0,ground=-Infinity,ankleMax=-Infinity,soleMin=Infinity;
     for(let i=0;i<240;i++){
      t+=1/60;p.x+=dx*speed/60;p.z+=dz*speed/60;p.motionSpeed=speed;p.vx=dx*speed;p.vz=dz*speed;
      player.root.position.set(p.x,0,p.z);player.root.rotation.set(0,0,0);updateRigAvatar(1/60);
      if(i<60)continue;
      states.add(avatar.lowerState);
      const gaitCalibration=avatar.motionCalibration.gaits[avatar.lowerState],calibrated=!!gaitCalibration&&gaitCalibration.authoredContacts!==false;
      for(let j=0;j<2;j++){
       const leg=avatar.legs[j],pos=leg.end.getWorldPosition(new THREE.Vector3());
       if(!Number.isFinite(pos.x+pos.y+pos.z))throw Error('Nonfinite skeleton '+id);
       const support=calibrated?leg.motionContact&&!leg.motionReleased&&leg.motionWeight>.75:avatar.feetWeight>.99&&leg.lastPhase>.03&&leg.lastPhase<.545;
       correction=Math.max(correction,leg.motionCorrection||0);
       if(calibrated&&leg.motionContact){contacts++;if(leg.motionReleased)released++;
        // A bounded IK release during the low-weight entry/toe-off envelope is
        // intentional. Separately enforce the guarantee for the planted core.
        const strength=motionContactStrength(avatar,j===0?'L':'R',avatar.motionPhase);
        if(strength>=.75){coreContacts++;if(leg.motionReleased)coreReleased++;}
       }
       const sole=leg.soleSupports?.length?Math.min(...leg.soleSupports.map(point=>point.clone().applyMatrix4(leg.end.matrixWorld).y)):null;
       if(sole!==null)soleMin=Math.min(soleMin,sole);
       if(support){open[j].push(pos.clone());ankleMax=Math.max(ankleMax,pos.y);if(sole!==null)ground=Math.max(ground,sole);}
       else if(open[j].length){finished.push(open[j]);open[j]=[];}
      }
     }
     const groups=finished.filter(g=>g.length>2),drifts=groups.map(g=>Math.hypot(g.at(-1).x-g[0].x,g.at(-1).z-g[0].z));
     outcomes.push({id,requested,speed,dx,dz,states:[...states],groups:groups.length,
      drift:drifts.length?Math.max(...drifts):null,ground:Number.isFinite(ground)?ground:null,ankleMax:Number.isFinite(ankleMax)?ankleMax:null,soleMin:Number.isFinite(soleMin)?soleMin:null,
      maxCorrection:correction,releasedFraction:contacts?released/contacts:0,coreReleasedFraction:coreContacts?coreReleased/coreContacts:0});
    }
   }
   return outcomes;
  }''')
  Path('/tmp/royaumes-stance-motion-report.json').write_text(json.dumps(result,indent=2))
  assert len(result)==88,result
  for check in result:
   assert check['groups']>=4,check
   assert check['drift'] is not None and check['drift']<.05,check
   assert check['ground'] is not None and check['ground']<.05,check
   assert check['soleMin'] is not None and check['soleMin']>-.004,check
   assert check['maxCorrection']<=.14001,check
   assert check['coreReleasedFraction']<.05,check
   expected='walk_back' if check['dz']>0 else 'strafe_right' if check['dx']>0 else 'strafe_left' if check['dx']<0 else None
   if expected:assert expected in check['states'],check
   else:assert any(s in ['walk','run'] for s in check['states']),check
  assert not errors,errors
  browser.close()
 print('PASS: eleven calibrated heroes, actual game-selected walk/run and four directions; core support drift below 5 cm, actual rigid sole hull near floor; bounded authored IK. Side/back analytical fallback is preserved, not presented as new directional animation. No FPS or artistic-quality claim.')
finally:
 server.shutdown();server.server_close()
