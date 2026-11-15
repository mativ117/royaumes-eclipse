"""Art state, original models, guide wind, shaders, gates, and restore resources."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1100,'height':760});errors=[];console=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
 page.set_content('<script>requestAnimationFrame=()=>0</script>'+(ROOT/'docs/index.html').read_text());page.click('#start');run=page.evaluate
 run('soundOn=false;p.inv=999;updateArtDirection(.02);renderer.render(scene,camera)')
 assert run('artDirection.grassMesh.count>300&&artDirection.contacts.count>0')
 assert run('campaign.landmarks.every(m=>m.craft&&m.root.userData.craftKind)')
 assert run('artDirection.gates.every(g=>g.craftedGate.hinges.length===2&&g.mesh.geometry.attributes.position.count===0)')
 assert run('document.body.classList.contains("immersive")')
 # Optional presentation is separate from controls and world state.
 run('state="menu";document.querySelector("#menu").hidden=false');page.select_option('#presentation','detailed')
 assert not run('document.body.classList.contains("immersive")')
 page.select_option('#presentation','immersive');run('state="playing";document.querySelector("#menu").hidden=true')
 run('var gate=world.obstacles.find(o=>o.gate==="pact");updateArtDirection(.1);var closed=gate.craftedGate.open;chooseBoon("haste");updateArtDirection(.2)')
 assert run('gate.craftedGate.open>closed&&gate.mesh.visible')
 run('p.x=26;p.z=-47;var valve=campaign.trialModels.find(m=>m.kind==="valve");var initial=valve.crystal.rotation.z;trialInteract({type:"valve",id:valve.id});t+=.2;updateArtDirection(.2);poseHero(.01)')
 assert run('valve.crystal.rotation.z>initial&&campaign.worldUse.type==="valve"&&player.arms[1].rotation.x>.5')
 # Wind requires an explicit hint, follows the valid route, then disappears.
 run('p.x=0;p.z=-38;navCache=null;guideRevealUntil=0;updateArtDirection(.1)');assert not run('artDirection.wind.visible')
 run('revealGuide();updateLandmarkReadability();updateArtDirection(.1);renderer.render(scene,camera)')
 assert run('artDirection.wind.visible&&artDirection.wind.count===22')
 run('state="map";updateArtDirection(.1)');assert not run('artDirection.wind.visible')
 run('state="playing";t+=8;updateArtDirection(.1)');assert not run('artDirection.wind.visible')
 run('p.x=-40;p.z=-58;for(let i=0;i<12;i++)updateArtDirection(1)');assert run('Math.abs(scene.fog.color.r-artDirection.palettes["Archives du Reflet"].fog.r)+Math.abs(scene.fog.color.g-artDirection.palettes["Archives du Reflet"].fog.g)+Math.abs(scene.fog.color.b-artDirection.palettes["Archives du Reflet"].fog.b)<.01')
 # Compile the wind-animated grass shader in standard, then verify the light option.
 run('renderer.render(scene,camera)');assert run('renderer.info.render.calls')<400
 run('var resources=[];for(let i=0;i<4;i++){restoreCampaign();update(1/60);updateArtDirection(.02);renderer.render(scene,camera);resources.push(renderer.info.memory.geometries)}')
 assert run('Math.max(...resources.slice(1))-Math.min(...resources.slice(1))<8'),run('resources')
 run('p.x=-20;p.z=-15;resetHeroAt(-20,-15);boon="haste";campaign.trials.escort.started=true;update(1/60);updateArtDirection(.02);renderer.render(scene,camera)')
 page.screenshot(path='/tmp/royaumes-011-garden.png')
 page.select_option('#quality','light',force=True);run('renderer.render(scene,camera)')
 assert not run('art.detail.visible') and run('renderer.info.render.calls')<400
 assert not errors,errors
 assert not console,console
 b.close()
 print('PASS: original landmark craft, animated gates, interaction pose, optional sparse HUD, request-only route wind, shader compilation, actor shadows, stable geometry resources and light-quality draw budget.')
