'use strict';
let sanctuary=null;
function initSanctuary(){
 const root=new THREE.Group();world.root.add(root);const limestone=new THREE.MeshStandardMaterial({color:'#b3aa98',roughness:.82,metalness:.08}),copper=new THREE.MeshStandardMaterial({color:'#a3855c',roughness:.4,metalness:.72}),basalt=new THREE.MeshStandardMaterial({color:'#333b43',roughness:.9});
 const stoneTexture=makeArtTexture((g,n)=>{g.fillStyle='#c8c5ba';g.fillRect(0,0,n,n);let seed=93;const r=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};for(let i=0;i<4500;i++){g.fillStyle=i%3?'#ebe7da22':'#313e4533';g.fillRect(r()*n,r()*n,1+r()*2,1+r()*2);}for(let i=0;i<20;i++){const y=r()*n;g.strokeStyle='#767b7e33';g.lineWidth=.6;g.beginPath();g.moveTo(0,y);g.bezierCurveTo(n*.3,y+20,n*.6,y-30,n,y+50);g.stroke();}},512);limestone.map=stoneTexture;limestone.bumpMap=stoneTexture;limestone.bumpScale=.035;
 const archGeo=new THREE.TorusGeometry(1,.06,8,40,Math.PI),columnGeo=new THREE.LatheGeometry([new THREE.Vector2(1,0),new THREE.Vector2(1,.16),new THREE.Vector2(.74,.23),new THREE.Vector2(.64,.4),new THREE.Vector2(.54,.6),new THREE.Vector2(.5,5.5),new THREE.Vector2(.58,5.7),new THREE.Vector2(.8,5.9),new THREE.Vector2(.8,6.2)],20);
 const batch=(geo,mat,items)=>{const obj=new THREE.InstancedMesh(geo,mat,items.length),dummy=new THREE.Object3D();items.forEach((q,i)=>{dummy.position.set(...q.p);dummy.rotation.set(...(q.r||[0,0,0]));dummy.scale.set(...q.s);dummy.updateMatrix();obj.setMatrixAt(i,dummy.matrix);});obj.castShadow=items.some(q=>q.p[1]<1);obj.userData.shadowRole=obj.castShadow?'grounded':'overhead';obj.receiveShadow=true;root.add(obj);return obj;};
 const piers=[],arches=[],ribs=[];
 for(const side of [-1,1])for(const z of [3,15,27]){piers.push({p:[side*18.2,-.2,z],s:[1,1.7,1]});arches.push({p:[side*18.2,8.8,z-6],s:[6,5,1],r:[0,Math.PI/2,0]});}
 batch(columnGeo,limestone,piers);batch(archGeo,copper,arches);
 // The two old cover pillars become carved, human-scale piers with the same footprint.
 for(const o of world.obstacles)if(Math.abs(o.x)===10&&o.z===13){o.mesh.geometry=columnGeo;o.mesh.material=limestone;o.mesh.scale.set(1.05,1.15,1.45);o.mesh.position.set(o.x,0,o.z);o.mesh.castShadow=true;}
 for(const z of [3,15,27]){ribs.push({p:[0,7.1,z],s:[10,8.2,1]});ribs.push({p:[0,7.15,z+.15],s:[9.8,8.1,1]});}batch(archGeo,limestone,ribs);
 // A fractured rose and suspended monolith form a strong destination in the central void.
 const ring=new THREE.Mesh(new THREE.TorusGeometry(6,.16,8,80),copper);ring.position.set(0,10,-14);root.add(ring);
 const spokes=[];for(let i=0;i<12;i++){const a=i*Math.PI/6;spokes.push({p:[Math.cos(a)*3,10+Math.sin(a)*3,-14],s:[.09,6,.1],r:[0,0,a-Math.PI/2]});}batch(boxGeo,copper,spokes);
 const monumentGeo=new THREE.IcosahedronGeometry(1,1),monument=new THREE.Mesh(monumentGeo,basalt);monument.position.set(0,8,-13);monument.scale.set(1.1,5,1.4);monument.rotation.z=.12;monument.castShadow=false;root.add(monument);
 // Basin: real non-traversable water and one collision source for both movement and map.
 const pool={x:0,z:13,w:7.6,d:10.2};const rim=[];
 for(const x of [-4.15,4.15])rim.push({p:[x,.1,13],s:[.52,.28,11.2]});for(const z of [7.4,18.6])rim.push({p:[0,.1,z],s:[8.8,.28,.52]});batch(boxGeo,limestone,rim);
 const reflection=new RoyaumesReflector(new THREE.PlaneGeometry(pool.w,pool.d),{color:0x71878b,textureWidth:512,textureHeight:512,clipBias:.004});reflection.getRenderTarget().texture.type=THREE.UnsignedByteType;reflection.rotation.x=-Math.PI/2;reflection.position.set(0,.025,13);root.add(reflection);
 const waterTime={value:0};reflection.material.uniforms.waterTime=waterTime;reflection.material.fragmentShader=reflection.material.fragmentShader.replace('uniform vec3 color;','uniform vec3 color;uniform float waterTime;').replace('texture2DProj( tDiffuse, vUv )','texture2DProj( tDiffuse, vUv + vec4(sin(vUv.y*60.0+waterTime*.7)*.0007,cos(vUv.x*48.0-waterTime*.5)*.0007,0.0,0.0) )');reflection.material.needsUpdate=true;
 const fallback=new THREE.Mesh(new THREE.PlaneGeometry(pool.w,pool.d),new THREE.ShaderMaterial({uniforms:{waterTime},vertexShader:'varying vec2 waterUv;void main(){waterUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'uniform float waterTime;varying vec2 waterUv;void main(){vec2 p=waterUv*2.0-1.0;float ripple=sin(p.y*46.0+sin(p.x*7.0+waterTime*.25)*.4-waterTime*.45);float gleam=pow(max(0.0,sin(p.y*9.0+sin(p.x*4.0+waterTime*.2)*.08)),32.0);float motif=exp(-pow((length(vec2(p.x*1.15,(p.y+.15)*.72))-.62)*38.0,2.0));vec3 c=mix(vec3(.035,.055,.075),vec3(.095,.15,.17),waterUv.y);c+=vec3(.08,.09,.10)*gleam+vec3(.28,.21,.12)*motif*.28+vec3(.008,.014,.018)*ripple;gl_FragColor=vec4(c,1.0);}'}));fallback.rotation.x=-Math.PI/2;fallback.position.copy(reflection.position);root.add(fallback);
 const waterBlock={...pool,w:8.8,d:11.72,mesh:fallback,landmark:'basin',projectilePass:true};world.obstacles.push(waterBlock);
 for(const f of world.floors)f.receiveShadow=true;
 // Replace the square tiling of the arrival court with a radial marble composition.
 const mosaic=makeArtTexture((g,n)=>{g.fillStyle='#b2ac9e';g.fillRect(0,0,n,n);let seed=33;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};for(let i=0;i<1800;i++){const x=rand()*n,y=rand()*n;g.strokeStyle=i%3?'#fff8dc14':'#3c45432a';g.lineWidth=.5;g.beginPath();g.moveTo(x,y);g.bezierCurveTo(x+8,y+4,x-4,y+12,x+20,y+16);g.stroke();}for(let ring=1;ring<10;ring++){g.strokeStyle=ring%3?'#776d5d':'#c6a56e';g.lineWidth=ring%3?1:3;g.beginPath();g.arc(n/2,n/2,ring*n/18,0,Math.PI*2);g.stroke();}for(let i=0;i<32;i++){const a=i*Math.PI/16;g.strokeStyle='#786e5b';g.lineWidth=1;g.beginPath();g.moveTo(n/2+Math.cos(a)*n*.12,n/2+Math.sin(a)*n*.12);g.lineTo(n/2+Math.cos(a)*n*.7,n/2+Math.sin(a)*n*.7);g.stroke();}},1024);
 const entryFloor=world.floors[0];entryFloor.material.map.dispose();entryFloor.material.map=mosaic;entryFloor.material.color.set('#b6b2a6');entryFloor.material.roughness=.56;entryFloor.material.metalness=.12;entryFloor.material.needsUpdate=true;
 // Dynamic shadows follow the playable actor, rather than an enormous low-resolution map.
 sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=sun.shadow.camera.bottom=-19;sun.shadow.camera.right=sun.shadow.camera.top=19;sun.shadow.camera.near=1;sun.shadow.camera.far=75;sun.shadow.bias=-.0002;sun.shadow.normalBias=.025;sun.target.position.set(0,0,13);scene.add(sun.target);
 const occluders=[];for(const o of world.obstacles)if(!o.gate&&o.mesh!==fallback){const mesh=o.mesh;mesh.material=mesh.material.clone();mesh.material.transparent=true;mesh.userData.occlusionOpacity=1;occluders.push(mesh);}
 sanctuary={root,reflection,fallback,waterTime,pool,occluders,ray:new THREE.Raycaster(),target:new THREE.Vector3(),direction:new THREE.Vector3(),monument,age:0};
 scene.fog.density=.012;camera.position.set(17,10,31);camera.lookAt(0,4,8);setSanctuaryQuality(quality);
}
function setSanctuaryQuality(mode){
 if(!sanctuary)return;const high=mode!=='light';renderer.shadowMap.enabled=high;heroShadow.visible=!high;renderer.shadowMap.type=THREE.PCFSoftShadowMap;sanctuary.reflection.visible=high;sanctuary.fallback.visible=!high;renderer.shadowMap.needsUpdate=true;
}
function updateSanctuary(dt){
 if(!sanctuary)return;const s=sanctuary;s.age+=dt;s.waterTime.value=s.age;
 // Snap in the light's projection plane, not world axes: stable shadow texels.
 const target=new THREE.Vector3(p?.x??0,0,p?.z??13),offset=new THREE.Vector3(-10,24,10);
 const basis=new THREE.Matrix4().lookAt(offset,new THREE.Vector3(),new THREE.Vector3(0,1,0));
 const right=new THREE.Vector3().setFromMatrixColumn(basis,0),up=new THREE.Vector3().setFromMatrixColumn(basis,1),texel=38/sun.shadow.mapSize.x;
 for(const axis of [right,up]){const value=target.dot(axis);target.addScaledVector(axis,Math.round(value/texel)*texel-value);}
 sun.position.copy(target).add(offset);sun.target.position.copy(target);sun.target.updateMatrixWorld();
 if(p){s.target.set(p.x,1.4,p.z);s.direction.copy(s.target).sub(camera.position);const length=s.direction.length();s.direction.normalize();s.ray.set(camera.position,s.direction);s.ray.far=Math.max(0,length-.3);const hit=new Set(s.ray.intersectObjects(s.occluders,false).map(h=>h.object));for(const mesh of s.occluders){const opacity=hit.has(mesh)?.18:1;mesh.material.opacity+=(opacity-mesh.material.opacity)*(1-Math.exp(-dt*9));mesh.material.depthWrite=mesh.material.opacity>.95;}}
 // No expensive off-screen mirror pass once the expedition leaves the court.
 s.reflection.visible=journey.level===1&&quality!=='light'&&(!p||p.z>-10);s.fallback.visible=!s.reflection.visible;
}
function cameraVisibleTarget(e){const point=new THREE.Vector3(e.x,1,e.z).project(camera);return point.z>-1&&point.z<1&&Math.abs(point.x)<1.1&&Math.abs(point.y)<1.1;}
