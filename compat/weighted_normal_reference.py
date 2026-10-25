"""Capture Blender inputs and outputs separately from upstream bevel approximation."""
import bpy,json,sys
from pathlib import Path
bpy.ops.wm.read_factory_settings(use_empty=True)
script=Path(__file__).with_name('golden')/'m2_weighted_normals.py'
source=script.read_text();split=source.index('for uv in (False,True):')
scope={'__name__':'__main__'};exec(compile(source[:split],str(script),'exec'),scope)
original=scope['weighted'];inputs=[]
def capture(obj,mode,keep,apply):
    mesh=obj.data
    inputs.append(dict(name=mesh.name,vertices=[list(v.co) for v in mesh.vertices],
        faces=[list(f.vertices) for f in mesh.polygons],smooth=[f.use_smooth for f in mesh.polygons],mode=mode,keep_sharp=keep))
    apply()
def weighted(obj,mode,keep):
    capture(obj,mode,keep,lambda:original(obj,mode,keep))
scope['weighted']=weighted;exec(compile(source[split:],str(script),'exec'),scope)
for obj in bpy.data.objects:
    bpy.context.view_layer.objects.active=obj
    if obj.modifiers:
        modifier=obj.modifiers[0]
        capture(obj,modifier.mode,modifier.keep_sharp,lambda:bpy.ops.object.modifier_apply(modifier=modifier.name))
normals={mesh.name:[list(n.vector) for n in mesh.corner_normals] for mesh in bpy.data.meshes}
Path(sys.argv[sys.argv.index('--')+1]).write_text(json.dumps(dict(blender=bpy.app.version_string,inputs=inputs,normals=normals))+'\n')
