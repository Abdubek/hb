import bpy,json,itertools
from pathlib import Path
out={}
for i,(segments,rings) in enumerate(itertools.product((3,8,12),(3,4,6))):
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 for m in list(bpy.data.meshes):bpy.data.meshes.remove(m)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=0,calc_uvs=False)
 m=bpy.context.object.data
 out[str(i)]=dict(segments=segments,rings=rings,vertices=[list(v.co) for v in m.vertices],edges=[list(e.vertices) for e in m.edges],faces=[list(f.vertices) for f in m.polygons])
Path('/results/zero-sphere-reference.json').write_text(json.dumps(out,indent=2)+'\n')
