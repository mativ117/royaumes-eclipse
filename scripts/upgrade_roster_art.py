"""Original roster art pass, Blender 4.3. Keeps the approved Lame untouched.

Run: blender -b -t 4 --python scripts/upgrade_roster_art.py -- --roles rempart
Intermediate GLBs go to /tmp/roster-art; retarget_roster_animations owns final GLBs.
"""
import ast, argparse, bpy, hashlib, json, math, struct, sys
from pathlib import Path
from mathutils import Vector
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/tmp/roster-art');OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'assets/source/roster';SOURCE.mkdir(parents=True,exist_ok=True)
ROLES=['rempart','voltigeur','tisseuse','cendres','voleur','bergere','colosse','accordeur','neant','eclipse']
NAMES=['Obsidian lamella','Weathered bronze','Cracked porcelain','Flax sleeve','Night brocade','Amber silk','Bound hair','Oiled leather']
# Same surface construction as the approved reference, with each role's own dye/patina.
PALETTES={
 'rempart':[(.10,.135,.14),(.53,.355,.16),(.72,.73,.68),(.23,.25,.22),(.065,.077,.073),(.31,.13,.075),(.05,.045,.035),(.09,.065,.04)],
 'voltigeur':[(.14,.17,.18),(.61,.40,.17),(.77,.72,.60),(.44,.40,.30),(.12,.105,.08),(.45,.20,.085),(.07,.055,.035),(.13,.085,.055)],
 'tisseuse':[(.12,.105,.17),(.51,.35,.24),(.73,.68,.70),(.30,.27,.34),(.105,.07,.15),(.32,.14,.27),(.055,.035,.065),(.09,.055,.09)],
 'cendres':[(.12,.10,.08),(.69,.31,.10),(.67,.62,.49),(.22,.18,.13),(.075,.06,.045),(.52,.14,.035),(.055,.035,.02),(.12,.065,.035)],
 'voleur':[(.095,.10,.13),(.38,.32,.27),(.64,.62,.61),(.17,.15,.20),(.055,.045,.075),(.25,.12,.20),(.035,.025,.05),(.065,.04,.065)],
 'bergere':[(.22,.29,.25),(.65,.53,.30),(.85,.81,.68),(.65,.62,.49),(.18,.26,.20),(.33,.44,.32),(.08,.10,.065),(.14,.105,.055)],
 'colosse':[(.50,.50,.44),(.47,.30,.13),(.82,.78,.65),(.30,.27,.22),(.11,.13,.125),(.34,.20,.10),(.06,.055,.04),(.13,.09,.055)],
 'accordeur':[(.18,.15,.17),(.64,.43,.22),(.76,.70,.61),(.39,.32,.33),(.15,.09,.13),(.43,.23,.25),(.065,.04,.055),(.13,.065,.075)],
 'neant':[(.055,.065,.11),(.31,.34,.44),(.55,.59,.72),(.12,.13,.22),(.035,.035,.08),(.13,.12,.30),(.025,.025,.045),(.05,.035,.08)],
 'eclipse':[(.07,.065,.07),(.78,.51,.18),(.85,.77,.55),(.36,.31,.22),(.035,.032,.04),(.67,.35,.09),(.045,.035,.025),(.085,.055,.03)]}
ACCENTS={'rempart':(.18,.60,.72),'voltigeur':(.9,.52,.16),'tisseuse':(.48,.25,.8),'cendres':(1,.20,.035),'voleur':(.45,.25,.65),'bergere':(.45,.85,.67),'colosse':(.90,.72,.36),'accordeur':(.80,.37,.49),'neant':(.25,.34,.85),'eclipse':(1,.54,.12)}
PROFILES={'rempart':(1.08,1.03,.80),'voltigeur':(.92,.94,.40),'tisseuse':(.91,.94,1.0),'cendres':(1.10,1.08,.65),'voleur':(.88,.90,.36),'bergere':(.94,.97,1.0),'colosse':(1.23,1.17,.74),'accordeur':(.93,.96,.92),'neant':(.90,.94,1.0),'eclipse':(1.06,1.06,1.0)}

base=ROOT/'scripts/author_characters.py';base_ns={'__file__':str(base)}
exec(compile(base.read_text().split('\nROLES=')[0],str(base),'exec'),base_ns)
base_ns['OUT']=OUT/'rig-cache';base_ns['OUT'].mkdir(exist_ok=True)
helpers=ast.parse((ROOT/'scripts/author_lame_reference.py').read_text())
for node in helpers.body:
 if isinstance(node,ast.FunctionDef) and node.name in {'atlas','blend','torso_weight','loft','ribbon'}:
  exec(compile(ast.Module(body=[node],type_ignores=[]),str(ROOT/'scripts/author_lame_reference.py'),'exec'))

def mesh(name,verts,faces,mat,weights,uv=None,group=None,thickness=0):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
 obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(materials[mat])
 layer=data.uv_layers.new(name='Tailored UV');region=2 if mat==8 else mat
 for loop in data.loops:
  co=data.vertices[loop.vertex_index].co
  coord=uv[loop.vertex_index] if uv else ((co.x+.67)/1.34,co.z/2.2)
  if name.startswith('Mask'):coord=((co.x+.17)/.34,(co.z-1.83)/.31)
  u,v=[max(.012,min(.988,float(n))) for n in coord]
  layer.data[loop.index].uv=((region%4+u)/4,(region//4+v)/2)
 for i,co in enumerate(verts):
  w=weights(co) if callable(weights) else {weights:1};total=sum(w.values()) or 1
  for bone,value in w.items():
   if bone not in obj.vertex_groups:obj.vertex_groups.new(name=bone)
   if value>0:obj.vertex_groups[bone].add([i],value/total,'REPLACE')
 for face in data.polygons:face.use_smooth=True
 if thickness:
  mod=obj.modifiers.new('Tailored thickness','SOLIDIFY');mod.thickness=thickness;bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
 (weapon_parts if group=='weapon' else parts).append(obj);return obj

def tube(name,points,radius,mat,bone,group=None,sides=8):
 verts=[];uv=[]
 for i,point in enumerate(points):
  tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)]);tangent.normalize()
  axis=tangent.cross(Vector((0,1,0)))
  if axis.length<.001:axis=tangent.cross(Vector((1,0,0)))
  axis.normalize();other=tangent.cross(axis).normalized()
  for j in range(sides):
   angle=j/sides*math.tau;verts.append(tuple(Vector(point)+radius*(axis*math.cos(angle)+other*math.sin(angle))));uv.append((j/sides,i/max(1,len(points)-1)))
 faces=[(i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j) for i in range(len(points)-1)]
 return mesh(name,verts,faces,mat,bone,uv,group)

def ellipsoid(name,center,radii,mat,bone,group=None,segments=24,rows=14):
 verts=[];uv=[]
 for i in range(rows+1):
  t=math.pi*i/rows
  for j in range(segments):
   a=math.tau*j/segments;verts.append((center[0]+radii[0]*math.sin(t)*math.cos(a),center[1]+radii[1]*math.sin(t)*math.sin(a),center[2]+radii[2]*math.cos(t)));uv.append((j/segments,i/rows))
 faces=[(i*segments+j,i*segments+(j+1)%segments,(i+1)*segments+(j+1)%segments,(i+1)*segments+j) for i in range(rows)]
 return mesh(name,verts,faces,mat,bone,uv,group)

def ring(name,center,rx,rz,radius,mat,bone,start=0,end=math.tau,group=None):
 return tube(name,[(center[0]+rx*math.cos(a),center[1],center[2]+rz*math.sin(a)) for a in np.linspace(start,end,65)],radius,mat,bone,group)

def surfaces(role):
 global COLORS,PREVIEW,materials
 COLORS=PALETTES[role];PREVIEW=OUT/role;PREVIEW.mkdir(exist_ok=True);materials=[]
 images=[atlas(1024,'color'),atlas(512,'orm'),atlas(512,'normal')]
 for image,label in zip(images,['color','orm','normal']):image.name=role+'_'+label
 for index,name in enumerate(NAMES):
  material=bpy.data.materials.new(role+' · '+name);material.use_nodes=True;p=material.node_tree.nodes.get('Principled BSDF');nodes=material.node_tree.nodes;links=material.node_tree.links
  for image,label in zip(images,['color','orm','normal']):
   texture=nodes.new('ShaderNodeTexImage');texture.image=image
   if label=='color':links.new(texture.outputs['Color'],p.inputs['Base Color'])
   elif label=='orm':
    split=nodes.new('ShaderNodeSeparateColor');links.new(texture.outputs['Color'],split.inputs[0]);links.new(split.outputs['Green'],p.inputs['Roughness']);links.new(split.outputs['Blue'],p.inputs['Metallic'])
   else:
    bump=nodes.new('ShaderNodeNormalMap');bump.inputs['Strength'].default_value=.30;links.new(texture.outputs['Color'],bump.inputs['Color']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
  materials.append(material)
 glow=materials[2].copy();glow.name=role+' · Resonance enamel';p=glow.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*ACCENTS[role],1);p.inputs['Emission Strength'].default_value=.65 if role!='eclipse' else 1.2;materials.append(glow)

def anatomy(role):
 width,depth,coat=PROFILES[role]
 profiles=[(.99,.19,.12),(1.10,.23,.135),(1.23,.20,.12),(1.40,.22,.135),(1.56,.265,.15),(1.68,.25,.13),(1.75,.106,.087)]
 rings=[]
 for i in range(len(profiles)-1):
  for k in range(4):
   f=k/4;z,rx,ry=[profiles[i][j]*(1-f)+profiles[i+1][j]*f for j in range(3)];rings.append((0,0,z,rx*width,ry*depth))
 rings.append((0,0,1.75,.106,.087));loft('Anatomical tailored torso',rings,4,torso_weight,48,.018)
 for side,sign in [('L',1),('R',-1)]:
  leg=[]
  for k in range(27):
   f=k/26;z=1.06-f*.93;r=float(np.interp(z,[.13,.25,.42,.57,.73,1.06],[.052,.062,.085,.066,.103,.112]));leg.append((sign*(.145+.005*f),0,z,r*(1+(width-1)*.3),r*.88))
  loft('Fitted articulated leg '+side,leg,7,lambda co,s=side:blend('shin.'+s,'thigh.'+s,(co[2]-.49)/.16),32,.016)
  sleeve=[]
  for k in range(23):
   f=k/22;z=1.66-f*.60;r=((.115-.043*f) if role in ['tisseuse','bergere','accordeur'] else (.10-.048*f))*(1+.035*math.sin(f*math.pi*8));sleeve.append((sign*(.27+.21*f),-.03*f,z,r,r*.94))
  loft('Continuous sleeve '+side,sleeve,3,lambda co,s=side:blend('forearm.'+s,'upper_arm.'+s,(co[2]-1.28)/.14),32,.025)
  boot=[(sign*.15,-.045,.025,.069,.134),(sign*.15,-.047,.042,.071,.136),(sign*.15,-.05,.07,.069,.133),(sign*.15,-.035,.12,.062,.108),(sign*.15,0,.22,.057,.061),(sign*.15,0,.36,.064,.063)]
  loft('Shaped boot '+side,boot,7,lambda co,s=side:blend('foot.'+s,'shin.'+s,(co[2]-.11)/.1),36,.009)
  glove=[(sign*.48,-.03,1.09,.044,.041),(sign*.48,-.04,1.05,.047,.039),(sign*.48,-.04,.99,.047,.034),(sign*.48,-.04,.94,.032,.026)]
  loft('Sculpted glove '+side,glove,7,'hand.'+side,24,.018)
  for finger in range(4):
   x=sign*(.445+finger*.021);tube('Bent finger '+side,[(x,-.04,.995),(x,-.07,.965),(x,-.082,.94),(x,-.065,.925)],.0088,7,'hand.'+side,sides=6)
  tube('Opposed thumb '+side,[(sign*.523,-.027,1.035),(sign*.54,-.055,1.01),(sign*.525,-.08,.98),(sign*.505,-.077,.972)],.011,7,'hand.'+side,sides=7)
 # A head about 0.28m tall on a 2.12m body; ornaments do not define anatomical height.
 loft('Adult head under mask',[(0,.015,1.84,.07,.067),(0,.01,1.88,.10,.09),(0,.016,1.965,.132,.114),(0,.025,2.055,.136,.116),(0,.03,2.105,.103,.09),(0,.025,2.125,.025,.025)],6,'head',44)
 loft('Folded neck collar',[(0,0,1.73,.115,.10),(0,.008,1.79,.101,.091),(0,.015,1.845,.082,.078)],4,'neck',40,.035)

def mask(role):
 heavy=role in ['rempart','cendres','colosse','eclipse'];mat=2 if role in ['colosse','bergere','tisseuse','eclipse'] else 0
 lower={'voleur':1.90,'neant':1.865,'accordeur':1.855}.get(role,1.855)
 def point(f,u,up):
  x=(u-.5)*2;eye=2.005+.018*abs(x);z=eye+.009+(2.13-eye-.009)*f if up else lower+(eye-.009-lower)*f
  half=float(np.interp(z,[1.85,1.93,2.04,2.14],[.071,.117,.138,.102]));front=-.106-.05*math.sqrt(max(0,1-x*x))
  if role in ['rempart','cendres']:front-=.016*math.cos(x*math.pi)*math.exp(-((z-1.95)/.13)**2)
  if role=='voleur':front-=.055*math.exp(-x*x*12)*max(0,(2.0-z)/.11)
  if role=='accordeur':front-=.025*math.sin(x*math.pi)**2
  return(x*half,front,z)
 for upper in [False,True]:ribbon('Mask upper' if upper else 'Mask lower',lambda f,u,up=upper:point(f,u,up),15,34,mat,'head',.006)
 for sign in [-1,1]:
  ribbon('Mask temple bridge',lambda f,u,sign=sign:(sign*(.10+.027*u),-.132+.02*u,1.988+.04*f),6,8,mat,'head',.005)
  # Recessed eye beneath a physical brow, not a painted luminous strip across the face.
  tube('Recessed eye',[(sign*.043,-.151,2.012),(sign*.064,-.147,2.017)],.0028,8,'head',sides=6)
 if heavy:
  loft('Helmet shell',[(0,.025,1.85,.09,.09),(0,.025,1.96,.145,.124),(0,.03,2.06,.146,.13),(0,.035,2.125,.105,.095),(0,.04,2.15,.018,.025)],0 if role!='colosse' else 2,'head',40)
  # Face remains forward of the shell; inset brows follow the skull rather than an oversized cube.
  for sign in [-1,1]:tube('Helmet cheek seam',[(sign*.10,-.129,1.88),(sign*.137,-.113,1.98),(sign*.13,-.12,2.08)],.003,1,'head')
 else:
  for sign in [-1,1]:
   ribbon('Folded fitted hood',lambda f,u,sg=sign:(sg*(.10+.055*math.sin(f*math.pi)+.015*u),.025+.10*math.sin(u*math.pi),1.83+.31*f),18,14,4,'head',.003)
  loft('Hood crown',[(0,.035,2.04,.143,.127),(0,.035,2.095,.118,.11),(0,.035,2.135,.025,.03)],4,'head',40,.018)

def armor_and_clothes(role):
 width,depth,coat=PROFILES[role];heavy=role in ['rempart','cendres','colosse','eclipse'];plate_mat=2 if role=='colosse' else 0
 # Torso surfaces are fitted layered ribbons, avoiding a single spherical breastplate.
 rows=5 if heavy else 0 if role in ['tisseuse','bergere','neant'] else 2
 for row in range(rows):
  ribbon('Fitted cuirass tier',lambda f,u,row=row:((u-.5)*(.47-row*.025)*width,-.134*depth-.055*math.sin(u*math.pi)-.009*f,1.68-row*.085-(.095+.01*math.sin(u*math.pi))*f+.04*(u-.5)),7,26,7 if role=='voleur' else plate_mat,torso_weight,.007 if heavy else .004)
 for side,sign in [('L',1),('R',-1)]:
  count=4 if heavy else 2
  for row in range(count):
   ribbon('Articulated shoulder tier '+side,lambda f,u,row=row,sg=sign:(sg*(.19+(.20 if heavy else .16)*f+row*.006),math.sin((u-.5)*math.pi)*(.095+.018*f),1.735-row*.039-.105*f*f+.025*math.cos((u-.5)*math.pi)),8,20,plate_mat,'upper_arm.'+side,.007)
  for row in range(3 if heavy else 2):
   z=1.27-row*.062;cx=sign*(.405+row*.017)
   ribbon('Fitted bracer '+side,lambda f,u,z=z,cx=cx:(cx+math.cos((u-.5)*math.pi)*.060,-.025-math.sin(u*math.pi)*.082,z-.075*f),5,17,plate_mat,'forearm.'+side,.005)
  if heavy:
   ribbon('Shin guard '+side,lambda f,u,sg=sign:(sg*.15+math.cos((u-.5)*math.pi)*.075,-.005-math.sin(u*math.pi)*.083,.48-.27*f),12,20,plate_mat,'shin.'+side,.006)
 loft('Waist harness',[(0,0,1.105,.235*width,.145),(0,0,1.155,.225*width,.142)],7,'pelvis',48)
 # Role-specific hem length and panel count, with pelvis-dominant weights to prevent flying tassets.
 length={'voltigeur':.37,'voleur':.28,'rempart':.48,'cendres':.41,'colosse':.46}.get(role,.78)
 for sign in [-1,1]:
  ribbon('Tailored split skirt',lambda f,u,sg=sign:(sg*(.026+.195*u+.055*f*u),-.145-.07*f+math.sin(u*math.pi*4+.4)*.012*f,1.11-length*f+.025*f*f*math.sin(u*math.pi*2.5)),22,18,4,lambda co,sg=sign:{'pelvis':.90,'thigh.'+('L' if sg>0 else 'R'):.10},.004)
 # A different mantle silhouette per class, always leaving both feet visible.
 cloak_length={'voleur':.64,'voltigeur':.95,'rempart':1.33,'cendres':.95,'colosse':1.10}.get(role,1.43)
 sides=[-1] if role=='voleur' else [-1,1]
 def cape_weight(co):
  q=max(0,min(1,(1.72-co[2])/cloak_length));return blend('chest','cape_mid',q/.45) if q<.45 else blend('cape_mid','cape_tip',(q-.45)/.55)
 for sign in sides:
  for inner,mat in [(False,4),(True,5)]:
   ribbon('Mantle lining' if inner else 'Tailored mantle',lambda f,u,sg=sign,inside=inner:(sg*(.018+.045*f+u*(.25+.17*f)),.145+.15*f+.07*f*f+math.sin(u*math.pi*5+f*.4)*.012*f+(-.006 if inside else 0),1.72-cloak_length*f+.025*math.sin(u*math.pi*2.3)*f),27,20,mat,cape_weight,0 if inner else .004)
  tube('Mantle stitched edge',[(sign*(.018+.045*f+.25+.17*f),.15+.15*f+.07*f*f,1.72-cloak_length*f) for f in np.linspace(0,1,28)],.0025,1,cape_weight)
 # Practical asymmetry: straps, separate buckles and hanging tokens.
 ribbon('Diagonal leather harness',lambda f,u:((-.22+.42*f+(u-.5)*.032)*width,-.193*depth-.01*math.sin(f*math.pi),1.67-.54*f),25,6,7,torso_weight,.004)
 for index in range(3):
  x=.07+index*.037;z=1.055-index*.028;tube('Memory cord',[(x,-.164,1.14),(x+.008,-.18,z)],.002,7,'pelvis');ring('Memory ring',(x,-.181,z),.012,.014,.0022,1,'pelvis')

def identity(role):
 if role=='rempart':
  ribbon('Single helmet ridge',lambda f,u:((u-.5)*.025,.025+.12*(f-.5),2.14+.035*math.sin(f*math.pi)),14,5,1,'head',.005)
  for side,sg in [('L',1),('R',-1)]:
   for i in range(3):tube('Cheek ventilation',[(sg*(.09+i*.01),-.147,1.90+i*.025),(sg*(.115+i*.007),-.137,1.91+i*.025)],.002,7,'head')
 elif role=='voltigeur':
  for i in range(3):
   ribbon('Wind feather scarf',lambda f,u,i=i:(.13+i*.045+(u-.5)*.025,.14+.34*f,1.77-.32*f+.025*math.sin(f*math.pi+i)),17,6,5,'chest',.002)
  ring('Wind clasp',(0,-.205,1.50),.065,.07,.007,1,'chest',0,math.pi*1.65)
 elif role=='tisseuse':
  for sign in [-1,1]:
   ribbon('High rift collar',lambda f,u,sg=sign:(sg*(.11+.11*u),.02+.12*u,1.72+.30*f-.07*u),16,12,1,'chest',.006)
  ring('Broken portal spindle',(0,.245,1.53),.29,.34,.011,1,'chest',.15,math.pi*1.78)
  for i in range(5):ellipsoid('Rift stud',((i-2)*.037,-.205,1.51-abs(i-2)*.022),(.008,.006,.008),8,'chest',segments=10,rows=6)
 elif role=='cendres':
  for sign in [-1,1]:
   for row in range(2):
    x=sign*(.12+row*.085);tube('Heat exchanger',[(x,.19,1.25),(x,.24,1.55),(x,.24,1.81-row*.08)],.034,1,'chest')
   for i in range(4):tube('Furnace cheek',[(sign*.035,-.166,1.89+i*.025),(sign*.09,-.151,1.89+i*.025)],.0028,8 if i%2==0 else 1,'head')
  for i in range(4):ribbon('Heat scale',lambda f,u,i=i:((u-.5)*.20,-.205-.008*math.sin(u*math.pi),1.43-i*.045-.025*f),3,14,1,'chest',.003)
 elif role=='voleur':
  ribbon('Asymmetric cowl edge',lambda f,u:((u-.5)*.43,.04+.09*math.sin(u*math.pi),1.73-.065*f+.07*math.sin(u*math.pi)),13,30,4,'chest',.004)
  for i in range(4):tube('Concealed sheath',[(.21+i*.025,.12,1.02),(.29+i*.023,.14,.73)],.009,7,'pelvis')
 elif role=='bergere':
  ring('Astral diadem',(0,.09,2.02),.20,.23,.0065,1,'head',.15,math.pi*.96)
  for i in range(5):
   a=.18+i*.185*math.pi;ellipsoid('Diadem star',(math.cos(a)*.20,.087,2.02+math.sin(a)*.23),(.012,.009,.014),8,'head',segments=12,rows=7)
  ribbon('Astral stole',lambda f,u:((u-.5)*.10,-.205-.006*math.sin(f*math.pi),1.68-.73*f),28,8,2,torso_weight,.003)
  for i in range(5):ring('Stole constellation',(0,-.214,1.56-i*.11),.024,.028,.0022,1,'spine')
 elif role=='colosse':
  for side,sg in [('L',1),('R',-1)]:
   loft('Porcelain shoulder shell '+side,[(sg*.32,.015,1.56,.12,.12),(sg*.34,0,1.65,.17,.16),(sg*.33,.015,1.75,.13,.13)],2,'upper_arm.'+side,36)
  for i in range(4):
   x=(-1 if i%2 else 1)*.07;tube('Gold repair seam',[(x,-.20,1.66-i*.09),(x+.045,-.207,1.61-i*.09),(x+.018,-.211,1.57-i*.09)],.0026,1,'chest')
  ring('Porcelain oath seal',(0,-.225,1.48),.068,.078,.005,1,'chest')
 elif role=='accordeur':
  for i in range(5):
   x=(i-2)*.06;tube('Back chime pipe',[(x,.22,1.23),(x,.23,1.81+(.10 if i in [0,4] else .04))],.013,1,'chest')
  for side,sg in [('L',1),('R',-1)]:
   tube('Tuning crown prong',[(sg*.11,.025,2.09),(sg*.15,.02,2.20),(sg*.12,.02,2.25)],.010,1,'head')
  for i in range(3):
   x=(i-1)*.067;tube('Pendant suspension',[(x,-.20,1.22),(x,-.215,1.02-i*.025)],.002,7,'spine');ellipsoid('Tuned pendulum',(x,-.215,1.04-i*.025),(.018,.016,.065),1,'spine',segments=14,rows=8)
 elif role=='neant':
  tube('Swept crescent horn',[(.08,.03,2.09),(.17,.07,2.19),(.23,.12,2.20),(.24,.16,2.15)],.015,0,'head')
  for i in range(3):
   ring('Broken void arc',(0,.25,1.53),.23+i*.025,.26+i*.025,.0045,1,'chest',.30+i*.2,1.65+i*.3)
  ellipsoid('Void heart',(0,-.22,1.47),(.033,.015,.044),8,'chest',segments=16,rows=9)
 elif role=='eclipse':
  for i in range(7):
   a=(i-3)*.29;x=math.sin(a)*.22;z=2.13+math.cos(a)*.18
   tube('Solar crown ray',[(x,.04,z-.04),(x*1.08,.045,z+.03+(.045 if i==3 else 0))],.009,1,'head')
  ring('Black solar aureole',(0,.255,1.72),.31,.33,.012,1,'chest',.10,math.tau-.10)
  for i in range(9):
   a=i/9*math.tau;ellipsoid('Aureole ember',(math.cos(a)*.31,.25,1.72+math.sin(a)*.33),(.009,.008,.012),8,'chest',segments=10,rows=6)
  for sg in [-1,1]:
   ribbon('Gilded solar sash',lambda f,u,sg=sg:(sg*(.11+.08*f)+(u-.5)*.025,-.211-.03*f,1.67-.95*f),28,7,1,lambda co:{'chest':.3,'pelvis':.7},.004)

def rematerial_weapon(obj,role):
 old=list(obj.data.materials);mapping=[]
 for material in old:
  name=material.name.lower();mapping.append(8 if 'slit' in name or 'glow' in name else 1 if 'copper' in name else 7 if 'leather' in name else 4 if 'charcoal' in name else 5 if 'mantle' in name else 2 if role=='colosse' else 0)
 poly_mats=[mapping[p.material_index] for p in obj.data.polygons];obj.data.materials.clear()
 for material in materials:obj.data.materials.append(material)
 for poly,index in zip(obj.data.polygons,poly_mats):poly.material_index=index
 uv=obj.data.uv_layers.active
 if uv:
  for poly in obj.data.polygons:
   region=2 if poly.material_index==8 else poly.material_index
   for i in poly.loop_indices:
    u,v=uv.data[i].uv;uv.data[i].uv=((region%4+.02+.96*u%1)/4,(region//4+.02+.96*v%1)/2)
 if role=='voleur':
  for vertex in obj.data.vertices:
   if vertex.co.z<.88:vertex.co.z=.88+(vertex.co.z-.88)*.62
  bpy.context.view_layer.objects.active=rig;bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT');tip=rig.data.edit_bones.get('blade_tip');tip.head=(-.48,-.04,.353);tip.tail=(-.48,-.04,.303);bpy.ops.object.mode_set(mode='OBJECT')
  # Motion stage calibrates independent anchors from this physical endpoint.
 obj.name=role+'_Weapon'

def export_role(role,render=False):
 global rig,materials,parts,weapon_parts
 base_ns['create'](role);rig=bpy.data.objects[role+'_Rig'];old_weapon=bpy.data.objects[role+'_Weapon']
 for obj in list(bpy.data.objects):
  if obj.type=='MESH' and obj!=old_weapon:bpy.data.objects.remove(obj,do_unlink=True)
 for datablock in list(bpy.data.materials):
  if datablock.users==0:bpy.data.materials.remove(datablock)
 for image in list(bpy.data.images):
  if image.users==0:bpy.data.images.remove(image)
 parts=[];weapon_parts=[];surfaces(role);rematerial_weapon(old_weapon,role)
 anatomy(role);mask(role);armor_and_clothes(role);identity(role)
 # Bind all new costume surfaces to the unchanged anatomical rig.
 bpy.ops.object.select_all(action='DESELECT')
 for obj in parts:obj.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object;body.name=role+'_Skinned';body.parent=rig;modifier=body.modifiers.new('Roster deformation','ARMATURE');modifier.object=rig
 rig.animation_data.action=None
 for pose in rig.pose.bones:pose.rotation_euler=(0,0,0);pose.location=(0,0,0)
 bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);body.select_set(True);old_weapon.select_set(True);bpy.context.view_layer.objects.active=rig
 path=OUT/(role+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_nla_strips=False,export_force_sampling=True,export_skins=True,export_def_bones=False,export_cameras=False,export_lights=False)
 source=SOURCE/(role+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
 glb=path.read_bytes();chunk_size=struct.unpack_from('<I',glb,12)[0];document=json.loads(glb[20:20+chunk_size])
 binding_path=SOURCE/'WEAPON-BINDINGS.json';bindings=json.loads(binding_path.read_text()) if binding_path.exists() else {'version':1,'generator':'scripts/upgrade_roster_art.py','characters':{}}
 bindings['characters'][role]={'source_sha256':hashlib.sha256(glb).hexdigest(),'coordinate_system':'Blender bind world Z-up','vertices':[{'position':[round(v,7) for v in old_weapon.matrix_world@vertex.co],'weights':[[old_weapon.vertex_groups[group.group].name,round(group.weight,7)] for group in vertex.groups if group.weight>0]} for vertex in old_weapon.data.vertices]}
 binding_path.write_text(json.dumps(bindings,separators=(',',':'))+'\n')
 info={'hero':role,'stage':'original roster art before external retarget','generator':'scripts/upgrade_roster_art.py','source':source.relative_to(ROOT).as_posix(),'intermediate':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'vertices':len(body.data.vertices)+len(old_weapon.data.vertices),'polygons':len(body.data.polygons)+len(old_weapon.data.polygons),'materials':len(document['materials']),'images':len(document['images']),'color_size':1024,'data_size':512,'bind_sole_height':.025,'anatomical_head_height':.285,'anatomical_height':2.125,'rig_rest_preserved':True,'weapon_modified':role=='voleur'}
 (OUT/(role+'.json')).write_text(json.dumps(info,indent=2)+'\n');print('ROSTER_ART_READY '+json.dumps(info),flush=True)
 if render:render_role(role,rig)
 return info

def render_role(role,rig):
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=420;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.world.color=(.06,.06,.06)
 for name,pos,power,size,color in [('Key',(-3,-4,5),650,3,(1,.91,.78)),('Rim',(2,2,3),550,2,(1,.52,.22)),('Fill',(3,-2,3),240,3,(.63,.75,1))]:
  light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;light.color=color;obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj);obj.location=pos;obj.rotation_euler=(Vector((0,0,1.15))-obj.location).to_track_quat('-Z','Y').to_euler()
 camera_data=bpy.data.cameras.new('Roster review');camera=bpy.data.objects.new('Roster review',camera_data);scene.collection.objects.link(camera);camera.location=(2.6,-4.5,2.35);camera.rotation_euler=(Vector((0,0,1.12))-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=65;scene.camera=camera
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.02));floor=bpy.context.object;material=bpy.data.materials.new('Review ground');material.diffuse_color=(.035,.032,.03,1);floor.data.materials.append(material)
 # Readable relaxed stance for production still; full motions reviewed after retarget.
 rig.animation_data.action=None
 for pose in rig.pose.bones:pose.rotation_euler=(0,0,0);pose.location=(0,0,0)
 rig.pose.bones['forearm.R'].rotation_euler.x=-.18;rig.pose.bones['forearm.L'].rotation_euler.x=-.18
 scene.render.filepath=str(OUT/(role+'-review.png'));bpy.ops.render.render(write_still=True)

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
parser=argparse.ArgumentParser();parser.add_argument('--roles',nargs='+',choices=ROLES,default=ROLES);parser.add_argument('--render',action='store_true');options=parser.parse_args(args)
records=[]
for role in options.roles:records.append(export_role(role,options.render))
(OUT/'READY.json').write_text(json.dumps({'generator':'scripts/upgrade_roster_art.py','roles':records},indent=2)+'\n')
