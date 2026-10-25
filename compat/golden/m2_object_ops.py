import bpy, math
HB_SYMBOLS={
 'bpy.ops.object.camera_add':'Create a camera in object mode with WORLD alignment; input scale is ignored, matching Blender.',
 'bpy.ops.object.light_add':'Create POINT/SUN/SPOT/AREA lights; AREA radius sets size, input scale is ignored.',
 'bpy.ops.object.empty_add':'Create non-image empty object display shapes; radius sets display size.',
 'bpy.types.Object.empty_display_size':'Persistent empty display radius, clamped at 0.0001.',
 'bpy.types.Object.empty_display_type':'Persistent empty display shape, excluding image empties.',
 'bpy.types.Object.dimensions':'Evaluated local bounding-box dimensions multiplied by world-axis scale; assignment preserves scale signs.',
}
assert bpy.context.scene.camera is None
bpy.ops.object.camera_add(location=(4,-6,4),rotation=(1.1,0,.6),scale=(2,3,4))
cam=bpy.context.object
assert cam.name=='Camera' and tuple(cam.scale)==(1,1,1)
assert bpy.context.scene.camera is None
bpy.context.scene.camera=cam
bpy.ops.object.camera_add(location=(0,0,5))
assert bpy.context.scene.camera is cam
bpy.data.objects.remove(bpy.context.object,do_unlink=True)
bpy.data.cameras.remove(bpy.data.cameras['Camera.001'])
for kind in ('POINT','SUN','SPOT','AREA'):
    bpy.ops.object.light_add(type=kind,radius=2,location=(2,-3,4),rotation=(.4,.2,0),scale=(2,3,4))
    o=bpy.context.object
    assert o.name==kind.title() and tuple(o.scale)==(1,1,1)
    assert o.data.energy==(1 if kind=='SUN' else 10)
    assert tuple(o.dimensions)==(0,0,0)
    if kind=='AREA':assert o.data.size==2
for shape in ('PLAIN_AXES','ARROWS','SINGLE_ARROW','CIRCLE','CUBE','SPHERE','CONE'):
    bpy.ops.object.empty_add(type=shape,radius=2,location=(1,2,3))
    o=bpy.context.object;o.name=shape
    assert o.empty_display_type==shape and o.empty_display_size==2
    o.empty_display_size=.5
    o.dimensions=(3,4,5)
    assert tuple(o.dimensions)==(0,0,0) and tuple(o.scale)==(1,1,1)
bpy.ops.mesh.primitive_cube_add(location=(0,0,1),rotation=(.4,.2,.1))
o=bpy.context.object;o.name='Dimension cube'
o.scale=(-2,0,3);bpy.context.view_layer.update()
assert all(abs(a-b)<1e-5 for a,b in zip(o.dimensions,(4,0,6)))
o.dimensions=(8,5,4);bpy.context.view_layer.update()
assert all(abs(a-b)<1e-5 for a,b in zip(o.dimensions,(8,5,4)))
assert all(abs(a-b)<1e-5 for a,b in zip(o.scale,(-4,2.5,2)))
o.dimensions.x=3;bpy.context.view_layer.update();assert abs(o.dimensions.x-3)<1e-5
parent=bpy.data.objects.new('Scaled parent',None);bpy.context.collection.objects.link(parent)
parent.scale=(2,3,4);o.parent=parent;o.rotation_euler=(0,0,0)
o.dimensions=(8,5,4);bpy.context.view_layer.update()
assert all(abs(a-b)<1e-5 for a,b in zip(o.dimensions,(16,15,16)))
assert all(abs(a-b)<1e-5 for a,b in zip(o.scale,(-4,2.5,2)))
parent.empty_display_size=0;assert abs(parent.empty_display_size-.0001)<1e-8
parent.empty_display_size=2000;assert parent.empty_display_size==1000
bpy.ops.object.select_all(action='DESELECT')
