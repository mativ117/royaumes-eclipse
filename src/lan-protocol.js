'use strict';
// Validation at the WebRTC trust boundary. No renderer, storage or network calls.
const EclipseLanProtocol=(()=>{
 const VERSION=1,MAX_PACKET_BYTES=65536,MAX_SDP_BYTES=32768,PAIR_TTL=600000,CLOCK_SKEW=120000,MAX_SEQ=2147483647;
 const HERO_HP=Object.freeze({rempart:150,voltigeur:110,lame:125,tisseuse:105,cendres:145,voleur:105,bergere:120,colosse:190,accordeur:120,neant:100,eclipse:140}),BANNED=new Set(['__proto__','prototype','constructor']);
 class ProtocolError extends Error{constructor(code){super('Échange LAN refusé : '+code);this.name='EclipseLanProtocolError';this.code=code;}}
 const fail=code=>{throw new ProtocolError(code);},has=(o,k)=>Object.hasOwn(o,k);
 function record(value,keys,required=keys){
  if(value===null||typeof value!=='object'||Array.isArray(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))fail('objet');
  const descriptors=Object.getOwnPropertyDescriptors(value);
  if(Object.getOwnPropertySymbols(value).length)fail('champ');
  for(const key of Object.getOwnPropertyNames(value))if(BANNED.has(key)||!keys.includes(key)||descriptors[key].get||descriptors[key].set)fail('champ');
  for(const key of required)if(!has(value,key))fail('champ-manquant');return value;
 }
 function num(value,min,max,integer=false){if(typeof value!=='number'||!Number.isFinite(value)||value<min||value>max||integer&&!Number.isInteger(value))fail('nombre');return value;}
 function bool(value){if(typeof value!=='boolean')fail('booléen');return value;}
 function text(value,max,min=0){if(typeof value!=='string'||value.length<min||value.length>max||/[\u0000-\u001f\u007f\u202a-\u202e\u2066-\u2069]/u.test(value))fail('texte');return value;}
 function one(value,values){if(!values.includes(value))fail('valeur');return value;}
 function array(value,max,min=0){if(!Array.isArray(value)||Object.getPrototypeOf(value)!==Array.prototype||value.length<min||value.length>max||Object.getOwnPropertySymbols(value).length||Object.keys(value).length!==value.length||Object.getOwnPropertyNames(value).length!==value.length+1)fail('liste');const descriptors=Object.getOwnPropertyDescriptors(value);for(let i=0;i<value.length;i++){const item=descriptors[i];if(!item||item.get||item.set)fail('liste');}return value;}
 function bytes(value,max){if(typeof value!=='string'||value.length>max||new TextEncoder().encode(value).byteLength>max)fail('taille');return value;}
 function sessionId(value){if(typeof value!=='string'||!/^[0-9a-f]{64}$/.test(value))fail('session');return value;}
 function hero(value){if(typeof value!=='string'||!has(HERO_HP,value))fail('héros');return value;}
 function parse(raw,max=MAX_PACKET_BYTES){
  if(typeof raw==='string'){bytes(raw,max);try{return JSON.parse(raw);}catch(_){fail('json');}}
  // Public helpers may receive an object from their trusted local caller.
  // Descriptors are checked by each schema before any field is read.
  return raw;
 }
 function createSessionId(){const data=new Uint8Array(32);if(!globalThis.crypto?.getRandomValues)fail('crypto-indisponible');globalThis.crypto.getRandomValues(data);return Array.from(data,x=>x.toString(16).padStart(2,'0')).join('');}
 function localAddress(value){
  if(/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.local$/i.test(value))return true;
  const parts=value.split('.');if(parts.length===4&&parts.every(x=>/^\d{1,3}$/.test(x)&&String(Number(x))===x&&Number(x)<=255)){
   const [a,b]=parts.map(Number);return a===10||a===127||a===192&&b===168||a===172&&b>=16&&b<=31||a===169&&b===254;
  }
  const ip=value.toLowerCase();if(!/^[0-9a-f:]+$/.test(ip)||!ip.includes(':')||ip.includes(':::'))return false;const compressed=ip.includes('::'),halves=ip.split('::');if(halves.length>2)return false;const groups=halves.flatMap(half=>half?half.split(':'):[]);if(groups.some(group=>!/^[0-9a-f]{1,4}$/.test(group))||(compressed?groups.length>=8:groups.length!==8))return false;const first=ip.startsWith('::')?0:parseInt(groups[0],16);return ip==='::1'||(first&0xfe00)===0xfc00||(first&0xffc0)===0xfe80;
 }
 function candidateIsLocal(line){
  const parts=line.slice(12).trim().split(/\s+/);return parts.length>=8&&parts.length<=30&&parts[1]==='1'&&['udp','tcp'].includes(parts[2]?.toLowerCase())&&/^\d+$/.test(parts[3]||'')&&Number(parts[3])<=4294967295&&localAddress(parts[4]||'')&&/^\d+$/.test(parts[5]||'')&&Number(parts[5])>=1&&Number(parts[5])<=65535&&parts[6]==='typ'&&parts[7]==='host'&&!parts.includes('raddr')&&!parts.includes('rport');
 }
 function validateSdp(description,kind){
  record(description,['type','sdp']);one(description.type,[kind]);const raw=bytes(description.sdp,MAX_SDP_BYTES);
  if(/[^\t\r\n\x20-\x7e]/.test(raw))fail('sdp-texte');const lines=raw.split(/\r?\n/);if(lines.length>400||lines.some(x=>x.length>1024)||lines[0]!=='v=0')fail('sdp-format');
  const connections=lines.filter(x=>x.startsWith('c='));if(!connections.length||connections.length>2||connections.some(line=>{const match=/^c=IN IP([46]) ([^ ]+)$/.exec(line);return !match||!['0.0.0.0','::'].includes(match[2])&&!localAddress(match[2]);}))fail('sdp-destination');
  const media=lines.filter(x=>x.startsWith('m='));if(media.length!==1||!/^m=application \d+ (?:UDP|TCP)\/DTLS\/SCTP webrtc-datachannel$/.test(media[0]))fail('sdp-canal');
  if(!lines.some(x=>/^a=fingerprint:sha-256 (?:[0-9A-Fa-f]{2}:){31}[0-9A-Fa-f]{2}$/i.test(x))||!lines.some(x=>/^a=ice-ufrag:[A-Za-z0-9+/]{4,256}$/.test(x))||!lines.some(x=>/^a=ice-pwd:[A-Za-z0-9+/]{22,256}$/.test(x)))fail('sdp-dtls');
  const candidates=lines.filter(x=>x.startsWith('a=candidate:'));if(!candidates.length||candidates.length>64||candidates.some(x=>!candidateIsLocal(x))||lines.some(x=>x.startsWith('a=remote-candidates:')))fail('sdp-réseau-local');
  return{type:kind,sdp:raw};
 }
 function filterLocalDescription(description){
  record(description,['type','sdp']);one(description.type,['offer','answer']);const raw=bytes(description.sdp,MAX_SDP_BYTES),sdp=raw.split(/\r?\n/).filter(line=>!line.startsWith('a=candidate:')||candidateIsLocal(line)).join('\r\n');return validateSdp({type:description.type,sdp},description.type);
 }
 function parsePairEnvelope(raw,{kind,session,now=Date.now()}={}){
  const envelope=record(parse(raw),['format','v','kind','session','created','expires','sdp']);one(envelope.format,['eclipse-lan-pair']);one(envelope.v,[VERSION]);one(envelope.kind,['offer','answer']);if(kind&&envelope.kind!==kind)fail('invitation-type');sessionId(envelope.session);if(session&&envelope.session!==session)fail('invitation-session');
  num(now,0,Number.MAX_SAFE_INTEGER);const created=num(envelope.created,0,Number.MAX_SAFE_INTEGER,true),expires=num(envelope.expires,0,Number.MAX_SAFE_INTEGER,true);if(expires<=now||created>now+CLOCK_SKEW||expires<=created||expires-created>PAIR_TTL||now-created>PAIR_TTL+CLOCK_SKEW)fail('invitation-expirée');
  return{format:'eclipse-lan-pair',v:VERSION,kind:envelope.kind,session:envelope.session,created,expires,sdp:validateSdp(envelope.sdp,envelope.kind)};
 }
 function createPairEnvelope(kind,session,sdp,{now=Date.now(),expires=now+PAIR_TTL}={}){return parsePairEnvelope({format:'eclipse-lan-pair',v:VERSION,kind,session,created:now,expires,sdp},{kind,session,now});}
 function hello(value){record(value,['name','hero']);return{name:text(value.name,24,1).trim()||'Voyageur',hero:hero(value.hero)};}
 function input(value){record(value,['x','z','aim','fire','dash','power','extra','interact']);return{x:num(value.x,-1,1),z:num(value.z,-1,1),aim:num(value.aim,-Math.PI,Math.PI),fire:bool(value.fire),dash:bool(value.dash),power:bool(value.power),extra:bool(value.extra),interact:bool(value.interact)};}
 function attack(value){
  if(value===null)return null;record(value,['melee','combo','elapsed','duration','hitAt','activeEnd','aim','charge','struck','id'],['melee','combo','elapsed','duration','hitAt','aim','struck']);const duration=num(value.duration,.01,4),hitAt=num(value.hitAt,0,duration),out={melee:bool(value.melee),combo:num(value.combo,0,3,true),elapsed:num(value.elapsed,0,duration+.1),duration,hitAt,aim:num(value.aim,-Math.PI,Math.PI),charge:has(value,'charge')?num(value.charge,0,3):0,struck:bool(value.struck)};if(has(value,'activeEnd'))out.activeEnd=num(value.activeEnd,hitAt,duration);if(has(value,'id'))out.id=num(value.id,0,MAX_SEQ,true);return out;
 }
 const ACTOR_REQUIRED=['slot','hero','x','z','vx','vz','aim','hp','max','downed'];
 const ACTOR_OPTIONAL=['inv','dash','dashT','power','shield','leap','recoil','combo','stagger','attack','dx','dz','dashElapsed','dashDuration','dashDistance','dashProfile','motionSpeed','shot','formT','incarnateT','fragileT','wardT','heat','incarnation','absorbLock','overcharge','doubleSwapLock','comboWindow','powerVisualT','powerVisualDuration','powerVisualSerial'];
 function actor(value){
  record(value,[...ACTOR_REQUIRED,...ACTOR_OPTIONAL],ACTOR_REQUIRED);const id=hero(value.hero),maximum=num(value.max,HERO_HP[id],HERO_HP[id]),out={slot:num(value.slot,0,1,true),hero:id,x:num(value.x,-18,18),z:num(value.z,-28,14),vx:num(value.vx,-12,12),vz:num(value.vz,-12,12),aim:num(value.aim,-Math.PI,Math.PI),hp:num(value.hp,0,maximum),max:maximum,downed:bool(value.downed)};
  for(const key of ['inv','dash','dashT','power','shield','leap','recoil','stagger','shot'])out[key]=has(value,key)?num(value[key],0,30):0;
  for(const key of ['formT','incarnateT','fragileT','wardT'])out[key]=has(value,key)?num(value[key],0,12):0;for(const key of ['heat','incarnation'])out[key]=has(value,key)?num(value[key],0,100):0;for(const key of ['absorbLock','doubleSwapLock'])out[key]=has(value,key)?num(value[key],0,1):0;for(const key of ['overcharge','comboWindow'])out[key]=has(value,key)?num(value[key],0,3):0;
  out.powerVisualT=has(value,'powerVisualT')?num(value.powerVisualT,0,4):0;out.powerVisualDuration=has(value,'powerVisualDuration')?num(value.powerVisualDuration,0,4):0;out.powerVisualSerial=has(value,'powerVisualSerial')?num(value.powerVisualSerial,0,MAX_SEQ,true):0;
  out.combo=has(value,'combo')?num(value.combo,0,3,true):0;out.attack=has(value,'attack')?attack(value.attack):null;
  for(const key of ['dx','dz'])out[key]=has(value,key)?num(value[key],-1,1):0;
  for(const key of ['dashElapsed','dashDuration'])out[key]=has(value,key)?num(value[key],0,1):0;
  out.dashDistance=has(value,'dashDistance')?num(value.dashDistance,0,6):0;out.dashProfile=has(value,'dashProfile')?one(value.dashProfile,['legacy','step']):'legacy';out.motionSpeed=has(value,'motionSpeed')?num(value.motionSpeed,0,40):Math.hypot(out.vx,out.vz);return out;
 }
 function bullet(value){record(value,['id','x','z','y','dx','dz','life','owner','type'],['x','z','y','dx','dz','life','owner','type']);const out={x:num(value.x,-80,80),z:num(value.z,-128,48),y:num(value.y,-1,12),dx:num(value.dx,-1,1),dz:num(value.dz,-1,1),life:num(value.life,0,3),owner:num(value.owner,0,1,true),type:one(value.type,['shot',...Object.keys(HERO_HP)])};if(has(value,'id'))out.id=num(value.id,1,MAX_SEQ,true);return out;}
 function effect(value){
  record(value,['id','kind','owner','x','z','r','life','color','x2','z2','boxes'],['id','kind','owner','x','z','r','life','color']);
  const out={id:num(value.id,0,MAX_SEQ,true),kind:one(value.kind,['rift','burn','double','bergere','neant','eclipse','cover','rhythm','incarnation']),owner:num(value.owner,0,1,true),x:num(value.x,-24,24),z:num(value.z,-34,20),r:num(value.r,0,8),life:num(value.life,0,12),color:text(value.color,7,7)};
  if(!/^#[0-9a-f]{6}$/i.test(out.color))fail('couleur');
  if(has(value,'x2')!==has(value,'z2')||out.kind==='rift'&&!has(value,'x2'))fail('portail');
  if(has(value,'x2')){if(out.kind!=='rift')fail('portail');out.x2=num(value.x2,-24,24);out.z2=num(value.z2,-34,20);}
  if(has(value,'boxes')){if(out.kind!=='cover')fail('abri');out.boxes=array(value.boxes,3).map(box=>{record(box,['x','z','w','d']);return{x:num(box.x,-24,24),z:num(box.z,-34,20),w:num(box.w,.1,2),d:num(box.d,.1,2)};});}
  return out;
 }
 function snapshot(value){
  record(value,['tick','time','phase','round','wins','winner','actors','bullets','effects'],['tick','time','phase','round','wins','actors','bullets']);const actors=array(value.actors,2,2).map(actor);if(new Set(actors.map(a=>a.slot)).size!==2)fail('joueurs');
  return{tick:num(value.tick,0,MAX_SEQ,true),time:num(value.time,0,180),phase:one(value.phase,['playing','paused','round-over','finished']),round:num(value.round,1,5,true),wins:array(value.wins,2,2).map(x=>num(x,0,3,true)),winner:has(value,'winner')?num(value.winner,-1,1,true):-1,actors,bullets:array(value.bullets,64).map(bullet),effects:has(value,'effects')?array(value.effects,24).map(effect):[]};
 }
 function payload(type,value){
  if(type==='hello')return hello(value);if(type==='input')return input(value);if(type==='snapshot')return snapshot(value);
  if(type==='ready'){record(value,['ready']);return{ready:bool(value.ready)};}
  if(type==='start'){record(value,['seed','round'],['seed']);return{seed:num(value.seed,0,MAX_SEQ,true),round:has(value,'round')?num(value.round,1,5,true):1};}
  if(type==='pause'){record(value,['paused']);return{paused:bool(value.paused)};}
  if(type==='request'){record(value,['action']);return{action:one(value.action,['pause','resume','leave'])};}
  if(type==='ping'){record(value,['stamp']);return{stamp:num(value.stamp,0,Number.MAX_SAFE_INTEGER)};}
  if(type==='bye'){record(value,['reason'],[]);return{reason:has(value,'reason')?one(value.reason,['leave','timeout','error','finished']):'leave'};}
  fail('type');
 }
 const DIRECTIONS=Object.freeze({host:['hello','ready','input','request','ping','bye'],guest:['hello','start','pause','snapshot','ping','bye']});
 function normalizePacket(raw){const value=record(parse(raw),['v','session','type','seq','payload']);one(value.v,[VERSION]);sessionId(value.session);const type=one(value.type,['hello','ready','input','request','start','pause','snapshot','ping','bye']);return{v:VERSION,session:value.session,type,seq:num(value.seq,0,MAX_SEQ,true),payload:payload(type,value.payload)};}
 function createPacket(type,session,seq,value){return normalizePacket({v:VERSION,session,type,seq,payload:value});}
 function encodePacket(value){const raw=JSON.stringify(normalizePacket(value));bytes(raw,MAX_PACKET_BYTES);return raw;}
 function bucket(rate,burst,now){let tokens=burst,last=now();return()=>{const time=now();if(!Number.isFinite(time))fail('horloge');tokens=Math.min(burst,tokens+Math.max(0,time-last)*rate/1000);last=time;if(tokens<1)fail('débit');tokens--;};}
 function createGuard({role,session,now=()=>globalThis.performance?.now?.()??Date.now()}={}){
  one(role,['host','guest']);sessionId(session);if(typeof now!=='function')fail('horloge');const all=bucket(80,100,now),limits={input:bucket(40,12,now),snapshot:bucket(30,8,now),ping:bucket(2,4,now),control:bucket(20,12,now)};let lastSeq=-1,count=0;
  return Object.freeze({accept(raw){all();const packet=normalizePacket(raw);if(packet.session!==session||!DIRECTIONS[role].includes(packet.type))fail('autorité');if(packet.seq<=lastSeq)fail('séquence');(limits[packet.type]||limits.control)();lastSeq=packet.seq;count++;return packet;},stats(){return Object.freeze({lastSeq,accepted:count});}});
 }
 return Object.freeze({VERSION,MAX_PACKET_BYTES,MAX_SDP_BYTES,PAIR_TTL,HERO_HP,ProtocolError,createSessionId,localAddress,filterLocalDescription,createPairEnvelope,parsePairEnvelope,createPacket,encodePacket,createGuard});
})();
if(typeof module!=='undefined'&&module.exports)module.exports=EclipseLanProtocol;
