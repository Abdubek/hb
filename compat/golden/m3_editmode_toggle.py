import bpy

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add(size=2, location=(3, -2, 1))
target = bpy.context.object
assert target.mode == 'OBJECT' and bpy.context.mode == 'OBJECT'
assert bpy.ops.object.editmode_toggle() == {'FINISHED'}
assert target.mode == 'EDIT' and bpy.context.mode == 'EDIT_MESH'
bpy.ops.mesh.primitive_cube_add(size=1, location=(4, -2, 1))
assert bpy.context.object == target and target.mode == 'EDIT'
assert bpy.ops.object.editmode_toggle() == {'FINISHED'}
assert target.mode == 'OBJECT' and bpy.context.mode == 'OBJECT'
assert bpy.ops.object.editmode_toggle() == {'FINISHED'}
bpy.ops.mesh.primitive_plane_add(size=2, location=(3, -2, 3))
assert bpy.ops.object.editmode_toggle() == {'FINISHED'}
assert target.mode == 'OBJECT' and bpy.context.mode == 'OBJECT'
assert bpy.context.object == target and len(bpy.context.scene.objects) == 1
assert len(target.data.vertices) == 20 and len(target.data.polygons) == 13
expected = [(x, y, z) for x in (-1., 1.) for y in (-1., 1.) for z in (-1., 1.)]
expected += [(x, y, z) for x in (.5, 1.5) for y in (-.5, .5) for z in (-.5, .5)]
expected += [(x, y, 2.) for x in (-1., 1.) for y in (-1., 1.)]
assert sorted(tuple(vertex.co) for vertex in target.data.vertices) == sorted(expected)
