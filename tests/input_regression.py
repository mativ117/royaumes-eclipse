"""Regression: transient focus changes must not pause touch or keyboard gameplay."""
from pathlib import Path
from playwright.sync_api import sync_playwright

html=(Path(__file__).resolve().parents[1]/'docs/index.html').read_text()
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
    errors=[]
    for viewport in [{'width':740,'height':390},{'width':390,'height':740}]:
        context=browser.new_context(viewport=viewport,has_touch=True,is_mobile=True)
        page=context.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html)
        page.tap('#start')
        page.evaluate('p.inv=999')
        client=context.new_cdp_session(page)
        stick=page.locator('#stick').bounding_box()
        fire=page.locator('#fire').bounding_box()
        move={'x':stick['x']+stick['width']/2+32,'y':stick['y']+stick['height']/2,'id':1}
        shoot={'x':fire['x']+fire['width']/2,'y':fire['y']+fire['height']/2,'id':2}
        client.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[move,shoot]})
        page.wait_for_timeout(200)
        assert page.evaluate('state')=='playing'
        before=page.evaluate('p.x')
        shots=page.evaluate('shotCount')
        # This same window focus event paused the original release.
        page.evaluate('window.dispatchEvent(new Event("blur"))')
        assert page.evaluate('state')=='playing'
        assert page.evaluate('joy.x')>0 and page.evaluate('shooting')
        page.wait_for_timeout(300)
        assert page.evaluate('p.x')>before
        assert page.evaluate('shotCount')>shots
        # Press dash with a third finger while movement and fire remain held.
        dash=page.locator('#dash').bounding_box()
        third={'x':dash['x']+dash['width']/2,'y':dash['y']+dash['height']/2,'id':3}
        client.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[move,shoot,third]})
        assert page.evaluate('p.dash')>0
        assert page.evaluate('state')=='playing'
        client.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
        assert page.evaluate('joy.x')==0 and not page.evaluate('shooting')
        # Visible visibilitychange and orientation/resize do not trigger a pause.
        page.evaluate('document.dispatchEvent(new Event("visibilitychange"))')
        assert page.evaluate('state')=='playing'
        page.set_viewport_size({'width':viewport['height'],'height':viewport['width']})
        assert page.evaluate('state')=='playing'
        page.tap('#pause')
        assert page.evaluate('state')=='paused'
        page.tap('#resume')
        assert page.evaluate('state')=='playing'
        # Reproduce the browser's hidden-page notification deterministically.
        page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,get:()=>true});Object.defineProperty(document,"visibilityState",{configurable:true,get:()=>"hidden"});document.dispatchEvent(new Event("visibilitychange"))')
        assert page.evaluate('state')=='paused'
        assert page.evaluate('pauseReason')=='hidden'
        page.evaluate('delete document.hidden;delete document.visibilityState')
        page.tap('#resume')
        assert page.evaluate('state')=='playing'
        # Defeat in the second room resets the encounter, not the expedition.
        page.evaluate('chooseBoon("haste");setupRoom(1);p.inv=0;p.shield=0;p.dashT=0;hurt(999)')
        assert page.evaluate('state')=='lost'
        page.tap('#resume')
        assert page.evaluate('room')==1 and page.evaluate('boon')=='haste'
        assert page.evaluate('p.hp')==page.evaluate('p.max')
        assert not page.evaluate('shard')
        # A chosen first-room pact must not leave its door locked on retry.
        page.evaluate('setupRoom(0);p.inv=0;hurt(999)')
        page.tap('#resume')
        assert page.evaluate('portal.visible')
        assert page.evaluate('boon')=='haste'
        context.close()
    # Space after clicking Resume must dash, never activate a focused Pause button.
    page=browser.new_page(viewport={'width':740,'height':440})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html);page.click('#start');page.evaluate('p.inv=999')
    page.click('#pause');page.click('#resume')
    page.keyboard.press('Space')
    assert page.evaluate('state')=='playing' and page.evaluate('p.dash')>0
    page.keyboard.down('d')
    page.evaluate('window.dispatchEvent(new Event("blur"))')
    assert page.evaluate('state')=='playing' and page.evaluate('keys.size')==0
    page.keyboard.press('Escape');assert page.evaluate('state')=='paused'
    page.keyboard.press('Escape');assert page.evaluate('state')=='playing'
    page.screenshot(path='/tmp/eclipse-v031.png')
    assert not errors,errors
    browser.close()
    print('PASS: landscape+portrait multi-touch move/fire/dash across blur; cancellation; resize; manual+hidden pause; keyboard focus; checkpoint retry with preserved pact. No JS errors.')
