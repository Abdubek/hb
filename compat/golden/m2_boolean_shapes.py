"""Boolean regression geometry; no additional bpy surface."""
HB_EQUIVALENT_MESH_PREFIXES=('Boolean rotated','Boolean cone','Boolean sphere','Boolean material','Boolean chained')
import bpy

def boolean(a,b,operation):
    bpy.context.view_layer.objects.active=a
    m=a.modifiers.new('Cut','BOOLEAN');m.solver='MANIFOLD';m.operation=operation;m.object=b
    bpy.ops.object.modifier_apply(modifier=m.name)
for operation in ('DIFFERENCE','UNION','INTERSECT'):
    bpy.ops.mesh.primitive_cube_add(size=2);a=bpy.context.object;a.data.name='Boolean rotated'
    bpy.ops.mesh.primitive_cube_add(size=2,location=(.7,.4,.3),rotation=(.2,.3,.4));b=bpy.context.object
    boolean(a,b,operation)
    bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=1,radius2=.5,depth=2);a=bpy.context.object;a.data.name='Boolean cone'
    bpy.ops.mesh.primitive_cube_add(size=2,location=(.7,.4,.3));b=bpy.context.object
    boolean(a,b,operation)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=1);a=bpy.context.object;a.data.name='Boolean sphere'
    bpy.ops.mesh.primitive_cube_add(size=2,location=(.7,.4,.3));b=bpy.context.object
    boolean(a,b,operation)
# INDEX preserves face slot indices while collecting distinct operand materials.
bpy.ops.mesh.primitive_cube_add();a=bpy.context.object;a.data.name='Boolean material'
mat=bpy.data.materials.new('Shared');a.data.materials.append(mat)
bpy.ops.mesh.primitive_cube_add(location=(1,0,0));b=bpy.context.object;b.data.materials.append(mat);b.data.materials.append(bpy.data.materials.new('Extra'))
for p in b.data.polygons:p.material_index=1
boolean(a,b,'UNION')
# An already evaluated operand can itself be used by another modifier.
bpy.ops.mesh.primitive_cube_add();a=bpy.context.object;a.data.name='Boolean chained'
bpy.ops.mesh.primitive_cube_add(location=(1,0,0));b=bpy.context.object
bpy.ops.mesh.primitive_cube_add(location=(1,1,0));c=bpy.context.object
m=b.modifiers.new('Clip','BOOLEAN');m.solver='MANIFOLD';m.operation='INTERSECT';m.object=c
boolean(a,b,'DIFFERENCE')
for scale in ((-1,-1,1),(.5,2,1)):
    bpy.ops.mesh.primitive_cube_add();a=bpy.context.object;a.data.name='Boolean rotated'
    bpy.ops.mesh.primitive_cube_add(location=(.7,.4,.3),rotation=(.2,.3,.4));b=bpy.context.object;b.scale=scale
    boolean(a,b,'DIFFERENCE')
