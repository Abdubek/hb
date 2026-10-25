"""Written before the shim. Run unchanged inside Blender and hb.

HB_SYMBOLS is consumed by generate_manifest.py; assertions are the contract.
The runner starts Blender with an empty scene, as does hb.
"""
HB_SYMBOLS = {
    'bpy.data.objects': 'Object database: iteration, length, name/index lookup, get',
    'bpy.data.objects.new': 'new(name, object_data); M0 supports empty objects only',
    'bpy.data.objects.get': 'get(name, default=None)',
    'bpy.context.object': 'Active object or None',
    'bpy.context.active_object': 'Active object or None',
    'bpy.context.selected_objects': 'List of selected, linked objects',
    'bpy.context.collection.objects.link': 'Link an existing object to the active collection',
    'bpy.context.scene.objects': 'Linked scene objects',
    'bpy.context.view_layer.objects.active': 'Read/write active linked object',
    'bpy.ops.mesh.primitive_cube_add': 'Keyword-only cube size/location/rotation/scale; WORLD or CURSOR, object or single-mesh EDIT construction; explicit zero size uses unit cube; return to OBJECT before script completion',
    'bpy.types.Object.name': 'Read/write unique name',
    'bpy.types.Object.location': 'XYZ float32 transform; assignment, indexed read/write, iteration',
    'bpy.types.Object.rotation_euler': 'Euler XYZ radians; assignment, indexed read/write, iteration',
    'bpy.types.Object.scale': 'XYZ float32 scale; assignment, indexed read/write, iteration',
    'bpy.types.Object.type': 'MESH or EMPTY',
    'bpy.types.Object.select_get': 'select_get() returns bool',
    'bpy.types.Object.select_set': 'select_set(state)',
}

import bpy

assert len(bpy.data.objects) == 0
assert bpy.context.object is None
assert bpy.data.objects.get('missing') is None
sentinel = object()
assert bpy.data.objects.get('missing', sentinel) is sentinel
empty = bpy.data.objects.new('Anchor', None)
assert empty.type == 'EMPTY'
assert len(bpy.context.scene.objects) == 0
bpy.context.collection.objects.link(empty)
assert len(bpy.context.scene.objects) == 1
result = bpy.ops.mesh.primitive_cube_add(size=2, location=(1, 2, 3))
assert result == {'FINISHED'}
a = bpy.context.object
assert a is bpy.context.active_object
assert a is bpy.context.view_layer.objects.active
assert a is bpy.data.objects['Cube']
assert a.type == 'MESH'
assert a.select_get()
assert tuple(a.scale) == (1, 1, 1)
a.name = 'Housing'
a.location = (2, -3, 0.5)
a.rotation_euler = (0.1, 0.2, 0.3)
a.scale = (1, 2, 3)
a.location[0] = 4
assert a.location[0] == 4
assert tuple(a.location) == (4, -3, 0.5)
assert bpy.ops.mesh.primitive_cube_add(size=0.25, scale=(2, 3, 4)) == {'FINISHED'}
b = bpy.context.object
assert b.name == 'Cube'
assert tuple(b.scale) == (1, 1, 1)
assert not a.select_get()
bpy.ops.mesh.primitive_cube_add()
c = bpy.context.object
assert c.name == 'Cube.001'
c.name = 'Housing'
assert c.name == 'Housing.001'
a.select_set(True)
assert {o.name for o in bpy.context.selected_objects} == {'Housing', 'Housing.001'}
bpy.context.view_layer.objects.active = a
assert bpy.context.object is a
bpy.context.view_layer.objects.active = None
assert bpy.context.object is None
assert {o.name for o in bpy.data.objects} == {'Anchor', 'Housing', 'Housing.001', 'Cube'}
