"""Smoke-test the actual published game, including lazy hero loading and the chronicle."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];version=(ROOT/'VERSION').read_text().strip()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1000,'height':700});page.add_init_script('requestAnimationFrame=()=>0');errors=[];missing=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:missing.append(r.url) if r.status>=400 else None)
 page.goto('https://mativ117.github.io/royaumes-eclipse/?v='+version);page.wait_for_function('avatarRuntime.status==="ready"',polling=50)
 assert page.evaluate('ROYAUMES_VERSION')==version
 assert 'soleil noir' in page.locator('#storyMenuText').text_content()
 page.select_option('#chapterSelect','2');page.click('[data-hero="tisseuse"]');page.wait_for_function('!!avatarRuntime.heroes.tisseuse&&!document.querySelector("#start").disabled',polling=50);page.click('#start')
 run=page.evaluate;assert run('state==="playing"&&journey.level===2&&hero==="tisseuse"')
 run('p.inv=999;for(let i=0;i<10;i++)update(1/60);updateSoundscape(.1);updateVisualWorld();renderPresentation()')
 assert run('soundscape.events>0&&presentation.stats.postPasses===3')
 run('openChronicle()');assert run('state==="chronicle"');page.keyboard.press('Escape');assert run('state==="playing"')
 page.screenshot(path='/tmp/royaumes-live-1-rc2.png');run('pause()')
 assert not errors,errors
 assert not missing,missing
 b.close()
print('PASS: live root redirect, correct version, contextual story, remote Tisseuse model, chapter II, postprocessing, score scheduling and chronicle pause/resume.')
