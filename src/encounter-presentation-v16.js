'use strict';
// Original chamber-synth score and diegetic encounter cues. No recorded music,
// remote service or additional audio destination: everything uses the existing buses.
const ENCOUNTER_SCORE_V16=Object.freeze({
 1:{root:110,beat:.75,roots:[0,-5,-8,-7],chords:[[0,3,7,14],[0,3,7,12],[0,4,7,11],[0,5,7,12]],motif:[12,19,22,19,15,14,12,7],color:'felt'},
 2:{root:146.832,beat:.69,roots:[0,-8,-5,-7],chords:[[0,3,7,14],[0,4,7,12],[0,3,7,10],[0,5,7,12]],motif:[19,17,15,12,10,12,14,7],color:'glass'},
 3:{root:130.813,beat:.80,roots:[0,-8,-5,-7],chords:[[0,3,7,12],[0,4,7,14],[0,3,7,12],[0,5,7,14]],motif:[12,15,19,24,22,19,17,14],color:'felt'}
});
const ENCOUNTER_SCORE_VOICE_LIMIT=28;
const encounterWavesV16=new WeakMap();
function encounterWaveV16(context,kind){
 let cache=encounterWavesV16.get(context);if(!cache){cache=new Map();encounterWavesV16.set(context,cache);}if(cache.has(kind))return cache.get(kind);
 const partials=kind==='pad'?[0,1,.16,.10,.035,.025]:kind==='glass'?[0,1,.025,.12,.01,.065]:[0,1,.20,.08,.035,.015];
 const wave=context.createPeriodicWave(new Float32Array(partials.length),new Float32Array(partials),{disableNormalization:false});cache.set(kind,wave);return wave;
}
function encounterScoreNoteV16(s,frequency,time,duration,volume,kind='felt'){
 if(s.voices.size>=ENCOUNTER_SCORE_VOICE_LIMIT)return false;
 const context=s.context,source=context.createOscillator(),filter=context.createBiquadFilter(),gain=context.createGain();
 if(kind==='bass')source.type='triangle';else source.setPeriodicWave(encounterWaveV16(context,kind));
 source.frequency.setValueAtTime(frequency,time);filter.type='lowpass';filter.Q.value=kind==='glass'?.6:.35;filter.frequency.setValueAtTime(kind==='pad'?1250:kind==='bass'?420:kind==='glass'?3600:2400,time);
 // A future note cancelled at pause must not revert to GainNode's default 1.
 gain.gain.value=.000001;
 const attack=kind==='pad'?.28:kind==='bass'?.025:.014,release=kind==='pad'?.45:.18;
 gain.gain.setValueAtTime(.000001,time);gain.gain.exponentialRampToValueAtTime(Math.max(.00001,volume),time+attack);
 gain.gain.exponentialRampToValueAtTime(Math.max(.00001,volume*(kind==='pad'?.76:.25)),time+Math.max(attack+.02,duration-release));gain.gain.exponentialRampToValueAtTime(.000001,time+duration);
 source.connect(filter);filter.connect(gain);gain.connect(s.music);source.scoreGain=gain;
 s.voices.add(source);source.onended=()=>{s.voices.delete(source);source.disconnect();filter.disconnect();gain.disconnect();};source.start(time);source.stop(time+duration+.02);s.events++;return true;
}
function scheduleEncounterScore(s,level,combat,now){
 const score=Object.hasOwn(ENCOUNTER_SCORE_V16,level)?ENCOUNTER_SCORE_V16[level]:ENCOUNTER_SCORE_V16[1];
 let transport=s.encounterScore;
 if(!transport||transport.level!==level){transport=s.encounterScore={level,intensity:0,lastNow:now,scheduled:0,bars:0};s.beat=0;}
 const delta=Math.max(0,Math.min(1,now-transport.lastNow));transport.intensity+=((combat?1:0)-transport.intensity)*(1-Math.exp(-delta/1.4));transport.lastNow=now;
 if(!((localProfile.settings.volume??1)>0)||!((localProfile.settings.music??.25)>0)){s.next=now;return 0;}
 if(s.next<now-.2)s.next=now;
 let scheduled=0,steps=0;
 while(s.next<now+.12&&steps++<4){
  const beat=s.beat,bar=Math.floor(beat/4),part=bar%4,root=score.roots[part],mix=transport.intensity,f=note=>score.root*Math.pow(2,note/12),at=s.next;
  if(beat%4===0){
   // Long overlapping voicings carry the space; the melody is deliberately sparse.
   for(const note of score.chords[part])scheduled+=Number(encounterScoreNoteV16(s,f(root+note+12),at,score.beat*4+.34,.0105*(1-mix*.22),'pad'));
   scheduled+=Number(encounterScoreNoteV16(s,f(root-12),at,score.beat*3.8,.046,'bass'));transport.bars++;
  }
  if(beat%2===0&&beat%8!==6)scheduled+=Number(encounterScoreNoteV16(s,f(score.motif[Math.floor(beat/2)%8]),at+.035,score.beat*2.1,.028-mix*.008,score.color));
  if(mix>.035){scheduled+=Number(encounterScoreNoteV16(s,f(root-12),at,score.beat*.48,.026*mix,'bass'));if(beat%2===1)scheduled+=Number(encounterScoreNoteV16(s,f(root+19),at+.018,score.beat*.52,.012*mix,'felt'));}
  s.beat=(beat+1)%32;s.next+=score.beat;
 }
 transport.scheduled+=scheduled;return scheduled;
}
const ENCOUNTER_SOUNDS_V16=Object.freeze({bow_draw:{duration:.54,amp:.050,frequency:650,priority:3},bow_release:{duration:.22,amp:.072,frequency:2350,priority:2},shade_reveal:{duration:.72,amp:.054,frequency:1350,priority:3},ceramic_hit:{duration:.32,amp:.060,frequency:3100,priority:2}});
function encounterSound(kind,position,strength=1){
 const settings=typeof kind==='string'&&Object.hasOwn(ENCOUNTER_SOUNDS_V16,kind)?ENCOUNTER_SOUNDS_V16[kind]:null;
 if(!settings||!soundOn||state!=='playing'||!audioCanSchedule()||!(localProfile.settings.volume>0)||!(strength>0))return null;
 const s=initSoundscape();syncSoundscapeLevels(s);const voice=createWorldVoice(s,settings.priority,position);if(!voice)return null;
 voice.encounterKind=kind;const context=s.context,now=context.currentTime,end=now+settings.duration,amplitude=settings.amp*Math.min(1.5,strength)*voice.placement.gain;
 const param=voice.gain.gain;param.setValueAtTime(.000001,now);param.exponentialRampToValueAtTime(Math.max(.00001,amplitude),now+(kind==='bow_draw'?.075:kind==='shade_reveal'?.11:.006));param.exponentialRampToValueAtTime(.000001,end);
 const noise=context.createBufferSource(),filter=context.createBiquadFilter();noise.buffer=s.noise;filter.type=kind==='ceramic_hit'?'highpass':'bandpass';filter.Q.value=kind==='shade_reveal'?.85:1.7;filter.frequency.setValueAtTime(settings.frequency,now);filter.frequency.exponentialRampToValueAtTime(kind==='bow_draw'?1700:kind==='shade_reveal'?420:settings.frequency*.7,end);noise.connect(filter);filter.connect(voice.gain);voice.nodes.push(filter);addWorldSource(voice,noise,end);
 const partials=kind==='ceramic_hit'?[[720,.65],[1150,.30],[1880,.14]]:kind==='bow_draw'?[[92,.35]]:kind==='bow_release'?[[185,.48]]:[[440,.12],[660,.065]];
 for(const [frequency,level]of partials){const oscillator=context.createOscillator(),gain=context.createGain();oscillator.type=kind==='bow_draw'?'triangle':'sine';oscillator.frequency.setValueAtTime(frequency,now);oscillator.frequency.exponentialRampToValueAtTime(kind==='bow_draw'?148:frequency*(kind==='shade_reveal'?.5:.78),end);gain.gain.setValueAtTime(level,now);gain.gain.exponentialRampToValueAtTime(.00001,end);oscillator.connect(gain);gain.connect(voice.gain);voice.nodes.push(gain);addWorldSource(voice,oscillator,end);}
 return voice;
}

const encounterPresentationV16={element:null,actor:null,level:0,seen:new Set(),queue:[],current:null,remaining:0,safe:0,lastHadEnemies:false};
function initEncounterPresentationV16(){
 const s=encounterPresentationV16;if(s.element)return s.element;
 const style=document.createElement('style');style.textContent='#encounterV16{position:fixed;left:50%;bottom:76px;transform:translateX(-50%);width:min(480px,calc(100vw - 36px));padding:12px 18px;border-left:2px solid #dca36a;background:linear-gradient(90deg,#151017e8,#151017b8);color:#efe2d0;pointer-events:none;z-index:2;text-align:left;box-sizing:border-box}#encounterV16 strong{display:block;font:20px/1.2 Georgia,serif;color:#f1c796;margin-bottom:5px}#encounterV16 span{display:block;font:13px/1.5 system-ui,sans-serif}@media(pointer:coarse),(max-width:600px){#encounterV16{bottom:244px;padding:10px 14px}#encounterV16 strong{font-size:18px}#encounterV16 span{font-size:12px}}@media(max-height:500px){#encounterV16{bottom:100px;width:min(330px,calc(100vw - 270px));padding:8px 12px}#encounterV16 strong{font-size:16px}#encounterV16 span{font-size:11px}}';document.head.append(style);
 const element=document.createElement('section');element.id='encounterV16';element.hidden=true;element.setAttribute('role','status');element.setAttribute('aria-live','polite');const title=document.createElement('strong'),text=document.createElement('span');element.append(title,text);document.body.append(element);s.element=element;return element;
}
function queueEncounterBeatV16(id,title,text){const s=encounterPresentationV16;if(s.seen.has(id)||s.queue.length>=3)return;s.seen.add(id);s.queue.push({id,title,text});}
function updateEncounterPresentation(dt){
 const s=encounterPresentationV16;
 if(state!=='playing'||!p||battle){if(s.element)s.element.hidden=true;s.current=null;s.remaining=0;s.safe=0;return;}
 if(s.actor!==p||s.level!==journey.level){s.actor=p;s.level=journey.level;s.seen.clear();s.queue=[];s.current=null;s.remaining=0;s.safe=0;s.lastHadEnemies=false;}
 const near=enemies.filter(e=>!e.dead&&Math.hypot(e.x-p.x,e.z-p.z)<13&&trialActive(e)),imminent=near.some(e=>e.mode==='windup'||e.mode==='charge');
 if(journey.level===1&&typeof world.zoneAt==='function'&&world.zoneAt(p.x,p.z).includes('Cloître'))queueEncounterBeatV16('cloitre','La voix qui manque','Le chant s’est brisé ici. La fresque garde encore la mémoire de ses trois voix.');
 if(near.some(e=>e.type==='archer'))queueEncounterBeatV16('archer','Le Veilleur des fils','Ses doigts cherchent la corde. Quittez sa ligne avant qu’elle ne se tende.');
 if(near.some(e=>e.type==='shade'))queueEncounterBeatV16('shade','Le reflet prend corps','Dans la lumière, l’ombre retrouve sa matière. Attendez qu’elle se dévoile pour frapper.');
 if(s.lastHadEnemies&&!near.length&&journey.level===1)queueEncounterBeatV16('quiet','La pierre se souvient','Un silence revient. Prenez le temps d’écouter ce que le combat couvrait.');
 s.lastHadEnemies=near.length>0;
 const busy=imminent||!!p.attack||!document.querySelector('#notice')?.hidden||!document.querySelector('#interact')?.hidden;
 s.safe=busy?0:s.safe+Math.max(0,dt);
 if(!s.current&&s.queue.length&&s.safe>.8){s.current=s.queue.shift();s.remaining=5.4;const element=initEncounterPresentationV16();element.firstElementChild.textContent=s.current.title;element.lastElementChild.textContent=s.current.text;}
 if(!s.current)return;
 if(!busy)s.remaining-=Math.max(0,Math.min(.1,dt));
 if(s.remaining<=0){s.current=null;s.element.hidden=true;return;}
 s.element.hidden=busy;
}
