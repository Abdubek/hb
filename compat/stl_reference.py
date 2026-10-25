"""Blender-only STL importer oracle; fixtures are preserved alongside results."""
import bpy,json,sys
from pathlib import Path
source=Path(__file__).with_name('fixtures')/'stl'
output=Path(sys.argv[sys.argv.index('--')+1])
result={}
for name in ('triangles-ascii','triangles-binary','degenerate-binary','empty','collinear','reverse-duplicate','degenerate-only'):
    for kind in ('objects','meshes'):
        for block in list(getattr(bpy.data,kind)):getattr(bpy.data,kind).remove(block)
    assert bpy.ops.wm.stl_import(filepath=str(source/(name+'.stl')))=={'FINISHED'}
    obj=bpy.context.object;mesh=obj.data
    result[name]={'name':obj.name,'mesh_name':mesh.name,'vertices':[list(v.co) for v in mesh.vertices],'edges':[list(e.vertices) for e in mesh.edges],'faces':[list(f.vertices) for f in mesh.polygons],'smooth':[f.use_smooth for f in mesh.polygons],'uv_layers':len(mesh.uv_layers),'normals':[list(f.normal) for f in mesh.polygons]}
output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
