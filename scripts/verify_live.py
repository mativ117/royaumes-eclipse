"""Verify the public Pages build and downloadable package against this checkout."""
from pathlib import Path
from urllib.request import Request,urlopen
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
version=(ROOT/'VERSION').read_text().strip();base='https://mativ117.github.io/royaumes-eclipse/'
def get(url):
 with urlopen(Request(url,headers={'Cache-Control':'no-cache'}),timeout=30) as r:return r.read()
def digest(data):return hashlib.sha256(data).hexdigest()
manifest=json.loads((ROOT/'docs/version.json').read_text())
for attempt in range(30):
 try:
  remote=json.loads(get(base+'docs/version.json?v='+version+'&t='+str(int(time.time()))))
  if remote==manifest:break
 except Exception as e:print('Pages not ready:',str(e)[:120],flush=True)
 if attempt==29:raise SystemExit('Pages did not serve the expected version')
 print('Waiting for Pages',attempt+1,flush=True);time.sleep(10)
html=get(base+'docs/index.html?v='+version);assert html==(ROOT/'docs/index.html').read_bytes(),'Public HTML differs'
for name,expected in manifest['models'].items():assert digest(get(base+'docs/assets/characters/'+name+'?v='+version))==expected,name
for name in [f'previews/r3-{tag}.jpg' for tag in ['selection','lame-atelier','atrium','archives','forge','jardin','convoi']]+['ambre-obsidienne.html','previews/r2-chronicle.jpg','atelier-lame.html','assets/concepts/lame-01.png']+[f'previews/{tag}-chapter-{n}.jpg' for tag in ['r1','r2'] for n in [1,2,3]]:
 assert get(base+'docs/'+name+'?v='+version)==(ROOT/'docs'/name).read_bytes(),name
archive=f'historique/livraisons-zip/royaumes-eclipse-{version}.zip';package=get('https://raw.githubusercontent.com/mativ117/royaumes-eclipse/main/'+archive);assert package==(ROOT/archive).read_bytes(),'Public ZIP differs'
proof={'version':version,'html_sha256':digest(html),'verified_models':len(manifest['models']),'zip_bytes':len(package),'zip_sha256':digest(package),'comparison_verified':True}
Path('/tmp/royaumes-live-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2));print('PASS: public HTML, model hashes, comparison and complete ZIP match this checkout.')
