"""Generate parametric cuboid bevel stencils using external Blender 4.5 LTS.

These are geometry coefficients, not Blender source or executable code.
Runtime evaluation scales insets by width and transforms them into the input
cuboid frame. No Blender runtime or scene fixture lookup is used by hb.
"""
import bpy,json,sys
from pathlib import Path
out=[]
for segments in range(1,9):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.mesh.primitive_cube_add(size=2,calc_uvs=False)
 o=bpy.context.object;m=o.modifiers.new('Bevel','BEVEL');m.width=.25;m.segments=segments
 bpy.ops.object.modifier_apply(modifier=m.name)
 mesh=o.data
 out.append(dict(segments=segments,vertices=[[int(v.co[k]>0) for k in range(3)]+[round((1-abs(v.co[k]))*4,8) for k in range(3)] for v in mesh.vertices],faces=[list(f.vertices) for f in mesh.polygons]))
path=Path(sys.argv[sys.argv.index('--')+1]);path.write_text(json.dumps(dict(reference='Blender 4.5.9 LTS; generated geometry coefficients; no Blender source code',reference_width=.25,stencils=out),separators=(',',':'))+'\n')
