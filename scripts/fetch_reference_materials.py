"""Fetch two CC0 Poly Haven materials; runtime build uses the committed copies offline."""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image
import json,hashlib,io
out=Path(__file__).resolve().parents[1]/'assets/materials';out.mkdir(exist_ok=True);records=[]
def get(url):return urlopen(Request(url,headers={'User-Agent':'RoyaumesEclipse material pipeline'}),timeout=45).read()
for role,aid in [('stone','pavement_01'),('masonry','castle_wall_slates')]:
 files=json.loads(get('https://api.polyhaven.com/files/'+aid));info=json.loads(get('https://api.polyhaven.com/info/'+aid))
 for key,field in [('Diffuse','map'),('nor_gl','normal'),('Rough','rough')]:
  item=files[key]['1k']['jpg'];raw=get(item['url']);assert hashlib.md5(raw).hexdigest()==item['md5'], 'Downloaded source checksum mismatch';image=Image.open(io.BytesIO(raw)).convert('RGB');image.thumbnail((512,512),Image.Resampling.LANCZOS);path=out/(role+'-'+field+'.jpg');image.save(path,'JPEG',quality=91,optimize=True)
  records.append({'role':role,'field':field,'asset':aid,'author':info.get('authors'),'source':item['url'],'source_md5':hashlib.md5(raw).hexdigest(),'runtime':path.name,'runtime_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'runtime_size':[image.width,image.height]});print(path.name,path.stat().st_size,flush=True)
(out/'PROVENANCE.json').write_text(json.dumps({'provider':'Poly Haven','license':'CC0','license_url':'https://polyhaven.com/license','license_verified_url':'https://docs.polyhaven.com/en/faq','license_verified_date':'2026-11-17','assets':records},indent=2)+'\n')
