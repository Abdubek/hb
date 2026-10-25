"""Inspect Blender's base icosahedron before changing its construction contract."""
import bpy,json,sys
from pathlib import Path
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
m=bpy.context.object.data
Path(sys.argv[sys.argv.index('--')+1]).write_text(json.dumps({
    'blender':bpy.app.version_string,
    'vertices':[list(v.co) for v in m.vertices],
    'faces':[list(f.vertices) for f in m.polygons],
    'uv':[list(p.uv) for p in m.uv_layers.active.data],
},indent=2)+'\n')
