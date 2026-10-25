"""Blender PLY oracle; preserve observations independently of the hb importer."""
import bpy,json,sys
from pathlib import Path
result={}
source=Path(__file__).with_name('fixtures')/'ply'
output=Path(sys.argv[sys.argv.index('--')+1])
for path in sorted(source.glob('*.ply')):
 for kind in ('objects','meshes'):
  for block in list(getattr(bpy.data,kind)):getattr(bpy.data,kind).remove(block)
 assert bpy.ops.wm.ply_import(filepath=str(path))=={'FINISHED'}
 o=bpy.context.object;m=o.data
 result[path.stem]={'name':o.name,'mesh_name':m.name,'vertices':[list(v.co) for v in m.vertices],'edges':[list(e.vertices) for e in m.edges],'faces':[list(p.vertices) for p in m.polygons],'smooth':[p.use_smooth for p in m.polygons],'uv_layers':[{'name':l.name,'data':[list(d.uv) for d in l.data]} for l in m.uv_layers],'normals':[list(n.vector) for n in m.corner_normals],'custom_normals':m.has_custom_normals,'colors':[{'name':c.name,'domain':c.domain,'data_type':c.data_type,'data':[list(d.color) for d in c.data]} for c in m.color_attributes]}
output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
