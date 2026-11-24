'use strict';
let expeditionContactShadows=null;
function updateExpeditionContactShadows(){
 if(!expeditionContactShadows){const material=new THREE.MeshBasicMaterial({color:'#050711',map:contactTexture,transparent:true,opacity:.42,depthWrite:false}),mesh=new THREE.InstancedMesh(new THREE.CircleGeometry(1,16),material,64);mesh.name='ExpeditionContactShadows';mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);mesh.frustumCulled=false;mesh.count=0;scene.add(mesh);expeditionContactShadows={mesh,dummy:new THREE.Object3D()};}
 const {mesh,dummy}=expeditionContactShadows;mesh.visible=quality==='light'&&journey.level>1;mesh.count=0;if(!mesh.visible||!p)return;
 for(const e of enemies){if(e.dead||!e.root?.visible||mesh.count>=64)continue;const actor=e.partyOwner,r=actor?(actor.heroId==='colosse'?.8:.55):['boss','porter'].includes(e.type)?1.45:e.creatureReference?.8:.58;dummy.position.set(e.x,.026,e.z);dummy.rotation.set(-Math.PI/2,0,0);dummy.scale.set(r,r*.68,1);dummy.updateMatrix();mesh.setMatrixAt(mesh.count++,dummy.matrix);}mesh.instanceMatrix.needsUpdate=true;
}
