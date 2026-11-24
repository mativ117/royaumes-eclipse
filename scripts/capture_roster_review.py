"""Capture final imported hero models in the actual WebGL studio, without retouching.

Serial GPU job, after build.py. Still images are evidence of rendered assets,
not a performance measurement or an assessment of animation quality.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import hashlib
import json
import time
from playwright.sync_api import sync_playwright
from browser_checks import install_csp_wait

install_csp_wait()
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/previews'
HEROES = ['rempart', 'voltigeur', 'lame', 'tisseuse', 'cendres', 'voleur', 'bergere', 'colosse', 'accordeur', 'neant', 'eclipse']


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    OUT.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'docs')))
    Thread(target=server.serve_forever, daemon=True).start()
    errors = []
    report = {'version': (ROOT / 'VERSION').read_text().strip(), 'captured_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'kind': 'actual WebGL studio stills; no retouching; no device FPS claim', 'outputs': []}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
            page = browser.new_page(viewport={'width': 600, 'height': 760}, device_scale_factor=1)
            page.add_init_script("requestAnimationFrame=()=>0;localStorage.setItem('royaumes-profile-v1',JSON.stringify({secret:[true,true,true]}));")
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
            for hero in HEROES:
                page.goto(f'http://127.0.0.1:{server.server_port}/atelier-lame.html?hero={hero}')
                page.wait_for_function('window.reviewReady===true', polling=50)
                assert page.evaluate('reviewHero') == hero
                assert page.evaluate("()=>{const materials=new Set();model.traverse(o=>{if(o.isMesh)for(const m of(Array.isArray(o.material)?o.material:[o.material]))materials.add(m);});return materials.size>=8&&[...materials].every(m=>m.map?.image?.width>=512&&m.normalMap?.image?.width>=256&&m.roughnessMap?.image?.width>=256);}"), f'{hero}: real embedded PBR maps failed to decode'
                page.add_style_tag(content='header,aside,#message,#load{display:none!important}#view{inset:0!important;height:100dvh!important}')
                page.evaluate("reviewResize();spin=false;angle=.36;elevation=.07;document.querySelector('#motion').value=actions.guard?'guard':'idle';selectMotion();mixer.update(.24);measureReviewFraming();fitReviewCamera();frame(performance.now());")
                target = OUT / f'r5-{hero}-studio.jpg'
                page.screenshot(path=str(target), type='jpeg', quality=90)
                report['outputs'].append({'hero': hero, 'file': target.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'model_sha256': hashlib.sha256((ROOT / f'docs/assets/characters/{hero}.glb').read_bytes()).hexdigest(), 'pose': page.evaluate('active.getClip().name'), 'width': 600, 'height': 760})
                print('Captured', hero, flush=True)
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (ROOT / 'design/CAPTURES-PERSONNAGES-1.5.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
