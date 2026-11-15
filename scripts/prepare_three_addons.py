"""Bundle pinned MIT Three.js r160 add-ons against the existing global engine."""
from pathlib import Path
import re,hashlib,json
root=Path(__file__).resolve().parents[1]
imports=set();sources=[];manifest=[]
for name in ['BufferGeometryUtils.js','GLTFLoader.js','Reflector.js']:
 p=root/'vendor/three-r160-upstream'/name;s=p.read_text()
 imports.update(x.strip() for x in re.search(r"import\s*\{([^}]+)\}\s*from 'three';",s,re.S).group(1).split(',') if x.strip())
 s=re.sub(r"import\s*\{[^}]+\}\s*from [^;]+;",'',s,flags=re.S)
 s=re.sub(r'export\s*\{[^}]+\};?','',s,flags=re.S)
 s=re.sub(r'\bexport\s+(?=(?:function|class|const|let)\b)','',s)
 sources.append(s);manifest.append({'file':name,'version':'r160','source':'https://github.com/mrdoob/three.js/blob/r160/examples/jsm/'+('utils/' if name.startswith('Buffer') else 'loaders/' if name.startswith('GLTF') else 'objects/')+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'license':'MIT; see vendor/THREE-LICENSE.txt'})
result='/* Three.js r160 add-ons, MIT; original sources retained beside this bundle. */\n(function(){\nconst {'+','.join(sorted(imports))+'}=THREE;\n'+'\n'.join(sources)+'\nwindow.RoyaumesGLTFLoader=GLTFLoader;window.RoyaumesReflector=Reflector;\n})();\n'
(root/'vendor/three-addons.js').write_text(result)
(root/'vendor/three-r160-upstream/PROVENANCE.json').write_text(json.dumps(manifest,indent=2)+'\n')
