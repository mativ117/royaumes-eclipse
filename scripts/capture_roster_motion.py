"""Export two current hero sequences from the real game camera at normal speed.

Serial WebGL job: run only after build.py and separately from other GPU tests.
Each 30 fps video frame advances exactly two fixed 1/60 s simulation steps.
The HUD is hidden for review; actors, level geometry and collisions are retained.
The actual Light preset is selected, with contact shadows, for motion inspection.
This is controlled frame export, without audio, not a device FPS benchmark or a
claim about animation quality. Historical r4 media are never changed.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import hashlib
import json
import subprocess
import tempfile
import time

from playwright.sync_api import sync_playwright
from browser_checks import install_csp_wait

install_csp_wait()
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/previews'
FPS, WIDTH, HEIGHT, SECONDS = 30, 600, 400, 4
HEROES = ('rempart', 'voleur')
HIDE = '#hud,#mobile,#controls,#notice,#zoneBanner,#interact,#bossHUD,.hero-preview,#duelBrain{display:none!important}'

SETUP = r'''() => {
 soundOn=false;clearInputs();
 if(typeof heroPreviewDispose==='function')heroPreviewDispose();
 camera.position.set(p.x,6.7,p.z+10.8);
 cameraLook.set(p.x,1.6,p.z-5);camera.lookAt(cameraLook);
 last=1000-1000/30;accumulator=0;lastRenderedState=null;
 window.proofCalls=0;window.proofOriginalUpdate=update;
 update=function(dt){proofCalls++;return proofOriginalUpdate(dt);};
 mouseAim=true;pointer.set(0,.2);
 return {x:p.x,z:p.z,hp:p.hp,shots:shotCount};
}'''
STEP = r'''({index,input}) => {
 joy.x=input.x||0;joy.y=input.z||0;shooting=!!input.attack;mouseDown=false;
 const now=1000+index*1000/30;
 const elapsed=Math.min(.1,(now-(last||now))/1000),before=proofCalls;
 accumulator=Math.max(0,2/60-elapsed)+1e-9;frame(now);
 if(proofCalls-before!==2)throw Error('Expected two simulation steps; got '+(proofCalls-before));
 return {state,t,x:p.x,z:p.z,hp:p.hp,combo:p.combo,attack:p.attack?.melee?'melee':p.attack?'shot':null,shots:shotCount};
}'''


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def controls(seconds):
    if .2 <= seconds < 1.2:
        return {'z': -.72}
    if 1.2 <= seconds < 1.7:
        return {'x': .65}
    if 1.7 <= seconds < 3.5:
        return {'z': -.34, 'attack': True}
    return {}


def encode(folder, target):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-framerate', str(FPS), '-i', str(folder / 'frame-%04d.png'),
                    '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(target)], check=True)
    meta = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                              '-show_format', '-of', 'json', str(target)]))
    streams = meta['streams']
    video = next(s for s in streams if s['codec_type'] == 'video')
    assert not any(s['codec_type'] == 'audio' for s in streams)
    assert video['width'] == WIDTH and video['height'] == HEIGHT
    assert abs(float(meta['format']['duration']) - SECONDS) < 1 / FPS
    return {'file': target.relative_to(ROOT).as_posix(), 'sha256': digest(target),
            'duration': float(meta['format']['duration']), 'width': WIDTH, 'height': HEIGHT,
            'fps': FPS, 'audio': False, 'playback_speed': 1, 'hardware_fps_measured': False}


def main():
    version = (ROOT / 'VERSION').read_text().strip()
    assert json.loads((ROOT / 'docs/version.json').read_text())['version'] == version, 'Build docs first'
    OUT.mkdir(exist_ok=True)
    report = {
        'version': version,
        'captured_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'notes': [
            'Actual WebGL game, ordinary desktop gameplay camera; controlled input timeline.',
            'HUD hidden for both clips; level, actors and collision simulation retained.',
            'Actual Light quality preset; detailed studio stills are separate. No full-shadow claim for these clips.',
            'Player begins at the real campaign spawn; no visual actor relocation.',
            'Two 1/60 s simulation calls per 30 fps frame; playback 1x, audio absent.',
            'Frame export does not measure physical-device performance, balance or artistic quality.',
        ],
        'outputs': [],
    }
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'docs')))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with tempfile.TemporaryDirectory(prefix='royaumes-r5-motion-', dir='/tmp') as scratch:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(executable_path='/usr/bin/chromium',
                                             args=['--no-sandbox', '--enable-unsafe-swiftshader'])
                try:
                    for hero in HEROES:
                        context = browser.new_context(viewport={'width': WIDTH, 'height': HEIGHT}, device_scale_factor=1)
                        try:
                            page = context.new_page()
                            page.add_init_script('requestAnimationFrame=()=>0')
                            errors = []
                            page.on('pageerror', lambda error: errors.append(str(error)))
                            page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
                            page.goto(f'http://127.0.0.1:{server.server_port}/index.html?hero={hero}')
                            page.wait_for_function('avatarRuntime.status==="ready"&&!document.querySelector("#start").disabled', polling=50)
                            assert page.evaluate('ROYAUMES_VERSION') == version
                            assert page.evaluate('hero') == hero
                            page.select_option('#quality', 'light')
                            assert page.evaluate('''()=>{const a=avatarRuntime.heroes[hero];return a.motionCalibration&&a.ownedMaterials.filter(m=>m.isMeshStandardMaterial).every(m=>m.map?.image?.width>=512&&m.normalMap?.image?.width>=256&&m.roughnessMap?.image?.width>=256);}'''), 'Authored PBR maps must decode before capturing'
                            page.click('#start')
                            page.wait_for_function('state==="playing"', polling=50)
                            page.add_style_tag(content=HIDE)
                            start = page.evaluate(SETUP)
                            sim_start = page.evaluate('t')
                            folder = Path(scratch) / hero
                            folder.mkdir()
                            combos, phases = set(), set()
                            end = None
                            for index in range(FPS * SECONDS):
                                end = page.evaluate(STEP, {'index': index, 'input': controls(index / FPS)})
                                assert end['state'] == 'playing', end
                                combos.add(end['combo'])
                                if end['attack']:
                                    phases.add(end['attack'])
                                page.screenshot(path=str(folder / f'frame-{index:04d}.png'))
                                if index % 30 == 0:
                                    print(hero, index, '/', FPS * SECONDS, flush=True)
                            calls = page.evaluate('proofCalls')
                            assert calls == FPS * SECONDS * 2, calls
                            assert end['shots'] > start['shots'], f'{hero}: authored attack release never occurred'
                            assert abs(end['x'] - start['x']) + abs(end['z'] - start['z']) > .5, f'{hero}: no actual traversal'
                            target = OUT / f'r5-{hero}-motion.mp4'
                            record = encode(folder, target)
                            record.update({'hero': hero, 'version': version, 'html_sha256': digest(ROOT / 'docs/index.html'),
                                           'model_sha256': digest(ROOT / f'docs/assets/characters/{hero}.glb'),
                                           'frames': FPS * SECONDS, 'simulation_calls': calls,
                                           'simulation_seconds': page.evaluate('t') - sim_start,
                                           'camera': 'ordinary desktop gameplay', 'hud_hidden': True, 'quality': 'light',
                                           'combos_seen': sorted(combos), 'attack_kinds_seen': sorted(phases),
                                           'start': start, 'end': end})
                            report['outputs'].append(record)
                            assert not errors, errors
                        finally:
                            context.close()
                finally:
                    browser.close()
    finally:
        server.shutdown()
        server.server_close()
    target = ROOT / 'design/CAPTURES-MOUVEMENT-1.5.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Recorded', target.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
