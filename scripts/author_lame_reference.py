"""Lame reference production 01. Blender 4.3, original surfaces and keyed poses.
Only exports lame.glb. Uses the existing, compatible skeleton builder; no other hero is regenerated.
"""
import bpy, math, json, hashlib, sys, shutil
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'assets/characters'; PREVIEW=Path('/tmp/lame-production');PREVIEW.mkdir(exist_ok=True)
# Reuse skeleton/socket conventions, not the old visible meshes or clip poses.
base=ROOT/'scripts/author_characters.py';ns={'__file__':str(base)};exec(compile(base.read_text().split('\nROLES=')[0],str(base),'exec'),ns);ns['OUT']=PREVIEW/'rig-cache';ns['OUT'].mkdir(exist_ok=True);ns['create']('lame')
rig=bpy.data.objects['lame_Rig']
for obj in list(bpy.data.objects):
 if obj.type=='MESH':bpy.data.objects.remove(obj,do_unlink=True)
rig.animation_data_clear()
for action in list(bpy.data.actions):bpy.data.actions.remove(action)
materials=[];parts=[];weapon=[]
COLORS=[(.13,.145,.16),(.55,.35,.17),(.80,.76,.66),(.64,.61,.52),(.115,.105,.10),(.51,.22,.075),(.11,.078,.055),(.17,.12,.085)]
NAMES=['Obsidian lamella','Weathered bronze','Cracked porcelain','Flax sleeve','Night brocade','Amber silk','Bound hair','Oiled leather']
# Shared atlas with deliberately separate regions; GLB embeds all three textures.
def atlas(size,kind):
 yy,xx=np.mgrid[0:size,0:size];u=(xx%(size//4))/(size//4);v=(yy%(size//2))/(size//2);index=(yy//(size//2))*4+xx//(size//4);rng=np.random.default_rng(8103)
 grain=rng.random((size,size))-.5;weave=np.sin(u*math.tau*100)*np.sin(v*math.tau*160);height=.03*weave+.015*grain
 cracks=(np.abs(np.sin(u*27+np.sin(v*18)*1.5))<.025)&(index==2)
 if kind=='color':
  a=np.zeros((size,size,4),dtype=np.float32);a[:,:,3]=1
  for i,c in enumerate(COLORS):
   region=index==i;variation=1+grain*.13+weave*(.05 if i in [3,4,5] else .012)
   for ch in range(3):a[:,:,ch][region]=(np.array(c[ch])*variation)[region]
  a[cracks,:3]=(.36,.22,.10)
  ornament=((np.abs(np.sin(u*math.tau*5+v*7))<.05)|(np.abs(v-.12)<.008))&(index==5);a[ornament,:3]=(.63,.35,.12)
 elif kind=='orm':
  a=np.ones((size,size,4),dtype=np.float32);rough=np.array([.42,.4,.62,.89,.88,.74,.47,.68]);metal=np.array([.65,.8,0,0,0,0,.03,.02]);a[:,:,1]=rough[index]+grain*.06;a[:,:,2]=metal[index]
 else:
  dy,dx=np.gradient(height);a=np.ones((size,size,4),dtype=np.float32);a[:,:,0]=.5-dx*2;a[:,:,1]=.5+dy*2;a[:,:,2]=1
 image=bpy.data.images.new('Lame_'+kind,width=size,height=size,alpha=True);
 if kind!='color':image.colorspace_settings.name='Non-Color'
 else:a[:,:,:3]=np.where(a[:,:,:3]<=.04045,a[:,:,:3]/12.92,((a[:,:,:3]+.055)/1.055)**2.4)
 image.pixels.foreach_set(a.ravel());image.filepath_raw=str(PREVIEW/(kind+('.jpg' if kind=='color' else '.png')));image.file_format='JPEG' if kind=='color' else 'PNG';image.save();image.pack();return image
color=atlas(2048,'color');orm=atlas(1024,'orm');normal=atlas(1024,'normal');orm.colorspace_settings.name=normal.colorspace_settings.name='Non-Color'
for i,name in enumerate(NAMES):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 for image,label in [(color,'color'),(orm,'orm'),(normal,'normal')]:
  t=n.new('ShaderNodeTexImage');t.image=image
  if label=='color':l.new(t.outputs['Color'],p.inputs['Base Color'])
  elif label=='orm':
   split=n.new('ShaderNodeSeparateColor');l.new(t.outputs['Color'],split.inputs[0]);l.new(split.outputs['Green'],p.inputs['Roughness']);l.new(split.outputs['Blue'],p.inputs['Metallic'])
  else:
   bump=n.new('ShaderNodeNormalMap');bump.inputs['Strength'].default_value=.35;l.new(t.outputs['Color'],bump.inputs['Color']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
 materials.append(m)
def mesh(name,verts,faces,mat,weights,uv=None,group=None,thickness=0):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);data.materials.append(materials[mat]);layer=data.uv_layers.new(name='Tailored UV')
 for loop in data.loops:
  co=data.vertices[loop.vertex_index].co;coord=uv[loop.vertex_index] if uv else ((co.x+.65)/1.3,co.z/2.35);layer.data[loop.index].uv=((mat%4+max(.01,min(.99,coord[0])))/4,(mat//4+max(.01,min(.99,coord[1])))/2)
 for i,co in enumerate(verts):
  w=weights(co) if callable(weights) else {weights:1}
  total=sum(w.values()) or 1
  for bn,value in w.items():
   if bn not in o.vertex_groups:o.vertex_groups.new(name=bn)
   if value>0:o.vertex_groups[bn].add([i],value/total,'REPLACE')
 for f in data.polygons:f.use_smooth=True
 if thickness:
  mod=o.modifiers.new('Tailored thickness','SOLIDIFY');mod.thickness=thickness;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 (weapon if group=='weapon' else parts).append(o);return o
def blend(a,b,w):return {a:1-max(0,min(1,w)),b:max(0,min(1,w))}
def torso_weight(co):return blend('spine','chest',(co[2]-1.28)/.28) if co[2]>1.23 else {'pelvis':1}
def loft(name,rings,mat,weights,segments=40,fold=0):
 vs=[];uv=[]
 for row,(cx,cy,z,rx,ry) in enumerate(rings):
  for j in range(segments):
   a=j/segments*math.tau;r=1+fold*math.sin(a*9+z*12);vs.append((cx+math.cos(a)*rx*r,cy+math.sin(a)*ry*r,z));uv.append((j/segments,row/(len(rings)-1)))
 fs=[(i*segments+j,i*segments+(j+1)%segments,(i+1)*segments+(j+1)%segments,(i+1)*segments+j) for i in range(len(rings)-1) for j in range(segments)];fs.extend([tuple(reversed(range(segments))),tuple((len(rings)-1)*segments+j for j in range(segments))]);return mesh(name,vs,fs,mat,weights,uv)
def tube(name,points,radius,mat,bone,group=None):
 vs=[];uv=[];sides=8
 for i,point in enumerate(points):
  tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)]);tangent.normalize();axis=tangent.cross(Vector((0,1,0)));axis.normalize();other=tangent.cross(axis).normalized()
  for j in range(sides):
   a=j/sides*math.tau;pos=Vector(point)+radius*(axis*math.cos(a)+other*math.sin(a));vs.append(tuple(pos));uv.append((j/sides,i/max(1,len(points)-1)))
 fs=[(i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j) for i in range(len(points)-1) for j in range(sides)];return mesh(name,vs,fs,mat,bone,uv,group)
def ribbon(name,fn,rows,cols,mat,weights,thickness=.004):
 vs=[];uv=[]
 for i in range(rows):
  for j in range(cols):vs.append(fn(i/(rows-1),j/(cols-1)));uv.append((j/(cols-1),i/(rows-1)))
 fs=[(i*cols+j,i*cols+j+1,(i+1)*cols+j+1,(i+1)*cols+j) for i in range(rows-1) for j in range(cols-1)];return mesh(name,vs,fs,mat,weights,uv,thickness=thickness)
# Smooth, tailored torso: many rings, weighted across three anatomical joints.
profile=[(.98,.205,.125),(1.09,.23,.135),(1.2,.195,.12),(1.34,.205,.13),(1.49,.25,.165),(1.61,.27,.14),(1.69,.23,.12),(1.76,.105,.085)]
rings=[]
for i in range(len(profile)-1):
 for k in range(5):
  f=k/5;z,rx,ry=[profile[i][j]*(1-f)+profile[i+1][j]*f for j in range(3)];rings.append((0,0,z,rx,ry))
rings.append((0,0,*profile[-1]));loft('Tailored anatomical tunic',rings,4,torso_weight,64,.02)
# Continuous legs and sleeves, blended at knees/elbows instead of separate ball joints.
for side,sign in [('L',1),('R',-1)]:
 thigh='thigh.'+side;shin='shin.'+side;upper='upper_arm.'+side;lower='forearm.'+side;hand='hand.'+side
 leg=[]
 for k in range(32):
  f=k/31;z=1.06-f*.93;radius=np.interp(z,[.13,.25,.42,.57,.73,1.06],[.052,.062,.09,.068,.102,.115]);leg.append((sign*(.145+.005*f),0,z,radius,radius*.86))
 loft('Fitted leg '+side,leg,7,lambda co,t=thigh,s=shin:blend(s,t,(co[2]-.49)/.16),40,.025)
 sleeve=[]
 for k in range(26):
  f=k/25;z=1.66-f*.60;x=sign*(.27+.21*f);r=(.10-.045*f)*(1+.09*math.sin(f*math.pi*9));sleeve.append((x,-.03*f,z,r,r*.95))
 loft('Linen articulated sleeve '+side,sleeve,3,lambda co,u=upper,l=lower:blend(l,u,(co[2]-1.28)/.14),40,.065)
 # Boot with instep/toe modeled by asymmetric rings rather than a box.
 boot=[(sign*.15,-.065,.025,.078,.165),(sign*.15,-.075,.055,.082,.175),(sign*.15,-.065,.11,.078,.155),(sign*.15,-.03,.16,.066,.105),(sign*.15,0,.24,.065,.07),(sign*.15,0,.34,.074,.074)]
 loft('Shaped boot '+side,boot,7,lambda co,s=side:blend('foot.'+s,'shin.'+s,(co[2]-.11)/.10),48,.02)
 glove=[(sign*.48,-.03,1.09,.064,.059),(sign*.48,-.04,1.04,.066,.048),(sign*.48,-.04,.97,.054,.045),(sign*.48,-.04,.93,.035,.03)]
 loft('Glove palm '+side,glove,7,hand,32,.025)
 for finger in range(4):
  x=sign*(.445+finger*.021);pts=[(x,-.04,.995),(x,-.071,.963),(x,-.083,.939),(x,-.065,.925)];tube('Bent finger '+side,pts,.009,7,hand)
 # Fitted overlapping bracer lamellae.
 for row in range(4):
  z=1.25-row*.055;cx=sign*(.41+row*.018)
  ribbon('Vambrace '+side,lambda f,u,z=z,cx=cx:(cx+math.cos((u-.5)*math.pi)*.065,-.035-math.sin(u*math.pi)*.085,z-.06*f),5,18,0,lower)
 # Offset shoulder tiers; right arm has fewer plates and more visible linen.
 for row in range(5 if side=='L' else 3):
  ribbon('Forged shoulder '+side,lambda f,u,row=row,sign=sign:(sign*(.18+.25*f+row*.016),math.sin((u-.5)*math.pi)*(.11+.035*f),1.77-row*.042-.15*f*f+.035*math.cos((u-.5)*math.pi)),10,24,0,upper,.008)
  pts=[(sign*(.43+row*.016),math.sin((u/20-.5)*math.pi)*.145,1.62-row*.042+.035*math.cos((u/20-.5)*math.pi)) for u in range(21)];tube('Copper shoulder edge',pts,.0022,1,upper)
# Tapered torso lamellae, arranged as diagonal fitted surfaces.
for row in range(5):
 ribbon('Cuirass layer',lambda f,u,row=row:((u-.5)*(.46-row*.035)+row*.013,-.145-.05*math.sin(u*math.pi)-f*.006,1.67-row*.074-.105*f+.18*(u-.5)),7,32,0,torso_weight,.006)
ribbon('Diagonal sword baldric',lambda f,u:(-.23+.43*f+(u-.5)*.043,-.19+.025*f-.025*math.sin(f*math.pi),1.69-.59*f),28,7,7,torso_weight,.004)
# Sash with visible construction, and a split skirt leaving both feet clear.
loft('Waist belt',[(0,0,1.105,.235,.146),(0,0,1.16,.224,.143)],7,'pelvis',64)
for sign in [-1,1]:
 ribbon('Front split tasset',lambda f,u,sign=sign:(sign*(.035+.18*u+.07*f*u),-.145-.07*f+.022*math.sin(u*math.pi*5+f*.5)*f,1.11-f*(.54+.14*u)),23,18,4,lambda co,sg=sign:blend('pelvis','thigh.'+('L' if sg>0 else 'R'),(1.05-co[2])/.65))
# Two shaped mantle panels and amber inner surfaces. Weight into three cape joints.
def capeweight(co):
 f=(1.72-co[2])/1.48;return blend('chest','cape_mid',f/.45) if f<.45 else blend('cape_mid','cape_tip',(f-.45)/.55)
for sign in [-1,1]:
 for inner,mat in [(False,4),(True,5)]:
  ribbon('Split mantle lining' if inner else 'Split mantle',lambda f,u,sign=sign,inner=inner:(sign*((.018+.055*f)+u*(.27+.23*f)),.14+.22*f+.10*f*f+math.sin(u*math.pi*6+f*.7)*(.008+.028*f)+(-.007 if inner else 0),1.72-f*(1.47-.055*math.sin(u*math.pi*3))),36,28,mat,capeweight,0 if inner else .004)
# Neck and head continuously shaped, mostly under a fitted cowl and mask.
loft('Neck wrap',[(0,0,1.69,.12,.105),(0,0,1.78,.10,.095),(0,0,1.86,.10,.09)],4,'neck',48,.035)
head=[(0,.015,1.82,.075,.073),(0,.01,1.88,.11,.105),(0,.015,1.98,.15,.125),(0,.025,2.08,.158,.13),(0,.035,2.17,.13,.115),(0,.035,2.22,.035,.04)]
loft('Underlying head',head,6,'head',64)
def maskpos(z,u):
 width=float(np.interp(z,[1.845,1.90,1.98,2.08,2.18],[.065,.105,.135,.145,.115]));x=u*width;front=-.10-.061*math.sqrt(max(0,1-u*u))-.022*math.exp(-u*u*40)*math.exp(-((z-1.98)/.09)**2);return(x,front,z+.014*u-.018*u*u*(1 if z>2.1 else -1))
for low,high in [(1.845,1.985),(2.017,2.18)]:ribbon('Porcelain mask',lambda f,u,lo=low,hi=high:maskpos(lo+(hi-lo)*f,(u-.5)*2),20,40,2,'head',.007)
for sign in [-1,1]:ribbon('Temple bridge',lambda f,u,sign=sign:maskpos(1.978+.043*f,sign*(.65+.35*u)),7,12,2,'head',.005)
ribbon('Nose bridge',lambda f,u:maskpos(1.96+f*.09,(u-.5)*.19),9,9,2,'head',.005)
for sign in [-1,1]:tube('Amber eye slit',[maskpos(2.005,sign*(.18+i*.023)) for i in range(20)],.003,1,'head')
for line in [[(-.1,2.16),(-.075,2.12),(-.081,2.09),(-.04,2.055)],[(.06,1.96),(.07,1.93),(.035,1.9),(.04,1.86)],[(.075,2.17),(.07,2.13),(.095,2.10)]]:
 tube('Inlaid fracture',[tuple(Vector(maskpos(z,x/.145))+Vector((0,-.004,0))) for x,z in line],.0017,1,'head')
# Hair cap and sculpted locks cover the scalp, leaving the porcelain face clear.
for strand in range(18):
 phi=.04+strand/17*math.pi
 ribbon('Scalp swept lock',lambda f,u,phi=phi:(.164*math.sin(.08+f*2.3)*math.cos(phi+(u-.5)*.20),.025+.142*math.sin(.08+f*2.3)*math.sin(phi+(u-.5)*.20),2.02+.217*math.cos(.08+f*2.3)+.002*math.sin(u*math.pi)),24,6,6,'head',.002)
# Small asymmetrical crescent crest, not a pair of horns.
ribbon('Offset crescent crest',lambda f,u:(.08+math.cos(-.7+f*3.5)*(.087+u*.009*math.sin(f*math.pi)), -.045,2.18+math.sin(-.7+f*3.5)*(.087+u*.009*math.sin(f*math.pi))),36,3,1,'head',.006)
# Hair strands sweep toward the tie and form a small wrapped bun.
for i in range(26):
 a=i/25*math.pi*1.8;pts=[]
 for k in range(15):
  f=k/14;pts.append((math.cos(a)*(.155*(1-f)+.035*f),.02+math.sin(a)*.12*(1-f)+.16*f,2.16+.052*math.sin(f*math.pi)-.15*f))
 tube('Swept hair strand',pts,.008+(i%3)*.001,6,'head')
for i in range(12):
 a=i/12*math.tau;tube('Bound hair knot',[(math.cos(a+k/18*math.tau)*.052,.18+math.sin(a+k/18*math.tau)*.036,2.02+(k/18-.5)*.055) for k in range(19)],.007,6,'head')
for i in range(4):tube('Loose hair',[(.10-i*.018,.09,2.10),(.16-i*.014,.14,2.03),(.17-i*.014,.20,1.96),(.13-i*.012,.23,1.90)],.0025,6,'head')
for strand in range(6):tube('Tied low tail',[(.01+strand*.009,.20,2.01),(.025+strand*.006,.23,1.89),(.045+strand*.003,.24,1.78),(.075,.27,1.69)],.009,6,'head')
# Memory tokens and small practical fastenings.
for i in range(4):
 x=.08+i*.032;z=1.05-i*.04;tube('Token tie',[(x,-.154,1.14),(x+.007,-.17,z)],.002,7,'pelvis');ribbon('Memory token',lambda f,u,x=x,z=z:(x+math.cos(f*math.tau)*(.013+u*.003),-.176,z+math.sin(f*math.tau)*(.013+u*.003)),24,3,1,'pelvis',.003)
# Single curved sabre. Profile has a spine, diamond section and tapered point.
blade=[];uv=[];rows=44
for i in range(rows):
 f=i/(rows-1);x=-.48-.18*f*f;z=.885-1.13*f;width=.027*(1-f)**.45
 for j,(edge,depth) in enumerate([(-1,0),(0,-.009),(1,0),(0,.009)]):blade.append((x+edge*width,-.045+depth*(1-f*.7),z));uv.append((j/3,f))
faces=[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j) for i in range(rows-1) for j in range(4)];mesh('Curved forged sabre',blade,faces,0,'hand.R',uv,'weapon')
tube('Amber blade seam',[(-.48-.18*(i/43)**2,-.056,.885-1.13*(i/43)) for i in range(44)],.0017,1,'hand.R','weapon')
tube('Bound sword grip',[(-.48,-.04,z) for z in [.89,.94,1.0,1.06]],.022,7,'hand.R','weapon')
tube('Crescent sword guard',[(-.48+math.cos(a)*.11,-.04+.025*math.sin(a),.89+math.sin(a)*.045) for a in np.linspace(.1,math.pi*1.9,34)],.009,1,'hand.R','weapon')
bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT');b=rig.data.edit_bones['blade_tip'];b.head=(-.66,-.045,-.245);b.tail=(-.665,-.045,-.29);bpy.ops.object.mode_set(mode='OBJECT')
# Merge by body / weapon, retain material slots and weights, one compatible armature.
exported=[]
for objects,label in [(parts,'Skinned'),(weapon,'Weapon')]:
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name='lame_'+label;o.parent=rig;mod=o.modifiers.new('Lame deformation','ARMATURE');mod.object=rig;exported.append(o)
# Independent key poses for this hero. Radians, body in place; travel is owned by the game.
P=rig.pose.bones
for p in P:p.rotation_mode='XYZ'
def interpolate(points,phase):
 for i in range(len(points)-1):
  if phase<=points[i+1][0]:
   a,A=points[i];b,B=points[i+1];u=max(0,min(1,(phase-a)/(b-a)));u=u*u*(3-2*u);keys=set(A)|set(B);return {key:tuple(A.get(key,(0,0,0))[j]*(1-u)+B.get(key,(0,0,0))[j]*u for j in range(3)) for key in keys}
 return points[-1][1]
guard={'upper_arm.R':(-.15,.02,-.16),'forearm.R':(-.24,.02,.05),'upper_arm.L':(-.20,0,.12),'forearm.L':(-.45,0,.08),'chest':(.025,0,-.07),'thigh.L':(.06,0,.03),'thigh.R':(-.06,0,-.03)}
ATTACKS={
 'attack1':[(0,guard),(.22,{'upper_arm.R':(-1.1,-.30,-.8),'forearm.R':(-.85,0,.1),'chest':(0,0,-.50),'upper_arm.L':(-.35,0,.35)}),(.37,{'upper_arm.R':(-.50,-.15,-.2),'forearm.R':(-.30,0,0),'chest':(.06,0,-.05)}),(.52,{'upper_arm.R':(.50,.25,.85),'forearm.R':(-.18,0,0),'chest':(.10,0,.50),'upper_arm.L':(.1,0,-.25)}),(.8,guard),(1,guard)],
 'attack2':[(0,guard),(.23,{'upper_arm.R':(.30,.35,.85),'forearm.R':(-.7,0,.2),'chest':(.10,0,.45)}),(.37,{'upper_arm.R':(-.45,.15,.1),'forearm.R':(-.32,0,0),'chest':(.03,0,0)}),(.55,{'upper_arm.R':(-1.30,-.15,-.75),'forearm.R':(-.3,0,0),'chest':(-.06,0,-.45),'upper_arm.L':(-.35,0,.25)}),(.86,guard),(1,guard)],
 'attack3':[(0,guard),(.26,{'upper_arm.R':(-2.1,0,-.2),'forearm.R':(-.65,0,0),'chest':(-.15,0,-.12),'upper_arm.L':(-.5,0,.30)}),(.39,{'upper_arm.R':(-.8,0,-.08),'forearm.R':(-.28,0,0),'chest':(.1,0,0)}),(.57,{'upper_arm.R':(.65,0,-.1),'forearm.R':(-.18,0,0),'chest':(.28,0,.10),'thigh.L':(.28,0,0),'thigh.R':(-.16,0,0)}),(.9,guard),(1,guard)]}
clips={'idle':2.4,'guard':2.4,'walk':1.1,'run':.75,'walk_back':1.1,'strafe_left':1.1,'strafe_right':1.1,'start':.3,'stop':.32,'turn_left':.45,'turn_right':.45,'attack1':.65,'attack2':.65,'attack3':.9,'shot':.28,'dash':.3,'dodge_left':.3,'dodge_right':.3,'leap':.75,'shield':1,'interact':.8,'carry':1.2,'hit':.3}
def arm_target(side,target,direction):
 upper=P['upper_arm.'+side];fore=P['forearm.'+side];hand=P['hand.'+side];bpy.context.view_layer.update();h=upper.head.copy();axis=Vector(target)-h;raw=axis.length;l1=upper.length;l2=fore.length;d=min(raw,l1+l2-.003);axis.normalize();pole=Vector((-1 if side=='R' else 1,.25,-.15));bend=(pole-axis*pole.dot(axis)).normalized();along=(l1*l1-l2*l2+d*d)/(2*d);lift=math.sqrt(max(0,l1*l1-along*along));elbow=h+axis*along+bend*lift;wrist=h+axis*d
 upper.matrix=Matrix.Translation(h)@(elbow-h).to_track_quat('Y','Z').to_matrix().to_4x4();bpy.context.view_layer.update();fore.matrix=Matrix.Translation(upper.tail.copy())@(wrist-elbow).to_track_quat('Y','Z').to_matrix().to_4x4();bpy.context.view_layer.update();hand.matrix=Matrix.Translation(fore.tail.copy())@Vector(direction).to_track_quat('Y','Z').to_matrix().to_4x4();bpy.context.view_layer.update()
def point_path(points,phase):
 for i in range(len(points)-1):
  if phase<=points[i+1][0]:
   a,A,D=points[i];b,B,E=points[i+1];u=max(0,min(1,(phase-a)/(b-a)));u=u*u*(3-2*u);return Vector(A).lerp(Vector(B),u),Vector(D).lerp(Vector(E),u)
 return Vector(points[-1][1]),Vector(points[-1][2])
G=(-.39,-.18,1.13);GD=(-.15,-.58,-.8)
HAND_PATHS={
 'attack1':[(0,G,GD),(.22,(-.43,-.1,2.03),(-.1,.3,1)),(.37,(-.03,-.47,1.50),(.5,-.3,-.6)),(.55,(.20,-.20,1.17),(.5,.1,-.8)),(.88,G,GD),(1,G,GD)],
 'attack2':[(0,G,GD),(.23,(-.43,-.25,1.13),(.2,-.1,-1)),(.37,(-.04,-.47,1.48),(-.4,-.4,.4)),(.57,(.12,-.17,2.01),(-.4,.1,.9)),(.9,G,GD),(1,G,GD)],
 'attack3':[(0,G,GD),(.26,(-.30,-.10,2.16),(.1,.2,1)),(.39,(-.21,-.47,1.56),(.05,-.7,-.7)),(.59,(-.28,-.29,1.09),(.1,-.3,-.94)),(.92,G,GD),(1,G,GD)]}
def pose(name,phase):
 D=dict(guard);Z=0
 if name in ATTACKS:D.update(interpolate(ATTACKS[name],phase))
 elif name in ['walk','run','walk_back','strafe_left','strafe_right']:
  cycle=math.sin(phase*math.tau);amp=.54 if name=='run' else .35
  for side,s in [('L',1),('R',-1)]:
   D['thigh.'+side]=(amp*cycle*s*( -1 if name=='walk_back' else 1),0,.10*cycle*s if name.startswith('strafe') else 0);D['shin.'+side]=(max(0,-cycle*s)*.78,0,0);D['foot.'+side]=(-.13*cycle*s,0,0)
  D['upper_arm.L']=(-.20-.18*cycle,0,.12);D['chest']=(.04,0,-.07+.035*cycle);Z=abs(cycle)*.018
 elif name in ['dash','dodge_left','dodge_right']:
  s=-1 if name=='dodge_left' else 1;f=math.sin(phase*math.pi);D.update({'chest':(.14*f,0,s*.16*f),'pelvis':(0,0,-s*.10*f),'thigh.L':(.12*f,0,s*.35*f),'thigh.R':(-.12*f,0,-s*.28*f),'shin.L':(.30*f,0,0),'shin.R':(.27*f,0,0),'upper_arm.L':(-.1,0,s*.35*f)})
 elif name=='leap':
  f=math.sin(phase*math.pi);D.update({'thigh.L':(-.40*f,0,.10),'thigh.R':(.26*f,0,-.1),'shin.L':(.65*f,0,0),'shin.R':(.35*f,0,0),'upper_arm.R':(-.7*f,0,-.3)})
 elif name in ['start','stop']:
  f=math.sin(phase*math.pi)*(1 if name=='start' else -1);D['chest']=(.12*f,0,-.07);D['thigh.L']=(.18*f,0,.03);D['shin.R']=(.2*abs(f),0,0)
 elif name.startswith('turn_'):
  s=-1 if name.endswith('left') else 1;f=math.sin(phase*math.pi);D['pelvis']=(0,s*.12*f,0);D['chest']=(.02,-s*.1*f,-.07);D['thigh.L']=(.12*f,0,.1*f);D['thigh.R']=(-.12*f,0,-.1*f)
 elif name in ['interact','carry','shield']:
  f=math.sin(phase*math.pi) if name=='interact' else 1;D['upper_arm.L']=(-.80*f,0,.18);D['forearm.L']=(-.9*f,0,0)
 elif name=='hit':D['chest']=(.20*math.sin(phase*math.pi),0,-.07)
 else:D['chest']=(.02+.012*math.sin(phase*math.tau),0,-.07)
 D['cape_mid']=(.025*math.sin(phase*math.tau),0,0);D['cape_tip']=(.045*math.sin(phase*math.tau+.5),0,0)
 for bn,p in P.items():p.rotation_euler=D.get(bn,(0,0,0));p.location=(0,0,0)
 P['root'].location.z=Z
 if name in HAND_PATHS:target,direction=point_path(HAND_PATHS[name],phase)
 else:target,direction=Vector(G),Vector(GD)
 arm_target('R',target,direction)
 if name in HAND_PATHS:arm_target('L',(.40,.04,1.24+math.sin(phase*math.pi)*.22),(.1,-.3,-1))
for name,duration in clips.items():
 action=bpy.data.actions.new(name);rig.animation_data_create();rig.animation_data.action=action;n=round(duration*30)
 for frame in range(n+1):
  pose(name,frame/n)
  for bone in P:bone.keyframe_insert(data_path='rotation_euler',frame=frame+1,group=bone.name)
  P['root'].keyframe_insert(data_path='location',frame=frame+1,group='root')
 action.use_fake_user=True
rig.animation_data.action=None
for p in P:p.rotation_euler=(0,0,0);p.location=(0,0,0)
bpy.context.scene.render.fps=30;bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for o in exported:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'lame.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_nla_strips=False,export_force_sampling=True,export_skins=True,export_def_bones=False,export_cameras=False,export_lights=False)
provenance={'generator':'scripts/author_lame_reference.py','base_rig':'scripts/author_characters.py','concept':'design/personnages/lame-eclipse/recherche-01.png','original_art':True,'status':'first 3D production following approved concept; not final art parity','clips':list(clips),'vertices':sum(len(o.data.vertices) for o in exported),'polygons':sum(len(o.data.polygons) for o in exported),'sha256':hashlib.sha256((OUT/'lame.glb').read_bytes()).hexdigest()};(OUT/'LAME-PRODUCTION.json').write_text(json.dumps(provenance,indent=2)+'\n')
# Review render rig, studio lighting, actual 3D geometry, no concept image substitution.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.world.color=(.1,.1,.1)
for name,pos,power,size,col in [('Key',(-3,-4,5),650,4,(1,.86,.68)),('Rim',(2,2,3),1000,3,(1,.4,.12)),('Fill',(3,-1,3),350,3,(.5,.65,1))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.lens=65
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.002));plane=bpy.context.object;floor=bpy.data.materials.new('Review floor');floor.diffuse_color=(.025,.025,.03,1);plane.data.materials.append(floor)
for label,pos,clip,frame in [('front',(2.3,-4,2),'idle',1),('back',(-2,4,2),'idle',1),('attack',(-2.3,-4,2),'attack1',11)]:
 rig.animation_data_create();rig.animation_data.action=bpy.data.actions[clip];scene.frame_set(frame);cam.location=pos;cam.rotation_euler=(Vector((0,0,1.13))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(PREVIEW/(label+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(PREVIEW/'lame-reference.blend'))
print('LAME_PRODUCTION',json.dumps(provenance))

(ROOT/"assets/source").mkdir(exist_ok=True);shutil.copyfile(PREVIEW/"lame-reference.blend",ROOT/"assets/source/lame-reference.blend")
