"""Current editable package, autonomous snapshot and untouched older archives."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
from playwright.sync_api import sync_playwright
import sys as _check_sys
from pathlib import Path as _CheckPath
_check_sys.path.insert(0,str(_CheckPath(__file__).resolve().parents[1]/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()
ROOT=Path(__file__).resolve().parents[1];version=(ROOT/'VERSION').read_text().strip()
old=json.loads((ROOT/'historique/INVENTAIRE.json').read_text())
for entry in old:
 if entry['file']=='historique/README.md' or f'v{version}' in entry['file'] or f'-{version}' in entry['file']:continue
 assert hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest()==entry['sha256'],entry['file']
subprocess.run(['python',str(ROOT/'scripts/package_release.py')],check=True)
path=ROOT/f'historique/livraisons-zip/royaumes-eclipse-{version}-projet.zip';first=hashlib.sha256(path.read_bytes()).hexdigest()
subprocess.run(['python',str(ROOT/'scripts/package_release.py')],check=True)
assert hashlib.sha256(path.read_bytes()).hexdigest()==first,'Same checkout must yield identical ZIP bytes'
with zipfile.ZipFile(path) as z:
 assert path.stat().st_size<=95_000_000,'Keep headroom below GitHub per-file limit'
 assert not any(name.startswith('historique/') for name in z.namelist()),'History remains in repository, without archive nesting'
 assert not any(name.endswith(('.blend1','.blend2','.pyc')) for name in z.namelist()),'No editor backup/cache files'
 manifest=json.loads(z.read('PAQUET.json'));assert manifest['version']==version
 assert manifest['history']=='https://github.com/mativ117/royaumes-eclipse/archive/refs/heads/main.zip'
 assert {row['file'] for row in manifest['files']}==set(z.namelist())-{'PAQUET.json'}
 for row in manifest['files']:assert hashlib.sha256(z.read(row['file'])).hexdigest()==row['sha256'],row['file']
 for model in (ROOT/'assets/characters').glob('*.glb'):assert z.read('docs/assets/characters/'+model.name)==model.read_bytes()
 if (ROOT/'assets/source/lame-reference.blend').exists():
  for name in ['assets/source/lame-reference.blend','src/input-settings.js','src/character-review.html','design/personnages/lame-eclipse/recherche-01.png']:assert name in z.namelist(),name
 for name in ['src/local-party.js','src/journey.js','src/lan-peer.js','src/tactical-bot.js','assets/source/roster/rempart.blend']:
  assert name in z.namelist(),name
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();errors=[];requests=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:requests.append(r.url));p.set_content('<script>requestAnimationFrame=()=>0</script>'+(ROOT/f'historique/royaumes-v{version}.html').read_text());p.wait_for_function('avatarRuntime.status==="ready"',polling=50);p.evaluate('ensureHeroModel("eclipse")');assert p.evaluate('Object.keys(ROYAUMES_CHARACTER_DATA).length')==11;assert not [r for r in requests if '.glb' in r],requests;assert not errors,errors;b.close()
print('PASS: old archives unchanged; deterministic current-project ZIP includes editable sources, all models and a checked manifest below GitHub size limit; history stays in repository; standalone loads secret model without model requests.')
