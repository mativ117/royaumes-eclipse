"""Original 1.6 creature production, Blender 4.3 CPU, no external assets.

Creates two materially and anatomically distinct skinned enemies, editable source
Blends and inspectable pose clips. Runtime AI/collisions remain separate.
"""
from pathlib import Path
import bpy, math, json, hashlib, sys
from mathutils import Vector
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/creatures';SOURCE=ROOT/'assets/source/creatures';REVIEW=Path('/tmp/enemy-v16-review')
for folder in [OUT,SOURCE,REVIEW]:folder.mkdir(parents=True,exist_ok=True)
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['archer','shade']
ROLES=[r for r in ARGS if r in ['archer','shade']] or ['archer','shade']

def reset():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for a in list(bpy.data.actions):bpy.data.actions.remove(a)
 for m in list(bpy.data.materials):bpy.data.materials.remove(m)
 for im in list(bpy.data.images):bpy.data.images.remove(im)
 bpy.context.scene.render.fps=30
 bpy.context.scene.frame_start=0

def make_materials(role):
 # Shared six-tile atlas, with distinct grain direction and fracture scratches.
 palette=[(.12,.145,.17),(.68,.65,.53),(.39,.25,.12),(.22,.12,.12),(.95,.39,.075),(.17,.23,.28)]
 names=['Obsidian lacquer','Porcelain bone','Oxidised bronze','Tendon','Threat glow','Membrane']
 textures={}
 for kind,size in [('color',1024),('normal',512),('orm',512)]:
  yy,xx=np.mgrid[0:size,0:size];tile_x=np.minimum(2,xx*3//size);tile_y=np.minimum(1,yy*2//size);tile=tile_y*3+tile_x
  u=(xx*3/size)%1;v=(yy*2/size)%1
  grain=np.sin(u*230+np.sin(v*29)*2)*np.sin(v*181+u*8)
  fracture=np.exp(-((np.sin(u*19+v*4)*.065+v-.46)/.006)**2)
  ribs=np.sin(v*140+u*7);noise=np.random.default_rng(16161).random((size,size))-.5
  pixels=np.ones((size,size,4),np.float32)
  if kind=='color':
   colors=np.asarray(palette)[tile]
   brightness=1+grain*.035+noise*.028-fracture*.2
   if role=='shade': colors=colors*np.asarray([.88,.96,1.07])
   c=np.clip(colors*brightness[:,:,None],0,1)
   pixels[:,:,:3]=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
  elif kind=='normal':
   pixels[:,:,0]=.5+np.round((grain*.017+fracture*.025)*64)/64
   pixels[:,:,1]=.5+np.round((ribs*.009)*64)/64
   pixels[:,:,2]=1
  else:
   pixels[:,:,1]=np.clip(np.asarray([.34,.61,.53,.72,.3,.48])[tile]+np.round(grain*3)/96+fracture*.08,0,1)
   pixels[:,:,2]=np.asarray([.62,0,.72,0,.16,.12])[tile]
  image=bpy.data.images.new(role+'_'+kind,width=size,height=size,alpha=kind!='color')
  if kind!='color':image.colorspace_settings.name='Non-Color'
  image.pixels.foreach_set(pixels.ravel())
  image.filepath_raw=str(REVIEW/(role+'_'+kind+('.jpg' if kind=='color' else '.png')))
  image.file_format='JPEG' if kind=='color' else 'PNG';image.save();image.pack();textures[kind]=image
 materials=[]
 for i,name in enumerate(names):
  m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');m.diffuse_color=(*palette[i],1)
  for kind,image in textures.items():
   node=n.new('ShaderNodeTexImage');node.image=image
   if kind=='color':l.new(node.outputs['Color'],p.inputs['Base Color'])
   elif kind=='normal':
    normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.32;l.new(node.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs['Normal'],p.inputs['Normal'])
   else:
    sep=n.new('ShaderNodeSeparateColor');l.new(node.outputs['Color'],sep.inputs[0]);l.new(sep.outputs['Green'],p.inputs['Roughness']);l.new(sep.outputs['Blue'],p.inputs['Metallic'])
  if name=='Threat glow':p.inputs['Emission Color'].default_value=(.8,.22,.025,1);p.inputs['Emission Strength'].default_value=.25
  m.use_backface_culling=False;materials.append(m)
 return materials

def blend(a,b,f):
 f=max(0,min(1,f));return {a:1-f,b:f}

class Sculpt:
 def __init__(self,materials):self.materials=materials;self.parts=[]
 def mesh(self,name,verts,faces,mat,weights,uv=None):
  data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);data.materials.append(self.materials[mat]);layer=data.uv_layers.new(name='Original sculpt atlas')
  for loop in data.loops:
   u,v=uv[loop.vertex_index] if uv else (.5+.25*verts[loop.vertex_index][0],.5+.2*verts[loop.vertex_index][2]);u=max(.008,min(.992,u));v=max(.008,min(.992,v));layer.data[loop.index].uv=((mat%3+u)/3,(mat//3+v)/2)
  for i,c in enumerate(verts):
   w=weights(c,i) if callable(weights) else {weights:1};total=sum(w.values())
   for bone,value in w.items():
    if bone not in ob.vertex_groups:ob.vertex_groups.new(name=bone)
    ob.vertex_groups[bone].add([i],value/total,'REPLACE')
  for face in data.polygons:face.use_smooth=True
  self.parts.append(ob);return ob
 def tube(self,name,points,radii,mat,weights,segments=16):
  pts=[Vector(p) for p in points];verts=[];uv=[]
  for k,center in enumerate(pts):
   axis=pts[min(len(pts)-1,k+1)]-pts[max(0,k-1)];axis.normalize();right=axis.cross(Vector((0,0,1)))
   if right.length<.1:right=axis.cross(Vector((0,1,0)))
   right.normalize();up=axis.cross(right).normalized();radius=radii[k] if hasattr(radii,'__len__') else radii
   if isinstance(radius,(tuple,list)):r1,r2=radius
   else:r1=r2=radius
   for j in range(segments):
    a=j/segments*math.tau;p=center+right*math.cos(a)*r1+up*math.sin(a)*r2;verts.append(tuple(p));uv.append((j/segments,k/max(1,len(pts)-1)))
  faces=[(k*segments+j,k*segments+(j+1)%segments,(k+1)*segments+(j+1)%segments,(k+1)*segments+j) for k in range(len(pts)-1) for j in range(segments)]
  faces += [tuple(reversed(range(segments))),tuple((len(pts)-1)*segments+j for j in range(segments))]
  return self.mesh(name,verts,faces,mat,weights,uv)
 def ellipsoid(self,name,center,radii,mat,bone,rings=12,segments=24):
  verts=[];uv=[]
  for k in range(rings+1):
   latitude=-math.pi/2+(k+.001)/(rings+.002)*math.pi
   for j in range(segments):
    a=j/segments*math.tau;verts.append((center[0]+math.cos(a)*math.cos(latitude)*radii[0],center[1]+math.sin(a)*math.cos(latitude)*radii[1],center[2]+math.sin(latitude)*radii[2]));uv.append((j/segments,k/rings))
  faces=[(k*segments+j,k*segments+(j+1)%segments,(k+1)*segments+(j+1)%segments,(k+1)*segments+j) for k in range(rings) for j in range(segments)]
  return self.mesh(name,verts,faces,mat,bone,uv)
 def plate(self,name,center,size,mat,bone):
  x,y,z=center;w,d,h=size
  return self.mesh(name,[(x-w,y,z-h*.25),(x+w,y,z-h*.25),(x+w*.7,y+d*.7,z+h*.6),(x,y+d,z+h),(x-w*.7,y+d*.7,z+h*.6),(x,y-.03,z+h*.38)],[(0,1,5),(1,2,5),(2,3,5),(3,4,5),(4,0,5),(0,4,3,2,1)],mat,bone)
 def join(self,rig,name):
  bpy.ops.object.select_all(action='DESELECT')
  for p in self.parts:p.select_set(True)
  bpy.context.view_layer.objects.active=self.parts[0];bpy.ops.object.join();body=bpy.context.object;body.name=name;body.parent=rig;mod=body.modifiers.new('Anatomical skin','ARMATURE');mod.object=rig;return body

def rig_for(role):
 arm=bpy.data.armatures.new(role+'_Skeleton');rig=bpy.data.objects.new(role+'_Rig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 specs=[('root',(0,0,0),(0,0,.1),None)]
 if role=='archer':
  specs += [('hips',(0,.08,1.0),(0,.04,1.15),'root'),('spine',(0,.04,1.15),(0,0,1.43),'hips'),('chest',(0,0,1.43),(0,-.025,1.67),'spine'),('neck',(0,-.025,1.67),(0,-.12,1.85),'chest'),('head',(0,-.12,1.85),(0,-.34,1.88),'neck'),('jaw',(0,-.17,1.81),(0,-.39,1.77),'head'),('bow_upper',(.63,-.43,1.5),(.75,-.52,2.12),'forearm.L'),('bow_lower',(.63,-.43,1.5),(.72,-.55,.92),'forearm.L')]
  for side,sign in [('L',1),('R',-1)]:
   specs += [(f'thigh.{side}',(sign*.17,.08,1.03),(sign*.24,-.04,.62),'hips'),(f'shin.{side}',(sign*.24,-.04,.62),(sign*.19,.12,.22),f'thigh.{side}'),(f'foot.{side}',(sign*.19,.12,.22),(sign*.19,-.09,.055),f'shin.{side}')]
  specs += [('arm.L',(.29,0,1.56),(.59,-.14,1.34),'chest'),('forearm.L',(.59,-.14,1.34),(.63,-.43,1.5),'arm.L'),('hand.L',(.63,-.43,1.5),(.66,-.52,1.5),'forearm.L'),('arm.R',(-.29,0,1.56),(-.48,.10,1.32),'chest'),('forearm.R',(-.48,.10,1.32),(-.17,-.22,1.48),'arm.R'),('hand.R',(-.17,-.22,1.48),(.01,-.31,1.49),'forearm.R'),('mantle.L',(.21,.12,1.55),(.40,.27,1.14),'chest'),('mantle.R',(-.21,.12,1.55),(-.40,.27,1.14),'chest')]
 else:
  specs += [('spine',(0,.1,1.15),(0,-.18,1.18),'root'),('chest',(0,-.18,1.18),(0,-.40,1.18),'spine'),('neck',(0,-.40,1.18),(0,-.58,1.13),'chest'),('head',(0,-.58,1.13),(0,-.79,1.08),'neck'),('jaw',(0,-.61,1.04),(0,-.86,.96),'head'),('tail.1',(0,.25,1.14),(0,.70,1.04),'spine'),('tail.2',(0,.70,1.04),(0,1.15,.85),'tail.1'),('tail.3',(0,1.15,.85),(0,1.6,.68),'tail.2'),('tail.4',(0,1.6,.68),(0,1.95,.82),'tail.3')]
  for side,sign in [('L',1),('R',-1)]:
   specs += [(f'wing.{side}',(sign*.12,.02,1.18),(sign*.57,.1,1.19),'spine'),(f'wing_tip.{side}',(sign*.57,.1,1.19),(sign*1.07,.49,.78),f'wing.{side}'),(f'arm.{side}',(sign*.22,-.38,1.1),(sign*.47,-.62,.67),'chest'),(f'claw.{side}',(sign*.47,-.62,.67),(sign*.38,-.99,.62),f'arm.{side}')]
 for name,head,tail,parent in specs:
  bone=arm.edit_bones.new(name);bone.head=head;bone.tail=tail
 # Resolve parents after creation because grown bow branches are declared early.
 for name,head,tail,parent in specs:
  if parent:arm.edit_bones[name].parent=arm.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
 return rig,specs

def archer(s):
 # Continuous torso and digitigrade legs, not a rescaled humanoid block.
 s.tube('Continuous waisted thorax',[(0,.08,.98),(0,.06,1.12),(0,.015,1.31),(0,0,1.48),(0,-.015,1.62),(0,-.02,1.70)],[(.15,.12),(.14,.10),(.22,.14),(.31,.18),(.28,.15),(.16,.13)],0,lambda c,i:blend('spine','chest',(c[2]-1.25)/.30),32)
 s.tube('Muscular forward neck',[(0,-.02,1.58),(0,-.055,1.73),(0,-.13,1.86)],[(.13,.12),(.105,.105),(.1,.10)],0,'neck',24)
 s.tube('Needle beaked skull',[(0,-.1,1.89),(0,-.19,1.94),(0,-.32,1.90),(0,-.45,1.83),(0,-.48,1.80)],[(.115,.13),(.14,.12),(.10,.085),(.046,.043),(.008,.008)],1,'head',32)
 s.tube('Working lower mandible',[(0,-.16,1.81),(0,-.31,1.77),(0,-.45,1.79)],[(.07,.028),(.062,.027),(.013,.012)],3,'jaw',18)
 for side,sign in [('L',1),('R',-1)]:
  path=[(sign*.17,.08,1.05),(sign*.20,.02,.89),(sign*.24,-.04,.62),(sign*.22,.02,.40),(sign*.19,.12,.22)]
  s.tube('Sinewed leg '+side,path,[.12,.11,.075,.060,.043],0,lambda c,i,si=side:blend('thigh.'+si,'shin.'+si,max(0,min(1,(.76-c[2])/.26))),24)
  s.tube('Planted elongated foot '+side,[(sign*.19,.13,.22),(sign*.19,.045,.12),(sign*.19,-.10,.057)],[(.048,.052),(.067,.05),(.08,.035)],1,'foot.'+side,22)
  for j in [-1,0,1]:
   x=sign*.19+j*.045;s.tube('Three hooked toes',[(x,-.075,.065),(x,-.14,.055),(x,-.205,.027)],[.025,.018,.003],2,'foot.'+side,10)
  # Long face crest and layered plates define creature rather than helmeted soldier.
  s.tube('Porcelain swept antenna '+side,[(sign*.09,-.09,1.97),(sign*.17,.03,2.12),(sign*.19,.11,2.27),(sign*.14,.14,2.32)],[.033,.037,.021,.003],1,'head',16)
  s.ellipsoid('Deep eye socket '+side,(sign*.105,-.25,1.936),(.040,.052,.034),0,'head',8,18)
  s.ellipsoid('Amber compound eye '+side,(sign*.127,-.255,1.942),(.014,.029,.014),4,'head',8,16)
  for k in range(4):
   s.plate('Grown rib armour '+side,(sign*(.17+k*.021),-.13,1.55-k*.095),(.15,.13,.085),1,'chest' if k<2 else 'spine')
  s.tube('Shoulder mantle tendon '+side,[(sign*.19,.1,1.64),(sign*.4,.21,1.47),(sign*.43,.28,1.22)],[(.09,.06),(.12,.04),(.05,.017)],5,'mantle.'+side,20)
  for k in range(3):s.plate('Mantle rim '+side,(sign*(.30+k*.055),.18+k*.03,1.54-k*.10),(.09,.13,.12),2,'mantle.'+side)
 s.tube('Left grown draw arm',[(.29,0,1.56),(.48,-.06,1.43),(.59,-.14,1.34),(.61,-.31,1.43),(.63,-.43,1.50)],[.10,.088,.061,.046,.043],0,lambda c,i:blend('arm.L','forearm.L',(i//20/4-.35)/.3),20)
 s.tube('Right drawing arm',[(-.29,0,1.56),(-.43,.07,1.45),(-.48,.10,1.32),(-.34,-.05,1.4),(-.17,-.22,1.48)],[.10,.086,.062,.05,.04],0,lambda c,i:blend('arm.R','forearm.R',(i//20/4-.35)/.3),20)
 for side,sign,center in [('L',1,(.63,-.43,1.5)),('R',-1,(-.17,-.22,1.48))]:
  x,y,z=center;s.ellipsoid('Talon palm '+side,center,(.047,.075,.045),1,'hand.'+side,8,18)
  for j in [-1,0,1]:s.tube('Grasping finger '+side,[(x+j*.025,y-.03,z),(x+j*.03,y-.09,z-.012),(x+j*.027,y-.13,z+.008)],[.012,.009,.003],1,'hand.'+side,8)
 # The weapon grows from the left forearm. Upper/lower limbs bend as separate bones.
 for upper,sign in [(True,1),(False,-1)]:
  bone='bow_upper' if upper else 'bow_lower';points=[]
  for k in range(12):
   f=k/11;points.append((.64+.13*math.sin(f*math.pi*.85),-.44-.17*f,1.50+sign*.64*f))
  s.tube('Living bow limb '+str(upper),points,[.055*(1-k/13) for k in range(12)],1,bone,18)
  s.tube('Bow nerve filament '+str(upper),[points[-1],(.60,-.52,1.50)],[.006,.008],4,bone,8)
 # Sternum channels announce attack without recolouring the entire body.
 s.tube('Sternum warning fissure',[(0,-.163,1.59),(0,-.193,1.47),(0,-.156,1.30)],[.015,.009,.006],4,'chest',10)
 for k in range(4):s.plate('Dorsal armour',(0,.15,1.53-k*.12),(.14,.18,.14),2,'chest' if k<2 else 'spine')

def shade(s):
 s.tube('Continuous ray thorax',[(0,.42,1.15),(0,.20,1.21),(0,-.04,1.23),(0,-.26,1.20),(0,-.47,1.14)],[(.08,.065),(.20,.12),(.30,.15),(.28,.12),(.14,.09)],0,lambda c,i:blend('spine','chest',(.1-c[1])/.5),32)
 s.tube('Forward neck',[(0,-.35,1.16),(0,-.5,1.14),(0,-.64,1.11)],[(.14,.10),(.12,.095),(.10,.075)],0,'neck',24)
 s.tube('Ray skull',[(0,-.53,1.15),(0,-.64,1.19),(0,-.78,1.14),(0,-.91,1.08)],[(.10,.09),(.16,.13),(.13,.09),(.025,.035)],1,'head',28)
 s.tube('Articulated underside jaw',[(0,-.59,1.07),(0,-.74,1.02),(0,-.90,1.06)],[(.085,.035),(.09,.04),(.025,.014)],3,'jaw',18)
 # Wings form broad continuous membranes with radial folds, weighted across two limbs.
 for side,sign in [('L',1),('R',-1)]:
  verts=[];uv=[];rows=17;segs=19
  for k in range(rows):
   span=k/(rows-1)
   for j in range(segs):
    f=j/(segs-1);y=-.30+f*1.05;edge=1.04*(math.sin(math.pi*(f*.80+.08))**.55)
    x=sign*(.12+span*edge);z=1.20-span*span*(.12+.22*f)+.035*math.sin(f*math.pi*6+span*.7)*span
    verts.append((x,y,z));uv.append((span,f))
  faces=[(k*segs+j,k*segs+j+1,(k+1)*segs+j+1,(k+1)*segs+j) for k in range(rows-1) for j in range(segs-1)]
  s.mesh('Ribbed manta membrane '+side,verts,faces,5,lambda c,i,si=side:blend('wing.'+si,'wing_tip.'+si,(abs(c[0])-.36)/.45),uv)
  # Stiff leading ray and trailing fin fingers are visible anatomical supports.
  leading=[(sign*.12,-.30,1.20),(sign*.5,-.27,1.20),(sign*.86,-.18,1.12),(sign*1.04,-.01,1.05)]
  s.tube('Wing leading ray '+side,leading,[.052,.043,.023,.004],1,lambda c,i,si=side:blend('wing.'+si,'wing_tip.'+si,(abs(c[0])-.36)/.45),14)
  for f in [.31,.55,.78]:
   edge=1.04*(math.sin(math.pi*(f*.80+.08))**.55)
   s.tube('Radial membrane spar '+side,[(sign*.16,-.30+f*1.05,1.2),(sign*(.12+edge*.55),-.30+f*1.05,1.16-f*.08),(sign*(.12+edge),-.30+f*1.05,1.08-f*.22)],[.018,.012,.003],2,lambda c,i,si=side:blend('wing.'+si,'wing_tip.'+si,(abs(c[0])-.36)/.45),10)
  path=[(sign*.22,-.38,1.10),(sign*.39,-.49,.88),(sign*.47,-.62,.67),(sign*.45,-.83,.58),(sign*.38,-.99,.62)]
  s.tube('Suspended grappling appendage '+side,path,[.076,.061,.038,.026,.012],0,lambda c,i,si=side:blend('arm.'+si,'claw.'+si,(i//18/4-.35)/.4),18)
  for j in [-1,1]:s.tube('Split hooked claw '+side,[(sign*.38,-.96,.62),(sign*(.38+j*.05),-1.07,.64),(sign*(.38+j*.06),-1.1,.72)],[.018,.014,.002],1,'claw.'+side,10)
  s.ellipsoid('Hollow eye well '+side,(sign*.118,-.71,1.205),(.046,.058,.025),0,'head',8,18)
  s.ellipsoid('Eye warning slit '+side,(sign*.124,-.727,1.213),(.013,.030,.012),4,'head',8,16)
  s.tube('Swept head feeler '+side,[(sign*.12,-.59,1.24),(sign*.20,-.47,1.38),(sign*.26,-.31,1.41)],[.023,.017,.002],1,'head',12)
 # Tail has four bending segments; filaments stay rooted in the same body hierarchy.
 points=[]
 for k in range(25):
  f=k/24;points.append((.045*math.sin(f*math.pi*2),.28+1.68*f,1.14-.47*math.sin(f*math.pi*.80)))
 def tail_weights(c,i):
  f=(c[1]-.28)/1.68;segment=min(2,max(0,int(f*4)));return blend('tail.'+str(segment+1),'tail.'+str(segment+2),f*4-segment)
 s.tube('Four segment tapering tail',points,[.075*(1-k/26) for k in range(25)],0,tail_weights,18)
 for sign in [-1,1]:
  thread=[(sign*.1,.32,1.07),(sign*.19,.69,.95),(sign*.19,1.10,.75),(sign*.11,1.55,.62),(sign*.06,1.9,.75)]
  s.tube('Tail silk filament',thread,[.012,.011,.008,.005,.0015],2,lambda c,i:tail_weights(c,i),9)
 for k in range(5):s.plate('Dorsal tide plate',(0,-.2+k*.16,1.31-k*.025),(.13-k*.012,.16,.055),1,'chest' if k<2 else 'spine')
 s.tube('Ventral warning vein',[(0,-.40,1.055),(0,-.22,1.065),(0,.02,1.07)],[.012,.016,.006],4,'chest',10)


def actions(role,rig):
 durations={'idle':2.4,'move':1.0 if role=='archer' else 1.4,'windup':1.1 if role=='archer' else .9,'release':.2 if role=='archer' else .4,'recover':1.1 if role=='archer' else 1.3,'hit':.3,'death':1.1}
 if role=='shade':durations['phase']=1.2
 pose=rig.pose.bones
 for b in pose:b.rotation_mode='XYZ'
 for name,duration in durations.items():
  action=bpy.data.actions.new(name);rig.animation_data_create();rig.animation_data.action=action
  n=round(duration*30)
  for k in range(n+1):
   f=k/n;wave=math.sin(f*math.tau)
   for b in pose:b.rotation_euler=(0,0,0);b.location=(0,0,0)
   if role=='archer':
    pose['chest'].rotation_euler.x=.015*wave;pose['head'].rotation_euler.z=.025*math.sin(f*math.tau+.4)
    for side,offset in [('L',0),('R',.5)]:
     pose['mantle.'+side].rotation_euler.x=.025*math.sin((f+offset)*math.tau)
     if name=='move':
      cycle=math.sin((f+offset)*math.tau);pose['thigh.'+side].rotation_euler.x=cycle*.32;pose['shin.'+side].rotation_euler.x=max(0,-cycle)*.48;pose['foot.'+side].rotation_euler.x=-max(0,cycle)*.10
    if name in ['windup','release','recover']:
     amount=f*f*(3-2*f) if name=='windup' else 1-f if name=='recover' else 1-f*.95
     pose['chest'].rotation_euler.z=-.22*amount;pose['arm.R'].rotation_euler.x=-.36*amount;pose['arm.R'].rotation_euler.z=.34*amount;pose['forearm.R'].rotation_euler.z=-.52*amount;pose['bow_upper'].rotation_euler.x=.15*amount;pose['bow_lower'].rotation_euler.x=-.15*amount;pose['head'].rotation_euler.z=.15*amount
     if name=='release':pose['chest'].rotation_euler.x=.065*math.sin(f*math.pi);pose['jaw'].rotation_euler.x=.14*math.sin(f*math.pi)
   else:
    pose['spine'].rotation_euler.x=.025*wave
    for side,sign in [('L',1),('R',-1)]:
     pose['wing.'+side].rotation_euler.y=sign*.065*wave;pose['wing_tip.'+side].rotation_euler.y=sign*.12*math.sin(f*math.tau+.5)
     pose['arm.'+side].rotation_euler.x=.04*math.sin(f*math.tau+.7)
    for i in range(1,5):pose['tail.'+str(i)].rotation_euler.z=.08*math.sin(f*math.tau+i*.45)
    if name=='move':
     for side,sign in [('L',1),('R',-1)]:pose['wing.'+side].rotation_euler.y=sign*.11*wave;pose['wing_tip.'+side].rotation_euler.y=sign*.21*math.sin(f*math.tau+.5)
    if name in ['windup','release','recover']:
     amount=f*f*(3-2*f) if name=='windup' else 1-f if name=='recover' else 1-.65*f
     pose['chest'].rotation_euler.x=-.18*amount;pose['jaw'].rotation_euler.x=.40*amount
     for side,sign in [('L',1),('R',-1)]:pose['wing.'+side].rotation_euler.y=-sign*.32*amount;pose['wing_tip.'+side].rotation_euler.y=-sign*.35*amount;pose['arm.'+side].rotation_euler.x=-.46*amount;pose['claw.'+side].rotation_euler.x=.25*amount
    if name=='phase':
     amount=math.sin(f*math.pi)
     for side,sign in [('L',1),('R',-1)]:pose['wing.'+side].rotation_euler.y=sign*.8*amount;pose['wing_tip.'+side].rotation_euler.y=sign*.42*amount
   if name=='hit':pose['chest'].rotation_euler.x=-.18*math.sin(f*math.pi);pose['head'].rotation_euler.z=.12*math.sin(f*math.pi)
   if name=='death':
    amount=f*f*(3-2*f);pose['root'].location.z=-.6*amount;pose['root'].rotation_euler.y=.7*amount
    if role=='archer':
     for side in ['L','R']:pose['thigh.'+side].rotation_euler.x=-.7*amount;pose['shin.'+side].rotation_euler.x=1.25*amount
    else:
     for side,sign in [('L',1),('R',-1)]:pose['wing.'+side].rotation_euler.y=sign*.9*amount
   for b in pose:
    b.keyframe_insert(data_path='rotation_euler',frame=k,group=b.name)
    if b.name=='root':b.keyframe_insert(data_path='location',frame=k,group=b.name)
  action.use_fake_user=True
 rig.animation_data.action=None
 for b in pose:b.rotation_euler=(0,0,0);b.location=(0,0,0)
 return durations

def render_review(role,rig):
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=700;scene.render.resolution_y=760;scene.render.resolution_percentage=100
 scene.world=bpy.data.worlds.new('Creature review world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.09,.12,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 for position,energy,color,size in [((-3,4,5),900,(1,.82,.60),4),((3,3,3),700,(.52,.72,1),3),((2,-3,4),1000,(1,.48,.18),3)]:
  light=bpy.data.lights.new('Review area','AREA');light.energy=energy;light.color=color;light.size=size;obj=bpy.data.objects.new('Review area',light);scene.collection.objects.link(obj);obj.location=position;obj.rotation_euler=(Vector((0,0,1.1))-obj.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.008));floor=bpy.context.object;m=bpy.data.materials.new('Review floor');m.diffuse_color=(.055,.05,.06,1);floor.data.materials.append(m)
 data=bpy.data.cameras.new('Review camera');camera=bpy.data.objects.new('Review camera',data);scene.collection.objects.link(camera);camera.location=(3.3,5.0,2.8) if role=='archer' else (3.5,4.8,2.8);target=Vector((0,0,1.10));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=65;scene.camera=camera
 scene.render.filepath=str(REVIEW/(role+'-guard.png'));bpy.ops.render.render(write_still=True)

reports={}
for role in ROLES:
 reset();materials=make_materials(role);rig,specs=rig_for(role);sculpt=Sculpt(materials);archer(sculpt) if role=='archer' else shade(sculpt);body=sculpt.join(rig,role+'_Skinned');durations=actions(role,rig)
 # Blender−Y anatomy becomes GLTF+Z by normal conversion. This one object yaw
 # makes the exported scene face GLTF−Z, with no extra runtime correction.
 rig.rotation_euler.z=math.pi
 if role=='archer':
  socket=bpy.data.objects.new('muzzle',None);bpy.context.collection.objects.link(socket);socket.parent=rig;socket.parent_type='BONE';socket.parent_bone='forearm.L';socket.location=(.0,.11,.0)
  # Set exact rig-local socket from model coordinates, independent of bone roll.
  socket.matrix_world=rig.matrix_world @ __import__('mathutils').Matrix.Translation((.66,-.64,1.50))
 name='archer-thorn' if role=='archer' else 'shade-manta';title='Veilleur des fils' if role=='archer' else 'Raie du reflet'
 bpy.context.view_layer.update()
 coords=[body.matrix_world@v.co for v in body.data.vertices]
 bounds={'min':[min(v[i] for v in coords) for i in range(3)],'max':[max(v[i] for v in coords) for i in range(3)]}
 meta={'version':1,'name':title,'role':role,'front':'-Z','units':'metres','generator':'scripts/build_enemy_v16.py','original_art':True,'third_party_art':False,'clips':durations,'rig_bones':len(specs),'vertices':len(body.data.vertices),'source':f'assets/source/creatures/{name}.blend','warning_material':'Threat glow','body_height':round(bounds['max'][2]-bounds['min'][2],6),'bind_bounds_blender':bounds,'collision_core_radius':.48 if role=='archer' else .55,'contact_policy':'digitigrade anatomy; runtime locomotion and foot planting remain separate' if role=='archer' else 'levitating anatomy; no ground-foot claim','author':'Les Royaumes de l’Éclipse project, original generated sculpture','release_event_at':2/30 if role=='archer' else 0,'fps':30}
 if role=='shade':
  meta['footprint']={'front':1.102,'back':1.963,'lateral_deployed':1.160,'lateral_folded':.516,'local_forward_axis':'-Z'}
  meta['wing_fold']={'axis':'local_X','main_radians':1.2,'tip_radians':.66,'same_positive_sign_both_sides':True,'bones':['wing.L','wing.R'],'tip_bones':['wing_tip.L','wing_tip.R'],'loader_bones':['wingL','wingR'],'loader_tip_bones':['wing_tipL','wing_tipR'],'observed_max_folded_y':2.24,'scope':'bind-pose real skinned geometry; runtime checks dynamic clearance'}
 rig['enemyProduction']=json.dumps(meta,ensure_ascii=False)
 bpy.context.view_layer.objects.active=rig;bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);body.select_set(True)
 if role=='archer':socket.select_set(True)
 source=SOURCE/(name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
 target=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_animation_mode='ACTIONS',export_nla_strips=False,export_force_sampling=True,export_skins=True,export_def_bones=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_yup=True)
 meta['sha256']=hashlib.sha256(target.read_bytes()).hexdigest();meta['bytes']=target.stat().st_size;reports[role]=meta;(OUT/(name+'-PROVENANCE.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 print('EXPORTED_ENEMY '+json.dumps(meta,ensure_ascii=False),flush=True)
 if '--no-render' not in ARGS:render_review(role,rig)
(OUT/'ENEMIES-PRODUCTION-1.6.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
