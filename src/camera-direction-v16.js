'use strict';
const encounterCamera={mix:0,focus:null,fill:null};
function cameraFramingV16(actor,focus,portrait,mix,aspect=portrait?.462:1.5,bodyHeight=2.8){
 const clamp=(n,a,b)=>Math.max(a,Math.min(b,n)),dx=focus?clamp(focus.x-actor.x,-10,10):0,dz=focus?clamp(focus.z-actor.z,-10,10):0;
 const framing={position:{x:actor.x+(actor.vx||0)*.06+dx*mix*.035,y:(portrait?9.2:6.7)-mix*(portrait?1.05:1),z:actor.z+(portrait?12.8:10.8)-mix*(portrait?1.35:1.8)},look:{x:actor.x+(actor.vx||0)*.08+dx*mix*.10,y:portrait?1.8:1.6,z:actor.z-(portrait?4:5)+mix*1.6+(actor.vz||0)*.08+dz*mix*.055}};
 if(focus&&mix>.001){const target=new THREE.Vector3(framing.look.x,framing.look.y,framing.look.z),offset=new THREE.Vector3(framing.position.x,framing.position.y,framing.position.z).sub(target),normal=offset.clone().normalize(),right=new THREE.Vector3().crossVectors(new THREE.Vector3(0,1,0),normal).normalize(),up=new THREE.Vector3().crossVectors(normal,right).normalize(),vertical=Math.tan(49*Math.PI/360)*.86,horizontal=vertical*Math.max(.3,aspect);let required=offset.length();for(const [body,height]of[[actor,bodyHeight],[focus,2.8]])for(const x of[-.7,.7])for(const y of[0,height])for(const z of[-.7,.7]){const q=new THREE.Vector3(body.x+x,y,body.z+z).sub(target);required=Math.max(required,q.dot(normal)+Math.max(Math.abs(q.dot(right))/horizontal,Math.abs(q.dot(up))/vertical));}offset.copy(normal).multiplyScalar(required);framing.position.x=target.x+offset.x;framing.position.y=target.y+offset.y;framing.position.z=target.z+offset.z;}
 return framing;
}
function updateCameraDirectionV16(elapsed){
 if(!encounterCamera.fill){const fill=new THREE.PointLight('#b6cbdf',16,13,2);fill.name='Character reading fill';fill.castShadow=false;scene.add(fill);encounterCamera.fill=fill;}
 encounterCamera.fill.visible=state!=='menu';encounterCamera.fill.position.set(p.x-2.5,4.2,p.z+4);
 const portrait=innerWidth<innerHeight,group=localParty.length?partyCameraCenter():null;
 if(group){encounterCamera.mix=0;encounterCamera.focus=null;camDesired.set(group.x+p.vx*.06,(portrait?9.2:6.7)+group.radius*1.1,group.z+(portrait?12.8:10.8)+group.radius*.9);cameraTarget.set(group.x+p.vx*.08,portrait?1.8:1.6,group.z-(portrait?4:5)+p.vz*.08);}
 else{
  const candidates=state==='playing'?enemies.filter(e=>!e.dead&&trialActive(e)&&distance(e,p)<12&&(e.type!=='boss'||campaign.bossAwake)&&(e.type!=='shade'||shadeVulnerable(e))&&e.root.visible!==false&&(cameraVisibleTarget(e)||distance(e,p)<5)&&clearStrikeLine(e.x,e.z)):[];
  let focus=encounterCamera.focus;if(!candidates.includes(focus))focus=null;const nearest=candidates.slice().sort((a,b)=>distance(a,p)-distance(b,p))[0];if(!focus||nearest&&distance(nearest,p)<distance(focus,p)*.65)focus=nearest||null;encounterCamera.focus=focus;
  const intent=!localProfile.settings.reduced&&focus&&(distance(focus,p)<8||p.attack||p.powerVisualT>0||focus.mode==='windup'||focus.mode==='charge');
  encounterCamera.mix+=((intent?1:0)-encounterCamera.mix)*(1-Math.exp(-Math.max(0,Math.min(.1,elapsed))*2.5));
  const framing=cameraFramingV16(p,focus,portrait,encounterCamera.mix,camera.aspect,Math.max(2.8,(avatarRuntime.current?.motionCalibration?.bodyHeight||2.3)*motionModelScale(avatarRuntime.current))+(player.root.position.y||0));camDesired.set(framing.position.x,framing.position.y,framing.position.z);cameraTarget.set(framing.look.x,framing.look.y,framing.look.z);
 }
 camera.position.lerp(camDesired,1-Math.exp(-elapsed*5));cameraLook.lerp(cameraTarget,1-Math.exp(-elapsed*7));camera.lookAt(cameraLook);
}
