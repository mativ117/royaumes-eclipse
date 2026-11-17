"""Comparable in-engine screenshots; no generated concept images."""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'docs/previews';out.mkdir(exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
 for tag,path in [('r1',ROOT/'historique/royaumes-v1.0-rc1.html'),('r2',ROOT/'docs/index.html')]:
  if len(sys.argv)>1 and tag not in sys.argv[1:] and not(tag=='r2' and '--chronicle' in sys.argv):continue
  page=b.new_page(viewport={'width':1000,'height':700});page.set_content('<script>requestAnimationFrame=()=>0</script>'+path.read_text());page.wait_for_function('avatarRuntime.status==="ready"',polling=50)
  for level,z in ([(3,-39)] if '--chronicle' in sys.argv else [(1,23),(2,-46),(3,-39)]):
   page.evaluate(f'''soundOn=false;hero='rempart';start();{'enterChapter('+str(level)+',3);' if level>1 else ''}resetHeroAt(0,{z});p.inv=999;for(let i=0;i<15;i++)update(1/60);camera.position.set(0,6.7,p.z+10.8);camera.lookAt(0,1.6,p.z-5);updateJourneyScenery(.1);updateSanctuary(.1);$('#zoneBanner').hidden=true;$('#notice').hidden=true;''')
   page.evaluate('updateVisualWorld();renderPresentation()' if tag=='r2' else 'renderer.render(scene,camera)')
   if '--chronicle' not in sys.argv:page.screenshot(path=str(out/f'{tag}-chapter-{level}.jpg'),type='jpeg',quality=90)
   print(tag,level,flush=True)
  if tag=='r2':
   page.evaluate('openChronicle()');page.screenshot(path=str(out/'r2-chronicle.jpg'),type='jpeg',quality=90)
  page.close()
 b.close()
