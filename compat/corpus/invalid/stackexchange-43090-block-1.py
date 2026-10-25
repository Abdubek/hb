import bpy
from math import radians
from mathutils import Vector

context = bpy.context
Name = 'Dimi'
# operators don't return object refs.
bpy.ops.mesh.primitive_cylinder_add(radius = 0.5, depth = 1)

scene = context.scene
ob = scene.objects.active # the newly added cylinder.
ob.name = Name
# move the object
ob.location += Vector((4, 0, 0))
# set the objects rotation
ob.rotation_euler = (0, 0, radians(20))
