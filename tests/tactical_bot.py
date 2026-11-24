"""CPU-only tactical decisions from public perception, without Three or a network.

These scenarios isolate the planner. They do not prove match balance, enjoyable
combat, animation quality or phone performance; the real arena is tested apart.
"""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = r'''
const assert=require('assert');let networkCalls=0;const denyNetwork=()=>{networkCalls++;throw Error('A local bot cannot call a network API');};globalThis.fetch=denyNetwork;for(const name of ['XMLHttpRequest','WebSocket','RTCPeerConnection'])globalThis[name]=class{constructor(){denyNetwork();}};const {TacticalDuelBot}=require(process.argv[1]+'/src/tactical-bot.js');
const clone=o=>JSON.parse(JSON.stringify(o));
const observation=()=>({self:{id:'bot',heroId:'lame',x:0,z:0,vx:0,vz:0,aim:0,hp:125,max:125,shot:0,dash:0,power:0,shield:0,stagger:0,attack:null},target:{id:'human',heroId:'rempart',x:0,z:-2.2,vx:0,vz:0,aim:Math.PI,hp:150,max:150,visible:true,shield:0,attack:null},projectiles:[],obstacles:[],arenaBounds:{minX:-18,maxX:18,minZ:-36,maxZ:10}});
const advance=(bot,o,seconds,hz=60,hook=null)=>{let last;for(let i=0;i<Math.round(seconds*hz);i++){hook?.(o,i/hz);last=bot.update(o,1/hz);}return last;};
const firstReaction=[];
for(const difficulty of ['veteran','tactician'])for(const hz of [30,60,120]){
 const bot=new TacticalDuelBot({difficulty,seed:22}),o=observation();o.target.attack={phase:'windup'};let first=null;
 for(let i=0;i<hz;i++){const input=bot.update(o,1/hz);if((i+1)/hz<bot.profile.reaction-1e-8)assert(!input.dash&&!input.power&&!input.fire,'No reaction to an unperceived attack');if(input.dash&&first===null){first=(i+1)/hz;o.self.dash=1.35;}}
 assert(first!==null&&first>=bot.profile.reaction&&first<=bot.profile.reaction+.11,'Reaction is delayed but not unbounded');firstReaction.push({difficulty,hz,first});
}
// Known movement animation is not an input command: a future target's private
// cooldown fields and non-existent hidden coordinates cannot influence actions.
{
 const a=new TacticalDuelBot({seed:9}),b=new TacticalDuelBot({seed:9}),oa=observation(),ob=observation();
 oa.target.attack={phase:'recover'};ob.target.attack={phase:'recover',inputPressed:true,secretCooldown:0};ob.target.shot=999;ob.target.dash=999;ob.target.power=999;
 for(let i=0;i<180;i++)assert.deepStrictEqual(a.update(oa,1/60),b.update(ob,1/60),'Private target state must be ignored');
 const hidden=new TacticalDuelBot({seed:9}),oh=observation();oh.target={visible:false,get x(){throw Error('Hidden position read');},get attack(){throw Error('Hidden attack read');}};
 advance(hidden,oh,1);assert(!hidden.debug.seen&&hidden.debug.state==='search');
}
// Recovery is a visible tactical opening, distinct from a face-to-face windup.
{
 const bot=new TacticalDuelBot({difficulty:'tactician',seed:6}),o=observation();o.target.attack={phase:'recover'};
 const output=advance(bot,o,.4);assert(bot.debug.state==='punish'&&output.fire,'Exploit recovery only after perception');
 o.self.attack={phase:'windup'};const locked=advance(bot,o,.2);assert(bot.debug.state==='recover'&&Math.hypot(locked.x,locked.z)===0&&!locked.fire,'Full-body committed attack cannot moonwalk or restart');
 o.self.attack={phase:'recover'};o.self.shot=.5;const moving=advance(bot,o,.2);assert(Math.hypot(moving.x,moving.z)>0&&!moving.fire,'Recovery releases movement, not a free extra attack');
 o.self.attack=null;o.self.shot=0;o.target.shield=2;const shielded=advance(bot,o,.4);assert(!shielded.fire,'Do not feed a visible shield with perfect continuous hits');
}
// Visible incoming projectiles may be dodged; a sufficiently late fast shot
// reaches the body before the reaction budget. The planner does not slow time.
{
 const bot=new TacticalDuelBot({difficulty:'tactician',seed:11}),o=observation();o.target.z=-12;let first=null;
 for(let i=0;i<30;i++){const t=(i+1)/60;o.projectiles=[{x:0,z:-7+10*t,dx:0,dz:1,speed:10,hostile:true,enemy:false}];const input=bot.update(o,1/60);if(input.dash&&first===null){first=t;o.self.dash=1.35;}}
 assert(first>=.16&&first<.5,'A hostile player projectile is not mistaken for a friendly NPC projectile');
 const late=new TacticalDuelBot({difficulty:'tactician',seed:11}),quick=observation();quick.target.z=-15;let dodgeBeforeImpact=false;
 for(let i=0;i<30;i++){const t=(i+1)/120;quick.projectiles=[{x:0,z:-5+32*t,dx:0,dz:1,speed:32,hostile:true}];if(late.update(quick,1/120).dash&&t<5/32)dodgeBeforeImpact=true;}
 assert(!dodgeBeforeImpact,'No impossible instantaneous dodge of a close fast shot');
}
// Real own cooldowns/stagger veto controls; input objects remain untouched.
{
 const bot=new TacticalDuelBot({difficulty:'tactician',seed:11}),o=observation();o.target.attack={phase:'windup'};o.self.dash=2;o.self.power=4;o.self.shot=.9;const before=clone(o);
 for(let i=0;i<60;i++){const input=bot.update(o,1/60);assert(!input.dash&&!input.power&&!input.fire);}
 assert.deepStrictEqual(o,before,'The planner cannot grant HP, cooldowns or damage');
 o.self.stagger=.3;const output=advance(bot,o,.3);assert(!output.dash&&!output.power&&!output.fire&&Math.hypot(output.x,output.z)===0);
}
// A target hidden behind a wall is not acquired through geometry. An enemy
// that was seen then moves out of view is investigated only at the remembered point.
{
 const bot=new TacticalDuelBot({difficulty:'tactician',seed:24}),o=observation();o.obstacles=[{x:0,z:-1.1,w:2,d:.5}];
 for(let i=0;i<60;i++){const input=bot.update(o,1/60);assert(!input.fire&&!input.dash&&!input.power);}
 assert(!bot.debug.seen&&bot.lastSeen===null,'Wall is a hard perception veto');
 const memory=new TacticalDuelBot({difficulty:'tactician',seed:24}),m=observation();advance(memory,m,.4);const point=clone(memory.lastSeen);m.target.visible=false;m.target.x=14;m.target.z=5;m.target.attack={phase:'windup'};advance(memory,m,.4);
 assert(memory.debug.memory&&!memory.debug.seen&&memory.debug.state==='investigate');assert(memory.plan.aimTarget.x===point.x&&memory.plan.aimTarget.z===point.z,'Investigation must not follow hidden live coordinates');
 advance(memory,m,1.6);assert(memory.debug.state==='search'&&!memory.debug.memory,'Memory expires instead of becoming wallhacks');
}
// Navigation goes around a pillar with body clearance rather than repeatedly
// issuing the same blocked straight-line movement. Low-health ranged actors seek cover.
const navigation={};
{
 const bot=new TacticalDuelBot({difficulty:'tactician',seed:7}),o=observation();o.self.z=2;o.target.z=-8;o.obstacles=[{x:0,z:-2,w:2.5,d:2.5}];let travelled=0,largestX=0;
 for(let i=0;i<360;i++){const input=bot.update(o,1/60),next={x:o.self.x+input.x*3/60,z:o.self.z+input.z*3/60};assert(!bot.blocked(next,bot.geometry(o.obstacles),.45),'Bot movement must respect a real body radius');travelled+=Math.hypot(next.x-o.self.x,next.z-o.self.z);o.self.x=next.x;o.self.z=next.z;largestX=Math.max(largestX,Math.abs(next.x));}
 assert(travelled>5&&largestX>1.8&&o.self.z<-3,'Pillar is actually passed, not just a nonzero steering vector');navigation.travelled=travelled;navigation.largestX=largestX;
 const cover=new TacticalDuelBot({difficulty:'tactician',seed:7}),c=observation();c.self.heroId='rempart';c.self.x=-4;c.self.hp=30;c.target.z=-8;c.obstacles=[{x:1,z:-4,w:2,d:2}];advance(cover,c,.4);assert(cover.debug.state==='cover'&&cover.coverGoal&&!cover.clear(c.target,cover.coverGoal,cover.geometry(c.obstacles),.05),'Low-health retreat must select an actual occluding cover point');
}
// The planner adapts the engagement range to the actual exported blade, not
// a long-sword assumption imposed on a short dagger. Travelling without firing
// turns the body towards movement so the rig can use its real forward stride.
{
 const short=new TacticalDuelBot({difficulty:'tactician',seed:6}),o=observation();o.self.attackReach=1.35;o.target.attack={phase:'recover'};
 assert(!advance(short,o,.4).fire,'A short blade must approach instead of swinging from a long-sword distance');
 o.target.z=-1.1;assert(advance(short,o,.4).fire,'The same blade can punish inside its own reach');
 const travel=new TacticalDuelBot({difficulty:'tactician',seed:9}),hidden=observation();hidden.self.aim=Math.PI;hidden.self.z=2;hidden.target={visible:false};
 const intent=advance(travel,hidden,.8),length=Math.hypot(intent.x,intent.z);assert(length>.2);assert((intent.ax*intent.x+intent.az*intent.z)/length>.9,'Search movement faces its path instead of forced slow backpedalling');
}
// Strong abilities compete with retreat when tactically useful; they are not
// dead branches hidden permanently below a higher fixed utility score.
{
 const cinders=new TacticalDuelBot({difficulty:'tactician',seed:2}),o=observation();o.self.heroId='cendres';o.self.hp=80;o.self.max=145;o.self.heat=90;o.target.z=-3.4;
 let used=false;advance(cinders,o,.5,60,()=>{});for(let i=0;i<30;i++)used=cinders.update(o,1/60).power||used;assert(used&&cinders.debug.state==='ability','A hot cannon actually uses its close-range release');
 const thief=new TacticalDuelBot({difficulty:'tactician',seed:2}),v=observation();v.self.heroId='voleur';v.self.hp=48;v.self.max=105;v.self.hasDouble=v.self.canSwap=true;v.self.doublePosition={x:0,z:7};v.target.z=-3.4;
 let swapped=false;for(let i=0;i<45;i++)swapped=thief.update(v,1/60).power||swapped;assert(swapped,'A thief can retreat to its own known safer double');
 const unsafe=new TacticalDuelBot({difficulty:'tactician',seed:2});v.self.doublePosition={x:0,z:-3};let badSwap=false;for(let i=0;i<45;i++)badSwap=unsafe.update(v,1/60).power||badSwap;assert(!badSwap,'Do not swap to a double closer to the attacker simply because cooldown is ready');
}

// Fixed decision cadence, seeded replay and bounded adaptation remain stable
// across the simulation rates used by the existing game tests.
const rates=[];
for(const hz of [30,60,120]){
 const bot=new TacticalDuelBot({difficulty:'tactician',seed:'same-round'}),other=new TacticalDuelBot({difficulty:'tactician',seed:'same-round'}),o=observation();let output;
 for(let i=0;i<hz*3;i++){const phase=Math.floor((i/hz)/.4)%2?'recover':'windup';o.target.attack={phase};output=bot.update(o,1/hz);assert.deepStrictEqual(output,other.update(o,1/hz),'Same seed/input replay must match exactly');assert(Math.hypot(output.x,output.z)<=1.000001);assert(Object.values(output).every(value=>typeof value==='boolean'||Number.isFinite(value)));}
 assert(bot.habits.closeAttacks>=0&&bot.habits.closeAttacks<=1);rates.push({hz,decisions:bot.decisionCount,state:bot.debug.state,switches:bot.switches});
}
assert(rates.every(r=>r.decisions===rates[0].decisions&&r.state===rates[0].state),'Decision ticks must not depend on render FPS');
{
 const bot=new TacticalDuelBot({difficulty:'constructor',seed:'safe'}),bad=observation();bad.target={visible:true,x:NaN,z:Infinity};bad.projectiles=[{x:0,z:0,dx:1e300,dz:1e300,speed:Infinity}];bad.arenaBounds={minX:-1e300,maxX:1e300,minZ:-1e300,maxZ:1e300};
 for(let i=0;i<60;i++){const input=bot.update(bad,1/60);assert(Object.values(input).every(value=>typeof value==='boolean'||Number.isFinite(value)));}
 assert(bot.samples.length<=260&&bot.difficulty==='veteran');
}
assert.strictEqual(networkCalls,0);console.log('BOT_REPORT '+JSON.stringify({firstReaction,navigation,rates,networkCalls}));
console.log('PASS: delayed public perception, geometry/hidden-state veto, recovery punish, fair projectile reactions, own cooldowns, actual pillar route, cover, expiring memory and deterministic bounded local utility decisions. No match-balance or AAA claim.');
'''
result = subprocess.run(['node', '-e', PROGRAM, str(ROOT)], cwd=ROOT, text=True, capture_output=True)
if result.stdout:
    print(result.stdout, end='')
if result.stderr:
    print(result.stderr, end='')
if result.returncode:
    raise SystemExit(result.returncode)
report_line = next(line for line in result.stdout.splitlines() if line.startswith('BOT_REPORT '))
Path('/tmp/royaumes-tactical-bot-report.json').write_text(json.dumps(json.loads(report_line.removeprefix('BOT_REPORT ')), indent=2) + '\n')
