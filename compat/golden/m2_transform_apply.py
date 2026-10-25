"""Transform baking contract, authored against Blender before implementation."""
import bpy
for location,rotation,scale in ((False,False,False),(True,False,False),(False,True,False),(False,False,True),(True,True,False),(True,False,True),(False,True,True),(True,True,True)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(1,2,3),rotation=(.2,.3,.4))
    obj=bpy.context.object;obj.scale=(2,.7,1.4)
    result=bpy.ops.object.transform_apply(location=location,rotation=rotation,scale=scale,properties=True,isolate_users=False)
    assert result=={'FINISHED'}
    if location:assert tuple(obj.location)==(0,0,0)
    if rotation:assert tuple(obj.rotation_euler)==(0,0,0)
    if scale:assert tuple(obj.scale)==(1,1,1)
