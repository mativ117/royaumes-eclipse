"""Original, articulated expedition characters. Run with Blender 4.3 in background.
blender --background --factory-startup --python scripts/author_characters.py
Exports two skinned GLBs with thirteen authored in-place actions; no downloaded art.
"""
import bpy,math,os,json,hashlib
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/characters';OUT.mkdir(parents=True,exist_ok=True)
FPS=30

def material(name,color,metal=0,rough=.6,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m

def create(role):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for a in list(bpy.data.actions):bpy.data.actions.remove(a)
 heavy=role=='rempart'
 palette={'steel':material('Obsidian steel',(.12,.18,.20),.75,.32),'gold':material('Brushed copper',(.55,.36,.16),.8,.3),'suit':material('Woven charcoal',(.045,.055,.072),.05,.85),'cloak':material('Oxide mantle',(.14,.045,.035) if heavy else (.27,.035,.035),.03,.92),'glow':material('Ivory slit',(.66,.72,.61),.3,.25,.5),'leather':material('Dark leather',(.065,.045,.035),.1,.8)}
 arm=bpy.data.armatures.new('Expedition_Skeleton');rig=bpy.data.objects.new(role+'_Rig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 specs=[('root',(0,0,0),(0,0,.15),None),('pelvis',(0,0,1.02),(0,0,1.23),'root'),('spine',(0,0,1.23),(0,0,1.48),'pelvis'),('chest',(0,0,1.48),(0,0,1.73),'spine'),('neck',(0,0,1.73),(0,0,1.86),'chest'),('head',(0,0,1.86),(0,0,2.12),'neck'),('cape_mid',(0,.18,1.65),(0,.28,1.1),'chest'),('cape_tip',(0,.28,1.1),(0,.43,.45),'cape_mid')]
 for side,sign in [('L',1),('R',-1)]:
  specs.extend([(f'upper_arm.{side}',(sign*.27,0,1.66),(sign*.45,0,1.35),'chest'),(f'forearm.{side}',(sign*.45,0,1.35),(sign*.48,-.03,1.06),f'upper_arm.{side}'),(f'hand.{side}',(sign*.48,-.03,1.06),(sign*.48,-.04,.94),f'forearm.{side}'),(f'thigh.{side}',(sign*.145,0,1.02),(sign*.15,-.015,.57),'pelvis'),(f'shin.{side}',(sign*.15,-.015,.57),(sign*.15,.015,.14),f'thigh.{side}'),(f'foot.{side}',(sign*.15,.015,.14),(sign*.15,-.20,.08),f'shin.{side}')])
 specs.extend([('muzzle',(-.48,-.89,1.26),(-.48,-.99,1.26),'hand.R'),('blade_tip',(-.48,-.04,.05),(-.48,-.04,.01),'hand.R')])
 for name,head,tail,parent in specs:
  b=arm.edit_bones.new(name);b.head=head;b.tail=tail
  if parent:b.parent=arm.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
 pieces=[]
 def finish(obj,name,bone,mat):
  obj.name=name;obj.data.materials.append(palette[mat]);bpy.context.view_layer.objects.active=obj;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  if bone:obj.vertex_groups.new(name=bone).add(list(range(len(obj.data.vertices))),1,'REPLACE')
  for f in obj.data.polygons:f.use_smooth=True
  pieces.append(obj);return obj
 def ellipsoid(name,pos,scale,bone,mat):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=pos);obj=bpy.context.object;obj.scale=scale;return finish(obj,name,bone,mat)
 def plate(name,pos,scale,bone,mat,rot=(0,0,0)):
  bpy.ops.mesh.primitive_cube_add(size=1,location=pos,rotation=rot);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  bevel=o.modifiers.new('Forged edges','BEVEL');bevel.width=.025;bevel.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
  return finish(o,name,bone,mat)
 def shaft(name,a,b,r,bone,mat,r2=None):
  a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r,radius2=r if r2 is None else r2,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return finish(o,name,bone,mat)
 # Shaped torso, weighted across pelvis, spine and chest rather than separate cubes.
 rings=[(.99,.21,.13),(1.14,.23,.14),(1.30,.21,.135),(1.49,.28,.17),(1.65,.30,.15),(1.74,.15,.10)]
 verts=[(math.cos(j/16*math.tau)*rx,math.sin(j/16*math.tau)*ry,z) for z,rx,ry in rings for j in range(16)]
 faces=[(i*16+j,i*16+(j+1)%16,(i+1)*16+(j+1)%16,(i+1)*16+j) for i in range(len(rings)-1) for j in range(16)]
 me=bpy.data.meshes.new('Tailored torso');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Tailored torso',me);bpy.context.collection.objects.link(o);finish(o,o.name,None,'suit')
 for bn in ['pelvis','spine','chest']:o.vertex_groups.new(name=bn)
 for i,v in enumerate(verts):
  z=v[2];weight=max(0,min(1,(z-1.25)/.3));o.vertex_groups['chest'].add([i],weight,'REPLACE');o.vertex_groups['spine' if z>=1.16 else 'pelvis'].add([i],1-weight,'REPLACE')
 ellipsoid('Breastplate',(0,-.105,1.49),(.29,.11,.28),'chest','steel')
 plate('Copper sternum',(0,-.208,1.49),(.045,.025,.45),'chest','gold')
 plate('Waist clasp',(0,-.14,1.11),(.14,.06,.11),'pelvis','gold')
 ellipsoid('Collar',(0,0,1.76),(.14,.13,.07),'neck','gold')
 ellipsoid('Helmet',(0,0,1.99),(.165,.145,.225),'head','steel' if heavy else 'suit')
 plate('Face mask',(0,-.12,1.98),(.27,.08,.25),'head','steel')
 plate('Visor slit',(0,-.166,2.035),(.235,.015,.025),'head','glow')
 if heavy:
  plate('Helmet crest',(0,.005,2.18),(.045,.25,.10),'head','gold')
 else:
  ellipsoid('Hood crown',(0,.025,2.05),(.195,.165,.205),'head','cloak')
  plate('Hood face',(0,-.155,2.035),(.235,.02,.025),'head','glow')
 for side,sign in [('L',1),('R',-1)]:
  s=sign
  shaft('Upper sleeve '+side,(s*.27,0,1.64),(s*.45,0,1.35),.105,'upper_arm.'+side,'suit',.085)
  ellipsoid('Shoulder '+side,(s*.32,0,1.65),(.17 if heavy else .12,.17,.13),'upper_arm.'+side,'steel')
  ellipsoid('Shoulder rim '+side,(s*.34,-.01,1.71),(.15 if heavy else .10,.15,.055),'upper_arm.'+side,'gold')
  ellipsoid('Elbow '+side,(s*.45,0,1.35),(.09,.09,.085),'forearm.'+side,'gold')
  shaft('Vambrace '+side,(s*.45,0,1.34),(s*.48,-.03,1.09),.085,'forearm.'+side,'steel',.065)
  ellipsoid('Glove '+side,(s*.48,-.035,1.01),(.065,.07,.09),'hand.'+side,'leather')
  shaft('Thigh '+side,(s*.145,0,1.04),(s*.15,-.015,.60),.115,'thigh.'+side,'suit',.09)
  ellipsoid('Knee '+side,(s*.15,-.045,.58),(.10,.10,.11),'shin.'+side,'gold')
  shaft('Greave '+side,(s*.15,-.015,.54),(s*.15,.015,.16),.085,'shin.'+side,'steel',.065)
  ellipsoid('Boot '+side,(s*.15,-.075,.09),(.10,.205,.09),'foot.'+side,'leather')
  plate('Toe cap '+side,(s*.15,-.21,.09),(.18,.13,.10),'foot.'+side,'steel')
 # Flowing mantle with articulated lower bones and a copper hem.
 verts=[];faces=[];rows=9;cols=9
 for row in range(rows):
  f=row/(rows-1);z=1.72-f*(1.05 if heavy else 1.25);width=.31+f*.15
  for col in range(cols):
   x=(col/(cols-1)*2-1)*width;y=.15+f*.24+math.sin(col/(cols-1)*math.pi*4)*(.015+f*.035);verts.append((x,y,z))
 for row in range(rows-1):
  for col in range(cols-1):i=row*cols+col;faces.append((i,i+1,i+cols+1,i+cols))
 me=bpy.data.meshes.new('Mantle weave');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Mantle',me);bpy.context.collection.objects.link(o);finish(o,'Mantle',None,'cloak')
 for bone in ['chest','cape_mid','cape_tip']:o.vertex_groups.new(name=bone)
 for i,v in enumerate(verts):
  f=(1.72-v[2])/(1.05 if heavy else 1.25)
  if f<.45:a,b,w='chest','cape_mid',f/.45
  else:a,b,w='cape_mid','cape_tip',(f-.45)/.55
  o.vertex_groups[a].add([i],1-w,'REPLACE');o.vertex_groups[b].add([i],w,'REPLACE')
 solid=o.modifiers.new('Woven thickness','SOLIDIFY');solid.thickness=.007
 weapon_start=len(pieces)
 # Weapons authored in the hand's rest position; the rig carries them through motion.
 if heavy:
  plate('Rifle receiver',(-.48,-.22,1.18),(.12,.38,.14),'hand.R','steel')
  shaft('Rifle barrel',(-.48,-.35,1.25),(-.48,-.88,1.25),.028,'hand.R','steel')
  shaft('Copper shroud',(-.48,-.40,1.25),(-.48,-.70,1.25),.04,'hand.R','gold')
  plate('Stock',(-.48,.02,1.16),(.10,.25,.13),'hand.R','leather')
  plate('Bracer shield',(.48,-.09,1.27),(.22,.09,.34),'forearm.L','steel')
 else:
  shaft('Sword grip',(-.48,-.04,1.04),(-.48,-.04,.88),.026,'hand.R','leather')
  plate('Sword guard',(-.48,-.04,.88),(.24,.07,.035),'hand.R','gold')
  # Tapered blade, broad at the guard, narrow at its point.
  vs=[(-.52,-.055,.88),(-.44,-.055,.88),(-.48,-.055,.03),(-.52,-.025,.88),(-.44,-.025,.88),(-.48,-.025,.03)]
  me=bpy.data.meshes.new('Forged blade');me.from_pydata(vs,[],[(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)]);me.update();o=bpy.data.objects.new('Sword blade',me);bpy.context.collection.objects.link(o);finish(o,o.name,'hand.R','gold')
 # Apply modifiers and merge into a true skinned mesh with shared material slots.
 exported=[]
 for group,label in [(pieces[:weapon_start],'Skinned'),(pieces[weapon_start:],'Weapon')]:
  bpy.ops.object.select_all(action='DESELECT')
  for o in group:
   o.select_set(True);bpy.context.view_layer.objects.active=o
   for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
  bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();body=bpy.context.object;body.name=role+'_'+label
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);body.parent=rig
  mod=body.modifiers.new('Expedition deformation','ARMATURE');mod.object=rig;exported.append(body)
 bpy.context.view_layer.objects.active=rig
 for p in rig.pose.bones:p.rotation_mode='XYZ'
 # Continuous, in-place cycles; actual displacement belongs to the controller.
 def pose(name,phase):
  P=rig.pose.bones;D={bn:[0,0,0] for bn in P.keys()};Z=0
  D['cape_mid'][0]=.06*math.sin(phase*math.tau);D['cape_tip'][0]=.10*math.sin(phase*math.tau+.5)
  if name in ['walk','run']:
   amp=.45 if name=='walk' else .68;cycle=math.sin(phase*math.tau)
   for side,s in [('L',1),('R',-1)]:
    D['thigh.'+side][0]=amp*cycle*s;D['shin.'+side][0]=max(0,-cycle*s)*(.7 if name=='walk' else 1.1);D['foot.'+side][0]=-.2*cycle*s
    D['upper_arm.'+side][0]=-.35*cycle*s;D['forearm.'+side][0]=-.18
   D['chest'][2]=cycle*.07;Z=abs(math.sin(phase*math.tau))*(.025 if name=='walk' else .045)
  elif name.startswith('attack'):
   number=int(name[-1]);side=1 if number!=2 else -1
   if phase<.26:
    k=phase/.26;D['upper_arm.R']=[-1.1*k,.2*k,-side*.6*k];D['forearm.R']=[-.75*k,0,0];D['chest'][2]=-side*.45*k
   elif phase<.55:
    k=(phase-.26)/.29;k=k*k*(3-2*k);D['upper_arm.R']=[-1.1+2*k,.2-.4*k,side*(-.6+1.2*k)];D['forearm.R']=[-.75+.55*k,0,0];D['chest'][2]=side*(-.45+1*k)
   else:
    k=(1-phase)/.45;D['upper_arm.R']=[.9*k,-.2*k,side*.6*k];D['forearm.R']=[-.2*k,0,0];D['chest'][2]=side*.55*k
   if number==3:D['chest'][0]=-.2*math.sin(phase*math.pi);D['upper_arm.R'][0]*=1.25
   D['thigh.L'][0]=.12;D['thigh.R'][0]=-.12
  elif name=='hit':
   f=math.sin(phase*math.pi);D['chest'][0]=.20*f;D['chest'][2]=-.14*f;D['neck'][0]=-.1*f
  elif name=='shot':
   pulse=math.exp(-((phase-.25)/.10)**2)
   D['chest'][0]=-.045*pulse;D['upper_arm.R'][0]=-.18-.07*pulse;D['forearm.R'][0]=-.08;D['upper_arm.L'][0]=-.5;D['forearm.L'][0]=-.65
  elif name in ['dash','leap']:
   f=math.sin(phase*math.pi);D['chest'][0]=.3*f;D['thigh.L'][0]=-.6*f;D['thigh.R'][0]=.6*f;D['shin.L'][0]=.8*f;D['shin.R'][0]=.9*f;D['upper_arm.R'][0]=.5*f
  elif name=='shield':
   D['upper_arm.L'][0]=-.8;D['forearm.L'][0]=-1.1;D['chest'][2]=-.12
  elif name=='interact':
   f=math.sin(phase*math.pi);D['upper_arm.R'][0]=-.9*f;D['forearm.R'][0]=-.5*f;D['chest'][0]=-.1*f
  elif name=='carry':
   D['upper_arm.L'][0]=D['upper_arm.R'][0]=-.7;D['forearm.L'][0]=D['forearm.R'][0]=-.9
  else:D['chest'][0]=.012*math.sin(phase*math.tau);D['head'][2]=.025*math.sin(phase*math.tau)
  for bn,rot in D.items():P[bn].rotation_euler=rot
  P['root'].location.z=Z
 clips={'idle':2,'walk':1.1,'run':.75,'attack1':.65,'attack2':.65,'attack3':.9,'shot':.45,'dash':.3,'leap':.75,'shield':1,'interact':.65,'carry':1.2,'hit':.3}
 for name,duration in clips.items():
  action=bpy.data.actions.new(name);rig.animation_data_create();rig.animation_data.action=action;n=round(duration*FPS)
  for frame in range(n+1):
   pose(name,frame/n)
   for bone in rig.pose.bones:
    bone.keyframe_insert(data_path='rotation_euler',frame=frame+1,group=bone.name)
   rig.pose.bones['root'].keyframe_insert(data_path='location',frame=frame+1,group='root')
  action.use_fake_user=True
 rig.animation_data.action=None
 for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
 scene=bpy.context.scene;scene.render.fps=FPS
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);
 for body in exported:body.select_set(True)
 bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.gltf(filepath=str(OUT/(role+'.glb')),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_nla_strips=False,export_force_sampling=True,export_skins=True,export_def_bones=False,export_materials='EXPORT',export_cameras=False,export_lights=False)
 print('AUTHORED',role,(OUT/(role+'.glb')).stat().st_size)

for role in ['rempart','voltigeur']:create(role)
(OUT/'PROVENANCE.json').write_text(json.dumps({'author':'Original models authored for Les Royaumes de l’Éclipse','generator':'scripts/author_characters.py','blender':'4.3.2','third_party_art':False,'files':['rempart.glb','voltigeur.glb'],'sha256':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['rempart.glb','voltigeur.glb']},'clips':['idle','walk','run','attack1','attack2','attack3','shot','dash','leap','shield','interact','carry','hit']},indent=2)+'\n')
