"""Retarget CC0 Quaternius Standard clips onto the existing Lame sculpture.

Run after author_lame_reference.py with Blender 4.3. Geometry, UVs, materials and
rest skeleton are preserved; source animation rigs never enter the exported GLB.
No source pose is claimed to be motion capture or a finished artistic result.
"""
from pathlib import Path
import bpy, math, json, hashlib, shutil, sys, struct
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/tmp/lame-retarget');OUT.mkdir(exist_ok=True)
SOURCES=ROOT/'assets/animations/quaternius'
BASE=ROOT/'assets/source/lame-reference.blend'
def geometry_uv_digest(raw):
 size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=raw[20+size+8:]
 def values(index):
  a=doc['accessors'][index];view=doc['bufferViews'][a['bufferView']];width={'VEC2':2,'VEC3':3}[a['type']];offset=view.get('byteOffset',0)+a.get('byteOffset',0)
  return [struct.unpack_from('<'+'f'*width,binary,offset+i*view.get('byteStride',width*4)) for i in range(a['count'])]
 result=[]
 for mesh in doc['meshes']:
  points=set()
  for primitive in mesh['primitives']:
   attrs=primitive['attributes'];points.update(tuple(round(v,5) for v in position+uv) for position,uv in zip(values(attrs['POSITION']),values(attrs['TEXCOORD_0'])))
  result.append((mesh['name'],sorted(points)))
 return hashlib.sha256(json.dumps(sorted(result),separators=(',',':')).encode()).hexdigest()
base_geometry_uv_sha256=geometry_uv_digest((ROOT/'assets/characters/lame.glb').read_bytes())
bpy.ops.wm.open_mainfile(filepath=str(BASE))
scene=bpy.context.scene;scene.render.fps=30;scene.render.fps_base=1
rig=bpy.data.objects['lame_Rig']; rig.animation_data_create();rig.animation_data.action=None
for track in rig.animation_data.nla_tracks:track.mute=True
# Add an independent weapon socket while preserving all previous rest joints.
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
E=rig.data.edit_bones
if 'weaponGrip' not in E:
 grip=E.new('weaponGrip');grip.head=(-.48,-.04,.99);grip.tail=(-.48,-.14,.99);grip.parent=E['hand.R']
 E['blade_tip'].parent=grip
 if 'blade_base' not in E:
  base=E.new('blade_base');base.head=(-.48,-.045,.885);base.tail=(-.48,-.045,.84);base.parent=grip
bpy.ops.object.mode_set(mode='OBJECT')
P=rig.pose.bones
for p in P:p.rotation_mode='XYZ';p.matrix_basis=Matrix.Identity(4)
# The long front panels need mostly pelvis influence. They previously inherited
# nearly a full thigh rotation and rose over the face during lunges.
body=bpy.data.objects['lame_Skinned']
cloth_slots={i for i,m in enumerate(body.data.materials) if m and m.name=='Night brocade'}
cloth_vertices={v for poly in body.data.polygons if poly.material_index in cloth_slots for v in poly.vertices}
for index in cloth_vertices:
 vertex=body.data.vertices[index]
 if vertex.co.y>-.105 or vertex.co.z>1.12:continue
 weights={body.vertex_groups[g.group].name:g.weight for g in vertex.groups}
 thighs={n:w for n,w in weights.items() if n.startswith('thigh.')}
 if not thighs:continue
 nominal=max(0,min(1,(1.05-vertex.co.z)/.65))
 for n,w in thighs.items():body.vertex_groups[n].add([index],nominal*.15,'REPLACE')
 body.vertex_groups['pelvis'].add([index],1-nominal*.15,'REPLACE')
weapon=bpy.data.objects['lame_Weapon']
if not weapon.get('independentWeaponSocket'):
 weapon.vertex_groups.clear();group=weapon.vertex_groups.new(name='weaponGrip');group.add(list(range(len(weapon.data.vertices))),1,'REPLACE');weapon['independentWeaponSocket']=True
bpy.context.view_layer.update()
base_objects=set(bpy.data.objects);base_actions={a.name for a in bpy.data.actions}
meshes=[o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
mesh_signature={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in meshes}
rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
MAPPING={'pelvis':'pelvis','spine':'spine_01','chest':'spine_03','neck':'neck_01','head':'Head'}
for side,source_side in [('L','l'),('R','r')]:
 for dst,src in [('upper_arm','upperarm'),('forearm','lowerarm'),('hand','hand'),('thigh','thigh'),('shin','calf'),('foot','foot')]:MAPPING[dst+'.'+side]=src+'_'+source_side
order=sorted(MAPPING,key=lambda name:len(list(rig.data.bones[name].parent_recursive)))

# Import both rigs once, then cache world-space samples before baking target keys.
def import_source(path,tag):
 before=set(bpy.data.objects);acts=set(bpy.data.actions)
 bpy.ops.import_scene.gltf(filepath=str(path));objects=[o for o in bpy.data.objects if o not in before]
 source=next(o for o in objects if o.type=='ARMATURE')
 actions={a.name.split('_Armature')[0]:a for a in set(bpy.data.actions)-acts}
 for track in source.animation_data.nla_tracks:track.mute=True
 for o in objects:o.hide_render=True;o.name=tag+'_'+o.name
 return source,actions
source1,actions1=import_source(SOURCES/'UAL1_Standard_RM.glb','UAL1')
source2,actions2=import_source(SOURCES/'UAL2_Standard_RM.glb','UAL2')
ratio=(rig.data.bones['thigh.L'].length+rig.data.bones['shin.L'].length)/(source1.data.bones['thigh_l'].length+source1.data.bones['calf_l'].length)
print('LEG_LENGTH_SCALE',ratio,flush=True)

def sample_pose(source,action,seconds):
 source.animation_data.action=action
 scene.frame_set(int(seconds*30),subframe=seconds*30-int(seconds*30));bpy.context.view_layer.update()
 world=source.matrix_world
 root_head=world@source.pose.bones['root'].head
 return {'root':root_head.copy(),'r':{name:(world.to_quaternion()@source.pose.bones[name].matrix.to_quaternion()) for name in set(MAPPING.values())},'head':{name:(world@source.pose.bones[name].head) for name in ['pelvis','foot_l','foot_r','ball_l','ball_r']}}

def sample_segment(source,action,start,end):
 count=round((end-start)*30)
 return [sample_pose(source,action,start+i/30) for i in range(count+1)]

rest_source={source.name:{name:(source.matrix_world.to_quaternion()@source.data.bones[name].matrix_local.to_quaternion()) for name in MAPPING.values()} for source in [source1,source2]}
source_head={source.name:source.matrix_world@source.data.bones['pelvis'].head_local for source in [source1,source2]}
# Arms are calibrated in a T-pose. Applying a T-pose delta directly to the target
# A-pose would fold the arms down twice. Leg/foot rest rolls remain target-specific.
reference={}
for source in [source1,source2]:
 ref={}
 for dst,src in MAPPING.items():
  dst_q=(rig.matrix_world@rest[dst]).to_quaternion()
  if dst.startswith(('upper_arm.','forearm.','hand.')):
   src_dir=(source.matrix_world.to_3x3()@source.data.bones[src].vector).normalized()
   dst_dir=(rig.matrix_world.to_3x3()@rig.data.bones[dst].vector).normalized()
   dst_q=dst_dir.rotation_difference(src_dir)@dst_q
  ref[dst]=dst_q
 reference[source.name]=ref

# The armed right arm uses the authored sword idle during locomotion. This keeps
# the long blade clear of the floor while retaining the source's torso and left arm.
guard_samples=sample_segment(source1,actions1['Sword_Idle'],0,50/30)
plans={
 'idle':(source1,sample_segment(source1,actions1['Sword_Idle'],0,50/30),False),
 'guard':(source1,guard_samples,False),
 'walk':(source1,sample_segment(source1,actions1['Walk_Loop'],0,40/30),True),
 'run':(source1,sample_segment(source1,actions1['Jog_Fwd_Loop'],0,28/30),True),
 'attack1':(source2,sample_segment(source2,actions2['Sword_Regular_A'],0,13/30)+sample_segment(source2,actions2['Sword_Regular_A_Rec'],0,15/30)[1:],False),
 'attack2':(source2,sample_segment(source2,actions2['Sword_Regular_B'],0,16/30)+sample_segment(source2,actions2['Sword_Regular_B_Rec'],0,15/30)[1:],False),
 'attack3':(source2,sample_segment(source2,actions2['Sword_Regular_C'],0,1.4),False),
}
for obj in [o for o in bpy.data.objects if o not in base_objects and o.type=='MESH']:obj.hide_set(True)
# End truncated recovery tails in the same authored sword guard. The source is
# still sampled at 1x; a short pose blend avoids an abrupt cut to the idle clip.
def blend_pose(sample,target,weight):
 return {'root':sample['root'].lerp(target['root'],weight),'r':{name:q.slerp(target['r'][name],weight) for name,q in sample['r'].items()},'head':{name:p.lerp(target['head'][name],weight) for name,p in sample['head'].items()}}
for attack in ['attack1','attack2','attack3']:
 source,samples,armed=plans[attack];count=min(8,len(samples)-2)
 for i in range(len(samples)-count,len(samples)):
  u=(i-(len(samples)-count))/(count-1);weight=u*u*(3-2*u);samples[i]=blend_pose(samples[i],guard_samples[0],weight)
# Derive ground-contact intervals from source RM ankle speed/height. The endpoint
# is the repeated first pose, not an extra footstep.
def contact_windows(samples,side,cycle_distance,duration):
 points=[p['head']['foot_'+side] for p in samples];count=len(points)-1
 heights=[p.z for p in points[:-1]];floor=min(heights);native_speed=cycle_distance/max(.001,duration)/ratio
 mask=[]
 for i in range(count):
  before=points[max(0,i-1)];after=points[min(count,i+1)];speed=(after-before).length/max(1/30,(min(count,i+1)-max(0,i-1))/30)
  mask.append(points[i].z<floor+.045 and speed<max(.35,native_speed*.75))
 # If toe roll makes an ankle detector sparse, retain low-height ground contact.
 if sum(mask)<count*.16:mask=[h<floor+.035 for h in heights]
 windows=[];start=None
 for i,active in enumerate(mask+[False]):
  if active and start is None:start=i
  if not active and start is not None:
   if i-start>=2:windows.append([round(start/count,5),round(i/count,5)])
   start=None
 return windows

calibration={'version':1,'units':'model','source':'Quaternius Universal Animation Library Standard CC0','gaits':{},'dodge':{'distance':1.6,'duration':.40},'attacks':{}}
for name in ['walk','run']:
 source,samples,_=plans[name];delta=samples[-1]['root']-samples[0]['root'];distance=Vector((delta.x,delta.y,0)).length*ratio;duration=(len(samples)-1)/30
 if distance<.1:raise RuntimeError('Root-motion source has no measurable cycle distance: '+name)
 calibration['gaits'][name]={'cycleDistance':round(distance,6),'duration':round(duration,6),'contacts':{side.upper():contact_windows(samples,side,distance,duration) for side in ['l','r']},'sourceClip':'Walk_Loop' if name=='walk' else 'Jog_Fwd_Loop'}
 print('GAIT',name,json.dumps(calibration['gaits'][name]),flush=True)

# Source root translations are removed from X/Y. The controller will move the
# actor using these measured distances; the source vertical pelvis motion remains.
blade_rest=rig.data.bones['blade_tip'].head_local.copy()
def blade_position():return rig.matrix_world@P['blade_tip'].head

def bake(name,source,samples,armed):
 old=bpy.data.actions.get(name)
 if old:bpy.data.actions.remove(old)
 action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
 previous={};trace=[];feet=[];source_rest=rest_source[source.name]
 for index,sample in enumerate(samples):
  scene.frame_set(index)
  for p in P:p.matrix_basis=Matrix.Identity(4)
  bpy.context.view_layer.update()
  pelvis_delta=(sample['head']['pelvis']-sample['root']-source_head[source.name])*ratio
  # Retain lateral shift, remove the source's fixed front offset from rest.
  P['root'].location=(0,0,0)
  for dst in order:
   src=MAPPING[dst];bone=P[dst];rotation=sample['r'][src]
   if armed and dst.endswith('.R') and dst.startswith(('upper_arm.','forearm.','hand.')):
    guard=guard_samples[round(index/(len(samples)-1)*(len(guard_samples)-1))]
    rotation=sample['r']['spine_03']@guard['r']['spine_03'].inverted()@guard['r'][src]
   world_rotation=rotation@source_rest[src].inverted()@reference[source.name][dst]
   if dst=='pelvis':head=rest[dst].translation+pelvis_delta
   else:
    parent=bone.parent
    head=(parent.matrix@parent.bone.matrix_local.inverted()@rest[dst]).translation if parent else rest[dst].translation
   local_rotation=rig.matrix_world.to_quaternion().inverted()@world_rotation
   bone.matrix=Matrix.Translation(head)@local_rotation.to_matrix().to_4x4()
   if dst in previous:bone.rotation_euler.make_compatible(previous[dst])
   previous[dst]=bone.rotation_euler.copy()
   bpy.context.view_layer.update()
  # Keep the draped panels gravity-oriented rather than rigidly inheriting the
  # full chest pitch/roll of a lunge. This is a rig correction, not cloth simulation.
  chest_delta=P['chest'].matrix.to_quaternion()@rest['chest'].to_quaternion().inverted()
  forward=chest_delta@Vector((0,-1,0));yaw=math.atan2(forward.x,-forward.y)
  for cape_name in ['cape_mid','cape_tip']:
   bone=P[cape_name];head=(bone.parent.matrix@bone.parent.bone.matrix_local.inverted()@rest[cape_name]).translation
   rotation=Quaternion((0,0,1),yaw)@rest[cape_name].to_quaternion()
   compress=min(1,max(.58,(P['cape_mid'].head.z-.05)/(rest['cape_mid'].translation.z-.17)))
   bone.matrix=Matrix.Translation(head)@rotation.to_matrix().to_4x4()@Matrix.Diagonal((1,compress,1,1));bpy.context.view_layer.update()
  # Quaternius' palm normal is the virtual sword axis. The original mesh was
  # attached along its fingers, so a dedicated socket corrects the weapon alone.
  hand_rotation=sample['r']['hand_r']
  if armed:
   guard=guard_samples[round(index/(len(samples)-1)*(len(guard_samples)-1))]
   hand_rotation=sample['r']['spine_03']@guard['r']['spine_03'].inverted()@guard['r']['hand_r']
  grip=P['weaponGrip'];pivot=(P['hand.R'].matrix@rest['hand.R'].inverted()@rest['weaponGrip']).translation
  blade_local=rest['weaponGrip'].to_quaternion().inverted()@(blade_rest-rest['weaponGrip'].translation).normalized()
  offset=blade_local.rotation_difference(Vector((0,0,1)))
  grip.matrix=Matrix.Translation(pivot)@(hand_rotation@offset).to_matrix().to_4x4()
  bpy.context.view_layer.update()
  trace.append(blade_position().copy());feet.append([P['foot.L'].head.z,P['foot.R'].head.z])
  for p in P:
   p.keyframe_insert(data_path='rotation_euler',frame=index,group=p.name)
   p.keyframe_insert(data_path='location',frame=index,group=p.name)
   p.keyframe_insert(data_path='scale',frame=index,group=p.name)
  for fc in action.fcurves:
   for kp in fc.keyframe_points:kp.interpolation='LINEAR'
 duration=(len(samples)-1)/30
 if name.startswith('attack'):
  # Locate the energetic swing from the actual target blade path, excluding the
  # recovery tail. These times are a collision window, not a radius damage event.
  speed=[(trace[i]-trace[i-1]).length*30 for i in range(1,len(trace))]
  search_end=min(len(speed),13 if name=='attack1' else 16 if name=='attack2' else len(speed)-8)
  peak=max(range(max(2,int(search_end*.12)),search_end),key=lambda i:speed[i])
  threshold=speed[peak]*.36;first=peak
  while first>0 and speed[first-1]>threshold:first-=1
  last=peak
  while last+1<search_end and speed[last+1]>threshold:last+=1
  hit=max(1,first+1)/30;end=min(duration,(last+2)/30)
  delta=samples[min(len(samples)-1,last+2)]['root']-samples[0]['root'];travel=min(1.2,Vector((delta.x,delta.y,0)).length*ratio)
  calibration['attacks'][name]={'hitAt':round(hit,6),'activeEnd':round(end,6),'duration':round(duration,6),'travel':round(max(.15,travel),6),'sourceClip':{'attack1':'Sword_Regular_A + A_Rec','attack2':'Sword_Regular_B + B_Rec','attack3':'Sword_Regular_C'}[name]}
  print('ATTACK',name,json.dumps(calibration['attacks'][name]),'bladeMinZ',round(min(p.z for p in trace),3),flush=True)
 print('BAKED',name,'duration',duration,'feetMin',min(min(p) for p in feet),'bladeMin',min(p.z for p in trace),flush=True)
 return action
for name,(source,samples,armed) in plans.items():bake(name,source,samples,armed)
rig.animation_data.action=None
for p in P:p.matrix_basis=Matrix.Identity(4)
rig['motionCalibration']=json.dumps(calibration,separators=(',',':'))
# Remove every imported object/action, not just hide it in the production source.
for obj in list(bpy.data.objects):
 if obj not in base_objects:bpy.data.objects.remove(obj,do_unlink=True)
for action in list(bpy.data.actions):
 if action.name not in {name for name in base_actions if name not in plans} and action.name not in plans:bpy.data.actions.remove(action)
assert mesh_signature=={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in meshes}
assert len(bpy.data.actions)==23,[a.name for a in bpy.data.actions]
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for mesh in meshes:mesh.select_set(True)
bpy.context.view_layer.objects.active=rig;bpy.context.view_layer.update()
temporary=OUT/'lame.glb'
bpy.ops.export_scene.gltf(filepath=str(temporary),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_nla_strips=False,export_force_sampling=True,export_skins=True,export_def_bones=False,export_cameras=False,export_lights=False,export_extras=True)
raw=temporary.read_bytes();size=struct.unpack_from('<I',raw,12)[0];document=json.loads(raw[20:20+size]);assert len(document['animations'])==23
assert len(document['materials'])==8 and len(document['images'])==3
(OUT/'motion-calibration.json').write_text(json.dumps(calibration,indent=2)+'\n')
# Keep one source with editable actions and packed original materials.
bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
scene.frame_set(1);rig.animation_data.action=bpy.data.actions['guard']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'lame-reference.blend'))
shutil.copyfile(temporary,ROOT/'assets/characters/lame.glb');shutil.copyfile(OUT/'lame-reference.blend',BASE)
provenance_path=ROOT/'assets/characters/LAME-PRODUCTION.json';provenance=json.loads(provenance_path.read_text());provenance.update({'base_geometry_uv_sha256':base_geometry_uv_sha256,'art_scope':'Original geometry and materials; seven retargeted CC0 Quaternius animations, remaining actions authored in the base generator','original_geometry':True,'weapon_socket':'weaponGrip, blade_base and blade_tip; all previous rest joints retained','cloth_skinning':'front panels 85%+ pelvis; gravity-oriented and crouch-compressed cape joints, no cloth simulation','animation_generator':'scripts/retarget_lame_animations.py','status':'third production: CC0 animation retarget and measured motion calibration; artistic review ongoing','retargeted_clips':list(plans),'motion_calibration':calibration,'animation_sources':'assets/animations/quaternius/PROVENANCE.json','sha256':hashlib.sha256(raw).hexdigest()});provenance_path.write_text(json.dumps(provenance,indent=2)+'\n')
print('RETARGET_EXPORTED',len(raw),provenance['sha256'],flush=True)
# Optional low-sample, unretouched CPU pose review. Chromium/GPU are not used.
if '--preview' in sys.argv:
 scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=480;scene.render.resolution_y=600;scene.render.resolution_percentage=100
 cam=scene.camera;cam.location=(2.5,-4.7,2);cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=65
 for name,frame in [('guard',10),('walk',12),('run',7),('attack1',10),('attack2',13),('attack3',30)]:
  rig.animation_data.action=bpy.data.actions[name];scene.frame_set(frame);scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
