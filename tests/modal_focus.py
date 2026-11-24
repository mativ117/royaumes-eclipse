"""Keyboard/pointer modal focus using real game markup; no WebGL or GPU renderer.

The full-game path is optional: run with --integration only after the root has
included modal-focus.js and initModalFocus() before initInputSettings().
"""
from pathlib import Path
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import sys as _check_sys
from pathlib import Path as _CheckPath
_check_sys.path.insert(0,str(_CheckPath(__file__).resolve().parents[1]/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()

ROOT = Path(__file__).resolve().parents[1]
template = (ROOT / 'src/template.html').read_text()
panels = ''.join(re.search(r'<section id="' + name + r'".*?</section>', template, re.S).group(0) for name in ['choicePanel', 'mapPanel', 'journeyChoice'])
bootstrap = '''
let state='playing', mapPreviousState='playing', dodgeCalls=0;
const $=selector=>document.querySelector(selector);
const selectedMode=()=> 'solo';
const keys=new Set();let observing=false;
function requestDodge(){dodgeCalls++;}
function clearInputs(){}
function releaseMenuFocus(){document.activeElement?.blur();}
function toggleMap(){if(state==='map'){state=mapPreviousState;$('#mapPanel').hidden=true;return;}mapPreviousState=state;state='map';$('#mapPanel').hidden=false;}
function openPact(){state='choice';$('#sealPact').disabled=true;$('#choicePanel').hidden=false;$('#interact').hidden=true;setTimeout(()=>$('#sealPact').disabled=false,30);}
function closePact(){state='playing';$('#choicePanel').hidden=true;releaseMenuFocus();}
function openJourneyChoice(){state='choice';$('#journeyChoice').hidden=false;$('#journeyChoices').innerHTML='<button id="routeFirst">Le Couchant</button><button id="routeLast">L’Orage</button>';for(const b of $('#journeyChoices').children)b.onclick=()=>{state='playing';$('#journeyChoice').hidden=true;releaseMenuFocus();};}
$('#mapButton').onclick=toggleMap;$('#closeMap').onclick=toggleMap;$('#interact').onclick=openPact;$('#leavePact').onclick=$('#sealPact').onclick=closePact;
addEventListener('keydown',event=>{if(event.key==='Escape'&&state==='map'){event.preventDefault();toggleMap();}else if(event.key==='Escape'&&state==='choice'){event.preventDefault();if(!$('#journeyChoice').hidden){$('#journeyChoice').hidden=true;state='playing';releaseMenuFocus();}else closePact();}});
'''
html = '''<!doctype html><html lang="fr"><meta charset="utf-8"><style>
body{margin:0;font:16px system-ui}button,input,summary{margin:6px;padding:8px}[hidden]{display:none!important}
.screen{position:fixed;inset:0;overflow:auto;z-index:4;background:#15131a;color:#fff;padding:30px}#choicePanel{z-index:6}#mapPanel{z-index:7}
canvas{width:20px;height:20px}.mapLayout{display:flex;gap:20px}.mapDrawing{max-width:180px}.mapJournal{max-width:400px}
</style><body><div id="hud"><button id="mapButton">Carte</button><button id="interact">Examiner</button></div><canvas id="world" tabindex="0"></canvas><aside id="alreadyInert" inert><button>Déjà inactif</button></aside>''' + panels + '''
<dialog id="helpDialog"><button id="helpClose">Fermer le guide</button></dialog>
<script>''' + bootstrap + '</script><script>' + (ROOT / 'src/modal-focus.js').read_text() + '</script><script>' + (ROOT / 'src/input-settings.js').read_text() + '''</script><script>
$('#missionList').innerHTML='<button id="missionFirst">Objectif suivi</button><button id="missionDisabled" disabled>Indisponible</button><div hidden><button id="missionHidden">Caché</button></div><button id="missionLast">Autre objectif</button><div style="visibility:hidden"><button id="missionInvisible">Invisible</button></div><fieldset disabled><button id="fieldsetDisabled">Indisponible aussi</button></fieldset>';
$('#helpClose').onclick=()=>$('#helpDialog').close();
initModalFocus();initModalFocus();
// Real input capture guard, registered after modal focus as in the game footer.
addEventListener('keydown',handleConfiguredKeyDown,true);addEventListener('keyup',handleConfiguredKeyUp,true);
</script></body></html>'''

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu', '--disable-software-rasterizer'])
    page = browser.new_page(viewport={'width': 1100, 'height': 760})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(html)
    run = page.evaluate
    assert run('modalFocusRuntime.initialized&&modalFocusRuntime.active===null')
    assert run('document.head.querySelectorAll("style").length===2'), 'Init must remain idempotent'
    page.click('#mapButton')
    page.wait_for_function('document.activeElement.id==="missionFirst"', polling=20)
    assert run('modalFocusItems($("#mapPanel")).map(e=>e.id||e.tagName).join(",")==="missionFirst,missionLast,guidanceToggle,threatToggle,SUMMARY,closeMap"')
    assert run('$("#hud").inert&&$("#world").inert&&$("#alreadyInert").inert')
    page.keyboard.press('Shift+Tab')
    assert run('document.activeElement.id==="closeMap"')
    page.keyboard.press('Tab')
    assert run('document.activeElement.id==="missionFirst"')
    page.focus('#guidanceToggle')
    page.keyboard.press('Tab')
    assert run('document.activeElement.id==="threatToggle"')
    page.keyboard.press('Space')
    assert not run('$("#threatToggle").checked')
    page.keyboard.press('Escape')
    page.wait_for_function('state==="playing"&&modalFocusRuntime.active===null', polling=20)
    assert run('document.activeElement.id==="mapButton"&&!$("#hud").inert&&!$("#world").inert&&$("#alreadyInert").inert')
    page.keyboard.press('Space')
    assert run('dodgeCalls===1&&state==="playing"&&$("#mapPanel").hidden'), 'Restored HUD focus must not steal gameplay Space'

    # The first pact action is intentionally disabled during confirmation delay.
    page.click('#interact')
    page.wait_for_function('document.activeElement.id==="leavePact"', polling=10)
    page.wait_for_function('!document.querySelector("#sealPact").disabled', polling=10)
    assert run('document.activeElement.id==="leavePact"'), 'Enabling an earlier action must not move focus'
    page.keyboard.press('Tab')
    assert run('document.activeElement.id==="sealPact"')
    page.keyboard.press('Escape')
    page.wait_for_function('modalFocusRuntime.active===null', polling=20)
    assert run('document.activeElement===document.body&&!$("#hud").inert'), 'Hidden world trigger must not be refocused; canvas must not be invented'

    run('openJourneyChoice()')
    page.wait_for_function('document.activeElement.id==="routeFirst"', polling=20)
    page.keyboard.press('Shift+Tab')
    assert run('document.activeElement.id==="routeLast"')
    page.keyboard.press('Enter')
    page.wait_for_function('state==="playing"&&modalFocusRuntime.active===null', polling=20)
    assert run('document.activeElement===document.body')

    # Dynamic empty/disabled choices keep focus on the dialog, without Tab escape.
    run('state="choice";$("#journeyChoices").innerHTML="<button disabled>Patientez</button>";$("#journeyChoice").hidden=false')
    page.wait_for_function('document.activeElement.id==="journeyChoice"', polling=20)
    page.keyboard.press('Tab')
    assert run('document.activeElement.id==="journeyChoice"')
    page.keyboard.press('Escape')
    page.wait_for_function('modalFocusRuntime.active===null', polling=20)
    assert run('!$("#journeyChoice").hasAttribute("tabindex")')

    # Native help retains ownership; the underlying map regains its last control.
    run('toggleMap()')
    page.wait_for_function('document.activeElement.id==="missionFirst"', polling=20)
    page.focus('#threatToggle')
    run('$("#helpDialog").showModal()')
    page.wait_for_function('document.activeElement.id==="helpClose"&&modalFocusRuntime.active===null', polling=20)
    page.click('#helpClose')
    page.wait_for_function('document.activeElement.id==="threatToggle"&&modalFocusRuntime.active?.id==="mapPanel"', polling=20)
    page.keyboard.press('Escape')
    page.wait_for_function('modalFocusRuntime.active===null', polling=20)

    # Managed layers hand focus back to the still-open lower dialog.
    run('$("#interact").hidden=false;$("#interact").focus();openPact()')
    page.wait_for_function('modalFocusRuntime.active?.id==="choicePanel"', polling=20)
    page.focus('#leavePact')
    run('state="map";$("#mapPanel").hidden=false')
    page.wait_for_function('modalFocusRuntime.active?.id==="mapPanel"', polling=20)
    run('state="choice";$("#mapPanel").hidden=true')
    page.wait_for_function('modalFocusRuntime.active?.id==="choicePanel"&&document.activeElement.id==="leavePact"', polling=20)
    page.keyboard.press('Escape')
    page.wait_for_function('modalFocusRuntime.active===null', polling=20)
    assert run('modalFocusRuntime.inerted.size===0&&modalFocusRuntime.entries.size===0&&$("#alreadyInert").inert')
    assert not errors, errors
    browser.close()

print('PASS: real modal markup, first enabled control, Tab/Shift+Tab containment, hidden/disabled/inert filtering, Escape from map checkbox, Space gameplay, dynamic choices, native/managed layering and sensible restoration. CPU-only, no WebGL context.')

if '--integration' in sys.argv:
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'docs')))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
            page = browser.new_page(viewport={'width': 1100, 'height': 760})
            page.add_init_script('requestAnimationFrame=()=>0')
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            page.wait_for_function('avatarRuntime.status==="ready"', polling=50)
            page.click('#start')
            page.evaluate('soundOn=false;p.inv=999')
            page.click('#mapButton')
            page.wait_for_function('modalFocusRuntime.active?.id==="mapPanel"&&document.querySelector("#mapPanel").contains(document.activeElement)', polling=50)
            page.focus('#guidanceToggle')
            page.keyboard.press('Escape')
            page.wait_for_function('state==="playing"&&modalFocusRuntime.active===null', polling=50)
            page.evaluate('openPact("vigor")')
            page.wait_for_function('modalFocusRuntime.active?.id==="choicePanel"&&document.querySelector("#choicePanel").contains(document.activeElement)', polling=50)
            page.keyboard.press('Escape')
            assert page.evaluate('state==="playing"')
            page.evaluate('openJourneyChoice("route")')
            page.wait_for_function('document.querySelector("#journeyChoice").contains(document.activeElement)', polling=50)
            page.keyboard.press('Escape')
            page.wait_for_function('state==="playing"&&modalFocusRuntime.active===null', polling=50)
            assert not errors, errors
            browser.close()
        print('PASS INTEGRATION: real game map, pact and journey choice focus; Escape from a real map checkbox resumes play.')
    finally:
        server.shutdown(); server.server_close()
