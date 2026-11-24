'use strict';

// Direct, manually paired WebRTC. This module never fetches a signalling service,
// configures STUN/TURN, accesses storage or exposes SDP through diagnostics.
class EclipseLanPeer {
 constructor(options={}){
  this.onStatus=typeof options.onStatus==='function'?options.onStatus:()=>{};
  this.onPacket=typeof options.onPacket==='function'?options.onPacket:()=>{};
  this.onOpen=typeof options.onOpen==='function'?options.onOpen:()=>{};
  this.onClose=typeof options.onClose==='function'?options.onClose:()=>{};
  this.role=null;this.session=null;this.pc=null;this.channel=null;this.connected=false;this.state='idle';
  this.closed=false;this.remoteReady=false;this._seq=0;this._guard=null;this._answerAccepted=false;
  this._gatherTimeout=Math.min(12000,Math.max(1000,Number(options.gatherTimeoutMs)||8000));
  this._connectTimeout=Math.min(60000,Math.max(5000,Number(options.connectTimeoutMs)||25000));
  this._staleTimeout=Math.min(20000,Math.max(4000,Number(options.staleTimeoutMs)||8000));
  this._maxBuffer=128*1024;this._timers=new Set();this._heartbeat=null;this._expiry=null;this._connecting=null;
  this._gatherCancel=null;this._pairExpires=0;this._lastReceive=0;
  this._stats={sent:0,received:0,dropped:0,rejected:0,bytesSent:0,bytesReceived:0,lastReceiveAt:0};
 }
 static supported(){return globalThis.isSecureContext!==false&&typeof RTCPeerConnection==='function'&&typeof globalThis.crypto?.getRandomValues==='function';}
 _status(state,message){this.state=state;this.onStatus({state,message});}
 _timer(fn,delay){const id=setTimeout(()=>{this._timers.delete(id);fn();},delay);this._timers.add(id);return id;}
 _clearTimer(id){if(id!==null){clearTimeout(id);this._timers.delete(id);}}
 _begin(role,session){
  if(this.closed||this.pc)throw new Error('Cette invitation est déjà utilisée. Crée une nouvelle connexion.');
  if(globalThis.isSecureContext===false)throw new Error('Ouvre le jeu avec son lien HTTPS pour préparer une connexion locale.');
  if(!EclipseLanPeer.supported())throw new Error('Ce navigateur ne permet pas la connexion directe. Ouvre le jeu dans Safari ou Chrome à jour.');
  this.role=role;this.session=session;this._guard=EclipseLanProtocol.createGuard({role,session});
  this.pc=new RTCPeerConnection({iceServers:[],iceTransportPolicy:'all',iceCandidatePoolSize:0,bundlePolicy:'max-bundle'});
  this.pc.onconnectionstatechange=()=>{
   if(this.closed)return;
   if(this.pc.connectionState==='failed')this._fail('network');
   else if(this.pc.connectionState==='closed')this.close('remote');
  };
  this.pc.oniceconnectionstatechange=()=>{if(!this.closed&&this.pc.iceConnectionState==='failed')this._fail('network');};
  this.pc.ondatachannel=event=>{
   if(this.closed){event.channel.close();return;}
   if(this.role!=='guest'||this.channel||event.channel.label!=='eclipse-lan-v1'||event.channel.protocol!=='eclipse/1'||!event.channel.ordered||event.channel.negotiated||event.channel.maxRetransmits!==null||event.channel.maxPacketLifeTime!==null){event.channel.close();this._fail('protocol');return;}
   this._bindChannel(event.channel);
  };
  if(role==='host')this._bindChannel(this.pc.createDataChannel('eclipse-lan-v1',{ordered:true,protocol:'eclipse/1'}));
 }
 _bindChannel(channel){
  this.channel=channel;channel.binaryType='arraybuffer';channel.bufferedAmountLowThreshold=32*1024;
  channel.onopen=()=>{
   if(this.closed)return;
   if(this._pairExpires&&Date.now()>=this._pairExpires){this._fail('expired');return;}
   this.connected=true;this._clearTimer(this._expiry);this._clearTimer(this._connecting);
   this._lastReceive=performance.now();this._stats.lastReceiveAt=this._lastReceive;
   this._status('connected','Appareils connectés directement.');
   this._heartbeat=setInterval(()=>{
    if(this.closed)return;
    if(performance.now()-this._lastReceive>this._staleTimeout){this._fail('stale');return;}
    this.send('ping',{stamp:performance.now()});
   },1000);
   this.onOpen();
  };
  channel.onmessage=event=>{
   if(this.closed||!this.connected)return;
   let packet;
   try{if(typeof event.data!=='string')throw new Error('binary');packet=this._guard.accept(event.data);}
   catch(_){this._stats.rejected++;this._fail('protocol');return;}
   this._lastReceive=performance.now();this._stats.received++;this._stats.bytesReceived+=new TextEncoder().encode(event.data).byteLength;this._stats.lastReceiveAt=this._lastReceive;
   if(packet.type==='bye'){this.close('remote');return;}
   if(packet.type==='ready')this.remoteReady=packet.payload.ready;
   if(packet.type!=='ping')this.onPacket(packet);
  };
  channel.onerror=()=>{if(!this.closed)this._fail('network');};
  channel.onclose=()=>{if(!this.closed)this.close('remote');};
 }
 _gather(){
  return new Promise((resolve,reject)=>{
   const pc=this.pc;let done=false,timer=null;
   const finish=error=>{if(done)return;done=true;this._clearTimer(timer);pc.removeEventListener('icegatheringstatechange',changed);this._gatherCancel=null;error?reject(error):resolve();};
   const changed=()=>{if(pc.iceGatheringState==='complete')finish();};
   this._gatherCancel=()=>finish(new Error('Appairage annulé.'));
   pc.addEventListener('icegatheringstatechange',changed);
   timer=this._timer(()=>finish(new Error('La collecte réseau n’a pas abouti. Vérifie le Wi-Fi et crée une nouvelle invitation.')),this._gatherTimeout);
   changed();
  });
 }
 _armExpiry(expires){
  this._pairExpires=expires;this._clearTimer(this._expiry);
  this._expiry=this._timer(()=>{if(!this.connected)this._fail('expired');},Math.max(1,expires-Date.now()));
 }
 async createOffer(){
  this._begin('host',EclipseLanProtocol.createSessionId());this._status('gathering','Préparation de l’invitation sur ce réseau…');
  try{
   await this.pc.setLocalDescription(await this.pc.createOffer());await this._gather();
   if(this.closed)throw new Error('Appairage annulé.');
   const invitation=EclipseLanProtocol.createPairEnvelope('offer',this.session,EclipseLanProtocol.filterLocalDescription({type:this.pc.localDescription.type,sdp:this.pc.localDescription.sdp}));
   this._armExpiry(invitation.expires);this._status('invitation','Invitation prête. Partage-la avec l’autre appareil, puis importe sa réponse.');return invitation;
  }catch(_){if(!this.closed)this._fail('gather');throw new Error('Impossible de préparer une invitation locale. Le navigateur ou ce réseau ne fournit pas de connexion directe utilisable.');}
 }
 async acceptOffer(raw){
  const invitation=EclipseLanProtocol.parsePairEnvelope(raw,{kind:'offer'});
  if(Date.now()>=invitation.expires)throw new Error('Cette invitation a expiré.');
  this._begin('guest',invitation.session);this._armExpiry(invitation.expires);this._status('gathering','Préparation de la réponse sur ce réseau…');
  try{
   await this.pc.setRemoteDescription(invitation.sdp);await this.pc.setLocalDescription(await this.pc.createAnswer());await this._gather();
   if(this.closed)throw new Error('Appairage annulé.');
   const response=EclipseLanProtocol.createPairEnvelope('answer',this.session,EclipseLanProtocol.filterLocalDescription({type:this.pc.localDescription.type,sdp:this.pc.localDescription.sdp}),{expires:invitation.expires});
   if(!this.connected)this._status('answer','Réponse prête. Renvoie-la à l’appareil qui a créé l’invitation.');return response;
  }catch(_){if(!this.closed)this._fail('gather');throw new Error('Impossible de répondre à cette invitation. Vérifie le réseau ou demande une nouvelle invitation.');}
 }
 async acceptAnswer(raw){
  if(this.closed||this.role!=='host'||!this.pc||this._answerAccepted||this.pc.signalingState!=='have-local-offer')throw new Error('Crée d’abord une nouvelle invitation.');
  if(Date.now()>=this._pairExpires){this._fail('expired');throw new Error('Cette invitation a expiré.');}
  const response=EclipseLanProtocol.parsePairEnvelope(raw,{kind:'answer',session:this.session});
  if(response.expires!==this._pairExpires)throw new Error('Cette réponse ne correspond pas à l’invitation en attente.');
  this._answerAccepted=true;this._status('connecting','Connexion directe en cours…');
  try{
   await this.pc.setRemoteDescription(response.sdp);
   if(!this.connected)this._connecting=this._timer(()=>{if(!this.connected)this._fail('timeout');},this._connectTimeout);
  }catch(_){if(!this.closed)this._fail('network');throw new Error('La connexion n’a pas abouti. Vérifie que les appareils peuvent communiquer sur ce Wi-Fi.');}
 }
 send(type,payload={}){
  if(!this.connected||this.closed||this.channel?.readyState!=='open')return false;
  const allowed=this.role==='host'?['hello','start','snapshot','pause','ping','bye']:['hello','ready','request','input','ping','bye'];
  if(!allowed.includes(type)){this._stats.rejected++;return false;}
  try{
   const packet=EclipseLanProtocol.createPacket(type,this.session,this._seq,payload),encoded=EclipseLanProtocol.encodePacket(packet),size=new TextEncoder().encode(encoded).byteLength;
   if(this.channel.bufferedAmount+size>this._maxBuffer){this._stats.dropped++;return false;}
   this.channel.send(encoded);this._seq++;this._stats.sent++;this._stats.bytesSent+=size;return true;
  }catch(_){this._stats.rejected++;return false;}
 }
 getStats(){return{...this._stats,connected:this.connected,state:this.state,bufferedAmount:this.channel?.bufferedAmount||0,connectionState:this.closed?'closed':this.pc?.connectionState||'new',iceConnectionState:this.closed?'closed':this.pc?.iceConnectionState||'new'};}
 _fail(reason){this._finish(reason,true);}
 close(reason='manual'){this._finish(reason,false);}
 _finish(reason,failed){
  if(this.closed)return;this.closed=true;this.connected=false;
  const messages={manual:'Connexion fermée.',remote:'L’autre appareil a quitté la connexion.',network:'Connexion locale impossible ou interrompue. Vérifie le Wi-Fi, l’isolation des appareils et le navigateur.',stale:'L’autre appareil ne répond plus. La partie est arrêtée.',timeout:'La connexion n’a pas abouti. Les appareils doivent pouvoir communiquer sur le même réseau.',expired:'Cette invitation a expiré. Crée une nouvelle connexion.',gather:'Aucune connexion locale utilisable n’a été trouvée. Ce Wi-Fi ou ce navigateur peut bloquer les échanges directs.',protocol:'La connexion a été arrêtée : des données non valides ont été reçues.'};
  if(this._gatherCancel)this._gatherCancel();for(const timer of this._timers)clearTimeout(timer);this._timers.clear();
  if(this._heartbeat!==null)clearInterval(this._heartbeat);this._heartbeat=null;
  if(this.channel){this.channel.onopen=this.channel.onmessage=this.channel.onclose=this.channel.onerror=null;try{this.channel.close();}catch(_){}}
  if(this.pc){this.pc.ondatachannel=this.pc.onconnectionstatechange=this.pc.oniceconnectionstatechange=null;try{this.pc.close();}catch(_){}}
  this.pc=null;this.channel=null;this._guard=null;this.session=null;this.remoteReady=false;this._status(failed?'failed':'closed',Object.hasOwn(messages,reason)?messages[reason]:messages.manual);this.onClose(reason);
 }
}

if(typeof module!=='undefined'&&module.exports)module.exports={EclipseLanPeer};
