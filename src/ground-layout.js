'use strict';
// Keep logical navigation regions intact while drawing their union only once.
function subtractGroundRectangle(region,cut){
 const x0=Math.max(region.x0,cut.x0),x1=Math.min(region.x1,cut.x1),z0=Math.max(region.z0,cut.z0),z1=Math.min(region.z1,cut.z1);
 if(x1<=x0||z1<=z0)return[region];
 const pieces=[{x0:region.x0,x1:x0,z0:region.z0,z1:region.z1},{x0:x1,x1:region.x1,z0:region.z0,z1:region.z1},{x0,x1,z0:region.z0,z1:z0},{x0,x1,z0:z1,z1:region.z1}];
 return pieces.filter(r=>r.x1-r.x0>1e-7&&r.z1-r.z0>1e-7).map(r=>({...region,...r}));
}
function uniqueGroundRectangles(regions,existing=[]){
 const result=[],covered=existing.slice();
 for(const region of regions){let pieces=[{...region}];for(const cut of covered)pieces=pieces.flatMap(r=>subtractGroundRectangle(r,cut));result.push(...pieces);covered.push(region);}
 return result;
}
