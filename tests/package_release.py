"""Current assets, autonomous historical build and original archives must survive packaging."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];version=(ROOT/'VERSION').read_text().strip()
old=json.loads((ROOT/'historique/INVENTAIRE.json').read_text())
for entry in old:
 if entry['file']=='historique/README.md' or f'v{version}' in entry['file'] or f'-{version}.zip' in entry['file']:continue
 assert hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest()==entry['sha256'],entry['file']
subprocess.run(['python',str(ROOT/'scripts/package_release.py')],check=True)
path=ROOT/f'historique/livraisons-zip/royaumes-eclipse-{version}.zip';first=hashlib.sha256(path.read_bytes()).hexdigest()
subprocess.run(['python',str(ROOT/'scripts/package_release.py')],check=True)
assert hashlib.sha256(path.read_bytes()).hexdigest()==first,'Same checkout must yield identical ZIP bytes'
with zipfile.ZipFile(path) as z:
 for model in (ROOT/'assets/characters').glob('*.glb'):assert z.read('docs/assets/characters/'+model.name)==model.read_bytes()
 if (ROOT/'assets/source/lame-reference.blend').exists():
  for name in ['assets/source/lame-reference.blend','src/input-settings.js','src/character-review.html','design/personnages/lame-eclipse/recherche-01.png']:assert name in z.namelist(),name
 assert 'src/local-party.js' in z.namelist() and 'src/journey.js' in z.namelist() and 'historique/cathedrale-v0.15.html' in z.namelist()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();errors=[];requests=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:requests.append(r.url));p.set_content('<script>requestAnimationFrame=()=>0</script>'+(ROOT/f'historique/royaumes-v{version}.html').read_text());p.wait_for_function('avatarRuntime.status==="ready"',polling=50);p.evaluate('ensureHeroModel("eclipse")');assert p.evaluate('Object.keys(ROYAUMES_CHARACTER_DATA).length')==11;assert not [r for r in requests if '.glb' in r],requests;assert not errors,errors;b.close()
print('PASS: original historical files unchanged; deterministic ZIP includes all current models and old HTMLs; standalone snapshot loads secret model without any model request.')
