"""Build the static GitHub Pages site without downloading anything."""
from pathlib import Path
import hashlib
import json
import base64

ROOT = Path(__file__).resolve().parents[1]
version = (ROOT / 'VERSION').read_text().strip()
template = (ROOT / 'src/template.html').read_text()
engine = (ROOT / 'vendor/three.min.js').read_text() + '\n' + (ROOT / 'vendor/three-addons.js').read_text()
models = 'const ROYAUMES_VERSION='+json.dumps(version)+';\nconst ROYAUMES_CHARACTER_DATA=' + json.dumps({name:base64.b64encode((ROOT/'assets/characters'/f'{name}.glb').read_bytes()).decode() for name in ['rempart','voltigeur']},separators=(',',':')) + ';\n'
game = (ROOT/'src/story-audio.js').read_text() + '\n' + (ROOT/'src/presentation.js').read_text() + '\n' + (ROOT/'src/visual-world.js').read_text() + '\n' + (ROOT/'src/roster.js').read_text() + '\n' + (ROOT/'src/dynamics.js').read_text() + '\n' + (ROOT/'src/class-abilities.js').read_text() + '\n' + (ROOT/'src/journey.js').read_text() + '\n' + (ROOT/'src/journey-art.js').read_text() + '\n' + (ROOT/'src/local-party.js').read_text() + '\n' + (ROOT/'src/complete-ui.js').read_text() + '\n' + models + (ROOT/'src/avatar-kinematics.js').read_text() + '\n' + (ROOT/'src/authored-avatar.js').read_text() + '\n' + (ROOT/'src/sanctuary.js').read_text() + '\n' + (ROOT / 'src/combat-motion.js').read_text() + '\n' + (ROOT / 'src/staging.js').read_text() + '\n' + (ROOT / 'src/art-direction.js').read_text() + '\n' + (ROOT / 'src/game.js').read_text()
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
(output / 'index.html').write_text(html)
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
    'models': {f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'assets/characters').glob('*.glb'))},
    'source_sha256': hashlib.sha256((template + engine + art + campaign + game).encode()).hexdigest(),
}, indent=2) + '\n')
print(f'Built version {version} in docs/')
