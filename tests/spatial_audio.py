"""Actual stereo PCM, master mute, bounded SFX and pause/footstep transport.

CPU-only Chromium: loads the audio source directly and uses OfflineAudioContext;
no WebGL renderer, speaker output, remote assets or visual quality assertion.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
bootstrap='''
let audio=null,soundOn=true,state='playing';
let localProfile={settings:{volume:1,music:0}};
let p={x:0,z:0,motionSpeed:2,dashT:0,leap:0};
let journey={level:1},campaign={bossAwake:false},battle=null,enemies=[];
let avatarRuntime={current:null};
const camera={matrixWorld:{elements:[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]},updateMatrixWorld(){}};
'''
source=(ROOT/'src/story-audio.js').read_text()
html='<script>'+bootstrap+'</script><script>'+source+'</script>'
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu','--disable-software-rasterizer']);page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);run=page.evaluate
 run('''window.audioCase=async function({kind='shot',position=null,volume=1,right=1,count=1,tone=false}={}){
  audio=new OfflineAudioContext(2,48000*.6,48000);soundscape=null;state='playing';soundOn=true;localProfile.settings.volume=volume;localProfile.settings.music=0;journey.level=1;p={x:0,z:0,motionSpeed:2,dashT:0,leap:0};camera.matrixWorld.elements[0]=right;avatarRuntime.current=null;
  initSoundscape();for(let i=0;i<count;i++)if(tone)playTone(440,.15,'sine',.025,position);else playWorldSound(kind,1,position);
  const active=soundscape.sfxVoices.size,peakActive=soundscape.sfxPeak,dropped=soundscape.sfxDropped,output=await audio.startRendering(),energy=[0,0],late=[0,0];let peak=0,crossings=0;
  for(let c=0;c<2;c++){const d=output.getChannelData(c);for(let i=0;i<d.length;i++){energy[c]+=d[i]*d[i];if(i>48000*.31)late[c]+=d[i]*d[i];peak=Math.max(peak,Math.abs(d[i]));if(c===0&&i>0&&d[i]*d[i-1]<0)crossings++;}}
  return{energy,late,peak,crossings,active,peakActive,dropped,remaining:soundscape.sfxVoices.size,created:soundscape.sfxCreated,disposed:soundscape.sfxDisposed};
 };void 0;''')
 right=run("audioCase({position:{x:8,z:0}})");left=run("audioCase({position:{x:-8,z:0}})");turned=run("audioCase({position:{x:8,z:0},right:-1})")
 assert right['energy'][1]>right['energy'][0]*15,right
 assert left['energy'][0]>left['energy'][1]*15,left
 assert turned['energy'][0]>turned['energy'][1]*15,turned
 near=run("audioCase({position:{x:2,z:0}})");far=run("audioCase({position:{x:20,z:0}})")
 assert sum(near['energy'])>sum(far['energy'])*15,(near,far)
 full=run('audioCase({volume:1})');half=run('audioCase({volume:.5})');muted=run('audioCase({volume:0})')
 ratio=sum(half['energy'])/sum(full['energy']);assert .24<ratio<.26,ratio
 assert muted['peak']==0 and muted['created']==0,muted
 tone=run('audioCase({tone:true})');tone_half=run('audioCase({tone:true,volume:.5})');tone_muted=run('audioCase({tone:true,volume:0})')
 assert .24<sum(tone_half['energy'])/sum(tone['energy'])<.26,(tone,tone_half)
 assert tone_muted['peak']==0 and tone_muted['created']==0,tone_muted
 # Muting the master also silences already sounding notes and their reverb tail.
 active_mute=run("""async()=>{audio=new OfflineAudioContext(2,48000*.7,48000);soundscape=null;state='playing';localProfile.settings.volume=1;localProfile.settings.music=.25;initSoundscape();updateSoundscape(.016);playWorldSound('threat');const paused=audio.suspend(.12),rendered=audio.startRendering();await paused;localProfile.settings.volume=0;updateSoundscape(.016);await audio.resume();const output=await rendered;let before=0,after=0;for(let c=0;c<2;c++){const d=output.getChannelData(c);for(let i=0;i<d.length;i++){if(i<48000*.1)before=Math.max(before,Math.abs(d[i]));if(i>48000*.15)after=Math.max(after,Math.abs(d[i]));}}return{before,after};}""")
 assert active_mute['before']>.001 and active_mute['after']==0,active_mute
 threat=run("audioCase({kind:'threat'})");impact=run("audioCase({kind:'impact'})")
 assert sum(threat['late'])>sum(impact['late'])*100+1e-8,(threat,impact)
 assert threat['crossings']!=impact['crossings'],(threat,impact)
 dense=run('audioCase({count:100})');assert dense['active']==16 and dense['peakActive']==16 and dense['dropped']==84,dense
 for result in [right,left,turned,near,far,full,half,muted,tone,tone_half,tone_muted,threat,impact,dense]:
  assert result['remaining']==0 and result['created']==result['disposed'],result
  assert result['peak']<.95,result
 # A priority warning can replace a footstep; repeated equal priority cannot grow the budget.
 run('audio=new OfflineAudioContext(2,48000,48000);soundscape=null;localProfile.settings.volume=1;initSoundscape();for(let i=0;i<16;i++)playWorldSound("step");playWorldSound("threat");')
 assert run('soundscape.sfxVoices.size===16&&soundscape.sfxCreated===17&&[...soundscape.sfxVoices].some(v=>v.priority===3)')
 run('audio.startRendering()')
 # Pause invalidates future notes and previous step distance; resuming cannot play a teleport step.
 run('''audio=new OfflineAudioContext(2,48000,48000);soundscape=null;state='playing';localProfile.settings.volume=1;initSoundscape();updateSoundscape(.016);soundscape.stepDistance=.79;soundscape.lastStep={x:0,z:0};scoreVoice(220,.3,.5,.05);window.oldSources=[...soundscape.voices];state='paused';updateSoundscape(.016);''')
 assert run('soundscape.voices.size===0&&soundscape.lastStep===null&&soundscape.stepDistance===0&&soundscape.musicLevel===0&&soundscape.sfxLevel===0&&soundscape.next===audio.currentTime')
 run('state="playing";p.x=10;updateSoundscape(.016)');assert run('soundscape.stepDistance===0&&soundscape.lastStep.x===10')
 # Calibrated Lame sounds follow actual contact serials, not accumulated travel.
 run('''avatarRuntime.current={motionCalibration:{version:1},motionFootstepSerial:4};soundscape.stepDistance=99;updateSoundscape(.016);window.stepCount=soundscape.sfxCreated;avatarRuntime.current.motionFootstepSerial=5;updateSoundscape(.016);''')
 assert run('soundscape.sfxCreated===stepCount+1&&soundscape.stepDistance===0')
 run('updateSoundscape(.016)');assert run('soundscape.sfxCreated===stepCount+1')
 run('avatarRuntime.current.motionFootstepSerial=0;updateSoundscape(.016)');assert run('soundscape.sfxCreated===stepCount+1')
 run('state="paused";updateSoundscape(.016);state="playing";avatarRuntime.current.motionFootstepSerial=15;updateSoundscape(.016)');assert run('soundscape.sfxCreated===stepCount+1')
 assert not errors,errors;browser.close()
print('PASS: rendered stereo follows camera orientation and distance; single master volume, exact zero mute for SFX/UI; distinct threat/impact, bounded voices and cleanup; pause clears queue and stale steps; calibrated contact-driven footsteps. CPU-only audio, not a listening or mobile-performance claim.')
