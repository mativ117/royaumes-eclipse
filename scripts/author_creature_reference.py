"""Original Fauche-Cendre quadruped: continuous anatomy, shared atlas and articulated rig.
Blender 4.3 CPU. Only writes assets/creatures and /tmp/creature-reference.
"""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/creatures';OUT.mkdir(exist_ok=True);PREVIEW=Path('/tmp/creature-reference');PREVIEW.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
arm=bpy.data.armatures.new('FaucheCendreSkeleton');rig=bpy.data.objects.new('FaucheCendreRig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
specs=[('root',(0,0,0),(0,0,.1),None),('hips',(0,.32,.66),(0,.12,.74),'root'),('spine',(0,.12,.74),(0,-.14,.82),'hips'),('chest',(0,-.14,.82),(0,-.40,.81),'spine'),('neck',(0,-.40,.81),(0,-.64,.71),'chest'),('head',(0,-.64,.71),(0,-.94,.62),'neck'),('jaw',(0,-.68,.61),(0,-.94,.55),'head'),('tail_1',(0,.43,.69),(0,.75,.63),'hips'),('tail_2',(0,.75,.63),(0,1.00,.72),'tail_1'),('tail_3',(0,1.00,.72),(0,1.21,.84),'tail_2')]
for side,sign in [('L',1),('R',-1)]:
 specs.extend([(f'fore_upper.{side}',(sign*.25,-.34,.80),(sign*.32,-.19,.43),'chest'),(f'fore_lower.{side}',(sign*.32,-.19,.43),(sign*.25,-.44,.11),f'fore_upper.{side}'),(f'fore_foot.{side}',(sign*.25,-.44,.11),(sign*.25,-.60,.055),f'fore_lower.{side}'),(f'hind_upper.{side}',(sign*.23,.34,.70),(sign*.32,.12,.41),'hips'),(f'hind_lower.{side}',(sign*.32,.12,.41),(sign*.23,.40,.12),f'hind_upper.{side}'),(f'hind_foot.{side}',(sign*.23,.40,.12),(sign*.23,.24,.06),f'hind_lower.{side}')])
for name,head,tail,parent in specs:
 b=arm.edit_bones.new(name);b.head=head;b.tail=tail
 if parent:b.parent=arm.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
# Four original materials and one embedded atlas; no external art or external texture request.
colors=[(.065,.072,.085),(.28,.30,.33),(.48,.47,.43),(.85,.26,.035)];materials=[]
for kind in ['base','orm','normal']:
 size=512;yy,xx=np.mgrid[0:size,0:size];index=(xx//256)+(yy//256)*2;u=(xx%256)/256;v=(yy%256)/256;noise=np.random.default_rng(441).random((size,size))-.5;image=bpy.data.images.new('FaucheCendre_'+kind,width=size,height=size,alpha=True);a=np.ones((size,size,4),dtype=np.float32)
 if kind=='base':
  for i,color in enumerate(colors):
   reg=index==i;variation=1+noise*.1+.035*np.sin(u*20+v*7)
   for c in range(3):a[:,:,c][reg]=(variation*color[c])[reg]
  a[:,:,:3]=np.where(a[:,:,:3]<=.04045,a[:,:,:3]/12.92,((a[:,:,:3]+.055)/1.055)**2.4)
 elif kind=='orm':
  image.colorspace_settings.name='Non-Color';a[:,:,1]=np.array([.62,.34,.50,.35])[index]+noise*.04;a[:,:,2]=np.array([.12,.62,0,.25])[index]
 else:image.colorspace_settings.name='Non-Color';a[:,:,0]=.5+noise*.025;a[:,:,1]=.5+noise*.025
 image.pixels.foreach_set(a.ravel());image.filepath_raw=str(PREVIEW/(kind+'.png'));image.file_format='PNG';image.save();image.pack();globals()[kind]=image
for i,name in enumerate(['Obsidian hide','Basalt scutes','Keratin','Amber warning']):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 for im,label in [(base,'base'),(orm,'orm'),(normal,'normal')]:
  t=n.new('ShaderNodeTexImage');t.image=im
  if label=='base':l.new(t.outputs['Color'],p.inputs['Base Color'])
  elif label=='orm':
   sep=n.new('ShaderNodeSeparateColor');l.new(t.outputs['Color'],sep.inputs[0]);l.new(sep.outputs['Green'],p.inputs['Roughness']);l.new(sep.outputs['Blue'],p.inputs['Metallic'])
  else:
   b=n.new('ShaderNodeNormalMap');b.inputs['Strength'].default_value=.28;l.new(t.outputs['Color'],b.inputs['Color']);l.new(b.outputs['Normal'],p.inputs['Normal'])
 if i==3:p.inputs['Emission Color'].default_value=(.8,.19,.018,1);p.inputs['Emission Strength'].default_value=.35
 materials.append(m)
parts=[]
def mesh(name,vertices,faces,material,weights,uv=None):
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(materials[material]);layer=me.uv_layers.new(name='Anatomy UV')
 for loop in me.loops:
  c=me.vertices[loop.vertex_index].co;u,v=uv[loop.vertex_index] if uv else ((c.x+.5),(.5+c.y*.4));layer.data[loop.index].uv=((material%2+max(.005,min(.995,u)))/2,(material//2+max(.005,min(.995,v)))/2)
 for i,c in enumerate(vertices):
  w=weights(c,i) if callable(weights) else {weights:1};total=sum(w.values())
  for bn,value in w.items():
   if bn not in ob.vertex_groups:ob.vertex_groups.new(name=bn)
   ob.vertex_groups[bn].add([i],value/total,'REPLACE')
 for f in me.polygons:f.use_smooth=True
 parts.append(ob);return ob
def blend(a,b,w):w=max(0,min(1,w));return{a:1-w,b:w}
def loft_y(name,rows,mat,weights,segments=40):
 vs=[];uv=[]
 for k,(y,z,rx,rz) in enumerate(rows):
  for j in range(segments):
   a=j/segments*math.tau;ridge=1+.012*math.sin(a*7+y*15);vs.append((math.cos(a)*rx*ridge,y,z+math.sin(a)*rz*ridge));uv.append((j/segments,k/(len(rows)-1)))
 fs=[(k*segments+j,k*segments+(j+1)%segments,(k+1)*segments+(j+1)%segments,(k+1)*segments+j) for k in range(len(rows)-1) for j in range(segments)];fs+=[tuple(reversed(range(segments))),tuple((len(rows)-1)*segments+j for j in range(segments))];return mesh(name,vs,fs,mat,weights,uv)
def smooth_rows(profile,steps=4):
 out=[]
 for i in range(len(profile)-1):
  for k in range(steps):
   f=k/steps;f=f*f*(3-2*f);out.append(tuple(profile[i][j]*(1-f)+profile[i+1][j]*f for j in range(4)))
 return out+[profile[-1]]
loft_y('Sculpted thorax and haunches',smooth_rows([(-.49,.76,.18,.19),(-.35,.79,.32,.30),(-.15,.72,.34,.32),(.06,.66,.235,.24),(.25,.66,.23,.24),(.40,.68,.26,.27),(.52,.65,.13,.15)]),0,lambda c,i:blend('hips','chest',(.30-c[1])/.65),48)
loft_y('Muscular neck',smooth_rows([(-.34,.78,.20,.20),(-.47,.76,.19,.18),(-.62,.69,.16,.14),(-.73,.65,.14,.12)]),0,'neck',40)
loft_y('Deep blunt predator cranium',smooth_rows([(-.54,.77,.16,.17),(-.64,.79,.23,.22),(-.75,.76,.23,.20),(-.87,.70,.17,.17),(-.91,.69,.145,.145)]),1,'head',48)
loft_y('Muscular lower jaw',smooth_rows([(-.62,.59,.145,.065),(-.76,.535,.18,.075),(-.89,.55,.125,.06)]),0,'jaw',32)
# Continuous limb skins follow the anatomical upper/lower path, including knee/elbow blends.
for side,sign in [('L',1),('R',-1)]:
 for family,centres in [('fore',[(.25,-.34,.80,.105),(.32,-.19,.43,.075),(.25,-.44,.11,.047)]),('hind',[(.23,.34,.70,.14),(.32,.12,.41,.085),(.23,.40,.12,.048)])]:
  vs=[];uv=[];rows=25;segs=28
  for k in range(rows):
   f=k/(rows-1);segment=min(1,int(f*2));u=f*2-segment
   C=[Vector((c[0],c[1],c[2])) for c in centres];C[0].x*=.74;C[0].z+=.055
   P1=C[segment];P2=C[segment+1];P0=C[segment-1] if segment>0 else C[0]-(C[1]-C[0]);P3=C[segment+2] if segment+2<len(C) else C[-1]+(C[-1]-C[-2])
   center=.5*((2*P1)+(-P0+P2)*u+(2*P0-5*P1+4*P2-P3)*u*u+(-P0+3*P1-3*P2+P3)*u*u*u)
   tangent=.5*((-P0+P2)+2*(2*P0-5*P1+4*P2-P3)*u+3*(-P0+3*P1-3*P2+P3)*u*u);tangent.x*=sign;tangent.normalize();center.x*=sign
   basis=Vector((1,0,0));basis=(basis-tangent*basis.dot(tangent)).normalized();other=tangent.cross(basis).normalized();r=float(np.interp(f,[0,.17,.5,.8,1],[centres[0][3]*.75,centres[0][3]*1.05,centres[1][3],centres[2][3]*1.18,centres[2][3]]))
   for j in range(segs):
    a=j/segs*math.tau;point=center+basis*(math.cos(a)*r)+other*(math.sin(a)*r*.86);vs.append(tuple(point));uv.append((j/segs,f))
  fs=[(k*segs+j,k*segs+(j+1)%segs,(k+1)*segs+(j+1)%segs,(k+1)*segs+j) for k in range(rows-1) for j in range(segs)];fs.extend([tuple(reversed(range(segs))),tuple((rows-1)*segs+j for j in range(segs))])
  mesh(family+' continuous leg '+side,vs,fs,0,lambda c,i,fa=family,si=side:blend(fa+'_upper.'+si,fa+'_lower.'+si,(i//segs/(rows-1)-.32)/.36),uv)
  cy=-.47 if family=='fore' else .36;cz=.075
  vs=[];uv=[]
  for k in range(11):
   f=k/10;y=cy+.10-f*.22;width=.042+.045*math.sin(f*math.pi)
   for j in range(24):
    a=j/24*math.tau;vs.append((sign*(.25 if family=='fore' else .23)+math.cos(a)*width,y,cz+math.sin(a)*(.035+.012*math.sin(f*math.pi))));uv.append((j/24,f))
  fs=[(k*24+j,k*24+(j+1)%24,(k+1)*24+(j+1)%24,(k+1)*24+j) for k in range(10) for j in range(24)];mesh(family+' planted paw '+side,vs,fs,0,family+'_foot.'+side,uv)
  for toe in [-1,0,1]:
   x=sign*(.25 if family=='fore' else .23)+toe*.035;y=cy-.105
   mesh('Curved claw',[(x-.011,y,.065),(x+.011,y,.065),(x+.007,y-.07,.035),(x,y-.09,.03),(x-.007,y-.07,.035),(x,y,.09)],[(0,1,2),(0,2,3),(0,3,4),(0,4,5),(1,5,2),(2,5,4),(2,4,3)],2,family+'_foot.'+side)
# Integrated obsidian plates lie on the spine, rather than floating above the body.
for k in range(6):
 y=-.32+k*.14;z=1.055 if k<3 else .93;width=.22 if k<3 else .17
 mesh('Dorsal fracture plate',[(0,y-.13,z+.03),(-width,y,z-.065),(0,y+.11,z-.01),(width,y,z-.065),(0,y+.012,z+.12)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(0,3,2,1)],1,'chest' if k<3 else 'hips')
# Two directional ears, facial cuts, fangs and a connected balancing tail.
for sign in [-1,1]:
 mesh('Swept ear',[(sign*.13,-.61,.84),(sign*.22,-.50,1.055),(sign*.22,-.66,.91),(sign*.16,-.72,.81)],[(0,1,2),(0,2,3),(0,3,1),(1,3,2)],1,'head')
 mesh('Inset amber eye',[(sign*.167,-.776,.745),(sign*.157,-.852,.723),(sign*.173,-.816,.708)],[(0,1,2),(2,1,0)],3,'head')
 for y in [-.77,-.86]:
  x=sign*(.125 if y<-.8 else .17);mesh('Fang',[(x-.021,y,.64),(x+.021,y,.64),(x,y-.012,.48),(x,y+.027,.635)],[(0,1,2),(0,2,3),(1,3,2),(0,3,1)],2,'head')
# Sculpted cheek/brow and scapular masses interrupt the former flat bill profile.
for sign in [-1,1]:
 mesh('Heavy swept brow',[(sign*.12,-.88,.83),(sign*.245,-.74,.92),(sign*.25,-.63,.90),(sign*.21,-.70,.80),(sign*.14,-.86,.77)],[(0,1,2),(0,2,3),(0,3,4),(4,3,2,1,0)],1,'head')
 scapula=loft_y('Connected scapula '+str(sign),smooth_rows([(-.45,.82,.10,.13),(-.32,.86,.16,.19),(-.16,.81,.13,.13)]),0,'chest',24)
 for vertex in scapula.data.vertices:vertex.co.x+=sign*.22
 # The cheek blades are rooted at the skull, not floating spikes.
 mesh('Cheek blade',[(sign*.16,-.87,.66),(sign*.24,-.76,.72),(sign*.24,-.58,.64),(sign*.14,-.65,.56)],[(0,1,2),(0,2,3),(0,3,1),(1,3,2)],1,'head')
# Tail: continuous changing cross section, smooth bone blend along its length.
rows=smooth_rows([(.43,.69,.09,.075),(.73,.63,.075,.06),(.98,.72,.045,.04),(1.21,.84,.018,.025)],8)
loft_y('Long articulated tail',rows,0,lambda c,i:blend('tail_1','tail_2',(c[1]-.63)/.25) if c[1]<.97 else blend('tail_2','tail_3',(c[1]-.97)/.20),28)
# Small sternum fissure belongs to warning hierarchy; runtime raises its intensity only in anticipation.
mesh('Sternum warning seam',[(-.018,-.43,.62),(.018,-.43,.62),(.009,-.47,.47),(-.009,-.47,.47)],[(0,1,2,3),(3,2,1,0)],3,'chest')
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object;body.name='FaucheCendre_Skinned';body.parent=rig;mod=body.modifiers.new('Anatomical deformation','ARMATURE');mod.object=rig
# Original pose clips provide inspectable intent; runtime uses distance-driven foot planting.
P=rig.pose.bones
for b in P:b.rotation_mode='XYZ'
clips={'idle':2.4,'walk':1.1,'trot':.7,'anticipate':.9,'strike':.16,'recover':1.1}
for name,duration in clips.items():
 action=bpy.data.actions.new(name);rig.animation_data_create();rig.animation_data.action=action
 for frame in range(round(duration*30)+1):
  f=frame/round(duration*30)
  for b in P:b.rotation_euler=(0,0,0);b.location=(0,0,0)
  P['spine'].rotation_euler.x=.012*math.sin(f*math.tau);P['tail_1'].rotation_euler.z=.06*math.sin(f*math.tau)
  if name in ['walk','trot']:
   for family,side,offset in [('fore','L',0),('fore','R',.5),('hind','L',.5),('hind','R',0)]:
    cycle=math.sin((f+offset)*math.tau);P[family+'_upper.'+side].rotation_euler.x=cycle*.32;P[family+'_lower.'+side].rotation_euler.x=max(0,-cycle)*.5
  elif name=='anticipate':P['chest'].rotation_euler.x=-.16*f;P['neck'].rotation_euler.x=.18*f;P['jaw'].rotation_euler.x=.23*f
  elif name=='strike':P['chest'].rotation_euler.x=.16*math.sin(f*math.pi);P['jaw'].rotation_euler.x=.3*(1-f)
  elif name=='recover':P['neck'].rotation_euler.x=.14*(1-f);P['tail_1'].rotation_euler.z=.12*math.sin(f*math.pi)
  for b in P:b.keyframe_insert(data_path='rotation_euler',frame=frame+1,group=b.name)
 action.use_fake_user=True
rig.animation_data.action=None
for b in P:b.rotation_euler=(0,0,0);b.location=(0,0,0)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);body.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'obsidian-warden.glb'),export_format='GLB',use_selection=True,export_animation_mode='ACTIONS',export_nla_strips=False,export_force_sampling=True,export_skins=True,export_def_bones=False,export_materials='EXPORT',export_cameras=False,export_lights=False)
proof={'name':'Fauche-Cendre','role':'warden','generator':'scripts/author_creature_reference.py','original_art':True,'materials':4,'rest_joints':len(specs),'vertices':len(body.data.vertices),'polygons':len(body.data.polygons),'clips':clips,'sha256':hashlib.sha256((OUT/'obsidian-warden.glb').read_bytes()).hexdigest(),'limits':'Stylised original quadruped; runtime foot planting is procedural, no soft tissue simulation, no claim of AAA anatomy.'};(OUT/'PROVENANCE.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False)+'\n')
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=1000;scene.render.resolution_y=700;scene.render.resolution_percentage=100;scene.world.color=(.08,.08,.08)
for name,pos,power,size,color in [('Key',(-3,-4,4),450,3,(1,.89,.76)),('Rim',(2,2,3),550,2,(1,.49,.20)),('Fill',(3,-2,2),140,3,(.6,.72,1))]:
 light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;light.color=color;o=bpy.data.objects.new(name,light);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
camera=bpy.data.objects.new('Review',bpy.data.cameras.new('Review'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.lens=60;camera.location=(2.2,-3.1,1.7);camera.rotation_euler=(Vector((0,.05,.5))-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,.005));floor=bpy.data.materials.new('Review floor');floor.diffuse_color=(.035,.035,.04,1);bpy.context.object.data.materials.append(floor)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'obsidian-warden.blend'));scene.render.filepath=str(PREVIEW/'warden-threequarter.png');
if '--no-render' not in sys.argv:bpy.ops.render.render(write_still=True)
print('CREATURE_PRODUCTION',json.dumps(proof))
