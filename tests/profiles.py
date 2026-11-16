"""Local profile import/export, validation, chapter continuation and no fake online account."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
import json,tempfile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'docs')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page();page.add_init_script('requestAnimationFrame=()=>0');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
  run('soundOn=false;ensureHeroModel("lame")');run('hero="lame";start();chooseBoon("vigor");snapshotCampaign(CAMPS[0]);document.querySelector("#back").click();')
  page.get_by_text('Profil et sauvegardes sur cet appareil',exact=True).click();page.locator('#profileName').fill('Voyageur de la nuit');page.locator('#profileName').dispatch_event('change')
  with page.expect_download() as saved:page.click('#exportSave')
  exported=json.loads(Path(saved.value.path()).read_text());assert exported['format']=='royaumes-save-1' and exported['expedition']['version']=='0.9'
  before=run('JSON.stringify(localProfile)')
  page.set_input_files('#importSave',{'name':'invalide.json','mimeType':'application/json','buffer':b'{"format":"wrong"}'});page.wait_for_timeout(100)
  assert run('JSON.stringify(localProfile)')==before
  # Profile fields are validated and displayed as plain text, never HTML.
  imported=exported;imported['profile']['name']='<img src=x onerror=bad()>abc';imported['profile']['secret']=[True,True,True];imported['profile']['journey']={'level':3,'hero':'tisseuse','boon':'haste','checkpoint':4,'route':'storm','core':240};imported['profile']['settings']={'volume':.35,'music':.15,'reduced':True};imported['expedition']=None
  page.set_input_files('#importSave',{'name':'voyage.json','mimeType':'application/json','buffer':json.dumps(imported).encode()});page.wait_for_timeout(100)
  assert run('localProfile.journey.route==="storm"&&localProfile.journey.core===240&&localProfile.name.length===24')
  assert page.locator('#profileName').input_value()==imported['profile']['name'][:24]
  assert page.locator('img[src=x]').count()==0
  assert page.locator('[data-hero=eclipse]').is_enabled()
  assert run('document.body.classList.contains("reduced-effects")&&localStorage.getItem(RUN_KEY)===null')
  page.reload();page.wait_for_function('avatarRuntime.status==="ready"',polling=50)
  assert page.locator('[data-hero=eclipse]').is_enabled()
  page.click('#continueJourney');page.wait_for_function('state==="playing"&&journey.level===3',polling=50)
  assert run('hero==="tisseuse"&&journey.step===4&&journey.route==="storm"&&journey.core===240')
  run('document.querySelector("#back").click();document.querySelector("#profileName").value="";document.querySelector("#profileName").dispatchEvent(new Event("change"))');assert run('localProfile.name')=='Voyageur'
  assert not errors,errors
  b.close()
 print('PASS: local export including old refuge; invalid import leaves data intact; safe name display; secret persistence; reduced effects/settings restore; actual lazy-loaded hero and storm/core checkpoint continuation. No authentication or backend simulated.')
finally:server.shutdown()
