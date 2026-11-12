"""Readable objectives, valid guidance, item states, map UI and mobile layout."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'docs/index.html').read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 errors=[]
 page=b.new_page(viewport={'width':1100,'height':800});page.add_init_script('requestAnimationFrame=()=>0');page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.click('#start');run=page.evaluate
 # Real route includes the wall detour, every step stays on ground and out of solids.
 run('soundOn=false;boon="haste";p.x=0;p.z=-38;campaign.keys=new Set(["west","east"]);')
 for x,z in [(-52,-68),(54,-68),(26,-47),(39,-68)]:
  result=run(f'var route=buildGuideRoute({{x:{x},z:{z}}});({{count:route.length,safe:route.every(q=>!blocked(q.x,q.z,.55)),arrived:Math.hypot(route.at(-1)?.x-({x}),route.at(-1)?.z-({z}))<1.8}})')
  assert result['count'] and result['safe'] and result['arrived'],result
 assert not run('buildGuideRoute({x:0,z:-80}).length'),'Closed ritual gate must block courtyard guidance'
 run('campaign.keys=new Set();campaign.trials=freshTrials();p.x=0;p.z=-38;toggleMap();')
 assert page.locator('.missionChoice').count()==2
 page.locator('.missionChoice').filter(has_text='carillon').click();assert run('trackedGoal')=='bells'
 assert 'fresque' in page.locator('#missionList').text_content()
 page.uncheck('#guidanceToggle');assert not run('guidanceOn') and not run('guideRoute().length')
 page.check('#guidanceToggle');page.uncheck('#threatToggle');assert not run('mapThreats')
 page.click('#closeMap');assert run('state')=='playing'
 # The next step updates after reading, wrong notes and successful notes.
 run('trialInteract({type:"fresco"});trackedGoal="bells";updateLandmarkReadability();')
 assert run('selectedMission().kind')=='lamp'
 assert run('document.querySelector("#trackedAction").textContent.includes(campaign.trials.bells.order[0])')
 run('trialInteract({type:"lamp",id:campaign.trials.bells.order[0]});updateLandmarkReadability();')
 assert run('document.querySelector("#trackedAction").textContent.includes(campaign.trials.bells.order[1])')
 # Item silhouettes are different; locked/used items do not look like available pickups.
 assert run('campaign.trialModels.find(m=>m.kind==="valve").crystal.geometry.type')=='TorusGeometry'
 assert run('campaign.core.crystal.geometry.type')=='IcosahedronGeometry'
 assert run('campaign.trialModels.find(m=>m.kind==="fresco").crystal.geometry.type')=='BoxGeometry'
 run('var valve=campaign.trialModels.find(m=>m.kind==="valve");campaign.trials.forge.valves.push(valve.id);p.x=valve.x;p.z=valve.z;updateLandmarkReadability()')
 assert not run('valve.tag.visible')
 assert run('landmarkState(campaign.core)')=='locked'
 run('campaign.trials.archive=true;campaign.trials.forge.carrying=true;toggleMap()')
 assert 'Lentille : obtenue' in page.locator('#questItems').text_content()
 assert 'Noyau : transporté' in page.locator('#questItems').text_content()
 # Portrait and landscape: map scrolls to every task and resume, no horizontal page overflow.
 for size in [{'width':390,'height':844},{'width':844,'height':390}]:
  ctx=b.new_context(viewport=size,is_mobile=True,has_touch=True);m=ctx.new_page();m.on('pageerror',lambda e:errors.append(str(e)));m.set_content(html);m.select_option('#quality','light');m.tap('#start');m.evaluate('soundOn=false;p.inv=999');m.wait_for_timeout(250)
  assert m.locator('#trackedTitle').is_visible()
  bounds=m.locator('#missionTracker').bounding_box();assert bounds['x']>=0 and bounds['x']+bounds['width']<=size['width']
  m.tap('#mapButton');assert m.locator('#missionList').is_visible()
  assert m.locator('#guidanceToggle').is_enabled()
  m.locator('.missionChoice').last.tap();m.locator('#closeMap').scroll_into_view_if_needed();m.screenshot(path=f'/tmp/royaumes-091-map-{size["width"]}.png');m.tap('#closeMap');assert m.evaluate('state')=='playing'
  assert m.evaluate('document.documentElement.scrollWidth<=innerWidth')
  m.screenshot(path=f'/tmp/royaumes-091-game-{size["width"]}.png');ctx.close()
 assert not errors,errors
 b.close()
 print('PASS: safe path routes, closed gates, selectable tasks, optional guidance, next-step updates, distinct item shapes/states, inventory, portrait/landscape map scrolling and viewport bounds. No JS errors.')
