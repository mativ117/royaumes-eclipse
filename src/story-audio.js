'use strict';
const STORY_CHAPTERS={
 1:{eyebrow:'I · LA VOIX SOUS LA CENDRE',title:'Ce que la nuit n’a pas encore pris.',premise:'Le soleil noir ne tue pas les royaumes : il efface leurs noms. Les routes deviennent des impasses, les visages des ombres. Dans la Cathédrale, un carillon retient encore la mémoire du monde.',purpose:'Retrouvez sa voix et guidez l’âme égarée jusqu’à elle. Sans ce premier souvenir, aucune route ne mènera à l’aube.',beats:['Un serment donne de la force, mais exige un prix. Choisissez celui avec lequel vous pourrez vivre.','Une âme erre à l’écart des grandes nefs. Elle ne demande pas un vainqueur : elle attend quelqu’un qui reste à ses côtés.','Le Carillon ne répond pas à la force. Les signes de la fresque gardent la mémoire de son chant.','Les Archives et la Forge ont chacune conservé un fragment de vérité. Réunissez ce que la Cathédrale a séparé.','Le Veilleur protège une promesse si ancienne qu’il en a oublié le sens. Ouvrir son cœur est le dernier passage.'],ending:'Le Carillon prononce un nom. Puis un autre. L’âme cesse de trembler : au-delà de la porte, un jardin se souvient encore de ceux qui l’ont gardé.'},
 2:{eyebrow:'II · LES GARDIENS SANS NOM',title:'On ne chasse pas une couronne.',premise:'Les Souverains protégeaient autrefois le jardin. Depuis l’Éclipse, ils ne reconnaissent plus ceux qu’ils défendent. Leur colère a pris racine dans les pierres.',purpose:'Suivez leurs traces, comprenez leurs faiblesses et rendez au jardin son passage. Un colosse vous attend de l’autre côté.',beats:['Deux traces demeurent : le fer et la pluie. Le jardin n’offre pas le même chemin à chacun.','Les gardiens défendent des souvenirs brisés. Leur préparation révèle l’instant où votre force peut porter.','Chaque signe retrouvé ajoute une voix au jardin. Écoutez avant d’appeler.','Le dernier gardien veille devant l’Observatoire. Sa charge le protège ; son épuisement vous laisse une ouverture.','Le Souverain change le terrain pour ne plus perdre ce qu’il protège. Gardez une issue, même lorsque son cœur se découvre.','Le jardin retrouve son nom. Il faut maintenant transporter son aube là où la nuit prend fin.'],ending:'Les racines desserrent leur étreinte. Sous le jardin, quelque chose d’immense respire : le dernier porteur d’aube vient de s’éveiller.'},
 3:{eyebrow:'III · LE DERNIER PORTEUR',title:'L’aube ne viendra pas seule.',premise:'Un peuple a bâti sa dernière demeure sur le dos d’un colosse. Il traverse la mer de cendre avec, dans sa poitrine, la lumière que le monde a réussi à sauver.',purpose:'Réparez ses liens, choisissez votre route et protégez son cœur jusqu’au dernier horizon. Votre victoire se mesure à ce qui arrive avec vous.',beats:['Le colosse avance, mais ses liens cèdent. Ce qui porte tout un peuple doit aussi être soutenu.','Le couchant et l’orage ouvrent deux routes. Le passage choisi fera partie de votre voyage.','À l’escale, chaque don engage la suite. Prenez le temps de lire ce que vous emportez.','Le cœur est exposé. Restez assez proche pour le défendre, assez mobile pour ne pas tomber avec lui.','Le Mange-Aube ne veut pas votre vie : il veut la lumière que vous transportez. Laissez-lui le moins d’espace possible.','Le dernier horizon est ouvert. Ramenez le colosse et ceux qu’il porte de l’autre côté.'],ending:'Les lanternes s’éteignent parce qu’on n’en a plus besoin. Derrière le colosse, les dunes restent noires. Devant lui, pour la première fois, quelqu’un peut nommer le matin.'}
};
let storyReturn='menu',storyFocus=null,storyDisplayed=0;
function storyProgress(level){if(localProfile.completed.includes(level))return STORY_CHAPTERS[level].beats.length-1;if(level!==journey.level)return 0;if(level>1)return Math.min(journey.step,STORY_CHAPTERS[level].beats.length-1);const q=campaign?.trials;return !boon?0:!q?.escort.done?1:!q.bells.done?2:!q.archive||!q.forge.done?3:4;}
function renderStory(level){storyDisplayed=level;const data=STORY_CHAPTERS[level];$('#chronicleEyebrow').textContent=data.eyebrow;$('#chronicleTitle').textContent=data.title;$('#chroniclePremise').textContent=data.premise;$('#chroniclePurpose').textContent=data.purpose;const notes=$('#chronicleNotes');notes.replaceChildren();for(const text of data.beats.slice(0,storyProgress(level)+1)){const p=document.createElement('p');p.textContent=text;notes.append(p);}$('#chronicleEnding').hidden=!localProfile.completed.includes(level);$('#chronicleEnding').textContent=data.ending;for(const button of document.querySelectorAll('[data-story-chapter]'))button.setAttribute('aria-pressed',String(Number(button.dataset.storyChapter)===level));}
function openChronicle(){if(!['menu','playing','paused'].includes(state))return;storyReturn=state;storyFocus=document.activeElement;clearInputs();state='chronicle';updateSoundscape(0);$('#mobile').classList.remove('playing');renderStory(storyReturn==='menu'?Number($('#chapterSelect').value):journey.level);$('#chronicle').hidden=false;$('#chronicleClose').focus();}
function closeChronicle(){if(state!=='chronicle')return;$('#chronicle').hidden=true;state=storyReturn;clearInputs();if(state==='playing')$('#mobile').classList.add('playing');last=performance.now();storyFocus?.focus();}
function updateStoryMenu(){const data=STORY_CHAPTERS[Number($('#chapterSelect').value)||1];$('#storyMenuTitle').textContent=data.title;$('#storyMenuText').textContent=data.premise;}
function initStoryPresentation(){
 const style=document.createElement('style');style.textContent='.story-premise{border-left:2px solid #d9964d;padding:2px 0 2px 18px;margin:22px 0;max-width:740px}.story-premise h2{font:26px Georgia;margin:0 0 10px;color:#ffd39a}.story-premise p{font-size:15px;line-height:1.6;color:#cfc0ac}.chronicle-panel{max-width:760px;width:100%;max-height:85dvh;overflow:auto;padding:clamp(20px,4vw,45px);background:#100e13f5;border:1px solid #9e7045;border-radius:12px}.chronicle-panel h2{font:clamp(30px,5vw,52px)/1.15 Georgia;color:#ffcf90}.chronicle-panel p{line-height:1.8}.chronicle-panel nav{display:flex;flex-wrap:wrap;gap:8px}.chronicle-panel nav button{background:#211a20;border:1px solid #6c513a;color:#dfcdb1;padding:10px 14px;border-radius:6px;font:inherit;cursor:pointer}.chronicle-panel button:focus-visible{outline:2px solid #ffbf76;outline-offset:3px}.chronicle-panel button[aria-pressed=true]{border-color:#ffc17b;color:#ffc17b}.chronicle-notes{border-top:1px solid #604632;margin-top:24px}.story-purpose{color:#ffd39a}.story-ending{font:22px/1.6 Georgia!important;color:#ffc17b}#chronicle{z-index:35}';document.head.append(style);
 const premise=document.createElement('section');premise.className='story-premise';premise.innerHTML='<h2 id="storyMenuTitle"></h2><p id="storyMenuText"></p><button id="storyMenuOpen" class="secondary">Comprendre le voyage</button>';$('#intro').after(premise);
 const panel=document.createElement('section');panel.className='screen';panel.id='chronicle';panel.hidden=true;panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-labelledby','chronicleTitle');panel.innerHTML='<article class="chronicle-panel"><button id="chronicleClose" class="secondary">Fermer la chronique</button><p id="chronicleEyebrow" class="eyebrow"></p><h2 id="chronicleTitle"></h2><nav aria-label="Chapitres de la chronique"><button data-story-chapter="1">I · Cathédrale</button><button data-story-chapter="2">II · Souverains</button><button data-story-chapter="3">III · Convoi</button></nav><p id="chroniclePremise"></p><p id="chroniclePurpose" class="story-purpose"></p><div id="chronicleNotes" class="chronicle-notes"></div><p id="chronicleEnding" class="story-ending" hidden></p></article>';document.body.append(panel);
 const button=document.createElement('button');button.id='chronicleButton';button.textContent='Récit';button.onclick=openChronicle;$('#mapButton').after(button);$('#storyMenuOpen').onclick=openChronicle;$('#chronicleClose').onclick=closeChronicle;for(const b of panel.querySelectorAll('[data-story-chapter]'))b.onclick=()=>renderStory(Number(b.dataset.storyChapter));$('#chapterSelect').addEventListener('change',updateStoryMenu);updateStoryMenu();
 addEventListener('keydown',e=>{if(state!=='chronicle')return;if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();closeChronicle();}else if(e.key==='Tab'){const all=[...panel.querySelectorAll('button')],first=all[0],last=all.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}},true);
}
// Original eight-bar motifs; each chapter has a different voicing and meter.
const SCORE={1:{root:110,beat:.62,chords:[0,5,3,7],motif:[12,19,15,14,12,7,10,7]},2:{root:123.47,beat:.53,chords:[0,3,5,7],motif:[12,15,19,22,19,15,14,7]},3:{root:130.81,beat:.68,chords:[0,7,5,3],motif:[7,12,15,19,17,15,14,12]}};
let soundscape=null;
const WORLD_SOUND_LIMIT=16;
function offlineAudioContext(){return !!audio&&typeof audio.startRendering==='function';}
function audioCanSchedule(){return !!audio&&audio.state!=='closed'&&(audio.state==='running'||offlineAudioContext());}
function initSoundscape(){
 if(!audio)return null;if(soundscape?.context===audio)return soundscape;
 const music=audio.createGain(),sfx=audio.createGain(),ui=audio.createGain(),master=audio.createGain(),wet=audio.createGain(),verb=audio.createConvolver(),limiter=audio.createDynamicsCompressor();
 limiter.threshold.value=-16;limiter.ratio.value=5;limiter.attack.value=.008;limiter.release.value=.25;
 music.gain.value=offlineAudioContext()?1:0;sfx.gain.value=ui.gain.value=0;master.gain.value=offlineAudioContext()?1:0;
 music.connect(limiter);sfx.connect(limiter);ui.connect(limiter);music.connect(verb);verb.connect(wet);wet.gain.value=.18;wet.connect(limiter);limiter.connect(master);master.connect(audio.destination);
 const impulse=audio.createBuffer(2,audio.sampleRate*1.8,audio.sampleRate);let seed=71;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 for(let c=0;c<2;c++){const d=impulse.getChannelData(c);for(let i=0;i<d.length;i++)d[i]=(random()*2-1)*Math.pow(1-i/d.length,3);}verb.buffer=impulse;
 const noise=audio.createBuffer(1,audio.sampleRate,audio.sampleRate),d=noise.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=random()*2-1;
 soundscape={context:audio,music,sfx,ui,master,wet,verb,limiter,noise,next:0,beat:0,level:0,voices:new Set(),sfxVoices:new Set(),lastStep:null,lastActor:null,stepDistance:0,events:0,active:null,sfxCreated:0,sfxDisposed:0,sfxDropped:0,sfxPeak:0};return soundscape;
}
function soundBusLevel(s,key,value,transition){
 if(s[key+'Level']===value)return;const now=audio.currentTime,bus=s[key];bus.gain.cancelScheduledValues(now);
 if(s[key+'Level']===undefined||key==='master'&&value===0)bus.gain.setValueAtTime(value,now);else bus.gain.setTargetAtTime(value,now,transition);
 s[key+'Level']=value;
}
function syncSoundscapeLevels(s){
 const enabled=soundOn&&state==='playing'&&audioCanSchedule(),volume=Math.max(0,Math.min(1,localProfile.settings.volume??1));
 soundBusLevel(s,'master',soundOn?volume:0,.02);soundBusLevel(s,'music',enabled?(localProfile.settings.music??.25):0,.18);
 soundBusLevel(s,'sfx',enabled?1:0,.025);soundBusLevel(s,'ui',soundOn?1:0,.025);soundBusLevel(s,'wet',enabled?.18:0,.02);return enabled;
}
function scoreVoice(frequency,time,duration,volume,kind='sine'){
 const s=initSoundscape();if(!s)return;const o=audio.createOscillator(),g=audio.createGain(),filter=audio.createBiquadFilter();o.type=kind;o.frequency.value=frequency;filter.type='lowpass';filter.frequency.value=kind==='triangle'?1000:2400;
 g.gain.setValueAtTime(0,time);g.gain.linearRampToValueAtTime(volume,time+Math.min(.12,duration*.1));g.gain.exponentialRampToValueAtTime(.0001,time+duration);o.connect(filter);filter.connect(g);g.connect(s.music);
 s.voices.add(o);o.scoreGain=g;o.onended=()=>{s.voices.delete(o);o.disconnect();filter.disconnect();g.disconnect();};o.start(time);o.stop(time+duration+.03);s.events++;
}
function stopScoreVoices(s,now){
 for(const source of s.voices){const gain=source.scoreGain?.gain;if(gain){gain.cancelScheduledValues(now);gain.setValueAtTime(gain.value,now);gain.linearRampToValueAtTime(0,now+.012);}try{source.stop(now+.015);}catch(_){}}
 s.voices.clear();
}
function worldSoundPlacement(position){
 if(!position||!Number.isFinite(position.x)||!Number.isFinite(position.z)||!p)return{pan:0,gain:1,distance:0};
 const dx=position.x-p.x,dz=position.z-p.z,distance=Math.hypot(dx,dz);let rightX=1,rightZ=0;
 if(typeof camera!=='undefined'){camera.updateMatrixWorld?.();const elements=camera.matrixWorld?.elements;if(elements&&Number.isFinite(elements[0])&&Number.isFinite(elements[2])){const length=Math.hypot(elements[0],elements[2]);if(length>.001){rightX=elements[0]/length;rightZ=elements[2]/length;}}}
 return{pan:distance<.2?0:Math.max(-.9,Math.min(.9,(dx*rightX+dz*rightZ)/distance)),gain:distance>=36?0:1/(1+(distance/8)**2),distance};
}
function finishWorldVoice(voice){
 if(voice.disposed)return;voice.disposed=true;voice.owner.sfxVoices.delete(voice);for(const node of voice.nodes)try{node.disconnect();}catch(_){}voice.owner.sfxDisposed++;
}
function stopWorldVoice(voice,now){
 if(voice.stopped||voice.disposed)return;voice.stopped=true;voice.owner.sfxVoices.delete(voice);voice.gain.gain.cancelScheduledValues(now);voice.gain.gain.setValueAtTime(voice.gain.gain.value,now);voice.gain.gain.linearRampToValueAtTime(0,now+.008);for(const source of voice.sources)try{source.stop(now+.01);}catch(_){}
}
function createWorldVoice(s,priority,position,role='world'){
 const placement=worldSoundPlacement(position);if(!placement.gain)return null;
 if(s.sfxVoices.size>=WORLD_SOUND_LIMIT){const oldest=[...s.sfxVoices].sort((a,b)=>a.priority-b.priority||a.started-b.started)[0];if(priority<=oldest.priority){s.sfxDropped++;return null;}stopWorldVoice(oldest,audio.currentTime);}
 const gain=audio.createGain(),panner=position&&typeof audio.createStereoPanner==='function'?audio.createStereoPanner():null,voice={owner:s,role,priority,started:audio.currentTime,gain,panner,sources:[],nodes:[gain],remaining:0,disposed:false,stopped:false,placement};
 if(panner){panner.pan.value=placement.pan;gain.connect(panner);panner.connect(role==='ui'?s.ui:s.sfx);voice.nodes.push(panner);}else gain.connect(role==='ui'?s.ui:s.sfx);
 s.sfxVoices.add(voice);s.sfxCreated++;s.sfxPeak=Math.max(s.sfxPeak,s.sfxVoices.size);return voice;
}
function addWorldSource(voice,source,end){
 voice.sources.push(source);voice.nodes.push(source);voice.remaining++;source.onended=()=>{voice.remaining--;if(!voice.remaining)finishWorldVoice(voice);};source.start();source.stop(end);
}
function playWorldSound(kind,strength=1,position=null){
 if(!soundOn||!audioCanSchedule()||state!=='playing'||!(localProfile.settings.volume>0)||!(strength>0))return null;
 const s=initSoundscape();syncSoundscapeLevels(s);const now=audio.currentTime,step=kind==='step',wood=step&&journey.level===3,threat=kind==='threat',impact=kind==='impact';
 const priority=step?0:threat?3:impact?2:1,voice=createWorldVoice(s,priority,position);if(!voice)return null;strength=Math.min(2,strength)*voice.placement.gain;
 const duration=step?.12:threat?.38:kind==='shot'?.18:kind==='blade'?.22:.28,filter=audio.createBiquadFilter(),noise=audio.createBufferSource();noise.buffer=s.noise;
 filter.type=wood?'lowpass':'bandpass';filter.frequency.value=step?(wood?520:1700):kind==='shot'?2200:kind==='blade'?3200:threat?950:680;filter.Q.value=step?.7:threat?2.2:1.1;
 const amplitude=(step?.025:kind==='shot'?.075:threat?.065:.055)*strength;
 if(threat){voice.gain.gain.setValueAtTime(.000001,now);voice.gain.gain.linearRampToValueAtTime(amplitude,now+.035);voice.gain.gain.setValueAtTime(amplitude*.8,now+.18);}else voice.gain.gain.setValueAtTime(amplitude,now);voice.gain.gain.exponentialRampToValueAtTime(.000001,now+duration);
 noise.connect(filter);filter.connect(voice.gain);voice.nodes.push(filter);addWorldSource(voice,noise,now+duration);
 if(impact||wood||threat){const oscillator=audio.createOscillator(),body=audio.createGain();oscillator.type=threat?'triangle':'sine';oscillator.frequency.setValueAtTime(threat?180:wood?95:75,now);oscillator.frequency.exponentialRampToValueAtTime(threat?62:35,now+(threat?.30:.12));body.gain.setValueAtTime(threat?.65:.7,now);body.gain.exponentialRampToValueAtTime(.00001,now+(threat?.34:.15));oscillator.connect(body);body.connect(voice.gain);voice.nodes.push(body);addWorldSource(voice,oscillator,now+(threat?.36:.16));}
 return voice;
}
function playTone(freq,dur=.06,type='sine',volume=.025,position=null){
 if(!soundOn||!audioCanSchedule()||!(localProfile.settings.volume>0)||!(volume>0))return null;const s=initSoundscape();syncSoundscapeLevels(s);const voice=createWorldVoice(s,4,position,'ui');if(!voice)return null;
 const now=audio.currentTime,oscillator=audio.createOscillator();dur=Math.max(.015,Math.min(3,dur));oscillator.type=type;oscillator.frequency.setValueAtTime(Math.max(20,freq),now);oscillator.frequency.exponentialRampToValueAtTime(Math.max(35,freq*.5),now+dur);
 voice.gain.gain.setValueAtTime(volume*voice.placement.gain,now);voice.gain.gain.exponentialRampToValueAtTime(.000001,now+dur);oscillator.connect(voice.gain);addWorldSource(voice,oscillator,now+dur);return voice;
}
function resetSoundscapeTransport(s,now){
 stopScoreVoices(s,now);for(const voice of s.sfxVoices)if(voice.role==='world')stopWorldVoice(voice,now);s.next=now;s.lastStep=null;s.stepDistance=0;s.lastActor=null;s.stepAvatar=null;s.lastFootstepSerial=null;
}
function updateSoundscape(dt){
 if(!audio||audio.state==='closed')return;const s=initSoundscape(),enabled=syncSoundscapeLevels(s),now=audio.currentTime;
 if(!enabled){if(s.active!==false)resetSoundscapeTransport(s,now);s.active=false;return;}
 const level=journey.level||1;if(s.active!==true||s.level!==level||s.lastActor&&s.lastActor!==p){resetSoundscapeTransport(s,now);if(s.level!==level)s.beat=0;s.level=level;s.active=true;}
 s.lastActor=p;const score=SCORE[level],combat=!!battle||campaign.bossAwake||enemies.some(e=>!e.dead&&e.alert>1&&Math.hypot(e.x-p.x,e.z-p.z)<12);if(s.next<now-.2)s.next=now;
 while(s.next<now+.12){const beat=s.beat,bar=Math.floor(beat/4),chord=score.chords[Math.floor(bar/2)%4],f=semitone=>score.root*Math.pow(2,semitone/12);if(beat%4===0){scoreVoice(f(chord-12),s.next,score.beat*4.2,.07,'triangle');scoreVoice(f(chord),s.next,score.beat*4.8,.025);scoreVoice(f(chord+7),s.next+.04,score.beat*4.6,.018);}if(beat%2===0)scoreVoice(f(score.motif[(beat/2)%8]),s.next,score.beat*2.8,.035);if(combat){scoreVoice(f(chord-12),s.next,.16,.065,'triangle');if(beat%2)scoreVoice(f(19),s.next,.12,.018);}s.beat=(beat+1)%32;s.next+=score.beat;}
 const point={x:p.x,z:p.z},avatar=typeof avatarRuntime!=='undefined'?avatarRuntime.current:null,calibrated=avatar?.motionCalibration&&Number.isFinite(avatar.motionFootstepSerial);
 if(calibrated){const serial=avatar.motionFootstepSerial;if(s.stepAvatar!==avatar||s.lastFootstepSerial===null||serial<s.lastFootstepSerial){s.stepAvatar=avatar;s.lastFootstepSerial=serial;}else if(serial>s.lastFootstepSerial){if(p.dashT<=0&&p.leap<=0&&(p.motionSpeed||0)>.18)playWorldSound('step',Math.min(1,(p.motionSpeed||1)/3),point);s.lastFootstepSerial=serial;}s.stepDistance=0;}
 else if(s.lastStep&&p.dashT<=0&&p.leap<=0){const distance=Math.hypot(point.x-s.lastStep.x,point.z-s.lastStep.z);if(distance<1){s.stepDistance+=distance;if(s.stepDistance>.82){playWorldSound('step',Math.min(1,(p.motionSpeed||1)/3),point);s.stepDistance%=.82;}}else s.stepDistance=0;}else s.stepDistance=0;s.lastStep=point;
}
