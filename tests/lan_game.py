"""Full game synchronization through an explicitly simulated, in-memory channel.

This is NOT a real WebRTC, Wi-Fi, phone or latency test. The production protocol
validates every packet crossing the test bridge. Native transport is separately
exercised (or explicitly skipped for managed browser policy) by lan_peer.py.
GPU game contexts must be run serially by the parent agent.
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

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass


SDP = ('v=0\r\no=- 1 1 IN IP4 0.0.0.0\r\ns=-\r\nt=0 0\r\n'
       'm=application 9 UDP/DTLS/SCTP webrtc-datachannel\r\nc=IN IP4 0.0.0.0\r\n'
       'a=ice-ufrag:abcd\r\na=ice-pwd:abcdefghijklmnopqrstuvwxyz\r\n'
       'a=fingerprint:sha-256 ' + ':'.join(['AA'] * 32) + '\r\n'
       'a=setup:actpass\r\na=sctp-port:5000\r\n'
       'a=candidate:1 1 udp 2122260223 192.168.1.5 50000 typ host\r\n')

MEMORY_PEER = r'''sdp=>{
 window.memoryOut=[];window.NativeLanPeer=EclipseLanPeer;
 class InMemoryLanPeer {
  static supported(){return true;}
  constructor(options){this.options=options;this.role=null;this.session=null;this.closed=false;this.connected=false;this.seq=0;this.receiveClock=0;this.state='idle';window.memoryPeer=this;}
  begin(role,session){this.role=role;this.session=session;this.guard=EclipseLanProtocol.createGuard({role,session,now:()=>this.receiveClock});}
  async createOffer(){this.begin('host',EclipseLanProtocol.createSessionId());this.state='waiting-answer';this.options.onStatus({state:this.state,message:'TEST: invitation préparée, sans connexion native.'});return EclipseLanProtocol.createPairEnvelope('offer',this.session,{type:'offer',sdp});}
  async acceptOffer(raw){const offer=EclipseLanProtocol.parsePairEnvelope(raw,{kind:'offer'});this.begin('guest',offer.session);this.state='waiting-host';return EclipseLanProtocol.createPairEnvelope('answer',this.session,{type:'answer',sdp});}
  async acceptAnswer(raw){EclipseLanProtocol.parsePairEnvelope(raw,{kind:'answer',session:this.session});this.connect();}
  connect(){this.connected=true;this.state='connected';this.options.onStatus({state:this.state,message:'TEST: transport en mémoire, pas WebRTC.'});this.options.onOpen();}
  send(type,payload){if(!this.connected||this.closed)return false;const allowed=this.role==='host'?['hello','start','snapshot','pause','ping','bye']:['hello','ready','request','input','ping','bye'];if(!allowed.includes(type))return false;const packet=EclipseLanProtocol.createPacket(type,this.session,this.seq++,payload);memoryOut.push(EclipseLanProtocol.encodePacket(packet));return true;}
  receive(raw){if(this.closed)return;this.receiveClock+=50;const packet=this.guard.accept(raw);if(packet.type==='bye'){this.close('remote');return;}this.options.onPacket(packet);}
  close(reason='manual'){if(this.closed)return;this.closed=true;this.connected=false;this.state='closed';this.options.onStatus({state:this.state,message:'TEST: transport fermé.'});this.options.onClose(reason);}
 }
 EclipseLanPeer=InMemoryLanPeer;
}'''

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'docs')))
Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
        contexts = [browser.new_context(viewport={'width':1100,'height':760}), browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)]
        pages=[];errors=[];external=[]
        for context in contexts:
            context.add_init_script('requestAnimationFrame=()=>0')
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:external.append(r.url) if r.url.startswith('http') and not r.url.startswith('http://127.0.0.1:') else None)
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            page.wait_for_function('avatarRuntime.status==="ready"&&typeof initSessionUI==="function"',polling=50)
            page.select_option('#playMode','lan');page.evaluate(MEMORY_PEER,SDP);pages.append(page)
        host,guest=pages
        host.click('[data-hero=rempart]');guest.click('[data-hero=lame]')
        for page in pages:
            page.wait_for_function('!document.querySelector("#start").disabled',polling=50)
            assert page.locator('#playMode option').count()==3
            assert page.locator('#duelOpponentHero option').count()==10
            page.evaluate('soundOn=false;window.saveBefore={journey:JSON.stringify(localProfile.journey),run:localStorage.getItem(RUN_KEY),secret:JSON.stringify(localProfile.secret),completed:JSON.stringify(localProfile.completed)}')
        host.click('#lanCreate');host.wait_for_function('sessionUi.outgoing?.kind==="offer"',polling=25)
        assert host.evaluate('!lanSession.peer.connected&&!lanSession.started')
        invitation=host.evaluate('sessionUi.outgoing')
        with host.expect_download() as downloaded: host.click('#lanDownload')
        assert json.loads(Path(downloaded.value.path()).read_text())['session']==invitation['session']
        guest.set_input_files('#lanIncomingFile',{'name':'eclipse-invitation.json','mimeType':'application/json','buffer':json.dumps(invitation).encode()})
        guest.wait_for_function('sessionUi.outgoing?.kind==="answer"',polling=25)
        answer=guest.evaluate('sessionUi.outgoing')
        assert not guest.evaluate('lanSession.peer.connected')
        host.set_input_files('#lanIncomingFile',{'name':'eclipse-reponse.json','mimeType':'application/json','buffer':json.dumps(answer).encode()})
        host.wait_for_function('lanSession.peer.connected',polling=25)
        guest.evaluate('memoryPeer.connect()')
        for page in pages:page.evaluate('clearInterval(lanSession.timer);lanSession.timer=null')

        def pump(rounds=4):
            for _ in range(rounds):
                for source,destination in [(host,guest),(guest,host)]:
                    packets=source.evaluate('memoryOut.splice(0)')
                    if packets:destination.evaluate('packets=>{for(const packet of packets)memoryPeer.receive(packet)}',packets)

        pump()
        for page in pages:
            page.wait_for_function('!!lanSession.remote',polling=25)
            assert page.evaluate('document.querySelector("#lanOutgoingCode").value===""&&sessionUi.outgoing===null')
            page.click('#lanReady');page.wait_for_function('lanSession.localReady',polling=25)
        pump();host.wait_for_function('lanSession.remoteReady',polling=25)
        host.click('#lanStart');host.wait_for_function('state==="playing"&&battle?.kind==="lan-host"',polling=50)
        pump();guest.wait_for_function('state==="playing"&&battle?.kind==="lan-guest"',polling=50)
        host.evaluate('lanNetworkTick()');pump()
        assert guest.evaluate('lanSession.stats.receivedSnapshots>0&&localParty[0].heroId==="rempart"&&hero==="lame"')
        assert host.evaluate('localParty[0].heroId==="lame"')

        # Only intent crosses from the guest; the host owns positions and health.
        before=host.evaluate('localParty[0].x');guest.evaluate('joy.x=-1')
        for _ in range(24):
            guest.evaluate('for(let i=0;i<4;i++)updateLanGuest(1/60);lanNetworkTick()');pump(1)
            host.evaluate('for(let i=0;i<4;i++)update(1/60);lanNetworkTick()');pump(1)
        after=host.evaluate('localParty[0].x')
        assert after<before-1,(before,after)
        assert abs(guest.evaluate('p.x')-after)<1.8
        guest.evaluate('joy.x=0;p.hp=1;lanNetworkTick()');pump()
        host.evaluate('lanNetworkTick()');pump()
        assert guest.evaluate('p.hp===HERO_DEFS.lame.hp'),'A client-side health mutation must be overwritten by the host snapshot'
        assert not guest.evaluate('memoryPeer.send("snapshot",lanSession.snapshot)'),'The guest cannot publish an authoritative snapshot'

        # Pause clears held intents; a guest asks the host to resume.
        host.evaluate('pause("manual");lanNetworkTick()');pump()
        assert guest.evaluate('state==="paused"')
        assert host.evaluate('!localParty[0].networkInput?.fire')
        guest.evaluate('requestLanPause(false)');pump()
        assert host.evaluate('state==="playing"')
        host.evaluate('lanNetworkTick()');pump();assert guest.evaluate('state==="playing"')

        # Use the real source-timed opponent attack and damage rules, without AI.
        host.evaluate('resetHeroAt(0,-7);p.inv=0;var opponent=localParty[0];opponent.x=0;opponent.z=-5.4;opponent.vx=opponent.vz=0;opponent.inv=0;opponent.aim=0;opponent.attack=null;opponent.shot=0;opponent.downed=false;syncDuelProxy(opponent);lanNetworkTick()')
        pump();health=host.evaluate('p.hp');guest.evaluate('shooting=true')
        for _ in range(45):
            guest.evaluate('for(let i=0;i<4;i++)updateLanGuest(1/60);lanNetworkTick()');pump(1)
            host.evaluate('if(state==="playing")for(let i=0;i<4;i++)update(1/60);lanNetworkTick()');pump(1)
        assert host.evaluate('p.hp')<health,'An input-driven physical strike must cause actual authoritative damage'
        assert guest.evaluate('localParty[0].hp')==host.evaluate('p.hp')
        guest.evaluate('shooting=false')
        host.evaluate('if(!battle.ended)endBattleRound(1);lanNetworkTick()');pump()
        assert guest.evaluate('state==="won"&&battle.ended&&document.querySelector("#nextChapter").hidden')
        host.evaluate('resetDuelRound();lanNetworkTick()');pump()
        assert guest.evaluate('state==="playing"&&battle.round>=2')

        for page in pages:
            assert page.evaluate('JSON.stringify(localProfile.journey)===saveBefore.journey&&localStorage.getItem(RUN_KEY)===saveBefore.run&&JSON.stringify(localProfile.secret)===saveBefore.secret&&JSON.stringify(localProfile.completed)===saveBefore.completed')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        host.evaluate('closeLanSession("manual")');pump()
        assert guest.evaluate('state==="paused"&&document.querySelector("#resume").hidden&&!lanSession.peer.connected')
        for page in pages:assert page.evaluate('sessionUi.outgoing===null&&document.querySelector("#lanOutgoingCode").value===""')
        assert not errors,errors
        assert not external,external
        Path('/tmp/royaumes-lan-game-report.json').write_text(json.dumps({'transport':'in-memory test bridge','native_rtc_validated':False,'physical_phones_validated':False,'checks':['file UI','role-bounded protocol','input-driven host movement','guest cannot assign health','shared pause and resume','physical strike damage','round transition','disconnect','save preservation','PC and portrait layout','no external API request']},indent=2)+'\n')
        browser.close()
    print('PASS GAME SIMULATION: two game contexts, manually exchanged files, validated in-memory packets, host-authoritative input/damage, pause/round/disconnect and saves. NOT native WebRTC, Wi-Fi or physical phones.')
finally:
    server.shutdown();server.server_close()
