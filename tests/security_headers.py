"""Actual browser enforcement of generated hashes and rejected script injection."""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from html_security import secure_html

source='''<!doctype html><html><head><meta charset="utf-8"><script>
window.trustedModel='before';window.violations=[];addEventListener('securitypolicyviolation',e=>violations.push(e.effectiveDirective));
</script></head><body><button id="test" onclick="window.injectedHandler=true">Test</button></body></html>'''
secured=secure_html(source)
injected=secured.replace('</body>',"<script>window.injectedScript=true</script></body>")
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu','--disable-software-rasterizer'])
 page=b.new_page();page.set_content(injected);page.click('#test')
 assert page.evaluate('trustedModel==="before"&&!window.injectedScript&&!window.injectedHandler')
 assert page.evaluate('violations.some(x=>x==="script-src-elem")&&violations.some(x=>x==="script-src-attr")')
 # Replacing an embedded model changes its script; the snapshot must be rehashed.
 page.close();page=b.new_page();page.set_content(secure_html(secured.replace("trustedModel='before'","trustedModel='after'")))
 assert page.evaluate('trustedModel==="after"')
 assert page.locator('meta[http-equiv="Content-Security-Policy"]').count()==1
 assert page.locator('meta[name="referrer"]').get_attribute('content')=='no-referrer'
 # GLTFLoader fetches embedded texture object URLs before ImageBitmap decode.
 # img-src alone does not authorize that fetch; connect-src must allow blob:.
 assert page.evaluate('''async()=>{const canvas=document.createElement('canvas');canvas.width=canvas.height=1;canvas.getContext('2d').fillRect(0,0,1,1);const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png')),url=URL.createObjectURL(blob);try{const image=await createImageBitmap(await(await fetch(url)).blob());const ok=image.width===1&&image.height===1;image.close();return ok;}finally{URL.revokeObjectURL(url);}}'''), 'The real embedded texture fetch/decode must survive the production CSP'
 b.close()
print('PASS: trusted scripts and embedded texture fetch/decode work, injected scripts/handlers do not, standalone edits are rehashed and referrer policy is set. CPU browser; not a penetration-test certification.')
