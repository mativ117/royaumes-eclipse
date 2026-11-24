"""Retarget the original roster art without changing the approved Lame.

Blender 4.3: blender -b -t 4 --python scripts/retarget_roster_animations.py -- rempart
No argument exports all ten updated heroes. Sources are the retained CC0 Standard
Quaternius libraries. KayKit sources remain available for later directional work;
this pass does not mislabel procedural directional fallbacks as captured clips.
"""
from pathlib import Path
import bpy, math, json, hashlib, shutil, sys, ast
from mathutils import Vector, Matrix, Quaternion
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/tmp/roster-retarget');OUT.mkdir(exist_ok=True)
SOURCES=ROOT/'assets/animations/quaternius'
ROLES=['rempart','voltigeur','tisseuse','cendres','voleur','bergere','colosse','accordeur','neant','eclipse']
EXPORT_CLIPS={'idle','guard','walk','run','walk_back','strafe_left','strafe_right','attack1','attack2','attack3','shot','power','dash','dodge_left','dodge_right','start','stop','turn_left','turn_right','leap','shield','interact','carry','hit'}
PROFILE={'rempart':'rifle','cendres':'rifle','tisseuse':'caster','bergere':'caster','accordeur':'caster','voleur':'dagger','colosse':'heavy','neant':'shadow','eclipse':'ultimate','voltigeur':'blade'}
# Share only pure transfer/sampling functions, never run the single-Lame module.
_original=(ROOT/'scripts/retarget_lame_animations.py').read_text()
_tree=ast.parse(_original)
for _node in _tree.body:
 if isinstance(_node,ast.FunctionDef) and _node.name in ['import_source','sample_pose','sample_segment','blend_pose','contact_windows']:
  exec(compile(ast.Module(body=[_node],type_ignores=[]),'<retarget sampling helpers>','exec'),globals())

def blend_guard(samples,guard,count=8):
 samples=list(samples);count=min(count,len(samples)-2)
 for i in range(len(samples)-count,len(samples)):
  u=(i-(len(samples)-count))/max(1,count-1);samples[i]=blend_pose(samples[i],guard,u*u*(3-2*u))
 return samples

def duration(action):return float(action.frame_range[1]-action.frame_range[0])/30

def restore_weapon_binding(role,weapon):
 # The weapon mesh also contains left-hand equipment. Restore the original
 # art weights even when rerunning on a previously exported source blend.
 # glTF material splits can change vertex ordering, so match bind positions.
 original=json.loads((ROOT/'assets/source/roster/WEAPON-BINDINGS.json').read_text())['characters'][role]['vertices']
 tree=KDTree(len(original));weights=[]
 for index,vertex in enumerate(original):
  tree.insert(Vector(vertex['position']),index)
  weights.append([('weaponGrip' if name=='hand.R' else name,weight) for name,weight in vertex['weights']])
 tree.balance();weapon.vertex_groups.clear();groups={}
 for vertex in weapon.data.vertices:
  _,index,distance=tree.find(weapon.matrix_world@vertex.co)
  if distance>1e-4:raise RuntimeError('Weapon bind geometry mismatch '+role+' '+str(distance))
  for name,weight in weights[index]:
   if name not in groups:groups[name]=weapon.vertex_groups.new(name=name)
   groups[name].add([vertex.index],weight,'REPLACE')

def export_role(role):
 global scene,rig,P,rest,MAPPING,ratio,rest_source,source_head,reference,guard_samples
 profile=PROFILE[role];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/source/roster'/f'{role}.blend'))
 scene=bpy.context.scene;scene.render.fps=30;scene.render.fps_base=1
 rig=bpy.data.objects[role+'_Rig'];rig.animation_data_create();rig.animation_data.action=None
 for track in rig.animation_data.nla_tracks:track.mute=True
 for p in rig.pose.bones:p.rotation_mode='XYZ';p.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.objects.active=rig;bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 E=rig.data.edit_bones
 if 'weaponGrip' not in E:
  grip=E.new('weaponGrip');grip.head=(-.48,-.04,.99);grip.tail=(-.48,-.14,.99);grip.parent=E['hand.R']
  if 'blade_base' not in E:
   base=E.new('blade_base');base.head=(-.48,-.04,.94);base.tail=(-.48,-.04,.89);base.parent=grip
 grip=E['weaponGrip']
 for socket in ['blade_tip','muzzle','foregrip','bolt']:
  if socket in E:E[socket].parent=grip
 if role=='colosse':E['blade_tip'].head=(-.48,-.04,.28);E['blade_tip'].tail=(-.48,-.04,.23)
 if role=='neant':E['blade_tip'].head=(-.48,-.04,.19);E['blade_tip'].tail=(-.48,-.04,.14)
 if role=='voleur':
  for name,z in [('blade_base_L',.88),('blade_tip_L',.5483)]:
   socket=E.get(name) or E.new(name);socket.head=(.48,-.04,z);socket.tail=(.48,-.04,z-.05);socket.parent=E['hand.L']
 bpy.ops.object.mode_set(mode='OBJECT');P=rig.pose.bones
 for p in P:p.rotation_mode='XYZ';p.matrix_basis=Matrix.Identity(4)
 weapon=bpy.data.objects[role+'_Weapon'];restore_weapon_binding(role,weapon)
 base_objects=set(bpy.data.objects);base_actions={a.name for a in bpy.data.actions}
 meshes=[o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
 rest={b.name:b.matrix_local.copy() for b in rig.data.bones};body=bpy.data.objects[role+'_Skinned']
 body_coords=[body.matrix_world@v.co for v in body.data.vertices];sole=min(v.z for v in body_coords);body_height=max(v.z for v in body_coords)-sole
 MAPPING={'pelvis':'pelvis','spine':'spine_01','chest':'spine_03','neck':'neck_01','head':'Head'}
 for side,source_side in [('L','l'),('R','r')]:
  for dst,src in [('upper_arm','upperarm'),('forearm','lowerarm'),('hand','hand'),('thigh','thigh'),('shin','calf'),('foot','foot')]:MAPPING[dst+'.'+side]=src+'_'+source_side
 order=sorted(MAPPING,key=lambda name:len(list(rig.data.bones[name].parent_recursive)))
 source1,actions1=import_source(SOURCES/'UAL1_Standard_RM.glb','UAL1');source2,actions2=import_source(SOURCES/'UAL2_Standard_RM.glb','UAL2')
 for obj in bpy.data.objects:
  if obj.type=='MESH':obj.hide_set(True)
 ratio=(rig.data.bones['thigh.L'].length+rig.data.bones['shin.L'].length)/(source1.data.bones['thigh_l'].length+source1.data.bones['calf_l'].length)
 rest_source={source.name:{name:(source.matrix_world.to_quaternion()@source.data.bones[name].matrix_local.to_quaternion()) for name in MAPPING.values()} for source in [source1,source2]}
 source_head={source.name:source.matrix_world@source.data.bones['pelvis'].head_local for source in [source1,source2]}
 reference={}
 for source in [source1,source2]:
  ref={}
  for dst,src in MAPPING.items():
   q=(rig.matrix_world@rest[dst]).to_quaternion()
   if dst.startswith(('upper_arm.','forearm.','hand.')):
    src_dir=(source.matrix_world.to_3x3()@source.data.bones[src].vector).normalized();dst_dir=(rig.matrix_world.to_3x3()@rig.data.bones[dst].vector).normalized();q=dst_dir.rotation_difference(src_dir)@q
   ref[dst]=q
  reference[source.name]=ref
 guard_name='Pistol_Idle_Loop' if profile=='rifle' else 'Idle_Torch_Loop' if profile=='caster' else 'Sword_Idle'
 guard_samples=sample_segment(source1,actions1[guard_name],0,duration(actions1[guard_name]))
 plans={};source_names={}
 def plan(name,source,action,start=0,end=None,armed=False,recover=False):
  acts=actions1 if source==source1 else actions2;clip=acts[action];end=min(duration(clip),end) if end is not None else duration(clip);samples=sample_segment(source,clip,start,end)
  if recover:samples=blend_guard(samples,guard_samples[0],min(8,max(2,len(samples)//4)))
  plans[name]=(source,samples,armed);source_names[name]=action
 plan('idle',source1,guard_name);plan('guard',source1,guard_name)
 plan('walk',source1,'Walk_Loop',end=40/30,armed=True);plan('run',source1,'Jog_Fwd_Loop',end=28/30,armed=True)
 if profile=='dagger':attacks=[(source1,'Punch_Jab',.8667),(source1,'Punch_Cross',1.),(source2,'Melee_Hook',.4667)]
 elif profile=='heavy':attacks=[(source2,'TreeChopping_Loop',.9667),(source2,'Sword_Heavy_Combo',1.4667),(source2,'Sword_Regular_C',1.6)]
 elif profile=='caster':attacks=[(source1,'Spell_Simple_Shoot',.5)]*3
 else:attacks=[(source2,'Sword_Regular_A',.9333),(source2,'Sword_Regular_B',1.0333),(source2,'Sword_Regular_C',1.4)]
 for index,(source,action,end) in enumerate(attacks,1):plan('attack'+str(index),source,action,end=end,recover=True)
 plan('shot',source1,'Pistol_Shoot' if profile=='rifle' else 'Spell_Simple_Shoot',recover=True)
 plan('power',source2 if role in ['rempart','cendres','voleur'] else source1,'Shield_OneShot' if role in ['rempart','cendres'] else 'Sword_Block' if role=='voleur' else 'Jump_Start' if role=='voltigeur' else 'Spell_Simple_Enter',end=.8333,recover=True)
 # Keep the original directional/dodge/transition gestures available until their
 # own external contact pass; forward gait and kit actions above are real sources.
 for alias,origin in [('walk_back','walk'),('strafe_left','walk'),('strafe_right','walk')]:
  plans[alias]=plans[origin];source_names[alias]=source_names[origin]+' directional fallback'
 for alias,origin in [('start','guard'),('stop','guard'),('turn_left','guard'),('turn_right','guard'),('dodge_left','dash'),('dodge_right','dash')]:
  if origin in plans:
   src,samples,armed=plans[origin];plans[alias]=(src,samples[:9 if alias in ['start','stop'] else 12],armed);source_names[alias]=source_names[origin]+' transition fallback'
  elif bpy.data.actions.get(origin):
   old=bpy.data.actions.get(alias)
   if old:bpy.data.actions.remove(old)
   action=bpy.data.actions[origin].copy();action.name=alias;action.use_fake_user=True
 calibration={'version':1,'heroId':role,'profile':profile,'units':'model','source':'Quaternius Standard CC0','soleClearance':round(max(0,min(.12,sole)),6),'bodyHeight':round(body_height,6),'gaits':{},'dodge':{'distance':1.6 if profile not in ['heavy','rifle'] else 1.4,'duration':.4 if profile!='heavy' else .48},'attacks':{},'shot':{'duration':(len(plans['shot'][1])-1)/30,'hitAt':.166667 if profile=='rifle' else .2},'power':{'clip':'power','duration':(len(plans['power'][1])-1)/30,'fullBody':profile in ['heavy','ultimate']},'weaponRadius':.22 if profile=='heavy' else .07 if profile=='dagger' else .10}
 for name in ['walk','run']:
  source,samples,_=plans[name];delta=samples[-1]['root']-samples[0]['root'];dist=Vector((delta.x,delta.y,0)).length*ratio;dur=(len(samples)-1)/30
  if dist<.2:raise RuntimeError('Missing root-motion stride '+name)
  calibration['gaits'][name]={'cycleDistance':round(dist,6),'duration':dur,'contacts':{side.upper():contact_windows(samples,side,dist,dur) for side in ['l','r']},'sourceClip':source_names[name]}
 # Compatible fallback annotations are honest: the source forward walk is used.
 for name in ['walk_back','strafe_left','strafe_right']:
  if name in plans:calibration['gaits'][name]=dict(calibration['gaits']['walk'])
 def basis_for(name,matrix,computed):
  parent=rig.data.bones[name].parent
  return rest[name].inverted()@(rest[parent.name]@computed[parent.name].inverted() if parent else Matrix.Identity(4))@matrix
 def blade_at(computed):
  return computed['weaponGrip']@rest['weaponGrip'].inverted()@rest['blade_tip'].translation
 def bake(name,source,samples,armed):
  old=bpy.data.actions.get(name)
  if old:bpy.data.actions.remove(old)
  action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action;previous={};trace=[];feet=[]
  for index,sample in enumerate(samples):
   scene.frame_set(index);computed={'root':rest['root'].copy()};bases={'root':Matrix.Identity(4)}
   pelvis_delta=(sample['head']['pelvis']-sample['root']-source_head[source.name])*ratio
   for dst in order:
    src=MAPPING[dst];rotation=sample['r'][src]
    if armed and dst.endswith('.R') and dst.startswith(('upper_arm.','forearm.','hand.')):
     guard=guard_samples[round(index/(len(samples)-1)*(len(guard_samples)-1))];rotation=sample['r']['spine_03']@guard['r']['spine_03'].inverted()@guard['r'][src]
    world_rotation=rotation@rest_source[source.name][src].inverted()@reference[source.name][dst]
    parent=rig.data.bones[dst].parent
    head=rest[dst].translation+pelvis_delta if dst=='pelvis' else (computed[parent.name]@rest[parent.name].inverted()@rest[dst]).translation
    matrix=Matrix.Translation(head)@(rig.matrix_world.to_quaternion().inverted()@world_rotation).to_matrix().to_4x4();computed[dst]=matrix;bases[dst]=basis_for(dst,matrix,computed)
   chest_delta=computed['chest'].to_quaternion()@rest['chest'].to_quaternion().inverted();forward=chest_delta@Vector((0,-1,0));yaw=math.atan2(forward.x,-forward.y)
   for cape in ['cape_mid','cape_tip']:
    parent=rig.data.bones[cape].parent.name;head=(computed[parent]@rest[parent].inverted()@rest[cape]).translation;rotation=Quaternion((0,0,1),yaw)@rest[cape].to_quaternion();compress=min(1,max(.62,(computed['cape_mid'].translation.z-.05)/(rest['cape_mid'].translation.z-.17))) if cape=='cape_tip' else 1
    matrix=Matrix.Translation(head)@rotation.to_matrix().to_4x4()@Matrix.Diagonal((1,compress,1,1));computed[cape]=matrix;bases[cape]=basis_for(cape,matrix,computed)
   hand_rotation=sample['r']['hand_r']
   if armed:
    guard=guard_samples[round(index/(len(samples)-1)*(len(guard_samples)-1))];hand_rotation=sample['r']['spine_03']@guard['r']['spine_03'].inverted()@guard['r']['hand_r']
   pivot=(computed['hand.R']@rest['hand.R'].inverted()@rest['weaponGrip']).translation
   if profile=='caster':rotation=Quaternion((0,0,1),yaw)@rest['weaponGrip'].to_quaternion()
   else:
    aim_rest=rest['muzzle'].translation-rest['weaponGrip'].translation if profile=='rifle' else rest['blade_tip'].translation-rest['weaponGrip'].translation
    local=rest['weaponGrip'].to_quaternion().inverted()@aim_rest.normalized();offset=local.rotation_difference(Vector((0,1,0)) if profile=='rifle' else Vector((0,0,1)));rotation=hand_rotation@offset
   matrix=Matrix.Translation(pivot)@rotation.to_matrix().to_4x4();computed['weaponGrip']=matrix;bases['weaponGrip']=basis_for('weaponGrip',matrix,computed)
   for bone in P:
    bone.matrix_basis=bases.get(bone.name,Matrix.Identity(4))
    if bone.name in previous:bone.rotation_euler.make_compatible(previous[bone.name])
    previous[bone.name]=bone.rotation_euler.copy()
    bone.keyframe_insert(data_path='rotation_euler',frame=index,group=bone.name);bone.keyframe_insert(data_path='location',frame=index,group=bone.name);bone.keyframe_insert(data_path='scale',frame=index,group=bone.name)
   trace.append(blade_at(computed));feet.append([computed['foot.L'].translation.z,computed['foot.R'].translation.z])
  for fc in action.fcurves:
   for key in fc.keyframe_points:key.interpolation='LINEAR'
  dur=(len(samples)-1)/30
  if name.startswith('attack'):
   speed=[(trace[i]-trace[i-1]).length*30 for i in range(1,len(trace))];end=max(3,len(speed)-max(2,min(8,len(speed)//4)));begin=max(1,int(end*.12));peak=max(range(begin,end),key=lambda i:speed[i]);threshold=speed[peak]*.36;first=peak;last=peak
   while first>0 and speed[first-1]>threshold:first-=1
   while last+1<end and speed[last+1]>threshold:last+=1
   hit=max(1,first+1)/30;active=min(dur,(last+2)/30);delta=samples[min(len(samples)-1,last+2)]['root']-samples[0]['root'];travel=min(1.2,Vector((delta.x,delta.y,0)).length*ratio)
   calibration['attacks'][name]={'duration':round(dur,6),'hitAt':round(hit,6),'activeEnd':round(max(hit+.033333,active),6),'travel':round(max(.1,travel),6),'sourceClip':source_names[name]}
   calibration['combatReach']=round(max(calibration.get('combatReach',.2),min(5,max(Vector((v.x,v.y,0)).length for v in trace)+calibration['weaponRadius'])),6)
  print('BAKED',role,name,round(dur,3),'footMin',round(min(min(a) for a in feet),3),flush=True)
 for name,(source,samples,armed) in plans.items():bake(name,source,samples,armed)
 rig.animation_data.action=None
 for p in P:p.matrix_basis=Matrix.Identity(4)
 rig['motionCalibration']=json.dumps(calibration,separators=(',',':'))
 for obj in list(bpy.data.objects):
  if obj not in base_objects:bpy.data.objects.remove(obj,do_unlink=True)
 for action in list(bpy.data.actions):
  if action.name not in EXPORT_CLIPS:bpy.data.actions.remove(action)
 for mesh in meshes:mesh.hide_set(False)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
 for mesh in meshes:mesh.select_set(True)
 bpy.context.view_layer.objects.active=rig;bpy.context.view_layer.update();target=OUT/(role+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_nla_strips=False,export_force_sampling=True,export_skins=True,export_def_bones=False,export_cameras=False,export_lights=False,export_extras=True)
 raw=target.read_bytes();shutil.copyfile(target,ROOT/'assets/characters'/f'{role}.glb')
 scene.frame_set(0);rig.animation_data.action=bpy.data.actions['guard'];bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/source/roster'/f'{role}.blend'),compress=True)
 report={'hero':role,'profile':profile,'generator':'scripts/retarget_roster_animations.py','art_generator':'scripts/upgrade_roster_art.py','source':f'assets/source/roster/{role}.blend','sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'motion_calibration':calibration,'retargeted_clips':list(plans),'sampled_clips':['idle','guard','walk','run','attack1','attack2','attack3','shot','power'],'derived_clips':['walk_back','strafe_left','strafe_right','start','stop','turn_left','turn_right'],'inherited_clips':['dash','leap','shield','interact','carry','hit','dodge_left','dodge_right'],'fallback_scope':'Backward/strafing clips use the source forward walk; transitions use short source guards. Dash, leap, shield, interact, carry and hit retain the original authored gestures; directional dodges copy dash. No purpose-built directional capture or dodge claim.','animation_sources':'assets/animations/quaternius/PROVENANCE.json'}
 (OUT/(role+'.json')).write_text(json.dumps(report,indent=2)+'\n');print('EXPORTED',role,len(raw),report['sha256'],flush=True)
 return report

roles=[a for a in (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []) if a in ROLES] or ROLES
reports={}
for role in roles:reports[role]=export_role(role)
metadata_path=ROOT/'assets/characters/ROSTER-PRODUCTION.json';metadata=json.loads(metadata_path.read_text()) if metadata_path.exists() else {'version':'1.5-rc1','characters':{}}
metadata['characters'].update(reports);metadata_path.write_text(json.dumps(metadata,indent=2)+'\n')
provenance_path=ROOT/'assets/characters/PROVENANCE.json';provenance=json.loads(provenance_path.read_text());provenance['third_party_animation']=True
for role,report in reports.items():provenance['sha256'][role+'.glb']=report['sha256'];provenance.setdefault('per_character',{})[role]=report
provenance_path.write_text(json.dumps(provenance,indent=2)+'\n')
