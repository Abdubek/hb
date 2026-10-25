"""Blender 4.5 golden exporter. blender -b --python ... -- script.py result.json"""
import bpy
import json
import sys
import ast
from pathlib import Path
script, output=sys.argv[sys.argv.index('--')+1:]
for kind in ('objects','meshes','curves','materials','cameras','lights','images','textures','worlds','collections'):
    db=getattr(bpy.data,kind)
    for block in list(db):db.remove(block)
for font in list(bpy.data.fonts):
    if font.name!='Bfont':bpy.data.fonts.remove(font)
c=bpy.data.collections.new('Collection');bpy.context.scene.collection.children.link(c)
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children['Collection']
bpy.context.scene.camera=None
# Each batch case receives the same construction context as a fresh hb run.
bpy.context.scene.cursor.location=(0,0,0)
bpy.context.scene.cursor.rotation_euler=(0,0,0)
w=bpy.data.worlds.new('World');w.color=(.05087608844041824,)*3;w.use_nodes=True;bpy.context.scene.world=w
bpy.context.scene.render.resolution_x=1920;bpy.context.scene.render.resolution_y=1080
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.render.pixel_aspect_x=1;bpy.context.scene.render.pixel_aspect_y=1
# Rendering tests compare operation/file behavior, using CPU Cycles as the oracle.
for node in ast.parse(Path(script).read_text()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HB_REFERENCE_RENDER_ENGINE' for t in node.targets):
        assert ast.literal_eval(node.value)==('CYCLES',)
        bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1;bpy.context.scene.cycles.device='CPU'
exec(compile(open(script).read(),script,'exec'),{'__name__':'__main__','__file__':script})
namespace={};exec(Path(__file__).with_name('observe.py').read_text(),namespace)
snapshot=namespace['observe']();snapshot['blender_version']=bpy.app.version_string
Path(output).write_text(json.dumps(snapshot,sort_keys=True,indent=2))
bpy.ops.export_scene.gltf(filepath=output+'.glb',export_format='GLB',export_cameras=True,export_lights=True,export_apply=True)
