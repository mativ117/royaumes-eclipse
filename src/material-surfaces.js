'use strict';
const referenceMaterialLoads=[];
function referenceSurface(kind,renderer){
 const data=typeof ROYAUMES_SURFACES!=='undefined'&&ROYAUMES_SURFACES[kind];if(!data)return null;
 const surface={dependents:new Set(),source:'Poly Haven CC0'};
 for(const field of ['map','normal','rough']){
  const canvas=document.createElement('canvas');canvas.width=canvas.height=512;const context=canvas.getContext('2d');context.fillStyle=field==='normal'?'#8080ff':field==='rough'?'#bcbcbc':'#5c5852';context.fillRect(0,0,512,512);
  const texture=new THREE.CanvasTexture(canvas);texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());if(field==='map')texture.colorSpace=THREE.SRGBColorSpace;surface[field]=texture;
  referenceMaterialLoads.push(new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>{context.drawImage(image,0,0,512,512);texture.needsUpdate=true;for(const clone of surface.dependents)clone.needsUpdate=true;resolve();};image.onerror=()=>reject(Error('Matière non chargée : '+kind+'/'+field));image.src=data[field];}));
 }
 return surface;
}
function waitReferenceMaterials(){return Promise.all(referenceMaterialLoads);}
