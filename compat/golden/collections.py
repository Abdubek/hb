"""Collection ordering and explicit primitive keyword regression contract."""
HB_SYMBOLS = {
    'bpy.context.scene.objects.get': 'get(name, default=None)',
    'bpy.context.collection.objects.get': 'get(name, default=None)',
    'bpy.context.view_layer.objects.get': 'get(name, default=None)',
    'bpy.context.collection.objects': 'Linked collection objects, insertion order',
    'bpy.context.view_layer.objects': 'View-layer objects, insertion order',
}
import bpy
from bpy import data as database
from bpy import context as ctx
assert database is bpy.data
assert ctx is bpy.context
names=['z','A','a','Z','foo.001','foo.009','foo.002']
for name in names:
    obj=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(obj)
    obj.select_set(True)
assert [o.name for o in bpy.data.objects] == ['A','a','foo.001','foo.002','foo.009','z','Z']
assert [o.name for o in bpy.context.scene.objects] == names
assert [o.name for o in bpy.context.collection.objects] == names
assert [o.name for o in bpy.context.view_layer.objects] == names
assert [o.name for o in bpy.context.selected_objects] == names
assert bpy.data.objects[0].name == 'A'
assert bpy.data.objects[-1].name == 'Z'
assert 'A' in bpy.data.objects
assert 'missing' not in bpy.data.objects
for collection in (bpy.context.scene.objects,bpy.context.collection.objects,bpy.context.view_layer.objects):
    assert collection.get('a') is bpy.data.objects['a']
    assert collection.get('missing') is None
    assert collection[0].name == 'z'
bpy.ops.mesh.primitive_cube_add(scale=(0,0,0),calc_uvs=False)
bpy.context.object.name='Collapsed'
assert tuple(bpy.context.object.scale)==(1,1,1)
bpy.ops.mesh.primitive_cube_add(size=0.5,scale=(-2,3,.5),location=(1,-2,3),rotation=(.1,-.2,.3))
bpy.context.object.name='Mirrored'
