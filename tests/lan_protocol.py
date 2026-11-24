"""Security contract at the LAN boundary: malformed, forged and excessive data.

Pure Node/JS; it does not create a network connection or a renderer.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
globalThis.crypto=require('crypto').webcrypto;
const P=require(process.argv[1]+'/src/lan-protocol.js'),sid=P.createSessionId();
const fingerprint=Array(32).fill('AB').join(':');
const sdp=(address='192.168.1.5',kind='offer')=>({type:kind,sdp:['v=0','o=- 12 2 IN IP4 127.0.0.1','s=-','t=0 0','a=group:BUNDLE 0','m=application 9 UDP/DTLS/SCTP webrtc-datachannel','c=IN IP4 0.0.0.0','a=mid:0','a=ice-ufrag:abcd','a=ice-pwd:abcdefghijklmnopqrstuv','a=fingerprint:sha-256 '+fingerprint,'a=setup:'+(kind==='offer'?'actpass':'active'),'a=sctp-port:5000','a=max-message-size:65536','a=candidate:1 1 udp 2122260223 '+address+' 54400 typ host','a=end-of-candidates',''].join('\r\n')});
function rejects(fn,label){assert.throws(fn,undefined,label);}
const now=1800000000000,invite=P.createPairEnvelope('offer',sid,sdp(),{now});
assert(/^[a-f0-9]{64}$/.test(sid));assert.notStrictEqual(sid,P.createSessionId());
assert.deepStrictEqual(P.parsePairEnvelope(JSON.stringify(invite),{kind:'offer',now}),invite);
for(const address of ['10.0.0.2','192.168.254.2','172.16.0.4','172.31.0.4','169.254.2.3','127.0.0.1','fd00::1','fc00::2','fe80::1234','::1','5ec43211-80c6-4e45-96e8-a53ffab56508.local']){
 assert(P.localAddress(address),address);assert(P.createPairEnvelope('offer',sid,sdp(address),{now}),address);
}
for(const address of ['8.8.8.8','172.32.0.4','172.15.0.4','198.51.100.4','192.168.01.1','256.0.0.1','0.0.0.0','example.com','a.b.local','fc:','fc00:','fc00::gg','fc00:::1','0fe8::1','2001:db8::1','::ffff:127.0.0.1']){
 assert(!P.localAddress(address),address);rejects(()=>P.createPairEnvelope('offer',sid,sdp(address),{now}),address);
}
const withPublic=sdp();withPublic.sdp=withPublic.sdp.replace('a=end-of-candidates','a=candidate:2 1 udp 1 203.0.113.4 54401 typ srflx raddr 192.168.1.5 rport 54400\r\na=end-of-candidates');
rejects(()=>P.createPairEnvelope('offer',sid,withPublic,{now}),'Foreign candidate must not cross the invitation boundary');
assert(!P.filterLocalDescription(withPublic).sdp.includes('203.0.113.4'),'Local outgoing filtering removes non-LAN candidates');
for(const raw of ['{bad',JSON.stringify({...invite,kind:'answer'}),JSON.stringify({...invite,session:'x'}),JSON.stringify({...invite,expires:now}),JSON.stringify({...invite,expires:now+P.PAIR_TTL+1}),JSON.stringify({...invite,created:now+120001}),JSON.stringify({...invite,tracking:'secret'}),JSON.stringify({...invite,sdp:{type:'offer',sdp:'x'.repeat(32769)}})])rejects(()=>P.parsePairEnvelope(raw,{kind:'offer',now}));
rejects(()=>P.parsePairEnvelope({...invite,sdp:{...sdp(),sdp:sdp().sdp.replace('0.0.0.0','8.8.8.8')}},{now}),'SDP connection line cannot point outside LAN');
rejects(()=>P.parsePairEnvelope(invite,{session:P.createSessionId(),now}),'Answer/invitation session pinning');
rejects(()=>P.parsePairEnvelope(invite,{now:now+P.PAIR_TTL+1}),'Expired invitation');

const heroes=vm.runInNewContext(fs.readFileSync(process.argv[1]+'/src/roster.js','utf8').split('function isHeroId')[0]+';HERO_DEFS');
assert.deepStrictEqual(Object.keys(P.HERO_HP).sort(),Object.keys(heroes).sort());
for(const [hero,hp] of Object.entries(P.HERO_HP)){
 assert.strictEqual(hp,heroes[hero].hp,'The network HP schema must follow the published roster');
 assert.strictEqual(P.createPacket('hello',sid,1,{name:'Voyageur',hero}).payload.hero,hero);
}
const input={x:.5,z:-1,aim:Math.PI,fire:true,dash:false,power:false,extra:true,interact:false};
const packet=P.createPacket('input',sid,1,input);assert.strictEqual(P.encodePacket(packet),JSON.stringify(packet));
for(const value of [NaN,Infinity,-Infinity,'1',null,true,1.001])rejects(()=>P.createPacket('input',sid,1,{...input,x:value}));
for(const key of ['hp','max','x2','slot','hero','damage','constructor','__proto__']){
 const value=JSON.parse(JSON.stringify(input));Object.defineProperty(value,key,{value:10,enumerable:true});rejects(()=>P.createPacket('input',sid,1,value),key);
}
for(const hero of ['constructor','toString','__proto__','prototype','missing',{},null])rejects(()=>P.createPacket('hello',sid,1,{name:'Joueur',hero}));
rejects(()=>P.createPacket('hello',sid,1,{name:'A\u202eB',hero:'lame'}));
rejects(()=>P.createPacket('hello',sid,1,{name:'a'.repeat(25),hero:'lame'}));
let getterRead=false;const getter={name:'Joueur'};Object.defineProperty(getter,'hero',{enumerable:true,get(){getterRead=true;return'lame';}});rejects(()=>P.createPacket('hello',sid,1,getter));assert(!getterRead,'Accessors must not execute at the boundary');
const symbolic={name:'Joueur',hero:'lame'};symbolic[Symbol('tracking')]=1;rejects(()=>P.createPacket('hello',sid,1,symbolic));

const actor=(slot,hero)=>({slot,hero,x:slot?9:-9,z:-7,vx:0,vz:0,aim:0,hp:P.HERO_HP[hero],max:P.HERO_HP[hero],downed:false,attack:{id:3,melee:true,combo:1,elapsed:.2,duration:.9,hitAt:.23,activeEnd:.35,aim:0,struck:false,charge:0},formT:8,incarnateT:8,fragileT:4,wardT:.2,heat:100,incarnation:100,absorbLock:.35,overcharge:3,doubleSwapLock:.7,comboWindow:1.05,powerVisualT:.35,powerVisualDuration:.5,powerVisualSerial:4});
const effects=['rift','burn','double','bergere','neant','eclipse','cover','rhythm','incarnation'].map((kind,id)=>({id,kind,owner:id%2,x:0,z:-7,r:4,life:2,color:'#aabbcc',...(kind==='rift'?{x2:4,z2:-10}:{}),...(kind==='cover'?{boxes:[{x:1,z:-7,w:.9,d:.9}]}:{})}));
const snap={tick:1,time:90,phase:'playing',round:1,wins:[0,0],winner:-1,actors:[actor(0,'lame'),actor(1,'rempart')],bullets:[{id:4,x:70,z:-120,y:3,dx:1,dz:0,life:1,owner:0,type:'tisseuse'}],effects};
assert.strictEqual(P.createPacket('snapshot',sid,2,snap).payload.effects.length,9);
for(const hero of Object.keys(heroes))assert(P.createPacket('snapshot',sid,2,{...snap,actors:[actor(0,hero),actor(1,'rempart')]}));
for(const [key,value] of [['x',18.01],['z',-28.01],['hp',151],['max',151],['formT',13],['heat',101],['incarnation',101],['dashDuration',2],['motionSpeed',41],['powerVisualT',4.01],['powerVisualDuration',Infinity],['powerVisualSerial',1.5]])rejects(()=>P.createPacket('snapshot',sid,2,{...snap,actors:[{...actor(0,'rempart'),[key]:value},actor(1,'lame')]}),key);
rejects(()=>P.createPacket('snapshot',sid,2,{...snap,actors:[actor(0,'lame'),actor(0,'rempart')]}),'Unique player slots');
rejects(()=>P.createPacket('snapshot',sid,2,{...snap,bullets:Array(65).fill(snap.bullets[0])}),'Bounded projectile work');
rejects(()=>P.createPacket('snapshot',sid,2,{...snap,effects:Array(25).fill(effects[0])}),'Bounded effect work');
rejects(()=>P.createPacket('snapshot',sid,2,{...snap,effects:[{...effects[0],color:'url(x) '}]}),'Color cannot become an injected URL');
const missingExit={...effects[0]};delete missingExit.x2;delete missingExit.z2;rejects(()=>P.createPacket('snapshot',sid,2,{...snap,effects:[missingExit]}),'A portal must have a complete finite exit before rendering');
rejects(()=>P.createPacket('snapshot',sid,2,{...snap,effects:[{...effects[6],boxes:Array(4).fill({x:1,z:-7,w:.9,d:.9})}]}),'Bounded collision work');
const hiddenArray=[actor(0,'lame'),actor(1,'rempart')];Object.defineProperty(hiddenArray,'secret',{value:1});rejects(()=>P.createPacket('snapshot',sid,2,{...snap,actors:hiddenArray}));
rejects(()=>P.encodePacket({v:1,session:sid,type:'input',seq:1,payload:{...input,padding:'x'.repeat(70000)}}));
rejects(()=>P.createGuard({role:'host',session:sid}).accept(' '.repeat(65537)),'Byte limit before JSON parsing');

let clock=0;const host=P.createGuard({role:'host',session:sid,now:()=>clock});host.accept(P.encodePacket(packet));
rejects(()=>host.accept(P.encodePacket(packet)),'Replay');rejects(()=>host.accept(P.encodePacket(P.createPacket('snapshot',sid,2,snap))),'Guest cannot assign state or HP');
rejects(()=>host.accept(P.encodePacket(P.createPacket('input',P.createSessionId(),2,input))),'Session isolation');
clock+=100;host.accept(P.encodePacket(P.createPacket('input',sid,2,input)));
const guest=P.createGuard({role:'guest',session:sid,now:()=>clock});guest.accept(P.encodePacket(P.createPacket('snapshot',sid,1,snap)));rejects(()=>guest.accept(P.encodePacket(P.createPacket('input',sid,2,input))),'Host input cannot replace a guest control');
let accepted=0;const flood=P.createGuard({role:'host',session:sid,now:()=>clock});for(let i=0;i<50;i++){try{flood.accept(P.encodePacket(P.createPacket('input',sid,i,input)));accepted++;}catch(_){}}
assert.strictEqual(accepted,12,'Burst input cap');clock+=1000;assert(flood.accept(P.encodePacket(P.createPacket('input',sid,100,input))));
assert(!JSON.stringify(host.stats()).includes(sid),'Diagnostics do not expose the session identifier');
console.log('PASS: 11 heroes, bounded schemas and visuals, private/mDNS ICE only, expiring pinned invitations, no prototype/accessor inputs, role/session/sequence authorization and flood/size limits. Pure CPU.');
'''
subprocess.run(['node', '-e', PROGRAM, str(ROOT)], check=True, cwd=ROOT)
