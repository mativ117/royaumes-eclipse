"""Narrative presentation and actual WebAudio signal; no claim of recorded orchestral sound."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content('<script>requestAnimationFrame=()=>0</script>'+(ROOT/'docs/index.html').read_text());page.wait_for_function('avatarRuntime.status==="ready"',polling=50);run=page.evaluate
 assert run('document.documentElement.scrollWidth<=innerWidth')
 assert 'soleil noir' in page.locator('#storyMenuText').text_content()
 page.click('#storyMenuOpen');assert run('state==="chronicle"&&storyReturn==="menu"')
 page.click('[data-story-chapter="3"]');assert page.locator('#chronicleEnding').is_hidden()
 page.keyboard.press('Escape');assert run('state==="menu"')
 page.click('#start');run('p.inv=999;updateSoundscape(.1)')
 assert run('soundscape.events>=4&&soundscape.level===1&&soundscape.voices.size>0')
 run('var beforeStory=t;joy.x=1;openChronicle();frame(performance.now()+100)')
 assert run('state==="chronicle"&&t===beforeStory&&joy.x===0')
 assert run('document.documentElement.scrollWidth<=innerWidth')
 page.keyboard.press('Tab');page.keyboard.press('Escape');assert run('state==="playing"&&joy.x===0')
 run('enterChapter(2);updateSoundscape(.1)');assert run('soundscape.level===2&&soundscape.beat>0')
 run("playWorldSound('step');playWorldSound('shot');playWorldSound('blade');playWorldSound('impact');var eventCount=soundscape.events;pause();updateSoundscape(.1)");assert run('soundscape.events===eventCount&&soundscape.musicLevel===0&&soundscape.sfxLevel===0')
 # Render the instruments, room convolution and limiter into PCM, without speakers.
 result=run('''async()=>{await audio.close();audio=new OfflineAudioContext(2,48000*3,48000);soundscape=null;initSoundscape();scoreVoice(110,0,2.4,.12,'triangle');scoreVoice(164.81,.2,1.8,.07);scoreVoice(220,.4,1.6,.06);const output=await audio.startRendering();let square=0,peak=0,tail=0;const d=output.getChannelData(0);for(let i=0;i<d.length;i++){square+=d[i]*d[i];peak=Math.max(peak,Math.abs(d[i]));if(i>96000)tail+=Math.abs(d[i]);}return{rms:Math.sqrt(square/d.length),peak,tail,voices:soundscape.voices.size};}''')
 assert .005<result['rms']<.3 and .015<result['peak']<.95 and result['tail']>1 and result['voices']==0,result
 assert not errors,errors
 b.close()
print('PASS: chapter premise, spoiler-aware chronicle, Escape/focus/viewport, paused simulation, chapter score changes, pause scheduling and rendered stereo PCM with reverb/limiter.')
