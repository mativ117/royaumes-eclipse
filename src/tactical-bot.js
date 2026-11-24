'use strict';
// A local, bounded utility planner. It emits the same controls as a player and
// never changes health, damage, cooldowns or the simulation clock.
const TACTICAL_BOT_PROFILES=Object.freeze({
 veteran:Object.freeze({reaction:.24,decision:.10,memory:1.25,range:22,fov:Math.PI*1.32,turn:6.2,aimError:.060,lead:.72,commit:.34}),
 tactician:Object.freeze({reaction:.16,decision:.10,memory:1.40,range:25,fov:Math.PI*1.48,turn:7.5,aimError:.032,lead:.88,commit:.28})
});
const TACTICAL_HERO_KITS=Object.freeze({
 rempart:{melee:false,preferred:7.5,reach:16},voltigeur:{melee:true,preferred:1.9,reach:2.55},lame:{melee:true,preferred:1.9,reach:2.45},tisseuse:{melee:false,preferred:6.6,reach:15},cendres:{melee:false,preferred:7.1,reach:16},voleur:{melee:true,preferred:1.45,reach:2.15},bergere:{melee:false,preferred:5.9,reach:14},colosse:{melee:true,preferred:2.25,reach:2.85},accordeur:{melee:false,preferred:5.8,reach:13},neant:{melee:true,preferred:1.9,reach:2.6},eclipse:{melee:true,preferred:2.0,reach:2.7}
});
class TacticalDuelBot{
 constructor(options={}){
  this.difficulty=Object.hasOwn(TACTICAL_BOT_PROFILES,options.difficulty)?options.difficulty:'veteran';
  this.profile=TACTICAL_BOT_PROFILES[this.difficulty];this.reset(options.seed??1);
 }
 reset(seed=this.initialSeed){
  let value=typeof seed==='number'&&Number.isFinite(seed)?seed>>>0:2166136261;
  if(typeof seed==='string')for(const char of seed.slice(0,128))value=Math.imul(value^char.charCodeAt(0),16777619)>>>0;
  this.initialSeed=seed;this.randomState=value||0x9e3779b9;this.clock=0;this.nextDecision=0;this.samples=[];this.lastSeen=null;this.aim=null;this.state='observe';this.stateUntil=0;this.coverGoal=null;this.coverUntil=0;this.nextCover=0;this.plan=this.neutral();this.pulses={};this.side=this.random()<.5?-1:1;this.aimNoise=0;this.decisionCount=0;this.switches=0;this.habits={closeAttacks:.5,observedAttacks:0,lastPhase:null};this.debug=Object.freeze({state:'observe',reason:'Observe les signes visibles.',reaction:this.profile.reaction,seen:false,decisionCount:0});
 }
 random(){let n=this.randomState;n^=n<<13;n^=n>>>17;n^=n<<5;this.randomState=n>>>0;return this.randomState/4294967296;}
 finite(value,fallback=0){return typeof value==='number'&&Number.isFinite(value)?value:fallback;}
 clamp(value,min,max){return Math.max(min,Math.min(max,value));}
 wrap(angle){return Math.atan2(Math.sin(angle),Math.cos(angle));}
 neutral(){return{x:0,z:0,ax:0,az:0,fire:false,dash:false,power:false,extra:false,interact:false};}
 actor(raw,self=false){
  if(!raw||typeof raw!=='object'||!Number.isFinite(raw.x)||!Number.isFinite(raw.z))return null;
  const actor={x:this.clamp(raw.x,-200,200),z:this.clamp(raw.z,-200,200),vx:this.clamp(this.finite(raw.vx),-15,15),vz:this.clamp(this.finite(raw.vz),-15,15),heroId:typeof raw.heroId==='string'&&Object.hasOwn(TACTICAL_HERO_KITS,raw.heroId)?raw.heroId:'lame',hp:this.clamp(this.finite(raw.hp,100),0,10000),max:this.clamp(this.finite(raw.max,100),1,10000),shield:raw.shield===true?1:this.clamp(this.finite(raw.shield),0,30),aim:Number.isFinite(raw.aim)?this.wrap(raw.aim):null};
  const phase=raw.attack?.phase;actor.attack=['windup','active','recover'].includes(phase)?{phase}:null;
  if(self){for(const key of ['shot','dash','power','stagger','heat','incarnation','incarnateT','formT'])actor[key]=this.clamp(this.finite(raw[key]),0,100);actor.hasDouble=raw.hasDouble===true;actor.canSwap=raw.canSwap===true;actor.attackReach=Number.isFinite(raw.attackReach)?this.clamp(raw.attackReach,.6,5):null;actor.doublePosition=raw.doublePosition&&Number.isFinite(raw.doublePosition.x)&&Number.isFinite(raw.doublePosition.z)?{x:this.clamp(raw.doublePosition.x,-200,200),z:this.clamp(raw.doublePosition.z,-200,200)}:null;}
  return actor;
 }
 geometry(raw){
  return(Array.isArray(raw)?raw:[]).slice(0,32).filter(o=>o&&o.enabled!==false&&Number.isFinite(o.x)&&Number.isFinite(o.z)).map(o=>({x:this.clamp(o.x,-200,200),z:this.clamp(o.z,-200,200),w:this.clamp(this.finite(o.w,1),.05,100),d:this.clamp(this.finite(o.d,1),.05,100),radius:Number.isFinite(o.radius)?this.clamp(o.radius,.025,50):null}));
 }
 bounds(raw){return{minX:this.clamp(this.finite(raw?.minX,-18),-200,200),maxX:this.clamp(this.finite(raw?.maxX,18),-200,200),minZ:this.clamp(this.finite(raw?.minZ,-36),-200,200),maxZ:this.clamp(this.finite(raw?.maxZ,10),-200,200)};}
 inside(p,b,pad=.5){return p.x>=b.minX+pad&&p.x<=b.maxX-pad&&p.z>=b.minZ+pad&&p.z<=b.maxZ-pad;}
 distance(a,b){return Math.hypot(a.x-b.x,a.z-b.z);}
 segmentBlocked(a,b,o,pad=0){
  if(o.radius!==null){const dx=b.x-a.x,dz=b.z-a.z,t=this.clamp(((o.x-a.x)*dx+(o.z-a.z)*dz)/Math.max(1e-9,dx*dx+dz*dz),0,1);return Math.hypot(a.x+dx*t-o.x,a.z+dz*t-o.z)<o.radius+pad;}
  const minX=o.x-o.w/2-pad,maxX=o.x+o.w/2+pad,minZ=o.z-o.d/2-pad,maxZ=o.z+o.d/2+pad;let enter=0,leave=1;
  for(const [position,delta,min,max]of [[a.x,b.x-a.x,minX,maxX],[a.z,b.z-a.z,minZ,maxZ]]){if(Math.abs(delta)<1e-9){if(position<=min||position>=max)return false;continue;}let one=(min-position)/delta,two=(max-position)/delta;if(one>two)[one,two]=[two,one];enter=Math.max(enter,one);leave=Math.min(leave,two);if(enter>=leave)return false;}
  return leave>0&&enter<1;
 }
 clear(a,b,obstacles,pad=0){return !obstacles.some(o=>this.segmentBlocked(a,b,o,pad));}
 blocked(p,obstacles,pad=.48){return !this.clear(p,p,obstacles,pad);}
 observe(observation,self,obstacles,observedAt=this.clock){
  const raw=observation.target;let target=null;
  // visible:false is a hard veto: never inspect the hidden coordinates/attack.
  if(raw&&raw.visible!==false){const candidate=this.actor(raw);if(candidate){const d=this.distance(self,candidate),heading=this.aim??(self.aim===null?0:this.wrap(self.aim+Math.PI)),bearing=Math.atan2(candidate.x-self.x,candidate.z-self.z),withinCone=d<3.2||Math.abs(this.wrap(bearing-heading))<=this.profile.fov/2;if(d<=this.profile.range&&withinCone&&this.clear(self,candidate,obstacles,.08))target=candidate;}}
  const projectiles=[];for(const rawBullet of (Array.isArray(observation.projectiles)?observation.projectiles:[]).slice(0,48)){
   if(!rawBullet||rawBullet.visible===false||rawBullet.hostile===false)continue;
   if(![rawBullet.x,rawBullet.z,rawBullet.dx,rawBullet.dz].every(Number.isFinite))continue;
   const length=Math.hypot(rawBullet.dx,rawBullet.dz);if(length<.001)continue;const bullet={x:this.clamp(rawBullet.x,-200,200),z:this.clamp(rawBullet.z,-200,200),dx:rawBullet.dx/length,dz:rawBullet.dz/length,speed:this.clamp(this.finite(rawBullet.speed,32),.1,60)};
   const d=this.distance(self,bullet),heading=this.aim??0,bearing=Math.atan2(bullet.x-self.x,bullet.z-self.z);if(d<=this.profile.range&&(d<2||Math.abs(this.wrap(bearing-heading))<=this.profile.fov/2)&&this.clear(self,bullet,obstacles,.05))projectiles.push(bullet);
  }
  this.samples.push({time:observedAt,target,projectiles});while(this.samples.length>1&&this.samples[1].time<this.clock-2)this.samples.shift();if(this.samples.length>260)this.samples.splice(0,this.samples.length-260);
 }
 perceived(time){let result=null;for(const sample of this.samples){if(sample.time<=time-this.profile.reaction+1e-8)result=sample;else break;}return result;}
 prediction(sample,time){
  if(!sample?.target)return null;const t=sample.target,age=this.clamp(time-sample.time,0,.4);
  return{...t,x:t.x+t.vx*age,z:t.z+t.vz*age};
 }
 threat(sample,self,obstacles,time,target){
  let result={score:0,x:0,z:0,kind:'none'};
  for(const bullet of sample?.projectiles||[]){const age=this.clamp(time-sample.time,0,.45),x=bullet.x+bullet.dx*bullet.speed*age,z=bullet.z+bullet.dz*bullet.speed*age,vx=bullet.dx*bullet.speed-self.vx,vz=bullet.dz*bullet.speed-self.vz,rx=x-self.x,rz=z-self.z,dot=rx*vx+rz*vz;if(dot>=0)continue;const eta=-dot/Math.max(.001,vx*vx+vz*vz),miss=Math.hypot(rx+vx*eta,rz+vz*eta);if(eta>.6||miss>1.05||!this.clear({x,z},self,obstacles,.06))continue;const score=(1-this.clamp(miss/1.05,0,1))*(.7+.3*(1-this.clamp(eta/.6,0,1)));if(score>result.score)result={score,x:bullet.dx,z:bullet.dz,kind:'projectile'};}
  if(target?.attack&&['windup','active'].includes(target.attack.phase)){const d=this.distance(self,target),dx=self.x-target.x,dz=self.z-target.z,facing=target.aim===null?1:(-Math.sin(target.aim)*dx-Math.cos(target.aim)*dz)/Math.max(.01,d);if(d<3.3&&facing>.35&&this.clear(self,target,obstacles,.05)){const score=.65+.3*(1-d/3.3);if(score>result.score)result={score,x:dx/Math.max(.01,d),z:dz/Math.max(.01,d),kind:'melee'};}}
  return result;
 }
 cover(self,target,obstacles,bounds){
  let best=null,score=-Infinity;
  for(const o of obstacles){const dx=o.x-target.x,dz=o.z-target.z,d=Math.max(.01,Math.hypot(dx,dz)),reach=(o.radius??Math.hypot(o.w,o.d)/2)+.9,point={x:o.x+dx/d*reach,z:o.z+dz/d*reach};if(!this.inside(point,bounds)||this.blocked(point,obstacles)||this.clear(target,point,obstacles,.05))continue;const value=2-this.distance(self,point)*.15-this.distance(target,point)*.025;if(value>score){score=value;best=point;}}
  return best;
 }
 route(self,goal,obstacles,bounds){
  const safe={x:this.clamp(goal.x,bounds.minX+.6,bounds.maxX-.6),z:this.clamp(goal.z,bounds.minZ+.6,bounds.maxZ-.6)};
  if(this.clear(self,safe,obstacles,.52)&&!this.blocked(safe,obstacles,.52))return safe;
  // A small visibility graph handles arena pillars without frame-by-frame wall
  // oscillation. Bound the graph instead of searching the whole level.
  const nearby=obstacles.slice().sort((a,b)=>Math.min(this.distance(self,a),this.distance(safe,a))-Math.min(this.distance(self,b),this.distance(safe,b))).slice(0,12),nodes=[{x:self.x,z:self.z},safe];
  for(const o of nearby){const halfX=(o.radius??o.w/2)+.64,halfZ=(o.radius??o.d/2)+.64;for(const sx of [-1,1])for(const sz of [-1,1]){const point={x:o.x+sx*halfX,z:o.z+sz*halfZ};if(this.inside(point,bounds)&&!this.blocked(point,obstacles,.51))nodes.push(point);}}
  const cost=nodes.map(()=>Infinity),previous=nodes.map(()=>-1),visited=new Set();cost[0]=0;
  for(let iteration=0;iteration<nodes.length;iteration++){let current=-1;for(let i=0;i<nodes.length;i++)if(!visited.has(i)&&(current<0||cost[i]<cost[current]))current=i;if(current<0||!Number.isFinite(cost[current]))break;if(current===1)break;visited.add(current);for(let next=1;next<nodes.length;next++){if(visited.has(next)||next===current||!this.clear(nodes[current],nodes[next],obstacles,.52))continue;const value=cost[current]+this.distance(nodes[current],nodes[next]);if(value<cost[next]){cost[next]=value;previous[next]=current;}}}
  if(previous[1]>=0){let next=1;while(previous[next]>0)next=previous[next];return nodes[next];}
  // No route is known; do not push forever into a solid object.
  return null;
 }
 steer(self,goal,obstacles,bounds,speed=1){
  if(!goal)return{x:0,z:0};const waypoint=this.route(self,goal,obstacles,bounds);if(!waypoint)return{x:0,z:0};const dx=waypoint.x-self.x,dz=waypoint.z-self.z,d=Math.hypot(dx,dz);if(d<.15)return{x:0,z:0};const heading=Math.atan2(dx,dz),probe=.7;let best=null,score=-Infinity;
  for(const offset of [0,.42,-.42,.85,-.85,1.3,-1.3,Math.PI]){const angle=heading+offset,x=Math.sin(angle),z=Math.cos(angle),point={x:self.x+x*probe,z:self.z+z*probe};if(!this.inside(point,bounds)||!this.clear(self,point,obstacles,.48))continue;const value=Math.cos(offset)-Math.abs(offset)*.04;if(value>score){score=value;best={x:x*speed,z:z*speed};}}
  return best||{x:0,z:0};
 }
 decide(self,sample,obstacles,bounds,time){
  this.decisionCount++;const target=this.prediction(sample,time),seen=!!target;
  if(target){this.lastSeen={...target,time:sample.time};const phase=target.attack?.phase||null;if(phase==='windup'&&this.habits.lastPhase!=='windup'){this.habits.observedAttacks++;this.habits.closeAttacks=this.habits.closeAttacks*.85+(this.distance(self,target)<3.3?1:0)*.15;}this.habits.lastPhase=phase;}
  const remembered=!target&&this.lastSeen&&time-this.lastSeen.time<=this.profile.memory?this.lastSeen:null,tacticalTarget=target||remembered,threat=this.threat(sample,self,obstacles,time,target),baseKit=TACTICAL_HERO_KITS[self.heroId],kit=self.attackReach&&baseKit.melee?{...baseKit,reach:self.attackReach,preferred:Math.max(.7,Math.min(baseKit.preferred,self.attackReach-.35))}:baseKit,melee=kit.melee,health=self.hp/self.max,options=[];
  const push=(state,score,goal=null,reason='',fire=false,dash=false,power=false)=>options.push({state,score,goal,reason,fire,dash,power});
  if(!tacticalTarget){const cx=(bounds.minX+bounds.maxX)/2,cz=(bounds.minZ+bounds.maxZ)/2,wx=(bounds.maxX-bounds.minX)*.28,wz=(bounds.maxZ-bounds.minZ)*.28,points=[{x:cx,z:cz},{x:cx-wx,z:cz-wz},{x:cx+wx,z:cz-wz},{x:cx+wx,z:cz+wz},{x:cx-wx,z:cz+wz}],index=Math.floor(time/4)%5;push('search',.3,points[this.side<0?(5-index)%5:index],'Cherche une ligne de vue.');}
  else if(!seen){if(health<.45&&this.coverGoal&&time<this.coverUntil)push('cover',.8,this.coverGoal,'Relit la situation depuis le couvert.');else push('investigate',.44,{x:remembered.x,z:remembered.z},'Vérifie la dernière position observée.');}
  else{
   const distance=this.distance(self,target),dx=(target.x-self.x)/Math.max(.01,distance),dz=(target.z-self.z)/Math.max(.01,distance),line=this.clear(self,target,obstacles,.08),preferred=kit.preferred+(melee?this.habits.closeAttacks*.2:0),side={x:dz*this.side,z:-dx*this.side},ready=self.shot<=0&&!self.attack;
   const pressure={x:target.x-dx*preferred+side.x*.7,z:target.z-dz*preferred+side.z*.7};
   if(!line){push('flank',.78,{x:target.x,z:target.z},'Contourne le couvert pour retrouver une ligne de vue.');}
   else{
    if(distance>preferred+.5)push('approach',.53+this.clamp((distance-preferred)/20,0,.15),pressure,'Réduit la distance en gardant un angle.');
    if(distance<preferred-.65)push('retreat',melee?.45:.77,{x:self.x-dx*3+side.x*1.3,z:self.z-dz*3+side.z*1.3},'Rétablit une distance utile.');
    push('pressure',.49,{x:pressure.x+side.x*.7,z:pressure.z+side.z*.7},'Met la garde sous pression.',ready&&target.shield<=0&&distance<kit.reach);
    if(target.attack?.phase==='recover'&&target.shield<=0&&distance<(melee?4.1:17))push('punish',.84,{x:target.x-dx*(melee?kit.preferred-.2:kit.preferred),z:target.z-dz*(melee?kit.preferred-.2:kit.preferred)},'Exploite la récupération visible.',ready&&distance<kit.reach+.25);
    if(health<.42&&distance<(melee?4:10)){const point=this.cover(self,target,obstacles,bounds);if(point&&(time>=this.nextCover||time<this.coverUntil))push('cover',.88+(1-health)*.08,point,'Se replie vers un couvert.');else push('retreat',.72+(1-health)*.13,{x:self.x-dx*3.5+side.x,z:self.z-dz*3.5+side.z},'Se désengage pour retrouver du temps.');}
   }
   // Decisions use only our own availability and delayed visible opponent state.
   // The ability itself remains the same castClassPower used by human controls.
   if(line&&self.power<=0&&target.shield<=0&&!(self.attack&&self.attack.phase!=='recover')){
    const recover=target.attack?.phase==='recover',near=distance<4.6;let useful=false,reason='Prépare son pouvoir.';
    if(self.heroId==='rempart'){useful=near&&(health<.65||threat.score>.25);reason='Érige son bastion à portée de riposte.';}
    if(self.heroId==='voltigeur'){useful=near&&(recover||threat.score>.25);reason='Prépare un bond pour changer le rythme.';}
    if(self.heroId==='lame'){useful=distance>2.7&&distance<5.3&&recover;reason='Prépare une traversée sur l’ouverture.';}
    if(self.heroId==='tisseuse'){useful=distance<3.2||distance>10&&distance<15;reason='Change la distance avec une faille.';}
    if(self.heroId==='cendres'){useful=distance<4.3&&(self.heat>=40||health<.55);reason='Libère sa chaleur à portée du brasier.';}
    if(self.heroId==='voleur'){const point=self.doublePosition,safeSwap=self.canSwap&&point&&health<.5&&!recover&&!this.blocked(point,obstacles)&&(this.distance(point,target)>distance+1||!this.clear(target,point,obstacles,.08));useful=!!safeSwap||!self.hasDouble&&distance<6;reason=safeSwap?'Se replie vers son propre double connu.':'Place un double pour soutenir ses frappes.';}
    if(self.heroId==='bergere'){useful=distance<8&&health<.8;reason='Appelle un astre de soin et de protection.';}
    if(self.heroId==='colosse'){useful=distance<4.5&&(recover||health<.6);reason='Dresse un abri après sa frappe de terre.';}
    if(self.heroId==='accordeur'){useful=distance<6.2;reason='Installe ses pulsations à portée.';}
    if(self.heroId==='neant'){useful=distance<6&&self.formT<=0;reason='Prend sa forme d’ombre à portée du duel.';}
    if(self.heroId==='eclipse'){useful=distance<8.5;reason='Place son soleil noir dans le cercle.';}
    if(useful){let utility=recover?.86:.76;if(self.heroId==='cendres')utility=.86+this.clamp(self.heat/100,0,1)*.06;else if(self.heroId==='rempart')utility=.85+(threat.score>.25?.10:0);else if(self.heroId==='tisseuse'&&distance<3.2)utility=.86;else if(self.heroId==='bergere'&&health<.55)utility=.88+(1-health)*.05;else if(self.heroId==='voleur'&&self.canSwap)utility=.90;else if(self.heroId==='colosse')utility=recover?.89:.87;else if(self.heroId==='eclipse')utility=recover?.87:.82;push('ability',utility,null,reason,false,false,true);}
   }
  }
  if(threat.score>.38){
   const tangent={x:threat.z*this.side,z:-threat.x*this.side},evade={x:self.x+tangent.x*2.8,z:self.z+tangent.z*2.8};
   if(self.shield<=0&&self.dash<=0)push('evade',.94+threat.score*.12,evade,'Quitte la trajectoire annoncée.',false,true);
   if(self.shield<=0&&self.power<=0&&(self.heroId==='rempart'||self.heroId==='lame'))push('guard',(self.dash>0?.98:.87)+threat.score*.08,null,'Répond à une menace déjà perçue.',false,false,true);
  }
  if(self.stagger>0||self.hp<=0)push('recover',2,null,'Subit le même étourdissement que le joueur.');
  if(self.attack&&self.attack.phase!=='recover')push('recover',1.3,null,'Termine son geste engagé.');
  let selected=options[0]||{state:'observe',score:0,goal:null,reason:'Observe.',fire:false,dash:false,power:false};
  for(const option of options){const inertia=option.state===this.state&&time<this.stateUntil?.13:0;if(option.score+inertia>selected.score+(selected.state===this.state&&time<this.stateUntil?.13:0))selected=option;}
  if(selected.state==='cover'&&this.state!=='cover'&&selected.goal){this.coverGoal={...selected.goal};this.coverUntil=time+1.1;this.nextCover=time+3;}
  if(selected.state!==this.state){this.switches++;this.state=selected.state;this.stateUntil=time+this.profile.commit;}
  let move=this.steer(self,selected.goal,obstacles,bounds,selected.state==='pressure'?.70:1);
  if(selected.state==='recover'||selected.state==='guard'||selected.state==='ability')move={x:0,z:0};
  this.aimNoise+=(this.random()*2-1)*.018;this.aimNoise=this.clamp(this.aimNoise,-this.profile.aimError,this.profile.aimError);
  let aimTarget=tacticalTarget;
  if(target){const lead=melee?0:this.clamp(this.distance(self,target)/32,0,.45)*this.profile.lead;aimTarget={x:target.x+target.vx*lead,z:target.z+target.vz*lead};}
  const extra=self.heroId==='eclipse'&&self.incarnation>=100&&self.incarnateT<=0&&seen&&this.distance(self,target)<9;
  const travelFacing=['search','investigate','flank','cover','retreat'].includes(selected.state)&&Math.hypot(move.x,move.z)>.05;
  this.plan={...this.neutral(),x:move.x,z:move.z,fire:!!selected.fire,dash:!!selected.dash,power:!!selected.power,extra,aimTarget,travelFacing};this.pulses={dash:false,power:false,extra:false};
  this.debug=Object.freeze({state:this.state,reason:selected.reason,reaction:this.profile.reaction,seen,memory:!!remembered,decisionCount:this.decisionCount,switches:this.switches,threat:Math.round(threat.score*100)/100,observedAttacks:this.habits.observedAttacks,score:Math.round(selected.score*100)/100});
 }
 update(observation={},dt=1/60){
  dt=this.clamp(this.finite(dt),0,.10);const self=this.actor(observation.self,true);if(!self||dt<=0)return this.neutral();this.clock+=dt;
  if(this.aim===null)this.aim=self.aim===null?0:this.wrap(self.aim+Math.PI);
  const obstacles=this.geometry(observation.obstacles),bounds=this.bounds(observation.arenaBounds);if(bounds.minX>=bounds.maxX||bounds.minZ>=bounds.maxZ)return this.neutral();
  this.observe(observation,self,obstacles,this.clock-dt);
  while(this.nextDecision<=this.clock+1e-8){this.decide(self,this.perceived(this.nextDecision),obstacles,bounds,this.nextDecision);this.nextDecision+=this.profile.decision;}
  if(this.plan.travelFacing||this.plan.aimTarget){const dx=this.plan.travelFacing?this.plan.x:this.plan.aimTarget.x-self.x,dz=this.plan.travelFacing?this.plan.z:this.plan.aimTarget.z-self.z,wanted=Math.atan2(dx,dz)+(this.plan.travelFacing?0:this.aimNoise);this.aim=this.wrap(this.aim+this.clamp(this.wrap(wanted-this.aim),-this.profile.turn*dt,this.profile.turn*dt));}else this.aim=this.wrap(this.aim+dt*.65*this.side);
  const output={...this.neutral(),x:this.plan.x,z:this.plan.z,ax:Math.sin(this.aim),az:Math.cos(this.aim)};
  const target=this.plan.aimTarget,bearing=target?Math.atan2(target.x-self.x,target.z-self.z):this.aim,aligned=Math.abs(this.wrap(bearing-this.aim))<(this.difficulty==='tactician'?.16:.23);
  output.fire=!!this.plan.fire&&aligned&&self.shot<=0&&!self.attack&&self.stagger<=0&&target&&this.clear(self,target,obstacles,.08);
  for(const action of ['dash','power','extra']){const ready=action==='extra'?self.heroId==='eclipse'&&self.incarnation>=100&&self.incarnateT<=0:self[action]<=0;output[action]=!!this.plan[action]&&!this.pulses[action]&&ready&&self.stagger<=0;if(output[action])this.pulses[action]=true;}
  return output;
 }
}
if(typeof module!=='undefined'&&module.exports)module.exports={TacticalDuelBot};
