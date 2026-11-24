"""Unretouched CPU views of final editable roster sources, for rig/pose review."""
from pathlib import Path
import bpy,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['rempart','guard','8']
hero=args[0];clip=args[1] if len(args)>1 else 'guard';frame=int(args[2]) if len(args)>2 else 8
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/source/roster'/f'{hero}.blend'))
scene=bpy.context.scene;rig=bpy.data.objects[hero+'_Rig'];rig.animation_data.action=bpy.data.actions[clip];scene.frame_set(frame);rig.location.z-=.025
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_x=480;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.world=bpy.data.worlds.new('Review world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.09,.105,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.01));plane=bpy.context.object;m=bpy.data.materials.new('Review floor');m.diffuse_color=(.055,.05,.06,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.055,.05,.06,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;plane.data.materials.append(m)
for position,power,size,color in [((-3,-4,5),650,4,(1,.83,.64)),((4,-1,3),380,3,(.58,.72,1)),((1,3,4),850,3,(1,.55,.23))]:
 data=bpy.data.lights.new('Review area','AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color;o=bpy.data.objects.new('Review area',data);scene.collection.objects.link(o);o.location=position;o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Review camera');camera=bpy.data.objects.new('Review camera',data);scene.collection.objects.link(camera);camera.location=(2.2,-4.7,2.05);camera.rotation_euler=(Vector((0,0,1.12))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=65;scene.camera=camera
output=Path('/tmp/roster-final-review');output.mkdir(exist_ok=True);scene.render.filepath=str(output/f'{hero}-{clip}.png');bpy.ops.render.render(write_still=True)
