"""Stable route identity, planted markers, encounter perception and art integration."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1050,'height':750});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((ROOT/'docs/index.html').read_text());page.click('#start')
 # Stop the animation loop after its pending frame for deterministic clocks.
 page.evaluate('requestAnimationFrame=()=>0');page.wait_for_timeout(150);run=page.evaluate
 run('soundOn=false;p.inv=999;boon="haste";campaign.keys=new Set(["west","east"]);p.x=0;p.z=-38;trackedGoal="forge";navCache=null;guideRoute();var rebuilds=guideRebuilds,original=navCache.route.slice(),anchors=JSON.stringify(navCache.anchors);')
 assert run('selectedMission().id')=='forge', 'A valve ID must not overwrite the mission ID'
 # Progress along a route trims it; no periodic search or moving anchors.
 run('for(let i=1;i<Math.min(18,original.length);i++){p.x=original[i].x;p.z=original[i].z;t+=.12;guideRoute()}')
 assert run('guideRebuilds===rebuilds&&navCache.cursor>0&&JSON.stringify(navCache.anchors)===anchors')
 assert run('navCache.anchors.every(a=>!blocked(a.x,a.z,.55))')
 run('p.x=-20;p.z=-38;t+=.1;guideRoute();var before=guideRebuilds;t+=.5;guideRoute()')
 assert run('guideRebuilds===before'),'Short deviation must not trigger a route replacement'
 run('t+=.7;guideRoute()');assert run('guideRebuilds===before+1')
 # The forge target stays selected despite crossing the nearest-item boundary.
 run('subgoalFocus={};p.x=26;p.z=-47;var one=selectedMission().targetId;p.x=53;p.z=-47;var same=selectedMission().targetId')
 assert run('one===same')
 run('campaign.trials.forge.valves.push(one)');assert run('selectedMission().targetId!==one')
 # Two frames of hint markers stay planted; default view is clear, reveal is explicit.
 run('p.x=0;p.z=-38;navCache=null;guideRevealUntil=0;updateLandmarkReadability()')
 assert run('campaign.guidePointers.every(m=>!m.visible)')
 run('revealGuide();updateLandmarkReadability();var markers=campaign.guidePointers.filter(m=>m.visible).map(m=>m.position.toArray());t+=.2;updateLandmarkReadability()')
 assert run('markers.length>0&&JSON.stringify(markers)===JSON.stringify(campaign.guidePointers.filter(m=>m.visible).map(m=>m.position.toArray()))')
 run('t+=8;updateLandmarkReadability()');assert run('campaign.guidePointers.every(m=>!m.visible)')
 # Awareness respects cover, with an actual transition instead of instant aggression.
 run('var foe=spawn(0,-38,"warden");p.x=0;p.z=-33;foe.alert=0;foe.awareness=0;foe.mode="idle";var first=perceiveEnemy(foe,.1)')
 assert not run('first')
 run('for(let i=0;i<8;i++)perceiveEnemy(foe,.1)');assert run('foe.awareness===1&&foe.alert>0')
 run('foe.alert=0;foe.awareness=0;foe.x=0;foe.z=-67;p.x=0;p.z=-71;var hidden=perceiveEnemy(foe,.4)')
 assert not run('hidden') and run('foe.awareness')==0
 assert run('stageAssets.body.warden!==stageAssets.body.archer&&stageAssets.body.archer!==stageAssets.body.sentinel')
 assert run('foe.rig.weapon.parent===foe.rig.arms[1]&&world.stage.root.children.length>4')
 assert run('player.legs.every(l=>l.isGroup&&l.children.length===3)'), 'Boots and knees must follow the leg, rather than slide beneath it'
 # A real hit cancels a pending attack and refunds its unused charge.
 run('p.x=0;p.z=-38;p.shot=0;p.inv=0;p.shield=0;p.dashT=0;p.leap=0;p.overcharge=2;beginAttack();hurt(1)')
 assert run('p.attack===null&&p.overcharge===2')
 assert not errors,errors
 b.close()
 print('PASS: route reuse while walking; stable subtargets; delayed off-route rebuild; planted request-only markers; blocked line of sight; detection delay; distinct enemy rigs; hit interruption and charge refund.')
