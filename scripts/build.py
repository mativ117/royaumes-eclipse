"""Build the static GitHub Pages site without downloading anything."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
version = (ROOT / 'VERSION').read_text().strip()
template = (ROOT / 'src/template.html').read_text()
engine = (ROOT / 'vendor/three.min.js').read_text()
game = (ROOT / 'src/game.js').read_text()
art = (ROOT / 'src/world.js').read_text()
campaign = (ROOT / 'src/campaign.js').read_text()
assert template.count('<!-- THREE_ENGINE -->') == 1
assert template.count('<!-- GAME_SCRIPT -->') == 1
assert f'Version {version}' in template
html = template.replace('<!-- THREE_ENGINE -->', '<script>' + engine + '</script>')
html = html.replace('<!-- GAME_SCRIPT -->', '<script>' + art + '</script><script>' + campaign + '</script><script>' + game + '</script>')
output = ROOT / 'docs'
output.mkdir(exist_ok=True)
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
(output / 'version.json').write_text(json.dumps({
    'version': version,
    'source_sha256': hashlib.sha256((template + engine + art + campaign + game).encode()).hexdigest(),
}, indent=2) + '\n')
print(f'Built version {version} in docs/')
