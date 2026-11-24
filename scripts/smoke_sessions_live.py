"""Public Pages smoke: actual bot match and unpaired phone LAN lobby.

Controlled software WebGL; neither a hardware benchmark nor a native LAN test.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_checks import install_csp_wait

install_csp_wait()
version = (Path(__file__).resolve().parents[1] / 'VERSION').read_text().strip()
url = 'https://mativ117.github.io/royaumes-eclipse/?v=' + version
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
    context = browser.new_context(viewport={'width': 1100, 'height': 760})
    context.add_init_script('requestAnimationFrame=()=>0')
    page = context.new_page()
    errors, missing, forbidden = [], [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: missing.append(response.url) if response.status >= 400 else None)
    page.on('request', lambda request: forbidden.append(request.url) if request.url.startswith('https://') and not request.url.startswith('https://mativ117.github.io/') else None)
    page.goto(url)
    page.wait_for_function('avatarRuntime.status==="ready"', polling=50)
    assert page.evaluate('ROYAUMES_VERSION') == version
    assert page.locator('#playMode option').count() == 3
    page.select_option('#quality', 'light')
    page.select_option('#playMode', 'duel')
    page.select_option('#duelOpponentHero', 'voleur')
    page.select_option('#botDifficulty', 'tactician')
    page.click('#start')
    page.wait_for_function('state==="playing"&&battle?.kind==="bot"&&!partyLoading', polling=50)
    page.evaluate('soundOn=false;p.inv=999;for(let i=0;i<240;i++)update(1/60);frame(performance.now())')
    assert page.evaluate('battle.time<87&&battle.time>85&&localParty.length===1&&localParty[0].avatar.motionCalibration.heroId==="voleur"&&Number.isFinite(p.hp)')
    assert page.evaluate('Math.abs(localParty[0].avatar.root.quaternion.dot(new THREE.Quaternion().setFromEuler(new THREE.Euler(0,Math.PI,0))))>1-1e-6')
    page.keyboard.press('e')
    assert page.evaluate('p.power>0&&p.shield>0')
    page.screenshot(path='/tmp/royaumes-live-duel-1.5.png')
    page.evaluate('pause()')
    page.click('#back')
    assert page.evaluate('state==="menu"&&battle===null&&localParty.length===0')
    page.set_viewport_size({'width': 390, 'height': 844})
    page.select_option('#playMode', 'lan')
    assert page.locator('#lanPanel').is_visible()
    assert page.evaluate('!lanActive()&&!lanSession.peer?.connected&&document.documentElement.scrollWidth<=innerWidth')
    assert 'expérimental' in page.locator('#menu').text_content()
    page.locator('#lanPanel').scroll_into_view_if_needed()
    page.screenshot(path='/tmp/royaumes-live-lan-lobby-1.5.png')
    assert not errors, errors
    assert not missing, missing
    assert not forbidden, forbidden
    browser.close()
print('PASS LIVE: bot duel, actual Voleur model, four-second simulation, native power, menu cleanup and portrait unpaired LAN lobby. No external API, errors or missing resources. NOT a native RTC or physical-phone result.')
