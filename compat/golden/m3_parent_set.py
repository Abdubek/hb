"""Object parenting with inverse-parent compensation and keep_transform."""
import bpy
from mathutils import Vector
bpy.ops.object.empty_add(location=(3,2,1),rotation=(.1,.2,.3))
parent=bpy.context.object;parent.name='Parent';parent.scale=(2,.7,1.3)
bpy.ops.object.empty_add(location=(-2,1,3),rotation=(.3,-.1,.2))
other=bpy.context.object;other.name='Other';other.scale=(.8,1.2,1.1)
for keep in (False,True):
    bpy.ops.mesh.primitive_cube_add(location=(1,2,4),rotation=(.2,.3,.1))
    child=bpy.context.object;child.name='Keep' if keep else 'Local'
    child.scale=(.5,.6,.7)
    parent.select_set(True);bpy.context.view_layer.objects.active=parent
    assert bpy.ops.object.parent_set(type='OBJECT',keep_transform=keep)=={'FINISHED'}
    assert child.parent==parent
    assert tuple(child.location)==(1,2,4)
    parent.location.x+=.5
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT');child.select_set(True);other.select_set(True)
    bpy.context.view_layer.objects.active=other
    assert bpy.ops.object.parent_set(type='OBJECT',keep_transform=keep)=={'FINISHED'}
    assert child.parent==other
    child.location.z+=.3
# Direct parent assignment continues using its ordinary local-coordinate contract.
bpy.ops.mesh.primitive_cube_add(location=(.5,.5,.5))
direct=bpy.context.object;direct.name='Direct';direct.parent=parent
# Reparent an object with an existing nonuniform parent and reflected local scale.
bpy.ops.mesh.primitive_cube_add(location=(2,-1,.5),rotation=(.3,.2,.4))
sheared=bpy.context.object;sheared.name='Reparented';sheared.scale=(-1,.6,1.2);sheared.parent=parent
bpy.context.view_layer.update()
other.select_set(True);bpy.context.view_layer.objects.active=other
assert bpy.ops.object.parent_set(type='OBJECT',keep_transform=True)=={'FINISHED'}
assert sheared.parent==other
