'use strict';
const HERO_DEFS={
 rempart:{name:'Le Dernier Rempart',hp:150,speed:4.9,dash:1.8,power:9,powerName:'Bastion',melee:false,rifle:true,color:'#7ad9ff',attackRate:1,description:'Tirs précis · bouclier qui interrompt et repousse.',weapon:'Fusil de cuivre'},
 voltigeur:{name:'Le Voltigeur',hp:110,speed:6.1,dash:1.15,power:7,powerName:'Bond',melee:true,color:'#ffba79',attackRate:1,description:'Lame vive · bond et frappe au sol.',weapon:'Lame des vents'},
 lame:{name:'La Lame d’Éclipse',hp:125,speed:5.5,dash:1.35,power:8,powerName:'Traversée',melee:true,color:'#a9edff',attackRate:1.1,description:'Longue lame · parade brève et traversée offensive.',weapon:'Sabre lunaire'},
 tisseuse:{name:'La Tisseuse de Failles',hp:105,speed:5.3,dash:1.5,power:10,powerName:'Failles',melee:false,color:'#c3a0ff',attackRate:1.15,description:'Projectiles arcaniques · deux passages pour corps et tirs.',weapon:'Bâton des passages'},
 cendres:{name:'Le Porte-Cendres',hp:145,speed:4.7,dash:1.7,power:8,powerName:'Fournaise',melee:false,rifle:true,color:'#ff8457',attackRate:.95,description:'Canon incandescent · chaleur accumulée puis libérée.',weapon:'Canon du brasier'},
 voleur:{name:'Le Voleur d’Ombres',hp:105,speed:6,dash:1.2,power:7,powerName:'Double',melee:true,color:'#bca4ec',attackRate:.85,description:'Lames jumelles · double offensif et échange de position.',weapon:'Dagues miroirs'},
 bergere:{name:'La Bergère des Astres',hp:120,speed:5.2,dash:1.5,power:10,powerName:'Astre',melee:false,color:'#a5efdb',attackRate:1.1,description:'Éclats stellaires · astre protecteur qui attire et soigne.',weapon:'Sceptre astral'},
 colosse:{name:'Le Colosse de Porcelaine',hp:190,speed:4.3,dash:2,power:11,powerName:'Rempart de terre',melee:true,color:'#e8ddc2',attackRate:1.45,description:'Marteau massif · frappe et abri matériel temporaire.',weapon:'Marteau de porcelaine'},
 accordeur:{name:'L’Accordeur',hp:120,speed:5.3,dash:1.4,power:9,powerName:'Résonance',melee:false,color:'#f5c9e1',attackRate:1,description:'Notes d’énergie · trois pulsations qui interrompent.',weapon:'Diapason royal'},
 neant:{name:'L’Enfant du Néant',hp:100,speed:5.8,dash:1.25,power:10,powerName:'Ombre vive',melee:true,color:'#8da8ef',attackRate:.9,description:'Faucille · ombre combattante et métamorphose.',weapon:'Croissant du Néant'},
 eclipse:{name:'L’Éclipse incarnée',hp:140,speed:5.5,dash:1.4,power:12,powerName:'Soleil noir',melee:true,color:'#ffdb85',attackRate:1.1,secret:true,description:'Fracture · soleil noir · Incarnation supplémentaire avec R.',weapon:'Fracture'}
};
function isHeroId(id){return typeof id==='string'&&Object.hasOwn(HERO_DEFS,id);}
function isMeleeHero(id=hero){return isHeroId(id)&&!!HERO_DEFS[id].melee;}
function isRifleHero(id=hero){return isHeroId(id)&&!!HERO_DEFS[id].rifle;}
function emptyProfile(){return {version:1,name:'Voyageur',secret:[false,false,false],completed:[],stats:{wins:0,deaths:0,kills:0,seconds:0,battleMatches:0,battleWins:0},settings:{volume:.6,music:.25,reduced:false},journey:null};}
let localProfile=emptyProfile();
// JSON files are already byte-limited at import; cap nesting/work before later
// cloning or restoring a save. This is not a network-message authorization rule.
function isBoundedSaveData(value){
 const pending=[[value,0]];let nodes=0;
 while(pending.length){const [item,depth]=pending.pop();if(++nodes>8192||depth>12)return false;if(item&&typeof item==='object'){const keys=Object.keys(item);if(keys.length>8192-nodes)return false;for(const key of keys)pending.push([item[key],depth+1]);}}
 return true;
}
function validateProfile(data){
 if(!data||!isBoundedSaveData(data)||data.version!==1||typeof data.name!=='string'||!Array.isArray(data.secret)||data.secret.length!==3||data.secret.some(v=>typeof v!=='boolean')||!Array.isArray(data.completed)||data.completed.some(n=>![1,2,3].includes(n)))throw Error('Sauvegarde incompatible.');
 const result=emptyProfile();result.name=data.name.trim().slice(0,24)||'Voyageur';result.secret=data.secret.slice();result.completed=[...new Set(data.completed)];
 for(const key of Object.keys(result.stats)){const n=Number(data.stats?.[key]);result.stats[key]=Number.isFinite(n)&&n>=0?Math.min(n,1e9):0;}
 for(const [key,fallback]of [['volume',.6],['music',.25]]){const n=Number(data.settings?.[key]??fallback);result.settings[key]=Number.isFinite(n)?Math.max(0,Math.min(1,n)):fallback;}result.settings.reduced=!!data.settings?.reduced;
 if(data.journey&&[1,2,3].includes(data.journey.level)&&isHeroId(data.journey.hero)&&['vigor','haste',''].includes(data.journey.boon)&&Number.isInteger(data.journey.checkpoint)&&data.journey.checkpoint>=0&&data.journey.checkpoint<=(data.journey.level===1?0:data.journey.level===2?5:6))result.journey={level:data.journey.level,hero:data.journey.hero,boon:data.journey.boon,checkpoint:data.journey.checkpoint,route:['sun','storm',''].includes(data.journey.route)?data.journey.route:'',core:Math.max(1,Math.min(300,Number(data.journey.core)||180))};
 return result;
}
try{const data=localStorage.getItem('royaumes-profile-v1');if(data)localProfile=validateProfile(JSON.parse(data));if(localStorage.getItem('royaumes-eclipse-reflet-v1')==='found')localProfile.secret[0]=true;}catch(_){}
function persistProfile(){try{localStorage.setItem('royaumes-profile-v1',JSON.stringify(localProfile));}catch(_){} }
function secretUnlocked(){return localProfile.secret.every(Boolean);}
function recordSecret(step){if(localProfile.secret[step])return;localProfile.secret[step]=true;persistProfile();if(secretUnlocked())announce('Le soleil noir a un nom. L’Éclipse incarnée est disponible dans la galerie des héros.');}
