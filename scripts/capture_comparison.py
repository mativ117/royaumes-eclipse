"""Capture actual 0.11 and 0.12 starting views. No image generation or retouching."""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
assert (ROOT/'VERSION').read_text().strip()=='0.12','This comparison is pinned to 0.12'
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 for device,viewport in [('pc',{'width':1100,'height':760}),('phone',{'width':390,'height':844})]:
  for version,filename in [('011','historique/cathedrale-v0.11.html'),('012','docs/index.html')]:
   if len(sys.argv)>1 and device+'-'+version!=sys.argv[1]:continue
   context=browser.new_context(viewport=viewport,is_mobile=device=='phone',has_touch=device=='phone');page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.set_content((ROOT/filename).read_text());page.select_option('#quality','light' if device=='phone' else 'standard');page.click('#start');page.wait_for_timeout(7200)
   assert not errors,errors
   assert page.evaluate('state')=='playing'
   assert page.evaluate('Math.abs(p.x)<.01&&Math.abs(p.z-23)<.01')
   if version=='012':assert page.evaluate('avatarRuntime.status')=='ready'
   page.screenshot(path=str(ROOT/f'docs/previews/{device}-{version}.jpg'),type='jpeg',quality=92)
   print('Captured',device,version,flush=True);context.close()
 browser.close()
