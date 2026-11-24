"""Actual duel actors, class controls and adventure isolation in the browser.

Run after scripts/build.py, serially with other WebGL tests. Fixed-step software
rendering checks simulation and real imported clips; it does not establish human
balance, phone frame rate, native networking or visual production quality.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from browser_checks import install_csp_wait

install_csp_wait()


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


HELPERS = r'''() => {
 window.duelTest = {
  check(value,message){if(!value)throw Error(message);},
  save(){return {journey:JSON.stringify(localProfile.journey),run:localStorage.getItem(RUN_KEY),secret:JSON.stringify(localProfile.secret),completed:JSON.stringify(localProfile.completed)};},
  unchanged(before){const after=this.save();for(const key of Object.keys(before))this.check(after[key]===before[key],'Duel changed adventure '+key);},
  input(value={}){this.check(setDuelRemoteInput(value),'Authoritative intent must be accepted');},
  tick(count,dt=1/60){for(let i=0;i<count;i++){if(battle?.kind==='lan-host')this.input();update(dt);}},
  finite(actor){return [actor.x,actor.z,actor.vx,actor.vz,actor.hp,actor.max].every(Number.isFinite);},
  ownedBones(avatar){let bones=null;avatar.root.traverse(o=>{if(o.isSkinnedMesh&&!bones)bones=o.skeleton.bones;});return bones;},
  cleanRound(){resetDuelRound({first:true});const actor=localParty[0];actor.bot=null;clearInputs();p.inv=actor.inv=0;hitPause=0;return actor;}
 };
}'''


BOT_COVER = r'''() => {
 const test=duelTest,actor=localParty[0],dt=1/60;
 test.check(actor.bot&&actor.heroId==='rempart','Exercise the actual ranged planner');
 // The existing pillar lies between these two legal positions. The planner is
 // not given the player's hidden position: it must regain a sight line itself.
 p.x=5.5;p.z=-22;p.vx=p.vz=0;p.inv=999;
 actor.x=5.5;actor.z=-11;actor.vx=actor.vz=0;actor.inv=999;
 actor.bot.reset(79831);actor.root.position.set(actor.x,0,actor.z);
 test.check(!classLine(actor,p),'The fixture must start behind real arena cover');
 let path=0,maxStep=0,visibleFrames=0,decisions=0;
 const reasons=new Set();
 for(let i=0;i<14/dt;i++){
  const x=actor.x,z=actor.z;update(dt);
  const step=Math.hypot(actor.x-x,actor.z-z);path+=step;maxStep=Math.max(maxStep,step);
  test.check(test.finite(actor)&&test.finite(p),'Finite body state during tactical simulation');
  test.check(world.onGround(actor.x,actor.z,.48)&&!blocked(actor.x,actor.z,.47),'The bot cannot cross arena cover or the edge');
  // Rempart has no blink. This bound includes the peaked physical dodge curve,
  // ordinary acceleration and capped body separation, without blessing a warp.
  test.check(step<.95,'A non-blinking bot moved instantaneously: '+step);
  if(classLine(actor,p))visibleFrames++;
  if(actor.bot.debug){reasons.add(actor.bot.debug.reason);decisions=actor.bot.debug.decisionCount;}
 }
 test.check(path>3&&visibleFrames>0,'The bot must leave cover and regain a sight line');
 test.check(decisions>50&&reasons.size>1,'The planner must continue making bounded tactical decisions');
 test.check(battle.time<77&&battle.time>75,'A fourteen-second simulation advances the round clock once');
 return {seconds:14,path,maxStep,visibleFrames,decisions,reasons:[...reasons]};
}'''


DAMAGE_RULES = r'''() => {
 const test=duelTest,actor=test.cleanRound(),max=actor.max;
 for(const field of ['shield','inv','dashT','leap']){
  actor.shield=actor.inv=actor.dashT=actor.leap=0;actor[field]=.5;
  partyHurt(actor,20);test.check(actor.hp===max,field+' must reject damage');
 }
 actor.shield=actor.inv=actor.dashT=actor.leap=0;
 for(const amount of [NaN,Infinity,-20,0])partyHurt(actor,amount);
 test.check(actor.hp===max,'Invalid damage must not alter health');
 battleDamage(actor,20,actor);test.check(actor.hp===max,'No same-team damage');
 partyHurt(actor,20);test.check(actor.hp===max-20&&actor.inv>0&&actor.stagger>0,'An unprotected hit must apply actual damage and a reaction');
 partyHurt(actor,20);test.check(actor.hp===max-20,'Repeated contact respects invulnerability');
 actor.inv=0;actor.formT=1;partyHurt(actor,20);test.check(Math.abs(actor.hp-(max-31))<1e-8,'Void mitigation is applied by the simulation');
 actor.inv=0;actor.formT=0;actor.fragileT=1;partyHurt(actor,20);test.check(Math.abs(actor.hp-(max-61))<1e-8,'Incarnation fragility changes actual damage');
 actor.inv=0;actor.fragileT=0;actor.attack={struck:false,charge:2};actor.shot=1;actor.overcharge=0;
 partyHurt(actor,1);test.check(actor.attack===null&&actor.shot<=.16&&actor.overcharge===2,'A hit cancels and refunds an unstruck charged attack');
 actor.inv=0;partyHurt(actor,10000);test.check(actor.hp===0&&actor.downed&&actor.proxy.dead,'A defeated opponent has one consistent body/proxy state');
 updateBattle(1/60);test.check(battle.ended&&battle.wins[p.slot]===1&&state==='won','Real damage concludes exactly one round');
 updateBattle(1/60);test.check(battle.wins[p.slot]===1,'A concluded round cannot score twice');
 resetDuelRound();test.check(battle.round===2&&battle.wins[p.slot]===1&&actor.hp===actor.max&&!actor.downed,'The next round restores both bodies and retains the score');
 test.check(!classEffects.length&&!bullets.length&&actor.attack===null&&p.attack===null,'The next round cannot carry an attack or persistent effect');
 return {health:max,round:battle.round,wins:battle.wins.slice()};
}'''


BLADE_CONTACT = r'''() => {
 const test=duelTest,actor=localParty[0],avatar=actor.avatar,dt=1/120;
 test.check(actor.heroId==='lame'&&avatar.motionCalibration,'Use the approved, imported Lame source');
 function prime(){
  test.cleanRound();actor.x=0;actor.z=-7;actor.aim=0;actor.inv=999;
  p.x=14;p.z=-7;p.vx=p.vz=0;p.max=p.hp=10000;p.inv=0;
  actor.root.position.set(actor.x,0,actor.z);actor.combo=0;actor.comboWindow=0;
  partyFire(actor);test.check(usesBladeContacts(actor.attack,avatar,'lame'),'The actor must use physical weapon contact');
  return actor.attack;
 }
 function pose(){t+=dt;poseDuelActor(actor,dt);avatar.root.updateWorldMatrix(true,true);}
 const reference=prime(),candidates=[];
 for(let i=0;actor.attack&&i<900;i++){
  pose();const a=actor.attack;
  if(a.elapsed>=a.hitAt&&a.elapsed<=a.activeEnd){
   const base=(avatar.bladeBase||avatar.hand).getWorldPosition(new THREE.Vector3()),tip=avatar.blade.getWorldPosition(new THREE.Vector3());
   for(const u of [1,.8,.6]){const point=base.clone().lerp(tip,u);if(point.y>.12&&point.y<2.1&&Math.hypot(point.x-actor.x,point.z-actor.z)>1.05)candidates.push({x:point.x,z:point.z});}
  }
  resolveBladeContacts(actor,avatar,'lame');advanceDuelAttack(actor,dt);
 }
 test.check(actor.attack===null&&candidates.length>0,'The authored weapon sweeps through a reachable body height');
 function attempt(point,mode='contact'){
  const attack=prime();p.x=point.x;p.z=point.z;let hits=0,early=true,recover=true,wall=null;
  if(mode==='wall'){wall={x:(actor.x+p.x)/2,z:(actor.z+p.z)/2,w:.8,d:.8};obstacles.push(wall);}
  for(let i=0;actor.attack&&i<900;i++){
   // Explicitly remove i-frames here to isolate the one-hit-per-sweep guard.
   p.inv=0;pose();const current=actor.attack,elapsed=current.elapsed,before=p.hp;
   if(mode!=='recovery'||elapsed>current.activeEnd+dt)resolveBladeContacts(actor,avatar,'lame');
   if(p.hp<before){hits++;if(elapsed<current.hitAt)early=false;if(elapsed>current.activeEnd)recover=false;}
   const beforeAdvance=p.hp;advanceDuelAttack(actor,dt);
   test.check(p.hp===beforeAdvance,'The calibrated actor must not add a legacy cone hit');
  }
  if(wall)obstacles.splice(obstacles.indexOf(wall),1);
  return {hits,early,recover,lost:10000-p.hp,duration:attack.duration,hitAt:attack.hitAt,activeEnd:attack.activeEnd,ended:actor.attack===null};
 }
 let selected=null,contact=null;
 for(let i=0;i<candidates.length;i+=Math.max(1,Math.floor(candidates.length/14))){const result=attempt(candidates[i]);if(result.hits){selected=candidates[i];contact=result;break;}}
 test.check(selected&&contact.hits===1&&contact.early&&contact.recover&&contact.ended,'A fixed body must receive exactly one source-timed blade contact');
 const wall=attempt(selected,'wall'),recovery=attempt(selected,'recovery');
 test.check(wall.hits===0&&recovery.hits===0,'Neither cover nor recovery-only contact may deal blade damage');
 const source=avatar.motionCalibration.attacks.attack1;
 test.check(Math.abs(reference.duration-source.duration)<1e-6&&Math.abs(reference.hitAt-source.hitAt)<1e-6,'The opponent retains source animation timing');
 return {contact,wall,recovery,point:selected};
}'''


RIFLE_COVER = r'''() => {
 const test=duelTest,actor=localParty[0];
 function shoot(x){
  test.cleanRound();actor.x=x;actor.z=-12;actor.aim=0;actor.inv=999;
  p.x=14;p.z=-24;p.inv=0;p.hp=p.max;
  actor.root.position.set(actor.x,0,actor.z);partyFire(actor);
  let found=null;
  for(let i=0;i<300&&!found;i++){test.input();update(1/120);found=bullets.find(b=>b.partyShot&&b.owner===actor);}
  test.check(found,'The actual rifle animation must emit its projectile');
  test.check(found.heroId==='rempart'&&found.owner===actor,'The projectile keeps its source hero and owner');
  const origin={x:found.x,z:found.z};
  // Match the actual imported muzzle axis rather than assuming its local offset.
  p.x=found.x;p.z=-22;p.vx=p.vz=0;p.inv=0;const before=p.hp;
  for(let i=0;i<150;i++){test.input();update(1/120);}
  return {origin,lost:before-p.hp,remaining:bullets.some(b=>b===found)};
 }
 const covered=shoot(5.5),open=shoot(0);
 test.check(covered.lost===0&&!covered.remaining,'A rifle shot must stop at the real pillar');
 test.check(open.lost>0&&!open.remaining,'The same native rifle must damage a body in the clear lane');
 // The authored muzzle is inside the body's collision radius in this pose.
 // The native pillar/open-lane checks above prove the real weapon. This distinct
 // regression controls an extended socket to cover future long-barrel weapons;
 // it is explicitly not evidence that the current model crosses legal cover.
 test.cleanRound();actor.x=0;actor.z=-7;actor.aim=0;p.x=14;p.z=-24;
 partyFire(actor);actor.attack.elapsed=actor.attack.hitAt;poseDuelActor(actor,actor.attack.hitAt);
 actor.root.updateWorldMatrix(true,true);
 const anchor=actor.avatar.muzzle,savedAnchor=anchor.position.clone(),body={x:actor.x,z:actor.z},nativeMuzzle=anchor.getWorldPosition(new THREE.Vector3());
 let muzzleCover=null;
 try{
  const extendedWorld=new THREE.Vector3(body.x,nativeMuzzle.y,body.z-1.5);
  anchor.parent.updateWorldMatrix(true,false);anchor.position.copy(anchor.parent.worldToLocal(extendedWorld));
  actor.root.updateWorldMatrix(true,true);
  const muzzle=anchor.getWorldPosition(new THREE.Vector3());muzzle.z-=.08;
  const cover={x:body.x+(muzzle.x-body.x)*.75,z:body.z+(muzzle.z-body.z)*.75,w:.02,d:.02};
  obstacles.push(cover);
  try{
   test.check(!blocked(body.x,body.z,.48),'The extended-socket fixture must keep the body legally outside thin cover');
   const wall=projectileBlockedAlong(body.x,body.z,muzzle.x,muzzle.z,.1);
   test.check(wall,'The controlled extended socket must cross actual cover collision');
   const before=bullets.length,beforeEffects=effects.length;partyStrike(actor);
   test.check(bullets.length===before,'An extended muzzle crossing nearby cover must not spawn a projectile beyond it');
   const impact=effects.at(-1)?.mesh.position;
   test.check(effects.length===beforeEffects+1&&impact&&Math.hypot(impact.x-wall.x,impact.z-wall.z)<1e-6,'The blocked shot must show its impact at the first cover contact');
   muzzleCover={fixture:'controlled extended muzzle anchor; not authored weapon proof',body,nativeMuzzle:{x:nativeMuzzle.x,z:nativeMuzzle.z},muzzle:{x:muzzle.x,z:muzzle.z},cover,wall};
  }finally{obstacles.splice(obstacles.indexOf(cover),1);}
 }finally{anchor.position.copy(savedAnchor);actor.root.updateWorldMatrix(true,true);}
 return {covered,open,muzzleCover};
}'''


RIFLE_ORIENTATION = r'''() => {
 const test=duelTest,actor=localParty[0],avatar=avatarRuntime.current,report=[];
 for(const mode of ['guard','release']){
  test.cleanRound();p.x=actor.x=0;p.z=actor.z=-7;p.vx=p.vz=actor.vx=actor.vz=p.motionSpeed=actor.motionSpeed=0;
  aim=targetAim=actor.aim=0;player.root.position.set(0,0,-7);player.root.rotation.set(0,0,0);
  for(const a of [avatar,actor.avatar]){a.mixer.stopAllAction();a.action=a.lowerAction=null;a.lastAttack=null;resetAvatarKinematics(a);playAvatarAction(a,'guard',0,true);playLowerAction(a,'guard',0,true);a.mixer.update(0);}
  const seconds=mode==='release'?avatar.motionCalibration.shot.hitAt:.4;
  if(mode==='release'){beginAttack();partyFire(actor);test.check(p.attack&&actor.attack,'Both source and clone must perform the real rifle attack');}
  for(let elapsed=0;elapsed<seconds-1e-9;){const dt=Math.min(1/120,seconds-elapsed);elapsed+=dt;t+=dt;if(mode==='release')p.attack.elapsed=actor.attack.elapsed=elapsed;updateRigAvatar(dt);poseDuelActor(actor,dt);}
  const direction=a=>{a.root.updateWorldMatrix(true,true);return a.muzzle.getWorldPosition(new THREE.Vector3()).sub(a.foregrip.getWorldPosition(new THREE.Vector3())).normalize();};
  const source=direction(avatar),opponent=direction(actor.avatar),forward=new THREE.Vector3(0,0,-1),same=source.dot(opponent);
  test.check(source.dot(forward)>.8&&opponent.dot(forward)>.8,'Both rifle axes must follow their public aim in '+mode+': '+JSON.stringify({source:source.toArray(),opponent:opponent.toArray()}));
  test.check(same>1-1e-6,'A cloned rifle must retain the source axis in '+mode);
  report.push({mode,source:source.toArray(),opponent:opponent.toArray(),same});
 }
 return report;
}'''


KIT_CHECK = r'''() => {
 const test=duelTest,actor=test.cleanRound(),id=hero,avatar=avatarRuntime.current;
 test.check(actor.heroId===id,'Both native bodies must exercise the selected class');
 test.check(actor.avatar!==avatar&&actor.root!==player.root,'The opponent has a separate runtime avatar');
 const canonical=new THREE.Quaternion().setFromEuler(new THREE.Euler(0,Math.PI,0));
 test.check(Math.abs(avatar.root.quaternion.dot(canonical))>1-1e-10&&Math.abs(actor.avatar.root.quaternion.dot(canonical))>1-1e-10,'Source and clone retain one canonical model-facing transform');
 const own=test.ownedBones(avatar),other=test.ownedBones(actor.avatar);
 test.check(own?.length>5&&other?.length>5&&own.every(b=>!other.includes(b)),'Skinned actors cannot share mutable bones');
 p.heat=actor.heat=0;beginAttack();partyFire(actor);
 const local=p.attack,remote=actor.attack;
 test.check(local&&remote&&local.melee===remote.melee&&local.id!==undefined&&remote.id!==undefined,'Both controls create a stable, native attack');
 test.check(Math.abs(local.duration-remote.duration)<1e-6&&Math.abs(local.hitAt-remote.hitAt)<1e-6,'Equivalent player and opponent attacks retain identical source timing');
 const definition=HERO_DEFS[id].melee?actor.avatar.motionCalibration?.attacks?.attack1:actor.avatar.motionCalibration?.shot;
 if(definition){test.check(Math.abs(remote.duration-definition.duration)<1e-6&&Math.abs(remote.hitAt-definition.hitAt)<1e-6,'Opponent attacks use their own source timing');}
 const attackReport={duration:remote.duration,hitAt:remote.hitAt,calibrated:!!definition};
 test.tick(Math.ceil(Math.max(local.duration,remote.duration)*60)+4);
 test.check(!p.attack&&!actor.attack,'Both native attacks finish without a stuck action');
 if(id==='cendres'){
  test.cleanRound();p.heat=actor.heat=100;beginAttack();partyFire(actor);
  const hotLocal=p.attack,hotRemote=actor.attack;
  test.check(hotLocal&&hotRemote&&Math.abs(hotLocal.duration-local.duration*1.6)<1e-6&&Math.abs(hotLocal.hitAt-local.hitAt*1.6)<1e-6,'Player overheat scales both duration and source hit time');
  test.check(Math.abs(hotLocal.duration-hotRemote.duration)<1e-6&&Math.abs(hotLocal.hitAt-hotRemote.hitAt)<1e-6,'Overheated Cendres has identical player and opponent timing');
  attackReport.overheated={duration:hotLocal.duration,hitAt:hotLocal.hitAt};
  test.tick(Math.ceil(Math.max(hotLocal.duration,hotRemote.duration)*60)+4);
  test.check(!p.attack&&!actor.attack,'Both overheated native attacks complete');
 }
 test.cleanRound();p.stagger=actor.stagger=.2;dash();test.input({dash:true,x:-1,z:0});update(1/60);
 test.check(p.dash>0&&p.dashT>0&&actor.dash>0&&actor.dashT>0,'Both class controls accept a dodge');
 test.check(p.stagger===0&&actor.stagger===0,'A valid dodge releases hit stagger');
 const px=p.x,pz=p.z,ax=actor.x,az=actor.z,duration=Math.max(actorDodgeConfig(p).duration,actorDodgeConfig(actor).duration);
 test.tick(Math.ceil((duration+.18)*60));
 const localDistance=Math.hypot(p.x-px,p.z-pz),remoteDistance=Math.hypot(actor.x-ax,actor.z-az);
 test.check(localDistance>.5&&remoteDistance>.5&&test.finite(p)&&test.finite(actor),'Both dodges physically move finite bodies');
 test.check(!blocked(p.x,p.z,.47)&&!blocked(actor.x,actor.z,.47),'Class dodges end at legal body positions');
 test.cleanRound();p.heat=actor.heat=72;const serial=p.powerVisualSerial||0,remoteSerial=actor.powerVisualSerial||0;
 power();test.input({power:true});update(1/60);
 test.check(p.power>0&&actor.power>0,'Both native bodies accept their own class power');
 if(avatar.motionCalibration?.power)test.check(p.powerVisualSerial>serial&&p.powerVisualT>0,'Player power has its authored visual lifetime');
 if(actor.avatar.motionCalibration?.power)test.check(actor.powerVisualSerial>remoteSerial&&actor.powerVisualT>0,'Opponent power has its authored visual lifetime');
 const powerReport={local:p.power,opponent:actor.power,localVisual:p.powerVisualT||0,opponentVisual:actor.powerVisualT||0};
 if(id==='rempart')test.check(p.shield>0&&actor.shield>0,'Both Remparts actually shield');
 if(id==='voltigeur')test.check(p.leap>0&&actor.leap>0,'Both Voltigeurs actually leap');
 if(id==='cendres')test.check(p.heat===0&&actor.heat===0&&classEffects.filter(f=>f.kind==='burn').length===2,'Both Cendres consume heat into distinct zones');
 if(id==='tisseuse')test.check(classEffects.filter(f=>f.kind==='rift').length===2,'Both Tisseuses own a separate rift');
 if(id==='voleur')test.check(classEffects.filter(f=>f.kind==='double').length===2,'Both Voleurs own a separate double');
 if(id==='colosse')test.check(classEffects.filter(f=>f.kind==='cover'&&f.collider.length>0).length===2,'Both Colosses create actual colliders');
 if(id==='neant')test.check(p.formT>0&&actor.formT>0,'Both Void bodies transform');
 if(id==='eclipse'){
  p.incarnation=actor.incarnation=100;activateIncarnation();test.input();update(1/60);test.input({extra:true});update(1/60);
  test.check(p.incarnateT>0&&actor.incarnateT>0&&p.incarnation===0&&actor.incarnation===0,'Both secret kits spend their actual Incarnation meter');
 }
 // Validate actual class instances through the production snapshot schema.
 // This isolates host serialization; lan_game.py separately checks delivery.
 const wire=EclipseLanProtocol.createPacket('snapshot',EclipseLanProtocol.createSessionId(),0,lanSerializeSnapshot()).payload;
 const persistent={tisseuse:'rift',cendres:'burn',voleur:'double',bergere:'bergere',colosse:'cover',accordeur:'rhythm',neant:'neant',eclipse:'eclipse'}[id];
 if(persistent)for(const slot of [0,1])test.check(wire.effects.some(f=>f.kind===persistent&&f.owner===slot),'The actual '+id+' persistent effect keeps owner '+slot+' across serialization');
 if(id==='tisseuse')test.check(wire.effects.every(f=>f.kind!=='rift'||Number.isFinite(f.x2)&&Number.isFinite(f.z2)),'Both serialized rifts have a finite exit');
 if(id==='colosse')test.check(wire.effects.filter(f=>f.kind==='cover').every(f=>f.boxes.length>0),'The actual cover geometry crosses the snapshot boundary');
 if(id==='eclipse')test.check(wire.effects.filter(f=>f.kind==='incarnation').length===2,'Both Incarnation effects cross the snapshot boundary');
 test.check(test.finite(p)&&test.finite(actor)&&p.hp>0&&actor.hp>0,'Each class remains a valid playable body after its kit');
 return {hero:id,attack:attackReport,dodge:{localDistance,remoteDistance,duration},power:powerReport,serializedEffects:wire.effects.map(f=>({kind:f.kind,owner:f.owner}))};
}'''


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'docs')))
Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path='/usr/bin/chromium', headless=True,
            args=['--no-sandbox', '--enable-unsafe-swiftshader'])
        page = browser.new_page(viewport={'width': 1100, 'height': 760})
        page.set_default_timeout(60000)
        page.add_init_script('requestAnimationFrame=()=>0')
        errors, external = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: external.append(request.url)
                if request.url.startswith('http') and not request.url.startswith('http://127.0.0.1:') else None)
        page.goto(f'http://127.0.0.1:{server.server_port}/')
        page.wait_for_function('avatarRuntime.status==="ready"&&sessionUi.initialized', polling=50)
        run = page.evaluate
        run(HELPERS)
        assert page.locator('#playMode option').count() == 3
        assert page.locator('#duelOpponentHero option').count() == 10
        assert page.locator('[data-hero=eclipse]').is_disabled()
        # Use a genuine old refuge and a nontrivial complete-journey checkpoint.
        run('''soundOn=false;hero='rempart';start();chooseBoon('vigor');snapshotCampaign(CAMPS[0]);
          localProfile.journey={level:2,hero:'rempart',boon:'vigor',checkpoint:1,route:'',core:180};
          localProfile.completed=[1];persistProfile();document.querySelector('#back').click();
          window.adventureBeforeDuels=duelTest.save();''')
        page.select_option('#playMode', 'duel')
        page.select_option('#duelOpponentHero', 'rempart')
        page.select_option('#botDifficulty', 'tactician')
        page.click('#start')
        page.wait_for_function('state==="playing"&&battle?.kind==="bot"&&!partyLoading', polling=50)
        assert run('localParty.length===1&&enemies.filter(e=>e.partyOwner).length===1&&journey.root.name==="DuelArena"&&boon===""')
        run('duelTest.unchanged(adventureBeforeDuels)')
        report = {'botCover': run(BOT_COVER), 'damage': run(DAMAGE_RULES)}
        run('duelTest.unchanged(adventureBeforeDuels)')

        run('ensureHeroModel("lame")')
        run("beginDuelMatch({kind:'lan-host',opponentHero:'lame',seed:31})")
        report['blade'] = run(BLADE_CONTACT)
        run("beginDuelMatch({kind:'lan-host',opponentHero:'rempart',seed:32})")
        report['rifle'] = run(RIFLE_COVER)
        run('duelTest.unchanged(adventureBeforeDuels)')

        # Secret access is granted explicitly by the test, after the locked UI
        # and untouched ordinary adventure have already been checked.
        run("localProfile.secret=[true,true,true];refreshProfileUI();sessionHeroOptions(document.querySelector('#duelOpponentHero'));window.unlockedAdventureBefore=duelTest.save();")
        assert page.locator('#duelOpponentHero option').count() == 11
        report['kits'] = []
        for name in run('Object.keys(HERO_DEFS)'):
            run('(id)=>ensureHeroModel(id)', name)
            run("async id=>{hero=id;await beginDuelMatch({kind:'lan-host',opponentHero:id,seed:73});}", name)
            orientation = run(RIFLE_ORIENTATION) if name in ['rempart', 'cendres'] else None
            result = run(KIT_CHECK)
            if orientation is not None: result['rifleOrientation'] = orientation
            report['kits'].append(result)
            run('duelTest.unchanged(unlockedAdventureBefore)')

        # Re-enter actual matches, then send one real configured key event.
        # Counting the handler entry catches duplicate bindings even if a second
        # activation would otherwise be concealed by the new cooldown.
        run("hero='rempart';window.originalDuelPower=power;window.originalDuelDodge=requestDodge;window.duelKeyCalls={power:0,dodge:0};power=function(){duelKeyCalls.power++;return originalDuelPower(...arguments)};requestDodge=function(){duelKeyCalls.dodge++;return originalDuelDodge(...arguments)};inputBindings={power:{code:'KeyK',label:'K'},dodge:{code:'KeyL',label:'L'}};")
        for index in range(3):
            run("beginDuelMatch({kind:'bot',opponentHero:'rempart',seed:99})")
            run('initSessionUI();releaseMenuFocus();duelKeyCalls.power=duelKeyCalls.dodge=0;')
            page.keyboard.press('k')
            page.keyboard.press('l')
            assert run('duelKeyCalls.power===1&&duelKeyCalls.dodge===1'), f'Duplicate input on match {index + 1}'
            assert run('p.power>0&&(p.dodgeBuffer>t||p.dash>0)'), 'Configured keys must cast the power and queue or immediately consume the available dodge'
            run('update(1/60)')
            assert run('p.dash>0'), 'The configured dodge must be consumed by the actual simulation'
            assert run('localParty.length===1&&enemies.filter(e=>e.partyOwner).length===1&&scene.children.filter(o=>o.name==="DuelOpponent").length===1')
            assert page.locator('#duelOptions').count() == 1
            run("document.querySelector('#back').click()")
            assert run('state==="menu"&&battle===null&&localParty.length===0&&!scene.children.some(o=>o.name==="DuelOpponent")')
        run('duelTest.unchanged(unlockedAdventureBefore);power=originalDuelPower;requestDodge=originalDuelDodge;inputBindings={};')
        page.select_option('#playMode', 'solo')
        page.click('#continueJourney')
        page.wait_for_function('state==="playing"&&journey.level===2&&journey.step===1', polling=50)
        assert run('battle===null&&localParty.length===0&&!enemies.some(e=>e.partyOwner)&&journey.root.name!=="DuelArena"&&hero==="rempart"')
        run('update(1/60);renderer.render(scene,camera)')
        assert not errors, errors
        assert not external, external
        browser.close()
    print(json.dumps(report, ensure_ascii=False))
    print('PASS: real tactical duel UI; 14 s bounded cover navigation; shields, invulnerability and rounds; imported Lame contact windows; rifle cover; eleven native class attacks, dodges and powers; three match lifecycles with one configured action per key; old refuge and adventure continuation preserved. Controlled browser integration, not human balance or hardware performance.')
finally:
    server.shutdown()
    server.server_close()
