"""CPU WebAudio PCM and non-modal encounter narration; no WebGL or FPS claim."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
bootstrap='''let audio=null,soundOn=true,state='playing',battle=null;
let localProfile={settings:{volume:1,music:.45}},p={x:0,z:0,motionSpeed:0,dashT:0,leap:0};
let journey={level:1},campaign={bossAwake:false},enemies=[],avatarRuntime={current:null};
let world={zoneAt:()=>"Cloître des cendres"};function trialActive(){return true;}
const camera={matrixWorld:{elements:[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]},updateMatrixWorld(){}};
'''
html='<div id="notice" hidden></div><button id="interact" hidden></button><script>'+bootstrap+'</script>'
html+='<script>'+(ROOT/'src/story-audio.js').read_text()+'</script><script>'+(ROOT/'src/encounter-presentation-v16.js').read_text()+'</script>'
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu','--disable-software-rasterizer'])
 page=browser.new_page(viewport={'width':1100,'height':760});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);run=page.evaluate
 run('''window.renderEncounterScore=async function(level,combat){
  audio=new OfflineAudioContext(2,48000*8.2,48000);soundscape=null;state='playing';soundOn=true;localProfile.settings={volume:1,music:.45};const s=initSoundscape();syncSoundscapeLevels(s);let maxVoices=0;
  scheduleEncounterScore(s,level,combat,0);const pauses=[];for(let i=1;i<=61;i++)pauses.push(audio.suspend(i*.1));const rendered=audio.startRendering();
  for(let i=0;i<pauses.length;i++){await pauses[i];if(i<59)scheduleEncounterScore(s,level,combat,audio.currentTime);else stopScoreVoices(s,audio.currentTime);maxVoices=Math.max(maxVoices,s.voices.size);await audio.resume();}
  const output=await rendered;let square=0,peak=0,crossings=0,tail=0;
  const d=output.getChannelData(0);for(let i=0;i<d.length;i++){square+=d[i]*d[i];peak=Math.max(peak,Math.abs(d[i]));if(i&&d[i]*d[i-1]<0)crossings++;if(i>48000*8.1)tail=Math.max(tail,Math.abs(d[i]));}
  return{level,combat,rms:Math.sqrt(square/d.length),peak,crossings,tail,maxVoices,remaining:s.voices.size,events:s.events,intensity:s.encounterScore.intensity,bars:s.encounterScore.bars};
 };void 0;''')
 music=[run('(level)=>renderEncounterScore(level,false)',level) for level in [1,2,3]]
 tension=run('renderEncounterScore(1,true)')
 for result in music+[tension]:
  assert .0005<result['rms']<.12 and .003<result['peak']<.85,result
  assert result['maxVoices']<=28 and result['remaining']==0 and result['events']>=13 and result['bars']>=2,result
  assert result['tail']<.001,result
 assert len({r['crossings'] for r in music})==3,music
 assert tension['intensity']>.97 and tension['events']>music[0]['events'],(tension,music[0])
 run('''window.renderEncounterSound=async function(kind,volume=1,x=8,count=1){
  audio=new OfflineAudioContext(2,48000*1.2,48000);soundscape=null;state='playing';soundOn=true;localProfile.settings={volume,music:0};const s=initSoundscape();syncSoundscapeLevels(s);
  let voice=null;for(let i=0;i<count;i++)voice=encounterSound(kind,{x,z:0});const atStart=s.sfxVoices.size,sourceCount=voice?.sources.length||0,output=await audio.startRendering();let peak=0,crossings=0;const energy=[0,0];
  for(let c=0;c<2;c++){const d=output.getChannelData(c);for(let i=0;i<d.length;i++){energy[c]+=d[i]*d[i];peak=Math.max(peak,Math.abs(d[i]));if(c===0&&i&&d[i]*d[i-1]<0)crossings++;}}
  return{kind,peak,crossings,energy,atStart,sourceCount,remaining:s.sfxVoices.size,created:s.sfxCreated,disposed:s.sfxDisposed,dropped:s.sfxDropped};
 };void 0;''')
 kinds=['bow_draw','bow_release','shade_reveal','ceramic_hit'];sounds=[run('(kind)=>renderEncounterSound(kind)',kind) for kind in kinds]
 for result in sounds:
  assert .0001<result['peak']<.85 and result['energy'][1]>result['energy'][0]*15,result
  assert result['remaining']==0 and result['created']==result['disposed']==1,result
  assert 2<=result['sourceCount']<=4,result
 assert len({r['crossings'] for r in sounds})==4,sounds
 half=run('renderEncounterSound("ceramic_hit",.5)');full=sounds[-1]
 assert .24<sum(half['energy'])/sum(full['energy'])<.26,(half,full)
 mute=run('renderEncounterSound("ceramic_hit",0)');assert mute['peak']==0 and mute['created']==0,mute
 dense=run('renderEncounterSound("bow_draw",1,8,100)');assert dense['atStart']==16 and dense['dropped']==84 and dense['created']==dense['disposed']==16,dense
 run('audio=new OfflineAudioContext(2,48000,48000);soundscape=null;state="playing";localProfile.settings={volume:1,music:0};var testScore=initSoundscape();scheduleEncounterScore(testScore,1,true,0);')
 assert run('testScore.voices.size===0&&testScore.events===0'),'Music zero must not keep scheduling inaudible notes'
 run('state="paused";');assert run('encounterSound("shade_reveal",{x:0,z:0})===null')
 # The presentation never changes simulation state, moves the hero or steals focus.
 run('state="playing";enemies=[{x:4,z:0,type:"archer",mode:"idle",dead:false}];window.beforeNarrative=JSON.stringify(p);for(let i=0;i<65;i++)updateEncounterPresentation(1/60);')
 assert run('encounterPresentationV16.current.id==="cloitre"&&!encounterPresentationV16.element.hidden&&state==="playing"&&JSON.stringify(p)===beforeNarrative')
 assert page.locator('#encounterV16').get_attribute('role')=='status'
 assert run('document.activeElement===document.body'),'Narrative must not take focus'
 run('enemies[0].mode="windup";updateEncounterPresentation(.016)');assert page.locator('#encounterV16').is_hidden(),'Warnings must keep the stage clear'
 run('enemies[0].mode="recover";document.querySelector("#notice").hidden=false;updateEncounterPresentation(.016)');assert page.locator('#encounterV16').is_hidden(),'Do not stack with existing clues'
 run('document.querySelector("#notice").hidden=true;updateEncounterPresentation(.016)')
 page.set_viewport_size({'width':390,'height':844});box=page.locator('#encounterV16').bounding_box();assert box and box['x']>=0 and box['x']+box['width']<=390 and box['y']>200 and box['y']+box['height']<620,box
 assert run('encounterPresentationV16.queue.length<=3&&[...encounterPresentationV16.seen].filter(x=>x==="archer").length===1')
 run('state="paused";updateEncounterPresentation(.016)');assert page.locator('#encounterV16').is_hidden()
 assert not errors,errors;browser.close()
report={'music':music,'tension':tension,'sounds':sounds,'scope':'CPU OfflineAudioContext signal and DOM; no WebGL, physical listening or hardware FPS claim'}
Path('/tmp/encounter-presentation-v16-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: three original chapter voicings, gradual combat layer, bounded voices, rendered stereo PCM, silence/cleanup, distinct local creature cues and non-modal contextual narration with clear warning/clue priority. CPU only.')
