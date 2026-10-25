"""Through holes and nested cavities retain closed, oriented surfaces."""
HB_EQUIVALENT_MESH_PREFIXES=('Boolean bore','Boolean cavity')
import bpy
for operation in ('DIFFERENCE','UNION','INTERSECT'):
    for scale,name in (((.5,.5,2),'Boolean bore'),((.5,.5,.5),'Boolean cavity')):
        bpy.ops.mesh.primitive_cube_add();a=bpy.context.object;a.data.name=name
        bpy.ops.mesh.primitive_cube_add();b=bpy.context.object;b.scale=scale
        m=a.modifiers.new('Cut','BOOLEAN');m.solver='MANIFOLD';m.object=b;m.operation=operation
        bpy.context.view_layer.objects.active=a;bpy.ops.object.modifier_apply(modifier=m.name)
