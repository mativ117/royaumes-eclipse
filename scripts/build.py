"""Build the static GitHub Pages site without downloading anything."""
from pathlib import Path
import hashlib
import json
import base64
from html_security import secure_html

ROOT = Path(__file__).resolve().parents[1]
version = (ROOT / 'VERSION').read_text().strip()
template = (ROOT / 'src/template.html').read_text()
engine = (ROOT / 'vendor/three.min.js').read_text() + '\n' + (ROOT / 'vendor/three-addons.js').read_text()
models = 'const ROYAUMES_VERSION='+json.dumps(version)+';\nconst ROYAUMES_CHARACTER_DATA=' + json.dumps({},separators=(',',':')) + ';\n'
creature_source=ROOT/'assets/creatures/obsidian-warden.glb'
models+='const ROYAUMES_ENEMY_DIRECTION_DATA={};\n'
models+='const ROYAUMES_CREATURE_DATA='+json.dumps(base64.b64encode(creature_source.read_bytes()).decode())+';\n'
surface_data={role:{field:'data:image/jpeg;base64,'+base64.b64encode((ROOT/'assets/materials'/f'{role}-{field}.jpg').read_bytes()).decode() for field in ['map','normal','rough']} for role in ['stone','masonry']}
material_data='const ROYAUMES_SURFACES='+json.dumps(surface_data,separators=(',',':'))+';\n'
game = '\n'.join((ROOT/'src'/name).read_text() for name in ['combat-feedback-v17.js','camera-direction-v16.js','environment-direction-v16.js','encounter-presentation-v16.js','enemy-direction-v16.js','ground-layout.js','combat-control.js','contact-shadows.js','lan-protocol.js','lan-peer.js','lan-game.js','session-ui.js','tactical-bot.js'])+'\n'+(ROOT/'src/blade-contact.js').read_text()+'\n'+(ROOT/'src/predator-combat.js').read_text()+'\n'+(ROOT/'src/modal-focus.js').read_text()+'\n'+(ROOT/'src/creature-reference.js').read_text()+'\n'+(ROOT/'src/hero-preview.js').read_text()+'\n'+material_data + (ROOT/'src/material-surfaces.js').read_text()+'\n'+ (ROOT/'src/environment-finish.js').read_text()+'\n'+ (ROOT/'src/input-settings.js').read_text() + '\n' + (ROOT/'src/story-audio.js').read_text() + '\n' + (ROOT/'src/presentation.js').read_text() + '\n' + (ROOT/'src/visual-world.js').read_text() + '\n' + (ROOT/'src/roster.js').read_text() + '\n' + (ROOT/'src/dynamics.js').read_text() + '\n' + (ROOT/'src/class-abilities.js').read_text() + '\n' + (ROOT/'src/journey.js').read_text() + '\n' + (ROOT/'src/journey-art.js').read_text() + '\n' + (ROOT/'src/session-modes.js').read_text() + '\n' + (ROOT/'src/complete-ui.js').read_text() + '\n' + models + (ROOT/'src/lame-motion.js').read_text() + '\n' + (ROOT/'src/avatar-kinematics.js').read_text() + '\n' + (ROOT/'src/authored-avatar.js').read_text() + '\n' + (ROOT/'src/sanctuary.js').read_text() + '\n' + (ROOT / 'src/combat-motion.js').read_text() + '\n' + (ROOT / 'src/staging.js').read_text() + '\n' + (ROOT / 'src/art-direction.js').read_text() + '\n' + (ROOT / 'src/game.js').read_text()
art = (ROOT / 'src/world.js').read_text()
campaign = (ROOT / 'src/expedition.js').read_text() + '\n' + (ROOT / 'src/readability.js').read_text() + '\n' + (ROOT / 'src/campaign.js').read_text()
assert template.count('<!-- THREE_ENGINE -->') == 1
assert template.count('<!-- GAME_SCRIPT -->') == 1
assert f'Version {version}' in template
html = template.replace('<!-- THREE_ENGINE -->', '<script>' + engine + '</script>')
html = html.replace('<!-- GAME_SCRIPT -->', '<script>' + art + '</script><script>' + campaign + '</script><script>' + game + '</script>')
output = ROOT / 'docs'
output.mkdir(exist_ok=True)
import shutil
model_output=output/'assets/characters'
model_output.mkdir(parents=True,exist_ok=True)
for source in (ROOT/'assets/characters').glob('*.glb'):shutil.copyfile(source,model_output/source.name)
html=secure_html(html)
(output / 'index.html').write_text(html)
(output/'assets/creatures').mkdir(exist_ok=True)
for source in (ROOT/'assets/creatures').glob('*.glb'):shutil.copyfile(source,output/'assets/creatures'/source.name)
# Preserve the already shared address while maintaining one canonical game file.
(output / 'cathedrale-v03.html').write_text('''<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Les Royaumes de l’Éclipse</title>
<meta http-equiv="refresh" content="0;url=./index.html">
<link rel="canonical" href="https://mativ117.github.io/royaumes-eclipse/">
<style>body{background:#140f19;color:#ffe3ad;font:18px system-ui;padding:32px}a{color:#ffc17b}</style>
</head><body><p>Le jeu se trouve désormais à son adresse principale.</p>
<a href="./index.html">Jouer aux Royaumes de l’Éclipse</a>
<script>location.replace('./index.html'+location.search+location.hash);</script>
</body></html>
''')
(output / '.nojekyll').write_text('')
(output/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#16131e"/><circle cx="32" cy="32" r="20" fill="none" stroke="#dfb477" stroke-width="3"/><circle cx="37" cy="28" r="17" fill="#16131e"/></svg>')
(output / 'version.json').write_text(json.dumps({
    'version': version,
    'modes': ['solo','duel','lan'],
    'network': {'transport':'WebRTC','pairing':'manual-files','players':2,'external_signaling':False,'api_calls':False},
    'security': {'scripts':'CSP hashes','referrer':'no-referrer'},
    'creatures': {f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'assets/creatures').glob('*.glb'))},
    'models': {f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'assets/characters').glob('*.glb'))},
    'source_sha256': hashlib.sha256((template + engine + art + campaign + game).encode()).hexdigest(),
}, indent=2) + '\n')
print(f'Built version {version} in docs/')

# Dedicated live 3D review for the first approved hero.
hero_meta=(ROOT/'src/roster.js').read_text().split('function isMeleeHero')[0]
review=(ROOT/"src/character-review.html").read_text().replace("<!-- THREE_ENGINE -->","<script>"+engine+"</script>").replace("__VERSION__",version).replace('<!-- HERO_META -->','<script>'+hero_meta+'</script>').replace('<!-- MATERIAL_DATA -->','<script>'+material_data+(ROOT/'src/material-surfaces.js').read_text()+'</script>')
(output/"atelier-lame.html").write_text(secure_html(review))
(output/"gestes-et-creatures.html").write_text(secure_html((ROOT/'src/quality-review.html').read_text().replace('__VERSION__',version)))
(output/"assets/concepts").mkdir(exist_ok=True)
shutil.copyfile(ROOT/"design/personnages/lame-eclipse/recherche-01.png",output/"assets/concepts/lame-01.png")
