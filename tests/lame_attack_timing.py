"""Real retargeted clips and weapon contacts, with fixed-step browser simulation.

Enemy AI is deliberately not advanced: a stationary body isolates the animation,
source-timed damage window and blade sweep. Geometric tunnelling edge cases live
in blade_contacts.py. This is not a playability or frame-rate benchmark.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import sys as _check_sys
from pathlib import Path as _CheckPath
_check_sys.path.insert(0,str(_CheckPath(__file__).resolve().parents[1]/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()
import json

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'docs')))
Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
        page = browser.new_page()
        page.add_init_script('requestAnimationFrame=()=>0')
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero=lame')
        page.wait_for_function('avatarRuntime.status==="ready"', polling=50)
        page.click('#start')
        run = page.evaluate
        run('soundOn=false;p.inv=999;')
        results = run(r'''()=>{
 const avatar=avatarRuntime.current,dt=1/120,report=[];
 function prime(combo){
  clearRoom();clearHazards();resetHeroAt(0,24);aim=targetAim=0;
  p.inv=999;p.motionSpeed=0;p.vx=p.vz=0;p.combo=combo-1;p.comboWindow=1;
  player.root.rotation.set(0,0,0);beginAttack();return p.attack;
 }
 function pose(){
  player.root.position.set(p.x,0,p.z);player.root.rotation.set(0,aim,0);
  poseHero(dt);avatar.root.updateWorldMatrix(true,true);
 }
 function sample(){return{base:(avatar.bladeBase||avatar.hand).getWorldPosition(new THREE.Vector3()),tip:avatar.blade.getWorldPosition(new THREE.Vector3())};}
 function reference(combo){
  const attack=prime(combo),candidates=[];
  while(p.attack){
   t+=dt;pose();const a=p.attack;
   if(a.elapsed>=a.hitAt&&a.elapsed<=a.activeEnd){
    const q=sample();
    // Fixed world-space targets derived from the real blade, not a guessed cone.
    for(const u of [1,.8,.6]){
     const point=q.base.clone().lerp(q.tip,u);
     if(point.y>.12&&point.y<2.15&&Math.hypot(point.x-p.x,point.z-p.z)>1.05)candidates.push({x:point.x,z:point.z});
    }
   }
   resolveBladeContacts();updateAttack(dt);
  }
  const picks=[];
  for(let i=0;i<candidates.length;i+=Math.max(1,Math.floor(candidates.length/9)))picks.push(candidates[i]);
  return{duration:attack.duration,hitAt:attack.hitAt,activeEnd:attack.activeEnd,candidates:picks.slice(0,12)};
 }
 function attempt(combo,point,mode='contact'){
  const attack=prime(combo),enemy=spawn(point.x,point.z,mode==='vertical'?'warden':'archer');
  enemy.hp=enemy.max=10000;enemy.mode='idle';
  if(mode==='vertical')enemy.root.position.y=10;
  const before=enemy.hp,shots=shotCount,contacts=[];let early=true,recovery=true,scale=1;
  while(p.attack){
   t+=dt;pose();const a=p.attack,elapsed=a.elapsed;
   enemy.root.position.x=enemy.x;enemy.root.position.z=enemy.z;
   const hp=enemy.hp;
   let wall=null;
   if(mode==='wall'){
    wall={x:(p.x+enemy.x)/2,z:(p.z+enemy.z)/2,w:.70,d:.70};obstacles.push(wall);
   }
   if(mode!=='late'||elapsed>a.activeEnd+dt)resolveBladeContacts();
   if(wall)obstacles.splice(obstacles.indexOf(wall),1);
   if(enemy.hp<hp)contacts.push({elapsed,amount:hp-enemy.hp});
   if(elapsed<a.hitAt&&enemy.hp!==before)early=false;
   // updateAttack still runs: an accidental legacy cone would damage here.
   const beforeUpdate=enemy.hp;updateAttack(dt);
   if(enemy.hp!==beforeUpdate)contacts.push({elapsed:elapsed+dt,amount:beforeUpdate-enemy.hp,legacy:true});
   if(elapsed>a.activeEnd&&enemy.hp!==hp)recovery=false;
   if(avatar.state==='attack'+combo)scale=avatar.action.getEffectiveTimeScale();
  }
  const body=bladeBodyCapsule(enemy);
  return{duration:attack.duration,hitAt:attack.hitAt,activeEnd:attack.activeEnd,before,after:enemy.hp,contacts,early,recovery,scale,shotDelta:shotCount-shots,ended:p.attack===null,bodyMinY:Math.min(body.a.y,body.b.y)};
 }
 for(const combo of [1,2,3]){
  const source=reference(combo),expected=avatar.actions['attack'+combo].getClip().duration;
  let point=null,contact=null;
  for(const candidate of source.candidates){const value=attempt(combo,candidate);if(value.after<value.before){point=candidate;contact=value;break;}}
  if(!contact){report.push({combo,source,error:'No stationary body intersects the actual active blade sweep'});continue;}
  report.push({combo,source:{duration:source.duration,hitAt:source.hitAt,activeEnd:source.activeEnd},expected,point,contact,
   wall:attempt(combo,point,'wall'),late:attempt(combo,point,'late'),
   miss:attempt(combo,{x:0,z:27.5}),vertical:attempt(combo,point,'vertical')});
 }
 clearRoom();return report;
}''')
        Path('/tmp/lame-attack-contact-report.json').write_text(json.dumps(results, indent=2))
        for row in results:
            assert 'error' not in row, row
            combo = row['combo']
            contact = row['contact']
            assert abs(contact['duration'] - row['expected']) < 1e-6, row
            assert contact['early'] and contact['recovery'] and contact['ended'], row
            assert abs(contact['scale'] - 1) < 1e-6 and contact['shotDelta'] == 1, row
            assert len(contact['contacts']) == 1, row
            hit = contact['contacts'][0]
            assert not hit.get('legacy') and contact['hitAt'] <= hit['elapsed'] <= contact['activeEnd'], row
            assert abs(hit['amount'] - (72 if combo == 3 else 44)) < 1e-6, row
            for mode in ['wall', 'late', 'miss', 'vertical']:
                value = row[mode]
                assert value['after'] == value['before'] and not value['contacts'], (mode, row)
            assert row['vertical']['bodyMinY'] > 8, row
        # Newly authored heroes use their own source timing, not Lame timing or
        # their former procedural hardcoded duration. Loading is lazy in 1.5.
        run('Promise.all(["voltigeur","rempart"].map(ensureHeroModel))')
        run('hero="voltigeur";applyHero();cancelAttack();p.shot=0;p.comboWindow=0;beginAttack()')
        assert run('''()=>{const a=avatarRuntime.current,d=a.motionCalibration?.attacks.attack1;
         return !!d&&!!p.attack&&Math.abs(p.attack.duration-a.actions.attack1.getClip().duration)<1e-6
          &&Math.abs(p.attack.hitAt-d.hitAt)<1e-6&&Math.abs(p.attack.activeEnd-d.activeEnd)<1e-6;}''')
        run('hero="rempart";applyHero();cancelAttack();p.shot=0;beginAttack()')
        assert run('''()=>{const d=avatarRuntime.current.motionCalibration?.shot;return !!d&&!!p.attack
         &&Math.abs(p.attack.duration-d.duration)<1e-6&&Math.abs(p.attack.hitAt-d.hitAt)<1e-6;}''')
        assert run('meleeClipDuration("absent",1,.43)===.43')
        # An optional model that has not loaded still retains a bounded fallback.
        assert run('''()=>{const a=avatarRuntime.heroes.voltigeur;try{delete avatarRuntime.heroes.voltigeur;
         return meleeClipDuration("voltigeur",1,.43)===.43;}finally{avatarRuntime.heroes.voltigeur=a;}}''')
        assert not errors, errors
        browser.close()
    print('PASS: three actual retargeted clips at 1x; fixed body hit once in the source window; physical wall, recovery, horizontal and vertical whiffs; no legacy cone damage; new hero source timings and missing-model fallback. No human balance or FPS claim.')
finally:
    server.shutdown()
    server.server_close()
