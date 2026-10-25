"""Mesh origin relocation with median/bounds centers and dependent objects."""
import bpy
for operation in ('ORIGIN_GEOMETRY','GEOMETRY_ORIGIN'):
    for center in ('MEDIAN','BOUNDS'):
        mesh=bpy.data.meshes.new('Offset tetrahedron')
        mesh.from_pydata([(0,0,0),(4,0,0),(0,2,0),(0,0,3),(8,0,0)],[],[(0,2,1),(0,1,3),(1,2,3),(2,0,3)])
        obj=bpy.data.objects.new(operation+' '+center,mesh);bpy.context.collection.objects.link(obj)
        obj.location=(2,3,4);obj.rotation_euler=(.2,.3,.4);obj.scale=(-2,.5,1.5)
        bpy.ops.object.empty_add(location=(3,4,5),rotation=(.1,.2,.3))
        parent=bpy.context.object;parent.scale=(2,.7,1.2);obj.parent=parent
        bpy.ops.object.empty_add(location=(.3,1,.2))
        child=bpy.context.object;child.parent=obj
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        assert bpy.ops.object.origin_set(type=operation,center=center)=={'FINISHED'}
# A shared mesh user outside the selection remains part of the resulting scene.
bpy.ops.mesh.primitive_cube_add(location=(2,0,0))
shared=bpy.context.object;shared.name='Shared selected'
for vertex in shared.data.vertices:vertex.co.x+=2
peer=shared.copy();peer.name='Shared unselected';bpy.context.collection.objects.link(peer);peer.location=(6,0,0);peer.select_set(False)
bpy.context.view_layer.objects.active=shared
assert bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='MEDIAN')=={'FINISHED'}
assert shared.data==peer.data
