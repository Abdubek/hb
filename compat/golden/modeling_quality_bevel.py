import bpy
for sides in (6,16,32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides,location=(sides*.15,0,0))
    o=bpy.context.object
    o.data.materials.append(bpy.data.materials.new('Body'))
    o.data.materials.append(bpy.data.materials.new('Cap'))
    o.data.polygons[0].material_index=1
    m=o.modifiers.new('Round','BEVEL');m.width=.08;m.segments=4
    bpy.ops.object.modifier_apply(modifier=m.name)
    assert len(o.data.vertices)>sides*2
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1)
m=bpy.context.object.modifiers.new('Soft','BEVEL');m.width=.05;m.segments=3;m.limit_method='NONE'
