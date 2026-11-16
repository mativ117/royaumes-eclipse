"""Package a playable release and preserve a fully self-contained historical snapshot."""
from pathlib import Path
import base64,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
version=(ROOT/'VERSION').read_text().strip()
html=(ROOT/'docs/index.html').read_text()
models={f.stem:base64.b64encode(f.read_bytes()).decode() for f in sorted((ROOT/'assets/characters').glob('*.glb'))}
start=html.index('const ROYAUMES_CHARACTER_DATA=')
end=html.index(';\n',start)+1
snapshot=html[:start]+'const ROYAUMES_CHARACTER_DATA='+json.dumps(models,separators=(',',':'))+';'+html[end:]
icon=base64.b64encode((ROOT/'docs/favicon.svg').read_bytes()).decode()
snapshot=snapshot.replace('href="./favicon.svg"','href="data:image/svg+xml;base64,'+icon+'"')
history=ROOT/'historique';history.mkdir(exist_ok=True)
(history/f'royaumes-v{version}.html').write_text(snapshot)
output=history/'livraisons-zip'/f'royaumes-eclipse-{version}.zip';output.parent.mkdir(exist_ok=True)
files=[]
for folder in ['src','docs','assets','vendor','scripts','tests','design']:
 files.extend(f for f in (ROOT/folder).rglob('*') if f.is_file() and '__pycache__' not in f.parts)
files.extend(f for f in history.rglob('*') if f.is_file() and f.suffix!='.zip' and f.name!='INVENTAIRE.json')
for name in ['README.md','VERSION','index.html','cathedrale-v03.html','.nojekyll','.gitignore']:
 if (ROOT/name).exists():files.append(ROOT/name)
def write(z,name,data):
 info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(output,'w') as z:
 for f in sorted(set(files)):write(z,f.relative_to(ROOT).as_posix(),f.read_bytes())
 included=[{'file':f.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(set(files)) if history in f.parents]
 write(z,'historique/INVENTAIRE-PAQUET.json',(json.dumps(included,indent=2)+'\n').encode())
inventory=[{'file':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(history.rglob('*')) if f.is_file() and f.name!='INVENTAIRE.json']
(history/'INVENTAIRE.json').write_text(json.dumps(inventory,indent=2,ensure_ascii=False)+'\n')
print(f'Packaged {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes); {len(models)} embedded historical models.')
