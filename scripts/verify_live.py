"""Verify the public Pages build and current-project package against this checkout."""
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import json
import time

from package_release import release_path

ROOT = Path(__file__).resolve().parents[1]
version = (ROOT / 'VERSION').read_text().strip()
base = 'https://mativ117.github.io/royaumes-eclipse/'


def get(url):
    with urlopen(Request(url, headers={'Cache-Control': 'no-cache'}), timeout=30) as r:
        return r.read()


def digest(data):
    return hashlib.sha256(data).hexdigest()


manifest = json.loads((ROOT / 'docs/version.json').read_text())
for attempt in range(30):
    try:
        remote = json.loads(get(base + 'docs/version.json?v=' + version + '&t=' + str(int(time.time()))))
        if remote == manifest:
            break
    except Exception as e:
        print('Pages not ready:', str(e)[:120], flush=True)
    if attempt == 29:
        raise SystemExit('Pages did not serve the expected version')
    print('Waiting for Pages', attempt + 1, flush=True)
    time.sleep(10)

html = get(base + 'docs/index.html?v=' + version)
assert html == (ROOT / 'docs/index.html').read_bytes(), 'Public HTML differs'
assert get(base + 'index.html?v=' + version) == (ROOT / 'index.html').read_bytes(), 'Root redirect differs'
for group, directory in [('models', 'characters'), ('creatures', 'creatures')]:
    for name, expected in manifest.get(group, {}).items():
        assert digest(get(base + 'docs/assets/' + directory + '/' + name + '?v=' + version)) == expected, name
assert len(manifest['models']) == 11, 'All ordinary and secret models must be published'

# Verify current review pages plus actual media. r1-r4 remain dated historical
# comparisons; their presence is never evidence of new 1.5 movement quality.
media = sorted(f.relative_to(ROOT / 'docs').as_posix()
               for f in (ROOT / 'docs/previews').glob('r6-*') if f.is_file())
review_files = ['gestes-et-creatures.html', 'atelier-lame.html', 'ambre-obsidienne.html',
                'assets/concepts/lame-01.png']
for name in review_files + media:
    assert get(base + 'docs/' + name + '?v=' + version) == (ROOT / 'docs' / name).read_bytes(), name

archive = release_path(version)
relative = archive.relative_to(ROOT).as_posix()
package = get('https://raw.githubusercontent.com/mativ117/royaumes-eclipse/main/' + relative)
assert package == archive.read_bytes(), 'Public current-project ZIP differs'
assert len(package) <= 100_000_000, 'Package exceeds publication headroom'
proof = {
    'version': version,
    'html_sha256': digest(html),
    'verified_models': len(manifest['models']),
    'verified_creatures': len(manifest.get('creatures', {})),
    'modes': manifest.get('modes', []),
    'package_scope': 'Current playable and editable project; full history stays in repository',
    'package_file': relative,
    'zip_bytes': len(package),
    'zip_sha256': digest(package),
    'verified_review_files': review_files,
    'verified_1_6_media': media,
    'real_device_lan_validation': False,
}
Path('/tmp/royaumes-live-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps(proof, indent=2))
print('PASS: public HTML, all eleven model hashes, review pages and current-project ZIP match this checkout.')
