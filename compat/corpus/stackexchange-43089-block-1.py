import bpy
from math import *  # It's considered bad practice to import everything from a library, especially when you're not using any (or just a few) of its function
import mathutils

Name = 'Dimi'

# The primitive_cylinder_add does not return the object, but rather only a status indicating success or failure
exitStatus = bpy.ops.mesh.primitive_cylinder_add(radius = 0.5, depth = 1)
scj = bpy.context.scene

# The added cylinder will be the active object afterits created
ob = bpy.context.object
me = ob.data
ob.name = Name

# These two lines are unnecessary and will generate another copy of your cylinder
#ob = bpy.data.objects.new(Name, me1)
#scj.objects.link(ob)

# If you want to move your object, simply set its location thus:
ob.location = ( 4, 0, 0 )

# And you can rotate the object the same way
ob.rotation_euler = (0,0,0)  # Note that you need to use radians rather than angles here
