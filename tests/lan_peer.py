"""Two real browser contexts exchange manual files and encrypted data channels.

No game, media capture or WebGL renderer. Uses CPU-only Chromium; it does not
stand for two physical phones, router compatibility, latency or throughput.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import sys as _check_sys
from pathlib import Path as _CheckPath
_check_sys.path.insert(0,str(_CheckPath(__file__).resolve().parents[1]/'scripts'))
from browser_checks import install_csp_wait
install_csp_wait()
import json
import subprocess
import sys

UNIT = r'''
const fs=require("fs"),vm=require("vm"),assert=require("assert");
globalThis.crypto=require("crypto").webcrypto;
const fp=Array(32).fill("AB").join(":"),description=kind=>({type:kind,sdp:["v=0","o=- 1 2 IN IP4 127.0.0.1","s=-","t=0 0","a=group:BUNDLE 0","m=application 9 UDP/DTLS/SCTP webrtc-datachannel","c=IN IP4 0.0.0.0","a=mid:0","a=ice-ufrag:abcd","a=ice-pwd:abcdefghijklmnopqrstuv","a=fingerprint:sha-256 "+fp,"a=setup:"+(kind==="offer"?"actpass":"active"),"a=sctp-port:5000","a=candidate:1 1 udp 2122260223 192.168.1.5 54400 typ host","a=end-of-candidates",""] .join("\r\n")});
class Channel{constructor(){this.label="eclipse-lan-v1";this.protocol="eclipse/1";this.ordered=true;this.negotiated=false;this.maxRetransmits=null;this.maxPacketLifeTime=null;this.readyState="connecting";this.bufferedAmount=0;this.sent=[];}send(raw){this.sent.push(raw);}close(){this.readyState="closed";this.onclose?.();}}
class FakeRTC{constructor(config){this.config=config;this.iceGatheringState="complete";this.signalingState="stable";this.connectionState=this.iceConnectionState="new";FakeRTC.created++;}createDataChannel(){this.channel=new Channel();return this.channel;}async createOffer(){return description("offer");}async createAnswer(){return description("answer");}async setLocalDescription(d){this.localDescription=d;this.signalingState=d.type==="offer"?"have-local-offer":"stable";}async setRemoteDescription(d){this.remoteDescription=d;this.signalingState=d.type==="offer"?"have-remote-offer":"stable";}addEventListener(){}removeEventListener(){}close(){this.connectionState=this.iceConnectionState="closed";}}FakeRTC.created=0;
globalThis.RTCPeerConnection=FakeRTC;
vm.runInThisContext(fs.readFileSync(process.argv[1]+"/src/lan-protocol.js","utf8"));
vm.runInThisContext(fs.readFileSync(process.argv[1]+"/src/lan-peer.js","utf8"));
const peers=[];function fresh(){const events=[],packets=[],reasons=[],peer=new EclipseLanPeer({onStatus:s=>events.push(s),onPacket:p=>packets.push(p),onClose:r=>reasons.push(r)});const entry={peer,events,packets,reasons};peers.push(entry);return entry;}
function opened(peer){peer.channel.readyState="open";peer.channel.onopen();}
(async()=>{
 const initialSecureContext=globalThis.isSecureContext;globalThis.isSecureContext=false;assert(!EclipseLanPeer.supported());const insecure=fresh(),initialCount=FakeRTC.created;await assert.rejects(()=>insecure.peer.createOffer(),/HTTPS/);assert(FakeRTC.created===initialCount);globalThis.isSecureContext=initialSecureContext;
 let host=fresh(),offer=await host.peer.createOffer();assert(host.peer.state==="invitation"&&!host.peer.connected);assert.deepStrictEqual(host.peer.pc.config.iceServers,[]);
 const bad={...offer,expires:0},guest=fresh(),created=FakeRTC.created;await assert.rejects(()=>guest.peer.acceptOffer(bad));assert(FakeRTC.created===created&&guest.peer.pc===null,"Invalid invitation must fail before an RTC object");
 const answer=await guest.peer.acceptOffer(offer);await host.peer.acceptAnswer(answer);opened(host.peer);guest.peer.pc.ondatachannel({channel:new Channel()});opened(guest.peer);
 assert(host.peer.connected&&guest.peer.connected);assert(host.peer.send("hello",{hero:"rempart",name:"Hôte"}));assert(!host.peer.send("input",{x:0,z:0,aim:0,fire:false,dash:false,power:false,extra:false,interact:false}));
 assert(!guest.peer.send("snapshot",{}));const first=host.peer.channel.sent[0];assert(JSON.parse(first).type==="hello");assert(guest.peer.send("ready",{ready:true}));host.peer.channel.onmessage({data:guest.peer.channel.sent[0]});assert(host.peer.remoteReady&&host.packets[0].type==="ready");
 const before=host.peer._seq;host.peer.channel.bufferedAmount=128*1024;assert(!host.peer.send("hello",{hero:"lame",name:"Hôte"}));assert(host.peer._seq===before&&host.peer.getStats().dropped===1);host.peer.channel.bufferedAmount=0;
 const session=host.peer.session,malicious=EclipseLanProtocol.encodePacket(EclipseLanProtocol.createPacket("pause",session,1,{paused:true}));host.peer.channel.onmessage({data:malicious});assert(host.peer.closed&&host.peer.state==="failed"&&host.reasons[0]==="protocol");assert(host.peer.pc===null&&host.peer.channel===null&&host.peer.session===null&&host.peer._timers.size===0&&host.peer._heartbeat===null);
 guest.peer.close();host=fresh();offer=await host.peer.createOffer();await host.peer.acceptAnswer(EclipseLanProtocol.createPairEnvelope("answer",host.peer.session,description("answer"),{expires:offer.expires}));opened(host.peer);const accepted=EclipseLanProtocol.encodePacket(EclipseLanProtocol.createPacket("ready",host.peer.session,1,{ready:true}));host.peer.channel.onmessage({data:accepted});host.peer.channel.onmessage({data:accepted});assert(host.peer.closed&&host.reasons[0]==="protocol","Replayed data must close rather than apply twice");
 host=fresh();offer=await host.peer.createOffer();await host.peer.acceptAnswer(EclipseLanProtocol.createPairEnvelope("answer",host.peer.session,description("answer"),{expires:offer.expires}));opened(host.peer);host.peer.channel.onmessage({data:" ".repeat(65537)});assert(host.peer.closed&&host.peer.getStats().rejected===1,"Receive byte cap applies before JSON work");
 host=fresh();await host.peer.createOffer();host.peer._armExpiry(Date.now()-1);await new Promise(r=>setTimeout(r,5));assert(host.peer.closed&&host.reasons[0]==="expired");
 host=fresh();offer=await host.peer.createOffer();await host.peer.acceptAnswer(EclipseLanProtocol.createPairEnvelope("answer",host.peer.session,description("answer"),{expires:offer.expires}));opened(host.peer);host.peer._lastReceive=performance.now()-30000;await new Promise(r=>setTimeout(r,1100));assert(host.peer.closed&&host.reasons[0]==="stale","Heartbeat timeout must run outside game update");
 for(const {peer}of peers){peer.close();assert(peer.pc===null&&peer.channel===null&&peer.session===null&&peer._timers.size===0&&peer._heartbeat===null);const stats=JSON.stringify(peer.getStats());assert(!/sdp|fingerprint|session/i.test(stats));}
 console.log("PASS UNIT: manual pairing state/roles, input authority, replay and byte rejection, bounded send queue, expiry, stale heartbeat and complete cleanup using a deterministic RTC test double. This is not a real transport/DTLS result.");
})().catch(e=>{for(const {peer}of peers)peer.close();console.error(e.stack);process.exitCode=1;});
'''

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(['node','-e',UNIT,str(ROOT)],check=True,cwd=ROOT)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self):
        if self.path.split('?')[0] != '/':
            self.send_response(404); self.end_headers(); return
        data=b'<!doctype html><meta charset="utf-8"><title>LAN CPU transport test</title>'
        self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)

server=ThreadingHTTPServer(('127.0.0.1',0), Quiet)
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu','--disable-software-rasterizer'])
        contexts=[browser.new_context(viewport={'width':1280,'height':800}),browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)]
        pages=[]; errors=[]; external=[]
        for context in contexts:
            page=context.new_page(); page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda req:external.append(req.url) if not req.url.startswith('http://127.0.0.1:') else None)
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            page.add_script_tag(content=(ROOT/'src/lan-protocol.js').read_text())
            page.add_script_tag(content=(ROOT/'src/lan-peer.js').read_text())
            page.evaluate('''()=>{window.mediaCalls=0;window.apiCalls=0;window.fetch=()=>{apiCalls++;throw Error('Unexpected API call')};if(navigator.mediaDevices)navigator.mediaDevices.getUserMedia=()=>{mediaCalls++;throw Error('Unexpected capture')};window.received=[];window.events=[];window.closeReasons=[];window.newPeer=()=>{window.peer=new EclipseLanPeer({onPacket:p=>received.push(p),onStatus:s=>events.push(s),onClose:r=>closeReasons.push(r)});};newPeer();}''')
            pages.append(page)
        host,guest=pages
        def connect():
            for page in pages:page.evaluate('if(peer.pc)peer.close();received=[];events=[];closeReasons=[];newPeer()')
            invitation=host.evaluate('peer.createOffer()')
            assert invitation['kind']=='offer'
            assert host.evaluate('peer.pc.getConfiguration().iceServers.length===0&&peer.pc.getSenders().length===0')
            response=guest.evaluate('(invitation)=>peer.acceptOffer(JSON.stringify(invitation))',invitation)
            assert response['kind']=='answer' and response['session']==invitation['session']
            host.evaluate('(response)=>peer.acceptAnswer(JSON.stringify(response))',response)
            for page in pages:page.wait_for_function('peer.connected===true&&peer.channel.readyState==="open"',timeout=30000,polling=25)
            assert host.evaluate('peer.role==="host"&&peer.channel.ordered')
            assert guest.evaluate('peer.role==="guest"&&peer.channel.maxRetransmits===null&&peer.channel.maxPacketLifeTime===null')
            return invitation

        # Probe native ICE without changing browser policy or candidate privacy.
        # Managed Chrome can intentionally prohibit all direct, non-proxied ICE.
        native=host.evaluate('''async()=>{const pc=new RTCPeerConnection({iceServers:[]});pc.createDataChannel('probe');await pc.setLocalDescription(await pc.createOffer());await new Promise(resolve=>{if(pc.iceGatheringState==='complete')return resolve();pc.onicegatheringstatechange=()=>pc.iceGatheringState==='complete'&&resolve();setTimeout(resolve,10000);});const count=pc.localDescription.sdp.split(/\\r?\\n/).filter(l=>l.startsWith('a=candidate:')).length;pc.close();return{candidateCount:count,browser:navigator.userAgent};}''')
        if native['candidateCount']==0:
            result=host.evaluate('''async()=>{try{await peer.createOffer();return false}catch(_){return peer.closed&&peer.state==='failed'&&peer.pc===null&&peer.channel===null&&peer._timers.size===0&&peer._heartbeat===null&&closeReasons.includes('gather')}}''')
            assert result,'No usable local candidate must stop the invitation and clean up'
            assert all(page.evaluate('mediaCalls===0&&apiCalls===0') for page in pages)
            assert not external,external
            assert not errors,errors
            report={'module_unit':'PASS','native_no_candidate_handling':'PASS','direct_roundtrip':'SKIP','reason':'Native browser produced zero ICE candidates. Managed policy may prohibit direct non-proxied WebRTC; no policy or privacy setting was changed.','native_candidate_count':0,'browser':native['browser'],'physical_devices_tested':False,'external_requests':len(external)}
            Path('/tmp/royaumes-lan-transport-report.json').write_text(json.dumps(report,indent=2)+'\n')
            for context in contexts:context.close()
            browser.close()
            print('PASS: real browser with no local candidates rejects invitation, reports failure and cleans up without API/media calls.')
            print('SKIP DIRECT RTC: native ICE produced no candidates under managed browser policy; DTLS round-trip and physical phones remain unverified.')
            raise SystemExit(1 if '--require-direct' in sys.argv else 0)

        invitation=connect()
        assert host.evaluate('peer.send("hello",{name:"Hôte",hero:"colosse"})')
        assert guest.evaluate('peer.send("hello",{name:"Invité",hero:"tisseuse"})')
        assert guest.evaluate('peer.send("ready",{ready:true})')
        assert guest.evaluate('peer.send("input",{x:.5,z:-.25,aim:1.2,fire:true,dash:false,power:false,extra:false,interact:false})')
        host.wait_for_function('received.some(p=>p.type==="input")&&peer.remoteReady',polling=25)
        assert host.evaluate('received.find(p=>p.type==="input").payload.x===.5')
        assert host.evaluate('peer.send("start",{seed:123,round:1})')
        snapshot={'tick':12,'time':88.5,'phase':'playing','round':1,'wins':[0,0],'actors':[{'slot':0,'hero':'colosse','x':-9,'z':-7,'vx':0,'vz':0,'aim':0,'hp':190,'max':190,'downed':False},{'slot':1,'hero':'tisseuse','x':9,'z':-7,'vx':0,'vz':0,'aim':0,'hp':105,'max':105,'downed':False}],'bullets':[],'effects':[{'id':1,'kind':'cover','owner':0,'x':0,'z':-7,'r':2,'life':4,'color':'#abcdef','boxes':[{'x':1,'z':-7,'w':.9,'d':.9}]}]}
        assert host.evaluate('(state)=>peer.send("snapshot",state)',snapshot)
        guest.wait_for_function('received.some(p=>p.type==="snapshot")&&received.some(p=>p.type==="start")',polling=25)
        assert guest.evaluate('received.find(p=>p.type==="snapshot").payload.effects[0].boxes[0].w===.9')
        assert not guest.evaluate('(state)=>peer.send("snapshot",state)',snapshot),'Sender must refuse foreign authority'
        assert not host.evaluate('peer.send("input",{x:0,z:0,aim:0,fire:false,dash:false,power:false,extra:false,interact:false})')
        assert guest.evaluate('(()=>{const max=peer._maxBuffer;peer._maxBuffer=1;const sent=peer.send("ready",{ready:true});peer._maxBuffer=max;return !sent&&peer.getStats().dropped===1;})()'),'Backpressure prevents growth instead of queueing more data'
        # A full second of idle still carries heartbeats outside any game update.
        host.wait_for_function('peer.getStats().received>=5',timeout=4000,polling=25)
        assert host.evaluate('peer.connected') and guest.evaluate('peer.connected')
        stats=host.evaluate('peer.getStats()')
        assert not any(key in json.dumps(stats).lower() for key in ['sdp','fingerprint','session'])
        assert all(page.evaluate('mediaCalls===0&&apiCalls===0') for page in pages)
        assert not external,external
        host.evaluate('peer.close()');guest.wait_for_function('peer.closed',polling=25)
        assert all(page.evaluate('peer.pc===null&&peer.channel===null&&peer.session===null&&peer._timers.size===0&&peer._heartbeat===null') for page in pages)

        # Invalid invitation rejection happens before constructing an RTC peer.
        for page in pages:page.evaluate('newPeer()')
        bad={**invitation,'expires':0}
        assert guest.evaluate('async raw=>{try{await peer.acceptOffer(raw);return false}catch(_){return peer.pc===null}}',bad)
        connect()
        # Bypass the sender helper to model a malicious peer: role authorization
        # must still happen on receipt and stop the connection.
        guest.evaluate('(state)=>peer.channel.send(EclipseLanProtocol.encodePacket(EclipseLanProtocol.createPacket("snapshot",peer.session,peer._seq++,state)))',snapshot)
        host.wait_for_function('peer.closed&&peer.state==="failed"',polling=25)
        assert host.evaluate('closeReasons.includes("protocol")&&peer.getStats().rejected===1')
        connect()
        guest.evaluate('clearInterval(peer._heartbeat);peer._heartbeat=null')
        host.evaluate('peer._lastReceive=performance.now()-30000')
        host.wait_for_function('peer.closed&&closeReasons.includes("stale")',timeout=4000,polling=25)
        for page in pages:page.evaluate('peer.close()')
        assert not errors,errors
        for context in contexts:context.close()
        browser.close()
    Path('/tmp/royaumes-lan-transport-report.json').write_text(json.dumps({'module_unit':'PASS','direct_roundtrip':'PASS','native_candidate_count':native['candidateCount'],'physical_devices_tested':False,'external_requests':len(external)},indent=2)+'\n')
    print('PASS: two real CPU browser contexts pair manually over local-only ICE; DTLS datachannel exchanges input/state, all-hero effects, authorization, bounded send queue, heartbeats, stale/invalid shutdown and full cleanup. No media/API calls; no physical-phone or performance claim.')
finally:
    server.shutdown();server.server_close()
