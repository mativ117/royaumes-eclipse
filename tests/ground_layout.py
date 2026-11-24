"""Planar union has no double-covered texture surface and preserves navigation area."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
program=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert'),context={};vm.createContext(context);vm.runInContext(fs.readFileSync(process.argv[1]+'/src/ground-layout.js','utf8'),context);
const regions=[{x0:-29,x1:-10,z0:-35,z1:4},{x0:10,x1:29,z0:-35,z1:4},{x0:-29,x1:29,z0:-43,z1:-32}];
const output=context.uniqueGroundRectangles(regions);const area=r=>(r.x1-r.x0)*(r.z1-r.z0);assert(output.reduce((s,r)=>s+area(r),0)===regions.reduce((s,r)=>s+area(r),0)-2*19*3);
function check(input,pieces){for(let i=0;i<pieces.length;i++)for(let j=i+1;j<pieces.length;j++){const a=pieces[i],b=pieces[j];assert(Math.min(a.x1,b.x1)<=Math.max(a.x0,b.x0)||Math.min(a.z1,b.z1)<=Math.max(a.z0,b.z0),'No two surface interiors may overlap');}for(let x=-30.125;x<50;x+=.5)for(let z=-70.125;z<6;z+=.5){const inside=r=>x>r.x0&&x<r.x1&&z>r.z0&&z<r.z1;assert(input.some(inside)===pieces.some(inside),'The visual ground union must preserve all actual ground');}}
check(regions,output);const secret=[{x0:30,x1:45,z0:-63,z1:-57},{x0:35,x1:47,z0:-68,z1:-51}];check(secret,context.uniqueGroundRectangles(secret));const nested=[{x0:0,x1:10,z0:0,z1:10},{x0:2,x1:8,z0:2,z1:8}];assert(context.uniqueGroundRectangles(nested).length===1);
console.log('PASS: overlapping chapter II floors and secret island draw once; union area, no interior overlap, no missing floor, nested regions and incremental cuts.');
'''
subprocess.run(['node','-e',program,str(ROOT)],check=True)
