"""Connected-route reachability, gates, checkpoints, AI and both hero victories."""
from pathlib import Path
from playwright.sync_api import sync_playwright
html=(Path(__file__).resolve().parents[1]/'docs/index.html').read_text()
nav='''function route(start,goal){const queue=[start],seen=new Map([[start.join(','),null]]);let end=null;for(let i=0;i<queue.length;i++){const [x,z]=queue[i];if(x===goal[0]&&z===goal[1]){end=[x,z];break;}for(const [dx,dz]of[[1,0],[-1,0],[0,1],[0,-1]]){const a=x+dx,b=z+dz,key=a+','+b;if(a<-30||a>30||b<-113||b>30||seen.has(key)||blocked(a,b))continue;seen.set(key,[x,z]);queue.push([a,b]);}}if(!end)return null;const path=[];while(end){path.unshift(end);end=seen.get(end.join(','));}return path;}
function walk(path){for(const [x,z]of path.slice(1)){let n=0;while(Math.hypot(x-p.x,z-p.z)>.3&&n++<100){const d=Math.hypot(x-p.x,z-p.z);joy.x=(x-p.x)/d;joy.y=(z-p.z)/d;update(1/60);}if(n>=100)throw Error('Stuck at '+x+','+z+' from '+p.x+','+p.z);}joy.x=joy.y=0;for(let i=0;i<20;i++)update(1/60);}
'''
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':960,'height':650});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.click('#start');run=page.evaluate
 page.evaluate('(code)=>{(0,eval)(code)}',nav+'soundOn=false;p.inv=999;')
 assert run('route([0,23],[9,7])!==null')
 assert run('route([0,23],[20,-20])===null')
 assert run('blocked(0,-15)') # Real central void, not a shortcut.
 # A full dash cannot tunnel through a closed pact gate.
 z=run('p.x=18;p.z=-3;moveEntity(p,0,-5);p.z');assert z>-5
 run('p.x=9;p.z=7;p.vx=p.vz=0;update(1/60)');page.keyboard.press('f');page.click('#sealPact')
 assert run('boon')=='haste'
 assert run('route([-20,-1],[-20,-32])!==null')
 assert run('route([18,-1],[18,-34])!==null')
 assert run('route([0,-38],[0,-85])===null')
 for x,z in [(-9,-62),(9,-55),(-23,-29),(-25,-27)]:
  assert run(f'route([0,-38],[{x},{z}])!==null'),(x,z)
 # Actual movement follows a route through the west bridge into the first refuge.
 run('p.x=-20;p.z=-1;p.vx=p.vz=0;p.inv=999;walk(route([-20,-1],[0,-38]));')
 assert run('campaign.checkpoint.id')=='crossing'
 assert run('p.z')<-32 and run('campaign.zone')=='Croisée des pèlerins'
 # Enemies do not attack across the entire map. The oracle has an announced attack.
 oracle=run('var oracle=enemies.find(e=>e.type==="oracle");p.x=oracle.x+2;p.z=oracle.z;p.vx=p.vz=0;oracle.mode="idle";oracle.timer=0;updateOracle(oracle,1/60);({mode:oracle.mode,delay:hazards[hazards.length-1].delay})')
 assert oracle['mode']=='windup' and oracle['delay']>1
 # Pickup after a refuge rolls back on death; earlier kills at a refuge stay dead.
 run('p.x=-9;p.z=-62;update(1/60)');assert run('campaign.keys.size')==1
 run('p.inv=0;p.shield=0;p.leap=0;p.dashT=0;hurt(999)');page.click('#resume')
 assert run('campaign.keys.size')==0 and run('campaign.checkpoint.id')=='crossing'
 assert abs(run('p.z')+36)<1
 # Get both seals, activate the next refuge, then enter the boss courtyard.
 run('p.inv=999;p.x=-9;p.z=-62;update(1/60);p.x=9;p.z=-55;update(1/60)')
 assert run('campaign.keys.size')==2
 assert run('route([0,-65],[0,-85])!==null')
 run('p.x=0;p.z=-65;update(1/60)');assert run('campaign.checkpoint.id')=='threshold'
 run('p.x=0;p.z=-80;p.inv=999;update(1/60)');assert run('campaign.bossAwake')
 assert run('route([0,-80],[0,-65])===null')
 # Bell cancels danger and can only be rung once.
 run('p.x=9;p.z=-82;p.vx=p.vz=0;boss.mode="windup";boss.timer=99;addHazard(9,-82,3,1);updateInteraction()');page.keyboard.press('f')
 assert run('bell.used') and run('boss.mode')=='recover'
 # Ranged victory in global coordinates.
 run('p.x=0;p.z=-83;p.vx=p.vz=0;p.inv=999;boss.mode="recover";boss.timer=99;clearHazards();aim=targetAim=0;mouseAim=false;shooting=true;for(let i=0;i<700;i++)update(1/60);shooting=false')
 assert run('boss.dead')
 run('p.x=0;p.z=-107;update(1/60)');assert run('state')=='won'
 page.click('#back');page.click('[data-hero=voltigeur]');page.click('#start')
 # Melee still respects cover; leap and damage work in the new courtyard.
 run('soundOn=false;chooseBoon("vigor");campaign.keys=new Set(["west","east"]);p.x=0;p.z=-80;p.inv=999;update(1/60);p.z=-90.5;p.vx=p.vz=0;boss.mode="recover";boss.timer=99;clearHazards();aim=targetAim=0;mouseAim=false;shooting=true;for(let i=0;i<700;i++)update(1/60);shooting=false')
 assert run('boss.dead')
 run('p.x=0;p.z=-107;update(1/60)');assert run('state')=='won'
 assert not errors,errors
 b.close();print('PASS: connected west/east paths, void and gate collisions, real walking, refuges, rollback, announced oracle, seals, courtyard lock, bell, ranged and melee victories. No JS errors.')
